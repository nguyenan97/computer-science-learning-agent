#!/usr/bin/env python3
"""Generate the IUH self-study map, original course questions and catalog coverage."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ('master', 'doctoral')


def validate_topics(data):
    topics = data['topics']
    ids = [t['id'] for t in topics]
    if not ids or any(not isinstance(key, str) or not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*', key) for key in ids) or len(ids) != len(set(ids)):
        raise ValueError('topic IDs must be safe, nonempty and unique')
    courses = {c['id']: c for c in data['courses']}
    if len(courses) != len(data['courses']): raise ValueError('duplicate course ID')
    sources = {s['id']: s for s in data['sources']}
    for course in courses.values():
        if (course['level'] not in LEVELS or course['area'] not in data['areas']
                or course['source_id'] not in sources or sources[course['source_id']]['level'] != course['level']):
            raise ValueError('course requires a matching level, source and area')
        for field in ('title', 'question'):
            if any(not isinstance(course[field].get(lang), str) or not course[field][lang].strip() for lang in ('en', 'vi')):
                raise ValueError('course title/question must be bilingual')
    lookup = {t['id']: t for t in topics}
    mapped = set()
    for topic in topics:
        for field in ('title', 'objective', 'practice'):
            if any(not isinstance(topic[field].get(lang), str) or not topic[field][lang].strip() for lang in ('en', 'vi')):
                raise ValueError(f'{topic["id"]}: incomplete bilingual {field}')
        if topic['level'] not in LEVELS or topic['area'] not in data['areas'] or topic['day_type'] not in ('build', 'paper'):
            raise ValueError('topic requires level, area and day_type')
        for course_id in topic['course_ids']:
            if course_id not in courses or courses[course_id]['level'] != topic['level']:
                raise ValueError('topic must map to existing courses of the same level')
            mapped.add(course_id)
        if any(parent not in lookup for parent in topic['prerequisites']):
            raise ValueError('unknown prerequisite topic')
        if len(topic['prerequisites']) != len(set(topic['prerequisites'])):
            raise ValueError('duplicate prerequisites')
        if topic['level'] == 'master' and any(lookup[p]['level'] == 'doctoral' for p in topic['prerequisites']):
            raise ValueError('master topics cannot depend on doctoral topics')
    if set(courses) != mapped: raise ValueError('every course/component must have a planned self-study unit')
    visited, visiting = set(), set()
    def visit(key):
        if key in visiting: raise ValueError('cyclic topic prerequisites')
        if key in visited: return
        visiting.add(key)
        for parent in lookup[key]['prerequisites']: visit(parent)
        visiting.remove(key); visited.add(key)
    for key in ids: visit(key)
    return topics


def covered_topics(data, entries, on=None):
    lookup = {t['id']: t for t in validate_topics(data)}
    covered = set()
    for entry in entries:
        keys = entry.get('topic_ids')
        if not isinstance(keys, list) or not keys or any(not isinstance(k, str) or k not in lookup for k in keys) or len(keys) != len(set(keys)):
            raise ValueError(f'{entry["id"]}: topic_ids must name unique inventory topics')
        if entry.get('day_type') not in ('build', 'paper'): raise ValueError('lesson requires build or paper day_type')
        if entry.get('published', True) is not True: raise ValueError('drafts belong outside the public catalog')
        if on is None or entry['date'] <= on: covered.update(keys)
    return covered


def coverage(data, entries, on=None):
    covered = covered_topics(data, entries, on)
    groups = defaultdict(list)
    for t in data['topics']: groups[(t['level'], t['area'])].append(t['id'])
    rows = []
    for (level, area), keys in sorted(groups.items(), key=lambda x: (LEVELS.index(x[0][0]), x[0][1])):
        count = len(set(keys) & covered)
        rows.append({'level': level, 'area': area, 'covered': count, 'planned': len(keys), 'percent': round(100 * count / len(keys), 1)})
    return {'covered_topic_ids': sorted(covered), 'covered': len(covered), 'planned': len(data['topics']), 'by_area': rows}


def render(data, language, entries=None):
    topics = validate_topics(data)
    entries = entries if entries is not None else json.loads((ROOT/'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
    progress = coverage(data, entries)
    covered = set(progress['covered_topic_ids'])
    labels = {'en': ('Master', 'Doctoral', 'Area', 'Published topics / planned', 'Coverage'),
              'vi': ('Thạc sĩ', 'Tiến sĩ', 'Nhóm', 'Chủ đề có bài / đã hoạch định', 'Độ phủ')}[language]
    title = 'IUH self-study topic map' if language == 'en' else 'Bản đồ tự học theo đề cương IUH'
    explanation = ('Mapped to the course-name inventory of IUH master (2020) and doctoral (October 2022) outlines. '
                   'Prerequisites and study objectives are project design. Coverage counts published lesson artifacts, not mastery, credits or degrees. '
                   'Elective names are included as optional breadth; this is not an official graduation plan.' if language == 'en' else
                   'Map theo danh sách tên học phần trong đề cương IUH thạc sĩ (2020) và tiến sĩ (tháng 10/2022). '
                   'Prerequisite và mục tiêu tự học do project thiết kế. Độ phủ đếm bài đã xuất bản, không phải mức nắm vững, tín chỉ hay bằng cấp. '
                   'Có cả tên học phần tự chọn để mở rộng kiến thức; đây không phải kế hoạch tốt nghiệp chính thức.')
    lines = [f'# {title}', '', '<!-- Generated from topics.json and lessons/catalog.json. -->', '', explanation, '',
             f'| {labels[0]} / {labels[1]} | {labels[2]} | {labels[3]} | {labels[4]} |', '|---|---|---:|---:|']
    for row in progress['by_area']:
        lines.append(f'| {labels[LEVELS.index(row["level"])]} | {data["areas"][row["area"]][language]} | {row["covered"]}/{row["planned"]} | {row["percent"]:.1f}% |')
    total = 'Total planned units' if language == 'en' else 'Tổng chủ đề đã hoạch định'
    lines += ['', f'**{total}: {progress["covered"]}/{progress["planned"]}.**', '',
              '[Course inventory and original study questions](topic-notes.md)' if language == 'en' else '[Danh sách học phần và câu hỏi tự học viết mới](topic-notes.md)', '']
    lookup = {t['id']: t for t in topics}
    for topic in topics:
        status = ('Published' if language == 'en' else 'Đã có bài') if topic['id'] in covered else ('Planned' if language == 'en' else 'Chưa có bài')
        lines += [f'## {topic["title"][language]}', '', f'- **{status}** · {labels[LEVELS.index(topic["level"])]} · {data["areas"][topic["area"]][language]} · `{topic["day_type"]}`',
                  '- **' + ('Foundations' if language == 'en' else 'Nền tảng') + ':** ' + (', '.join(lookup[p]['title'][language] for p in topic['prerequisites']) or '—'),
                  '- **' + ('Objective' if language == 'en' else 'Mục tiêu') + ':** ' + topic['objective'][language],
                  '- **' + ('Practice' if language == 'en' else 'Thực hành') + ':** ' + topic['practice'][language], '']
    return '\n'.join(lines)


def render_notes(data, language):
    labels = ('Master', 'Doctoral') if language == 'en' else ('Thạc sĩ', 'Tiến sĩ')
    lines = ['# ' + ('IUH course-name inventory and original study questions' if language == 'en' else 'Danh sách tên học phần IUH và câu hỏi tự học viết mới'), '',
             '<!-- Generated factual names/codes and original project questions; no syllabus descriptions reproduced. -->', '',
             ('Course names and codes come from the repository’s historical condensed tables. The original PDFs have not been independently reverified. '
              'The questions below are newly written project prompts, not IUH outcomes or syllabus text. The elective pool is retained for optional breadth.' if language == 'en' else
              'Tên và mã học phần lấy từ bảng rút gọn lịch sử trong repo. PDF gốc chưa được kiểm chứng lại độc lập. '
              'Các câu hỏi dưới đây do project viết mới, không phải chuẩn đầu ra hay nội dung đề cương IUH. Giữ cả nhóm tự chọn để mở rộng khi cần.'), '']
    for level in LEVELS:
        lines += [f'## {labels[LEVELS.index(level)]}', '',
                  '| ' + ('Source code | Course/component | Original study question' if language == 'en' else 'Mã trong nguồn | Học phần/thành phần | Câu hỏi tự học viết mới') + ' |', '|---|---|---|']
        for course in data['courses']:
            if course['level'] == level:
                lines.append(f'| {" / ".join(course["source_codes"])} | {course["title"][language]} | {course["question"][language]} |')
        lines.append('')
    lines += [('The historical literature-review table contains codes 6201301 and 6201302; this inventory preserves the ambiguity. Research components mean preparation in reading, reproduction and writing, not completion of a thesis or a publication.' if language == 'en' else
               'Bảng tổng quan tài liệu lịch sử chứa mã 6201301 và 6201302; bản đồ giữ nguyên điểm chưa rõ này. Các thành phần nghiên cứu là chuẩn bị kỹ năng đọc, reproduce và viết, không phải đã hoàn thành luận văn, luận án hay công bố.'), '',
              '[Topic map](topic-map.md) · [Sources and licensing](../docs/content-provenance.md)' if language == 'en' else '[Bản đồ chủ đề](topic-map.md) · [Nguồn và giấy phép](../docs/content-provenance.md)', '']
    return '\n'.join(lines)


def generate(root=ROOT, check=False):
    data = json.loads((root/'references/topics.json').read_text(encoding='utf-8'))
    entries = json.loads((root/'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
    outputs = []
    for lang, prefix in [('en', ''), ('vi', 'vi/')]:
        outputs += [(root/f'{prefix}references/topic-map.md', render(data, lang, entries)),
                    (root/f'{prefix}references/topic-notes.md', render_notes(data, lang))]
    if check:
        for path, text in outputs:
            if not path.is_file() or path.read_text(encoding='utf-8') != text:
                raise ValueError(f'{path.relative_to(root)} is stale; run python scripts/add_lesson_navigation.py')
    else:
        for path, text in outputs: path.write_text(text, encoding='utf-8')
    return len(outputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try: generate(check=args.check)
    except (ValueError, KeyError, OSError) as error: raise SystemExit(str(error))
    print('Bilingual IUH map, course questions and publication coverage are up to date.')


if __name__ == '__main__': main()
