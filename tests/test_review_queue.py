"""Verify public-calendar retrieval scheduling without personal state."""
from copy import deepcopy
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/review_queue.py'
spec = importlib.util.spec_from_file_location('review_queue', SCRIPT)
review_queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review_queue)


def lesson(key, published_on):
    return {
        'id': key, 'date': published_on, 'title': {'en': key, 'vi': f'Bài {key}'},
        'files': [f'lessons/{key}/lesson.md', f'vi/lessons/{key}/lesson.md'],
        'recall': [
            {'id': f'question-{number}',
             'question': {'en': f'Question {number}?', 'vi': f'Câu hỏi {number}?'},
             'answer': {'en': f'Answer {number}.', 'vi': f'Đáp án {number}.'}}
            for number in range(1, 4)
        ],
    }


class ReviewQueueTests(unittest.TestCase):
    def test_exact_intervals_prioritize_recent_lessons_and_cap_at_three(self):
        on = date(2026, 10, 22)
        entries = [lesson(f'age-{age}', (on - timedelta(days=age)).isoformat())
                   for age in (21, 7, 3, 1)]
        queue = review_queue.select_reviews(entries, on)
        self.assertEqual([row['lesson_id'] for row in queue['reviews']],
                         ['age-1', 'age-3', 'age-7'])
        self.assertEqual([row['offset_days'] for row in queue['reviews']], [1, 3, 7])
        self.assertTrue(all(row['overdue_days'] == 0 for row in queue['reviews']))
        self.assertEqual([row['recall_id'] for row in queue['reviews']],
                         ['question-1', 'question-2', 'question-3'])
        self.assertEqual(queue['timezone'], 'Asia/Bangkok')

    def test_calendar_rotation_keeps_day_21_from_starving_under_three_question_limit(self):
        older_intervals = set()
        for day in (22, 23, 24):
            on = date(2026, 10, day)
            entries = [lesson(f'age-{age}', (on - timedelta(days=age)).isoformat())
                       for age in (1, 3, 7, 21)]
            queue = review_queue.select_reviews(entries, on)
            self.assertEqual(len(queue['reviews']), 3)
            self.assertEqual(queue['reviews'][0]['offset_days'], 1)
            self.assertTrue(all(row['overdue_days'] == 0 for row in queue['reviews']))
            older_intervals.update(row['offset_days'] for row in queue['reviews'][1:])
        self.assertEqual(older_intervals, {3, 7, 21})

    def test_missed_three_days_is_deterministic_and_never_duplicates_a_lesson(self):
        entries = [lesson('recent', '2026-10-06'),
                   lesson('previous', '2026-10-04'),
                   lesson('older', '2026-09-30'),
                   lesson('long-term', '2026-09-16')]
        before = deepcopy(entries)
        first = review_queue.select_reviews(entries, '2026-10-10')
        second = review_queue.select_reviews(entries, '2026-10-10')
        self.assertEqual(first, second)
        self.assertEqual(entries, before)
        self.assertEqual([row['lesson_id'] for row in first['reviews']],
                         ['recent', 'previous', 'older'])
        self.assertEqual([row['overdue_days'] for row in first['reviews']], [3, 3, 3])
        self.assertEqual(len({row['lesson_id'] for row in first['reviews']}), 3)

    def test_future_today_unpublished_and_non_bilingual_pages_are_excluded(self):
        draft = lesson('draft', '2026-10-01')
        draft['published'] = False
        incomplete = lesson('incomplete', '2026-10-01')
        incomplete['files'].pop()
        entries = [lesson('future', '2026-10-11'), lesson('today', '2026-10-10'),
                   draft, incomplete, lesson('prior', '2026-10-09')]
        queue = review_queue.select_reviews(entries, '2026-10-10')
        self.assertEqual([row['lesson_id'] for row in queue['reviews']], ['prior'])

    def test_later_intervals_do_not_pull_in_lessons_before_their_due_date(self):
        entries = [lesson('yesterday', '2026-10-09'), lesson('two-days', '2026-10-08')]
        self.assertEqual(len(review_queue.select_reviews(entries, '2026-10-10')['reviews']), 1)
        self.assertEqual(len(review_queue.select_reviews(entries, '2026-10-11')['reviews']), 2)

    def test_question_rotation_and_catalog_order_tie_breaking(self):
        entries = [lesson('first', '2026-10-01'), lesson('second', '2026-10-01')]
        queues = [review_queue.select_reviews(entries, f'2026-10-0{day}')
                  for day in (2, 3, 4, 5)]
        self.assertEqual([queue['reviews'][0]['lesson_id'] for queue in queues], ['first'] * 4)
        self.assertEqual([queue['reviews'][0]['recall_id'] for queue in queues],
                         ['question-1', 'question-2', 'question-3', 'question-1'])

    def test_empty_catalog_and_first_day_have_no_reviews(self):
        self.assertEqual(review_queue.select_reviews([], '2026-10-06')['reviews'], [])
        self.assertEqual(review_queue.select_reviews([lesson('first', '2026-10-06')],
                                                    '2026-10-06')['reviews'], [])

    def test_malformed_catalog_and_dates_fail_instead_of_silently_scheduling(self):
        base = lesson('first', '2026-10-06')
        cases = []
        for field, value in [('date', '2026-02-30'), ('date', '20261006'),
                             ('id', '../first'), ('id', 'a' * 81), ('published', 'yes'),
                             ('files', 'lessons/first/lesson.md'), ('recall', [])]:
            entry = deepcopy(base)
            entry[field] = value
            cases.append([entry])
        for field, value in [('id', ''), ('question', {'en': 'Question'}),
                             ('answer', {'en': 'Answer', 'vi': '  '})]:
            entry = deepcopy(base)
            entry['recall'][0][field] = value
            cases.append([entry])
        duplicate_recall = deepcopy(base)
        duplicate_recall['recall'][1]['id'] = duplicate_recall['recall'][0]['id']
        cases += [[duplicate_recall], [deepcopy(base), deepcopy(base)], {}, [None]]
        for entries in cases:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                review_queue.select_reviews(entries, '2026-10-10')
        for on in ('2026-13-01', '20261010', None):
            with self.subTest(on=on), self.assertRaises(ValueError):
                review_queue.select_reviews([base], on)

    def test_markdown_places_prompts_before_collapsible_bilingual_answers(self):
        queue = review_queue.select_reviews([lesson('first', '2026-10-06')], '2026-10-07')
        for lang, question, answer in [('en', 'Question 1?', 'Answer 1.'),
                                       ('vi', 'Câu hỏi 1?', 'Đáp án 1.')]:
            text = review_queue.render_markdown(queue, lang)
            self.assertLess(text.index(question), text.index('<details>'))
            self.assertGreater(text.index(answer), text.index('<summary>'))
        self.assertIn('Chưa có bài trước', review_queue.render_markdown(
            review_queue.select_reviews([], '2026-10-07'), 'vi'))

    def test_cli_reads_only_catalog_and_reports_errors_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / 'catalog.json'
            catalog.write_text(json.dumps({'lessons': [lesson('first', '2026-10-06')]}),
                               encoding='utf-8')
            before = catalog.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), '--catalog', str(catalog),
                                     '--on', '2026-10-07'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['reviews'][0]['lesson_id'], 'first')
            self.assertEqual(catalog.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [catalog])
            bad = subprocess.run([sys.executable, str(SCRIPT), '--catalog', str(catalog),
                                  '--on', '2026-02-30'], capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('invalid calendar date', bad.stderr)
            self.assertNotIn('Traceback', bad.stderr)


if __name__ == '__main__':
    unittest.main()
