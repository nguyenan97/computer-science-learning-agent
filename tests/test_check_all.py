"""Check the published archive independently of the working-tree lab."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('check_all', ROOT / 'scripts/check_all.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CatalogLabChecks(unittest.TestCase):
    def test_bootstrap_checks_pinned_sdk_even_when_dotnet_exists(self):
        with patch.object(checker.shutil, 'which', return_value='/usr/bin/dotnet'), \
                patch.object(checker.subprocess, 'run') as run:
            run.return_value.stdout = '8.0.400 [/usr/share/dotnet/sdk]\n'
            self.assertFalse(checker.sdk_ready({}))
            run.return_value.stdout += '10.0.401 [/usr/share/dotnet/sdk]\n'
            self.assertTrue(checker.sdk_ready({}))

    def test_csharp_archive_runs_same_check_and_builds_optional_projects(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'labs/example/dotnet'
            source.mkdir(parents=True)
            (source / 'Core.csproj').write_text('<Project />')
            site = root / 'site'
            archive = site / 'labs/example/lab.zip'
            archive.parent.mkdir(parents=True)
            with ZipFile(archive, 'w') as packed:
                packed.writestr('dotnet/Core.csproj', '<Project />')
                packed.writestr('dotnet/Benchmarks/Benchmarks.csproj', '<Project />')
            command = ['dotnet', 'run', '--project', 'Core', '--', '--check']
            labs = [{'directory': 'labs/example/dotnet', 'language': 'csharp',
                     'check': command, 'archive': 'labs/example/lab.zip'}]
            with patch.object(checker, 'require_sdk'), patch.object(checker, 'run') as run:
                checker.check_labs(root, site, root / 'scratch', labs, {})
            calls = run.call_args_list
            self.assertEqual(calls[0].args[0], command)
            self.assertEqual(calls[1].args[0], command)
            self.assertNotEqual(calls[0].args[1], calls[1].args[1])
            self.assertEqual({call.args[0][-1] for call in calls[2:]},
                             {'Core.csproj', 'Benchmarks/Benchmarks.csproj'})
            self.assertFalse((source / 'bin').exists())

    def test_missing_dotnet_is_a_failure_with_setup_command(self):
        with patch.object(checker.shutil, 'which', return_value=None):
            with self.assertRaisesRegex(ValueError, 'bash scripts/setup_environment.sh'):
                checker.require_sdk([{'language': 'csharp'}], {})

    def test_csharp_metadata_requires_archive_and_inside_lab_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'lessons').mkdir()
            (root / 'labs/example').mkdir(parents=True)
            catalog = root / 'lessons/catalog.json'
            entry = {'id': 'example', 'labs': [{'language': 'csharp', 'directory': 'labs/example',
                                              'check': ['dotnet', 'run']}]}
            catalog.write_text(json.dumps({'lessons': [entry]}))
            with self.assertRaisesRegex(ValueError, 'downloadable archive'):
                checker.labs_from_catalog(root)
            entry['labs'][0].update(directory='labs/../private', archive='labs/example/lab.zip')
            catalog.write_text(json.dumps({'lessons': [entry]}))
            with self.assertRaisesRegex(ValueError, 'inside labs/'):
                checker.labs_from_catalog(root)


if __name__ == '__main__':
    unittest.main()
