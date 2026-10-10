"""Release and topic graph invariants that protect the reviewed workflow."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('topic_generator', ROOT / 'scripts/generate_topic_map.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class ProjectContractTests(unittest.TestCase):
    def test_deploy_requires_same_commit_validation_without_privileged_validation(self):
        pages = yaml.load((ROOT / '.github/workflows/pages.yml').read_text(), Loader=yaml.BaseLoader)
        validation = yaml.load((ROOT / '.github/workflows/validate-learning.yml').read_text(), Loader=yaml.BaseLoader)
        self.assertIn('workflow_call', validation['on'])
        self.assertEqual(pages['jobs']['validate']['uses'], './.github/workflows/validate-learning.yml')
        deploy = pages['jobs']['deploy']
        self.assertEqual(deploy['needs'], 'validate')
        self.assertEqual(deploy['if'], "github.ref == 'refs/heads/main'")
        self.assertEqual(pages['permissions'], {'contents': 'read'})
        self.assertEqual(validation['permissions'], {'contents': 'read'})
        for steps in (deploy['steps'], validation['jobs']['validate']['steps']):
            checkout = next(step for step in steps if step.get('uses', '').startswith('actions/checkout@'))
            self.assertEqual(checkout['with']['ref'], '${{ github.sha }}')

    def test_required_validation_uses_consolidated_checks_and_main_does_not_duplicate_runs(self):
        validation = yaml.load((ROOT / '.github/workflows/validate-learning.yml').read_text(), Loader=yaml.BaseLoader)
        self.assertNotIn('push', validation['on'])
        self.assertIn('pull_request', validation['on'])
        steps = validation['jobs']['validate']['steps']
        commands = [step.get('run', '') for step in steps]
        self.assertIn('python scripts/check_all.py', commands)
        self.assertFalse(any(step.get('continue-on-error') == 'true' for step in steps))
        self.assertFalse((ROOT / '.github/workflows/validate-docs-navigation.yml').exists())

    def test_browser_and_benchmark_failures_cannot_block_required_validation(self):
        validation = yaml.load((ROOT / '.github/workflows/validate-learning.yml').read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(set(validation['jobs']), {'validate'})
        workflow = yaml.load((ROOT / '.github/workflows/lesson-diagnostics.yml').read_text(), Loader=yaml.BaseLoader)
        diagnostics = workflow['jobs']['optional-diagnostics']
        self.assertEqual(diagnostics['continue-on-error'], 'true')
        self.assertNotIn('needs', diagnostics)
        self.assertEqual(workflow['on']['push']['branches'], ['main'])
        self.assertEqual(workflow['permissions'], {'contents': 'read'})
        for step in diagnostics['steps']:
            if 'run' in step:
                self.assertEqual(step['continue-on-error'], 'true')

    def test_frontend_dependencies_are_local_versioned_and_intact(self):
        html = (ROOT / 'index.html').read_text()
        references = re.findall(r'<(?:script|link)\b[^>]*(?:src|href)="([^"]+)"', html)
        self.assertEqual(set(reference for reference in references if not reference.startswith('vendor/')),
                         {'site.css', 'site.js'})
        references = [reference for reference in references if reference.startswith('vendor/')]
        self.assertEqual(len(references), 7)
        manifest = json.loads((ROOT / 'vendor/manifest.json').read_text())
        assets = {asset['path']: asset for asset in manifest['assets']}
        for reference in references:
            self.assertRegex(reference, r'^vendor/[a-z-]+-\d+\.\d+\.\d+/[^/]+$')
            self.assertIn(reference, assets)
        for asset in assets.values():
            with self.subTest(path=asset['path']):
                self.assertRegex(asset['source'], r'^https://cdn\.jsdelivr\.net/npm/[a-z-]+@\d+\.\d+\.\d+/')
                self.assertEqual(hashlib.sha256((ROOT / asset['path']).read_bytes()).hexdigest(), asset['sha256'])
        for package in manifest['packages']:
            self.assertEqual(package['license'], 'MIT')
            self.assertIn(package['license_file'], assets)
            self.assertIn('Permission is hereby granted', (ROOT / package['license_file']).read_text())
        css = (ROOT / 'vendor/docsify-4.13.1/vue.css').read_text()
        self.assertNotIn('@import', css)
        self.assertNotRegex(css, r'url\([\'"]?https?://')
        self.assertIn('noEmoji: true', html)

    def test_topic_graph_rejects_missing_duplicate_and_cyclic_dependencies(self):
        data = json.loads((ROOT / 'references/topics.json').read_text())
        generator.validate_topics(data)
        for variant in ('missing', 'duplicate', 'cycle', 'translation', 'empty-id', 'non-string-id'):
            invalid = copy.deepcopy(data)
            if variant == 'missing': invalid['topics'][0]['prerequisites'] = ['absent']
            if variant == 'duplicate': invalid['topics'].append(copy.deepcopy(invalid['topics'][0]))
            if variant == 'cycle': invalid['topics'][0]['prerequisites'] = [invalid['topics'][0]['id']]
            if variant == 'translation': del invalid['topics'][0]['objective']['vi']
            if variant == 'empty-id': invalid['topics'][0]['id'] = ''
            if variant == 'non-string-id': invalid['topics'][0]['id'] = []
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                generator.validate_topics(invalid)


if __name__ == '__main__':
    unittest.main()
