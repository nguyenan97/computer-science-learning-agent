# C# lab - Budget selection with DP and approximation

Use .NET SDK **10.0.401**, pinned in `global.json`, targeting **net10.0**. No third-party package or database is required. Install the SDK from [Microsoft](https://dotnet.microsoft.com/en-us/download/dotnet/10.0) if needed.

Download [the ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/budget-selection/dotnet-lab.zip), extract it and run inside `dotnet`. In a checkout, use `labs/budget-selection/dotnet`.

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

```text
Exact: value=10, cost=6, ids=B,C
Density: value=7, cost=4, ids=A
HalfApprox: value=7, cost=4, ids=A
PASS: 12226 instances checked against exhaustive optimum, feasibility and half guarantee.
```

The first three lines are the demo; the last is `--check`. Checks compare both DP variants with an independent subset oracle, validate returned subsets and the half guarantee, and exercise input/numeric/resource limits. `--experiment` prints 52 CSV data rows from 13 controlled cases with separate operation units and density comparisons. It does not measure elapsed time, SQL query performance or worker latency.

After a successful build, add `--no-restore` for offline use. Without the SDK, use the full code, table and worked answers in [the lesson](../../../lessons/2026-10-08-dp-approximation/lesson.md). In a checkout, `python scripts/check_all.py` prepares the supported environment and checks temporary lab copies.

IDs must be nonempty and unique under ordinal comparison. Costs must be positive integers; values nonnegative; capacity nonnegative. The total value of all jobs, including oversized ones, must fit `long`. Exact and rolling DP have a 2,000,000-cell limit; the oracle accepts at most 22 jobs. A limit failure throws rather than silently substituting an approximation. The half guarantee assumes one budget and independent indivisible jobs with additive values. Ties need not give identical subsets.

Sources:

- [Budget.cs](LessonLab/Budget.cs)
- [Oracle.cs](LessonLab/Oracle.cs)
- [Program.cs](LessonLab/Program.cs)
- [Checks.cs](LessonLab/Checks.cs)
- [Experiment.cs](LessonLab/Experiment.cs)
- [LessonLab.csproj](LessonLab/LessonLab.csproj)
- [global.json](global.json)
- [MIT](LICENSE-MIT.txt)

All code is original MIT teaching code. Prose uses CC BY 4.0. PostgreSQL and the textbook are linked and analyzed in the lesson; their code and PDF are not redistributed.
