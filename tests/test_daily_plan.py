"""Public-artifact planning, curriculum gating, coverage and Vietnamese dates."""
from copy import deepcopy
from datetime import date, datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from daily_plan import next_date, plan
from generate_topic_map import coverage, covered_topics, validate_topics
from study_profile import load_profile, study_date

DATA = json.loads((ROOT/'references/topics.json').read_text(encoding='utf-8'))
BASE_LESSON = json.loads((ROOT/'lessons/catalog.json').read_text(encoding='utf-8'))['lessons'][0]


def inventory():
    data = deepcopy(DATA)
    lookup = {t['id']: t for t in data['topics']}
    foundation = lookup['foundations.program-reasoning']
    master = lookup['algorithms.graphs']
    doctoral = lookup['doctoral.6201100']
    doctoral['prerequisites'] = []
    # Doctoral first in the array still cannot bypass uncovered master's units.
    data['topics'] = [doctoral, foundation, master]
    mapped = {c for t in data['topics'] for c in t['course_ids']}
    data['courses'] = [c for c in data['courses'] if c['id'] in mapped]
    return data


def lesson(key, on, topics):
    entry = deepcopy(BASE_LESSON)
    entry.update(id=key, date=on, topic_ids=topics,
                 files=[f'lessons/{key}/lesson.md', f'vi/lessons/{key}/lesson.md'])
    return entry


