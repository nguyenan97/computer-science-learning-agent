import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from check_lesson_contract import check_text


class LessonContractTests(unittest.TestCase):
    def test_code_examples_are_not_mistaken_for_real_answers_or_prose(self):
        text = ('```csharp\nConsole.WriteLine("<details open>—");\n```\n'
                'Question?\n<details>\n<summary>Answer</summary>\n\nWorked example.\n</details>\n')
        self.assertEqual(check_text(text), 1)

    def test_open_malformed_or_nonrendering_answers_have_actionable_errors(self):
        for text, message in (
            ('<details open="false"><summary>Answer</summary>\n\nA</details>', 'remove the open'),
            ('<details><summary>A</summary>\nText</details>', 'blank line'),
            ('<details><summary>A</summary>\n\nText', 'unclosed'),
            ('</details>', 'no opening'),
            ('<details>\n\nText</details>', 'needs a summary'),
            ('<details><summary>Answer\n\nText</details>', 'unclosed answer summary'),
            ('<details><summary>A</summary>\n\n—\n</details>', 'plain hyphen')):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, message):
                check_text(text, 'example.md')


if __name__ == '__main__': unittest.main()
