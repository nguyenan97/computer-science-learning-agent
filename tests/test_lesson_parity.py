"""Detect translation drift while allowing translated comments and prose output."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('parity', Path(__file__).resolve().parents[1]/'scripts/check_lesson_parity.py')
parity = importlib.util.module_from_spec(spec); spec.loader.exec_module(parity)


class LessonParityTests(unittest.TestCase):
    def test_translated_comments_preserve_markers_inside_strings(self):
        for lang, a, b in (
            ('python', 'print("# value") # note\n', 'print("# value") # ghi chu\n'),
            ('csharp', 'var url = "https://example.test"; // note\n', 'var url = "https://example.test"; // ghi chu\n'),
            ('tsql', "SELECT '-- value'; -- note\n", "SELECT '-- value'; -- ghi chu\n"),
        ):
            with self.subTest(language=lang):
                parity.compare(f'# Title\n```{lang}\n{a}```\n', f'# Tieu de\n```{lang}\n{b}```\n')
        with self.assertRaises(ValueError):
            parity.compare('```csharp\nvar url="https://one.test";\n```', '```csharp\nvar url="https://two.test";\n```')

    def test_missing_structure_and_changed_code_fail(self):
        original = '# Title\n## Part\n| a | b |\n|---|---|\n| 1 | 2 |\n```python\nreturn_value = 1\n```'
        for translated in (original.replace('## Part','### Part'), original.replace('| 1 | 2 |\n',''),
                           original.replace('return_value = 1','return_value = 2'), original.replace('python','bash')):
            with self.subTest(translated=translated), self.assertRaises(ValueError):
                parity.compare(original, translated)

    def test_prose_fence_can_translate(self):
        parity.compare('# Title\n```text\nEmpty input\n```', '# Tieu de\n```text\nInput rong\n```')


if __name__ == '__main__': unittest.main()
