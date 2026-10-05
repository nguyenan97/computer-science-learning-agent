"""Optional checks; a passing suite does not certify learner mastery."""
import argparse
import importlib.util
from pathlib import Path
import unittest
MODULE=None


class Checks(unittest.TestCase):
    def test_stable_output_and_input_preservation(self):
        for values,expected in [([],[]),(['A1'],['A1']),(['B2','A1','B2','C3','A1'],['B2','A1','C3']),(['x','x','x'],['x']),(['a','A','a'],['a','A'])]:
            with self.subTest(values=values):
                before=values.copy();output,calls=MODULE.unique_hash(values)
                self.assertEqual(output,expected);self.assertEqual(calls,len(values));self.assertEqual(values,before)

    def test_duplicate_counts_and_order(self):
        for values,expected in [([],[]),(['B2','A1','B2','C3','A1'],[('B2',2),('A1',2)]),(['x','x','x'],[('x',3)]),(['x','y'],[])]:
            before=values.copy();self.assertEqual(MODULE.duplicate_summary(values),expected);self.assertEqual(values,before)

    def test_collisions_preserve_correctness(self):
        class Key:
            def __init__(self,value):self.value=value
            def __hash__(self):return 1
            def __eq__(self,other):return isinstance(other,Key) and self.value==other.value
        result,calls=MODULE.unique_hash([Key(2),Key(1),Key(2)])
        self.assertEqual([k.value for k in result],[2,1]);self.assertEqual(calls,3)

    def test_counted_model_rejects_membership_scan(self):
        class Key:
            comparisons=0
            def __init__(self,value):self.value=value
            def __hash__(self):return self.value
            def __eq__(self,other):
                type(self).comparisons+=1
                return isinstance(other,Key) and self.value==other.value
        values=[Key(i) for i in range(256)]
        output,calls=MODULE.unique_hash(values)
        self.assertEqual([k.value for k in output],list(range(256)));self.assertEqual(calls,256)
        self.assertLess(Key.comparisons,256)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--module',default='solution.py');args=p.parse_args()
    spec=importlib.util.spec_from_file_location('submission',Path(args.module).resolve())
    MODULE=importlib.util.module_from_spec(spec);spec.loader.exec_module(MODULE)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
