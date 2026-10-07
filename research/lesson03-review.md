# Lesson 03 authoring and verification review

## Scope and selection

`python scripts/daily_plan.py` selected `algorithms.graphs` for the next lesson
following Lesson 02, with a build-day objective: choose BFS or Dijkstra from edge
assumptions and give a counterexample for a wrong choice. The selected recall is
Lesson 02's lower-bound partition invariant. Publication coverage supports topic
selection; no learner attendance, answers, scores or mastery are inferred.

The complete EN/VI pages teach unit-cost BFS, nonnegative-cost Dijkstra, finalization,
strict relaxation, lazy heap entries, route reconstruction and changed-state modeling.
Eight activity sections follow the study profile, including breaks at their intended
positions. The opening has only core concepts, examples before formulas and no total
budget, update date or schedule table. Familiar English words are retained in context.
Every answer is in a native details element without an open attribute.

## Source review

The following OSRM v5.27.1 files were retrieved and read at commit
`4f3ee609ec1af40eb1f445c6706cfa5beb04c990`:

- `README.md`: route services, the Berlin example, CH/MLD preprocessing and the
  recommendation to use MLD by default, except cases such as large distance matrices.
- `profiles/car.lua`: `routability` is the default weight objective; duration/distance
  are alternatives. The turn handler includes penalties. We do not equate all weights
  with travel seconds.
- `src/engine/routing_algorithms/direct_shortest_path.cpp`: CH query heaps, endpoint
  candidates, search, path unpacking and route extraction.
- `include/engine/routing_algorithms/routing_base_ch.hpp`: minimum heap removal,
  direction checks, positive traversed-edge assertions, strict relaxation, parent
  updates and DecreaseKey. Endpoint offsets and stopping/stalling are explicitly
  outside the lab's reproduced scope.
- `LICENSE.TXT`: BSD-2-Clause terms. No OSRM code is redistributed; the case study
  links to and analyzes it. Lab code is original MIT, with the license in the ZIP.

Boost 1.85 BFS/Dijkstra documentation and Microsoft .NET PriorityQueue Remarks were
also read. Their claims support edge-count distance, the nonnegative prerequisite,
minimum priority and lack of FIFO ties. The lesson derives its lazy-heap complexity
independently rather than copying Boost's stated complexity to another implementation.
The proposed consequences of switching OSRM to BFS are labeled design inference,
not a reported maintainer experiment. No OSRM timing, graph-size measurement or API
reproduction is claimed.

## Content and code review

EN/VI meaning was reviewed for assumptions, proof steps, counterexamples, commands,
output interpretation and all worked answers. The lazy heap uses strict improvement,
checks stale entries before stopping, and reserves long.MaxValue for infinity.
Graph construction validates all edges and copies adjacency data; the query does not
mutate it. BFS rejects non-unit graphs rather than quietly solving a different
objective. The experiment explicitly projects weights and separately evaluates the
returned route under original costs.

The numeric contract rejects any examined candidate at or above the reserved value,
even an irrelevant non-improving candidate. Equal-cost alternatives need not return
the same path. The tuple tie-break does not promise lexicographically smallest routes,
and a node sequence cannot identify a particular parallel edge. Both limitations
are explained. The constrained-route exercise uses expanded state and a synthetic
zero-cost target without changing the original solver.

Review corrected the setup's source-file count to four and extended the pinned
CH function link through its route-return line.

## Checks run

- `python scripts/check_all.py`: passed 48 repository tests, catalog/planner/link/
  navigation/coverage checks, EN/VI structure and code parity, all three labs, extracted
  ZIP checks and builds of every archived project. The new lab build had zero warnings
  and zero errors. All build outputs stayed in temporary or ignored copies.
- New lab `--check`: 7,683 independent oracle/path comparisons, plus deterministic
  edge, numeric and invalid-input checks. Small random graphs include zero weights;
  unit projections also exercise BFS. A disconnected target drains an actual stale
  queue entry, separate from early-return examples.
- Code extracted directly from the page: all four C# source fences match the lab;
  copied project and SDK fences compile. Demo, check and experiment commands passed.
  The transfer snippet returns cost 3 and states `0->4->2->7->8`.
- `--experiment`: all 12 predicted rows observed. For n=64, weighted projection-BFS
  returns one edge costing 128 in the original graph; Dijkstra returns cost 63.
  Direct-cost-zero and adjacency-order variations were also executed and matched
  their worked answers at n=64, 256 and 1024.
- Browser diagnostic in local Chromium: 6 lesson pages, 6 language switches,
  6 previous/next clicks, 147 internal document links and 14 asset links passed;
  no runtime errors or external requests. ZIP links were checked against the staged
  candidate site, not asserted to be published on Pages.
- Additional browser check: all 14 answer panels per language start closed and
  toggle open/closed. The correctness runner renders as a C# code block inside
  its panel. Mobile toggling passed at 390px; the Vietnamese mobile screenshot
  was visually reviewed.
- Typography scan and `git diff --check`: passed. No em/en dashes or initially
  open answer panels in the new lessons, lab guides or catalog text.

No elapsed-time benchmark was run. The experiment measures operation counts only;
these do not establish runtime latency, heap peaks, GC pressure or service p99.
The finite oracle suite supplements the proof but cannot establish correctness for
all graphs. Pages publication is left to the learner's PR merge.
