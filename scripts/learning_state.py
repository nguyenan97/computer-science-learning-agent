#!/usr/bin/env python3
"""Archived optional v3 state tools, outside the daily lesson loop. No network."""
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
TEMPLATE = ROOT / 'state/learning-state.example.json'
DEFAULT_STATE = ROOT / '.learning-private/learning-state.json'


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
        if status == 'completed' and not any(
                assessments[a]['kind'] in completion_kinds
                and assessments[a]['topic_id'] == lesson['topic_id']
                and assessments[a]['observed_on'] <= lesson['completed_on']
                for a in lesson['assessment_ids']):
            raise ValueError(f'{lesson["id"]}: completion requires an observed task attempt '
                             'for the same lesson topic before completion; low performance '
                             'is allowed. Prerequisite evidence for another topic cannot '
                             'complete this lesson; assess its objective or preserve it in_progress.')
    order = {a['id']: i for i, a in enumerate(state['assessments'])}
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
        for aid in a['resolves_assessment_ids']:
            previous = assessments.get(aid)
            if (previous is None or previous['outcome'] != 'needs_support'
                    or previous['topic_id'] != a['topic_id']
                    or (previous['observed_on'], order[aid]) >= (a['observed_on'], order[a['id']])
                    or a['outcome'] != 'independent' or a['kind'] == 'exit'):
                raise ValueError('repair requires later independent non-exit evidence for the same topic')
    used = set()
    for r in state['reviews']:
        lesson = lessons.get(r['lesson_id'])
        if lesson is None or lesson['status'] != 'completed' or r['topic_id'] != lesson['topic_id']:
            raise ValueError('review requires a completed source lesson and matching topic')
        if r['initial_due_on'] <= lesson['completed_on']:
            raise ValueError('delayed review must follow completion')
        due = r['initial_due_on']; last_key = (lesson['completed_on'], -1)
        for attempt in r['attempts']:
            a = assessments.get(attempt['assessment_id'])
            if a is None or a['kind'] not in ('retrieval','transfer') or a['topic_id'] != r['topic_id'] or a['outcome'] == 'unassessed':
                raise ValueError('review requires assessed retrieval/transfer evidence')
            key = (a['observed_on'], order[a['id']])
            if (a['id'] in used or a['observed_on'] <= lesson['completed_on']
                    or key <= last_key or attempt['scheduled_for'] != due
                    or attempt['next_due_on'] < a['observed_on']):
                raise ValueError('invalid review history or reused attempt')
            used.add(a['id']); last_key = key; due = attempt['next_due_on']
        if r['due_on'] != due:
            raise ValueError('review due date disagrees with history')
    return state


def unresolved_errors(state, topic, as_of=None):
    evidence = [a for a in state['assessments'] if a['topic_id'] == topic
                and (as_of is None or a['observed_on'] <= as_of)]
    resolved = {aid for a in evidence for aid in a['resolves_assessment_ids']}
    return [a['id'] for a in evidence if a['outcome'] == 'needs_support' and a['id'] not in resolved]


def mastery(state, topic, as_of=None):
    if unresolved_errors(state, topic, as_of): return 'needs_remediation'
    completed = [l for l in state['lessons'] if l['topic_id'] == topic and l['status'] == 'completed' and (as_of is None or l['completed_on'] <= as_of)]
    if not completed: return 'unknown'
    completed_on = min(l['completed_on'] for l in completed)
    evidence = [a for a in state['assessments'] if a['topic_id'] == topic and a['outcome'] != 'unassessed' and (as_of is None or a['observed_on'] <= as_of)]
    if not evidence: return 'unknown'
    # Append order disambiguates same-day events; date still measures delay.
    independent = []
    for kind in ('practice', 'retrieval', 'transfer'):
        observations = [a for a in evidence if a['kind'] == kind]
        if not observations:
            continue
        recent = max(enumerate(observations), key=lambda item: (item[1]['observed_on'], item[0]))[1]
        if recent['outcome'] == 'independent' and not recent['hints']:
            independent.append(recent)
    if any(a['kind'] == 'practice' for a in independent):
        delayed = {a['kind'] for a in independent if a['observed_on'] > completed_on}
        if {'retrieval','transfer'} <= delayed: return 'retained_and_transferred'
        return 'provisional'
    return 'developing'


