# C# lab - sampling uncertainty

Use SDK **10.0.401**, runtime **10.0.12**, target **net10.0**; roll-forward is disabled. No external NuGet packages; restore checks the lock file. Run from `dotnet` after extracting the ZIP.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

The demo traces prefix 1,0,1,0,0; checks print `PASS: 20300 score inversions; binary-sequence weights; endpoints; seed; validation.` Experiment prints 11 method/size/group comparisons and writes `distribution.csv` in the current directory. Seeds 101/202/303 reproduce synthetic data, not independence or RNG quality. Do not use the generator for security.

No latency measurement or SQL Server/SciPy/R execution. The model uses fixed p, specified units and equal-size/identical-outcome groups where stated. Wilson finite coverage can fall below 95%. Score inversion checks the formula, not production coverage. If execution is unavailable, read the code, tables and chart in the lesson; do not describe reading as your own execution.

Sources: [Stats.cs](LessonLab/Stats.cs), [Draws.cs](LessonLab/Draws.cs), [Checks.cs](LessonLab/Checks.cs), [Experiment.cs](LessonLab/Experiment.cs), [Program.cs](LessonLab/Program.cs), [project](LessonLab/LessonLab.csproj), [lock](LessonLab/packages.lock.json), [SDK](global.json), [MIT](LICENSE-MIT.txt).

[Complete lesson](../../../lessons/2026-10-11-sampling-uncertainty/lesson.md)
