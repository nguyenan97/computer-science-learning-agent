using System.Globalization;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args.Length == 0) Experiment.Demo();
else if (args.SequenceEqual(new[] { "--check" })) Checks.Run();
else if (args.SequenceEqual(new[] { "--experiment" })) Experiment.Run();
else throw new ArgumentException("Use no arguments, --check or --experiment.");
