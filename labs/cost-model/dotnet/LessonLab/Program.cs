using CostModel;

if (args.Contains("--check")) { Checks.Run(); return; }

string[] example = ["B2", "A1", "B2", "C3", "A1"];
Console.WriteLine($"Stable result: {string.Join(", ", Deduplication.Hash(example))}");
Console.WriteLine($"Example scan comparisons: {Deduplication.CountScan(example).Comparisons}");
Console.WriteLine("n,scan_equality_comparisons,hash_add_calls (not hash-table work)");
foreach (int n in new[] { 128, 256, 512 })
{
    string[] values = Dataset.Make(n, n);
    var hashed = Deduplication.CountHash(values);
    Console.WriteLine($"{n},{Deduplication.CountScan(values).Comparisons},{hashed.AddCalls}");
}
Console.WriteLine($"128 identical IDs: {Deduplication.CountScan(Dataset.Make(128, 1)).Comparisons} scan comparisons");
Console.WriteLine($"Duplicates: {string.Join(", ", Deduplication.DuplicateSummary(example).Select(x => $"{x.Id}={x.Count}"))}");
Console.WriteLine("Agent/reference execution is not learner evidence.");
