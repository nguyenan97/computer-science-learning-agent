"""Protect bilingual reader navigation as catalog entries are added or reordered."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('navigation', ROOT / 'scripts/add_lesson_navigation.py')
navigation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(navigation)


def fixture(root):
    entries = []
    for number in range(1, 4):
        key = f'lesson-{number}'
        entries.append({'id':key, 'title':{'en':f'Lesson {number}', 'vi':f'Bài {number}'},
                        'files':[f'lessons/{key}/lesson.md', f'vi/lessons/{key}/lesson.md'],
                        'related':{lang:[{'title':'Topic map', 'path':('vi/' if lang=='vi' else '')+'references/topic-map.md',
                                         'description':'Choose a useful next topic.'}] for lang in ('en','vi')}})
    for entry in entries:
        for name in entry['files']:
            path=root/name; path.parent.mkdir(parents=True,exist_ok=True);path.write_text('# Lesson\n\nComplete content.\n')
    for name in ('README.md','vi/README.md','references/topic-map.md','vi/references/topic-map.md'):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('# Reading\n')
    (root/'lessons/catalog.json').write_text(json.dumps({'lessons':entries}))
    return entries


class LessonNavigationTests(unittest.TestCase):
    def test_bilingual_neighbors_boundaries_and_idempotent_updates(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);fixture(root)
            navigation.generate(root)
            navigation.generate(root,check=True)
            first=(root/'lessons/lesson-1/lesson.md').read_text()
            middle=(root/'vi/lessons/lesson-2/lesson.md').read_text()
            last=(root/'lessons/lesson-3/lesson.md').read_text()
            self.assertNotIn('Previous:',first)
            self.assertIn('[Next: Lesson 2 →](../lesson-2/lesson.md)',first)
            self.assertIn('[← Bài trước: Bài 1](../lesson-1/lesson.md)',middle)
            self.assertIn('[Bài sau: Bài 3 →](../lesson-3/lesson.md)',middle)
            self.assertIn('[Danh sách bài học](../../README.md)',middle)
            self.assertNotIn('Next:',last)
            before=(root/'vi/lessons/lesson-2/lesson.md').read_bytes()
            navigation.generate(root)
            self.assertEqual(before,(root/'vi/lessons/lesson-2/lesson.md').read_bytes())
            self.assertTrue(middle.rstrip().endswith(navigation.END))

    def test_reordering_refreshes_neighbors_without_duplicating_footer(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);entries=fixture(root);navigation.generate(root)
            entries.reverse();(root/'lessons/catalog.json').write_text(json.dumps({'lessons':entries}))
            with self.assertRaisesRegex(ValueError,'stale'):navigation.generate(root,check=True)
            navigation.generate(root)
            first=(root/'lessons/lesson-3/lesson.md').read_text()
            self.assertNotIn('Previous:',first)
            self.assertIn('Next: Lesson 2',first)
            self.assertEqual(first.count(navigation.START),1)

    def test_missing_private_or_malformed_targets_fail_before_any_writes(self):
        for variant in ('missing','private','incomplete-marker','content-after-footer'):
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);entries=fixture(root)
                first=root/entries[0]['files'][0]
                last=root/entries[-1]['files'][-1]
                if variant=='missing':entries[0]['related']['en'][0]['path']='references/missing.md'
                if variant=='private':
                    private=root/'.learning-private/notes.md';private.parent.mkdir();private.write_text('private')
                    entries[0]['related']['en'][0]['path']='.learning-private/notes.md'
                if variant=='incomplete-marker':last.write_text('# Last\n'+navigation.START)
                if variant=='content-after-footer':last.write_text('# Last\n'+navigation.START+'\n'+navigation.END+'\nExtra content')
                (root/'lessons/catalog.json').write_text(json.dumps({'lessons':entries}))
                before=first.read_bytes()
                with self.assertRaises(ValueError):navigation.generate(root)
                self.assertEqual(first.read_bytes(),before)

    def test_lesson_file_or_parent_symlink_cannot_mutate_private_or_other_pages(self):
        for alias in ('file', 'parent'):
            for check in (False, True):
                with self.subTest(alias=alias, check=check),tempfile.TemporaryDirectory() as directory:
                    root=Path(directory);entries=fixture(root)
                    last=root/entries[-1]['files'][-1]
                    private=root/'.learning-private/lesson-copy/lesson.md'
                    private.parent.mkdir(parents=True)
                    private.write_text('# Synthetic private lesson\n\nPreserve the original evidence.\n')
                    last.unlink()
                    if alias=='file':last.symlink_to(private)
                    else:
                        last.parent.rmdir()
                        last.parent.symlink_to(private.parent, target_is_directory=True)
                    pages=[root/name for entry in entries for name in entry['files']]
                    before={page:page.read_bytes() for page in pages}
                    private_before=private.read_bytes()
                    with self.assertRaisesRegex(ValueError, 'cannot use symlinks'):
                        navigation.generate(root,check=check)
                    self.assertEqual(private.read_bytes(),private_before)
                    self.assertEqual({page:page.read_bytes() for page in pages},before)


if __name__=='__main__':unittest.main()
