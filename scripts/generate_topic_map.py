#!/usr/bin/env python3
"""Generate bilingual topic guidance from the topic inventory; no network."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_topics(data):
    topics = data['topics']
    ids = [topic['id'] for topic in topics]
    if not ids or any(not isinstance(key, str) or not key.strip() for key in ids) or len(ids) != len(set(ids)):
        raise ValueError('topic IDs must be nonempty and unique')
    lookup = {topic['id']: topic for topic in topics}
    for topic in topics:
        for field in ('title', 'objective', 'practice'):
            if any(not isinstance(topic[field].get(lang), str) or not topic[field][lang].strip()
                   for lang in ('en', 'vi')):
                raise ValueError(f'{topic["id"]}: incomplete bilingual {field}')
        if any(parent not in lookup for parent in topic['prerequisites']):
            raise ValueError('unknown prerequisite topic')
    visited, visiting = set(), set()

    def visit(key):
        if key in visiting:
            raise ValueError('cyclic topic prerequisites')
        if key in visited:
            return
        visiting.add(key)
        for parent in lookup[key]['prerequisites']:
            visit(parent)
        visiting.remove(key)
        visited.add(key)

    for key in ids:
        visit(key)
    return topics


def render(data, language):
    topics = validate_topics(data)
    lookup = {topic['id']: topic for topic in topics}
    if language == 'en':
        lines = ['# Technical topic map', '',
                 '<!-- Generated from topics.json by scripts/generate_topic_map.py. -->', '',
                 'Choose a practical question you want to answer. Each topic below names useful foundations, '
                 'a concrete objective and a way to test your understanding with code or an experiment. '
                 'If a foundation is unfamiliar, start with a small trace or example before the larger task.', '',
                 'Use [topic notes](topic-notes.md) to explore the ideas further. '
                 'The suggested relationships guide your study; you can adapt them to what you already understand.', '']
        labels = ('Useful foundations', 'Learning objective', 'Practice')
    else:
        lines = ['# Bản đồ chủ đề kỹ thuật', '',
                 '<!-- Generated from topics.json by scripts/generate_topic_map.py. -->', '',
                 'Chọn một câu hỏi thực tế bạn muốn trả lời. Mỗi chủ đề bên dưới nêu nền tảng hữu ích, '
                 'mục tiêu cụ thể và cách kiểm tra hiểu biết bằng code hoặc thí nghiệm. '
                 'Nếu chưa quen một nền tảng, bắt đầu bằng trace hoặc ví dụ nhỏ trước bài lớn.', '',
                 'Dùng [ghi chú theo chủ đề](topic-notes.md) để tìm hiểu sâu hơn. '
                 'Quan hệ gợi ý giúp định hướng học; bạn có thể điều chỉnh theo phần đã hiểu.', '']
        labels = ('Nền tảng hữu ích', 'Mục tiêu học', 'Thực hành')
    for topic in topics:
        lines += [f'## {topic["title"][language]}', '',
                  f'- **{labels[0]}:** ' + (', '.join(lookup[p]['title'][language] for p in topic['prerequisites']) or ('check the basics needed by the task' if language == 'en' else 'kiểm tra nền tảng cần cho tác vụ')),
                  f'- **{labels[1]}:** {topic["objective"][language]}',
                  f'- **{labels[2]}:** {topic["practice"][language]}', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = json.loads((ROOT / 'references/topics.json').read_text(encoding='utf-8'))
    for lang, relative in [('en', 'references/topic-map.md'), ('vi', 'vi/references/topic-map.md')]:
        path = ROOT / relative
        expected = render(data, lang)
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != expected:
                raise SystemExit(f'{relative} is stale; run python scripts/generate_topic_map.py')
        else:
            path.write_text(expected, encoding='utf-8')
    print('English and Vietnamese topic maps are up to date.' if args.check else 'Generated bilingual topic maps.')


if __name__ == '__main__':
    main()
