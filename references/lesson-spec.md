# Daily lesson spec

This is the single authoring contract for the [Codex skill](../skills/cs-daily-deep-study/SKILL.md).
The catalog supplies publication dates, order, bilingual titles, recall and lab metadata.
The website teaches the learner; this spec governs authoring and remains repository documentation.

## Scope and selection

Self-study follows IUH master (2020) and doctoral (October 2022) course-name
inventories, with original project objectives and prerequisites. Read the public
[topic map](topic-map.md) and [source scope](../docs/content-provenance.md).
No credits, admissions, degree award or verified proficiency are inferred.

For the next lesson run `python scripts/daily_plan.py --next` **before editing the
catalog**. It selects the day after the latest published catalog date, even when that
date differs from the machine's today. An empty catalog uses today's study date.
For an explicit date use `--on YYYY-MM-DD`; these date flags are mutually exclusive.
Without either flag, the default date is the study date
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

[study-profile.json](study-profile.json) owns the default elapsed-minute budget,
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
Sections may split or combine a block when the topic needs it, but the assigned minutes
and outputs must still account for that block. Do not make the learner hunt in an earlier
section for the current task/timebox. Supporting headings such as sources and licensing
need not invent additional study time. The [template](lesson-template.md) is an authoring
scaffold, not a mandated sequence of identical paragraphs.
Offer a reading-only route through worked traces, lab explanations and answers.
All tasks remain optional, and access to tomorrow's lesson requires no submission.

Every lesson is a full day, so the page never announces it. Do not put a header line such
as "full day: 420 minutes", a study/break split or an "updated" date under the title,
and do not open with a schedule table. Put the plan where the learner needs it: each
major section starts with one line, e.g. `**Nền tảng · 50 phút:** chạy từng bước theo
bảng, rồi nêu bất biến`, with the task and stop condition from the profile block it
implements. Use a reader-facing activity label, not an internal block ID. Breaks and lunch get a one-line divider at the
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
- A **concept primer** right after the objective and before any derivation: explain
  the few central ideas needed to follow the lesson, each in one or two plain
  sentences with a small example and the question it answers. For a Big-O lesson,
  prioritize the cost model, asymptotic bounds, expected/amortized reasoning and
  correctness invariant. This is not a dictionary of English developer vocabulary:
  API, input, output, query, test, debug and duplicate need no primer entries or
  compulsory glosses. Introduce supporting concepts where they become useful in
  the body. Formal definitions, quantifiers and proofs follow the intuitive examples.
- A **real-world application** section: where this idea shows up in a production
  .NET/SQL Server/Angular/Azure system, then one case study from a well-known public
  repository (see Sources and code). Say what problem the project solves with the
  idea, what would break without it and what trade-off the maintainers accepted.
- The selected build/paper activities embedded in section task/timebox/stop lines,
  with a concrete contract, prediction, foundation, narrated trace and a counterexample.
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
- Write complete, natural Vietnamese sentences with accurate technical and research
  terminology; follow [vi-style-glossary](vi-style-glossary.md). Keep familiar English
  terms when useful, without mandatory translations or primer entries. Use established
  Vietnamese terms where they clarify the idea, including mô hình chi phí, cận trên,
  bất biến, giả định and quan sát. Never translate deduplication as "khử trùng".
  Explain unfamiliar concepts in context, not by attaching a gloss to every English
  word. Remove redundant wording and English fragments that interrupt Vietnamese syntax.
- Research explanations connect the question, assumptions, method, evidence and
  limits of the conclusion. Distinguish a model assumption, a testable hypothesis,
  an observed result and an inference. Preserve qualifications needed for correctness;
  do not remove them merely to shorten a paragraph.
- Short sentences, one idea each. Show the concrete example before the formula or
  definition. Prefer "mỗi lần `Contains` quét hết list" over abstract nominalizations.
- The English page follows the same rule: plain words, no jargon unexplained.
- Depth is measured against the day's budget, not a page count: every profile block
  needs matching material on the page (primer, trace, source reading, real-world
  case, lab, experiment, changed-context task, synthesis). A page that finishes
  the objective in a few minutes of reading is too thin. Remove redundant prose while
  preserving substantive explanations and practice. Add worked variations, traces,
  production scenarios or sources only when an objective or block needs more material.

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
an offline fallback. Pin the SDK with roll-forward disabled, the executable runtime
version and its roll-forward policy, and external dependencies including their transitive
lock file. Say which installation/first restore needs a network and which run is offline.
Include the essential implementations and solutions on the page;
a ZIP is a convenience copy. Code must run under the stated environment. Distinguish
observed output from predictions and unrun examples. Measurements need a hypothesis,
controls, workload and limitations; one machine cannot establish universal performance.

A controlled experiment names assumptions, prediction, changed/fixed variables,
observation and inference separately. Put its worked result in a closed answer block
immediately below the task. Label simulated values even when they use real-world units.
Exact calculation under a model does not validate the model against reality. Explain
uncontrolled factors and what could falsify the claim. An independent oracle avoids
the main algorithm's key mechanism; name any shared validation, assumptions or
representation, finite cases covered and the argument needed for a general claim.

Complete runnable lab fences have a visible filename and an adjacent invisible marker
`<!-- lab-file: LessonLab/Program.cs -->` before the opening fence. Paths are relative
to the lab directory, including `global.json`, project files and dependency locks.
The catalog's declared source/config files determine the required set. Snippets and
changed-context replacements have no marker. `check_all.py` compares those fences
with downloads, builds/runs each language in isolation, and checks the source ZIP.
Keep code/setup in the lab's closed answer and individual defect questions outside it.
This checks executable agreement, not proof validity or translation quality.

## Repository workflow

Generic lessons and shared labs are public by default. A request for today's or the
next lesson authorizes writing them and opening a PR; merging or pushing main still
requires an explicit instruction. There is no automatic daily schedule. The learner
requests a lesson when ready, including the next morning after a skipped evening.

1. Save the planner result in ignored `work/` before changing the catalog. Explain
   the choice, inherited knowledge and missing foundation briefly on the page.
   Add EN and VI lesson pages and shared lab assets, then update the catalog with
   bilingual title, Vietnamese study date, `topic_ids`, `day_type`, files, related
   reading, recall and lab metadata.
2. Run `python scripts/add_lesson_navigation.py`. The catalog generates lesson footers,
   sidebars, homepage lists and topic coverage; neither contract nor workflow maintains lesson order.
3. Run `python scripts/check_all.py`; a fresh session bootstraps its environment automatically. Correctness,
   structural parity, page-derived executable checks and public-asset checks are required. Optional browser/benchmark diagnostics belong in verification,
   with observed results reported honestly.
4. Use the [review checklist](../docs/lesson-review.md) for semantic review and browser
   verification. Check desktop/mobile collapse, code, table scrolling, formulas/plots,
   keyboard use, language, neighbors and actual ZIP downloads as requested. Inspect
   each CI step at the final PR head, including diagnostics with continue-on-error;
   a green workflow alone is insufficient. Sources/downloads supplement the full page.
5. Open a PR and return its link. After an explicitly authorized merge, verify Pages
   deployment before claiming the new public URL works.

Use `work/` for temporary verification. Never commit personal submissions or records.
There is no personal-progress engine. Agent checks verify artifacts; only actual learner work can support
an observation about learning, and no such record is retained by this workflow.

Original project prose uses CC BY 4.0 and original code snippets use MIT.
Keep third-party notices and source citations; see [licensing](../docs/licensing.md).
