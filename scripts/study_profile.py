#!/usr/bin/env python3
"""One study budget and Vietnamese calendar shared by planning and recall."""
from datetime import datetime, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / 'references/study-profile.json'


def load_profile(path=PROFILE_PATH):
    profile = json.loads(Path(path).read_text(encoding='utf-8'))
    ZoneInfo(profile['timezone'])
    budget = profile['daily_minutes']
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 10:
        raise ValueError('daily_minutes must be an integer of at least 10')
    if set(profile['day_types']) != {'build', 'paper'}:
        raise ValueError('study profile requires build and paper days')
    for kind, day in profile['day_types'].items():
        blocks = day['blocks']
        if not blocks or any(not isinstance(b['minutes'], int) or isinstance(b['minutes'], bool)
                             or b['minutes'] <= 0 for b in blocks):
            raise ValueError(f'{kind}: blocks require positive integer minutes')
        if sum(b['minutes'] for b in blocks) != budget:
            raise ValueError(f'{kind}: block minutes must sum to the daily budget')
        for block in blocks:
            if any(not isinstance(block['output'].get(lang), str) or not block['output'][lang].strip()
                   for lang in ('en', 'vi')):
                raise ValueError('each block needs a bilingual output or rest instruction')
    return profile


def study_date(moment=None, profile=None):
    profile = profile or load_profile()
    moment = moment or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        raise ValueError('study_date requires a timezone-aware datetime')
    return moment.astimezone(ZoneInfo(profile['timezone'])).date()
