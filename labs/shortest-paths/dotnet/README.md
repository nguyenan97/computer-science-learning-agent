# C# lab - BFS and Dijkstra

SDK/runtime roll-forward is disabled: use SDK 10.0.401 and runtime 10.0.12.

Use .NET SDK **10.0.401**, pinned by `global.json`, with **net10.0**. No third-party packages or network service is needed. Install the matching SDK from [Microsoft](https://dotnet.microsoft.com/en-us/download/dotnet/10.0) if necessary.

Download [the ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/shortest-paths/dotnet-lab.zip), extract it and open a terminal inside its `dotnet` directory. From a repository checkout, the working directory is `labs/shortest-paths/dotnet`.

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

The demo contrasts one edge costing 10 with three edges costing 3 in total. Checks compare routes with an independent repeated-relaxation oracle and validate paths, zero cycles, stale entries, errors and numeric limits. The experiment prints CSV operation counts for unit and weighted chains with a shortcut; it does not measure elapsed time or service p99.

After a first successful build, add `--no-restore` to the run command for offline use. If the SDK is unavailable, use the complete implementations, traces and worked answers in [the lesson](../../../lessons/2026-10-07-shortest-paths/lesson.md). In the repository, run `python scripts/check_all.py` from the root to bootstrap the supported environment and check labs in temporary copies.

An invalid node or negative cost is rejected during graph construction. BFS also rejects non-unit costs. `long.MaxValue` is reserved for unreachable; an examined Dijkstra candidate at or above that value throws `OverflowException`. Equal-cost routes need not have the same path; only minimum distance is promised. The node path does not identify which parallel edge was used.

Sources:

- [Graph and solvers](LessonLab/Routes.cs)
- [Demo](LessonLab/Program.cs)
- [Correctness runner](LessonLab/Checks.cs)
- [Experiment](LessonLab/Experiment.cs)
- [Project](LessonLab/LessonLab.csproj) and [SDK pin](global.json)
- [MIT license](LICENSE-MIT.txt)

All lab code is original MIT teaching code, not adapted OSRM source. Lesson prose uses CC BY 4.0. OSRM is only linked and analyzed in the lesson, credited under its BSD-2-Clause license.
