#!/usr/bin/env python3
"""Stage learner documentation and catalog-declared lab downloads for Pages."""
import argparse
from html import escape
import json
from pathlib import Path, PurePosixPath
import re
import shutil
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = (
    '.nojekyll', 'index.html', 'site.css', 'site.js', '404.html', 'README.md', '_404.md', '_sidebar.md', '_navbar.md',
    'vi/README.md', 'vi/_404.md', 'vi/_sidebar.md', 'vi/_navbar.md',
    'references/topic-map.md', 'references/topic-notes.md', 'references/topics.json',
    'vi/references/topic-map.md', 'vi/references/topic-notes.md', 'lessons/catalog.json',
    'docs/content-provenance.md', 'vi/docs/content-provenance.md',
    'docs/licensing.md', 'vi/docs/licensing.md', 'LICENSE', 'LICENSES/MIT.txt', 'LICENSES/CC-BY-4.0.txt',
    'references/study-profile.json',
    'vendor/README.md', 'vendor/manifest.json',
    'vendor/docsify-4.13.1/vue.css', 'vendor/docsify-4.13.1/docsify.min.js',
    'vendor/docsify-4.13.1/search.min.js', 'vendor/docsify-4.13.1/LICENSE',
    'vendor/prismjs-1.30.0/prism-csharp.min.js', 'vendor/prismjs-1.30.0/prism-python.min.js',
    'vendor/prismjs-1.30.0/prism-typescript.min.js', 'vendor/prismjs-1.30.0/prism-sql.min.js',
    'vendor/prismjs-1.30.0/LICENSE',
)
# Markdown links inside code fences remain examples rather than publication inputs.
LINK = re.compile(r'(!?)\[([^\]]+)\]\(([^\s)]+)(?:\s+([\'"])(.*?)\4)?\)')
PRIVATE_PARTS = {'.learning-private', 'bin', 'obj', '__pycache__', 'node_modules'}
INTERNAL_FILES = {'record.json', 'repository-evidence.json', 'sources.json', 'benchmark-run.txt'}


def safe_path(name, *, lab=False):
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError('catalog paths must be nonempty POSIX paths')
    path = PurePosixPath(name)
    if (path.is_absolute() or '..' in path.parts or path.as_posix() != name
            or any(part.startswith('.') or part in PRIVATE_PARTS for part in path.parts)):
        raise ValueError(f'catalog path must be safe and public: {name}')
    allowed = ('labs/',) if lab else ('lessons/', 'vi/lessons/', 'labs/')
    if not name.startswith(allowed):
        raise ValueError('catalog may publish only lesson and lab paths')
    if path.name in INTERNAL_FILES or path.name.startswith('agent-'):
        raise ValueError(f'agent logs and evidence cannot be published: {name}')
    return Path(path)


