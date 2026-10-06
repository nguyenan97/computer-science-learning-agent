# Daily lesson spec

This is the single authoring contract for the [Codex skill](../skills/cs-daily-deep-study/SKILL.md).
The catalog supplies publication dates, order, bilingual titles, recall and lab metadata.
The website teaches the learner; this spec governs authoring and remains repository documentation.

## Scope and selection

Choose one measurable objective that follows existing catalog objectives and the relevant
[topic map](topic-map.md). Explain why it matters in a concrete engineering or research
problem. Include supporting outcomes and the minimum foundations needed to follow it.
Use the learner's .NET/data experience for examples without assuming mathematical mastery.

Build toward graduate-level depth through explicit assumptions, derivations or proofs,
counterexamples, controlled experiments and critical reading of research. Introduce
these gradually instead of assigning an unrelated advanced paper to fill a day.
The material supports self-study; it does not award a degree or certify competence.

Reuse the learner's stated time and tools. Without a smaller request, plan a full
research day. Use flexible blocks, each with an estimated range, a concrete output
and a stop condition. Adapt ranges to this objective rather than copying a fixed
total or percentage table. Budget breaks and setup explicitly. A foundation bridge
replaces a depth block; an experiment ends when its question has enough evidence.

| Block | Useful output | Stop condition |
|---|---|---|
| Recall and readiness | Reconstructed prior idea; prerequisite prediction | Compare with answers, identify one foundation to revisit |
| Contract, foundation and worked trace | Annotated trace; model or invariant; counterexample | Explain the mechanism and its assumptions |
| Bounded source investigation | Answers to a few research questions; testable claim | Each question has support or a stated uncertainty |
| Implementation and debugging | Runnable C# or T-SQL artifact; explained edge cases | Correctness checks pass and failures are understood |
| Controlled experiment | Measurements with controls; interpretation and limits | Evidence answers the hypothesis without unbounded benchmarking |
| Transfer and synthesis | Changed-context solution; revised model; open question | Explain when to apply the model and when it fails |

Prefer prediction, reconstruction, tracing, implementation, debugging, claim checking
and changed-context reasoning over long uninterrupted exposition. Source reading can
be the main activity when it produces a defended argument, derivation or comparison.
Offer a reading-only route through worked traces, lab explanations and solutions.
All hands-on tasks are optional; continuing tomorrow requires no submission.

## Recall without learner records

Run `python scripts/review_queue.py --on YYYY-MM-DD` using the requested study date
or the learner's current local date. Start with its selection of at most three
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
- The flexible plan for this particular day, followed by a concrete contract,
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

Write only learner-useful information on the page. Internal IDs, state procedures,
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
   bilingual title, publication date, files, related reading, recall and lab metadata.
2. Run `python scripts/add_lesson_navigation.py`. The catalog generates lesson footers,
   sidebars and homepage lists; neither contract nor workflow maintains lesson order.
3. Run `work/venv/bin/python scripts/check_all.py` after environment setup. Correctness,
   structural parity and public-asset checks are required. Optional browser/benchmark diagnostics belong in verification,
   with observed results reported honestly.
4. Inspect the staged lesson, language switch, catalog links and downloads. Test the
   extracted lab when producing a ZIP. Sources and downloads supplement the full page.
5. Open a PR and return its link. After an explicitly authorized merge, verify Pages
   deployment before claiming the new public URL works.

Use `work/` for temporary verification. Never commit personal submissions or records.
The legacy state engine is maintainer-only and is not initialized or consulted for
daily lessons. Agent checks verify artifacts; only actual learner work can support
an observation about learning, and no such record is retained by this workflow.
