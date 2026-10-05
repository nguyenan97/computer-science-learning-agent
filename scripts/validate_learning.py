#!/usr/bin/env python3
"""Check real state, sample/fixture isolation, owned contracts and sample artifacts."""
import json
from pathlib import Path
import re
from learning_state import ROOT, validate


def main():
    validate(json.loads((ROOT/'state/learning-state.json').read_text()))
    for path in (ROOT/'tests/fixtures').glob('*.json'):
        state=json.loads(path.read_text())
        if state.get('fixture') is not True: raise ValueError(f'{path}: fixture marker missing')
        validate(state,allow_fixture=True)
    state=json.loads((ROOT/'state/learning-state.json').read_text())
    sample=json.loads((ROOT/'lessons/boundary-search/record.json').read_text())
    synthetic={'schema_version':1,'fixture':True,'learner':state['learner'],'lessons':[sample],'assessments':[],'reviews':[]}
    validate(synthetic,allow_fixture=True)
    if sample['id'] in {l['id'] for l in state['lessons']}: raise ValueError('sample leaked into learner state')
    for name in ('learning-workflow','pedagogy','source-policy','lesson-template'):
        en=(ROOT/f'references/{name}.md').read_text(); vi=(ROOT/f'vi/references/{name}.md').read_text()
        a=re.search(r'<!-- contract-version: (\d+) -->',en); b=re.search(r'<!-- contract-version: (\d+) -->',vi)
        if not a or not b or a[1]!=b[1]: raise ValueError(f'{name}: translation contract version mismatch')
    for page in ('state/learning-ledger.md','vi/state/learning-ledger.md'):
        text=(ROOT/page).read_text()
        if 'learning-state.json' not in text or '<!-- LESSON_RECORD' in text: raise ValueError('ledger must point to canonical JSON')
    for l in [*state['lessons'],sample]:
        path=(ROOT/l['artifact']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file(): raise ValueError('lesson artifact missing or outside repo')
    lesson=(ROOT/sample['artifact']).read_text()
    for heading in ('Selection and measurable outcomes','Retrieval warm-up and prerequisite check','Problem and prediction','Foundation and mental model','Worked example','Guided lab','GitHub repository activity and evaluation','Independent challenge','Rubric, feedback and explain-back','Research sources and review hooks'):
        if not re.search(r'^## '+re.escape(heading),lesson,re.M): raise ValueError('sample missing section: '+heading)
    repo=json.loads((ROOT/'lessons/boundary-search/repository-evidence.json').read_text())
    if not re.fullmatch('[0-9a-f]{40}',repo['pin']) or not repo['checked_on']: raise ValueError('repo requires immutable pin and checked date')
    for target in repo['read_targets']:
        if repo['pin'] not in target['url']: raise ValueError('repo target is not pinned')
    # Local Markdown links are checked throughout docs, excluding Docsify root routes.
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts: continue
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)',path.read_text()):
            if target.startswith(('https:','http:','/','#','mailto:')): continue
            clean=target.split('#',1)[0]
            if clean and not (path.parent/clean).exists(): raise ValueError(f'{path.relative_to(ROOT)}: broken link {target}')
    print('Learning contracts, real state, fixture isolation, sample artifacts and local links valid.')
    print('Translation version checks are structural; semantic parity still requires bilingual review.')
    return 0

if __name__=='__main__': raise SystemExit(main())
