#!/usr/bin/env python3
"""Stage only public documentation and the fixed teaching example for Pages."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = (
    '.nojekyll', 'index.html', '404.html', 'README.md', '_404.md', '_sidebar.md', '_navbar.md',
    'state/learning-ledger.md', 'state/learning-state.schema.json', 'state/learning-state.example.json',
    'vi/state/learning-ledger.md', 'lessons/boundary-search/lesson.md',
    'lessons/boundary-search/record.json', 'lessons/boundary-search/repository-evidence.json',
    'vi/lessons/boundary-search/lesson.md', 'research/source-checks.json',
    'research/runtime-source-checks.json', 'skills/master-iuh-daily-learning/SKILL.md',
    'skills/master-iuh-daily-learning/evals/cases.json',
    'skills/master-iuh-daily-learning/agents/openai.yaml',
    'lessons/catalog.json',
)
PUBLIC_DOC_DIRS = ('curricula', 'references', 'research', 'vi/curricula', 'vi/references', 'vi/research')
PUBLIC_LAB_FILES = ('check.py','observe.py','starter.py','mentor/hints.md','mentor/solution.py')


def catalog_files(source):
    """Explicit publication list; private work is never discovered by a glob."""
    entries=json.loads((source/'lessons/catalog.json').read_text())['lessons']
    paths=[]
    ids=set()
    for entry in entries:
        if entry['id'] in ids: raise ValueError('duplicate published lesson ID')
        ids.add(entry['id'])
        for name in entry['files']:
            path=Path(name)
            if (path.is_absolute() or '..' in path.parts
                    or not (name.startswith('lessons/') or name.startswith('vi/lessons/') or name.startswith('labs/'))):
                raise ValueError('catalog may publish only lesson and lab paths')
            paths.append(source/path)
    return paths


def build(source, destination):
    source=source.resolve(); destination=destination.resolve()
    if destination.exists(): raise ValueError('output already exists; choose a fresh directory')
    if source.is_relative_to(destination): raise ValueError('output must not contain the source repository')
    paths=[source/p for p in PUBLIC_FILES]
    paths += catalog_files(source)
    paths += [source/'labs/boundary-search'/p for p in PUBLIC_LAB_FILES]
    for directory in PUBLIC_DOC_DIRS:
        paths += list((source/directory).rglob('*.md'))
    paths += [source/'vi'/name for name in ('README.md','_404.md','_sidebar.md','_navbar.md')]
    for path in paths:
        if not path.is_file() or not path.resolve().is_relative_to(source):
            raise ValueError(f'public file missing or outside source: {path}')
        # Reject symlinks in public trees, including parent directory symlinks.
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != source):
            raise ValueError(f'public file must not use symlinks: {path}')
    destination.mkdir(parents=True)
    for path in paths:
        target=destination/path.relative_to(source)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    return len(paths)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(f'Staged {build(ROOT,args.output)} public files.')

if __name__=='__main__': main()
