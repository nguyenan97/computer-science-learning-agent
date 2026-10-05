"""MENTOR SOLUTION: reveal only after an attempt, explicit request, or worked review."""

def lower_bound(values, target):
    lo, hi = 0, len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def count_window(timestamps, start, end):
    if end < start:
        raise ValueError('end precedes start')
    return lower_bound(timestamps, end) - lower_bound(timestamps, start)
