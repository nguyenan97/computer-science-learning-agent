#!/usr/bin/env python3
"""Check real state, sample/fixture isolation, owned contracts and sample artifacts."""
import json
from pathlib import Path
import re
import subprocess
import yaml
from learning_state import ROOT, TEMPLATE, validate


def validate_skill():
    directory=ROOT/'skills/cs-daily-deep-study'
    text=(directory/'SKILL.md').read_text()
    match=re.match(r'\A---\n(.*?)\n---\n',text,re.S)
    if not match: raise ValueError('skill requires YAML frontmatter')
    metadata=yaml.safe_load(match[1])
    name=metadata.get('name',''); description=metadata.get('description','')
    if (not isinstance(name,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name)
            or len(name)>64 or name!=directory.name
            or not isinstance(description,str) or not 1<=len(description)<=1024):
        raise ValueError('skill name/description violates Agent Skills specification')
    interface=yaml.safe_load((directory/'agents/openai.yaml').read_text())['interface']
    if f'${name}' not in interface['default_prompt']:
        raise ValueError('OpenAI default prompt must mention the skill')
    cases=json.loads((directory/'evals/cases.json').read_text())
    ids=[case['id'] for case in cases['evals']]
    if cases['skill_name']!=name or not ids or len(ids)!=len(set(ids)):
        raise ValueError('skill evaluation cases require matching skill and unique IDs')


def main():
    validate_skill()
    tracked=subprocess.run(['git','ls-files','--','.learning-private'],cwd=ROOT,check=True,capture_output=True,text=True)
    if tracked.stdout.strip(): raise ValueError('private learner workspace must not be tracked by Git')
    state=json.loads(TEMPLATE.read_text())
    validate(state)
    if any(state[c] for c in ('lessons','assessments','reviews')):
        raise ValueError('public initialization template must remain empty')
    if state['learner'] != {'timezone':'Asia/Bangkok','daily_minutes':None,'goals':[],'background':None}:
        raise ValueError('public template must not contain a real learner profile')
    for path in (ROOT/'tests/fixtures').glob('*.json'):
        fixture=json.loads(path.read_text())
        if fixture.get('fixture') is not True: raise ValueError(f'{path}: fixture marker missing')
        validate(fixture,allow_fixture=True)
    sample=json.loads((ROOT/'lessons/boundary-search/record.json').read_text())
    synthetic={'schema_version':3,'fixture':True,'learner':state['learner'],'lessons':[sample],'assessments':[],'reviews':[]}
    validate(synthetic,allow_fixture=True)
    if sample['id'] in {l['id'] for l in state['lessons']}: raise ValueError('sample leaked into learner state')
    for name in ('learning-workflow','pedagogy','source-policy','lesson-template'):
        en=(ROOT/f'references/{name}.md').read_text(); vi=(ROOT/f'vi/references/{name}.md').read_text()
        a=re.search(r'<!-- contract-version: (\d+) -->',en); b=re.search(r'<!-- contract-version: (\d+) -->',vi)
        if not a or not b or a[1]!=b[1]: raise ValueError(f'{name}: translation contract version mismatch')
    for page in ('state/learning-ledger.md','vi/state/learning-ledger.md'):
        text=(ROOT/page).read_text()
        if '.learning-private/learning-state.json' not in text or '<!-- LESSON_RECORD' in text: raise ValueError('ledger must point to private state')
    for l in [*state['lessons'],sample]:
        path=(ROOT/l['artifact']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file(): raise ValueError('lesson artifact missing or outside repo')
    lesson=(ROOT/sample['artifact']).read_text()
    for heading in ('Selection and measurable outcomes','Retrieval warm-up and prerequisite check','Problem and prediction','Foundation and mental model','Worked example','Guided lab','Read the standard-library implementation','Independent challenge','Rubric, feedback and explain-back','Further questions and review plan'):
        if not re.search(r'^## '+re.escape(heading),lesson,re.M): raise ValueError('sample missing section: '+heading)
    repo=json.loads((ROOT/'lessons/boundary-search/repository-evidence.json').read_text())
    if not re.fullmatch('[0-9a-f]{40}',repo['pin']) or not repo['checked_on']: raise ValueError('repo requires immutable pin and checked date')
    for target in repo['read_targets']:
        if repo['pin'] not in target['url']: raise ValueError('repo target is not pinned')
    # Local Markdown links are checked throughout docs, excluding Docsify root routes.
    for path in ROOT.rglob('*.md'):
        if any(part in ('.git','.learning-private','.site-build','.venv','work') for part in path.parts): continue
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)',path.read_text()):
            if target.startswith(('https:','http:','/','#','mailto:')): continue
            clean=target.split('#',1)[0]
            if clean and not (path.parent/clean).exists(): raise ValueError(f'{path.relative_to(ROOT)}: broken link {target}')
    print('Learning contracts, empty public template, fixture isolation, sample artifacts and local links valid.')
    print('Translation version checks are structural; semantic parity still requires bilingual review.')
    return 0

if __name__=='__main__': raise SystemExit(main())
