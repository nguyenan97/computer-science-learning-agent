# Lesson 06 - Transactions and recovery: a correct write can use a stale decision

[Tiếng Việt](../../vi/lessons/2026-10-10-transactions-recovery/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/transactions-recovery/dotnet-lab.zip)

An inventory service has ten units. Two requests both read ten, then reserve seven and five. Each UPDATE succeeds and every stored balance stays nonnegative, yet twelve units have been promised. We will reproduce that schedule, repair the decision boundary, and reopen a database after killing a writer before or after commit.

**Goal:** distinguish an atomic transaction from a valid business decision, detect stale reads, justify a guarded reservation and interpret a bounded crash/recovery trace. The planner selects transactions after indexes. We reuse SQL parameters, independent result checks and the difference between a model and an observation; transaction boundaries, isolation, snapshots and WAL are introduced here.

## Core ideas

- **Atomic work.** Decreasing stock and storing its reservation receipt belong together. Commit publishes the group; rollback removes the group's changes. Atomicity does not itself prove that a quantity chosen from an earlier read is valid.
- **Isolation and a schedule.** Two clients can read before either writes. A schedule describes that interleaving. Isolation governs database transactions, so first identify which reads and writes belong to each transaction.
- **A stale decision and a version guard.** A request that read version 0 must not silently replace stock already changed to version 1. The write can test both the expected version and current stock, then report a conflict instead of guessing.
- **Snapshot.** A WAL reader can keep seeing stock ten while another client commits stock three. This stable view is useful, but SQLite will reject promotion of that old read snapshot into a writer.
- **Recovery and the commit boundary.** WAL records changed pages and a commit marker. After a process crash, pages beyond the last valid committed boundary must not become visible. Commit is different from copying those pages back by checkpointing.

You may read every trace, complete program and worked result without running it. Limit setup to 15 minutes of the lab block, then use the reading route. The lab creates its own temporary database and kills only its own child process; no server or personal data is needed.

## 1. Recall and the missing boundary

**Recall · 20 minutes.** Reconstruct the two planner-selected mechanisms, then identify a new correctness condition. **Done when:** you can say which evidence a plan label or a stored old value fails to provide.

1. From Lesson 05: why can SEARCH cost more than SCAN for a broad noncovering aggregate?

<details>
<summary>Answer</summary>

Seek locates the range; visiting matching entries and fetching missing Amount values still cost work. Scan can avoid the extra route for a broad range. Coverage, order and cache matter, so the plan label alone does not rank runtime. Likewise, a fast reservation lookup does not prove the value is still current when a later write uses it.

</details>

2. From Lesson 03: why can the lazy heap contain two entries for a node, and how are stale entries handled? State the bounds.

<details>
<summary>Answer</summary>

A strict improvement enqueues another cost instead of decreasing the old key. Skip an entry whose cost differs from dist[node]. With at most E improvements, time is O(V+E log(E+2)) and search memory O(V+E), assuming adjacency arrays and bounded integer operations. The analogy today is checking old evidence against current state; it does not make a database version check a shortest-path proof.

</details>

3. If a transaction decreases stock and inserts a receipt together, does that alone prevent two requests from reserving more than the initial stock?

<details>
<summary>Answer</summary>

No. Atomicity makes each pair all-or-nothing. The business condition also requires that its decision use admissible current stock. An old read outside that transaction can still authorize an invalid write. A CHECK that Available is nonnegative cannot detect all promises stored in other rows.

</details>

## 2. A schedule, an invariant and a guarded decision

**Foundation · 50 minutes.** Trace the ten-unit counterexample and derive the repair. **Done when:** you can justify every commit, conflict and rollback without relying on elapsed timing.

### First trace the business operation

The database contains one Stock row with Available=10, Version=0 and an empty Reservations table. T1 requests seven units; T2 requests five. Each client first reads in autocommit, stores that value in application memory, and later begins a separate write transaction. Its two writes are stock plus receipt.

Predict the final stock and total reserved under `Available = oldAvailable - quantity`. Which rule is broken?

<details>
<summary>Answer</summary>

| Step | T1 | T2 | Committed stock | Reserved total |
|---|---|---|---|---|
| 1 | Read (10,0), outside write transaction | | 10 | 0 |
| 2 | | Read (10,0), outside write transaction | 10 | 0 |
| 3 | Begin; set 10-7=3; receipt A=7; commit | | 3 | 7 |
| 4 | | Begin; set old 10-5=5; receipt B=5; commit | 5 | 12 |

Both write transactions are atomic and execute one after the other. The second overwrites the first decrement using an old application value. This is a lost update at the business-operation level, not evidence that SQLite silently allows a stale read transaction to upgrade. Nonnegative stock still passes, but 5+12=17 rather than the original ten. Neither legal serial order can accept both requests: one must be rejected.

</details>

### Name the invariant and transaction scope

Assume no restocking, cancellation or external writes during this fixture. Let A be current available stock, S the sum of quantities in committed receipts and I initial stock. The example motivates **A+S=I**, with A>=0. A receipt must correspond to exactly one committed decrement. All writers must obey the rule; the database cannot infer the business meaning of an arbitrary UPDATE.

Atomicity is all-or-nothing; consistency requires the chosen constraints and application operations to preserve the intended rules; isolation limits interactions between transactions; durability concerns committed effects under a stated failure model. These are the ACID properties. An isolation level is a chosen guarantee, not a promise that every application workflow spanning transactions is serializable.

A serial schedule runs whole business operations one at a time. To justify our controlled outcome, compare it with the legal order T1 then T2. T1 commits seven, leaving three; T2 rechecks three and rejects five. Choosing the opposite order can produce another valid answer. The lab tests its selected order, not fairness.

### Validate the old evidence at the write

Version is an application integer increased on every accepted change to Stock. It is not SQLite's internal WAL position and not SQL Server's binary rowversion type. The guarded UPDATE subtracts from current stock only when the expected version matches and current Available is sufficient. Receipt insertion and UPDATE share one transaction.

```sql
UPDATE Stock SET Available=Available-$q,Version=Version+1
WHERE Id=1 AND Version=$v AND Available >= $q;
```

