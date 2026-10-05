#!/usr/bin/env python3
"""Stage only public documentation and the fixed teaching example for Pages."""
import argparse
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

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

# Docsify routes are not filesystem paths. Resolve local links while staging,
# so the original Markdown still works on GitHub and assets bypass hash routing.
LINK = re.compile(r'(?<!!)\[([^\]]+)\]\(([^\s)]+)(?:\s+([\'"])(.*?)\3)?\)')


def site_links(text, relative, public_paths):
    def replace(match):
        label, target, _, title = match.groups()
        if target.startswith(('/', '#')) or urlsplit(target).scheme:
            return match.group(0)
        parts = urlsplit(target)
        resolved = (Path('/') / relative.parent / parts.path).resolve().relative_to('/')
        if resolved not in public_paths:
            raise ValueError(f'{relative}: link is not published: {target}')
        if resolved.suffix == '.md':
            route = '/' + resolved.as_posix()[:-3]
            if resolved.name == 'README.md':
                route = '/' + resolved.parent.as_posix().removeprefix('.') + '/'
                route = route.replace('//', '/')
            if parts.query: route += '?' + parts.query
            if parts.fragment: route += '#' + parts.fragment
            return f'[{label}]({route}' + (f' "{title}"' if title else '') + ')'
        if parts.query or parts.fragment:
            raise ValueError(f'{relative}: asset links with query/fragment need an absolute URL')
        # Plain relative URLs resolve from the browser document, ignoring its hash.
        # Avoid ./, which Docsify rebases using the last slash inside the hash route.
        return f'[{label}]({resolved.as_posix()} ":ignore")'

    # Leave fenced examples verbatim, including Markdown examples in documentation.
    result=[]; fence=None
    for line in text.splitlines(keepends=True):
        marker=re.match(r'^\s*(`{3,}|~{3,})',line)
        if marker:
            if fence is None: fence=marker[1][0]
            elif marker[1][0]==fence: fence=None
            result.append(line)
        else: result.append(line if fence else LINK.sub(replace,line))
    return ''.join(result)


def lab_archive(source, destination):
    directory=destination/'labs/cost-model/dotnet'
    if not directory.is_dir(): return
    archive=destination/'labs/cost-model/dotnet-lab.zip'
    with ZipFile(archive,'w',compression=ZIP_DEFLATED) as z:
        for path in sorted(directory.rglob('*')):
            if not path.is_file(): continue
            info=ZipInfo('dotnet/'+path.relative_to(directory).as_posix(),date_time=(2026,10,5,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            # Keep filesystem-relative links in the downloadable README.
            z.writestr(info,(source/path.relative_to(destination)).read_bytes())


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
    public_paths={p.relative_to(source) for p in paths}
    for path in paths:
        target=destination/path.relative_to(source)
        target.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix == '.md':
            target.write_text(site_links(path.read_text(),path.relative_to(source),public_paths))
        else: shutil.copyfile(path,target)
    lab_archive(source,destination)
    return len(paths)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(f'Staged {build(ROOT,args.output)} public files.')

if __name__=='__main__': main()
