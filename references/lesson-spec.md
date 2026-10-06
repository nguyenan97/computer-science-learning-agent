# Daily lesson spec

This is the single authoring contract for the [Codex skill](../skills/cs-daily-deep-study/SKILL.md).
The catalog supplies publication dates, order, bilingual titles, recall and lab metadata.
The website teaches the learner; this spec governs authoring and remains repository documentation.

## Scope and selection

Self-study follows IUH master (2020) and doctoral (October 2022) course-name
inventories, with original project objectives and prerequisites. Read the public
[topic map](topic-map.md) and [source scope](../docs/content-provenance.md).
No credits, admissions, degree award or verified proficiency are inferred.

Run `python scripts/daily_plan.py --on YYYY-MM-DD`. The default date is the study date
in **Asia/Ho_Chi_Minh**, including an evening or early-morning request. The script
chooses the first uncovered eligible master topic, then doctoral topics after all
master units are represented. Array order breaks ties; only published catalog
`topic_ids` on or before that date satisfy prerequisites. The same input produces
the same plan. An existing same-day lesson is returned rather than duplicated.
An explicit topic request may override this order with a stated foundation bridge.

Coverage is the ratio of planned topics with published artifacts in each level/area.
One lesson may name several topics only when its actual content teaches their stated
objectives. Repeated lessons do not inflate the count. This is artifact coverage,
not evidence that the learner studied or mastered a topic. All elective names are
available for optional breadth; the inventory does not assert official enrollment choices.

## Build day and paper day

[study-profile.json](study-profile.json) owns the default **420 elapsed minutes**,
the Vietnamese timezone and both block schedules. Both schedules sum to that budget
and include breaks. Honor a shorter explicit request. A bridge replaces depth work;
bound setup, stop a block at its timebox and carry unresolved questions forward.
Do not copy a budget table into the contract or require an active-work percentage.

A **build day** produces an invariant/trace, runnable implementation, edge-case
checks, a controlled experiment and a changed-context worked answer.
A **paper day** produces annotated claims and methods, an explicit claim ledger,
one reproduced result or derivation, a comparison and a cited critique. Reading
that produces an argument, annotation, claim ledger or reproduction counts as active
work. Passive reading is allowed but does not stand in for those planned outputs.
Paper study is not forced to include a benchmark or a new code lab when analytic
reproduction better tests the objective. Explain any unrun executable reproduction.

Each block has the profile's concrete output plus an objective-specific stop condition.
Offer a reading-only route through worked traces, lab explanations and answers.
All tasks remain optional, and access to tomorrow's lesson requires no submission.

## Recall without learner records

Use the recall returned by `daily_plan.py`; the standalone
`python scripts/review_queue.py --on YYYY-MM-DD` uses the same Vietnamese calendar. Start with its selection of at most three
questions from earlier catalog lessons around the 1, 3, 7 and 21-day offsets.
Selection is deterministic and tolerates gaps in publication dates. The daily cap
samples eligible intervals; it does not guarantee every lesson appears at every
offset. These offsets are a project heuristic, not a proven optimum for this learner.

Each catalog lesson has three recall entries, with English and Vietnamese questions
and complete answers. Questions should reconstruct a mechanism, justify a choice or
find a counterexample rather than repeat trivia. Provide the selected questions and
answers on the new page; suggest recalling before opening the answer when useful.
If there are no eligible lessons, proceed with prerequisite self-checks.

The queue uses catalog dates, not attendance, submission or completion. Do not claim
the learner performed a review because a prompt was delivered. No learner answers,
scores or progress logs are persisted. Discuss voluntary feedback in the current chat;
a fresh relevant example can repair a reported error without changing access to lessons.

## Teach completely in English and Vietnamese

Each page independently teaches the whole objective in connected prose. Include:

- Practical motivation, the main objective and concrete prerequisites with optional
  self-checks, worked answers and a foundation bridge.
