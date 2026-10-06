#!/usr/bin/env python3
"""Run the required lesson checks, including labs from their downloadable ZIPs."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

from build_public_site import build

ROOT = Path(__file__).resolve().parents[1]
SDK_VERSION = '10.0.401'
IGNORED_LAB_OUTPUTS = shutil.ignore_patterns('bin', 'obj', '__pycache__', 'BenchmarkDotNet.Artifacts')


def run(command, directory, environment):
    print(f"Checking {directory.name}: {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=directory, env=environment, check=True)


def environment(root):
    result = os.environ.copy()
    local_sdk = root / 'work/dotnet'
    if (local_sdk / 'dotnet').is_file():
        result['PATH'] = str(local_sdk) + os.pathsep + result.get('PATH', '')
        result['DOTNET_ROOT'] = str(local_sdk)
    result.setdefault('DOTNET_CLI_TELEMETRY_OPTOUT', '1')
    result.setdefault('DOTNET_NOLOGO', '1')
    result.setdefault('DOTNET_CLI_HOME', str(root / 'work/dotnet-home'))
    result.setdefault('NUGET_PACKAGES', str(root / 'work/nuget-packages'))
    return result


def labs_from_catalog(root):
    entries = json.loads((root / 'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
    labs = []
    seen = set()
    for entry in entries:
        for lab in entry.get('labs', []):
            directory = Path(lab['directory'])
            if (directory.is_absolute() or '..' in directory.parts
                    or not directory.parts or directory.parts[0] != 'labs'):
                raise ValueError(f"{entry['id']}: lab directory must be inside labs/")
            if lab['language'] not in ('csharp', 'python', 'tsql'):
                raise ValueError(f"{entry['id']}: unsupported lab language")
            command = lab.get('check')
            if not isinstance(command, list) or not command or any(not isinstance(x, str) for x in command):
                raise ValueError(f"{entry['id']}: lab check must be a nonempty command argument list")
            if lab['directory'] in seen:
                raise ValueError(f"duplicate lab directory: {lab['directory']}")
            seen.add(lab['directory'])
            if not (root / directory).is_dir():
                raise ValueError(f"lab directory missing: {directory}")
            archive = lab.get('archive')
            if archive is not None:
                path = Path(archive)
                if (path.is_absolute() or '..' in path.parts or not path.parts
                        or path.parts[0] != 'labs' or path.suffix != '.zip'):
                    raise ValueError(f"invalid lab archive: {archive}")
            if lab['language'] == 'csharp' and not archive:
                raise ValueError(f"C# lab requires a downloadable archive: {directory}")
            labs.append(lab)
    return labs


def require_sdk(labs, env):
    if any(lab['language'] == 'csharp' for lab in labs) and not shutil.which('dotnet', path=env.get('PATH')):
        raise ValueError('C# lab checks require .NET SDK 10.0.401. Run bash scripts/setup_environment.sh, '
                         'then work/venv/bin/python scripts/check_all.py.')


def sdk_ready(env):
    executable = shutil.which('dotnet', path=env.get('PATH'))
    if not executable:
        return False
    try:
        result = subprocess.run([executable, '--list-sdks'], env=env, capture_output=True,
                                text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    return any(line.split()[0] == SDK_VERSION for line in result.stdout.splitlines() if line.strip())


def command_for_python(command):
    # Use the interpreter running this check, including its isolated dependencies.
    return [sys.executable, *command[1:]] if command[0] in ('python', 'python3') else command


def check_labs(root, site, scratch, labs, env):
    require_sdk(labs, env)
    for index, lab in enumerate(labs):
        source = root / lab['directory']
        copied = scratch / f'lab-{index}' / source.name
        shutil.copytree(source, copied, ignore=IGNORED_LAB_OUTPUTS)
        command = command_for_python(lab['check'])
        run(command, copied, env)
        if not lab.get('archive'):
            continue
        archive = site / lab['archive']
        if not archive.is_file():
            raise ValueError(f'published lab archive missing: {lab["archive"]}')
        extracted = scratch / f'archive-{index}'
        with ZipFile(archive) as zip_file:
            for member in zip_file.namelist():
                path = Path(member)
                if path.is_absolute() or '..' in path.parts:
                    raise ValueError(f'unsafe archive path: {member}')
            zip_file.extractall(extracted)
        downloaded = extracted / source.name
        if not downloaded.is_dir():
            raise ValueError(f'lab archive must contain a {source.name}/ directory')
        run(command, downloaded, env)
        # The normal lab command need not use optional projects. Build each one
        # from the actual archive so an incomplete source ZIP cannot pass CI.
        if lab['language'] == 'csharp':
            for project in sorted(downloaded.rglob('*.csproj')):
                run(['dotnet', 'build', '-c', 'Release', str(project.relative_to(downloaded))], downloaded, env)


def check_benchmarks(root, labs, env):
    require_sdk(labs, env)
    with tempfile.TemporaryDirectory(prefix='lesson-benchmarks-') as temporary:
        for index, lab in enumerate(labs):
            command = lab.get('benchmark')
            if not command:
                continue
            if not isinstance(command, list) or any(not isinstance(x, str) for x in command):
                raise ValueError('benchmark must be a command argument list')
            copied = Path(temporary) / str(index)
            shutil.copytree(root / lab['directory'], copied, ignore=IGNORED_LAB_OUTPUTS)
            run(command_for_python(command), copied, env)


def check_all(root=ROOT, benchmarks_only=False):
    root = root.resolve()
    env = environment(root)
    labs = labs_from_catalog(root)
    if benchmarks_only:
        check_benchmarks(root, labs, env)
        return
    # Fail before claiming a full validation when the supported SDK is absent.
    require_sdk(labs, env)
    commands = [
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'],
        [sys.executable, 'scripts/validate_learning.py'],
        [sys.executable, 'scripts/generate_topic_map.py', '--check'],
        [sys.executable, 'scripts/add_lesson_navigation.py', '--check'],
        [sys.executable, 'scripts/validate_docs_navigation.py'],
        [sys.executable, 'scripts/check_lesson_parity.py'],
    ]
    for command in commands:
        run(command, root, env)
    with tempfile.TemporaryDirectory(prefix='lesson-checks-') as temporary:
        scratch = Path(temporary)
        site = scratch / 'site'
        print(f'Staged {build(root, site)} public files.', flush=True)
        check_labs(root, site, scratch, labs, env)
    print('All required lesson checks passed; lab outputs stayed in temporary copies.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-bootstrap', action='store_true', help='require an already provisioned environment')
    parser.add_argument('--benchmarks-only', action='store_true', help='run optional catalog benchmark commands')
    args = parser.parse_args()
    try:
        # Fresh Codex sessions can run the same command without editing cloud configuration.
        env = environment(ROOT)
        if not args.no_bootstrap and (importlib.util.find_spec('yaml') is None
                                     or not sdk_ready(env)):
            subprocess.run(['bash', str(ROOT / 'scripts/setup_environment.sh')], cwd=ROOT, check=True)
            command = [str(ROOT / 'work/venv/bin/python'), str(Path(__file__).resolve()), '--no-bootstrap']
            if args.benchmarks_only: command.append('--benchmarks-only')
            return subprocess.run(command, cwd=ROOT, env=environment(ROOT)).returncode
        check_all(benchmarks_only=args.benchmarks_only)
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f'Check failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
