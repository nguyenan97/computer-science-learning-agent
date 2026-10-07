# Lesson 06 authoring and verification review

## Selection and scope

Main at selection was `a620f3f8049b745338914732d28d8c86992ec8a0`, with
Lesson 05 dated 2026-10-09. The next catalog day is 2026-10-10.
Before editing the catalog, `python scripts/daily_plan.py --on 2026-10-10`
selected `data.transactions`, Transactions, concurrency and recovery, on the
build profile. Its published prerequisite is `data.indexes`. Recall selects
Lesson 05's seek-work mechanism and Lesson 03's lazy-queue stale entry/bounds.
No answers, scores, attendance or personal progress are recorded.

Full EN/VI lessons use the existing C#/SQLite environment to concentrate on
transaction boundaries rather than server setup. They introduce ACID, schedules,
application versions, snapshots, guarded updates, commit/checkpoint and recovery.
Eight activity sections have tasks, minutes and completion conditions, with the
profile's four rest blocks in place and a setup timebox/reading-only route.
Each page has 19 individually accessible, immediate, default-closed answer panels.
The catalog adds three bilingual recall entries, the runnable lab/archive and
related links; navigation/coverage are generated through the repository script.

## Sources read and limits of attribution

SQLite tag version-3.50.4 at immutable GitHub commit
`8ed5e7365e6f12f427910188bbf6b254daad2ef6`, matching the tested engine version:

- `src/wal.c`, 15-133: frame/commit/end-mark model and the wal-index's role in
  avoiding per-page linear scans of potentially multi-megabyte WAL files.
- 3664-3725: `sqlite3WalBeginWriteTransaction`, single writer lock and stale
  header comparison returning SQLITE_BUSY_SNAPSHOT.
- 4138-4188: `walFrames`, commit database-size marking and configured sync work.
- 1481-1528: `walIndexRecover`, decoded frames and last committed header;
  1000-1045: `walDecodeFrame`, salts/page/checksum validation.

Official SQLite Isolation, separate-connection/WAL examples; WAL 2.1-2.3;
transaction 2.1-2.2; and synchronous pragma were retrieved and read. The
Microsoft.Data.Sqlite deferred-transaction section was read for the provider
bridge. SQL Server's transaction locking/row-versioning guide was read in the
ACID, concurrency-control and RCSI/SNAPSHOT sections. The SQL Server application
and T-SQL fragment remain design discussion, not an executed SQL Server result.
Source is linked and analyzed, not copied; original C# is MIT and prose CC BY 4.0.
SQLite's public-domain notice and third-party package terms remain applicable.

The source verifies writer exclusion, stale-snapshot rejection and committed
boundary handling, not the endpoint's business semantics or every pager/VFS path.
Application Version is distinct from WAL frame position and SQL Server rowversion.
Keeping transactions short and validating an external stale proposal are stated
as design inference. A derived wal-index is not the durable source of truth.

## Content and code review

The lost update deliberately crosses database transaction boundaries: two
application reads precede two serialized atomic write transactions. It is not
presented as SQLite allowing a held stale snapshot to promote silently. The
separate held-snapshot trace reproduces rejection instead. The one-item proof
states no restock/cancellation/concurrent reset and requires all correct writers
follow the rule; it is not a theorem for arbitrary multi-row invariants.

A+S=I and nonnegative stock are checked with complete receipt/decrement atomicity.
Guarded UPDATE tests both current stock and expected version. A zero-row write
does not insert a receipt; a retry re-reads after ending the failed transaction.
Existing request identity is checked inside IMMEDIATE before admission, including
payload mismatch, so successful replay does not decrement again. The transfer
uses a new connection and intentionally ignores the first result to model a lost
reply; no HTTP transport fault is claimed. Rejected outcomes are not durably
recorded. A real multi-item/tenant endpoint needs those fields in its identity
payload and a retention policy. The temporary fixture is removed at completion;
a service must retain its database across restarts.

Each client owns its own private-cache connection and gates select R1,R2,W1,W2.
No sleeps manufacture the race; tasks overlap in lifetime, not in SQLite writer
ownership. Retry is bounded to one fresh attempt under this chosen two-client
schedule. Conflict counters include a second failed attempt if it occurs.

Review corrected the draft's provider timeout: zero means unlimited busy waiting,
so the final configuration is one second. Warnings-as-errors review also removed
a nullable ProcessPath dereference. Initial stock/quantity/request bounds and
1000-unit boundary cases are checked. Final sources and on-page fences agree.

The parent launches only its own executable, waits for a before/after commit
signal and kills only that child. All setup connections are closed before the
kill. The child transfers ten and uses 64 artificial 4096-byte blobs plus a
ten-page cache to force WAL spill; the before-commit case has actual WAL bytes,
not merely unflushed application memory. Fresh SQL reads check exact balances
and noise count, not just the sum of balances or file length. WAL validation and
recovery are performed by SQLite, not a custom binary parser.

## Local verification

- `python scripts/check_all.py`: 48 repository tests; planner/catalog/parity,
  generated navigation/coverage and links. All six labs execute from temporary
  source copies and extracted ZIPs; archived projects build successfully. New
  project: zero warnings/errors with locked dependency restore.
- New lab: 225 two-client schedules compared with an independent serial business
  admission model (no SQL/version/retry logic in the oracle). Decisions, remaining
  stock, receipt sum, versions and conservation agree. Additional checks cover
  the blind witness, error 517, injected rollback, replay/payload mismatch,
  validation/upper bounds and two process-crash boundaries.
- Seven C# fences are identical EN/VI; six match files byte-for-byte. SDK, project,
  lock and source fences extracted directly from the page compile and run demo,
  checks and experiment, including their child-process modes.
- The transfer Program fence runs and prints the stated one-receipt/remaining=3
  result. The defect variant retaining old StockView was executed: both retry
  cases still conflict, with two conflict attempts and one retry, as explained.
- All six CSV rows and two recovery comments match predictions. Before-commit
  reopening returns balances 100/100 and noise 0; after-commit returns 90/110
  and noise 64. Both cases have WAL data beyond the header before killing.
- ZIP CRC/inventory/bytes match all 12 lab source/setup/guide/license files;
  no bin/obj, package binaries or database. Required checks build/run the archive.
- Chromium: 12 EN/VI lesson pages, 12 language switches, 12 previous/next clicks,
  289 internal document links and 43 assets; no runtime errors or outside requests.
- Desktop 1440px/mobile 390px: all 19 panels per language start closed and toggle
  both ways; six lab fences and one transfer fence render. Mobile language and
  previous/next round trips work, with no document overflow. Opened answer tables
  fit the viewport and allow horizontal scrolling. Vietnamese mobile table layout
  was visually inspected.
- EN/VI meaning, proofs, source boundaries, commands, outputs and qualifications
  were reviewed. Typography, parity, catalog validation and git diff --check pass.

## Unverified scope and publication

These are deterministic schedule and process-crash results, not measured
throughput/latency, contention/fairness distributions or all interleavings.
The OS remains alive: power loss, device cache/flush behavior, torn writes,
arbitrary kill points, checkpoint crashes and all VFS implementations are not
tested. FULL requests SQLite/VFS synchronization but the experiment does not
certify physical storage durability. SQL Server/T-SQL execution, production
multi-item isolation, authentication, external payment effects and actual HTTP
transport failures remain unverified. Candidate browser/ZIP checks are local;
Pages is not claimed live before merge. PR CI and its individual diagnostic
steps are reported after completion in the PR and response.
