# Archived v3 state tools

The daily lesson loop uses the public catalog and saves no learner answers,
progress or completion records. Reading and requesting lessons requires no state
initialization. This page contains no learner records or counters.

`scripts/learning_state.py` is retained as an optional archived maintainer tool.
Only [schema v3](learning-state.schema.json) is supported; v1/v2 conversion has been
removed. The [empty example](learning-state.example.json) is a synthetic template,
not learner progress. The current authoring workflow is in the
[lesson spec](../references/lesson-spec.md).

If a maintainer independently uses the archived tool, real state stays in
`.learning-private/learning-state.json` or an external private workspace. Do not
commit learner state or submitted work to this public repository.