A zero-row update means the predicate did not admit a write. Here it is a conflict; a fresh read may reveal insufficient stock. Do not insert a receipt after zero rows. Roll back, re-read and reconsider the whole decision within a bounded retry policy. Retrying the identical stale value is not reconsideration.

The guarded proof is inductive: initially A=I and S=0. Rejection/conflict changes neither. An admitted quantity q satisfies A>=q; commit changes A to A-q and S to S+q together, retaining their sum and nonnegative A. A failure between writes rolls back both. A replay whose durable receipt already exists changes neither. Version increments invalidate older snapshots. This proof assumes one stock item and all mutations follow this transaction rule; it is not a proof for arbitrary multi-row constraints.

Why does starting the write with BEGIN IMMEDIATE fail to repair the blind strategy?

<details>
<summary>Answer</summary>

IMMEDIATE obtains the writer slot before its statements, but the application's earlier read is already outside that transaction. Serializing the later writes does not refresh that value. The version/current-stock predicate ties permission to current database state. A transaction that starts before its read and retains the writer slot is another design, with more blocking.

</details>

Why must a retry read again?

<details>
<summary>Answer</summary>

A retry must use newly read state. With five units, reading stock three changes the decision to rejection; a two-unit request can succeed. The old view cannot support that new decision. An intervening writer may still cause another conflict.

</details>

Pause - 10 minutes away from the screen.

## 3. Read isolation and recovery guarantees

**Source reading · 45 minutes.** Annotate the official guarantees against our schedules. **Done when:** each claim has a source and an explicit boundary.

