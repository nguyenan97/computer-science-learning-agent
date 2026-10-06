#!/usr/bin/env python3
"""Choose a repeatable IUH self-study objective and recall from public artifacts."""
import argparse
import json
from pathlib import Path

from generate_topic_map import LEVELS, coverage, covered_topics, validate_topics
from review_queue import load_catalog, parse_date, select_reviews
from study_profile import ROOT, load_profile, study_date


def plan(data, entries, on, profile=None, day_type=None):
    parse_date(on)
    topics = validate_topics(data)
    profile = profile or load_profile()
    if day_type is not None and day_type not in profile['day_types']:
        raise ValueError('day_type must be build or paper')
    covered = covered_topics(data, entries, on)
    same_day = [e for e in entries if e['date'] == on]
    result = {'on': on, 'timezone': profile['timezone'], 'daily_minutes': profile['daily_minutes'],
              'coverage': coverage(data, entries, on), 'recall': select_reviews(entries, on)}
    if same_day:
        lesson = same_day[-1]
        kind = day_type or lesson['day_type']
        result.update(action='existing-lesson', lesson_id=lesson['id'], topic_ids=lesson['topic_ids'],
                      day_type=kind, blocks=profile['day_types'][kind]['blocks'])
        return result
    # All planned master's units precede doctoral units; inventory order breaks ties.
    for level in LEVELS:
        remaining = [t for t in topics if t['level'] == level and t['id'] not in covered]
        if not remaining: continue
        eligible = [t for t in remaining if set(t['prerequisites']) <= covered]
        if not eligible:
            result.update(action='blocked', level=level,
                          missing_prerequisites={t['id']: sorted(set(t['prerequisites'])-covered) for t in remaining})
            return result
        topic = eligible[0]
        kind = day_type or topic['day_type']
        result.update(action='new-lesson', topic=topic, day_type=kind,
                      blocks=profile['day_types'][kind]['blocks'])
        return result
    result.update(action='research-extension', topic=None,
                  reason='All currently planned units have published artifacts. Propose a new research question; no degree or proficiency is inferred.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--on', default=study_date().isoformat())
    parser.add_argument('--topics', type=Path, default=ROOT/'references/topics.json')
    parser.add_argument('--catalog', type=Path, default=ROOT/'lessons/catalog.json')
    parser.add_argument('--day-type', choices=('build', 'paper'))
    args = parser.parse_args()
    try:
        data = json.loads(args.topics.read_text(encoding='utf-8'))
        result = plan(data, load_catalog(args.catalog), args.on, day_type=args.day_type)
    except (ValueError, KeyError, OSError) as error: parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
