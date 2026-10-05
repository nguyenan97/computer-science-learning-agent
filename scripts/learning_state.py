#!/usr/bin/env python3
"""Validate, inspect and update one local canonical learning state. No network."""
from __future__ import annotations
import argparse
import copy
from datetime import date, datetime
import json
import os
from pathlib import Path
import sys
import tempfile
from zoneinfo import ZoneInfo
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'state/learning-state.schema.json').read_text())


def validate(state, *, allow_fixture=False):
    errors = list(Draft202012Validator(SCHEMA, format_checker=FormatChecker()).iter_errors(state))
    if errors:
        raise ValueError('; '.join(f'{list(e.path)}: {e.message}' for e in errors))
    if state['fixture'] and not allow_fixture:
        raise ValueError('fixture must not be used as real learning state')
    ZoneInfo(state['learner']['timezone'])
    lessons = {x['id']: x for x in state['lessons']}
    assessments = {x['id']: x for x in state['assessments']}
    for collection in ('lessons', 'assessments', 'reviews'):
        ids = [x['id'] for x in state[collection]]
        if len(ids) != len(set(ids)):
            raise ValueError(f'duplicate {collection} id')
    seen_core = set()
    for lesson in state['lessons']:
        status = lesson['status']
        dates = [lesson['created_on']]
        for field, needed in [('assigned_on', status != 'generated'), ('started_on', status in ('in_progress', 'completed')), ('completed_on', status == 'completed')]:
            if (lesson[field] is not None) != needed:
                raise ValueError(f'{lesson["id"]}: invalid lifecycle date {field}')
            if needed:
                dates.append(lesson[field])
        if dates != sorted(dates):
            raise ValueError('lifecycle dates out of order')
        if lesson['kind'] == 'core':
            if lesson['topic_id'] in seen_core:
                raise ValueError('duplicate core topic; resume or use review/remediation/deepening')
            seen_core.add(lesson['topic_id'])
        elif not lesson['related_to']:
            raise ValueError('non-core session must name related topics')
        if len(lesson['assessment_ids']) != len(set(lesson['assessment_ids'])):
            raise ValueError('duplicate assessment link')
        for aid in lesson['assessment_ids']:
            if aid not in assessments or assessments[aid]['lesson_id'] != lesson['id']:
                raise ValueError('dangling assessment link')
        completion_kinds = ('practice', 'retrieval', 'transfer', 'prerequisite')
        if status == 'completed' and not any(assessments[a]['kind'] in completion_kinds and assessments[a]['observed_on'] <= lesson['completed_on'] for a in lesson['assessment_ids']):
            raise ValueError('completion requires an observed task attempt before completion; low performance is allowed')
    for a in state['assessments']:
        lesson = lessons.get(a['lesson_id'])
        if lesson is None or a['id'] not in lesson['assessment_ids']:
            raise ValueError('assessment missing reciprocal lesson link')
        if lesson['status'] not in ('in_progress', 'completed') or a['observed_on'] < lesson['started_on']:
            raise ValueError('assessment requires a started lesson and a valid observation date')
        if a['score'] is not None and not a['score_basis']:
            raise ValueError('score requires explicit scoring basis')
        if a['outcome'] == 'unassessed' and (a['score'] is not None or a['explanation_quality'] is not None):
            raise ValueError('unassessed evidence cannot have inferred score/explanation')
        if a['outcome'] == 'independent' and a['hints']:
            raise ValueError('hinted work cannot count as independent')
    used = set()
    for r in state['reviews']:
        lesson = lessons.get(r['lesson_id'])
        if lesson is None or lesson['status'] != 'completed' or r['topic_id'] != lesson['topic_id']:
            raise ValueError('review requires a completed source lesson and matching topic')
        if r['initial_due_on'] <= lesson['completed_on']:
            raise ValueError('delayed review must follow completion')
        due = r['initial_due_on']; last_observed = lesson['completed_on']
        for attempt in r['attempts']:
            a = assessments.get(attempt['assessment_id'])
            if a is None or a['kind'] not in ('retrieval','transfer') or a['topic_id'] != r['topic_id'] or a['outcome'] == 'unassessed':
                raise ValueError('review requires assessed retrieval/transfer evidence')
            if a['id'] in used or a['observed_on'] <= last_observed or attempt['scheduled_for'] != due or attempt['next_due_on'] <= a['observed_on']:
                raise ValueError('invalid review history or reused attempt')
            used.add(a['id']); last_observed = a['observed_on']; due = attempt['next_due_on']
        if r['due_on'] != due:
            raise ValueError('review due date disagrees with history')
    return state


def mastery(state, topic, as_of=None):
    completed = [l for l in state['lessons'] if l['topic_id'] == topic and l['status'] == 'completed' and (as_of is None or l['completed_on'] <= as_of)]
    if not completed: return 'unknown'
    completed_on = min(l['completed_on'] for l in completed)
    evidence = [a for a in state['assessments'] if a['topic_id'] == topic and a['outcome'] != 'unassessed' and (as_of is None or a['observed_on'] <= as_of)]
    if not evidence: return 'unknown'
    latest = max(a['observed_on'] for a in evidence)
    if any(a['outcome'] == 'needs_support' for a in evidence if a['observed_on'] == latest): return 'needs_remediation'
    # Older success must not hide a more recent partial/hinted attempt of that kind.
    independent = []
    for kind in ('practice', 'retrieval', 'transfer'):
        observations = [a for a in evidence if a['kind'] == kind]
        if not observations:
            continue
        newest = max(a['observed_on'] for a in observations)
        recent = [a for a in observations if a['observed_on'] == newest]
        if all(a['outcome'] == 'independent' and not a['hints'] for a in recent):
            independent.extend(recent)
    if any(a['kind'] == 'practice' for a in independent):
        delayed = {a['kind'] for a in independent if a['observed_on'] > completed_on}
        if {'retrieval','transfer'} <= delayed: return 'retained_and_transferred'
        return 'provisional'
    return 'developing'


