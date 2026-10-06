"""Publication isolation and lab correctness regressions."""
import importlib.util
import json
import shutil
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class PublicSiteTests(unittest.TestCase):
    def test_only_public_content_is_staged(self):
        spec=importlib.util.spec_from_file_location('build',ROOT/'scripts/build_public_site.py')
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'source';source.mkdir()
            for name in builder.PUBLIC_FILES:
                target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
            for path in builder.catalog_files(ROOT):
                target=source/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
            hidden=('.learning-private/learning-state.json','state/learning-state.json','lessons/private/lesson.md',
                    'research/internal-review.md','vi/research/internal-review.md','skills/example/SKILL.md',
                    'references/internal-agent-spec.md','vi/references/internal-agent-spec.md')
            for name in hidden:
                p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('SYNTHETIC_PRIVATE_MARKER')
            out=Path(directory)/'site';builder.build(source,out)
            self.assertTrue((out/'index.html').is_file())
            self.assertTrue((out/'lessons/boundary-search/lesson.md').is_file())
            self.assertTrue((out/'lessons/2026-10-05-cost-model/lesson.md').is_file())
            self.assertTrue((out/'vi/lessons/2026-10-05-cost-model/lesson.md').is_file())
            self.assertFalse((out/'state').exists())
            self.assertFalse((out/'state/learning-state.json').exists())
            for name in ('.learning-private','.git','tests','scripts','.github','skills','research','vi/research'):
                self.assertFalse((out/name).exists())
            self.assertFalse((out/'lessons/private/lesson.md').exists())
            for name in hidden:self.assertFalse((out/name).exists())
            self.assertFalse(any(b'SYNTHETIC_PRIVATE_MARKER' in p.read_bytes() for p in out.rglob('*') if p.is_file()))
            with self.assertRaises(ValueError):builder.build(source,out)
            (source/'index.html').unlink();(source/'index.html').symlink_to(source/'.learning-private/learning-state.json')
            with self.assertRaises(ValueError):builder.build(source,Path(directory)/'symlink-site')
            catalog={'lessons':[{'id':'invalid','files':['.learning-private/learning-state.json']}]}
            (source/'lessons/catalog.json').write_text(json.dumps(catalog))
            with self.assertRaises(ValueError):builder.catalog_files(source)

if __name__=='__main__':unittest.main()
