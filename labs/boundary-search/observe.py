#!/usr/bin/env python3
"""Deterministic baseline observations; counts are not wall-clock benchmarks."""
from bisect import bisect_left

class Counted:
    def __init__(self,n): self.n=n; self.reads=0
    def __len__(self): return self.n
    def __getitem__(self,i):
        if not 0<=i<self.n: raise IndexError(i)
        self.reads+=1; return i*2

for n in (8,1024,65536):
    a=Counted(n)
    result=bisect_left(a,n)
    print(f'n={n} target={n} index={result} element_reads={a.reads}')
print('duplicates:',bisect_left([2,4,4,9],4))
print('missing:',bisect_left([2,4,4,9],5))
