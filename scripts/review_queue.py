#!/usr/bin/env python3
"""Select dated retrieval prompts from the public catalog, without learner state.

Intervals are 1, 3, 7 and 21 calendar days. Day 1 has first priority; priority
among days 3, 7 and 21 rotates with the calendar date so the three-question
limit does not permanently starve day 21. For each interval, choose the closest
lesson that is due or overdue and has not already appeared in this queue.
Stop after three questions. A missed study day therefore needs
no catch-up log: the next invocation uses the nearest older eligible lesson.
A future lesson, a lesson dated today, or an explicitly unpublished lesson is
never selected. One question per lesson rotates by interval and lateness: exact
day-1/day-3/day-7/day-21 reviews use questions 1/2/3/1 respectively, and each
overdue day advances the question by one, deterministically.

The queue does not know whether a prompt was answered or answered correctly.
It schedules retrieval opportunities, not individual mastery or remediation.
"""
import argparse
from datetime import date, datetime
import json
from pathlib import Path
import re
from study_profile import load_profile, study_date


ROOT = Path(__file__).resolve().parents[1]
TIMEZONE = load_profile()['timezone']
OFFSETS = (1, 3, 7, 21)
MAX_QUESTIONS = 3
LANGUAGES = ('en', 'vi')


def parse_date(value):
    """Accept one unambiguous calendar-date representation."""
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('dates must use YYYY-MM-DD')
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f'invalid calendar date: {value}') from error


def _identifier(value, label):
    if (not isinstance(value, str) or not 1 <= len(value) <= 80
            or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value)):
        raise ValueError(f'{label} must be a safe identifier of 1–80 characters')


def _bilingual(value, label):
    if (not isinstance(value, dict)
            or any(not isinstance(value.get(language), str)
                   or not value[language].strip() for language in LANGUAGES)):
        raise ValueError(f'{label} must contain nonempty en and vi text')


def validate_catalog(entries):
    """Validate retrieval metadata, including drafts and future entries."""
    if not isinstance(entries, list):
        raise ValueError('catalog lessons must be a list')
    lesson_ids = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('catalog lessons must be objects')
        lesson_id = entry.get('id')
        _identifier(lesson_id, 'lesson ID')
        if lesson_id in lesson_ids:
            raise ValueError(f'duplicate lesson ID: {lesson_id}')
        lesson_ids.add(lesson_id)
        parse_date(entry.get('date'))
        _bilingual(entry.get('title'), 'lesson title')
        if 'published' in entry and not isinstance(entry['published'], bool):
            raise ValueError('published must be a boolean')
        files = entry.get('files')
        if not isinstance(files, list) or any(not isinstance(path, str) for path in files):
            raise ValueError('lesson files must be a list of paths')
        recalls = entry.get('recall')
        if not isinstance(recalls, list) or len(recalls) != 3:
            raise ValueError(f'{lesson_id} must have exactly three recall questions')
        recall_ids = set()
        for recall in recalls:
            if not isinstance(recall, dict):
                raise ValueError('recall questions must be objects')
            recall_id = recall.get('id')
            _identifier(recall_id, 'recall ID')
            if recall_id in recall_ids:
                raise ValueError(f'duplicate recall ID in {lesson_id}: {recall_id}')
            recall_ids.add(recall_id)
            _bilingual(recall.get('question'), 'recall question')
            _bilingual(recall.get('answer'), 'recall answer')


def load_catalog(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or 'lessons' not in data:
        raise ValueError('catalog must contain lessons')
    validate_catalog(data['lessons'])
    return data['lessons']


def _published(entry):
    return (entry.get('published', True)
            and f'lessons/{entry["id"]}/lesson.md' in entry['files']
            and f'vi/lessons/{entry["id"]}/lesson.md' in entry['files'])


def select_reviews(entries, on):
    """Return at most three bilingual prompts, with dates and due intervals."""
    validate_catalog(entries)
    if isinstance(on, str):
        on = parse_date(on)
    if not isinstance(on, date) or isinstance(on, datetime):
        raise ValueError('on must be a calendar date')
    candidates = []
    for index, entry in enumerate(entries):
        age = (on - parse_date(entry['date'])).days
        if age >= 1 and _published(entry):
            candidates.append((age, index, entry))
    selected = set()
    reviews = []
    older_offsets = OFFSETS[1:]
    rotation = on.toordinal() % len(older_offsets)
    priority = (OFFSETS[0], *older_offsets[rotation:], *older_offsets[:rotation])
    for offset in priority:
        eligible = [item for item in candidates
                    if item[0] >= offset and item[2]['id'] not in selected]
        if not eligible:
            continue
        age, _, entry = min(eligible, key=lambda item: (item[0] - offset, item[1]))
        recall_index = (OFFSETS.index(offset) + age - offset) % len(entry['recall'])
        recall = entry['recall'][recall_index]
        reviews.append({
            'lesson_id': entry['id'],
            'lesson_date': entry['date'],
            'title': entry['title'],
            'age_days': age,
            'offset_days': offset,
            'overdue_days': age - offset,
            'recall_id': recall['id'],
            'question': recall['question'],
            'answer': recall['answer'],
        })
        selected.add(entry['id'])
        if len(reviews) == MAX_QUESTIONS:
            break
    return {'on': on.isoformat(), 'timezone': TIMEZONE,
            'offsets': list(OFFSETS), 'interval_priority': list(priority), 'reviews': reviews}


def render_markdown(queue, language):
    if language not in LANGUAGES:
        raise ValueError('language must be en or vi')
    heading = 'Review' if language == 'en' else 'Ôn lại'
    instructions = ('You may recall from memory, or open each answer immediately.' if language == 'en'
                    else 'Bạn có thể nhớ lại trước, hoặc mở ngay từng đáp án.')
    lines = [f'## {heading} - {queue["on"]}', '', instructions, '']
    if not queue['reviews']:
        lines.append('No earlier lessons are due.' if language == 'en'
                     else 'Chưa có bài trước đến lịch ôn.')
        return '\n'.join(lines) + '\n'
    summary = 'Answer' if language == 'en' else 'Đáp án'
    for index, review in enumerate(queue['reviews'], 1):
        lines += [f'{index}. {review["question"][language]}', '', '<details>',
                  f'<summary>{summary}</summary>', '',
                  f'**{review["title"][language]}**', '', review['answer'][language],
                  '', '</details>', '']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=ROOT / 'lessons/catalog.json')
    parser.add_argument('--on', default=study_date().isoformat(),
                        help='calendar date YYYY-MM-DD (default: today in Asia/Ho_Chi_Minh)')
    parser.add_argument('--language', choices=LANGUAGES, default='vi',
                        help='Markdown language; JSON always contains both languages')
    parser.add_argument('--format', choices=('json', 'markdown'), default='json')
    args = parser.parse_args(argv)
    try:
        queue = select_reviews(load_catalog(args.catalog), args.on)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.format == 'json':
        print(json.dumps(queue, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(queue, args.language), end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
