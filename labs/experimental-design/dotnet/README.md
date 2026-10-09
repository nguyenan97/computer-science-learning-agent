# C# lab - Experimental design

Use SDK 10.0.401, runtime Microsoft.NETCore.App 10.0.12, net10.0; disable roll-forward and restore in locked mode. No external NuGet dependencies. Run from `dotnet` after extracting the ZIP.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Demo gives D=-2, synthetic oracle -4 and sharp-null p=54/64. Checks compare 64 assignments with an independent arm scan, exhaust 6561 small potential-outcome tables and check variance, null size, ties and validation. Experiment writes `assignments.csv`: four groups with all 64 masks each, 256 data rows. Outcomes are synthetic values labelled milliseconds, not measured latency. Mask 21 is preselected; the program enumerates an equal-probability mathematical design, not a live allocation system/RNG. No network/database is used.

The lesson includes all code, formulas, trace and a changed-context solution. If the SDK is unavailable, read them and the CSV to check by hand. Changing pins creates a different experiment. The p-value needs the paired design and individual sharp null; it is not the probability the null is true, an average-effect interval or an analysis valid for every rollout. GrowthBook SDK execution, SQL Server integration, missing data and production interference remain untested.