- The selected build/paper plan for this particular day, followed by a concrete contract,
  prediction, foundation, narrated example or trace and a counterexample.
- A few answerable research questions, source-backed explanations, an implementation
  slice and the assumptions that connect theory to behavior.
- Complete runnable task code, copyable commands, expected observations, debugging
  guidance and a controlled experiment with an interpretation of its limits.
- A changed-context task, explained solutions, useful success criteria and a short
  synthesis of the model, trade-offs and remaining questions.

Every prompt has an immediately accessible complete answer, beside it or in a
collapsible section. Hints may offer a route to the answer but never impose an attempt
or submission requirement. Answers should explain reasoning and edge cases, not just
show final code. An answer already seen is not evidence of independent retrieval.

Keep code, commands, cases, table structure and substantive content aligned in both
languages. Translate explanatory comments when helpful without changing behavior.
Structural parity checks supplement a review of meaning; equal headings alone do
not prove an accurate translation.

Write only learner-useful information on the page. Internal audits and
source-access logs and agent verification reports belong in maintainer work, not
the lesson or published catalog assets. Cite relevant claims briefly and describe
source or execution limitations only when they affect understanding or reproduction.

## Sources and code

Use a small useful set of primary papers, standards, official documentation and
implementation code. Say what claim or question each source supports. Distinguish
stable theory, version-specific behavior and instructor inference. Inspect the
sections needed for the claim; abstract-only access cannot establish methods or
full-paper findings. On access failure, use a verified alternative or state the limit.

For a selected repository slice, pin an immutable commit SHA and explain its teaching
value in one sentence. Do not build routine popularity, maintenance or star dossiers.
Preserve attribution and redistribution notices. Explain essential ideas in original
words; do not publish raw paper, institutional syllabus or repository text extracts.

C# is the default lab language. Use T-SQL for database examples and experiments.
Python is justified only when the necessary research or technical ecosystem requires
it; include a concrete C# bridge describing the equivalent API, invariant or design.
Choose the simplest tool that tests the objective, without unnecessary infrastructure.

Give runtime/dependency pins, working directories, commands, deterministic cases and
an offline fallback. Include the essential implementations and solutions on the page;
a ZIP is a convenience copy. Code must run under the stated environment. Distinguish
observed output from predictions and unrun examples. Measurements need a hypothesis,
controls, workload and limitations; one machine cannot establish universal performance.

## Repository workflow

Generic lessons and shared labs are public by default. A request for today's or the
next lesson authorizes writing them and opening a PR; merging or pushing main still
requires an explicit instruction. There is no automatic daily schedule. The learner
requests a lesson when ready, including the next morning after a skipped evening.

1. Add EN and VI lesson pages and shared lab assets, then update the catalog with
   bilingual title, Vietnamese study date, `topic_ids`, `day_type`, files, related
   reading, recall and lab metadata.
2. Run `python scripts/add_lesson_navigation.py`. The catalog generates lesson footers,
   sidebars, homepage lists and topic coverage; neither contract nor workflow maintains lesson order.
3. Run `python scripts/check_all.py`; a fresh session bootstraps its environment automatically. Correctness,
   structural parity and public-asset checks are required. Optional browser/benchmark diagnostics belong in verification,
   with observed results reported honestly.
4. Inspect the staged lesson, language switch, catalog links and downloads. Test the
   extracted lab when producing a ZIP. Sources and downloads supplement the full page.
5. Open a PR and return its link. After an explicitly authorized merge, verify Pages
   deployment before claiming the new public URL works.

Use `work/` for temporary verification. Never commit personal submissions or records.
There is no personal-progress engine. Agent checks verify artifacts; only actual learner work can support
an observation about learning, and no such record is retained by this workflow.

Original project prose uses CC BY 4.0 and original code snippets use MIT.
Keep third-party notices and source citations; see [licensing](../docs/licensing.md).