def plan(state, today, prerequisite='unknown', source_available=True, lab_available=True):
    due = [r['id'] for r in state['reviews'] if r['due_on'] <= today]
    pending = [l['id'] for l in state['lessons'] if l['status'] in ('assigned','in_progress')]
    levels = {t: mastery(state,t,today) for t in sorted({l['topic_id'] for l in state['lessons']})}
    if not source_available or not lab_available: action,reason = 'fallback','Use verified pinned sources or paper traces; record limitations, never claim an unobserved run.'
    elif prerequisite == 'weak': action,reason = 'prerequisite_bridge','Repair the observed gap, then recheck before a new core topic.'
    elif due: action,reason = 'review','Attempt due retrieval first; review-only if the time budget is consumed.'
    elif pending: action,reason = 'resume','Resume assigned/in-progress work; do not infer completion.'
    elif 'needs_remediation' in levels.values(): action,reason = 'remediation','Target observed errors with a new variation and feedback.'
    elif prerequisite == 'unknown' or not state['lessons']: action,reason = 'diagnostic','Ask goals/time/tools; collect short prerequisite evidence. Mastery is unknown.'
    elif 'retained_and_transferred' in levels.values(): action,reason = 'deepen','Offer a harder variation or next prerequisite-safe topic based on goals.'
    else: action,reason = 'core','Select one curriculum objective; check prerequisite evidence and semantic duplication.'
    observed = [a for a in state['assessments'] if a['observed_on'] <= today]
    summary = {
        'completed_core_lessons': sum(l['kind'] == 'core' and l['status'] == 'completed' and l['completed_on'] <= today for l in state['lessons']),
        'assessment_count': len(observed),
        'hints_used': sum(len(a['hints']) for a in observed),
        'overdue_days': {r['id']: (date.fromisoformat(today) - date.fromisoformat(r['due_on'])).days for r in state['reviews'] if r['due_on'] < today},
    }
    return {'action':action,'reason':reason,'due_reviews':due,'pending_lessons':pending,'mastery':levels,'minutes':state['learner']['daily_minutes'],'summary':summary}


def transition(state, lesson_id, target, on):
    new = copy.deepcopy(state)
    lesson = next((l for l in new['lessons'] if l['id'] == lesson_id),None)
    if lesson is None: raise ValueError('unknown lesson')
    if {'generated':'assigned','assigned':'in_progress','in_progress':'completed'}.get(lesson['status']) != target:
        raise ValueError('illegal lifecycle transition')
    lesson['status'] = target
    lesson[{'assigned':'assigned_on','in_progress':'started_on','completed':'completed_on'}[target]] = on
    validate(new,allow_fixture=new['fixture'])
    return new


def atomic_save(path, state):
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,delete=False) as f:
        json.dump(state,f,ensure_ascii=False,indent=2); f.write('\n'); tmp=f.name
    try: os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state',type=Path,default=ROOT/'state/learning-state.json'); p.add_argument('--allow-fixture',action='store_true')
    sub=p.add_subparsers(dest='cmd',required=True); sub.add_parser('validate')
    q=sub.add_parser('plan'); q.add_argument('--on'); q.add_argument('--prerequisite',choices=['unknown','weak','ready'],default='unknown'); q.add_argument('--source-unavailable',action='store_true'); q.add_argument('--lab-unavailable',action='store_true')
    q=sub.add_parser('transition'); q.add_argument('lesson_id'); q.add_argument('status',choices=['assigned','in_progress','completed']); q.add_argument('--on')
    q=sub.add_parser('add'); q.add_argument('collection',choices=['lessons','assessments','reviews']); q.add_argument('record',type=Path)
    q=sub.add_parser('review'); q.add_argument('review_id'); q.add_argument('assessment_id'); q.add_argument('--next-due',required=True); q.add_argument('--reason',required=True)
    args=p.parse_args()
    try:
        state=validate(json.loads(args.state.read_text()),allow_fixture=args.allow_fixture)
        today=getattr(args,'on',None) or datetime.now(ZoneInfo(state['learner']['timezone'])).date().isoformat(); date.fromisoformat(today)
        if args.cmd=='validate': print('Learning state valid.'); return 0
        if args.cmd=='plan':
            print(json.dumps(plan(state,today,args.prerequisite,not args.source_unavailable,not args.lab_unavailable),indent=2)); return 0
        if args.cmd=='transition': state=transition(state,args.lesson_id,args.status,today)
        if args.cmd=='add':
            record=json.loads(args.record.read_text())
            if args.collection=='lessons' and record['status']!='generated': raise ValueError('new lesson must start generated')
            state[args.collection].append(record)
            if args.collection=='assessments': next(l for l in state['lessons'] if l['id']==record['lesson_id'])['assessment_ids'].append(record['id'])
        if args.cmd=='review':
            review=next(r for r in state['reviews'] if r['id']==args.review_id)
            review['attempts'].append({'assessment_id':args.assessment_id,'scheduled_for':review['due_on'],'next_due_on':args.next_due,'reason':args.reason}); review['due_on']=args.next_due
        validate(state,allow_fixture=args.allow_fixture); atomic_save(args.state,state); print('Saved validated state.'); return 0
    except (ValueError,KeyError,StopIteration,OSError) as e:
        print(f'Invalid state/action: {e}',file=sys.stderr); return 1

if __name__=='__main__': raise SystemExit(main())
