# Review a lesson before publication

This is a maintainer checklist, not a learner scoring system. The
[lesson spec](../references/lesson-spec.md) owns requirements, the
[profile](../references/study-profile.json) owns timeboxes, and the
[scaffold](../references/lesson-template.md) suggests a flexible structure.
Record artifact evidence and unresolved limits; save no learner answers or history.

## Plan and learning argument

- Was the next date obtained from the catalog and planner before catalog edits?
  Does the objective justify its topic IDs rather than inherit them from a title?
- Can the objective be checked using a trace, argument, program, ledger or critique?
  Are prerequisites introduced before use and inherited limits retained?
- Is there a concrete example before the formula? Does the proof identify its
  invariant/base/preservation/conclusion, or another valid argument and its assumptions?
  Does the counterexample attack the actual mistaken rule?
- Does every timed section identify work and a concrete stopping product? Are split
  block minutes and correctly placed breaks accounted for without an opening schedule?
  Could setup, source volume or exercises exceed the timebox? Is there a useful fallback?
- Does transfer change an objective, constraint, unit or failure boundary? Can recall
  reconstruct a mechanism and its assumptions? Are individual prompts immediately
  followed by individual default-closed worked answers?
- Read both languages for meaning, technical terms, limitations and natural sentences.
  Similar headings/fence counts are structural evidence only. Treat harmless style
  differences separately from incorrect or missing explanations.

## Evidence and execution

- Recompute each formula/example/trace/table, including empty, tied and boundary cases.
  Check quantifiers: worst-case, expected, amortized, finite model and observed workload.
- Read the cited source at the full commit SHA, named file/function/range. Does it
  support the exact claim? Identify verified behavior, design inference and unrun
  integration. Link-access success alone is not a semantic source check.
- Run commands from the stated directory under exact pins. Compare complete
  page-derived files with the source lab; inspect the source-only ZIP and run its checks
  after extraction. Run transfer programs separately when they replace an entry point.
  Compare announced output with actual output, allowing only explained variable values.
- Is the oracle independent of the key mechanism? Name shared assumptions/validation
  and finite inputs. Passing tests does not prove all inputs/interleavings.
- For experiments, identify assumption, prediction, changed/fixed variables, observation,
  inference and uncontrolled factors. Mark simulations, model calculations and actual
  timings accurately. Correct exact arithmetic does not certify a real-world model.

Preserve scope: local SQLite is not production/SQL Server evidence; two process-kill
boundaries do not certify power loss; one-database receipts do not certify distributed
exactly-once delivery. Wilson finite coverage, linked observations, paired-design
weighting and sharp-null tests retain their stated models and limitations.

## Browser and release

Use commands in [maintaining](maintaining.md). Check each published EN/VI page
at desktop/mobile widths, each answer initially closed and toggleable, rendered code,
wide tables/scroll containers, formulas and available plots. Test keyboard summaries
and horizontal scrolling, focus visibility, measured text contrast, correct document
language, language switching, neighbors and actual staged ZIP downloads.

Review findings with location, evidence, learner impact and a concrete repair. Classify
correctness, missing foundation/evidence, structure, wording or style separately. Fix
verified issues; defer larger proposals with missing evidence. Rerun checks after
changes and inspect each CI step at the final PR commit, including continue-on-error
diagnostics. An open PR does not update Pages. Claim publication only after an
authorized merge and verified deployment.
