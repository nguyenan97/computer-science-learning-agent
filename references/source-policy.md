<!-- contract-version: 1 -->
# Source policy

This is the single research and repository-evaluation policy. Curriculum establishes scope; primary technical sources establish implementation behavior; academic research establishes theoretical or learning claims; open-source code demonstrates one implementation; instructor synthesis proposes connections. Label all five roles explicitly and never attribute inferred prerequisites to IUH.

## Research for each lesson

Read curriculum first, then research foundational theory and a directly related evolving detail. Prefer systematic reviews/meta-analyses and original academic studies for pedagogical claims; inspect participants, tasks, control conditions, delay, outcomes, uncertainty and moderators before claiming an effect. Prefer official documentation, standards and official implementation/tests for APIs. Old foundational theory may remain useful; newer is not inherently better evidence.

Use the smallest source set that supports the actual objectives (often 3–6, heuristic). For each source log title/author, URL, role, claim/section used, checked date, version/commit when applicable, access status (`read`, `metadata_only`, `unavailable`) and limitations/conflicts. Reading an abstract or a citation is not reading methods. Do not turn inaccessible sources into invented findings or benchmarks. Clearly separate stable theory, verified version-specific behavior, unverified current guidance and instructor judgment.

Check volatile facts at lesson time: tool/dependency versions, support status, cloud limits, security advice, APIs and repo popularity/activity. Pin reproducibility versions separately; an old pinned example is not necessarily the latest or recommended production version. If live access fails, use verified stable material, mark limits, or defer. No hard-coded current year.

## GitHub research protocol

1. Derive a narrow repository query from the objective and stack. Discover highly starred relevant projects and official/specialist alternatives. Shortlist only enough to compare; usually select one, occasionally two. For a nontechnical topic, explain why none is useful.
2. At research time inspect the repository and record exact stars if obtainable, timestamp/date, maintainer identity, archived status, recent default-branch commit and release evidence. GitHub API is preferred when available; HTML is acceptable with field provenance. If unavailable/ambiguous use null plus a reason, never estimate. Star thresholds are discovery heuristics only.
3. Evaluate objective fit, maintainer authority, evidence of usage (users/downstream references; stars alone do not establish adoption), maintenance/release activity, code/test/benchmark quality, docs, license, setup cost and learning complexity. State unknowns instead of inventing a composite score.
4. Select based on pedagogical fit and manageable slice. Explain why a lower-star official/specialist repo can beat a popular tutorial; document the rejected alternative briefly. Verify archived status explicitly when possible; absence of a visible archive banner is weaker evidence.
5. Pin a commit SHA or immutable release with resolved SHA, link exact file/function/test/benchmark/issue/PR targets, and explain each target's task. Require a prediction, trace, defect repair, benchmark experiment or comparison that connects implementation to theory and trade-offs.
6. Record versions/data/commands, expected observations and what you actually ran. Full upstream build is optional; reading a pinned implementation slice and running a local equivalent must be labelled as such. License does not automatically grant permission to redistribute all dependencies or curriculum materials.

No README-only link dump, no stars-as-quality guarantee, no benchmark speed claims without workload/environment, no unchecked generated API claims. Do not force GitHub or the default C#/.NET/T-SQL/TypeScript/Azure stack where a smaller or more appropriate tool teaches the objective better.
