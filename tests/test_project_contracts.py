"""Release and topic graph invariants that protect the reviewed workflow."""
import copy
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

    def test_all_frontend_cdn_dependencies_have_exact_versions(self):
        html = (ROOT / 'index.html').read_text()
        packages = re.findall(r'https://cdn\.jsdelivr\.net/npm/([^/]+)', html)
        self.assertGreaterEqual(len(packages), 6)
        for package in packages:
            self.assertRegex(package, r'^[a-z-]+@\d+\.\d+\.\d+$')

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
