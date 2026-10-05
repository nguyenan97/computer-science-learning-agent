"""Regression cases from the repository review; all records are synthetic."""
import copy
import importlib.util
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_learning_state import ROOT, engine, empty, lesson, assessment, completed, add


class EvidenceRegressionTests(unittest.TestCase):
    def check(self,s): return engine.validate(s,allow_fixture=True)

    def test_exit_cannot_hide_error_and_only_explicit_reassessment_repairs(self):
        s=completed(); l=s['lessons'][0]
        add(s,assessment(l,'recall','retrieval','2026-10-06'))
        add(s,assessment(l,'transfer','transfer','2026-10-06'))
        add(s,assessment(l,'failed','prerequisite','2026-10-07','needs_support'))
        add(s,assessment(l,'exit','exit','2026-10-08','developing'))
        self.check(s)
        self.assertEqual(engine.mastery(s,l['topic_id']),'needs_remediation')
        self.assertEqual(engine.plan(s,'2026-10-08','ready')['unresolved_assessments'],{l['topic_id']:['failed']})
        repair=assessment(l,'repair','prerequisite','2026-10-08'); add(s,repair)
        self.check(s)
        self.assertEqual(engine.mastery(s,l['topic_id']),'needs_remediation')
        repair['resolves_assessment_ids']=['failed']; self.check(s)
        self.assertEqual(engine.mastery(s,l['topic_id']),'retained_and_transferred')
        self.assertEqual(engine.mastery(s,l['topic_id'],'2026-10-07'),'needs_remediation')

    def test_invalid_repair_links_rejected(self):
        for variant in ('exit','hinted','partial','other-topic','earlier','missing','not-error'):
            with self.subTest(variant=variant):
                s=completed('needs_support'); l=s['lessons'][0]
                a=assessment(l,'repair','practice','2026-10-06'); a['resolves_assessment_ids']=['practice']; add(s,a)
                if variant=='exit': a['kind']='exit'
                if variant=='hinted': a['hints']=['Fixture hint']
                if variant=='partial': a['outcome']='developing'
                if variant=='other-topic': a['topic_id']='another-topic'
                if variant=='earlier': a['observed_on']='2026-10-04'
                if variant=='missing': a['resolves_assessment_ids']=['absent']
                if variant=='not-error': s['assessments'][0]['outcome']='independent'
                with self.assertRaises(ValueError): self.check(s)

    def test_diagnostic_error_without_completion_is_visible(self):
        s=empty(); l=lesson('in_progress'); s['lessons']=[l]
        a=assessment(l,kind='prerequisite',outcome='needs_support'); a['topic_id']='array-indexing'; add(s,a)
        self.check(s)
        p=engine.plan(s,'2026-10-05','ready')
        self.assertEqual(p['mastery']['array-indexing'],'needs_remediation')
        self.assertEqual(p['unresolved_assessments']['array-indexing'],['practice'])

    def test_same_day_retry_preserves_due_and_order(self):
        s=completed(); l=s['lessons'][0]
        fail=assessment(l,'fail','retrieval','2026-10-06','needs_support'); add(s,fail)
        r={'id':'r','lesson_id':l['id'],'topic_id':l['topic_id'],'prompt':'Fixture recall','initial_due_on':'2026-10-06','due_on':'2026-10-06','attempts':[{'assessment_id':'fail','scheduled_for':'2026-10-06','next_due_on':'2026-10-06','reason':'Fixture correction and retry today'}]}
        s['reviews']=[r];self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-06')['due_reviews'],['r'])
        retry=assessment(l,'retry','retrieval','2026-10-06');retry['resolves_assessment_ids']=['fail'];add(s,retry)
        r['attempts'].append({'assessment_id':'retry','scheduled_for':'2026-10-06','next_due_on':'2026-10-10','reason':'Fixture corrected response'});r['due_on']='2026-10-10';self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-06')['due_reviews'],[])
        bad=copy.deepcopy(s);bad['reviews'][0]['attempts'].reverse()
        with self.assertRaises(ValueError):self.check(bad)

    def test_generated_draft_reused_and_historical_lifecycle_projected(self):
        s=empty();s['lessons']=[lesson()];self.check(s)
        p=engine.plan(s,'2026-10-05','ready')
        self.assertEqual(p['action'],'deliver');self.assertEqual(p['generated_lessons'],['fixture-session'])
        s['lessons'][0]['created_on']='2026-10-10';self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-05','ready')['action'],'diagnostic')
        s=completed();self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-04','ready')['pending_lessons'],[])
        l=s['lessons'][0];l['completed_on']='2026-10-07';self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-06','ready')['pending_lessons'],[l['id']])

    def test_past_plan_uses_review_due_before_future_reschedule(self):
        s=completed();l=s['lessons'][0];add(s,assessment(l,'recall','retrieval','2026-10-10'))
        s['reviews']=[{'id':'r','lesson_id':l['id'],'topic_id':l['topic_id'],'prompt':'Fixture recall','initial_due_on':'2026-10-06','due_on':'2026-10-15','attempts':[{'assessment_id':'recall','scheduled_for':'2026-10-06','next_due_on':'2026-10-15','reason':'Fixture recall'}]}];self.check(s)
        self.assertEqual(engine.plan(s,'2026-10-08')['summary']['overdue_days'],{'r':2})
        self.assertEqual(engine.plan(s,'2026-10-10')['due_reviews'],[])


