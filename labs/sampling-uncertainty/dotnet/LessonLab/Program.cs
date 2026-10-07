using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args.Length == 1 && args[0] == "--check") { Checks.Run(); return; }
if (args.Length == 1 && args[0] == "--experiment") { Experiment.Run(); return; }
if (args.Length != 0) throw new ArgumentException("Use no argument, --check or --experiment.");
Console.WriteLine("n,k,estimate,wilson_low,wilson_high");
int count = 0, n = 0;
foreach (int observation in new[] { 1, 0, 1, 0, 0 })
{
    count += observation; n++; var ci = Stats.Wilson(count, n);
    Console.WriteLine($"{n},{count},{(double)count / n:F4},{ci.Low:F4},{ci.High:F4}");
}
