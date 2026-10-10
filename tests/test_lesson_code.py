"""Missing setup and shared EN/VI drift must fail before publishing runnable labs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from lesson_code import extract, page_files, write_files


class LessonCodeTests(unittest.TestCase):
    def test_raw_literal_content_cannot_be_discarded_as_translated_comments(self):
        from lesson_code import comparable
        original = 'var url = """{"url":"https://first.test"}"""; // comment\n'
        changed = original.replace('first.test', 'other.test')
        self.assertNotEqual(comparable('Program.cs', original), comparable('Program.cs', changed))
        self.assertEqual(comparable('Program.cs', original),
                         comparable('Program.cs', original.replace('// comment', '// chú thích')))

    def test_extract_preserves_bytes_and_ignores_illustrative_markers(self):
        text = ('```text\n<!-- lab-file: fake.cs -->\n```\n'
                '<!-- lab-file: LessonLab/Program.cs -->\n\n```csharp\n'
                'Console.WriteLine("// still a string");\n```\n')
        files = extract(text)
        self.assertEqual(files, {'LessonLab/Program.cs': 'Console.WriteLine("// still a string");\n'})
        with tempfile.TemporaryDirectory() as directory:
            write_files(files, Path(directory))
            self.assertEqual((Path(directory)/'LessonLab/Program.cs').read_text(), files['LessonLab/Program.cs'])

    def test_unsafe_duplicate_missing_and_unclosed_fences_report_file(self):
        good = '<!-- lab-file: Program.cs -->\n```csharp\nreturn 0;\n```\n'
        for text in (good+good, good.replace('Program.cs','../secret.cs'),
                     good.replace('Program.cs','/tmp/Program.cs'),
                     good.replace('Program.cs','bin/../Program.cs'),
                     good.replace('```csharp', 'not a fence'), good.rsplit('```',1)[0]):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'lesson'):
                extract(text)

    def test_same_error_in_both_languages_cannot_hide_download_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); lab = {'directory': 'labs/example/dotnet'}
            source = root/lab['directory']; source.mkdir(parents=True)
            (source/'Program.cs').write_text('return 0; // source comment\n')
            (source/'global.json').write_text('{"sdk":{"version":"10.0.401"}}\n')
            entry = {'id':'example', 'files':[f'{lab["directory"]}/Program.cs',
                                            f'{lab["directory"]}/global.json']}
            good = ('<!-- lab-file: Program.cs -->\n```csharp\nreturn 0; // translated\n```\n'
                    '<!-- lab-file: global.json -->\n```json\n{"sdk":{"version":"10.0.401"}}\n```\n')
            for lang in ('en','vi'):
                page = root/('' if lang=='en' else 'vi')/'lessons/example/lesson.md'
                page.parent.mkdir(parents=True); page.write_text(good)
                self.assertEqual(len(page_files(root, entry, lab, lang)),2)
                for broken, message in ((good.replace('return 0','return 1'), 'differs'),
                                        (good.split('<!-- lab-file: global.json')[0], 'missing'),
                                        (good.replace('10.0.401','10.0.999'), 'differs'),
                                        (good+'<!-- lab-file: Other.cs -->\n```csharp\nreturn 0;\n```\n','undeclared')):
                    page.write_text(broken)
                    with self.assertRaisesRegex(ValueError, message): page_files(root, entry, lab, lang)


if __name__ == '__main__': unittest.main()