def plan(state, today, prerequisite='unknown', source_available=True, lab_available=True, minutes=None):
    budget = minutes if minutes is not None else state['learner']['daily_minutes']
    budget_source = 'plan_override' if minutes is not None else 'learner_profile'
    if budget is None:
        budget = 420
        budget_source = 'full_day_default'
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 10:
        raise ValueError('elapsed time budget must be an integer of at least 10 minutes')
    visible = [l for l in state['lessons'] if l['created_on'] <= today]
    def status_on(l):
        for status, field in [('completed','completed_on'), ('in_progress','started_on'), ('assigned','assigned_on')]:
            if l[field] is not None and l[field] <= today: return status
        return 'generated'
    pending = [l['id'] for l in visible if status_on(l) in ('assigned','in_progress')]
    generated = [l['id'] for l in visible if status_on(l) == 'generated']
    lessons = {l['id']: l for l in visible}
    assessments = {a['id']: a for a in state['assessments']}
    review_dates = {}
    for r in state['reviews']:
        l = lessons.get(r['lesson_id'])
        if l is None or status_on(l) != 'completed': continue
        due_on = r['initial_due_on']
        for attempt in r['attempts']:
            a = assessments[attempt['assessment_id']]
            if a['observed_on'] <= today: due_on = attempt['next_due_on']
        review_dates[r['id']] = due_on
    due = [rid for rid, on in review_dates.items() if on <= today]
    observed = [a for a in state['assessments'] if a['observed_on'] <= today]
    topics = ({l['topic_id'] for l in visible}
              | {t for l in visible for t in l['prerequisites']}
              | {a['topic_id'] for a in observed})
    levels = {t: mastery(state,t,today) for t in sorted(topics)}
    if not source_available or not lab_available: action,reason = 'fallback','Use verified pinned sources or paper traces; record limitations, never claim an unobserved run.'
    elif prerequisite == 'weak': action,reason = 'prerequisite_bridge','Bridge the indicated prerequisite gap, then recheck; a caller flag alone is not observed evidence.'
    elif due: action,reason = 'review','Attempt due retrieval first; review-only if the time budget is consumed.'
    elif pending: action,reason = 'resume','Offer to resume unfinished work; a requested new objective remains available without inferred completion.'
    elif 'needs_remediation' in levels.values(): action,reason = 'remediation','Target observed errors with a new variation and feedback.'
    elif prerequisite == 'unknown' or not visible: action,reason = 'diagnostic','Include optional self-checks and prerequisite bridges in delivery; unknown knowledge does not block the next lesson.'
    elif generated: action,reason = 'deliver','Inspect existing generated work and diagnostic fit before delivery; do not create a duplicate.'
    elif 'retained_and_transferred' in levels.values(): action,reason = 'deepen','Offer a harder variation or next prerequisite-safe topic based on goals.'
    else: action,reason = 'core','Select one topic objective; check prerequisite evidence and semantic duplication.'
    knowledge = {
        'background': {'status': 'self_reported' if state['learner']['background'] else 'unknown',
                       'value': state['learner']['background']},
        'goals': {'status': 'self_reported' if state['learner']['goals'] else 'unknown',
                  'value': state['learner']['goals']},
        'prerequisite_context': {'value': prerequisite,
                                 'status': 'unknown' if prerequisite == 'unknown' else 'caller_supplied',
                                 'note': 'The planner does not verify this flag or infer topic mastery from it.'},
        'topics': {},
    }
    for topic in sorted(topics):
        evidence = [a for a in observed if a['topic_id'] == topic]
        assessed = [a for a in evidence if a['outcome'] != 'unassessed']
        knowledge['topics'][topic] = {
            'status': 'observed' if assessed else 'unknown',
            'assessment_ids': [a['id'] for a in assessed],
            'unassessed_ids': [a['id'] for a in evidence if a['outcome'] == 'unassessed'],
            'observed_misconceptions': [
                {'assessment_id': a['id'], 'misconceptions': a['misconceptions']}
                for a in assessed if a['misconceptions']],
        }
    summary = {
        'completed_core_lessons': sum(l['kind'] == 'core' and l['status'] == 'completed' and l['completed_on'] <= today for l in state['lessons']),
        'assessment_count': len(observed),
        'hints_used': sum(len(a['hints']) for a in observed),
        'overdue_days': {rid: (date.fromisoformat(today) - date.fromisoformat(on)).days for rid, on in review_dates.items() if on < today},
    }
    return {'action':action,'reason':reason,'due_reviews':due,'pending_lessons':pending,
            'generated_lessons':generated,'mastery':levels,
            'unresolved_assessments':{t: unresolved_errors(state,t,today) for t in sorted(topics) if unresolved_errors(state,t,today)},
            'minutes':budget,
            'time_budget': {'elapsed_minutes': budget, 'includes_breaks': True,
                            'source': budget_source,
                            'mode': 'full_day' if budget >= 360 else 'shortened'},
            'knowledge':knowledge,'summary':summary}


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


def check_private_path(path):
    path = path.resolve()
    if path.is_relative_to(ROOT) and not path.is_relative_to(ROOT / '.learning-private'):
        raise ValueError('real state must be in .learning-private/ or outside this repository')
    return path


