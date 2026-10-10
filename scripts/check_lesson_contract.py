#!/usr/bin/env python3
"""Check mechanical page rules; task granularity and teaching quality need review."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def prose(text):
    """Blank fenced examples while retaining line numbers for useful diagnostics."""
    fence = None
    result = []
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            result.append('\n' if line.endswith('\n') else '')
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]; result.append('\n' if line.endswith('\n') else '')
        else:
            result.append(line)
    return ''.join(result)


class Answers(HTMLParser):
    def __init__(self, label):
        super().__init__(); self.label = label; self.stack = []; self.count = 0

    def fail(self, message):
        raise ValueError(f'{self.label}:{self.getpos()[0]}: {message}')

    def handle_starttag(self, tag, attrs):
        if tag == 'details':
            if any(name == 'open' for name, _ in attrs):
                self.fail('answer must be closed by default; remove the open attribute')
            self.stack.append({'started': False, 'ended': False}); self.count += 1
        elif tag == 'summary':
            if not self.stack: self.fail('summary is outside an answer')
            if self.stack[-1]['started']: self.fail('answer has more than one summary')
            self.stack[-1]['started'] = True

    def handle_endtag(self, tag):
        if tag == 'summary':
            if not self.stack or not self.stack[-1]['started'] or self.stack[-1]['ended']:
                self.fail('closing summary has no opening tag')
            self.stack[-1]['ended'] = True
        elif tag == 'details':
            if not self.stack: self.fail('closing details has no opening tag')
            state = self.stack.pop()
            if not state['started']: self.fail('answer needs a summary')
            if not state['ended']: self.fail('unclosed answer summary')


def check_text(text, label='lesson'):
    text = prose(text)
    for number, line in enumerate(text.splitlines(), 1):
        if re.search('[—–]', line):
            raise ValueError(f'{label}:{number}: use a plain hyphen instead of a typographic dash')
    for summary in re.finditer(r'</summary>', text, flags=re.I):
        if not text[summary.end():].startswith('\n\n'):
            number = text[:summary.start()].count('\n')+1
            raise ValueError(f'{label}:{number}: put a blank line after summary so Markdown renders')
    parser = Answers(label); parser.feed(text); parser.close()
    if parser.stack: raise ValueError(f'{label}: unclosed answer details')
    if not parser.count: raise ValueError(f'{label}: no worked answer blocks')
    return parser.count


def main():
    count = 0
    for entry in json.loads((ROOT/'lessons/catalog.json').read_text())['lessons']:
        for prefix in ('', 'vi/'):
            path = Path(prefix+'lessons')/entry['id']/'lesson.md'
            count += check_text((ROOT/path).read_text(encoding='utf-8'), path.as_posix())
    print(f'{count} source answer blocks are balanced and closed; prose typography is valid. '
          'Review prompt/answer meaning and granularity separately.')


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError) as error: raise SystemExit(str(error))
