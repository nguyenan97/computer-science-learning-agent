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