class PrivateWorkspaceTests(unittest.TestCase):
    def run_cli(self,path,*args):
        return subprocess.run([sys.executable,str(ROOT/'scripts/learning_state.py'),'--state',str(path),*args],capture_output=True,text=True)

    def test_init_profile_and_no_overwrite_or_public_state_write(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'private/state.json'
            self.assertEqual(self.run_cli(path,'init').returncode,0)
            before=path.read_bytes()
            self.assertEqual(self.run_cli(path,'init').returncode,1);self.assertEqual(path.read_bytes(),before)
            self.assertEqual(self.run_cli(path,'profile','--minutes','25','--goal','Fixture goal','--timezone','Asia/Bangkok').returncode,0)
            self.assertEqual(json.loads(path.read_text())['learner']['goals'],['Fixture goal'])
            before=path.read_bytes()
            self.assertEqual(self.run_cli(path,'profile','--minutes','1').returncode,1);self.assertEqual(path.read_bytes(),before)
            self.assertEqual(self.run_cli(ROOT/'state/learning-state.example.json','init').returncode,1)

    def test_migration_preserves_original_and_keeps_errors_unresolved(self):
        with tempfile.TemporaryDirectory() as directory:
            old=Path(directory)/'v1.json';new=Path(directory)/'v2.json'
            state=completed('needs_support');state['schema_version']=1
            for a in state['assessments']:del a['resolves_assessment_ids']
            old.write_text(json.dumps(state));before=old.read_bytes()
            result=self.run_cli(new,'--allow-fixture','migrate','--from-state',str(old))
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(old.read_bytes(),before)
            migrated=engine.validate(json.loads(new.read_text()),allow_fixture=True)
            self.assertEqual(engine.unresolved_errors(migrated,migrated['lessons'][0]['topic_id']),['practice'])

    def test_real_lesson_artifact_is_required_and_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'state.json';self.assertEqual(self.run_cli(path,'init').returncode,0)
            record=lesson();record['id']='private-session';record_path=Path(directory)/'record.json'
            record_path.write_text(json.dumps(record));before=path.read_bytes()
            self.assertEqual(self.run_cli(path,'add','lessons',str(record_path)).returncode,1)
            self.assertEqual(path.read_bytes(),before)
            artifact=path.parent/record['artifact'];artifact.parent.mkdir(parents=True);artifact.write_text('Synthetic private lesson')
            self.assertEqual(self.run_cli(path,'add','lessons',str(record_path)).returncode,0)
            s=json.loads(path.read_text());s['lessons'][0]['artifact']='../outside.md';path.write_text(json.dumps(s))
            self.assertEqual(self.run_cli(path,'validate').returncode,1)

    def test_real_migration_copies_lesson_files_and_refuses_missing_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);old=directory/'v1.json';new=directory/'private/state.json'
            state=completed('needs_support');state['fixture']=False;state['schema_version']=1
            for a in state['assessments']:del a['resolves_assessment_ids']
            old.write_text(json.dumps(state));before=old.read_bytes()
            self.assertEqual(self.run_cli(new,'migrate','--from-state',str(old)).returncode,1)
            self.assertFalse(new.exists())
            source=directory/'original';artifact=source/state['lessons'][0]['artifact'];artifact.parent.mkdir(parents=True);artifact.write_text('Synthetic migration lesson')
            result=self.run_cli(new,'migrate','--from-state',str(old),'--artifact-root',str(source))
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(old.read_bytes(),before)
            self.assertEqual((new.parent/state['lessons'][0]['artifact']).read_text(),artifact.read_text())
            self.assertEqual(self.run_cli(new,'validate').returncode,0)

    def test_seven_day_synthetic_cli_loop(self):
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);path=directory/'state.json';engine.atomic_save(path,empty())
            def run(*args):
                result=self.run_cli(path,'--allow-fixture',*args)
                self.assertEqual(result.returncode,0,result.stderr)
                return result.stdout
            def save(name,data):
                p=directory/name;p.write_text(json.dumps(data));return str(p)
            l=lesson();run('add','lessons',save('lesson.json',l))
            self.assertEqual(json.loads(run('plan','--on','2026-10-05','--prerequisite','ready'))['action'],'deliver')
            run('transition',l['id'],'assigned','--on','2026-10-05')
            run('transition',l['id'],'in_progress','--on','2026-10-05')
            run('add','assessments',save('practice.json',assessment(l)))
            run('transition',l['id'],'completed','--on','2026-10-05')
            review={'id':'r','lesson_id':l['id'],'topic_id':l['topic_id'],'prompt':'Fixture recall','initial_due_on':'2026-10-06','due_on':'2026-10-06','attempts':[]}
            run('add','reviews',save('review.json',review))
            fail=assessment(l,'fail','retrieval','2026-10-06','needs_support')
            run('add','assessments',save('fail.json',fail));run('review','r','fail','--next-due','2026-10-06','--reason','Fixture immediate correction')
            retry=assessment(l,'retry','retrieval','2026-10-06');retry['resolves_assessment_ids']=['fail']
            run('add','assessments',save('retry.json',retry));run('review','r','retry','--next-due','2026-10-08','--reason','Fixture fresh repaired case')
            for day in ('2026-10-07','2026-10-08','2026-10-09'):
                run('plan','--on',day)
            recall=assessment(l,'later-recall','retrieval','2026-10-10');transfer=assessment(l,'later-transfer','transfer','2026-10-11')
            run('add','assessments',save('recall.json',recall));run('review','r','later-recall','--next-due','2026-10-15','--reason','Fixture delayed independent recall')
            run('add','assessments',save('transfer.json',transfer))
            p=json.loads(run('plan','--on','2026-10-11','--prerequisite','ready'))
            self.assertEqual(p['mastery'][l['topic_id']],'retained_and_transferred')
            state=json.loads(path.read_text());self.assertEqual(len(state['reviews'][0]['attempts']),3)
            self.assertEqual(state['reviews'][0]['attempts'][0]['scheduled_for'],'2026-10-06')


