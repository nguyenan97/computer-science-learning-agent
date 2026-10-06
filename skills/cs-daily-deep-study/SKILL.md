---
name: cs-daily-deep-study
description: >-
  Write complete bilingual CS self-study days mapped to IUH master and doctoral
  outlines. Use for bài hôm nay, today's/next lesson, full-day research, paper
  reading, labs, recall or clarification of an existing lesson.
---

# Daily IUH Computer Science self-study

This is a repository-scoped Codex skill. Locate the repository root with Git.
Use this canonical file through `.agents/skills/cs-daily-deep-study` discovery.
Match the conversation language; every daily lesson is complete in English and Vietnamese.

## Plan the day

1. Read the single [lesson spec](../../references/lesson-spec.md).
2. Run `python scripts/daily_plan.py`, or supply `--on YYYY-MM-DD` when the learner
   names a study date. Its default calendar is Asia/Ho_Chi_Minh.
3. Follow the returned topic: an uncovered master unit with published prerequisites,
   then a doctoral unit after the master inventory is covered. Inventory order breaks
   ties. Coverage counts published artifacts and never certifies knowledge or a degree.
4. If today's lesson already exists, return it rather than generate a duplicate.
   An explicitly requested topic may override selection; explain the prerequisite bridge.
5. Use the returned `build` or `paper` schedule and opening recall. Both use the budget
   in [study profile](../../references/study-profile.json); honor a smaller request.
6. Keep the familiar C#/data context, deepen proofs, critical paper reading,
   reproduction and research writing progressively. Current-chat errors can guide a
   fresh correction; do not save answers, scores or a progress log.

## Teach on the page

Explain the full objective in connected prose: foundation, derivation, narrated trace,
complete task code, expected observations, worked answers and limits.
Sources and ZIPs supplement the explanations. An outline or link list is insufficient.
Provide optional self-checks, a foundation bridge and a reading-only route.
Every recall prompt, exercise and lab has a complete answer available immediately,
inside a collapsible `<details>` block under its prompt (see the lesson spec).
Trying first is optional; access to the next lesson requires no submission.

Page rules that readers flagged on lesson 1 (details in the lesson spec):
- Open with a short concept primer for the central ideas (e.g. Big-O), using a plain
  explanation and a small example before formal definitions. Familiar English developer
  words do not need glossary entries; explain supporting ideas where they are used.
- No "full day / 420 minutes" header or schedule table. Put the activity, minutes
  and task at the start of each section, and a one-line divider for breaks.
- Plain hyphen `-` only; never `—` or `–`.
- Natural Vietnamese with precise technical and research terminology, following
  [vi-style-glossary](../../references/vi-style-glossary.md). Keep familiar English
  words where useful, without compulsory glosses; use established Vietnamese terms
  for the explanation. Never use "khử trùng" for deduplication. Remove filler while
  preserving assumptions, evidence and limits needed for a correct conclusion.
- Real-world application plus one researched case study from a well-known GitHub
  repository, pinned to a commit: what problem the idea solves there and how to apply it.
- Preserve substantive depth and practice for the whole day while removing redundant
  prose. Add traces, scenarios or sources only when an objective needs more material.

A build day emphasizes implementation, debugging and a controlled experiment.
A paper day produces annotations, a claim ledger, a reproduced result or derivation,
and a cited critique. Reading with such output is active work; no percentage quota
penalizes paper study. Use the profile's output and stop conditions to bound the day.

C# is the default executable lab; T-SQL handles data work. Use Python only for an
essential research ecosystem, with a concrete C# bridge. A paper's derivation may be
reproduced analytically when executable reproduction is unavailable; label that scope.

## Sources and verification

Use primary papers, standards, official documentation and a manageable code slice.
Pin implementation links to a commit SHA and explain the slice's teaching value.
Separate verified findings, predictions and instructor inference. Never invent access,
measurements or novelty. Preserve citations and third-party license notices.
Use the IUH source only for names/codes; do not republish its syllabus descriptions.

Review EN/VI meaning, code, commands, examples, answers and limitations. Scan
the Vietnamese for literal translations and for any `—`/`–` before publishing.
Run `python scripts/check_all.py`; it bootstraps dependencies and the SDK in a fresh
checkout. Required checks include labs and extracted ZIPs. Browser and benchmark
checks are separate diagnostics; report whether they ran.

## Publish through a PR

“Bài hôm nay” authorizes generic public pages, lab assets and a PR. Write
`lessons/<id>/lesson.md`, its complete `vi/lessons/<id>/lesson.md` mirror and shared labs.
Add date, `topic_ids`, `day_type`, titles, files, related reading and three bilingual
recall question/answer entries to the catalog. Use the study date for the ID and date.
Run `python scripts/add_lesson_navigation.py` to refresh navigation and coverage.
Never edit generated blocks or hard-code lesson order.

The learner normally merges on GitHub. Merge only if the current conversation
explicitly authorizes it; existing authorization need not be requested again.
After a merge, verify Pages before claiming the lesson is live.
No automatic daily schedule is created. Finish with the objective, recall choice,
verified artifacts and the PR or verified live page link.
