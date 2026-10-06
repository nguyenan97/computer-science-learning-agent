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

Every lesson is a full day, so the page never announces it. Do not put a header line such
as "full day: 420 minutes", a study/break split or an "updated" date under the title,
and do not open with a schedule table. Put the plan where the learner needs it: each
major section starts with one line, e.g. `**Block foundation · ~50 phút · Làm:** trace
the table by hand, then state the invariant`, taken from the profile block it
implements, with its stop condition. Breaks and lunch get a one-line divider at the
point where they fall. The section minutes plus breaks still sum to the profile budget.

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
- A **concept primer** right after the objective and before any derivation: every
  term the lesson depends on (for a Big-O lesson: Big-O itself, cost model, worst/
  expected/amortized case, collision, invariant) gets a one-to-two sentence idea in
  plain words and a tiny concrete example. Say what question it answers. Formal
  definitions, quantifiers and proofs come later in the body. A term may not first
  appear in a section heading, table or answer without having been introduced here.
- A **real-world application** section: where this idea shows up in a production
  .NET/SQL Server/Angular/Azure system, then one case study from a well-known public
  repository (see Sources and code). Say what problem the project solves with the
  idea, what would break without it and what trade-off the maintainers accepted.
- The selected build/paper plan for this particular day, followed by a concrete contract,
  prediction, foundation, narrated example or trace and a counterexample.
- A few answerable research questions, source-backed explanations, an implementation
  slice and the assumptions that connect theory to behavior.
- Complete runnable task code, copyable commands, expected observations, debugging
  guidance and a controlled experiment with an interpretation of its limits.
- A changed-context task, explained solutions, useful success criteria and a short
  synthesis of the model, trade-offs and remaining questions.

Every prompt has an immediately accessible complete answer. Put each one in a
collapsible `<details><summary>Đáp án</summary>` block (`Answer` in English) directly
under its prompt, with a blank line after `<summary>` so Markdown, tables and code
inside render. Never print answers inline under the question; the learner decides when
to open them. A one-click answer is still immediate and requires no submission. Group
the self-check answers per question, not as one wall of text. Hints may offer a route
to the answer but never impose an attempt or submission requirement. Answers should explain reasoning and edge cases, not just
show final code. An answer already seen is not evidence of independent retrieval.

### Wording, typography and depth

- Use a plain hyphen `-` for punctuation. Never use the em dash `—` or en dash `–`
  in lesson prose, titles, tables or headings; use `-`, a comma or a new sentence.
  Numeric ranges use `-` too (`0-20`).
- Write Vietnamese the way developers speak at work. Keep established English terms
  as they are and follow [vi-style-glossary](vi-style-glossary.md): e.g. *duplicate*,
  *dedupe*, *hash*, *bucket*, *collision*, *trace*, *benchmark*, *worst case*, *amortized*.
  Do not coin literal translations ("khử trùng", "khấu hao", "chặn trên" for terms
  engineers say in English). On the first use of a kept term, add a short Vietnamese
  gloss in parentheses; later uses stay English. Vietnamese carries the connecting
  sentences, not the vocabulary. If a sentence needs a dictionary, rewrite it.
- Short sentences, one idea each. Show the concrete example before the formula or
  definition. Prefer "mỗi lần `Contains` quét hết list" over abstract nominalizations.
- The English page follows the same rule: plain words, no jargon unexplained.
- Depth is measured against the day's budget, not a page count: every profile block
  needs matching material on the page (primer, trace, source reading, real-world
  case, lab, experiment, changed-context task, synthesis). A page that finishes
  the objective in a few minutes of reading is too thin. Add worked variations,
  more traces, a production scenario or a second source before shortening anything.

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

Each lesson also needs a **real-world case study**: research one well-known public
repository (framework, runtime, database, messaging or developer tool) that applies
this lesson's idea, preferably in the learner's .NET/SQL Server/Angular/Azure world.
Read the actual code or docs at a pinned commit and report: the file/function, what
problem the idea solves there, the data size or workload the maintainers care about,
the alternative they avoided, and how the learner could apply the same decision in
their own project. Reading the standard library implementation of the data structure
is source reading, not a case study; the case study shows the idea *used to solve a
product problem*. State what was verified in the code and what is inference. If the
repository cannot be reached, choose another verified one or say so; never invent a
usage or a link.
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