class PublicSiteTests(unittest.TestCase):
    def test_only_public_content_is_staged(self):
        spec=importlib.util.spec_from_file_location('build',ROOT/'scripts/build_public_site.py')
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'source';source.mkdir()
            for name in (*builder.PUBLIC_FILES, *(f'labs/boundary-search/{p}' for p in builder.PUBLIC_LAB_FILES), *(f'vi/{p}' for p in ('README.md','_404.md','_sidebar.md','_navbar.md'))):
                target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
            for path in builder.catalog_files(ROOT):
                target=source/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
            for name in builder.PUBLIC_DOC_DIRS: shutil.copytree(ROOT/name,source/name,dirs_exist_ok=True)
            for name in ('.learning-private/learning-state.json','state/learning-state.json','lessons/private/lesson.md'):
                p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('SYNTHETIC_PRIVATE_MARKER')
            out=Path(directory)/'site';builder.build(source,out)
            self.assertTrue((out/'index.html').is_file())
            self.assertTrue((out/'lessons/boundary-search/lesson.md').is_file())
            self.assertTrue((out/'lessons/2026-10-05-cost-model/lesson.md').is_file())
            self.assertTrue((out/'vi/lessons/2026-10-05-cost-model/lesson.md').is_file())
            self.assertTrue((out/'state/learning-state.example.json').is_file())
            self.assertFalse((out/'state/learning-state.json').exists())
            for name in ('.learning-private','.git','tests','scripts','.github'):
                self.assertFalse((out/name).exists())
            self.assertFalse((out/'lessons/private/lesson.md').exists())
            self.assertFalse(any('SYNTHETIC_PRIVATE_MARKER' in p.read_text() for p in out.rglob('*') if p.is_file()))
            with self.assertRaises(ValueError):builder.build(source,out)
            (source/'index.html').unlink();(source/'index.html').symlink_to(source/'.learning-private/learning-state.json')
            with self.assertRaises(ValueError):builder.build(source,Path(directory)/'symlink-site')
            catalog={'lessons':[{'id':'invalid','files':['.learning-private/learning-state.json']}]}
            (source/'lessons/catalog.json').write_text(json.dumps(catalog))
            with self.assertRaises(ValueError):builder.catalog_files(source)


class LabRegressionTests(unittest.TestCase):
    def test_linear_or_mutating_window_submission_fails_checks(self):
        spec=importlib.util.spec_from_file_location('checks',ROOT/'labs/boundary-search/check.py')
        checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
        class Linear:
            @staticmethod
            def count_window(data,start,end): return sum(start<=x<end for x in data)
        checks.MODULE=Linear
        result=unittest.TestResult();checks.TransferChecks('test_window_access_budget_and_no_copy').run(result)
        self.assertTrue(result.failures or result.errors)
        class Mutating:
            @staticmethod
            def count_window(data,start,end):
                if end<start:raise ValueError()
                value=sum(start<=x<end for x in data);data.reverse();return value
        checks.MODULE=Mutating
        result=unittest.TestResult();checks.TransferChecks('test_half_open_time_window').run(result)
        self.assertTrue(result.failures or result.errors)

if __name__=='__main__':unittest.main()
