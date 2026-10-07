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
