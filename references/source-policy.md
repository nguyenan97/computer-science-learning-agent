# Source Policy

## Goal

Use sources to create a defensible lesson, not to maximize citation count.

## Source Tiers

### Tier A — Project Ground Truth

The user's Master IUH sources define curriculum scope, terminology, course outcomes, and institutional framing.

Use them first when deciding what the program expects.

### Tier B — Primary Technical Authority

Examples:

- Microsoft Learn / .NET documentation
- Azure Architecture Center / Well-Architected Framework
- official product documentation
- standards / RFCs
- official framework design documents
- official source repositories

Use these for current behavior, API semantics, architecture guidance, support status, limits, and recommended patterns.

### Tier C — Rigorous Academic Sources

Prefer:

- textbooks named by the curriculum
- peer-reviewed papers
- MIT OpenCourseWare
- Stanford / CMU / Berkeley / Harvard / Cornell and comparable university material
- authoritative lecture notes / problem sets

Use these for theory, proofs, problem sets, experimental method, and durable mental models.

### Tier D — Production OSS Evidence

Use mature repositories to show how concepts are implemented in real systems.

Evaluate:

1. relevance to the lesson
2. maintainer authority
3. recency of commits / releases
4. quality of tests / benchmarks
5. issue and PR discussion quality
6. real adoption
7. stars / forks / contributors as secondary signals

For community repositories, >= 5k stars is a useful discovery threshold, not a guarantee.

Read the smallest useful slice:

- implementation file
- unit / integration test
- benchmark
- design note
- issue
- merged PR

Do not ask the learner to browse a huge repository without a precise target.

### Tier E — Secondary Sources

Blogs, tutorials, videos, Q&A sites.

Use only when they provide a uniquely clear explanation or practical reproduction that primary sources do not.

Never let Tier E override a current primary source.

## Currentness Rules

External facts that may change must be verified at lesson time:

- .NET / C# / Angular / SQL Server / Azure versions and features
- package APIs
- cloud service behavior / limits
- GitHub stars / activity
- security guidance
- AI model / SDK behavior

Prefer recent sources, but do not discard old foundational theory merely for being old.

## Source Triangulation

For claims with production impact, try to triangulate:

- what the curriculum teaches
- what official docs recommend today
- what real source code / tests show

If they differ, explain why.

## Suggested Search Patterns

- `<concept> site:learn.microsoft.com`
- `<concept> site:github.com/dotnet`
- `<concept> site:ocw.mit.edu problem set`
- `<concept> Stanford course notes`
- `<concept> paper survey`
- `<concept> benchmark GitHub`

## Anti-Patterns

Avoid:

- SEO listicles as primary evidence
- stale Stack Overflow answers for current framework behavior
- star count as the only repository quality metric
- summarizing a paper without reading methodology / evaluation
- presenting benchmark numbers without environment and workload context
- using generated code as evidence that an API exists
