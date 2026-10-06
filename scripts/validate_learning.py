#!/usr/bin/env python3
"""Validate the Codex skill, public catalog, private isolation and local links."""
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit
import yaml

from add_lesson_navigation import validate_catalog as validate_navigation
from build_public_site import build
from learning_state import ROOT, TEMPLATE, validate
from review_queue import validate_catalog as validate_recall

EXCLUDED = {'.git', '.agents', '.learning-private', '.site-build', '.venv', 'work',
            'bin', 'obj', '__pycache__', 'BenchmarkDotNet.Artifacts'}


def validate_skill():
    directory = ROOT / 'skills/cs-daily-deep-study'
    text = (directory / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not match: raise ValueError('skill requires YAML frontmatter')
    metadata = yaml.safe_load(match[1])
    name = metadata.get('name', ''); description = metadata.get('description', '')
    if (not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name)
            or len(name) > 64 or name != directory.name
            or not isinstance(description, str) or not 1 <= len(description) <= 1024):
        raise ValueError('skill name/description violates Agent Skills specification')
    interface = yaml.safe_load((directory / 'agents/openai.yaml').read_text(encoding='utf-8'))['interface']
    if f'${name}' not in interface['default_prompt']:
        raise ValueError('OpenAI default prompt must mention the skill')
    discovered = ROOT / '.agents/skills' / name
    if not discovered.is_dir() or (discovered / 'SKILL.md').resolve() != (directory / 'SKILL.md').resolve():
        raise ValueError('Codex discovery must point to the canonical repository skill')


def validate_private_isolation():
    tracked = subprocess.run(['git', 'ls-files', '--', '.learning-private'], cwd=ROOT,
                             check=True, capture_output=True, text=True)
    if tracked.stdout.strip(): raise ValueError('private learner workspace must not be tracked by Git')
    state = json.loads(TEMPLATE.read_text(encoding='utf-8'))
    validate(state)
    if any(state[key] for key in ('lessons', 'assessments', 'reviews')):
        raise ValueError('legacy public initialization template must remain empty')
    if state['learner'] != {'timezone': 'Asia/Bangkok', 'daily_minutes': None, 'goals': [], 'background': None}:
        raise ValueError('public template must not contain a real learner profile')
    for path in (ROOT / 'tests/fixtures').glob('*.json'):
        fixture = json.loads(path.read_text(encoding='utf-8'))
        if fixture.get('fixture') is not True: raise ValueError(f'{path}: fixture marker missing')
        validate(fixture, allow_fixture=True)


def markdown_links(text):
    fence = None
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        yield from re.findall(r'\[[^\]]*\]\(([^\s)]+)', line)


def validate_links():
    for path in ROOT.rglob('*.md'):
        if any(part in EXCLUDED for part in path.relative_to(ROOT).parts): continue
        for target in markdown_links(path.read_text(encoding='utf-8')):
            parts = urlsplit(target)
            if target.startswith(('/', '#')) or parts.scheme: continue
            clean = unquote(parts.path)
            if clean and not (path.parent / clean).exists():
                raise ValueError(f'{path.relative_to(ROOT)}: broken link {target}')


def main():
    try:
        validate_skill()
        validate_private_isolation()
        entries = json.loads((ROOT / 'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
        validate_navigation(ROOT, entries)
        validate_recall(entries)
        validate_links()
        with tempfile.TemporaryDirectory(prefix='public-validation-') as directory:
            count = build(ROOT, Path(directory) / 'site')
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error))
    print(f'Codex skill, catalog, recall, private isolation and local/public links valid ({count} public files).')
    return 0


if __name__ == '__main__': raise SystemExit(main())
