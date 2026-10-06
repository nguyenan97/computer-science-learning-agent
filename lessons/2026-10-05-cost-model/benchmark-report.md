# Lesson 01 - measured benchmark / Benchmark đã đo

Agent execution on 2026-10-05; not learner work or learning evidence.
ShortRun: 12 cases, one launch, three warmup and three measurement iterations.
Process priority elevation was denied; intervals are wide on this cloud host.
Use these results to inspect the time/allocation trade-off, not to promise service speed.
Input generation is outside measurement; each operation allocates new output/table.
Allocated includes those allocations, excluding the prebuilt input; it is not peak memory.

Số đo agent ngày 05/10/2026; không phải bài làm hay bằng chứng học tập của người học.
12 case ShortRun, một launch, ba warmup và ba measurement iteration mỗi case.
Không nâng được priority; khoảng tin cậy rộng. Dùng để đọc trade-off thời gian/allocation,
không dùng làm cam kết service. Allocated gồm output/table mới, không gồm input tạo sẵn,
không phải peak memory. Chưa chạy workload production hay bộ test upstream.

Command / Lệnh (from `labs/cost-model/dotnet`):

```bash
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

```

BenchmarkDotNet v0.15.8, Linux Debian GNU/Linux 13 (trixie)
INTEL XEON PLATINUM 8573C 2.30GHz, 1 CPU, 5 logical and 5 physical cores
.NET SDK 10.0.401
  [Host]   : .NET 10.0.12 (10.0.12, 10.0.1226.42308), X64 RyuJIT x86-64-v4
  ShortRun : .NET 10.0.12 (10.0.12, 10.0.1226.42308), X64 RyuJIT x86-64-v4

Job=ShortRun  IterationCount=3  LaunchCount=1  
WarmupCount=3  

```
| Method | N    | UniquePercent | Mean          | Error        | StdDev      | Ratio | RatioSD | Gen0   | Gen1   | Allocated | Alloc Ratio |
|------- |----- |-------------- |--------------:|-------------:|------------:|------:|--------:|-------:|-------:|----------:|------------:|
| **Scan**   | **128**  | **10**            |      **6.107 μs** |    **16.110 μs** |   **0.8830 μs** |  **1.01** |    **0.18** |      **-** |      **-** |     **328 B** |        **1.00** |
| Hash   | 128  | 10            |      3.237 μs |     6.443 μs |   0.3532 μs |  0.54 |    0.08 | 0.0076 |      - |    1120 B |        3.41 |
|        |      |               |               |              |             |       |         |        |        |           |             |
| **Scan**   | **128**  | **100**           |     **47.783 μs** |    **29.580 μs** |   **1.6214 μs** |  **1.00** |    **0.04** |      **-** |      **-** |    **2192 B** |        **1.00** |
| Hash   | 128  | 100           |      5.011 μs |     7.224 μs |   0.3960 μs |  0.10 |    0.01 | 0.0687 |      - |    9568 B |        4.36 |
|        |      |               |               |              |             |       |         |        |        |           |             |
| **Scan**   | **512**  | **10**            |     **78.994 μs** |   **100.111 μs** |   **5.4874 μs** |  **1.00** |    **0.08** |      **-** |      **-** |    **1144 B** |        **1.00** |
| Hash   | 512  | 10            |     10.939 μs |    24.178 μs |   1.3253 μs |  0.14 |    0.02 | 0.0305 |      - |    4560 B |        3.99 |
|        |      |               |               |              |             |       |         |        |        |           |             |
| **Scan**   | **512**  | **100**           |    **922.355 μs** | **2,261.779 μs** | **123.9758 μs** |  **1.01** |    **0.17** |      **-** |      **-** |    **8384 B** |        **1.00** |
| Hash   | 512  | 100           |     22.218 μs |    19.147 μs |   1.0495 μs |  0.02 |    0.00 | 0.3052 |      - |   42896 B |        5.12 |
|        |      |               |               |              |             |       |         |        |        |           |             |
| **Scan**   | **2048** | **10**            |  **1,780.935 μs** | **5,972.646 μs** | **327.3809 μs** |  **1.03** |    **0.25** |      **-** |      **-** |    **4264 B** |        **1.00** |
| Hash   | 2048 | 10            |     47.224 μs |    13.203 μs |   0.7237 μs |  0.03 |    0.00 | 0.1221 |      - |   20344 B |        4.77 |
|        |      |               |               |              |             |       |         |        |        |           |             |
| **Scan**   | **2048** | **100**           | **10,856.396 μs** | **7,586.749 μs** | **415.8553 μs** | **1.001** |    **0.05** |      **-** |      **-** |   **33008 B** |        **1.00** |
| Hash   | 2048 | 100           |     92.221 μs |    59.240 μs |   3.2471 μs | 0.009 |    0.00 | 1.3428 | 0.3662 |  187224 B |        5.67 |
