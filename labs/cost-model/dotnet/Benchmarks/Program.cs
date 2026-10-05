using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Running;
using CostModel;

BenchmarkSwitcher.FromAssembly(typeof(DedupeBenchmarks).Assembly).Run(args);

[MemoryDiagnoser]
public class DedupeBenchmarks
{
    [Params(128, 512, 2048)] public int N { get; set; }
    [Params(10, 100)] public int UniquePercent { get; set; }
    private string[] values = [];

    [GlobalSetup]
    public void Setup() => values = Dataset.Make(N, Math.Max(1, N * UniquePercent / 100));

    [Benchmark(Baseline = true)] public List<string> Scan() => Deduplication.Scan(values);
    [Benchmark] public List<string> Hash() => Deduplication.Hash(values);
}
