# Learning science for practical daily deep study

Checked **2026-10-06**. Scope: self-directed Computer Science, programming and technical experimentation, with uncertain prerequisites and optional submissions. This is a focused evidence review with explicit access limits, **not a systematic review or an evaluation of this tutor's educational effectiveness**. No new experiments or numerical effect estimates are claimed.

## What was checked

Searches targeted retrieval, spacing, interleaving, examples, deliberate practice, feedback and cognitive load. Candidate sources came from academic publishers, author/university repositories, PubMed and an evidence-informed practice guide. Selected relevant sections were examined to connect claims to activities. There was no preregistered search, exhaustive screening, independent risk-of-bias assessment or reanalysis. Older foundational evidence is useful but does not settle every modern programming task.

The [machine-readable log](deep-study-source-checks.json) records URLs, timestamps, HTTP status, bytes, hashes, inspection scope and limitations. Six sources had accessible full text and **selected sections read**; three had **abstracts only read**; one candidate publisher source was unavailable. Download success is not equivalent to a full-paper review. The [earlier log](source-checks.json) remains historical; earlier proxy refusals do not describe today's successful access.

| Source and access | Examined material | Remaining boundary |
|---|---|---|
| [Dunlosky et al. (2013)](https://iverson.cm.utexas.edu/courses/310M/Handouts/Dunlosky%20et%20al.%20-%202013%20-%20Improving%20Students%E2%80%99%20Learning%20With%20Effective%20Learni.pdf), university-hosted publisher PDF, HTTP 200 | Summary, retrieval implementation/assessment, spacing discussion, interleaving cautions, utility table | Selected sections; underlying experiments were not independently audited |
| [Cepeda et al. (2006)](https://escholarship.org/content/qt3rr6q10c/qt3rr6q10c_noSplash_2440ea21aa88b3b0722b0afa9171f88b.pdf), academic repository, HTTP 200 | Abstract, introduction, search/methods and interval coding | Author manuscript may differ from final publication; verbal-recall evidence |
| [Shute (2008)](https://myweb.fsu.edu/vshute/pdf/shute%202008_b.pdf), author-hosted PDF, HTTP 200 | Abstract, introduction/method, feedback guidelines and timing | Selected sections of a heterogeneous research review |
| [Ericsson, Krampe & Tesch-Römer (1993)](https://blogs.ischool.berkeley.edu/i225s14/files/2014/04/Ericsson-1993-article.pdf), university-hosted PDF, HTTP 200 | Practice definition, feedback/resource requirements, music-cohort design | Expertise/music context; not a programming training trial |
| [Sweller, van Merriënboer & Paas (2019)](https://link.springer.com/article/10.1007/s10648-019-09465-5), publisher full text, HTTP 200 | Worked examples, split attention, expertise reversal and fading | Framework/research review; selected sections, not universal prescriptions |
| [Pashler et al. (2007), IES/WWC guide](https://ies.ed.gov/ncee/WWC/Docs/PracticeGuide/20072004.pdf), HTTP 200 | Evidence table, scope and spacing/examples/quizzing/explanations guidance | Primary intended scope grades 3–12; college relevance discussed; agent tutoring untested |
| [Rowland (2014)](https://pubmed.ncbi.nlm.nih.gov/25150680/), PubMed HTTP 200 | Meta-analysis abstract and bibliographic record | Full methods/moderators not examined |
| [Brunmair & Richter (2019)](https://pubmed.ncbi.nlm.nih.gov/31556629/), PubMed HTTP 200 | Interleaving meta-analysis abstract | Full methods not examined; web reader failed, executor access succeeded |
| [Macnamara, Hambrick & Oswald (2014)](https://pubmed.ncbi.nlm.nih.gov/24986855/), PubMed HTTP 200 | Abstract and notice of 2018 corrigendum | Correction contents/full methods unreviewed; quantitative claims withheld |
| [Atkinson et al. (2000)](https://journals.sagepub.com/doi/10.3102/00346543070002181), publisher HTTP 403 | Search metadata only | Not counted as examined full-text evidence; examples policy uses accessible sources above |

The browser service timed out on the Dunlosky publisher page and returned 429/fetch failures for some metadata pages. Executor HTTPS requests through the inherited proxy subsequently retrieved academic copies/abstracts. These separate outcomes are logged; no access restriction was bypassed.

## Findings versus instructional choices

The research supports some general principles, with task/population limits. The rightmost column below is **our inference for lesson design**, not an intervention tested by those papers.

| Method | Supported principle and boundary | Concrete technical activity |
|---|---|---|
| Retrieval | Dunlosky's review and Rowland's abstract support retrieval rather than relying solely on restudy; learning/transfer remain task dependent | Reconstruct an invariant or predict output without notes, then inspect the answer and repair the model |
| Spacing | Cepeda's synthesis links useful study gaps to the intended retention horizon; it does not establish universal offsets | Revisit a trace on a later date, record actual delay/hints and adapt the next prompt to observed difficulty |
| Interleaving | Brunmair's abstract reports material-dependent results; indiscriminate mixing is unjustified | After initial learning, contrast related strategies and justify selection before implementation |
| Worked examples | Sweller's review describes novice benefit, integration requirements and expertise-dependent fading | Narrated trace → completion task → fresh independent variation, with explanations beside the relevant code |
| Purposeful/deliberate practice | Ericsson defines targeted monitored improvement; Macnamara's abstract cautions against a practice-only explanation of expertise | Isolate an observed bug pattern, create a minimal counterexample, correct it and try a new case; do not count routine coding as proof |
| Feedback | Shute recommends specific task-related correction with context-dependent timing | Compare the actual response to a criterion, explain a mismatch, offer a usable correction and invite a fresh case |
| Cognitive load | Sweller describes constraints related to interacting elements and expertise; reported effort is not a direct capacity measure | Reduce irrelevant setup, integrate diagrams/code and explanations, then fade redundant scaffolding |

The IES guide independently connects spacing, worked solutions/problem solving, retrieval and explanatory questions to instructional recommendations, with different evidence levels. Those recommendations neither certify all techniques equally nor validate a seven-hour daily tutor schedule. Self-explanation is included to inspect reasoning; a fluent but wrong explanation still needs correction. Transfer is tested explicitly rather than inferred from identical test cases.

## Project decisions, not scientific optima

The requested full-time day is a **6–8-hour elapsed design**, default **420 minutes = 360 learning + 60 breaks**, with **235 active minutes (65.3% of learning time)**. At least 60% of learning time is active technical work. These values reflect the project's practical emphasis and a reversible workload choice. The review does not identify an optimal daily dose, break pattern or percentage. A full day includes mixed activities and rest; it is not a claim that seven hours of continuous deliberate practice is suitable.

The [template](../references/lesson-template.md) defines the exact schedule: orient/retrieve 20; model/worked trace 50; break 10; source research 45; implementation trace 45; lunch 30; lab/debug 75; break 10; controlled experiment 45; break 10; changed-context task 35; synthesis 45. Passive reading, watching, setup and breaks do not count as active practice. A self-check bridge replaces depth work, setup has a bounded fallback and secondary questions are deferred. Shorter explicit budgets override the default.

Each day has one main objective and a small set of supporting outcomes, bounded research questions, reproducible artifacts and observable checkpoints. Research produces a claim ledger; experiments record hypothesis, variable, controls, seed/cases, result and limits. Benchmark findings are specific to workload/environment. They are not universal implementation rankings.

Provide a full EN and VI version with identical objectives, code, sources, commands, experiments and worked answers. The reading-only path and all solutions are accessible immediately; no submission is required for tomorrow's lesson. The practical ratio describes the **offered full-day path**, not a requirement imposed on a learner choosing the reading path.

## Knowledge and evidence contract

Keep self-reported background, actual observed evidence, unknown/unverified knowledge and observed misconceptions distinct. A programming career can guide examples but is not an assessment of algorithms or mathematics. Agent tests verify artifacts, never learner proficiency. Reading/answer viewing does not generate mastery or completion.

Completion is separate from proficiency: schema v3 requires a qualifying lifecycle-valid assessment on the same topic. The tutor additionally checks **objective → task → rubric → evidence** alignment, which topic equality cannot establish. Assistance is recorded; a solution already shown requires a fresh unseen variation for any later independent assessment. Completion can coexist with needs_support. Repair links need relevant fresh independent non-exit evidence; original errors remain available.

Same-day independent performance is provisional. Delayed unaided recall and meaningful changed-context transfer strengthen confidence only within their scope. One later calendar date is a minimal observable delay, not proof of lasting mastery. Review dates and difficulty choices are heuristics based on observed results and retention goals, not fixed universal schedules.

## How to evaluate the design

Over weeks, compare delayed accuracy, explanation quality, hint dependence, repeated misconceptions and changed-context performance, recording task difficulty and actual delays. Track setup time, workload and self-reported fatigue separately. Do not label uncontrolled before/after improvement causal: familiarity, workload and topic difficulty can explain trends.

Repository tests verify state/linkage/privacy and reproducibility; bilingual review checks content parity; skill scenarios specify desired behavior. Neither technical tests nor unexecuted scenario files establish that the model follows the skill or that learners improve. A stronger educational claim would require actual learner outcomes and a suitable comparison design.

Implemented contracts: [pedagogy](../references/pedagogy.md), [workflow](../references/learning-workflow.md), [source policy](../references/source-policy.md), [template](../references/lesson-template.md), [agent skill](../skills/cs-daily-deep-study/SKILL.md) and [full-day example](../lessons/2026-10-05-cost-model/lesson.md).