def validate_private_artifacts(state, directory, state_path):
    canonical_state = state_path.resolve()
    for lesson in state['lessons']:
        artifact = (directory / lesson['artifact']).resolve()
        if (artifact == canonical_state
                or (artifact.is_file() and canonical_state.is_file()
                    and artifact.samefile(canonical_state))):
            raise ValueError('learner lesson artifact cannot be the canonical state file')
        if not artifact.is_relative_to(directory.resolve()) or not artifact.is_file():
            raise ValueError('learner lesson artifact must exist within the selected private workspace')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state',type=Path,default=DEFAULT_STATE); p.add_argument('--allow-fixture',action='store_true')
    sub=p.add_subparsers(dest='cmd',required=True); sub.add_parser('validate')
    sub.add_parser('init')
    q=sub.add_parser('profile'); q.add_argument('--timezone'); q.add_argument('--minutes',type=int); q.add_argument('--goal',action='append'); q.add_argument('--background')
    q=sub.add_parser('plan'); q.add_argument('--on'); q.add_argument('--minutes',type=int,help='One-off elapsed budget including breaks; does not change the profile'); q.add_argument('--prerequisite',choices=['unknown','weak','ready'],default='unknown'); q.add_argument('--source-unavailable',action='store_true'); q.add_argument('--lab-unavailable',action='store_true')
    q=sub.add_parser('transition'); q.add_argument('lesson_id'); q.add_argument('status',choices=['assigned','in_progress','completed']); q.add_argument('--on')
    q=sub.add_parser('add'); q.add_argument('collection',choices=['lessons','assessments','reviews']); q.add_argument('record',type=Path)
    q=sub.add_parser('review'); q.add_argument('review_id'); q.add_argument('assessment_id'); q.add_argument('--next-due',required=True); q.add_argument('--reason',required=True)
    args=p.parse_args()
    try:
        if args.allow_fixture and args.state.resolve() == DEFAULT_STATE.resolve():
            raise ValueError('fixtures require a separate explicit --state path')
        if not args.allow_fixture: args.state = check_private_path(args.state)
        if args.cmd == 'init':
            if args.state.exists(): raise ValueError('destination already exists; initialization never overwrites state')
            state = json.loads(TEMPLATE.read_text())
            validate(state,allow_fixture=args.allow_fixture)
            if not state['fixture']: args.state = check_private_path(args.state)
            args.state.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            if not state['fixture']: validate_private_artifacts(state,args.state.parent,args.state)
            atomic_save(args.state,state); print('Created private v3 state.'); return 0
        if not args.state.exists(): raise ValueError('state missing; run init once or select an existing private --state path')
        state=validate(json.loads(args.state.read_text()),allow_fixture=args.allow_fixture)
        if not state['fixture']:
            args.state = check_private_path(args.state)
            validate_private_artifacts(state,args.state.parent,args.state)
        today=getattr(args,'on',None) or datetime.now(ZoneInfo(state['learner']['timezone'])).date().isoformat(); date.fromisoformat(today)
        if args.cmd=='validate': print('Learning state valid.'); return 0
        if args.cmd=='plan':
            print(json.dumps(plan(state,today,args.prerequisite,not args.source_unavailable,not args.lab_unavailable,args.minutes),indent=2)); return 0
        if args.cmd=='transition': state=transition(state,args.lesson_id,args.status,today)
        if args.cmd=='profile':
            for field, value in [('timezone',args.timezone),('daily_minutes',args.minutes),('goals',args.goal),('background',args.background)]:
                if value is not None: state['learner'][field] = value
        if args.cmd=='add':
            record=json.loads(args.record.read_text())
            if args.collection=='lessons' and record['status']!='generated': raise ValueError('new lesson must start generated')
            state[args.collection].append(record)
            if args.collection=='assessments': next(l for l in state['lessons'] if l['id']==record['lesson_id'])['assessment_ids'].append(record['id'])
        if args.cmd=='review':
            review=next(r for r in state['reviews'] if r['id']==args.review_id)
            review['attempts'].append({'assessment_id':args.assessment_id,'scheduled_for':review['due_on'],'next_due_on':args.next_due,'reason':args.reason}); review['due_on']=args.next_due
        validate(state,allow_fixture=args.allow_fixture)
        if not state['fixture']: validate_private_artifacts(state,args.state.parent,args.state)
        atomic_save(args.state,state); print('Saved validated state.'); return 0
    except (ValueError,KeyError,StopIteration,OSError) as e:
        print(f'Invalid state/action: {e}',file=sys.stderr); return 1

if __name__=='__main__': raise SystemExit(main())
