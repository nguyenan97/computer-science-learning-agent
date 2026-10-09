"""Extract complete named lab fences, and detect page/download source drift.

Only explicitly marked files are runnable inputs. Illustrative snippets and transfer
programs remain separate. The catalog's existing file allowlist owns the required
source/configuration set; no second manifest of lab files is maintained.
"""
from pathlib import Path, PurePosixPath
import re

from check_lesson_parity import without_comments

MARKER = re.compile(r'^<!-- lab-file: (.+) -->$')
FENCE = re.compile(r'^(`{3,}|~{3,})([\w-]*)\s*$')
SUFFIXES = {'.cs', '.csproj', '.json', '.props', '.targets'}


def extract(text, label='lesson'):
    files = {}
    lines = text.splitlines(keepends=True)
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        marker = MARKER.fullmatch(line)
        if not marker:
            # A lab-file marker inside an illustrative fence is not metadata.
            fence = FENCE.fullmatch(line)
            if fence:
                index += 1
                while index < len(lines) and lines[index].strip() != fence[1]:
                    index += 1
            index += 1
            continue
        name = marker[1]
        path = PurePosixPath(name)
        if (path.is_absolute() or path.as_posix() != name or '\\' in name
                or any(part.startswith('.') for part in path.parts)
                or path.suffix not in SUFFIXES):
            raise ValueError(f'{label}: unsafe lab-file path: {name}')
        if name in files:
            raise ValueError(f'{label}: duplicate lab-file: {name}')
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        fence = FENCE.fullmatch(lines[index].strip()) if index < len(lines) else None
        if not fence:
            raise ValueError(f'{label}: lab-file {name} must immediately precede a code fence')
        index += 1
        start = index
        while index < len(lines) and lines[index].strip() != fence[1]:
            index += 1
        if index == len(lines):
            raise ValueError(f'{label}: unclosed lab-file fence: {name}')
        files[name] = ''.join(lines[start:index])
        index += 1
    return files


def comparable(name, text):
    # Comments may be translated, but C# strings and operators must agree.
    return without_comments(text, 'csharp') if name.endswith('.cs') else text.strip()


def page_files(root, entry, lab, language):
    directory = Path(lab['directory'])
    required = {Path(name).relative_to(directory).as_posix() for name in entry['files']
                if Path(name).is_relative_to(directory) and Path(name).suffix in SUFFIXES}
    page = root / ('' if language == 'en' else 'vi') / 'lessons' / entry['id'] / 'lesson.md'
    label = page.relative_to(root).as_posix()
    files = extract(page.read_text(encoding='utf-8'), label)
    missing = required - files.keys()
    extra = files.keys() - required
    if missing or extra:
        raise ValueError(f'{label}: lab-file set differs from catalog; '
                         f'missing={sorted(missing)}, undeclared={sorted(extra)}')
    for name, text in files.items():
        original = (root / directory / name).read_text(encoding='utf-8')
        if comparable(name, text) != comparable(name, original):
            raise ValueError(f'{label}: {name} differs from downloadable lab; '
                             'update the complete fence and source together')
    return files


def write_files(files, destination):
    for name, text in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
