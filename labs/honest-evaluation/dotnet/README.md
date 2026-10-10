# C# lab - Honest evaluation

Use SDK 10.0.401, runtime Microsoft.NETCore.App 10.0.12 and net10.0 with SDK/runtime roll-forward disabled. No external NuGet dependencies. Extract the ZIP and run from its `dotnet` directory. Initial SDK/reference-pack installation or restore may need network; after restore the no-restore runs below need none.

```bash
dotnet --version
dotnet restore LessonLab
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
dotnet run --no-restore -c Release --project LessonLab -- --transfer
```

The demo fits thresholds using twenty training tickets, selects among four candidates on ten validation tickets and reports ten test tickets only afterward. Customer groups are disjoint. The selected threshold is 5; its test TP/FP/FN/TN is 2/3/1/4, cost 7 at FP=1/FN=4. The prespecified cutoff-7 baseline has cost 5; do not reselect from test and call that an untouched audit.

Checks exhaust 1554 ordered small datasets, two cost settings and 3108 fits, compare independent confusion tables, and check ties, input and split guards. Experiments deliberately copy future labels into features and expose held-out customers to a memorizer; neither invalid path is a deployable model. Transfer changes ticket weighting to equal-customer weighting.

Everything is synthetic and deterministic. Exact counts do not prove generalization, model calibration, causal savings or production usefulness. No sklearn, ML.NET, SQL Server or Azure integration is executed. The page contains all source/config, proofs, outputs and separate worked answers; use them without running when the pinned SDK is unavailable. Changing feature domains/pins changes the experiment.
