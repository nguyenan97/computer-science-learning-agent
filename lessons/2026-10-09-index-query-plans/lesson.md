# Lesson 05 - Indexes and query plans: when a seek still does much work

[Tiếng Việt](../../vi/lessons/2026-10-09-index-query-plans/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/index-query-plans/dotnet-lab.zip)

An ASP.NET reporting endpoint totals one tenant's events in a time window. The same endpoint can match 18 rows or 18,000 rows. Adding an index changes how rows are reached; it does not make the rows or their values disappear. We will read real SQLite plans and compare equivalent queries, including the cost of maintaining indexes when writing.

**Goal:** explain bounded index access, full scans, composite key order, table lookups and covering indexes. Connect the plan to selectivity, storage and measured read/write work. The roadmap selects storage and indexes after boundary search; Lesson 04's state and cost distinctions remain useful. Arrays, loops, comparisons and half-open windows are prerequisites. Database pages, B-trees, row locators, SQL aggregates and plan interpretation are introduced here.

## Core ideas

- **Pages and an ordered tree.** A database stores chunks called pages; a B-tree routes a key search through a few page levels rather than comparing every row. Many entries fit in one page, so one comparison is not one disk read.
- **Composite index.** Order by one field, break ties by the next, and retain a row locator. In `(Tenant,Occurred)`, tenant 1's times are together; time 5 across all tenants is not necessarily one consecutive interval.
- **Seek and scan.** A seek locates a starting key; the query may then scan many entries. Finding the first of 18,000 matches is only the beginning of the work.
- **Coverage.** An index covers a query when it contains every value that query needs. Adding `Amount` can avoid fetching each matching row from the table; `Payload` is still absent.
- **Selectivity.** Of 20,000 rows, 18 matches is 0.09%, while 18,000 is 90%. We use this matching fraction, r/N, as selectivity. A smaller fraction often makes bounded access attractive, but coverage, ordering and page layout also matter.

You may follow the worked tables, plans and complete code without running the lab. Limit setup to 15 minutes of the lab block, then continue reading if needed. No submission or saved learner record is required.

## 1. Recall and prerequisite bridge

**Recall · 20 minutes.** Reconstruct the two planner-selected mechanisms, then connect an array boundary to a database query. **Done when:** you can state what information each representation retains.

1. From Lesson 04: what does F(i,c) retain in 0/1 selection?

<details>
<summary>Answer</summary>

It is the greatest additive value using the first i jobs at cost at most c. The prefix records which jobs are available; both skip and take read the previous prefix, preventing repetition. Likewise, an index key must retain the fields needed to locate rows and meet later requirements. A scalar estimated cost cannot replace those fields.

</details>

2. From Lesson 02: for `[2,2,4,7,7]`, how many events lie in `[2,7)`, and why are two lower bounds sufficient?

<details>
<summary>Answer</summary>

Three: lower_bound(2)=0 and lower_bound(7)=3, so 3-0=3. Both 2s are included, both 7s excluded. Array positions give ranks, so their difference counts elements. A B-tree cursor does not provide the same fixed array rank; a filtered SQL aggregate generally still visits matching entries.

</details>

3. Does `SELECT COUNT(*), SUM(Amount)` return one event row or one aggregate row? Can one returned row mean one examined row?

<details>
<summary>Answer</summary>

Without GROUP BY it returns one aggregate row, even for no matches: COUNT is 0 and SUM is NULL; COALESCE changes that NULL to 0 in the lab. This says nothing about rows examined. The sum may read thousands of Amount values. We use r for matching input rows, not the number of output rows.

</details>

## 2. Storage, key order and a correct range

**Foundation · 50 minutes.** Trace a composite-key interval and explain which values must be read. **Done when:** you can justify the stopping boundary and reject “an index makes this aggregate O(log N)”.

### Concrete rows before formulas

Think of `Occurred` as integer minutes from a simulated origin, not a formatted date string. `Id` uniquely identifies an event; tenant is a customer group. A row has `Amount` and a 96-character payload. These are synthetic data, without real customer records.

| Id | Tenant | Occurred | Amount |
|---|---|---|---|
| 1 | 2 | 0 | 1 |
| 2 | 1 | 0 | 2 |
| 3 | 1 | 1 | 3 |
| 4 | 1 | 1 | 4 |
| 5 | 1 | 2 | 5 |
| 6 | 1 | 2 | 6 |
| 7 | 1 | 3 | 7 |
| 8 | 1 | 3 | 8 |

For an ordinary SQLite rowid table, `Id INTEGER PRIMARY KEY` aliases the rowid. A secondary `(Tenant,Occurred)` index retains that rowid, giving effective tie order `(Tenant,Occurred,Id)`. This is specific to this schema; WITHOUT ROWID tables and SQL Server row locators have different rules. Columns sort lexicographically: compare Tenant, then Occurred, then the rowid tie-break.

The reporting predicate is `Tenant=1 AND Occurred>=1 AND Occurred<3`. Its thin-index order is `(1,0,2), (1,1,3), (1,1,4), (1,2,5), (1,2,6), (1,3,7), (1,3,8), (2,0,1)`.

Trace the first matching key, the stop key, the selected IDs and both totals. What breaks if the end comparison becomes `<=3`?

<details>
<summary>Answer</summary>

| Step | Key | Action | Count | Amount sum |
|---|---|---|---|---|
| Seek | (1,1,3) | Include first match | 1 | 3 |
| Next | (1,1,4) | Include duplicate minute | 2 | 7 |
| Next | (1,2,5) | Include | 3 | 12 |
| Next | (1,2,6) | Include | 4 | 18 |
| Boundary | (1,3,7) | Stop before upper endpoint | 4 | 18 |

Return IDs 3,4,5,6 and totals (4,18). `<=3` wrongly includes IDs 7,8, yielding (6,33). Adjacent half-open windows would then count the boundary twice. Seeking to the first key at least `(1,1)` includes all duplicates at the start, rather than choosing an arbitrary equal key.

</details>

### Why the interval is complete

Fixing Tenant makes one contiguous prefix group. Inside that group, times are nondecreasing. A lower-bound seek skips exactly the earlier times; advancing visits every subsequent entry in key order. Until the first time at least end, all visited times satisfy the interval. Afterwards none can re-enter it, because times cannot decrease. Stop also at a different tenant. This proves inclusion and exclusion without assuming unique times. In the lab, SQL is responsible for implementing the predicate; the independent C# scan checks the result.

A composite index does not sort by every column independently. With `(Occurred,Tenant)`, one time range includes multiple tenant groups interleaved by time. With `(Tenant,Occurred,Amount)`, Amount breaks same-time ties before Id; that can affect `ORDER BY Occurred,Id`. Index order never replaces an explicit SQL ORDER BY requirement.

