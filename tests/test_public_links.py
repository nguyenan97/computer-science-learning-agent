"""Regression checks for catalog publication, download URLs and source archives."""
import importlib.util
import sys
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from urllib.parse import urljoin
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('site_builder', ROOT / 'scripts/build_public_site.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
spec = importlib.util.spec_from_file_location('site_navigation', ROOT / 'scripts/add_lesson_navigation.py')
navigation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(navigation)


def public_source(directory):
    source = directory / 'source'
    source.mkdir()
    for name in [*builder.PUBLIC_FILES, *(path.relative_to(ROOT) for path in builder.catalog_files(ROOT))]:
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return source


class PublishedLinksTests(unittest.TestCase):
    def test_relative_content_links_resolve_under_project_pages(self):
        page = Path('vi/lessons/example/lesson.md')
        public = {Path('lessons/example/lesson.md'), Path('labs/example/dotnet/Program.cs')}
        text = '[English](../../../lessons/example/lesson.md)\n[Code](../../../labs/example/dotnet/Program.cs)\n'
        staged = builder.site_links(text, page, public)
        self.assertIn('[English](/lessons/example/lesson)', staged)
        self.assertIn('[Code](labs/example/dotnet/Program.cs ":ignore")', staged)
        self.assertNotIn('../', staged)
        with self.assertRaises(ValueError):
            builder.site_links('[Private](../../../.learning-private/learning-state.json)', page, public)

    def test_advertised_absolute_pages_zip_must_exist_in_the_publication_plan(self):
        public = {Path('labs/example/dotnet-lab.zip')}
        for target in ('https://reader.github.io/course/labs/example/dotnet-lab.zip',
                       'https://reader.github.io/labs/example/dotnet-lab.zip'):
            text = f'[Download]({target})'
            self.assertEqual(builder.site_links(text, Path('README.md'), public), text)
        for target in ('https://reader.github.io/course/labs/missing/lab.zip', '/labs/missing.zip'):
            with self.assertRaisesRegex(ValueError, 'ZIP is not published'):
                builder.site_links(f'[Download]({target})', Path('README.md'), public)
        # Remote third-party downloads and fenced examples do not advertise local outputs.
        text = '[Source](https://example.org/download.zip)\n```md\n[Example](/labs/missing.zip)\n```\n'
        self.assertEqual(builder.site_links(text, Path('README.md'), public), text)

    def test_root_docsify_routes_resolve_only_to_published_pages(self):
        public = {Path('README.md'), Path('vi/README.md'), Path('references/topic-map.md'),
                  Path('lessons/example/lesson.md'), Path('labs/example/source.zip')}
        page = Path('lessons/example/lesson.md')
        text = ('[Home](/)\n[Vietnamese](/vi/)\n[Topic](/references/topic-map#foundations)\n'
                '[Lesson](/lessons/example/lesson.md)\n[Download](/labs/example/source.zip)\n[Here](#trace)\n')
        staged = builder.site_links(text, page, public)
        self.assertIn('[Home](/)', staged)
        self.assertIn('[Vietnamese](/vi/)', staged)
        self.assertIn('[Topic](/references/topic-map#foundations)', staged)
        self.assertIn('[Lesson](/lessons/example/lesson)', staged)
        self.assertIn('[Download](labs/example/source.zip ":ignore")', staged)
        self.assertIn('[Here](#trace)', staged)
        for target in ('/lessons/missing/lesson', '/research/internal-review', '/references/missing.md', '/missing/'):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'not published'):
                builder.site_links(f'[Broken]({target})', page, public)

    def test_local_images_are_published_and_resolve_from_the_project_site_base(self):
        public = {Path('labs/example/diagram.svg')}
        page = Path('vi/lessons/example/lesson.md')
        for target in ('../../../labs/example/diagram.svg', '/labs/example/diagram.svg'):
            staged = builder.site_links(f'![Diagram & trace]({target} "A & B")', page, public)
            self.assertEqual(staged, '<img src="labs/example/diagram.svg" alt="Diagram &amp; trace" title="A &amp; B">')
            self.assertEqual(urljoin('https://reader.github.io/course/#/vi/lessons/example/lesson',
                                     'labs/example/diagram.svg'), 'https://reader.github.io/course/labs/example/diagram.svg')
        for target in ('../../../labs/example/private.svg', '/labs/example/private.svg'):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'not published'):
                builder.site_links(f'![Unpublished]({target})', page, public)
        external = '![Remote](https://images.example.org/diagram.svg)\n![Protocol relative](//images.example.org/diagram.svg)'
        self.assertEqual(builder.site_links(external, page, public), external)

    def test_lab_zip_contains_complete_source_without_build_or_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory) / 'site'
            builder.build(ROOT, site)
            _, archives = builder.catalog_assets(ROOT)
            self.assertTrue(archives)
            for path, lab_directory, files in archives:
                with ZipFile(site / path) as archive:
                    expected = {lab_directory.name + '/' + source.relative_to(lab_directory).as_posix() for source in files}
                    self.assertEqual(set(archive.namelist()), expected)
                    self.assertFalse(any('/bin/' in n or '/obj/' in n or '.learning-private' in n for n in expected))
                    for source in files:
                        name = lab_directory.name + '/' + source.relative_to(lab_directory).as_posix()
                        self.assertEqual(archive.read(name), (ROOT / source).read_bytes())
            self.assertFalse((site / 'skills').exists())
            self.assertFalse((site / 'state').exists())
            self.assertFalse((site / 'research').exists())
            self.assertFalse((site / 'vi/research').exists())
            self.assertEqual({path.name for path in (site / 'references').iterdir()},
                             {'topic-map.md', 'topic-notes.md', 'topics.json', 'study-profile.json'})
            self.assertFalse(any(path.name.startswith('agent-') for path in site.rglob('*')))

    def test_new_lesson_requires_only_catalog_and_new_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = public_source(directory)
            catalog_path = source / 'lessons/catalog.json'
            catalog = json.loads(catalog_path.read_text())
            entry = {
                'id': 'synthetic-third', 'date': '2026-10-07',
                'topic_ids': ['algorithms.graphs'], 'day_type': 'build',
                'title': {'en': 'Lesson 03 — Synthetic source lab', 'vi': 'Bài 03 — Lab nguồn giả lập'},
                'files': ['lessons/synthetic-third/lesson.md', 'vi/lessons/synthetic-third/lesson.md',
                          'labs/synthetic-third/dotnet/README.md', 'labs/synthetic-third/dotnet/Program.cs'],
                'related': {lang: [{'title': 'Topic map', 'path': ('vi/' if lang == 'vi' else '') + 'references/topic-map.md',
                                   'description': 'Choose the next objective.'}] for lang in ('en', 'vi')},
                'labs': [{'language': 'csharp', 'directory': 'labs/synthetic-third/dotnet',
                          'archive': 'labs/synthetic-third/source.zip', 'check': ['dotnet', 'run', '--', '--check']}],
            }
            catalog['lessons'].append(entry)
            catalog_path.write_text(json.dumps(catalog))
            for name in entry['files']:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('# Synthetic source\n' if path.suffix == '.md' else '// Synthetic source\n')
            for prefix in ('', 'vi/'):
                (source / f'{prefix}lessons/synthetic-third/lesson.md').write_text(
                    '# Synthetic lesson\n\n[Download](https://reader.github.io/course/labs/synthetic-third/source.zip)\n')
            readme = source / 'labs/synthetic-third/dotnet/README.md'
            readme.write_text('# Source guide\n\n[Program](Program.cs)\n')
            for name in ('unpublished.txt', 'bin/generated.dll', 'obj/project.assets.json'):
                path = readme.parent / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('Do not publish this unallowlisted file.')
            navigation.generate(source)
            navigation.generate(source, check=True)
            self.assertIn('synthetic-third/lesson', (source / '_sidebar.md').read_text())
            self.assertIn('vi/lessons/synthetic-third/lesson', (source / 'vi/_sidebar.md').read_text())
            self.assertIn('Lesson 03', (source / 'README.md').read_text())
            self.assertIn('Bài 03', (source / 'vi/README.md').read_text())
            site = directory / 'site'
            builder.build(source, site)
            with ZipFile(site / 'labs/synthetic-third/source.zip') as zipped:
                self.assertEqual(set(zipped.namelist()), {'dotnet/README.md', 'dotnet/Program.cs'})
                self.assertIn(b'(Program.cs)', zipped.read('dotnet/README.md'))
            self.assertIn('labs/synthetic-third/dotnet/Program.cs ":ignore"',
                          (site / 'labs/synthetic-third/dotnet/README.md').read_text())
            second = directory / 'second'
            builder.build(source, second)
            self.assertEqual((site / 'labs/synthetic-third/source.zip').read_bytes(),
                             (second / 'labs/synthetic-third/source.zip').read_bytes())
            self.assertFalse((site / 'labs/synthetic-third/dotnet/unpublished.txt').exists())

    def test_catalog_cannot_publish_agent_evidence_or_build_outputs(self):
        for name in ('lessons/example/agent-checks.txt', 'lessons/example/record.json',
                     'lessons/example/sources.json', 'labs/example/bin/Debug/program.dll',
                     'labs/example/obj/project.assets.json', 'labs/example/.hidden'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                builder.safe_path(name)

    def test_broken_absolute_download_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = public_source(directory)
            (source / 'README.md').write_text('[Download](https://reader.github.io/course/labs/missing.zip)\n')
            site = directory / 'site'
            with self.assertRaisesRegex(ValueError, 'ZIP is not published'):
                builder.build(source, site)
            self.assertFalse(site.exists())

    def test_draft_entry_cannot_be_exposed_via_the_public_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory)
            source=public_source(directory)
            catalog_path=source/'lessons/catalog.json'
            catalog=json.loads(catalog_path.read_text())
            catalog['lessons'][0]['published']=False
            catalog_path.write_text(json.dumps(catalog))
            site=directory/'site'
            with self.assertRaisesRegex(ValueError,'unpublished lessons'):
                builder.build(source,site)
            self.assertFalse(site.exists())


if __name__ == '__main__':
    unittest.main()