class DailyPlanTests(unittest.TestCase):
    def test_next_publication_date_uses_latest_catalog_date_not_order_or_today(self):
        entries = [lesson('future', '2026-10-12', []), lesson('older', '2026-10-05', [])]
        self.assertEqual(next_date(entries, date(2026, 10, 9)), '2026-10-13')
        self.assertEqual(next_date([], date(2026, 10, 9)), '2026-10-09')
        with tempfile.TemporaryDirectory() as directory:
            topics = Path(directory)/'topics.json'; catalog = Path(directory)/'catalog.json'
            topics.write_text(json.dumps(inventory()))
            catalog.write_text(json.dumps({'lessons': [lesson('future', '2026-10-12',
                                                              ['foundations.program-reasoning'])]}))
            args = [sys.executable, str(ROOT/'scripts/daily_plan.py'), '--topics', str(topics),
                    '--catalog', str(catalog), '--next']
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)['on'], '2026-10-13')
            self.assertEqual(json.loads(result.stdout)['topic']['id'], 'algorithms.graphs')
            conflict = subprocess.run(args + ['--on', '2026-10-07'], capture_output=True, text=True)
            self.assertNotEqual(conflict.returncode, 0)

    def test_master_priority_prerequisites_and_repeatability(self):
        data = inventory()
        self.assertEqual(plan(data, [], '2026-10-07')['topic']['id'], 'foundations.program-reasoning')
        entries = [lesson('foundation', '2026-10-05', ['foundations.program-reasoning'])]
        before = deepcopy((data, entries))
        first = plan(data, entries, '2026-10-07')
        self.assertEqual(first['topic']['id'], 'algorithms.graphs')
        self.assertEqual(first, plan(data, entries, '2026-10-07'))
        self.assertEqual((data, entries), before)
        entries.append(lesson('graphs', '2026-10-06', ['algorithms.graphs']))
        result = plan(data, entries, '2026-10-07')
        self.assertEqual(result['topic']['id'], 'doctoral.6201100')
        self.assertEqual(result['day_type'], 'paper')

    def test_same_day_returns_published_lesson_instead_of_duplicate(self):
        data = inventory()
        entries = [lesson('today', '2026-10-07', ['foundations.program-reasoning'])]
        result = plan(data, entries, '2026-10-07')
        self.assertEqual(result['action'], 'existing-lesson')
        self.assertEqual(result['lesson_id'], 'today')
        self.assertNotIn('topic', result)

    def test_future_artifacts_do_not_satisfy_earlier_prerequisites(self):
        data = inventory()
        entries = [lesson('future', '2026-10-08', ['foundations.program-reasoning'])]
        result = plan(data, entries, '2026-10-07')
        self.assertEqual(result['topic']['id'], 'foundations.program-reasoning')
        self.assertEqual(result['coverage']['covered'], 0)

    def test_publication_coverage_deduplicates_and_groups_by_area(self):
        data = inventory()
        entries = [lesson('first', '2026-10-05', ['foundations.program-reasoning']),
                   lesson('repeat', '2026-10-06', ['foundations.program-reasoning'])]
        result = coverage(data, entries)
        self.assertEqual(result['covered'], 1)
        self.assertEqual(result['planned'], 3)
        master = next(r for r in result['by_area'] if r['level'] == 'master')
        self.assertEqual((master['covered'], master['planned'], master['percent']), (1, 2, 50.0))
        with self.assertRaises(ValueError):
            covered_topics(data, [lesson('unknown', '2026-10-05', ['unknown.topic'])])

    def test_full_inventory_leads_to_research_extension_without_degree_claim(self):
        data = inventory()
        entries = [lesson('prior', '2026-10-05', [t['id'] for t in data['topics']])]
        result = plan(data, entries, '2026-10-07')
        self.assertEqual(result['action'], 'research-extension')
        self.assertIsNone(result['topic'])
        self.assertIn('no degree', result['reason'])

    def test_invalid_level_mapping_missing_course_and_reverse_dependency_fail(self):
        for variant in ('level', 'area', 'course', 'unmapped', 'reverse'):
            data = inventory()
            if variant == 'level': data['topics'][1]['level'] = 'bachelor'
            if variant == 'area': data['topics'][1]['area'] = 'absent'
            if variant == 'course': data['topics'][1]['course_ids'] = ['absent']
            if variant == 'unmapped': data['topics'][0]['course_ids'] = []
            if variant == 'reverse': data['topics'][1]['prerequisites'] = ['doctoral.6201100']
            with self.subTest(variant=variant), self.assertRaises(ValueError): validate_topics(data)

    def test_build_paper_budgets_and_override(self):
        profile = load_profile()
        self.assertEqual(profile['daily_minutes'], 420)
        for blocks in (d['blocks'] for d in profile['day_types'].values()):
            self.assertEqual(sum(b['minutes'] for b in blocks), profile['daily_minutes'])
            self.assertEqual(sum(b['minutes'] for b in blocks if b['break']), 60)
        result = plan(inventory(), [], '2026-10-07', day_type='paper')
        self.assertEqual(result['day_type'], 'paper')
        self.assertTrue(any(b['id'] == 'paper-reading' for b in result['blocks']))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'profile.json'
            invalid = deepcopy(profile); invalid['day_types']['paper']['blocks'][0]['minutes'] += 1
            path.write_text(json.dumps(invalid))
            with self.assertRaises(ValueError): load_profile(path)

    def test_vietnamese_midnight_not_utc_midnight(self):
        self.assertEqual(study_date(datetime(2026, 10, 6, 16, 59, tzinfo=timezone.utc)).isoformat(), '2026-10-06')
        self.assertEqual(study_date(datetime(2026, 10, 6, 17, 0, tzinfo=timezone.utc)).isoformat(), '2026-10-07')
        self.assertEqual(load_profile()['timezone'], 'Asia/Ho_Chi_Minh')
        with self.assertRaises(ValueError): study_date(datetime(2026, 10, 6))

    def test_cli_has_repeatable_output_and_does_not_write_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topics = root/'topics.json'; catalog = root/'catalog.json'
            topics.write_text(json.dumps(inventory()))
            catalog.write_text(json.dumps({'lessons': []}))
            args = [sys.executable, str(ROOT/'scripts/daily_plan.py'), '--topics', str(topics),
                    '--catalog', str(catalog), '--on', '2026-10-07']
            first = subprocess.run(args, capture_output=True, text=True, check=True)
            second = subprocess.run(args, capture_output=True, text=True, check=True)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['catalog.json', 'topics.json'])

    def test_personal_progress_engine_and_its_fixtures_are_absent(self):
        for path in ('scripts/learning_state.py', 'tests/test_learning_state.py',
                     'state/learning-state.schema.json', 'state/learning-state.example.json',
                     'state/learning-ledger.md', 'vi/state/learning-ledger.md', 'tests/fixtures/low-result.json'):
            with self.subTest(path=path): self.assertFalse((ROOT/path).exists())
        skill = (ROOT/'skills/cs-daily-deep-study/SKILL.md').read_text()
        self.assertNotIn('legacy state', skill)
        self.assertNotIn('assessment', skill)


if __name__ == '__main__': unittest.main()
