#!/usr/bin/env python3
"""Check lesson structure and executable code parity; meaning needs bilingual review."""
import argparse
import io
import json
from pathlib import Path
import re
import tokenize

ROOT = Path(__file__).resolve().parents[1]
PROSE_FENCES = {'', 'text', 'plaintext', 'markdown', 'md', 'output'}


def without_comments(code, language):
    """Strip comments without treating comment markers inside strings as comments."""
    if language in ('python', 'py'):
        return [(token.type, token.string) for token in tokenize.generate_tokens(io.StringIO(code).readline)
                if token.type not in (tokenize.COMMENT, tokenize.NL, tokenize.ENCODING)]
    result = []
    index = 0
    quote = None
    verbatim = False
    while index < len(code):
        char = code[index]
        if quote is None and language in ('csharp', 'cs') and code.startswith('"""', index):
            # Raw C# literals may contain ordinary quotes and comment-like text.
            # Preserve the whole literal, including interpolated raw-string text.
            count = 3
            while index + count < len(code) and code[index + count] == '"':
                count += 1
            delimiter = '"' * count
            end = code.find(delimiter, index + count)
            if end < 0:
                raise ValueError('unterminated C# raw string')
            result.append(code[index:end + count]); index = end + count; continue
        if quote:
            result.append(char)
            if char == quote:
                if language in ('sql', 'tsql') or verbatim:
                    if index + 1 < len(code) and code[index + 1] == quote:
                        result.append(code[index + 1]); index += 2; continue
                quote = None; verbatim = False
            elif char == '\\' and language not in ('sql', 'tsql') and not verbatim and index + 1 < len(code):
                result.append(code[index + 1]); index += 2; continue
            index += 1; continue
        if char in ('"', "'", '`'):
            quote = char
            verbatim = language in ('csharp', 'cs') and char == '"' and index > 0 and code[index - 1] == '@'
            result.append(char); index += 1; continue
        line_comment = ('--' if language in ('sql', 'tsql') else
                        '#' if language in ('bash', 'sh', 'shell', 'powershell', 'ps1', 'yaml', 'yml') else '//')
        if code.startswith(line_comment, index):
            newline = code.find('\n', index)
            index = len(code) if newline < 0 else newline
            continue
        if code.startswith('/*', index) and language not in ('bash', 'sh', 'shell'):
            end = code.find('*/', index + 2)
            if end < 0:
                raise ValueError('unterminated block comment')
            result.append(' ')
            index = end + 2; continue
        result.append(char); index += 1
    return tuple(line.rstrip() for line in ''.join(result).splitlines() if line.strip())


def structure(text):
    headings = []
    tables = []
    fences = []
    fence = None
    language = None
    block = []
    table = []
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fences.append((language, '\n'.join(block) + '\n'))
                fence = None; block = []
            else:
                block.append(line)
            continue
        if marker:
            if table: tables.append(len(table)); table = []
            fence = marker[1]; language = marker[2].strip().lower().split(' ', 1)[0]
            continue
        heading = re.match(r'^(#{1,6})\s+', line)
        if heading: headings.append(len(heading[1]))
        if line.lstrip().startswith('|') and line.rstrip().endswith('|'):
            table.append(line)
        elif table:
            tables.append(len(table)); table = []
    if fence: raise ValueError('unclosed code fence')
    if table: tables.append(len(table))
    return headings, tables, fences


def compare(en, vi):
    left = structure(en); right = structure(vi)
    if left[0] != right[0]: raise ValueError('heading levels/order differ')
    if left[1] != right[1]: raise ValueError('table row counts/order differ')
    if [language for language, _ in left[2]] != [language for language, _ in right[2]]:
        raise ValueError('code fence languages/order differ')
    for index, ((language, a), (_, b)) in enumerate(zip(left[2], right[2]), 1):
        if language not in PROSE_FENCES and without_comments(a, language) != without_comments(b, language):
            raise ValueError(f'executable code differs in fence {index} ({language})')


def check(root=ROOT):
    entries = json.loads((root / 'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
    for entry in entries:
        try:
            compare((root / f'lessons/{entry["id"]}/lesson.md').read_text(encoding='utf-8'),
                    (root / f'vi/lessons/{entry["id"]}/lesson.md').read_text(encoding='utf-8'))
        except (ValueError, tokenize.TokenError) as error:
            raise ValueError(f'{entry["id"]}: {error}') from error
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try: count = check()
    except (ValueError, OSError) as error: raise SystemExit(str(error))
    print(f'{count} EN/VI lesson structures and executable code blocks match; review translation meaning separately.')


if __name__ == '__main__': main()
