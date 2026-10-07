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
