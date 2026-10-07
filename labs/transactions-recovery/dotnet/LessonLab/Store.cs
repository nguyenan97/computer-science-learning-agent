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
