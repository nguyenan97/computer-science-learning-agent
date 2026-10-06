# Maintaining the learning agent

Daily lessons use the public catalog. They do not require learner state, saved
answers, attendance or completion. The learner requests each day manually in Codex.

## Codex and environment setup

The root [AGENTS.md](../AGENTS.md) selects the canonical
[cs-daily-deep-study skill](../skills/cs-daily-deep-study/SKILL.md), also discoverable
through `.agents/skills/cs-daily-deep-study`. Both paths use one skill source.
The single [lesson spec](../references/lesson-spec.md) owns authoring requirements.

Use Python 3.12 and install the development dependencies. From the repository root:

```bash
bash scripts/setup_environment.sh
work/venv/bin/python scripts/check_all.py
```

The setup script installs the pinned .NET SDK used by the labs and prepares Python
dependencies in `work/venv`. Activate that virtual environment before using the
short `python` commands below. To make setup available in a new Codex cloud session, add the script
invocation to that environment's setup configuration; a session-local installation
does not configure future containers. Follow the script's output for its SDK path.
Do not claim environment configuration was changed merely because local setup ran.

## Add a lesson

Write the complete page in `lessons/<id>/lesson.md` and
`vi/lessons/<id>/lesson.md`, with shared runnable lab assets. Use C# by default,
T-SQL for data work and Python only for an essential ecosystem with a C# bridge.
Explanations, essential code and complete answers belong on each page; sources and
downloads are supplements. Do not publish agent logs, audit dossiers or learner data.

Update [catalog](../lessons/catalog.json) with its date, bilingual title, public
files, related reading, three bilingual recall questions/answers and runnable lab
metadata. Lab entries identify language, directory, correctness command and an
optional archive; optional benchmark commands are diagnostic. Catalog entries are
the source for navigation, lab archives, the public build and correctness runs.

```bash
python scripts/review_queue.py --on YYYY-MM-DD
python scripts/add_lesson_navigation.py
work/venv/bin/python scripts/check_all.py
```

Copy the queue's selected questions and worked answers into the new lesson opening.
It samples up to three eligible lessons deterministically, tolerates gaps in dates
and uses no learner history; it does not guarantee each lesson at every interval. Discuss
voluntary feedback in the current chat; do not persist a wrong-answer queue or log.

The navigation generator updates lesson footers, sidebars and marked homepage lists.
Do not edit generated blocks manually. To change the broader topic map, edit
[topics.json](../references/topics.json) and run `python scripts/generate_topic_map.py`.
Adding a lesson does not require changing the skill, contract or CI workflow.

## Verification and publication

The consolidated check runs required artifact validation, unit tests, catalog lab
correctness, public build and extracted archive checks. Structural EN/VI parity
does not replace a review of translation meaning. Browser verification and benchmark
Dry runs are separate diagnostics; report whether they actually ran and their limits.
Use `work/` for temporary copies so lab builds do not leave generated files in source.

A request for today's lesson authorizes generic public files and a PR. Open the PR
after checks pass, but merge or push main only after an explicit instruction. The
existing main-branch Pages workflow deploys after required validation. Verify its
result before reporting a new page as live. Local staging alone is not publication.

The public builder stages catalog assets and a small explicit learner-document set,
generates lab archives and normalizes links for Docsify. Verify both language pages,
navigation and extracted lab commands. Never expose state, private directories or
internal reports through the public file list. Tests verify code and content;
they do not establish learner proficiency or educational effectiveness.

## Legacy tools and provenance

`scripts/learning_state.py` and the retained schema/tests are legacy maintainer tools,
outside the daily loop. No real learner state is needed or initialized, and there is
no old state to retain; v1/v2 migration support has been removed. Do not add a new state schema or mastery
model to support ordinary lesson creation.

Keep attribution and redistribution limits in
[content provenance](content-provenance.md). The repository's public content should
be original explanations with concise citations. Raw institutional syllabus extracts
and internal research reviews are not public learning assets. Existing history is
not rewritten by these authoring and build rules.
