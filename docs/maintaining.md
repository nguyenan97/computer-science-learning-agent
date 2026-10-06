# Maintaining the learning agent

The public home and lesson pages teach the reader. This repository document covers authoring, private state and release checks.

## Authoring

Keep the repository available when using [cs-daily-deep-study](../skills/cs-daily-deep-study/SKILL.md); its instructions use shared [pedagogy](../references/pedagogy.md), [source policy](../references/source-policy.md), [template](../references/lesson-template.md) and [workflow](../references/learning-workflow.md). Every lesson has full English and Vietnamese explanations, inline worked answers and supplementary sources/downloads. Internal state, audit logs and agent implementation details belong in maintainer documents or private workspaces.

Edit [topics.json](../references/topics.json), then run `python scripts/generate_topic_map.py`. Keep publication order, bilingual titles and useful related links in [catalog](../lessons/catalog.json). Add only generic lesson/lab assets to its explicit `files` list. Run `python scripts/add_lesson_navigation.py` after publishing a new page or changing catalog order. It updates the bottom related/previous/next links for every language and never points to an unpublished lesson.

## Private state and migration

Use Python 3.12 and `requirements-dev.txt`. Canonical state defaults to ignored `.learning-private/learning-state.json` or an explicit external `--state`. Keep authored personal lessons, code and evidence beside it, untracked. Public [template](../state/learning-state.example.json) remains empty; [schema v3](../state/learning-state.schema.json) has no course codes. Initializing state is not required to read the website.

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py init
python scripts/learning_state.py validate
python scripts/learning_state.py plan
python scripts/learning_state.py plan --minutes 60
```

For existing v1/v2 state, choose a fresh destination and retain the source:

```bash
python scripts/learning_state.py --state /private/new/learning-state.json migrate --from-state /private/old/learning-state.json --artifact-root /private/old
```

Migration preserves source and evidence; course metadata remains in the original. Invalid old completion linkage is rejected without inventing observations. Artifact/state path collisions are rejected before copying. Storage supports one writer; atomic replacement is not locking or backup. Structural topic linkage does not establish semantic objective/evidence relevance, which the assessor must review. See workflow for lifecycle, error-repair links and review history.

## Validation and release

```bash
python scripts/generate_topic_map.py --check
python scripts/add_lesson_navigation.py --check
python scripts/validate_docs_navigation.py
python scripts/validate_learning.py
python -m unittest discover -s tests -v
python scripts/build_public_site.py --output .site-build
python scripts/check_lesson_site.py --site .site-build
```

The browser check needs playwright==1.62.0 and installed Chromium. CI additionally runs Python labs, .NET SDK 10.0.401 correctness checks, BenchmarkDotNet Dry and an extracted lab build. Checks verify artifacts, not learner mastery or educational effectiveness. The [verification record](../research/verification.md) and [learning-science review](../research/learning-science-review.md) give evidence and remaining limits; [skill scenarios](../skills/cs-daily-deep-study/evals/cases.json) are specifications, not executed model benchmarks.

The site builder normalizes repository Markdown links to Docsify routes, sends assets outside hash routing and stages only public content. Main-branch deployment calls the reusable validation job on the same `github.sha` and requires success. Editing or local staging does not publish; merging/pushing main triggers the existing Pages workflow.

Inherited [attribution](../research/content-provenance.md) is retained separately from topic selection. A project license remains undecided. Semantic bilingual parity requires review beyond structural checks.
