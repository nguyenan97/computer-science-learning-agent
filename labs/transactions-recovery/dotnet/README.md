# C# lab - Transactions and recovery

SDK/runtime roll-forward is disabled: use SDK 10.0.401 and runtime 10.0.12.

Use .NET SDK **10.0.401**, **net10.0**, Microsoft.Data.Sqlite **10.0.9**, SQLitePCLRaw.bundle_e_sqlite3 **3.0.3** and the checked-in lock file. The engine is **SQLite 3.50.4**. First restore needs NuGet access; cached no-restore runs need no database server.

Download [the ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/transactions-recovery/dotnet-lab.zip), extract and run inside `dotnet`; a checkout uses `labs/transactions-recovery/dotnet`.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Demo: blind reads both see ten, both requests commit, remaining=5 and reserved=12. Guarded retry leaves three, reserves seven and rejects the five-unit request. `--check` prints `PASS: 225 serial-oracle schedules; stale snapshot=517; rollback/replay; 2 crash boundaries.` Checks include independent serial admission, held-snapshot upgrade, injected rollback, request identity and payload mismatch.

`--experiment` emits six CSV rows and two recovery comments. It counts outcomes/conflicts/retries, not elapsed time or throughput. Blind intentionally violates the one-item conservation rule. Controlled tasks own separate private-cache connections and use gates, not sleep. WAL has one writer. DefaultTimeout=1 bounds provider waiting; zero would wait without a limit.

Crash cases spawn only this executable as a child, signal before or after commit, then the parent kills that child and reopens. A ten-unit account transfer and 64 artificial blobs force WAL evidence. Before commit: balances 100/100, noise 0. After commit: 90/110, noise 64. WAL size is checked but exact bytes vary. OS and storage stay alive, so these are process-crash cases, not power-loss certification.

All fixtures create/remove only their own generated temporary directory, use WAL/FULL and disable autocheckpoint for this experiment. Stock is 0-1000, quantities 1-1000 and request IDs nonblank up to 100 characters. No restock/cancellation/concurrent reset is modeled; retry has one fresh attempt under the selected two-client order. The internal `--child` mode is for the parent harness, not an application database command.

Sources: [Store.cs](LessonLab/Store.cs), [Schedules.cs](LessonLab/Schedules.cs), [Crash.cs](LessonLab/Crash.cs), [Checks.cs](LessonLab/Checks.cs), [Experiment.cs](LessonLab/Experiment.cs), [Program.cs](LessonLab/Program.cs), [project](LessonLab/LessonLab.csproj), [lock](LessonLab/packages.lock.json), [SDK](global.json), [MIT](LICENSE-MIT.txt).

The [complete lesson](../../../lessons/2026-10-10-transactions-recovery/lesson.md) supplies code, traces, individual answers and a reading-only route when subprocess creation or setup is unavailable. ZIP contains source/setup, not SDK/package binaries or a database. Original C# is MIT; prose CC BY 4.0; third-party dependencies retain their own terms. SQLite source is cited at a pinned commit, not copied.
