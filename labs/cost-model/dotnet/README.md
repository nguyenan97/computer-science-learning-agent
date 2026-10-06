# Lesson 01 lab — C# / .NET

[Tiếng Việt](README.vi.md) · [English lesson](../../../lessons/2026-10-05-cost-model/lesson.md)

The full-day lesson uses this lab for guided C# implementation, debugging and a
CPU/allocation experiment. Complete worked code is in [Core/Deduplication.cs](Core/Deduplication.cs).
Keep your attempts and experiment notes in a private copy; unchanged commands run
reference code and do not demonstrate independent learner work. All practice and
submission remain optional, and the next lesson is available without submitting.
The lesson includes an inline Python comparison and narrated traces for reading
offline; Python set internals are not interchangeable with this C# lab.

## Run the small lab

Install the **.NET SDK**, not only the runtime. Reproducibility pin: SDK **10.0.401**,
runtime **10.0.12**, target **net10.0**. Windows, macOS or Linux with that SDK; no SQL
Server, Docker or Python needed. Checked on Linux; other OS runs not claimed.
The core lab has no third-party packages. Benchmarking additionally restores
BenchmarkDotNet **0.15.8** and transitive NuGet dependencies, requiring network access.

Either clone the repository or download the complete lab:

- [Repository](https://github.com/nguyenan97/computer-science-learning-agent)
- [Lab ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip)

From a clone:

```bash
git clone https://github.com/nguyenan97/computer-science-learning-agent.git
cd computer-science-learning-agent/labs/cost-model/dotnet
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

For an existing clone, run `git pull --ff-only` first from the repository root.
For the ZIP, extract it and open a terminal in its `dotnet` folder (the folder with
`global.json`). Then use the same three `dotnet` commands.

Expected checkpoints:

```text
Stable result: B2, A1, C3
Example scan comparisons: 6
n,scan_equality_comparisons,hash_add_calls (not hash-table work)
128,8128,128
256,32640,256
512,130816,512
128 identical IDs: 127 scan comparisons
Duplicates: B2=2, A1=2
```

The eight checks cover order/input preservation, edge cases, comparer semantics,
null policy, count model, lookup work on one workload, forced collisions and counts.
Passing them verifies reference-code behavior, not learning or durable mastery.
`CountScan` is an explicit operation model, not an instrumented measurement of all
runtime instructions inside `List.Contains`.

## Optional benchmark

From the same `dotnet` folder, in Release without a debugger:

```bash
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

PowerShell and bash both accept these single quotes. The first restore/build and
12 benchmark cases can take several minutes. `--job short` is a learning experiment,
not a production capacity test. For a pipeline smoke check replace `short` with `dry`;
Dry results are not useful speed estimates. After changing code, rerun correctness
checks before benchmarking.

Input creation is in `GlobalSetup`, outside the measured method. Each invocation
creates a fresh output/HashSet; the input is not mutated and returned results are
consumed by the harness. Both paths use ordinal equality and first-occurrence order.
The matrix uses N=128/512/2048 and nominal unique percentages 10/100; actual distinct
count is `max(1, floor(N * UniquePercent / 100))`. IDs have fixed width. Real lengths,
ordering, duplicate frequencies and CPU/cache effects may differ.

Read Mean, Error, Ratio and Allocated together. Allocated includes new output and
table storage per invocation, excluding the prebuilt input. It is **not** peak working
set, surviving heap or an application-wide GC/p99 measurement. Gen0 is collection
frequency normalized by the harness, not allocated bytes.

Reports are in `BenchmarkDotNet.Artifacts/results`. Do not copy one machine's ratio
as a service performance guarantee; save the environment header and input parameters.
Do not benchmark `CountScan` against uninstrumented Hash: counters change the workload.

## Troubleshooting and offline path

| Symptom | Action |
|---|---|
| `dotnet` missing | Install the SDK from [Microsoft](https://dotnet.microsoft.com/download/dotnet/10.0), restart terminal, run `dotnet --list-sdks` |
| SDK from `global.json` not found | Install 10.0.401 or a compatible later patch in the 10.0.4xx feature band; no need to change your production application's target |
| Project not found | Check the working directory contains Core, LessonLab, Benchmarks and global.json |
| NuGet restore fails | Check NuGet/network access; read the lab output and code instead if offline; do not treat an unrun benchmark as measured |
| Benchmark has no valid results | Inspect build errors and environment header; use Release without debugger and a writable working directory |

Without setup, the full lesson's trace, formulas and worked code form the reading-only
path. Benchmark results are optional evidence about execution, never learner assessment.
