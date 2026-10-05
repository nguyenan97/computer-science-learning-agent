"""Deterministic observations / Quan sat tai lap. Standard library only."""
import argparse
import sqlite3
import timeit
from solution import unique_scan, unique_hash, duplicate_summary


def observe():
    orders = ['B2', 'A1', 'B2', 'C3', 'A1']
    scan, comparisons = unique_scan(orders)
    hashed, calls = unique_hash(orders)
    assert scan == hashed == ['B2', 'A1', 'C3']
    print('orders:', orders)
    print('scan:', scan, 'equality_checks:', comparisons)
    print('hash:', hashed, 'membership_calls:', calls)
    print('duplicates:', duplicate_summary(orders))
    for n in (128, 256, 512):
        values = list(range(n))
        scan, comparisons = unique_scan(values)
        hashed, calls = unique_hash(values)
        assert scan == hashed == values
        print(f'n={n} scan_equality_checks={comparisons} hash_membership_calls={calls}')
    print('all_equal_n=128 scan_equality_checks=',unique_scan(['A1']*128)[1],sep='')


def sql_example():
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE events (pos INTEGER PRIMARY KEY, order_id TEXT NOT NULL)')
        db.executemany('INSERT INTO events VALUES (?,?)',enumerate(['B2','A1','B2','C3','A1']))
        rows=db.execute('SELECT order_id, COUNT(*) FROM events GROUP BY order_id ORDER BY MIN(pos)').fetchall()
        print('SQLite:',sqlite3.sqlite_version,'counts_in_first_occurrence_order:',rows)


def collision_example():
    class Key:
        equality_checks = 0
        def __init__(self,value): self.value=value
        def __hash__(self): return 1  # intentionally bad / co tinh collision
        def __eq__(self,other):
            type(self).equality_checks += 1
            return isinstance(other,Key) and self.value==other.value
    result,calls=unique_hash([Key(i) for i in range(100)])
    assert [k.value for k in result]==list(range(100))
    print('collision_n=100 membership_calls=',calls,' actual_equality_checks=',Key.equality_checks,sep='')


def timings():
    for n in (512,1024):
        values=list(range(n))
        # Includes counters; same data/interpreter, not production benchmarking.
        scan=min(timeit.repeat(lambda:unique_scan(values),repeat=5,number=1))
        hashed=min(timeit.repeat(lambda:unique_hash(values),repeat=5,number=1))
        print(f'timing_n={n} scan_seconds={scan:.6f} hash_seconds={hashed:.6f}')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--sql',action='store_true');p.add_argument('--collisions',action='store_true');p.add_argument('--timing',action='store_true');args=p.parse_args()
    observe()
    if args.sql:sql_example()
    if args.collisions:collision_example()
    if args.timing:timings()
