#!/usr/bin/env python3
"""Generate bottom-of-lesson related reading and previous/next links from catalog."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- LESSON_NAVIGATION_START -->'
END = '<!-- LESSON_NAVIGATION_END -->'


def page_path(entry, language):
    return PurePosixPath(('vi/' if language == 'vi' else '') + f'lessons/{entry["id"]}/lesson.md')


def validate_catalog(root, entries):
    ids = [entry['id'] for entry in entries]
    if not ids or any(not isinstance(key, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key) for key in ids) or len(ids) != len(set(ids)):
        raise ValueError('catalog lesson IDs must be nonempty, safe and unique')
    for entry in entries:
        for lang in ('en', 'vi'):
            title = entry['title'].get(lang)
            if not isinstance(title, str) or not title.strip():
                raise ValueError('lesson titles must be bilingual')
            page = page_path(entry, lang)
            if page.as_posix() not in entry['files'] or not (root / page).is_file():
                raise ValueError(f'catalog lesson page missing or unpublished: {page}')
            if (not (root / page).resolve().is_relative_to(root.resolve())
                    or any((root / parent).is_symlink() for parent in (page, *page.parents)
                           if parent != PurePosixPath('.'))):
                raise ValueError(f'catalog lesson page must stay within the repository and cannot use symlinks: {page}')
            if not isinstance(entry['related'][lang], list) or not entry['related'][lang]:
                raise ValueError('each lesson needs useful related reading in both languages')
            for item in entry['related'][lang]:
                path = PurePosixPath(item['path'])
                if (path.is_absolute() or '..' in path.parts or path.suffix != '.md'
                        or path.parts[0] not in ('references', 'lessons', 'labs', 'vi')
                        or any(part.startswith('.') for part in path.parts)):
                    raise ValueError('related reading must use safe repository Markdown paths')
                if (not (root / path).is_file() or not (root / path).resolve().is_relative_to(root.resolve())
                        or any((root / parent).is_symlink() for parent in (path, *path.parents) if parent != PurePosixPath('.'))):
                    raise ValueError(f'related reading missing or outside repository: {path}')
                if any(not isinstance(item.get(field), str) or not item[field].strip() for field in ('title', 'description')):
                    raise ValueError('related reading requires a title and useful description')


def relative_link(page, target):
    return Path(os.path.relpath(target, page.parent)).as_posix()


def render(entries, index, lang):
    entry = entries[index]
    page = page_path(entry, lang)
    heading = 'Related reading' if lang == 'en' else 'Nội dung liên quan'
    home = PurePosixPath('vi/README.md' if lang == 'vi' else 'README.md')
    home_label = 'All lessons' if lang == 'en' else 'Danh sách bài học'
    lines = [START, f'## {heading}', '']
    for item in entry['related'][lang]:
        lines.append(f'- [{item["title"]}]({relative_link(page, PurePosixPath(item["path"]))}) — {item["description"]}')
    lines += ['', '---', '']
    links = []
    if index > 0:
        previous = entries[index - 1]
        label = 'Previous' if lang == 'en' else 'Bài trước'
        links.append(f'[← {label}: {previous["title"][lang]}]({relative_link(page, page_path(previous, lang))})')
    links.append(f'[{home_label}]({relative_link(page, home)})')
    if index + 1 < len(entries):
        following = entries[index + 1]
        label = 'Next' if lang == 'en' else 'Bài sau'
        links.append(f'[{label}: {following["title"][lang]} →]({relative_link(page, page_path(following, lang))})')
    lines += [' · '.join(links), END]
    return '\n'.join(lines) + '\n'


def updated_text(text, footer):
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise ValueError('lesson footer markers must occur exactly once')
        start, end = text.index(START), text.index(END) + len(END)
        if start >= end or text[end:].strip():
            raise ValueError('lesson navigation must be the final section')
        text = text[:start]
    return text.rstrip() + '\n\n' + footer


def generate(root, check=False):
    entries = json.loads((root / 'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
    validate_catalog(root, entries)
    # Prepare all outputs before writing, so malformed inputs cannot partly update pages.
    outputs = []
    for index, entry in enumerate(entries):
        for lang in ('en', 'vi'):
            path = root / page_path(entry, lang)
            old = path.read_text(encoding='utf-8')
            outputs.append((path, old, updated_text(old, render(entries, index, lang))))
    if check:
        stale = [str(path.relative_to(root)) for path, old, new in outputs if old != new]
        if stale:
            raise ValueError('lesson navigation is stale; run python scripts/add_lesson_navigation.py: ' + ', '.join(stale))
    else:
        for path, old, new in outputs:
            if old != new:
                path.write_text(new, encoding='utf-8')
    return len(outputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        count = generate(ROOT, args.check)
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error))
    print(f'{count} bilingual lesson footers ' + ('are up to date.' if args.check else 'updated.'))


if __name__ == '__main__':
    main()