### Pages and work

SQLite's table B-tree stores rows under rowid; a secondary index is a separate B-tree of keys and rowids. Interior pages guide the search, and a cursor advances in sorted order. SQLite index entries can occur in interior and leaf pages: do not assume it is exactly SQL Server's leaf-only B+ tree arrangement. The small trace abstracts those implementation details. SQL Server's disk-based rowstore indexes use B+ trees, as its official design guide explains.

A balanced B-tree keeps leaves at the same depth; separator keys route searches to child key intervals. A hypothetical small-capacity index for our eight keys could look like this:

| Page | Stored keys | Role |
|---|---|---|
| Root | (1,2,5) | Separate earlier and later keys; this is also an index entry |
| Left child | (1,0,2), (1,1,3), (1,1,4) | Keys before the root entry |
| Right child | (1,2,6), (1,3,7), (1,3,8), (2,0,1) | Keys after the root entry |

Seeking time 1 under tenant 1 routes left. Ordered traversal then includes the root entry and continues right; index iteration is not merely following leaves. This is a teaching layout, not an inspected file: eight real entries can fit in a single page. With many children per page, adding a tree level can accommodate many more entries, which motivates the logarithmic height model.

A thin index lacks Amount, so matching rowids lead to table records. A covering `(Tenant,Occurred,Amount)` index can read Amount without that second tree access. This is coverage for this aggregate, not for every endpoint or for Payload.

Use N for table rows, r for matches and B for typical page branching factor. Under bounded keys and a reasonably populated balanced tree, locating the range takes about O(log_B N) page levels; scanning r entries then costs work proportional to r plus page traversal. A covering aggregate has a simplified comparison/entry-work bound O(log N+r); separate table lookups can give O(log N+r log N) under a per-row tree-search model. Cache reuse and page locality can make physical reads much smaller than those counts. These are models, not predictions of milliseconds or exact I/O.

Unlike Lesson 04's pseudopolynomial capacity C, these bounds use a count N of stored entries, with fixed integer keys. Building and maintaining the tree is extra work. Inserting into an existing tree typically routes a key and may split pages; adding wider keys or more indexes adds storage and maintenance. The SQL wrapper, transaction and flush costs are also outside a simple comparison bound.


Why cannot an ordinary index alone make this SUM query O(log N) for arbitrary Amount values?

<details>
<summary>Answer</summary>

Without a stored aggregate summary, changing an unread matching Amount can change the answer while leaving key boundaries unchanged. A correct exact sum must account for every matching value, giving an Ω(r) value-inspection requirement in this model. Returning one aggregate row does not remove it. Prefix sums, materialized summaries or augmented trees change the representation and its update obligations; they are not implemented here.

</details>

Pause - 10 minutes away from the screen.

## 3. Read plans and source claims

**Source reading · 45 minutes.** Read the bounded official sections and annotate one plan per access method. **Done when:** each interpretation names a claim, its evidence and a limit.

Read SQLite's [EXPLAIN QUERY PLAN, section 1.1](https://www.sqlite.org/eqp.html#table_and_index_scans), [Query Planning, sections 1.4, 1.6 and 1.7](https://www.sqlite.org/queryplanner.html) and [optimizer overview, section 2](https://www.sqlite.org/optoverview.html#where_clause_analysis). The first defines plan labels, the second explains rowid lookup, composite order and coverage, and the third limits usable key prefixes and range terms. These are bounded reading assignments, not a requirement to read every optimization.

### Three equivalent queries, different access

Our predicate values are SQL parameters; tenant and endpoints never become interpolated SQL. `SUM` returns NULL for an empty match, so `COALESCE` gives the lab's (0,0) result. The aggregate SQL is the same under all access methods. Only an enum-selected access directive changes.

```sql
SELECT COUNT(*),COALESCE(SUM(Amount),0) FROM Events
WHERE Tenant=$tenant AND Occurred >= $start AND Occurred < $end;

CREATE INDEX ix_thin ON Events(Tenant,Occurred);
CREATE INDEX ix_cover ON Events(Tenant,Occurred,Amount);
```

With 2,000 generated rows, tenant 1 and `[0,10)`, the demo returns count 18, amount 198 in all three layouts. The actual SQLite 3.50.4 demo plans are:

| Layout | Plan detail | Meaning |
|---|---|---|
| No secondary index | `SCAN Events` | Visit table rows and evaluate the predicate |
| Thin | `SEARCH Events USING INDEX ix_thin (Tenant=? AND Occurred>? AND Occurred<?)` | Restrict by tenant/time, then fetch Amount from table |
| Covering | `SEARCH Events USING COVERING INDEX ix_cover (Tenant=? AND Occurred>? AND Occurred<?)` | Restrict by tenant/time and read Amount from index |

The detail string summarizes both lower and upper range constraints; its `>` notation does not change our SQL `>=` semantics. Tests check the returned boundary results. It is a high-level plan description, not a counter of rows, I/O or elapsed time. SQLite documents that this text may change between versions; production applications should not parse it as a stable API. The lab's label checks are deliberately version-specific diagnostics.

Without a forcing directive, the planner selects a plan from available candidates using estimates and statistics. `ANALYZE` supplies statistics, not future certainty. In the experiment, `NOT INDEXED` and `INDEXED BY` deliberately hold the strategy fixed. SQLite's [INDEXED BY documentation](https://www.sqlite.org/lang_indexedby.html) specifies a requirement, not an advisory hint; a missing or unusable named index can fail preparation. We use it for a controlled comparison, not as a production tuning recommendation.

Can `SCAN` use an index, and does `SEARCH` mean the query is cheap?

<details>
<summary>Answer</summary>

Yes. SCAN can describe traversing an entire index rather than the table; a narrower covering index can make that useful. SEARCH means bounded access, but its interval can still contain 90% of the table. Read which constraints delimit the search and whether extra table lookups occur. Neither label proves a runtime ranking.

</details>

Write three claim/evidence/limit rows for bounded access, coverage and composite prefixes. Does a missing leading equality mean no index can ever be used?

<details>
<summary>Answer</summary>

| Claim | Evidence | Limit |
|---|---|---|
| Seek locates an interval, then entries are visited | Query Planning 1.4 and the demo's range terms | Aggregate input work remains; plan text is not measured I/O |
| Coverage avoids base-row value retrieval | Query Planning 1.7 and the covering demo | Only columns needed by this query are covered; wider indexes cost more storage |
| Leading equality followed by a range yields a simple contiguous slice | Optimizer overview 2 | Skip-scan and other strategies are exceptions to simplistic “leftmost or impossible” rules |