Read SQLite [Isolation](https://www.sqlite.org/isolation.html), its separate-connection and WAL examples; [WAL sections 2.1-2.3](https://www.sqlite.org/wal.html), on checkpointing, concurrency and performance; and [transaction sections 2.1-2.2](https://www.sqlite.org/lang_transaction.html), on read/write and DEFERRED/IMMEDIATE. Read Microsoft.Data.Sqlite's [deferred transactions](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/transactions#deferred-transactions). Shared cache plus read_uncommitted is an exception to SQLite's ordinary separate-connection visibility; the lab uses private caches.

### A stable read is not a fresh write

A DEFERRED transaction postpones obtaining the writer slot. Its first SELECT establishes the read view. In WAL, a writer can append committed pages while that reader keeps its older snapshot. Our read transaction sees ten both before and after the writer commits three. Promotion of that stale transaction to a writer fails with SQLITE_BUSY_SNAPSHOT (extended code 517 in this pinned engine). End the old transaction before retrying; waiting longer does not make its snapshot current.

Trace this case and explain how it differs from the blind reservation.

<details>
<summary>Answer</summary>

| Step | Reader R | Writer W | Current committed stock |
|---|---|---|---|
| 1 | BEGIN DEFERRED; SELECT -> 10 | | 10 |
| 2 | Keep transaction open | Guarded reserve 7; commit | 3 |
| 3 | SELECT -> still 10 | | 3 |
| 4 | Try UPDATE -> error 517 | | 3 |
| 5 | ROLLBACK; new SELECT -> 3 | | 3 |

Unlike the blind example, R's read and attempted write belong to the same still-open database transaction. SQLite refuses its stale upgrade. The blind workflow ended its earlier read and later opened a new write transaction, carrying only an unchecked application value. Both stories can coexist without contradicting SQLite's guarantees. SQLITE_BUSY for writer-slot contention and SQLITE_BUSY_SNAPSHOT for an old view are not interchangeable retry situations.

</details>

### Changed pages, commit and checkpoint

SQLite's write-ahead log (WAL) is a separate file of changed pages. A changed page buffered in memory is called dirty; it can be spilled into WAL before commit. A WAL frame stores one such page plus a header. A valid commit frame records the resulting database size. Recovery recognizes the last valid committed boundary; an unfinished suffix is not a committed transaction. A checkpoint later transfers eligible committed pages into the database file. A successful commit can exist in WAL before that transfer.

Readers retain an end mark, so a long read can prevent checkpoint progress and keep WAL space in use. SQLite WAL permits readers with one writer, not many simultaneous writers. It needs local shared-memory coordination; it is not a network-filesystem or distributed replication protocol.

Write one claim/evidence/limit row each for snapshot, stale upgrade and committed recovery.

<details>
<summary>Answer</summary>

| Claim | Evidence | Limit |
|---|---|---|
| WAL reader retains its view | Isolation example and WAL 2.2 end mark | It may be stale relative to a later request; long reads affect checkpointing |
| Old read view cannot become a writer after another commit | Isolation's BUSY_SNAPSHOT example | A new application transaction using old values needs its own guard |
| A committed WAL group is recoverable after a process crash | WAL commit/checkpoint description and the lab below | Two kill boundaries do not test power loss, torn writes, every VFS or device |

Microsoft.Data.Sqlite documents retrying the entire deferred transaction after a failed upgrade. SQLite's [synchronous pragma](https://www.sqlite.org/pragma.html#pragma_synchronous) qualifies durability by mode and synchronization. FULL is selected here, but our process kill leaves the OS alive; it does not test a failing storage device.

</details>

## 4. Project decisions and a pinned SQLite source walk

**Implementation reading · 45 minutes.** Map the reservation to an API and read three bounded WAL slices. **Done when:** you distinguish what the source enforces from an application rule it cannot infer.

### An ASP.NET inventory endpoint

Bind a request ID, item and quantity, validate them, and place the stock change plus durable receipt in one database transaction. Never hold a transaction while waiting for an Angular user or an external payment service. A stale UI value is a proposal, not authoritative inventory. The server must decide again at the write boundary.

SQL Server can use a guarded UPDATE and inspect its affected-row result, storing the receipt atomically. Its [transaction guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17), ACID, concurrency control and row-versioning isolation sections, distinguishes READ COMMITTED with RCSI's statement view from SNAPSHOT's transaction view. A database option and engine's guarantees matter; copying SQLite's error 517 or WAL format does not establish SQL Server behavior.

How would you express the guarded write in T-SQL, and what remains unverified?

<details>
<summary>Answer</summary>

The following is a design fragment, not the executable lab. It requires tables/parameters with appropriate types and a unique request key; it has not been run on SQL Server. @@ROWCOUNT must be checked immediately after UPDATE. Production code must also handle replay lookup, payload mismatch, errors, permissions and its selected isolation policy.

```tsql
SET XACT_ABORT ON;
BEGIN TRANSACTION;
UPDATE dbo.Stock SET Available=Available-@Quantity, Version=Version+1
WHERE Id=@ItemId AND Version=@ExpectedVersion AND Available>=@Quantity;
IF @@ROWCOUNT = 1
    INSERT dbo.Reservations(RequestId,Quantity) VALUES(@RequestId,@Quantity);
ELSE
BEGIN
    ROLLBACK TRANSACTION;
    THROW 50001, 'Conflict or insufficient stock', 1;
END;
COMMIT TRANSACTION;
```

XACT_ABORT makes many runtime errors abort the transaction; it is not a replacement for correct application exception handling. This integer Version is a design choice, not SQL Server's automatic rowversion. Plans, blocking, retries and throughput still need SQL Server execution. The tested implementation below uses C# and SQLite so the transaction/crash experiments run without a server.

</details>

### Why the embedded database needs this mechanism

SQLite's WAL lets an embedded application keep readers active while a writer commits. Its [source overview](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L15-L133) describes frames, commit markers, reader end marks and a wal-index to avoid scanning potentially multi-megabyte WAL files for every page. This is the product problem: efficient reads must still choose a committed version. The derived wal-index accelerates lookup; it is not the durable source of truth.

Use immutable commit **8ed5e7365e6f12f427910188bbf6b254daad2ef6**, tag version-3.50.4, matching our engine version:

1. [sqlite3WalBeginWriteTransaction, lines 3664-3725](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L3664-L3725) obtains the single writer lock, compares the reader's WAL header with the current header and rejects a stale snapshot.
2. [walFrames, lines 4138-4188](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L4138-L4188) gives the final committed frame a database-size marker and handles configured commit synchronization. It does not say every dirty page spill is a commit.
3. [walIndexRecover, lines 1481-1528](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L1481-L1528) reads/decodes frames, stops on invalid data and advances the committed header when nTruncate is nonzero. [walDecodeFrame, lines 1000-1045](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L1000-L1045) checks salts, page number and cumulative checksum.

**Verified:** one writer, stale-header rejection, commit marking and committed-boundary reconstruction. **Design inference:** keeping transactions short reduces how long our endpoint holds resources; adding a version predicate protects its external stale decision. These slices do not prove every pager/VFS failure path or our business invariant. SQLite accepts the one-writer/local-coordination trade-off; the lab does not measure maximum concurrency.

If unfinished frames are present after a crash, why cannot file length alone tell you which balances to return?

<details>
<summary>Answer</summary>

File length shows bytes, not a valid committed boundary. Frames need validation, and only a valid commit marker advances the readable committed state. An uncommitted spill may be physically present but invisible after reopening. The lab checks resulting SQL state and observes WAL presence; it does not parse or validate every binary frame itself. SQLite performs that recovery.

</details>

Lunch and rest - 30 minutes.

## 5. C# lab: two clients and a killed writer

**Lab · 75 minutes.** Run the controlled schedules, fix the stale-value defect and verify rollback/recovery. **Done when:** the checks pass and you can identify the exact transaction/failure boundaries.

Implement the stock-plus-receipt operation, then let two clients read before T1 commits and T2 writes. Preserve a receipt only when the stock decrement commits. Test a read transaction that remains open and both crash boundaries. Use the complete solution if setup or implementation exceeds its timebox.

<details>
<summary>Answer - complete runnable lab</summary>

Use SDK **10.0.401** (latestPatch roll-forward), **net10.0**, **Microsoft.Data.Sqlite 10.0.9**, **SQLitePCLRaw.bundle_e_sqlite3 3.0.3** and the checked-in lock file. The engine reports **SQLite 3.50.4**. The first restore needs NuGet; subsequent no-restore runs can use cached packages. No database server is required.

Extract into `dotnet`, or use `labs/transactions-recovery/dotnet` in a checkout. Rebuilding from the page requires every file below. [The lab guide](../../labs/transactions-recovery/dotnet/README.md) links individual sources. All databases live in generated temporary directories; the ZIP contains source/setup only.

Task.Run starts each client task; each owns a separate connection. TaskCompletionSource gates control read1, read2 and written1. Await waits for an acknowledged step, not a guessed delay. The clients overlap in lifetime while statements follow R1,R2,W1,W2; this is not two simultaneous SQLite writers. Gate timeouts detect broken coordination, not a lock-retry policy.

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

The fixture bounds initial stock to 0-1000, quantity to 1-1000 and request IDs to nonblank strings of at most 100 characters. Private caches, Pooling=false, WAL, synchronous=FULL and wal_autocheckpoint=0 are explicit. DefaultTimeout=1 bounds provider busy waiting; zero means no timeout. Version is bounded in the schema and successful guarded decrements cannot outnumber the initial stock. Reset occurs only outside client tasks; restocks and cancellations are not modeled.

The controlled retry permits one fresh attempt. It is sufficient for this two-client ordered case, not a general contention algorithm. Conflict is not success; a production caller needs a bounded policy and a way to report unresolved results. Fixed teaching SQL goes to Exec/Scalar; request values are parameters.

`LessonLab/Store.cs`. Store creates schema, binds values and keeps decrement plus receipt in one IMMEDIATE write transaction. The blind branch is intentionally wrong; the guarded branch checks version/current stock. Existing receipts are looked up before admission so a matching replay does not consume stock again.

```csharp
// Original MIT teaching code; SQLite implementation is linked, not copied.
using Microsoft.Data.Sqlite;

public readonly record struct StockView(int Available, int Version);
public enum Outcome { Committed, Rejected, Conflict, Replayed }
public enum Strategy { Blind, Guarded, Retry }

public sealed class Store : IDisposable
{
    private readonly string directory = Path.Combine(Path.GetTempPath(), "cs-tx-lab-" + Guid.NewGuid().ToString("N"));
    public string FilePath { get; }
    public Store(int initial = 10)
    {
        if (initial < 0 || initial > 1000) throw new ArgumentOutOfRangeException(nameof(initial));
        Directory.CreateDirectory(directory);
        FilePath = Path.Combine(directory, "stock.db");
        using var c = Open(FilePath);
        Exec(c, """
            PRAGMA page_size=4096; PRAGMA journal_mode=WAL;
            CREATE TABLE Stock(Id INTEGER PRIMARY KEY CHECK(Id=1),
              Available INTEGER NOT NULL CHECK(Available BETWEEN 0 AND 1000),
              Version INTEGER NOT NULL CHECK(Version BETWEEN 0 AND 1000));
            CREATE TABLE Reservations(Request TEXT PRIMARY KEY NOT NULL,
              Quantity INTEGER NOT NULL CHECK(Quantity BETWEEN 1 AND 1000));
            CREATE TABLE Accounts(Id INTEGER PRIMARY KEY, Balance INTEGER NOT NULL CHECK(Balance BETWEEN 0 AND 200));
            INSERT INTO Accounts VALUES(1,100),(2,100);
            CREATE TABLE Noise(Id INTEGER PRIMARY KEY, Payload BLOB NOT NULL);
            """);
        Reset(initial);
    }
    public static SqliteConnection Open(string path)
    {
        var c = new SqliteConnection(new SqliteConnectionStringBuilder {
            DataSource = path, Pooling = false, Cache = SqliteCacheMode.Private, DefaultTimeout = 1 }.ToString());
        c.Open();
        Exec(c, "PRAGMA synchronous=FULL; PRAGMA wal_autocheckpoint=0;");
        return c;
    }
    public static void Exec(SqliteConnection c, string sql, SqliteTransaction? tx = null)
    {
        using var cmd = c.CreateCommand(); cmd.Transaction = tx; cmd.CommandText = sql; cmd.ExecuteNonQuery();
    }
    public static long Scalar(SqliteConnection c, string sql, SqliteTransaction? tx = null)
    {
        using var cmd = c.CreateCommand(); cmd.Transaction = tx; cmd.CommandText = sql;
        return Convert.ToInt64(cmd.ExecuteScalar());
    }
    public static string Engine(SqliteConnection c)
    {
        using var cmd = c.CreateCommand(); cmd.CommandText = "SELECT sqlite_version()";
        return (string)cmd.ExecuteScalar()!;
    }
    public void Reset(int initial)
    {
        if (initial < 0 || initial > 1000) throw new ArgumentOutOfRangeException(nameof(initial));
        using var c = Open(FilePath); using var tx = c.BeginTransaction(deferred: false);
        Exec(c, "DELETE FROM Reservations; DELETE FROM Stock", tx);
        using var cmd = c.CreateCommand(); cmd.Transaction = tx;
        cmd.CommandText = "INSERT INTO Stock VALUES(1,$n,0)"; cmd.Parameters.AddWithValue("$n", initial);
        cmd.ExecuteNonQuery(); tx.Commit();
    }
    public static StockView Read(SqliteConnection c, SqliteTransaction? tx = null)
    {
        using var cmd = c.CreateCommand(); cmd.Transaction = tx;
        cmd.CommandText = "SELECT Available,Version FROM Stock WHERE Id=1";
        using var r = cmd.ExecuteReader();
        if (!r.Read()) throw new InvalidOperationException("Missing stock row.");
        return new StockView(r.GetInt32(0), r.GetInt32(1));
    }
    public static Outcome Reserve(SqliteConnection c, string request, int quantity, StockView expected,
        bool guarded = true, bool failAfterUpdate = false)
    {
        if (string.IsNullOrWhiteSpace(request) || request.Length > 100) throw new ArgumentException("Invalid request.");
        if (quantity < 1 || quantity > 1000) throw new ArgumentOutOfRangeException(nameof(quantity));
        // IMMEDIATE serializes these writes; it cannot make an earlier application read current.
        using var tx = c.BeginTransaction(deferred: false);
        using (var existing = c.CreateCommand())
        {
            existing.Transaction = tx; existing.CommandText = "SELECT Quantity FROM Reservations WHERE Request=$id";
            existing.Parameters.AddWithValue("$id", request); object? value = existing.ExecuteScalar();
            if (value is not null)
            {
                if (Convert.ToInt32(value) != quantity) throw new ArgumentException("Request reused with different quantity.");
                tx.Commit(); return Outcome.Replayed;
            }
        }
        if (expected.Available < quantity) { tx.Commit(); return Outcome.Rejected; }
        using (var update = c.CreateCommand())
        {
            update.Transaction = tx;
            update.CommandText = guarded ? """
                UPDATE Stock SET Available=Available-$q,Version=Version+1
                WHERE Id=1 AND Version=$v AND Available >= $q
                """ : "UPDATE Stock SET Available=$left,Version=Version+1 WHERE Id=1";
            update.Parameters.AddWithValue("$q", quantity); update.Parameters.AddWithValue("$v", expected.Version);
            update.Parameters.AddWithValue("$left", expected.Available - quantity);
            if (update.ExecuteNonQuery() != 1) return Outcome.Conflict; // Disposal rolls back; no receipt is inserted.
        }
        if (failAfterUpdate) throw new InvalidOperationException("Injected failure before receipt.");
        using (var insert = c.CreateCommand())
        {
            insert.Transaction = tx; insert.CommandText = "INSERT INTO Reservations VALUES($id,$q)";
            insert.Parameters.AddWithValue("$id", request); insert.Parameters.AddWithValue("$q", quantity);
            insert.ExecuteNonQuery();
        }
        tx.Commit(); return Outcome.Committed;
    }
    public static long Reserved(SqliteConnection c) => Scalar(c, "SELECT COALESCE(SUM(Quantity),0) FROM Reservations");
    public void Dispose() => Directory.Delete(directory, true); // Only this fixture's generated directory.
}
```

`LessonLab/Schedules.cs`. Schedules logs two real connection-owning tasks with acknowledged gates, then runs a separate held-snapshot trace. The SQL statements are deliberately ordered; no sleep is used to manufacture a race.

```csharp
using System.Collections.Concurrent;

public sealed record RunResult(Outcome First, Outcome Second, int Conflicts, int Retries,
    int Remaining, long Reserved, int Version, string[] Trace);

public static class Schedules
{
    private static TaskCompletionSource<bool> Gate() => new(TaskCreationOptions.RunContinuationsAsynchronously);
    public static async Task<RunResult> Run(string path, int q1, int q2, Strategy strategy)
    {
        if (!Enum.IsDefined(strategy)) throw new ArgumentOutOfRangeException(nameof(strategy));
        var read1 = Gate(); var read2 = Gate(); var written1 = Gate();
        var log = new ConcurrentQueue<string>(); int conflicts = 0, retries = 0;
        var first = Task.Run(async () => {
            using var c = Store.Open(path); var s = Store.Read(c);
            log.Enqueue($"T1 READ available={s.Available} version={s.Version}"); read1.SetResult(true);
            await read2.Task.WaitAsync(TimeSpan.FromSeconds(20));
            var result = Store.Reserve(c, "A", q1, s, strategy != Strategy.Blind);
            log.Enqueue($"T1 {result}"); written1.SetResult(true); return result;
        });
        var second = Task.Run(async () => {
            await read1.Task.WaitAsync(TimeSpan.FromSeconds(20));
            using var c = Store.Open(path); var s = Store.Read(c);
            log.Enqueue($"T2 READ available={s.Available} version={s.Version}"); read2.SetResult(true);
            await written1.Task.WaitAsync(TimeSpan.FromSeconds(20));
            var result = Store.Reserve(c, "B", q2, s, strategy != Strategy.Blind);
            log.Enqueue($"T2 {result}");
            if (result == Outcome.Conflict)
            {
                conflicts++;
                if (strategy == Strategy.Retry)
                {
                    retries++; s = Store.Read(c);
                    log.Enqueue($"T2 READ available={s.Available} version={s.Version}");
                    result = Store.Reserve(c, "B", q2, s);
                    if (result == Outcome.Conflict) conflicts++;
                    log.Enqueue($"T2 {result}");
                }
            }
            return result;
        });
        var results = await Task.WhenAll(first, second).WaitAsync(TimeSpan.FromSeconds(25));
        using var final = Store.Open(path); var stock = Store.Read(final);
        return new RunResult(results[0], results[1], conflicts, retries,
            stock.Available, Store.Reserved(final), stock.Version, log.ToArray());
    }
    public static int Snapshot(string path)
    {
        using var reader = Store.Open(path); using var writer = Store.Open(path);
        using var tx = reader.BeginTransaction(deferred: true);
        var old = Store.Read(reader, tx);
        if (Store.Reserve(writer, "snapshot-writer", 7, Store.Read(writer)) != Outcome.Committed)
            throw new Exception("Writer did not commit.");
        if (Store.Read(reader, tx) != old) throw new Exception("Snapshot changed.");
        int code;
        try { Store.Exec(reader, "UPDATE Stock SET Available=Available-1 WHERE Id=1", tx);
            throw new Exception("Stale snapshot unexpectedly wrote."); }
        catch (Microsoft.Data.Sqlite.SqliteException ex) when (ex.SqliteErrorCode == 5)
        { code = ex.SqliteExtendedErrorCode; }
        tx.Rollback();
        if (Store.Read(reader).Available != 3 || code != 517) throw new Exception("Unexpected pinned-version snapshot result.");
        return code;
    }
}
```

`LessonLab/Crash.cs`. Crash starts only this executable as a child. The child transfers ten between accounts in one transaction and inserts 64 noise blobs of 4096 bytes with a ten-page cache to force dirty-page spill. These artificial blobs exercise WAL presence, not a business workload. It signals before commit or after Commit returns, then waits; the parent kills it, waits for exit and opens a fresh connection. No setup connection remains open at that kill.

```csharp
using System.Diagnostics;
using System.Reflection;
using Microsoft.Data.Sqlite;

public readonly record struct RecoveryResult(long A, long B, long Noise, long WalBytes);

public static class Crash
{
    public static void Child(string path, string point)
    {
        if (point is not ("before" or "after")) throw new ArgumentException("Unknown crash point.");
        using var c = Store.Open(path);
        Store.Exec(c, "PRAGMA cache_size=10; PRAGMA cache_spill=ON;");
        using var tx = c.BeginTransaction(deferred: false);
        Store.Exec(c, "UPDATE Accounts SET Balance=Balance-10 WHERE Id=1; UPDATE Accounts SET Balance=Balance+10 WHERE Id=2;", tx);
        // Force dirty page spill, so the before-commit case really leaves WAL frames.
        using (var insert = c.CreateCommand())
        {
            insert.Transaction = tx; insert.CommandText = "INSERT INTO Noise VALUES($id,zeroblob(4096))";
            var id = insert.Parameters.Add("$id", SqliteType.Integer);
            for (int i = 1; i <= 64; i++) { id.Value = i; insert.ExecuteNonQuery(); }
        }
        if (point == "after") tx.Commit();
        Console.WriteLine("READY " + point); Console.Out.Flush();
        Console.ReadLine(); // Parent kills this process at the acknowledged boundary.
    }
    public static async Task<RecoveryResult> Run(string point)
    {
        using var store = new Store(); // No connection remains open after setup.
        string executable = Environment.ProcessPath ?? throw new Exception("Missing process path.");
        var info = new ProcessStartInfo(executable) {
            RedirectStandardOutput = true, RedirectStandardError = true, RedirectStandardInput = true,
            UseShellExecute = false };
        if (string.Equals(Path.GetFileNameWithoutExtension(executable), "dotnet", StringComparison.OrdinalIgnoreCase))
            info.ArgumentList.Add(Assembly.GetExecutingAssembly().Location);
        foreach (string arg in new[] { "--child", store.FilePath, point }) info.ArgumentList.Add(arg);
        using var child = Process.Start(info) ?? throw new Exception("Could not start child.");
        var errors = child.StandardError.ReadToEndAsync();
        try
        {
            string? signal = await child.StandardOutput.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(20));
            if (signal != "READY " + point) throw new Exception("Child did not acknowledge crash boundary.");
            string wal = store.FilePath + "-wal";
            long size = File.Exists(wal) ? new FileInfo(wal).Length : 0;
            if (size <= 32) throw new Exception("Expected spilled or committed WAL frames.");
            child.Kill(entireProcessTree: true);
            await child.WaitForExitAsync().WaitAsync(TimeSpan.FromSeconds(20));
            using var recovered = Store.Open(store.FilePath);
            return new RecoveryResult(Store.Scalar(recovered, "SELECT Balance FROM Accounts WHERE Id=1"),
                Store.Scalar(recovered, "SELECT Balance FROM Accounts WHERE Id=2"),
                Store.Scalar(recovered, "SELECT COUNT(*) FROM Noise"), size);
        }
        finally
        {
            if (!child.HasExited) child.Kill(entireProcessTree: true);
            await child.WaitForExitAsync();
            string stderr = await errors;
            if (!string.IsNullOrWhiteSpace(stderr)) Console.Error.WriteLine(stderr);
        }
    }
}
```

`LessonLab/Checks.cs`. Checks uses an independent serial admission model for all 225 combinations of initial 0-8 and quantities 1-5. It checks remaining stock, receipt sum, version and decisions, plus stale snapshots, injected rollback, replay, rejection cases and two crash boundaries.

```csharp
public static class Checks
{
    private static void Require(bool ok, string why) { if (!ok) throw new Exception(why); }
    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); } catch (T) { return; }
        throw new Exception($"Expected {typeof(T).Name}.");
    }
    public static async Task Run()
    {
        using var store = new Store();
        using (var c = Store.Open(store.FilePath)) Require(Store.Engine(c) == "3.50.4", "Unexpected engine version.");
        var broken = await Schedules.Run(store.FilePath, 7, 5, Strategy.Blind);
        Require(broken.Remaining == 5 && broken.Reserved == 12, "Lost-update witness missing.");
        int cases = 0;
        for (int initial = 0; initial <= 8; initial++)
            for (int a = 1; a <= 5; a++)
                for (int b = 1; b <= 5; b++)
                {
                    store.Reset(initial); var actual = await Schedules.Run(store.FilePath, a, b, Strategy.Retry);
                    // Independent serial business model: no SQL, version predicate or retry state.
                    int left = initial, total = 0, commits = 0;
                    bool acceptA = a <= left; if (acceptA) { left -= a; total += a; commits++; }
                    bool acceptB = b <= left; if (acceptB) { left -= b; total += b; commits++; }
                    Require(actual.Remaining == left && actual.Reserved == total && actual.Version == commits, "Serial oracle differs.");
                    Require(actual.First == (acceptA ? Outcome.Committed : Outcome.Rejected)
                        && actual.Second == (acceptB ? Outcome.Committed : Outcome.Rejected), "Wrong admission decision.");
                    Require(actual.Remaining + actual.Reserved == initial, "Conservation failed."); cases++;
                }
        store.Reset(10); Require(Schedules.Snapshot(store.FilePath) == 517, "Stale snapshot not rejected.");
        store.Reset(10);
        using (var c = Store.Open(store.FilePath))
        {
            var old = Store.Read(c);
            Throws<InvalidOperationException>(() => Store.Reserve(c, "fail", 7, old, failAfterUpdate: true));
            Require(Store.Read(c) == old && Store.Reserved(c) == 0, "Rollback left half a reservation.");
            Require(Store.Reserve(c, "same", 7, old) == Outcome.Committed, "Initial request failed.");
            Require(Store.Reserve(c, "same", 7, old) == Outcome.Replayed, "Replay consumed stock.");
            Require(Store.Read(c).Available == 3 && Store.Reserved(c) == 7, "Replay changed the result.");
            Throws<ArgumentException>(() => Store.Reserve(c, "same", 6, old));
            Throws<ArgumentException>(() => Store.Reserve(c, " ", 1, old));
            Throws<ArgumentOutOfRangeException>(() => Store.Reserve(c, "bad", 0, old));
            Throws<ArgumentOutOfRangeException>(() => store.Reset(1001));
        }
        store.Reset(1000);
        using (var c = Store.Open(store.FilePath))
        {
            Require(Store.Reserve(c, new string('x', 100), 1000, Store.Read(c)) == Outcome.Committed, "Upper-bound reservation failed.");
            Require(Store.Read(c) == new StockView(0, 1) && Store.Reserved(c) == 1000, "Upper-bound totals differ.");
            Require(Store.Reserve(c, "empty", 1, Store.Read(c)) == Outcome.Rejected, "Empty stock admitted a request.");
            Throws<ArgumentOutOfRangeException>(() => Store.Reserve(c, "large", 1001, Store.Read(c)));
            Throws<ArgumentException>(() => Store.Reserve(c, new string('x', 101), 1, Store.Read(c)));
        }
        var before = await Crash.Run("before"); var after = await Crash.Run("after");
        Require(before.A == 100 && before.B == 100 && before.Noise == 0, "Uncommitted work became visible.");
        Require(after.A == 90 && after.B == 110 && after.Noise == 64, "Acknowledged commit lost.");
        Console.WriteLine($"PASS: {cases} serial-oracle schedules; stale snapshot=517; rollback/replay; 2 crash boundaries.");
    }
}
```

`LessonLab/Experiment.cs`. Experiment varies strategy within a fixed schedule, then changes T2 quantity as a separate case. It counts conflicts/retries and checks the business outcome. No throughput or elapsed-time benchmark is performed.

```csharp
public static class Experiment
{
    public static async Task Run()
    {
        using var store = new Store();
        Console.WriteLine("strategy,q2,remaining,reserved,conflicts,retries,first,second,conserves");
        foreach (int q2 in new[] { 5, 2 })
            foreach (var strategy in Enum.GetValues<Strategy>())
            {
                store.Reset(10); var r = await Schedules.Run(store.FilePath, 7, q2, strategy);
                Console.WriteLine($"{strategy},{q2},{r.Remaining},{r.Reserved},{r.Conflicts},{r.Retries}," +
                    $"{r.First},{r.Second},{r.Remaining + r.Reserved == 10}");
            }
        foreach (string point in new[] { "before", "after" })
        {
            var r = await Crash.Run(point);
            Console.WriteLine($"# crash={point}; A={r.A}; B={r.B}; noise={r.Noise}; walFramesPresent={r.WalBytes > 32}");
        }
    }
}
```

`LessonLab/Program.cs`. Program selects the demo, checks, experiment or internal child mode. The normal commands never take an external database path.

```csharp
if (args.Length == 3 && args[0] == "--child") { Crash.Child(args[1], args[2]); return; }
if (args.Length == 1 && args[0] == "--check") { await Checks.Run(); return; }
if (args.Length == 1 && args[0] == "--experiment") { await Experiment.Run(); return; }
if (args.Length != 0) throw new ArgumentException("Use no argument, --check or --experiment.");
using var store = new Store();
using (var c = Store.Open(store.FilePath)) Console.WriteLine("SQLite " + Store.Engine(c));
foreach (var strategy in new[] { Strategy.Blind, Strategy.Retry })
{
    store.Reset(10); var r = await Schedules.Run(store.FilePath, 7, 5, strategy);
    Console.WriteLine(strategy);
    foreach (string line in r.Trace) Console.WriteLine(line);
    Console.WriteLine($"remaining={r.Remaining}; reserved={r.Reserved}; conserves={r.Remaining + r.Reserved == 10}");
}
```

Expected demo:

```text
SQLite 3.50.4
Blind
T1 READ available=10 version=0
T2 READ available=10 version=0
T1 Committed
T2 Committed
remaining=5; reserved=12; conserves=False
Retry
T1 READ available=10 version=0
T2 READ available=10 version=0
T1 Committed
T2 Conflict
T2 READ available=3 version=1
T2 Rejected
remaining=3; reserved=7; conserves=True
```

Expected `--check`:

```text
PASS: 225 serial-oracle schedules; stale snapshot=517; rollback/replay; 2 crash boundaries.
```

The finite oracle validates these data and the forced T1-before-T2 order, not every interleaving or every database engine. The invariant argument explains why the guarded transaction preserves the one-item rule. Subprocess creation/kill must be available for checks; otherwise use the traces and expected results as the reading route, without claiming to have observed them.

</details>

Defect exercise: after T2 gets Conflict, retry with the same old StockView. Will a second identical attempt authorize the five-unit request? Repair that boundary.

<details>
<summary>Answer</summary>

No. Its version 0 still differs from current version 1. A loop repeating that value can keep conflicting; an unbounded loop has no progress argument. The repair is the Retry branch: end the failed transaction, call Store.Read again, then Store.Reserve with that fresh view. The five-unit case is rejected on stock three; the two-unit case succeeds. If another writer intervenes again, a conflict can still occur and must not be reported as success.

</details>

Pause - 10 minutes away from the screen.

## 6. Controlled schedules and recovery observations

**Experiment · 45 minutes.** Predict the six schedule rows and two crash outcomes, then compare with `--experiment`. **Done when:** you separate an invariant observation from an untested performance or durability claim.

### Hold the schedule fixed

Keep initial stock ten, T1 quantity seven, the same schema/engine and R1,R2,W1,W2 order. Reset between runs. Within each T2-quantity case vary only Blind, Guarded (no retry) or Retry (one fresh attempt). The inputs are synthetic. Quantity five versus two is a separate variation, not a strategy change.

Predict remaining stock, committed receipt total, conflict/retry counts and final decisions for all six rows.

<details>
<summary>Answer</summary>

| T2 quantity | Strategy | Remaining | Reserved | Conflicts | Retries | T2 result | Conserves ten? |
|---|---|---|---|---|---|---|---|
| 5 | Blind | 5 | 12 | 0 | 0 | Committed | No |
| 5 | Guarded | 3 | 7 | 1 | 0 | Conflict | Yes |
| 5 | Retry | 3 | 7 | 1 | 1 | Rejected | Yes |
| 2 | Blind | 8 | 9 | 0 | 0 | Committed | No |
| 2 | Guarded | 3 | 7 | 1 | 0 | Conflict | Yes |
| 2 | Retry | 1 | 9 | 1 | 1 | Committed | Yes |

T1 commits in every row. The blind two-unit case still loses its decrement despite not overselling: 8+9=17. Guarded without retry preserves the invariant but leaves T2 unresolved even when stock is sufficient. Retry can change both state and decision; fewer conflicts alone is not better if the business result is wrong.

</details>

### A process-crash experiment

Keep both account balances at 100 and transfer ten within one transaction. The only failure-position change is the child's acknowledged before/after commit boundary. Cache/spill settings and 64 noise rows are identical. Signal receipt ensures the intended boundary was reached; the parent then kills only that child and reopens after exit. Autocheckpoint is disabled to keep WAL evidence available before the kill.

Predict both balances, noise count and whether a WAL containing more than its header exists. Does preserving the total balance alone prove atomic recovery?

<details>
<summary>Answer</summary>

| Kill boundary | A after reopening | B after reopening | Noise rows | WAL bytes before kill |
|---|---|---|---|---|
| Before commit | 100 | 100 | 0 | More than header; dirty spill present |
| After Commit returned | 90 | 110 | 64 | More than header; committed frames present |

Both totals equal 200, so the sum alone cannot distinguish old from new state. Check exact balances and noise count. Half-applied (90,100) or (100,110) would fail. The code checks file presence/size but lets SQLite validate/recover frames; exact WAL byte counts can vary and are not golden output.

</details>

### Observed scope and research limits

The supplied six CSV rows and both recovery states were observed when authoring with the pinned Linux runtime. Checks also reproduced error 517. This is deterministic schedule evidence, not a random race benchmark or proof across all interleavings. Gates select the schedule and process signals select failure boundaries; they do not measure fairness, lock contention, throughput or p99.

Assumptions are private caches, one item, no concurrent reset/restock, every correct writer using the rule, a local filesystem and an OS that remains running. Predictions are the tables above. Observations are SQL outcomes, traces, error code and WAL presence. The inference is that these mechanisms reproduce the modeled stale-read and committed-boundary behavior here. Source supports the mechanism; the finite runs support these cases.

Power loss, device cache lies, torn writes, arbitrary kill points, checkpoint crashes and SQL Server execution remain untested. FULL requests synchronization through SQLite/VFS; a process kill does not remove OS cache. Do not relabel this as a physical durability certification or universal contention result.

Pause - 10 minutes away from the screen.

## 7. Transfer: commit succeeds but the response is lost

**Transfer · 35 minutes.** Change the context from two competing orders to redelivery of the same request. **Done when:** a matching retry creates one durable receipt and one decrement, while mismatched data fails.

An HTTP response is lost after reservation R-42 for seven commits. The client retries R-42. A HashSet in one process disappears on restart and cannot coordinate multiple instances. Design persistent identity and an atomic boundary, then test a new connection receiving that same request. What changes if the retry uses quantity six?

<details>
<summary>Answer - replay design and complete program</summary>

Use the request ID as the unique receipt key and persist quantity with it. Check that receipt inside the write transaction before consuming stock. A matching receipt returns Replayed, even if only three stock remain; a different quantity under the same identity is an error. Decrement and insertion share one commit, so failure cannot leave a consumed stock value without its receipt.

In a separate copy of the lab, replace Program.cs with this complete program and keep the other files. Run the same no-restore command after restore. Ignoring the first result models a lost reply; no real HTTP transport failure is injected.

```csharp
using var store = new Store(10);
using (var first = Store.Open(store.FilePath))
{
    var result = Store.Reserve(first, "R-42", 7, Store.Read(first));
    if (result != Outcome.Committed) throw new Exception("Initial request failed.");
    // Pretend its HTTP response never reached the caller.
}
using (var retry = Store.Open(store.FilePath))
{
    if (Store.Reserve(retry, "R-42", 7, Store.Read(retry)) != Outcome.Replayed)
        throw new Exception("Matching retry was not recognized.");
    bool mismatch = false;
    try { Store.Reserve(retry, "R-42", 6, Store.Read(retry)); }
    catch (ArgumentException) { mismatch = true; }
    if (!mismatch) throw new Exception("Changed payload was accepted.");
    if (Store.Read(retry).Available != 3 || Store.Reserved(retry) != 7
        || Store.Scalar(retry, "SELECT COUNT(*) FROM Reservations") != 1)
        throw new Exception("Duplicate business effect.");
}
Console.WriteLine("PASS: R-42 replayed; remaining=3; reserved=7; receipts=1; mismatch rejected.");
```

Expected: `PASS: R-42 replayed; remaining=3; reserved=7; receipts=1; mismatch rejected.` Identity/payload comparison is inside the same writer transaction, and the unique key backs the identity. This is idempotency for successful one-database reservations, not exactly-once HTTP delivery or a distributed payment transaction. Rejected requests are not stored as receipts here, so repeating a rejection is not a persisted result policy. The fixture deletes its database when it finishes; a service must retain the database across restarts. For multiple items or tenants, persist and compare those fields as part of the request payload too. Do not delete receipts without defining a retention/reuse rule.

</details>

## 8. Synthesis and retrieval

**Synthesis · 45 minutes.** Reconstruct the boundaries without the page and write a decision plus a falsifying test. **Done when:** your claim identifies the business rule, evidence, failure model and remaining uncertainty.

1. Why are atomicity and a nonnegative CHECK insufficient for the blind schedule?

<details>
<summary>Answer</summary>

Each decrement/receipt pair can commit atomically while using old application stock. The CHECK inspects one stored value, not the sum of promises. The result 5+12 violates A+S=10. Correct placement of the read/guard and the transaction preserving both changes are separate requirements.

</details>

2. Why does repeating a write in an old WAL read transaction fail to refresh its decision?

<details>
<summary>Answer</summary>

Its read end mark remains fixed until the transaction ends. After another writer commits, promotion can return BUSY_SNAPSHOT. Roll back/end the old transaction and redo the business decision from a fresh read. A bounded retry may still conflict; never count that as a committed reservation.

</details>

3. What do the two crash observations establish, and what do they leave open?

<details>
<summary>Answer</summary>

At the selected process-kill boundaries, fresh SQL reads give old (100,100,0 noise) or committed (90,110,64 noise) state with WAL present before the kill. They support these atomic visibility/recovery cases. They do not certify power-loss durability, arbitrary corruption, all kill offsets, checkpoint crashes, storage flush behavior or another engine.

</details>

4. Propose a production validation that could overturn a guarded-reservation recommendation.

<details>
<summary>Answer</summary>

Use the target engine and representative request conflicts, retries, multi-item rules and delivery identities. Check invariant/receipt agreement first, then measure blocking, throughput and unresolved outcomes with bounded retry. A high conflict rate, unacceptable writer-slot time, an external payment effect outside the atomic boundary or a multi-row invariant not protected by this predicate can require a different design. SQL Server isolation and error handling must be verified there; our local counters do not select them.

</details>

## Sources and reuse

- SQLite [Isolation](https://www.sqlite.org/isolation.html), [WAL 2.1-2.3](https://www.sqlite.org/wal.html), [transactions 2.1-2.2](https://www.sqlite.org/lang_transaction.html) and [synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous) support the stated visibility and recovery boundaries.
- SQLite source at commit `8ed5e7365e6f12f427910188bbf6b254daad2ef6`, tag version-3.50.4; bounded links are in section 4. [Public-domain notice](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/LICENSE.md). GitHub mirror hashes differ from sqlite_source_id's Fossil identifier; matching the engine version does not turn a timing into a source claim.
- [Microsoft.Data.Sqlite transactions](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/transactions), deferred transaction section, supports the provider bridge. [SQL Server transaction guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17), ACID, concurrency control and row-versioning isolation, supports the separate application discussion. The T-SQL fragment is unexecuted.
- Original lesson prose is CC BY 4.0 and original teaching C# is MIT, with the license in the ZIP. SQLite source is analyzed, not copied. Packages retain their own licenses.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 05 - Indexes and query plans](../2026-10-09-index-query-plans/lesson.md) - Separate access cost, correctness and the pagination snapshot assumption.
- [Lesson 03 - Shortest paths](../2026-10-07-shortest-paths/lesson.md) - Recall checking stale evidence against current state.
- [C# lab guide](../../labs/transactions-recovery/dotnet/README.md) - Pinned setup, schedules, process-crash checks and limitations.

---

[← Previous: Lesson 05 - Indexes and query plans: when a seek still does much work](../2026-10-09-index-query-plans/lesson.md) · [All lessons](../../README.md) · [Next: Lesson 07 - Sampling uncertainty: more records need not mean more evidence →](../2026-10-11-sampling-uncertainty/lesson.md)
<!-- LESSON_NAVIGATION_END -->
