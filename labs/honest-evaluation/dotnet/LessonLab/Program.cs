using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else if (args is ["--transfer"]) Transfer.Run();
else if (args.Length == 0)
{
    var sets = Data.Split();
    Evaluation.Disjoint(sets);
    var candidates = Evaluation.Candidates(sets[0]);
    var winner = Evaluation.Select(candidates, sets[1], 4);
    Console.WriteLine($"Selected on validation: {winner.Name}, threshold={winner.Threshold}");
    foreach (var rule in candidates)
    {
        var m = Evaluation.Count(sets[2], rule);
        string precision = m.Precision?.ToString("F3") ?? "undefined";
        string recall = m.Recall?.ToString("F3") ?? "undefined";
        Console.WriteLine($"{rule.Name}: t={rule.Threshold} TP={m.TP} FP={m.FP} FN={m.FN} TN={m.TN} accuracy={m.Accuracy:F3} precision={precision} recall={recall} cost={m.Cost(4)}");
    }
}
else throw new ArgumentException("Use no args, --check, --experiment or --transfer.");