For `(Tenant,Occurred)`, a query on time alone lacks one simple tenant-prefix interval. SQLite may scan an index or use skip-scan when statistics and duplicate leading keys make it attractive. Do not turn a useful design rule into a claim that index use is impossible. Likewise, columns to the right of a range usually cannot further narrow this basic slice; they can still supply coverage or filtering.

</details>

## 4. Project application and pinned SQLite implementation

**Implementation reading · 45 minutes.** Follow the range-search and cost slices below, then map their decisions to a reporting endpoint. **Done when:** you separate the verified mechanism from a production recommendation that still needs measurement.

### Application: tenant reports in .NET and SQL Server

An ASP.NET service accepts a tenant and `[start,end)` timestamps, computes count/amount totals, and returns them to Angular. Bind parameters and validate the interval. SQL Server rowstore may use a nonclustered index whose leading key is tenant, then time, with Amount included to cover the aggregate. Choose timestamp units, timezone conversion and value types explicitly; the lab's integer minutes are only a simulation.

A covering candidate in SQL Server can be `(TenantId,OccurredUtc) INCLUDE(Amount)`. INCLUDE stores a nonkey value without making it a sort tie-breaker; SQLite's `ix_cover` puts Amount in the key itself. Those layouts share a coverage goal but differ in ordering and storage. Never copy SQLite page counts, cost constants or forcing syntax into SQL Server claims. Its [index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17) explains B+ trees, row locators, included columns and read/write trade-offs.

Return exactly the same business answer before comparing performance. Measure representative tenant sizes, time windows, projected columns and insert/update rates. A broad noncovering lookup can lose to scan; a covering plan can change that choice. Avoid adding Payload merely to make every query covering: wide indexes increase storage and writes. Correctness, performance and access authorization are separate responsibilities; this lab uses synthetic tenants and does not implement an API's authorization.

### A database uses the idea to execute queries

SQLite source at tag `version-3.50.4`, immutable GitHub commit **`8ed5e7365e6f12f427910188bbf6b254daad2ef6`**, is the case study. SQLite is the actual database in the C# lab, not just a container for a hand-written search.

