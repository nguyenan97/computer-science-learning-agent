"""Regression checks for the published lesson's routes and downloadable lab."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('site_builder',ROOT/'scripts/build_public_site.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


class PublishedLinksTests(unittest.TestCase):
    def test_relative_content_links_resolve_under_project_pages(self):
        page=Path('vi/lessons/2026-10-05-cost-model/lesson.md')
        public={Path('lessons/2026-10-05-cost-model/lesson.md'),Path('labs/cost-model/dotnet/Core/Deduplication.cs')}
        text='[English](../../../lessons/2026-10-05-cost-model/lesson.md)\n[Code](../../../labs/cost-model/dotnet/Core/Deduplication.cs)\n'
        staged=builder.site_links(text,page,public)
        self.assertIn('[English](/lessons/2026-10-05-cost-model/lesson)',staged)
        self.assertIn('[Code](labs/cost-model/dotnet/Core/Deduplication.cs ":ignore")',staged)
        self.assertNotIn('../',staged)
        with self.assertRaises(ValueError): builder.site_links('[Private](../../../.learning-private/learning-state.json)',page,public)

    def test_lab_zip_contains_complete_source_without_build_or_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            site=Path(directory)/'site';builder.build(ROOT,site)
            with ZipFile(site/'labs/cost-model/dotnet-lab.zip') as archive:
                names=set(archive.namelist())
                for name in ('global.json','README.md','README.vi.md','Core/Core.csproj','Core/Deduplication.cs','LessonLab/LessonLab.csproj','LessonLab/Program.cs','LessonLab/Checks.cs','Benchmarks/Benchmarks.csproj','Benchmarks/Program.cs'):
                    self.assertIn('dotnet/'+name,names)
                self.assertFalse(any('/bin/' in n or '/obj/' in n or '.learning-private' in n for n in names))
                self.assertIn(b'(Core/Deduplication.cs)',archive.read('dotnet/README.md'))
            # Assets bypass Docsify's Markdown routing; translated documents retain routes.
            lesson=(site/'vi/lessons/2026-10-05-cost-model/lesson.md').read_text()
            self.assertIn('labs/cost-model/dotnet/Core/Deduplication.cs ":ignore"',lesson)
            self.assertIn('/lessons/2026-10-05-cost-model/lesson)',lesson)


if __name__=='__main__':unittest.main()
