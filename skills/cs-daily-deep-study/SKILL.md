---
name: cs-daily-deep-study
description: >-
  Write and tutor complete bilingual Computer Science research days with runnable
  labs and worked answers. Use for today's/next lesson, bài hôm nay, học cả ngày,
  deep research, recall, labs, quizzes or clarification of an existing lesson.
---

# Daily Computer Science deep study

This is a repository-scoped Codex skill. Locate the repository root with Git;
the canonical skill is `skills/cs-daily-deep-study/SKILL.md`.
Match the conversation language. Deliver complete English and Vietnamese lessons.

## Load and select

1. Read [lesson spec](../../references/lesson-spec.md), the single authoring contract.
2. Read `lessons/catalog.json` and the relevant [topic map](../../references/topic-map.md).
   Inspect previous objectives before choosing one coherent next objective.
3. Use the learner's local date; an explicit requested date takes precedence.
   Run `python scripts/review_queue.py --on YYYY-MM-DD` for opening recall prompts.
4. Reuse stated context: full-day research, a familiar .NET/data stack and the goal
   of developing graduate-level reasoning. Build foundations, proofs, experiments
   and paper criticism progressively; do not claim a degree or certified mastery.
5. Prefer continuity and useful prerequisites. A deeper lesson needs a changed
   objective. Current-chat misunderstandings can guide a short correction.

## Write for the reader

Teach the entire objective on each language page: connected explanations,
derivations, narrated traces, complete task code, commands and interpreted results.
Sources and downloads supplement the page. An outline or reading list is insufficient.
Introduce unfamiliar foundations with optional self-checks and a worked bridge.
Provide a reading-only route and optional depth; no prior submission is required.

Use the spec's flexible blocks with outputs and stop conditions. Replace depth
with a foundation bridge when necessary; bound setup and offer an offline trace.
Keep the day focused on one objective with a small set of research questions.
Default to C# labs, T-SQL for data work. Use Python only when an essential ecosystem
requires it, and explain the transfer to C# rather than changing the teaching stack.

Every recall question, exercise, diagnostic and lab has a complete answer available
immediately. Trying first is optional. Hints, submission and completion never unlock
answers or the next lesson. Give concrete success criteria and explain likely errors.

## Research and verify

Use primary papers, standards, official documentation or a manageable implementation.
Explain what each citation supports and its relevant limits; separate observed results
from predictions and instructor inference. Pin implementation links to a commit SHA
and give one sentence explaining why that slice serves the objective.
Preserve attribution and license notices. Do not invent source access or measurements.
Do not publish source dumps, agent logs or internal audit dossiers as lesson content.

Review EN/VI meaning as well as structural parity: objectives, code, examples,
commands, experiments, answers, limits and troubleshooting must match.
Run `work/venv/bin/python scripts/check_all.py` after environment setup, including
the applicable runnable lab checks.
Check generated navigation, language routes and ZIP contents before calling a download
usable. Report actual checks and any unrun environment-dependent verification.

## Save and deliver

A request for today's/next lesson authorizes generic public lesson/lab files and a PR.
Write `lessons/<id>/lesson.md`, `vi/lessons/<id>/lesson.md` and shared lab assets;
add the entry, recall questions/answers and runnable lab metadata to the catalog.
Run `python scripts/add_lesson_navigation.py` to generate catalog-derived navigation.
Never hard-code lesson order in this contract or link to an unpublished future page.

Do not create learner state, assessment records, progress logs or automatic schedules.
Selection and recall use published catalog dates even when the learner skips a day.
The legacy state engine is outside this loop. Feedback is handled in the current chat.
Never interpret lesson delivery, reading or agent tests as learner proficiency.

Open a reviewable PR when GitHub access is available. Do not merge it or push to main
without a separate explicit instruction. After an authorized merge, verify deployment
before returning a live page link; otherwise return the PR and available preview.
End with a brief explanation of the objective, recall choice and verified deliverables.
