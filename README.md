# Computer Science Learning Agent

[English](README.md) · [Tiếng Việt](vi/README.md)

A curriculum-grounded daily CS tutor with research, reproducible practice, delayed review and evidence-bearing progress. IUH Master's and PhD curricula are reference implementations; the workflow can serve other curricula.

## Learn each day

1. Ask the agent to use [master-iuh-daily-learning](skills/master-iuh-daily-learning/SKILL.md), stating your goal, available minutes and tools. Example: “Give me a 25-minute lesson; I know arrays but am unsure about loop invariants; Python is available.”
2. The agent reads [canonical state](state/learning-state.json), due reviews and unfinished work, then collects a prerequisite response. Unknown skill is not assumed mastered. Today may be review-only or prerequisite repair.
3. Study one researched core objective using a worked example, step-by-step lab and independent transfer task. Ask for progressive hints if needed. Short/standard/extended modes adapt scope to your time.
4. Submit your code/trace, actual output and explain-back. The agent records only observed attempts, hints, misconceptions and assessment evidence. Generated content and agent verification never prove your learning.
5. After completion, choose a next review date based on results and retention goal. Later recall and changed-context performance strengthen evidence; completion alone does not establish mastery.

Read the [daily workflow](references/learning-workflow.md) for CLI updates and fallback behavior. [The complete sample](lessons/boundary-search/lesson.md) includes a deterministic offline lab, pinned GitHub source/test activity, independent challenge and rubric. It has not been assigned and is outside real progress.

## Research and policies

- [Repository review before changes](research/repository-review.md)
- [Learning-science evidence, citations and access limitations](research/learning-science-review.md)
- [Pedagogy](references/pedagogy.md), [source policy](references/source-policy.md), [lesson template](references/lesson-template.md)
- [Learning ledger pointer](state/learning-ledger.md) and [versioned state schema](state/learning-state.schema.json)
- [Verification results and remaining limits](research/verification.md)

One policy owner per contract; SKILL dispatches rather than copying them. The only learner state is `state/learning-state.json`. English and Vietnamese ledger pages point to it. Fixtures never enter learner progress. A JSON file and local scripts are enough; no backend/database is required.

## Local validation

Use Python 3.12. The lab itself uses only the standard library; schema checks use a pinned development dependency.

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py validate
python scripts/learning_state.py plan
python scripts/generate_curriculum_map.py --check
python scripts/validate_docs_navigation.py
python scripts/validate_learning.py
python -m unittest discover -s tests -v
```

To inspect synthetic scenarios without touching real progress:

```bash
python scripts/learning_state.py --state tests/fixtures/low-result.json --allow-fixture plan --prerequisite ready
```

Learner lab commands are in the sample; `starter.py` intentionally needs implementation. Full challenge solutions are separate mentor material, opened only after an attempt, explicit request or worked review. CI verifies the mentor implementation, not learner completion. Do not interpret checkpoint test counts as mastery scores.

## Curriculum and generated files

[Master's curriculum](curricula/iuh/master/curriculum.md) and [PhD curriculum](curricula/iuh/phd/curriculum.md) own English curriculum facts. Their historical source dates remain intact. Vietnamese curriculum pages are reader-facing translations. The [generated map](references/curriculum-map.md) separates extracted official relationships from labelled learning-agent synthesis.

```bash
python scripts/generate_curriculum_map.py
python scripts/generate_curriculum_map.py --check
```

Edit the curriculum or generator, never generated maps manually. No original PDF or live IUH-regulation verification was performed in this refactor; condensed curricula do not replace current institutional rules.

## Documentation and localization

Docsify site: [English](https://nguyenan97.github.io/computer-science-learning-agent/#/) · [Tiếng Việt](https://nguyenan97.github.io/computer-science-learning-agent/#/vi/). This task changes repository files only; it does not publish or deploy.

English owns policy/fact authoring; Vietnamese mirrors the same contract version. Field names and canonical state do not change with language. Translation version/navigation checks are structural; semantic parity needs human review. Shared scripts, code and metadata are not duplicated under `vi/`.

Use hash routing for GitHub Project Pages. Sidebars contain documentation routes only; navbars own language switching. Use root-relative Docsify routes, without hard-coded `#/` in navigation. Keep `loadNavbar: true`, `navbarPreservePath: true` and `fallbackLanguages: ['vi']`. `404.html` remains the physical deep-link fallback. Existing navigation/map workflows and the new learning workflow run checks automatically.

Key paths: `skills/` dispatch skill; `references/` owned contracts and map; `research/` evidence/review/results; `state/` canonical JSON/schema and pointer; `lessons/` sample handout/record/source dossier; `labs/` student starter/checkpoints and gated mentor material; `tests/` isolated scenarios; `scripts/` validators/local state CLI; `vi/` translations.

## License

A project license still needs to be selected before encouraging external contributions. Curriculum-derived Markdown retains source attribution. This refactor does not invent a license or vendor third-party implementation code.
