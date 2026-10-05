#!/usr/bin/env python3
"""Checkpoint/transfer checks; no learner score is inferred from this run."""
import argparse
import bisect
import importlib.util
import itertools
from pathlib import Path
import unittest

MODULE = None

class PartitionChecks(unittest.TestCase):
    def test_partition_and_edges(self):
        for n in range(7):
            for data in itertools.combinations_with_replacement(range(4), n):
                for x in range(-1,5):
                    with self.subTest(data=data,x=x):
                        values=list(data); before=values.copy()
                        i=MODULE.lower_bound(values,x)
                        self.assertEqual(i,bisect.bisect_left(values,x))
                        self.assertTrue(all(v<x for v in values[:i]))
                        self.assertTrue(all(v>=x for v in values[i:]))
                        self.assertEqual(values,before)

    def test_logarithmic_access_budget(self):
        class Counted:
            def __init__(self,n): self.n=n; self.reads=0
            def __len__(self): return self.n
            def __getitem__(self,i):
                if isinstance(i,slice): raise AssertionError('No slicing/copying in search')
                if not 0<=i<self.n: raise IndexError(i)
                self.reads+=1; return i*2
        for n in (0,1,2,31,1024,65536):
            for x in (-1,n,n*2):
                a=Counted(n); i=MODULE.lower_bound(a,x)
                self.assertEqual(i,bisect.bisect_left(range(0,n*2,2),x))
                self.assertLessEqual(a.reads,n.bit_length())

class TransferChecks(unittest.TestCase):
    def test_half_open_time_window(self):
        data=[10,10,20,30,30,40]
        for start,end in [(0,50),(10,30),(30,30),(11,39),(41,50),(10,10)]:
            with self.subTest(start=start,end=end):
                self.assertEqual(MODULE.count_window(data,start,end),sum(start<=t<end for t in data))
        self.assertEqual(MODULE.count_window([],0,1),0)
        with self.assertRaises(ValueError): MODULE.count_window(data,30,10)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--module',default='starter.py'); p.add_argument('--stage',choices=['guided','all'],default='guided'); args=p.parse_args()
    path=Path(args.module).resolve(); spec=importlib.util.spec_from_file_location('submission',path)
    MODULE=importlib.util.module_from_spec(spec); spec.loader.exec_module(MODULE)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(PartitionChecks)
    if args.stage=='all': suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TransferChecks))
    raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
