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
