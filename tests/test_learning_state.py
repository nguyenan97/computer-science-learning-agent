"""Behavioral checks for learner safety: synthetic records never enter real state."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('learning_state',ROOT/'scripts/learning_state.py')
engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)


def empty():
    s=json.loads((ROOT/'state/learning-state.json').read_text()); s['fixture']=True
    return s


def lesson(status='generated'):
    l=json.loads((ROOT/'lessons/boundary-search/record.json').read_text())
    l.update(id='fixture-session',status=status)
    if status!='generated': l['assigned_on']='2026-10-05'
    if status in ('in_progress','completed'): l['started_on']='2026-10-05'
    if status=='completed': l['completed_on']='2026-10-05'
    return l


def assessment(l, aid='practice',kind='practice',on='2026-10-05',outcome='independent'):
    return {'id':aid,'lesson_id':l['id'],'topic_id':l['topic_id'],'kind':kind,'observed_on':on,'task':'Fixture task, not learner work','evidence':['FIXTURE: synthetic trace and test output'],'assessed_by':'fixture-test','outcome':outcome,'score':None,'score_basis':None,'hints':[],'misconceptions':[],'explanation_quality':None,'feedback':'Fixture feedback','next_action':'Fixture recheck'}


def completed(outcome='independent'):
    s=empty(); l=lesson('completed'); a=assessment(l,outcome=outcome); l['assessment_ids']=[a['id']]; s['lessons']=[l]; s['assessments']=[a]; return s


def add(s,a):
    s['assessments'].append(a); s['lessons'][0]['assessment_ids'].append(a['id'])

class ScenarioTests(unittest.TestCase):
    def check(self,s): return engine.validate(s,allow_fixture=True)

    def test_new_learner_unknown_not_expert(self):
        s=self.check(empty()); self.assertEqual(engine.plan(s,'2026-10-05')['action'],'diagnostic')
        self.assertEqual(engine.mastery(s,'new-topic'),'unknown')

    def test_assigned_unattempted_resume_no_mastery(self):
        s=empty(); s['lessons']=[lesson('assigned')]; self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-05')['action'],'resume')
        self.assertEqual(engine.mastery(s,s['lessons'][0]['topic_id']),'unknown')
        with self.assertRaises(ValueError): engine.transition(s,'fixture-session','completed','2026-10-05')

    def test_weak_prerequisite_bridge(self):
        self.assertEqual(engine.plan(self.check(empty()),'2026-10-05','weak')['action'],'prerequisite_bridge')

    def test_review_only_and_diagnostic_sessions_can_complete(self):
        for kind, assessment_kind in [('review','retrieval'),('remediation','prerequisite')]:
            s=completed('developing'); l=s['lessons'][0]
            l['kind']=kind; l['related_to']=[l['topic_id']]
            s['assessments'][0]['kind']=assessment_kind
            self.check(s)
            self.assertNotEqual(engine.mastery(s,l['topic_id']),'retained_and_transferred')

    def test_overdue_stays_due_and_history_is_validated(self):
        s=completed(); l=s['lessons'][0]
        r={'id':'review-1','lesson_id':l['id'],'topic_id':l['topic_id'],'prompt':'Fixture recall','initial_due_on':'2026-10-06','due_on':'2026-10-06','attempts':[]}; s['reviews']=[r]; self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-10')['due_reviews'],['review-1'])
        self.assertEqual(engine.plan(s,'2026-10-10')['summary']['overdue_days'],{'review-1':4})
        a=assessment(l,'recall','retrieval','2026-10-10','needs_support'); add(s,a)
        r['attempts']=[{'assessment_id':a['id'],'scheduled_for':'2026-10-06','next_due_on':'2026-10-11','reason':'Fixture failed recall: earlier retry'}]; r['due_on']='2026-10-11'; self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-10')['due_reviews'],[])
        self.assertEqual(engine.mastery(s,l['topic_id']),'needs_remediation')
        bad=copy.deepcopy(s); bad['reviews'][0]['due_on']='2026-10-20'
        with self.assertRaises(ValueError): self.check(bad)

    def test_low_result_remediation_completion_not_mastery(self):
        s=self.check(completed('needs_support'))
        self.assertEqual(engine.plan(s,'2026-10-05','ready')['action'],'remediation')
        self.assertEqual(engine.plan(s,'2026-10-05','ready')['summary']['completed_core_lessons'],1)

    def test_mastery_requires_delayed_recall_and_transfer(self):
        s=completed(); l=s['lessons'][0]; self.check(s)
        self.assertEqual(engine.mastery(s,l['topic_id']),'provisional')
        add(s,assessment(l,'same-day','transfer')); self.check(s)
        self.assertEqual(engine.mastery(s,l['topic_id']),'provisional')
        add(s,assessment(l,'later-recall','retrieval','2026-10-12')); add(s,assessment(l,'later-transfer','transfer','2026-10-12')); self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-12','ready')['action'],'deepen')
        self.assertEqual(engine.plan(s,'2026-10-05','ready')['mastery'][l['topic_id']],'provisional')
        partial=copy.deepcopy(s)
        add(partial,assessment(l,'partial-recall','retrieval','2026-10-15','developing'))
        self.check(partial)
        self.assertEqual(engine.mastery(partial,l['topic_id']),'provisional')
        add(s,assessment(l,'relapse','retrieval','2026-10-20','needs_support')); self.check(s)
        self.assertEqual(engine.mastery(s,l['topic_id']),'needs_remediation')

    def test_source_or_lab_unavailable_fallback(self):
        s=self.check(empty())
        self.assertEqual(engine.plan(s,'2026-10-05',source_available=False)['action'],'fallback')
        self.assertEqual(engine.plan(s,'2026-10-05',lab_available=False)['action'],'fallback')

    def test_fixture_rejected_for_real_state(self):
        with self.assertRaises(ValueError): engine.validate(empty())

    def test_no_assessment_for_generated_or_unobserved_completion(self):
        s=empty(); l=lesson(); s['lessons']=[l]; a=assessment(l); add(s,a)
        with self.assertRaises(ValueError): self.check(s)
        s=empty(); s['lessons']=[lesson('completed')]
        with self.assertRaises(ValueError): self.check(s)

    def test_no_duplicate_core_but_intentional_remediation_allowed(self):
        s=completed(); other=lesson(); other['id']='second'; s['lessons'].append(other)
        with self.assertRaises(ValueError): self.check(s)
        other['kind']='remediation'; other['related_to']=[other['topic_id']]; self.check(s)

    def test_unknown_results_and_hints_cannot_become_scores_or_independent(self):
        s=completed(); a=s['assessments'][0]; a['score']=99
        with self.assertRaises(ValueError): self.check(s)
        a['score']=None; a['hints']=['Fixture hint']
        with self.assertRaises(ValueError): self.check(s)
        a['outcome']='developing'; self.check(s)

    def test_atomic_round_trip(self):
        s=empty()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.json'; engine.atomic_save(p,s); self.assertEqual(self.check(json.loads(p.read_text())),s)

    def test_cli_lifecycle_review_and_invalid_update_preserves_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory); path=directory/'state.json'
            engine.atomic_save(path,empty())
            def run(*args, success=True):
                result=subprocess.run([sys.executable,str(ROOT/'scripts/learning_state.py'),'--state',str(path),'--allow-fixture',*args],capture_output=True,text=True)
                self.assertEqual(result.returncode,0 if success else 1,result.stderr)
            def record(name,value):
                p=directory/name; p.write_text(json.dumps(value)); return str(p)
            l=lesson(); run('add','lessons',record('lesson.json',l))
            run('transition',l['id'],'assigned','--on','2026-10-05')
            before=path.read_bytes()
            run('transition',l['id'],'completed','--on','2026-10-05',success=False)
            self.assertEqual(path.read_bytes(),before)
            run('transition',l['id'],'in_progress','--on','2026-10-05')
            run('add','assessments',record('practice.json',assessment(l)))
            run('transition',l['id'],'completed','--on','2026-10-05')
            r={'id':'review-1','lesson_id':l['id'],'topic_id':l['topic_id'],'prompt':'Fixture review','initial_due_on':'2026-10-06','due_on':'2026-10-06','attempts':[]}
            run('add','reviews',record('review.json',r))
            run('add','assessments',record('retrieval.json',assessment(l,'recall','retrieval','2026-10-08')))
            run('review','review-1','recall','--next-due','2026-10-15','--reason','Fixture independent recall')
            state=self.check(json.loads(path.read_text()))
            self.assertEqual(state['reviews'][0]['attempts'][0]['scheduled_for'],'2026-10-06')
            self.assertEqual(state['reviews'][0]['due_on'],'2026-10-15')

if __name__=='__main__': unittest.main()