def catalog_assets(source):
    """Return explicit public files and archive inputs; never discover lab sources."""
    entries = json.loads((source / 'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
    files = []
    archives = []
    ids = set()
    archive_paths = set()
    for entry in entries:
        if entry.get('published', True) is not True:
            raise ValueError('the public catalog cannot contain unpublished lessons; keep drafts outside it')
        key = entry['id']
        if (not isinstance(key, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key)
                or key in ids):
            raise ValueError('published lesson IDs must be safe and unique')
        ids.add(key)
        declared = [safe_path(name) for name in entry['files']]
        for lang in ('', 'vi/'):
            if Path(f'{lang}lessons/{key}/lesson.md') not in declared:
                raise ValueError(f'catalog must publish both lesson languages: {key}')
        files.extend(declared)
        for lab in entry.get('labs', []):
            if lab['language'] not in ('csharp', 'python', 'tsql'):
                raise ValueError('lab language must be csharp, python or tsql')
            directory = safe_path(lab['directory'], lab=True)
            lab_files = [path for path in declared if path.is_relative_to(directory)]
            if not lab_files:
                raise ValueError(f'lab has no declared source files: {directory}')
            for command in ('check', 'benchmark'):
                argv = lab.get(command)
                if argv is not None and (not isinstance(argv, list) or not argv
                        or any(not isinstance(arg, str) or not arg or '\x00' in arg for arg in argv)):
                    raise ValueError(f'lab {command} must be a nonempty command argument list')
            if 'archive' not in lab:
                continue
            archive = safe_path(lab['archive'], lab=True)
            if archive.suffix != '.zip' or archive in archive_paths or archive in declared:
                raise ValueError('lab archive must be a unique generated ZIP path')
            archive_paths.add(archive)
            archives.append((archive, directory, lab_files))
    files = list(dict.fromkeys(files))
    if archive_paths.intersection(files):
        raise ValueError('generated lab archives cannot also be source files')
    return files, archives


def catalog_files(source):
    """Compatibility helper returning the catalog's explicit publication list."""
    files, _ = catalog_assets(source)
    return [source / path for path in files]


def check_download(target, relative, public_paths):
    """Check project and user Pages ZIP URLs against the staged publication plan."""
    parts = urlsplit(target)
    if not unquote(parts.path).endswith('.zip'):
        return
    if parts.scheme or parts.netloc:
        if not parts.hostname or not parts.hostname.lower().endswith('.github.io'):
            return
    elif not target.startswith('/'):
        return  # Ordinary relative links are resolved by site_links.
    clean = Path(unquote(parts.path).lstrip('/'))
    candidates = {clean}
    if len(clean.parts) > 1:
        candidates.add(Path(*clean.parts[1:]))  # GitHub project Pages repository prefix.
    if not candidates.intersection(public_paths):
        raise ValueError(f'{relative}: advertised lab ZIP is not published: {target}')


def site_links(text, relative, public_paths):
    def replace(match):
        image, label, target, _, title = match.groups()
        check_download(target, relative, public_paths)
        parts = urlsplit(target)
        if target.startswith('#') or parts.scheme or parts.netloc:
            return match.group(0)
        root_route = target.startswith('/')
        parent = Path('/') if root_route else Path('/') / relative.parent
        resolved = (parent / unquote(parts.path).lstrip('/')).resolve().relative_to('/')
        if not image and root_route and resolved not in public_paths:
            candidates = [resolved / 'README.md'] if parts.path.endswith('/') else [
                Path(resolved.as_posix() + '.md'), resolved / 'README.md']
            resolved = next((path for path in candidates if path in public_paths), resolved)
        if resolved not in public_paths:
            raise ValueError(f'{relative}: link is not published: {target}')
        if image:
            if parts.query or parts.fragment:
                raise ValueError(f'{relative}: asset links with query/fragment need an absolute URL')
            # Docsify rebases Markdown images using the current hash route and does
            # not support :ignore for images. HTML src resolves from the site base.
            attributes = f'src="{escape(resolved.as_posix(), quote=True)}" alt="{escape(label, quote=True)}"'
            if title and title != ':ignore':
                attributes += f' title="{escape(title, quote=True)}"'
            return f'<img {attributes}>'
        if resolved.suffix == '.md':
            route = '/' + resolved.as_posix()[:-3]
            if resolved.name == 'README.md':
                route = '/' + resolved.parent.as_posix().removeprefix('.') + '/'
                route = route.replace('//', '/')
            if parts.query:
                route += '?' + parts.query
            if parts.fragment:
                route += '#' + parts.fragment
            return f'[{label}]({route}' + (f' "{title}"' if title else '') + ')'
        if parts.query or parts.fragment:
            raise ValueError(f'{relative}: asset links with query/fragment need an absolute URL')
        return f'[{label}]({resolved.as_posix()} ":ignore")'

    result = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1][0]
            elif marker[1][0] == fence:
                fence = None
            result.append(line)
        else:
            result.append(line if fence else LINK.sub(replace, line))
    return ''.join(result)


def lab_archive(source, destination, archive, directory, files):
    """Package only allowlisted source bytes with a reproducible ZIP timestamp."""
    target = destination / archive
    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, 'w', compression=ZIP_DEFLATED) as zipped:
        for path in sorted(files):
            name = directory.name + '/' + path.relative_to(directory).as_posix()
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            # Downloadable Markdown uses original filesystem-relative links.
            zipped.writestr(info, (source / path).read_bytes())


def build(source, destination):
    source = source.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise ValueError('output already exists; choose a fresh directory')
    if source.is_relative_to(destination):
        raise ValueError('output must not contain the source repository')
    catalog_paths, archives = catalog_assets(source)
    paths = list(dict.fromkeys([*(source / p for p in PUBLIC_FILES), *(source / p for p in catalog_paths)]))
    for path in paths:
        if not path.is_file() or not path.resolve().is_relative_to(source):
            raise ValueError(f'public file missing or outside source: {path}')
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != source):
            raise ValueError(f'public file must not use symlinks: {path}')
    public_paths = {path.relative_to(source) for path in paths} | {archive for archive, _, _ in archives}
    # Validate and render before creating outputs, so broken publication plans fail cleanly.
    rendered = {path: site_links(path.read_text(encoding='utf-8'), path.relative_to(source), public_paths)
                for path in paths if path.suffix == '.md'}
    destination.mkdir(parents=True)
    for path in paths:
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path in rendered:
            target.write_text(rendered[path], encoding='utf-8')
        else:
            shutil.copyfile(path, target)
    for archive, directory, files in archives:
        lab_archive(source, destination, archive, directory, files)
    return len(public_paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        count = build(ROOT, args.output)
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error))
    print(f'Staged {count} public files including catalog lab downloads.')


if __name__ == '__main__':
    main()