1. [`sqlite3BtreeIndexMoveto`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/btree.c#L6044-L6195) compares key cells inside a page, updates search bounds, and descends through a chosen child when needed. This connects binary search inside pages to a multi-page tree. The bounded slice is not a full proof of all cursor edge cases.
2. [`sqlite3BtreeNext`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/btree.c#L6317-L6337) advances the current cell and delegates page-boundary handling to `btreeNext`. A seek is followed by traversal; it does not answer the aggregate by itself.
3. [Cost construction in `whereLoopAddBtreeIndex`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/where.c#L3440-L3480) explicitly estimates finding the first entry, visiting additional entries and, without coverage, finding corresponding table rows. Key/table row-size estimates also enter the model. These are estimates in SQLite's logarithmic cost representation, not measured milliseconds or a universal crossover percentage.
4. [`OP_DeferredSeek`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/vdbe.c#L6587-L6665) connects an index rowid to a table cursor and can defer the actual table seek until a value is read. This explains why “one lookup per candidate” is a useful model but not a claim of one physical I/O per candidate.

**Verified in source:** page-key search, subsequent cursor traversal, a coverage-sensitive cost term and deferred table access. **Design inference:** losing coverage as the projection changes can increase work and alter a plan choice. We do not attribute our measured timings to maintainers or claim their optimizer always chooses the fastest plan. Source reading is bounded to these functions; it does not reproduce the entire optimizer, cache or pager.

Which part of the pinned cost slice represents the extra work of a noncovering index? Does it promise one disk read for every matching row?

<details>
<summary>Answer</summary>

The source sets rRun from the index-search/traversal estimate, then adds a term based on nOut when flags do not establish index-only/IPK/expression-index access. This models matching table-row searches. DeferredSeek and cached pages explain why that is not a literal disk-read count. Inspecting a cost formula verifies the model structure, not its accuracy on a new workload.

</details>

Lunch and rest - 30 minutes.

## 5. C# lab: real plans and independent result checks

**Lab · 75 minutes.** Create a temporary database, run all access methods and check index maintenance after mutations. **Done when:** correctness checks pass and you can explain a performance defect that leaves results correct.

Implement the reporting query, inspect its plan without forcing, then compare forced scan/thin/covering paths against an independent C# predicate scan. Keep `[start,end)`, tenant isolation and identical count/amount results. Use the complete answer below if setup or implementation exceeds its timebox.

<details>
<summary>Answer - complete runnable lab</summary>

Use **.NET SDK 10.0.401**, **net10.0**, **Microsoft.Data.Sqlite 10.0.9** and **SQLitePCLRaw.bundle_e_sqlite3 3.0.3**. The bundled engine reports **SQLite 3.50.4**, matching the source case study. `packages.lock.json` pins transitive versions and hashes. These are source downloads; the ZIP does not bundle .NET, NuGet binaries or a database.

Extract the ZIP and work inside `dotnet`; in a checkout, use `labs/index-query-plans/dotnet`. The first restore requires network access to NuGet. With dependencies cached, the no-restore runs need no database server or network service. If you rebuild from the page, create the files below with the same paths. The [lab guide](../../labs/index-query-plans/dotnet/README.md) also links individual files.

`dotnet/global.json`:

```json
{
  "sdk": { "version": "10.0.401", "rollForward": "latestPatch" }
}
```

`dotnet/LessonLab/LessonLab.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.Data.Sqlite" Version="10.0.9" />
    <PackageReference Include="SQLitePCLRaw.bundle_e_sqlite3" Version="3.0.3" />
  </ItemGroup>
</Project>
```

`dotnet/LessonLab/packages.lock.json`:

```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {
      "Microsoft.Data.Sqlite": {
        "type": "Direct",
        "requested": "[10.0.9, )",
        "resolved": "10.0.9",
        "contentHash": "/eBwiZPcNisn0qZX+Zk4YCftlK/vnoWqv7hHnmSk8MjPxFdYYkmPObpogT0MfCCWN6oAIZnMCo0SoOtZlbbmgQ==",
        "dependencies": {
          "Microsoft.Data.Sqlite.Core": "10.0.9",
          "SQLitePCLRaw.bundle_e_sqlite3": "2.1.11",
          "SQLitePCLRaw.core": "2.1.11"
        }
      },
      "SQLitePCLRaw.bundle_e_sqlite3": {
        "type": "Direct",
        "requested": "[3.0.3, )",
        "resolved": "3.0.3",
        "contentHash": "Zt8jmSL5zcDWGk8rmzhWBJ6IRyLWh1yWS04Pg72+GIvo3Ba4E/rG4Y/4l7AWlSEogEbzyKRTCXUAs1v/O7Pkkg==",
        "dependencies": {
          "SQLitePCLRaw.config.e_sqlite3": "3.0.3",
          "SourceGear.sqlite3": "3.50.4.5"
        }
      },
      "Microsoft.Data.Sqlite.Core": {
        "type": "Transitive",
        "resolved": "10.0.9",
        "contentHash": "iZrONyMKPjxfVZnUktqO30QjzNwAGH+AxM61s8lKQnVhgbQ3bn0hiXI129ZmVicEbIcwljyy2OVsIYUR51ZHKQ==",
        "dependencies": {
          "SQLitePCLRaw.core": "2.1.11"
        }
      },
      "SourceGear.sqlite3": {
        "type": "Transitive",
        "resolved": "3.50.4.5",
        "contentHash": "UtnipXhJYZKQOQIfpws/msLK7IRhMplE1CZCaZLIQXRnGD474QVpO/J9nMlQQY8NZueGz1aidjoxDRnrC1NT3Q=="
      },
      "SQLitePCLRaw.config.e_sqlite3": {
        "type": "Transitive",
        "resolved": "3.0.3",
        "contentHash": "caP/ap0X2fyVmstCXu5ueOmcr2XWAxA2XyKghV7H4bOAFmq3nWcsGl9q44iY1HYG+i8Qr4G9XEqdfti0rV6/ZQ==",
        "dependencies": {
          "SQLitePCLRaw.provider.e_sqlite3": "3.0.3"
        }
      },
      "SQLitePCLRaw.core": {
        "type": "Transitive",
        "resolved": "3.0.3",
        "contentHash": "bjm6FY4lZyP+t7GmiuvSM0QXpFihAvyE0Y9O2yibm3g95AAWJPNnHOKVNJGyPTGIKuK7Pr4Wh8Rd8/aOtAclQw=="
      },
      "SQLitePCLRaw.provider.e_sqlite3": {
        "type": "Transitive",
        "resolved": "3.0.3",
        "contentHash": "wd+fGvZTrr3BJNe48opSczmC176Okd61ZgoZNQcdvZwkek6to978ccdpcFmNo5GHxCnk29KwT+f+lAZYgfLVZg==",
        "dependencies": {
          "SQLitePCLRaw.core": "3.0.3"
        }
      }
    }
  }
}
```

Run inside `dotnet`:

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Each Database instance creates and removes only its own generated temporary directory. Do not point this lab at application data. It uses a single connection, 4096-byte pages, DELETE journal mode and FULL synchronous setting. The measurement does not benchmark concurrency or a production durability deployment.

Rows have unique IDs in 1-50000, positive tenant IDs, signed `long` integer minutes and Amount in 0-1000. The ID bound limits stored rows, keeping sums within `long`. Empty windows are legal; reversed endpoints are rejected. A row at `long.MaxValue` cannot be included by a half-open window with a representable greater endpoint. Failed insert batches roll back; the wrapper is not a general database abstraction.

`LessonLab/Database.cs` creates schema and data, binds query parameters, exposes plans and runs the independent predicate scan. `Exec` is used only with fixed teaching SQL, never arbitrary user input. SQL index maintenance is performed by SQLite, not hand-written tree updates.

```csharp
// Original MIT teaching code; SQLite source is linked, not copied.
using Microsoft.Data.Sqlite;

public readonly record struct EventRow(int Id, int Tenant, long Occurred, int Amount);
public readonly record struct Totals(long Count, long Amount);
public enum AccessPath { Auto, Scan, Thin, Covering }
public enum IndexLayout { None, Thin, Covering, Both }

public sealed class Database : IDisposable
{
    public const int MaxRows = 50_000;
    private readonly string directory;
    public SqliteConnection Connection { get; }

    public Database()
    {
        directory = Path.Combine(Path.GetTempPath(), "cs-index-lab-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        Connection = new SqliteConnection(new SqliteConnectionStringBuilder {
            DataSource = Path.Combine(directory, "events.db"), Pooling = false }.ToString());
        Connection.Open();
        Exec("PRAGMA page_size=4096; PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL;");
        Exec("""
            CREATE TABLE Events(
                Id INTEGER PRIMARY KEY CHECK(Id BETWEEN 1 AND 50000),
                Tenant INTEGER NOT NULL CHECK(Tenant > 0),
                Occurred INTEGER NOT NULL,
                Amount INTEGER NOT NULL CHECK(Amount BETWEEN 0 AND 1000),
                Payload TEXT NOT NULL);
            """);
    }

    public void Exec(string sql)
    {
        using var cmd = Connection.CreateCommand();
        cmd.CommandText = sql;
        cmd.ExecuteNonQuery();
    }

    public static EventRow[] Generate(int n)
    {
        if (n < 0 || n > MaxRows) throw new ArgumentOutOfRangeException(nameof(n));
        return Enumerable.Range(0, n).Select(i =>
            new EventRow(i + 1, i % 10 == 0 ? 2 : 1, i / 2, 1 + i % 97)).ToArray();
    }

    public void Insert(IReadOnlyList<EventRow> rows)
    {
        ArgumentNullException.ThrowIfNull(rows);
        if (rows.Count > MaxRows) throw new ArgumentOutOfRangeException(nameof(rows));
        var ids = new HashSet<int>();
        foreach (var row in rows)
            if (row.Id < 1 || row.Id > MaxRows || row.Tenant <= 0 || row.Amount < 0 || row.Amount > 1000
                || !ids.Add(row.Id)) throw new ArgumentException("Invalid or duplicate row.", nameof(rows));
        using var transaction = Connection.BeginTransaction();
        using var cmd = Connection.CreateCommand();
        cmd.Transaction = transaction;
        cmd.CommandText = "INSERT INTO Events VALUES($id,$tenant,$time,$amount,$payload)";
        foreach (string name in new[] { "$id", "$tenant", "$time", "$amount" })
            cmd.Parameters.Add(name, SqliteType.Integer);
        cmd.Parameters.AddWithValue("$payload", new string('x', 96));
        cmd.Prepare();
        foreach (var row in rows)
        {
            cmd.Parameters["$id"].Value = row.Id;
            cmd.Parameters["$tenant"].Value = row.Tenant;
            cmd.Parameters["$time"].Value = row.Occurred;
            cmd.Parameters["$amount"].Value = row.Amount;
            cmd.ExecuteNonQuery();
        }
        transaction.Commit();
    }

    public void SetIndexes(IndexLayout layout)
    {
        if (!Enum.IsDefined(layout)) throw new ArgumentOutOfRangeException(nameof(layout));
        Exec("DROP INDEX IF EXISTS ix_thin; DROP INDEX IF EXISTS ix_cover;");
        if (layout is IndexLayout.Thin or IndexLayout.Both)
            Exec("CREATE INDEX ix_thin ON Events(Tenant,Occurred)");
        if (layout is IndexLayout.Covering or IndexLayout.Both)
            Exec("CREATE INDEX ix_cover ON Events(Tenant,Occurred,Amount)");
        Exec("ANALYZE");
    }

    public SqliteCommand Query(AccessPath path, int tenant, long start, long end)
    {
        if (tenant <= 0) throw new ArgumentOutOfRangeException(nameof(tenant));
        if (start > end) throw new ArgumentException("Window must satisfy start <= end.");
        string hint = path switch {
            AccessPath.Auto => "", AccessPath.Scan => "NOT INDEXED",
            AccessPath.Thin => "INDEXED BY ix_thin", AccessPath.Covering => "INDEXED BY ix_cover",
            _ => throw new ArgumentOutOfRangeException(nameof(path)) };
        var cmd = Connection.CreateCommand();
        // Only enum-selected identifiers are interpolated; all predicate values are parameters.
        cmd.CommandText = $"""
            SELECT COUNT(*),COALESCE(SUM(Amount),0) FROM Events {hint}
            WHERE Tenant=$tenant AND Occurred >= $start AND Occurred < $end
            """;
        cmd.Parameters.AddWithValue("$tenant", tenant);
        cmd.Parameters.AddWithValue("$start", start);
        cmd.Parameters.AddWithValue("$end", end);
        return cmd;
    }

    public static Totals Read(SqliteCommand cmd)
    {
        using var reader = cmd.ExecuteReader();
        if (!reader.Read()) throw new InvalidOperationException("Missing aggregate row.");
        return new Totals(reader.GetInt64(0), reader.GetInt64(1));
    }

    public Totals Run(AccessPath path, int tenant, long start, long end)
    {
        using var cmd = Query(path, tenant, start, end);
        return Read(cmd);
    }

    public string Plan(AccessPath path, int tenant, long start, long end)
    {
        using var cmd = Query(path, tenant, start, end);
        cmd.CommandText = "EXPLAIN QUERY PLAN " + cmd.CommandText;
        using var reader = cmd.ExecuteReader();
        var lines = new List<string>();
        while (reader.Read()) lines.Add(reader.GetString(3));
        return string.Join(" | ", lines);
    }

    public long Scalar(string sql)
    {
        using var cmd = Connection.CreateCommand(); cmd.CommandText = sql;
        return Convert.ToInt64(cmd.ExecuteScalar());
    }

    public long AllocatedBytes => checked(Scalar("PRAGMA page_count") * Scalar("PRAGMA page_size"));

    public string Version
    {
        get { using var cmd = Connection.CreateCommand(); cmd.CommandText = "SELECT sqlite_version()";
            return (string)cmd.ExecuteScalar()!; }
    }

    public static Totals Reference(IEnumerable<EventRow> rows, int tenant, long start, long end)
    {
        long count = 0, total = 0;
        foreach (var row in rows)
            if (row.Tenant == tenant && row.Occurred >= start && row.Occurred < end)
            { count++; total = checked(total + row.Amount); }
        return new Totals(count, total);
    }

    public void Dispose()
    {
        Connection.Dispose();
        Directory.Delete(directory, true); // Only this instance's generated temporary directory.
    }
}
```

`LessonLab/Program.cs` selects demo, checks or experiment.

```csharp
if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else if (args.Length == 0)
{
    using var db = new Database();
    db.Insert(Database.Generate(2000));
    Console.WriteLine($"SQLite {db.Version}");
    foreach (var layout in new[] { IndexLayout.None, IndexLayout.Thin, IndexLayout.Covering })
    {
        db.SetIndexes(layout);
        var result = db.Run(AccessPath.Auto, 1, 0, 10);
        Console.WriteLine($"{layout}: count={result.Count}, amount={result.Amount}");
        Console.WriteLine(db.Plan(AccessPath.Auto, 1, 0, 10));
    }
}
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

`LessonLab/Checks.cs` checks all windows over a small fixture against a direct C# predicate, across all four paths. It then tests update/delete/insert maintenance, extreme endpoints, invalid inputs and atomic rollback on an existing-ID conflict. It does not use SQL or boundary search as its reference, so a shared window-boundary defect is less likely to pass unnoticed.

```csharp
using Microsoft.Data.Sqlite;

public static class Checks
{
    private static int comparisons;
    private static void Require(bool condition, string message)
    { if (!condition) throw new InvalidOperationException(message); }
    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); } catch (T) { return; }
        throw new InvalidOperationException($"Expected {typeof(T).Name}.");
    }

    private static void Compare(Database db, EventRow[] rows, int tenant, long start, long end)
    {
        var expected = Database.Reference(rows, tenant, start, end);
        foreach (var path in Enum.GetValues<AccessPath>())
        {
            Require(db.Run(path, tenant, start, end) == expected, "Database differs from independent predicate scan.");
            comparisons++;
        }
    }

    public static void Run()
    {
        using var db = new Database();
        db.SetIndexes(IndexLayout.Both);
        Compare(db, [], 1, 0, 10);
        EventRow[] rows = Database.Generate(80);
        db.Insert(rows);
        foreach (int tenant in new[] { 1, 2, 3 })
            for (int start = -1; start <= 41; start++)
                for (int end = start; end <= 41; end++) Compare(db, rows, tenant, start, end);
        Compare(db, rows, 1, long.MinValue, long.MaxValue);
        db.Exec("UPDATE Events SET Tenant=2,Occurred=100,Amount=999 WHERE Id=2");
        rows[1] = new EventRow(2, 2, 100, 999);
        db.Exec("DELETE FROM Events WHERE Id=3");
        rows = rows.Where(r => r.Id != 3).ToArray();
        EventRow[] extra = [new(81, 1, 5, 42), new(82, 1, 5, 0)];
        db.Insert(extra); rows = rows.Concat(extra).ToArray();
        foreach (int tenant in new[] { 1, 2, 3 })
            foreach (var range in new[] { (0L, 40L), (5L, 6L), (100L, 101L), (0L, 0L) })
                Compare(db, rows, tenant, range.Item1, range.Item2);
        db.Insert([new(83, 1, long.MaxValue, 1)]);
        rows = rows.Append(new EventRow(83, 1, long.MaxValue, 1)).ToArray();
        Compare(db, rows, 1, long.MaxValue, long.MaxValue); // Empty, even at the largest endpoint.
        Compare(db, rows, 1, long.MinValue, long.MaxValue); // MaxValue itself is excluded.
        Require(db.Plan(AccessPath.Scan, 1, 0, 10).Contains("SCAN Events"), "Missing forced scan.");
        Require(db.Plan(AccessPath.Thin, 1, 0, 10).Contains("USING INDEX ix_thin"), "Missing thin index.");
        Require(db.Plan(AccessPath.Covering, 1, 0, 10).Contains("USING COVERING INDEX ix_cover"), "Missing covering index.");
        Throws<ArgumentException>(() => db.Run(AccessPath.Auto, 1, 10, 0));
        Throws<ArgumentOutOfRangeException>(() => db.Run(AccessPath.Auto, 0, 0, 1));
        Throws<ArgumentOutOfRangeException>(() => db.Run((AccessPath)100, 1, 0, 1));
        Throws<ArgumentException>(() => db.Insert([new(90, 1, 1, 1), new(90, 1, 2, 1)]));
        Throws<ArgumentException>(() => db.Insert([new(90, 1, 1, 1001)]));
        Throws<ArgumentOutOfRangeException>(() => Database.Generate(Database.MaxRows + 1));
        // A database-level duplicate after a successful insert must roll back the whole batch.
        long before = db.Scalar("SELECT COUNT(*) FROM Events");
        Throws<SqliteException>(() => db.Insert([new(90, 1, 1, 1), new(2, 1, 2, 1)]));
        Require(db.Scalar("SELECT COUNT(*) FROM Events") == before, "Failed batch was partly committed.");
        Require(db.Scalar("SELECT COUNT(*) FROM Events WHERE Id=90") == 0, "Rollback left first row.");
        Console.WriteLine($"PASS: {comparisons} aggregate comparisons; index maintenance, plans and rollback checked.");
    }
}
```

`LessonLab/Experiment.cs` measures identical prepared aggregate queries, rotating execution order. The second experiment uses fresh databases with zero or one index and includes the full Insert call, validation, transaction and commit in each measured batch. Creation of schema/indexes and result verification are outside that write interval.

```csharp
using System.Diagnostics;
using System.Globalization;

public static class Experiment
{
    private static string F(double value) => value.ToString("F4", CultureInfo.InvariantCulture);
    private static double Median(double[] values) { var copy = values.Order().ToArray(); return copy[copy.Length / 2]; }

    public static void Run()
    {
        EventRow[] rows = Database.Generate(20_000);
        using (var db = new Database())
        {
            db.Insert(rows); db.SetIndexes(IndexLayout.Both);
            Console.WriteLine($"# SQLite={db.Version}; query warmups=3, rounds=9; pageSize=4096; journal=DELETE; synchronous=FULL");
            Console.WriteLine("kind,case,path,n,matches,amount,medianMs,minMs,maxMs,allocatedDbBytes");
            foreach (int end in new[] { 10, 1000, 10000 })
            {
                AccessPath[] paths = [AccessPath.Scan, AccessPath.Thin, AccessPath.Covering];
                var expected = Database.Reference(rows, 1, 0, end);
                var commands = paths.Select(p => db.Query(p, 1, 0, end)).ToArray();
                try
                {
                    foreach (var cmd in commands)
                    { cmd.Prepare(); for (int warmup = 0; warmup < 3; warmup++) Database.Read(cmd); }
                    var times = paths.Select(_ => new double[9]).ToArray();
                    for (int round = 0; round < 9; round++)
                        for (int slot = 0; slot < paths.Length; slot++)
                        {
                            int i = (slot + round) % paths.Length; // Rotate execution order.
                            var watch = Stopwatch.StartNew();
                            Totals result = Database.Read(commands[i]);
                            watch.Stop();
                            if (result != expected) throw new InvalidOperationException("Measured query changed the answer.");
                            times[i][round] = watch.Elapsed.TotalMilliseconds;
                        }
                    for (int i = 0; i < paths.Length; i++)
                    {
                        Console.WriteLine($"query,end={end},{paths[i]},{rows.Length},{expected.Count},{expected.Amount}," +
                            $"{F(Median(times[i]))},{F(times[i].Min())},{F(times[i].Max())},{db.AllocatedBytes}");
                        Console.WriteLine($"# plan end={end} {paths[i]}: {db.Plan(paths[i], 1, 0, end)}");
                    }
                }
                finally { foreach (var cmd in commands) cmd.Dispose(); }
            }
        }
        EventRow[] writeRows = Database.Generate(5000);
        // Fresh databases; schema/index creation excluded, transaction+inserts+commit included.
        IndexLayout[] layouts = [IndexLayout.None, IndexLayout.Thin, IndexLayout.Covering];
        var writes = layouts.Select(_ => new double[5]).ToArray();
        var sizes = new long[layouts.Length];
        for (int round = -1; round < 5; round++) // One unrecorded batch per layout.
            for (int slot = 0; slot < layouts.Length; slot++)
            {
                int i = (slot + Math.Max(round, 0)) % layouts.Length;
                using var db = new Database(); db.SetIndexes(layouts[i]);
                var watch = Stopwatch.StartNew(); db.Insert(writeRows); watch.Stop();
                if (db.Run(AccessPath.Scan, 1, 0, 2500) != Database.Reference(writeRows, 1, 0, 2500))
                    throw new InvalidOperationException("Write experiment changed the answer.");
                if (round >= 0) writes[i][round] = watch.Elapsed.TotalMilliseconds;
                sizes[i] = db.AllocatedBytes;
            }
        for (int i = 0; i < layouts.Length; i++)
            Console.WriteLine($"insert,batch,{layouts[i]},{writeRows.Length},4500," +
                $"{Database.Reference(writeRows, 1, 0, 2500).Amount},{F(Median(writes[i]))}," +
                $"{F(writes[i].Min())},{F(writes[i].Max())},{sizes[i]}");
    }
}
```

Expected demo and check output:

```text
SQLite 3.50.4
None: count=18, amount=198
SCAN Events
Thin: count=18, amount=198
SEARCH Events USING INDEX ix_thin (Tenant=? AND Occurred>? AND Occurred<?)
Covering: count=18, amount=198
SEARCH Events USING COVERING INDEX ix_cover (Tenant=? AND Occurred>? AND Occurred<?)
PASS: 11416 aggregate comparisons; index maintenance, plans and rollback checked.
```

The first seven lines come from the demo; the last comes from `--check`. All four source files and setup fences are complete. Tests provide evidence for these fixtures and implementation paths, not a proof of the SQLite engine or every SQL query. The range argument in section 2 explains the intended result, and SQLite executes the real query.

</details>

Defect exercise: replace both Occurred comparisons by comparisons on `(Occurred+0)`. On this integer fixture, are totals still correct? What may be lost from the thin-index plan, and how would you repair it?

<details>
<summary>Answer</summary>

Adding integer zero preserves these values, so semantic checks can still pass. With the ordinary `(Tenant,Occurred)` index, SQLite 3.50.4 no longer treats the expression as the raw time key for this range: the forced thin plan has `(Tenant=?)`, omitting Occurred bounds. SEARCH remains in the label, but it may visit the whole tenant group before evaluating time. Restore comparisons on the raw key, using the Query method above. Check both results and range terms; correctness tests alone do not detect every performance regression. Expression indexes can support selected expressions, but are a different design needing their own validation.

</details>

Pause - 10 minutes away from the screen.

## 6. Controlled experiments: selection, coverage and writes

**Experiment · 45 minutes.** Predict the deterministic totals, run `--experiment` and compare repeated times without changing the objective. **Done when:** you can separate a query effect from a write/storage trade-off and name an uncontrolled factor.

### Read experiment

Keep the same 20,000-row database, row order, amounts, payload width, parameters and aggregate. Generated rows have time `i/2`, tenant 2 when `i%10==0`, otherwise tenant 1, and amount `1+i%97`. Both indexes already exist; index creation is outside read timing. The query does not sort output: adding ORDER BY would change the workload.

For tenant 1 and start 0, vary only end=10,1000,10000 between cases. Within a case vary only the forced access path. Prepare all commands, execute three warmups each, then measure nine queries per path in rotating order. Timing includes execution, reading both aggregate fields and disposing the reader. It excludes prepare, database creation, index building, result verification and printing. Warmups intentionally produce a warm-cache experiment, not cold-storage I/O.

Predict the matches, amount sums and fraction r/N. Predict a likely trend, not exact milliseconds.

What are the deterministic predictions, and why can a broad thin-index query lose to scan?

<details>
<summary>Answer</summary>

| End | Matches r | Amount sum | r/N |
|---|---|---|---|
| 10 | 18 | 198 | 0.09% |
| 1000 | 1800 | 87228 | 9% |
| 10000 | 18000 | 881310 | 90% |

A narrow path skips most rows. At 90%, a thin path traverses index entries and fetches most table rows; a scan can avoid that additional tree work. Coverage removes Amount lookups, so its result can differ from the thin path. These are cost-model predictions, not guarantees of a timing order. The program validates every measured result against the independent reference.

</details>

### One observed run, not required timing output

The following medians were observed on one Linux execution with the pinned runtime and this exact dataset. The counts above matched. Values are an example to interpret; your machine and repeated runs may differ.

| End | Scan median ms | Thin median ms | Covering median ms |
|---|---|---|---|
| 10 | 1.2817 | 0.0176 | 0.0083 |
| 1000 | 1.2587 | 0.2193 | 0.1253 |
| 10000 | 1.8831 | 2.4323 | 1.1849 |

The broad thin query was slower than scan in this run. The CSV also reports min/max: broad thin 2.1426-2.8583 ms and scan 1.5982-2.7117 ms overlap. Coverage helped in this run, but the measurements do not locate a universal crossover or prove an expected latency. INDEXED BY controls access; it does not demonstrate the unforced planner's choice under every window.

### Write and storage experiment

Use fresh databases with the same 5,000 rows and either no index, thin only or covering only. Schema/index creation is outside timing. Insert all rows in one transaction; include validation, command setup, execution and commit. Run one unrecorded batch per layout and five recorded batches each, rotating layout order. Compare median/min/max and logical allocated database bytes (`page_count*page_size`), not peak RAM or total journal traffic.

An observed example:

| Layout | Insert median ms | Logical database bytes |
|---|---|---|
| None | 14.0416 | 581632 |
| Thin | 16.9022 | 647168 |
| Covering | 15.8131 | 659456 |

All batches produce 4,500 tenant-1 matches and amount 219489 over `[0,2500)`. Extra indexes occupied more space and had higher median insertion time than no index in this run. Covering was not slower than thin by the median, despite being wider. Five batches and overlapping ranges are not enough to infer a stable ranking between them. The query experiment's database has both indexes; its allocated size is 2793472 bytes for every read path, so those repeated sizes do not measure incremental index size.

Variation: what must change to test cold reads or decide which index to deploy? Does a smaller median alone prove the recommendation?

<details>
<summary>Answer</summary>

A separate cold-read protocol must control SQLite and OS caches and storage; merely reopening a connection does not clear the OS page cache. Use representative tenant skew, query mix, projections, writes, file size and concurrency. Keep identical results, count total read/write/storage costs and repeat with uncertainty. This lab does not control CPU scheduling, OS cache eviction, storage flush implementation or a concurrent workload. Its timings describe a small warm-cache local database; they cannot establish SQL Server plans, production p99, durable-storage guarantees or a business index policy.

</details>

Pause - 10 minutes away from the screen.

## 7. Transfer: ordered pages need a different contract

**Transfer · 35 minutes.** Change the endpoint from totals to two events per page, ordered by `(Occurred,Id)`. **Done when:** duplicate times are neither skipped nor repeated, and the index respects both ordering and projection.

Use the eight rows from section 2, tenant 1 and page size 2. The first page is IDs 2,3, ending at time 1/Id 3. Why does remembering only time and querying `Occurred>1` fail? Design a cursor, index and next-page predicate. Explain what must stay fixed across requests.

<details>
<summary>Answer - cursor, complete implementation and checks</summary>

The next page should start with Id 4, also at time 1. A time-only predicate skips it and returns 5,6. Keep `(lastTime,lastId)` and require the next lexicographic pair to be strictly greater. Because Id is unique, this gives a total order. Keep a fixed dataset/snapshot across pages for this proof; concurrent insert/update/delete can otherwise change which events appear.

An index `(Tenant,Occurred,Id,Amount)` covers the page and orders equal times by Id before Amount. The aggregate's `(Tenant,Occurred,Amount)` does not provide that same tie order. The added Id is explicit even though rowid is also retained. The predicate below uses `Occurred>=lastTime` as a coarse range and filters the equal-time prefix by Id; it does not claim a single ideal composite seek for every cursor. It avoids incrementing a timestamp, which could overflow.

In a separate copy of the lab, keep Database.cs and replace Program.cs with the complete code below. Run `dotnet run --no-restore -c Release --project LessonLab` after restore. The list scan/order is the independent reference.

```csharp
using Microsoft.Data.Sqlite;

using var db = new Database();
EventRow[] rows = Database.Generate(8);
db.Insert(rows);
db.Exec("CREATE INDEX ix_page ON Events(Tenant,Occurred,Id,Amount)");
var seen = new List<int>();
long lastTime = long.MinValue;
int lastId = 0;
while (true)
{
    using var cmd = PageCommand(db, lastTime, lastId);
    using var reader = cmd.ExecuteReader();
    var page = new List<(int Id, long Time, int Amount)>();
    while (reader.Read()) page.Add((reader.GetInt32(0), reader.GetInt64(1), reader.GetInt32(2)));
    if (page.Count == 0) break;
    foreach (var item in page)
    {
        if (rows.Single(r => r.Id == item.Id).Amount != item.Amount) throw new Exception("Wrong Amount.");
        seen.Add(item.Id);
    }
    (lastId, lastTime, _) = page[^1];
    if (seen.Count > rows.Length) throw new Exception("Cursor repeated a page.");
}
int[] expected = rows.Where(r => r.Tenant == 1).OrderBy(r => r.Occurred).ThenBy(r => r.Id)
    .Select(r => r.Id).ToArray();
if (!seen.SequenceEqual(expected)) throw new Exception("Missing or repeated event.");
using (var plan = PageCommand(db, 1, 3))
{
    plan.CommandText = "EXPLAIN QUERY PLAN " + plan.CommandText;
    using var reader = plan.ExecuteReader();
    var detail = new List<string>();
    while (reader.Read()) detail.Add(reader.GetString(3));
    if (!detail.Any(s => s.Contains("USING COVERING INDEX ix_page")) || detail.Any(s => s.Contains("TEMP B-TREE")))
        throw new Exception("Unexpected pinned-version page plan.");
}
Console.WriteLine($"PASS: keyset pages ids={string.Join(",", seen)}; no skipped duplicate timestamp.");

static SqliteCommand PageCommand(Database db, long time, int id)
{
    var cmd = db.Connection.CreateCommand();
    cmd.CommandText = """
        SELECT Id,Occurred,Amount FROM Events INDEXED BY ix_page
        WHERE Tenant=$tenant AND Occurred >= $time AND (Occurred > $time OR Id > $id)
        ORDER BY Occurred,Id LIMIT $take
        """;
    cmd.Parameters.AddWithValue("$tenant", 1);
    cmd.Parameters.AddWithValue("$time", time);
    cmd.Parameters.AddWithValue("$id", id);
    cmd.Parameters.AddWithValue("$take", 2);
    return cmd;
}
```

Expected: `PASS: keyset pages ids=2,3,4,5,6,7,8; no skipped duplicate timestamp.` The range predicate plus strict cursor comparison includes every remaining pair once and never returns the cursor pair. The explicit ORDER BY fixes the contract; LIMIT only truncates that ordered suffix. A stable snapshot is assumed, not implemented across HTTP requests. The lab's pinned-version plan check is not a production plan parser.

In SQL Server the comparable index key can be `(TenantId,OccurredUtc,EventId) INCLUDE(Amount)`, because Amount need not participate in ordering. That is a design candidate, not a verified SQL Server execution plan. Changing from totals to ordered pagination is why state, predicate, projection and index design must be reconsidered together.

</details>

## 8. Synthesis and retrieval

**Synthesis · 45 minutes.** Reconstruct the model without the page, then write one index decision and one falsifying test. **Done when:** the decision names the workload, result contract, evidence and remaining uncertainty.

1. Why do two boundary searches count an array window quickly, while the lab aggregate still examines matching Amount values?

<details>
<summary>Answer</summary>

Array indices supply ranks, so subtraction counts elements without visiting them. Ordinary SQLite index cursors do not expose that representation, and a sum depends on the actual matching values. With no stored summary, seek only finds where to start; traversal and any required table lookups remain.

</details>

2. What counterexample rejects “SEARCH is always faster than SCAN”?

<details>
<summary>Answer</summary>

The observed 90%-match thin-index aggregate had a larger median than forced scan on identical input and output. It visited index entries and fetched Amount from the table; scan avoided the extra index route. This is a measured counterexample to a universal claim, not a theorem that scan wins above 90% on every system. Changing coverage or ordering can change the result.

</details>

3. Separate assumptions, predictions, observations and inferences for the experiment.

<details>
<summary>Answer</summary>

Assumptions: fixed synthetic rows, bounded integer values, one connection, the specified page/journal settings and identical aggregate semantics. Predictions: deterministic totals, sparse-range savings and possible broad noncovering penalties. Observations: real plans, the validated CSV totals, repeated timings and allocated pages. Inferences: the selected implementation reproduced these mechanisms and a read/write trade-off on this workload. It does not establish cold I/O, production concurrency or SQL Server behavior.

</details>

4. Write a defensible deployment decision and a test that could overturn it.

<details>
<summary>Answer</summary>

For a tenant/time aggregate, trial a tenant-leading covering index if representative read savings justify its storage and write overhead. Verify identical totals and observe real unforced plans; compare against a scan and existing indexes with repeated measurements. Reject or revise the candidate if write throughput, memory/storage budget, broad-window latency or a changed projection is unacceptable. The page index needs a separate order contract. Do not turn the lab result or Lesson 04's knapsack half guarantee into an optimizer-quality guarantee.

</details>

## Sources and reuse

- SQLite official [Query Planning](https://www.sqlite.org/queryplanner.html), sections 1.4, 1.6, 1.7; [EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html), section 1.1; [optimizer overview](https://www.sqlite.org/optoverview.html), section 2 and skip-scan; [INDEXED BY](https://www.sqlite.org/lang_indexedby.html); [file format, B-tree pages](https://www.sqlite.org/fileformat.html#b_tree_pages).
- SQLite source tag `version-3.50.4` at GitHub commit `8ed5e7365e6f12f427910188bbf6b254daad2ef6`; bounded implementation links in section 4. The GitHub mirror's hash differs from the Fossil hash reported by `sqlite_source_id()`; the engine version here matches the tag. [SQLite public-domain notice](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/LICENSE.md). No SQLite code is copied into the lesson lab.
- Microsoft [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17) supports the application bridge, B+ tree distinction and INCLUDE semantics. No SQL Server plan or timing was reproduced.
- [Microsoft.Data.Sqlite overview](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/) supplies the C# provider context. Package versions are pinned in the project and lock file; dependencies retain their own license terms.
- Original lesson prose uses CC BY 4.0; original C# teaching code uses MIT, included in the ZIP.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 02 - Boundary search](../boundary-search/lesson.md) - Recall half-open windows, duplicate boundaries and rank subtraction.
- [Lesson 04 - Dynamic programming and approximation](../2026-10-08-dp-approximation/lesson.md) - Recall state requirements and separate models from measurements.
- [C# lab guide](../../labs/index-query-plans/dotnet/README.md) - Pinned dependencies, checks, measurements and sources.

---

[← Previous: Lesson 04 - Dynamic programming and approximation: selecting jobs within a budget](../2026-10-08-dp-approximation/lesson.md) · [All lessons](../../README.md)
<!-- LESSON_NAVIGATION_END -->
