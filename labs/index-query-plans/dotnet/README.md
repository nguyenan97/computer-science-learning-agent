# C# lab - Indexes and query plans

SDK/runtime roll-forward is disabled: use SDK 10.0.401 and runtime 10.0.12.

Use .NET SDK **10.0.401**, target **net10.0**, Microsoft.Data.Sqlite **10.0.9** and SQLitePCLRaw.bundle_e_sqlite3 **3.0.3**. The bundled engine reports **SQLite 3.50.4**. Project and lock file pin dependencies; the first restore needs NuGet access. No database server is required.

Download [the ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/index-query-plans/dotnet-lab.zip), extract it and run inside `dotnet`. In a checkout use `labs/index-query-plans/dotnet`.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

The demo prints count 18, amount 198 in all layouts: no secondary index gives SCAN, thin gives SEARCH USING INDEX, and covering gives SEARCH USING COVERING INDEX. Plan text is a version-specific diagnostic, not a stable application API.

`--check` prints `PASS: 11416 aggregate comparisons; index maintenance, plans and rollback checked.` It compares all four access paths with an independent C# predicate scan, tests window boundaries, updates/deletes/inserts and atomic rollback after a batch conflict. `--experiment` prints 12 CSV data rows plus metadata/plan comments: nine read comparisons and three insert configurations. It reports repeated median/min/max timings and logical allocated database bytes. Timings vary; warm-cache local results do not establish SQL Server performance or production p99.

Each instance creates and removes only its own generated temporary directory. It uses one connection, page_size 4096, DELETE journaling and FULL synchronous setting. IDs are unique 1-50000, tenants positive, time a signed long integer and Amount 0-1000. Those bounds keep sums safe. Empty windows are valid; reversed endpoints fail. Rows at long.MaxValue cannot be included by a greater representable half-open endpoint.

After restore, the no-restore commands can use cached packages offline. ZIP contains source and setup only, without SDK, package binaries or a database. If setup is unavailable, use the complete code/plans/answers in [the lesson](../../../lessons/2026-10-09-index-query-plans/lesson.md). In a checkout, `python scripts/check_all.py` checks temporary copies and extracted ZIPs.

Sources:

- [Database.cs](LessonLab/Database.cs)
- [Program.cs](LessonLab/Program.cs)
- [Checks.cs](LessonLab/Checks.cs)
- [Experiment.cs](LessonLab/Experiment.cs)
- [LessonLab.csproj](LessonLab/LessonLab.csproj)
- [packages.lock.json](LessonLab/packages.lock.json)
- [global.json](global.json)
- [MIT](LICENSE-MIT.txt)

Original lab code is MIT; lesson prose is CC BY 4.0. SQLite source is analyzed at a pinned commit, not copied. Third-party packages keep their own license terms.
