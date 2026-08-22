from __future__ import annotations
from collections import Counter

COUNTERS = Counter()

def inc(name: str, value: int = 1):
    COUNTERS[name] += value

def snapshot():
    return dict(COUNTERS)
