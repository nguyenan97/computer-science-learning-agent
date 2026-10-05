"""Reference solutions / Loi giai: first occurrence order for hashable keys."""
def unique_scan(values):
    result = []
    comparisons = 0
    for value in values:
        found = False
        for previous in result:
            comparisons += 1
            if previous == value:
                found = True
                break
        if not found:
            result.append(value)
    return result, comparisons


def unique_hash(values):
    result = []
    seen = set()
    membership_calls = 0
    for value in values:
        membership_calls += 1
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result, membership_calls


def duplicate_summary(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [(value, count) for value, count in counts.items() if count > 1]
