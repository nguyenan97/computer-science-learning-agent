# Lesson 02 lab - Boundary search in C#

[Tiếng Việt](README.vi.md) · [English lesson](../../../lessons/boundary-search/lesson.md)

This standalone console lab implements a first-duplicate lower boundary and counts
sorted integer timestamps in `[start,end)`. Full worked code is in
[LessonLab/BoundarySearch.cs](LessonLab/BoundarySearch.cs); tests are in
[LessonLab/Checks.cs](LessonLab/Checks.cs). Reimplement it in a copy for practice,
then compare your reasoning with the solution whenever useful.

## Run

Install .NET SDK **10.0.401** (target **net10.0**), then open a terminal in this
`dotnet` folder, which contains `global.json`. The lab has no third-party packages,
benchmark dependency, Python dependency or SQL Server requirement.

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --observe
```

For a clone, the working directory is `labs/boundary-search/dotnet`. For the
[lab ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/boundary-search/dotnet-lab.zip),
extract it and locate the folder containing `global.json` before running these commands.
The default run prints:

```text
Array.BinarySearch(30) found a match: True
LowerBound(30): 3
List.BinarySearch(11): -3; insertion position: 2
Count [10, 30): 3
Count [30, 30): 0
Count [11, 39): 3
```

`--check` prints **17/17 checks passed** and exits 0 when every check succeeds;
any failed check exits 1. It covers empty data, first duplicates, missing targets,
outside ranges, negative/extreme keys, endpoint semantics, reversed bounds, input
preservation, null input, .NET's negative-result encoding, a virtual large array
and small cases compared against a scanning oracle. The virtual array requires only
logarithmically many indexed reads; it does not allocate `int.MaxValue` entries.

## What to explain

`Array.BinarySearch` and `List<T>.BinarySearch` return **a** matching position when
found, without promising the first duplicate. An absent target returns the bitwise
complement of its insertion position; decode a negative result with `~result`,
not `-result`. The custom method moves `hi` on equality to return the first boundary.
Its safe midpoint is `lo + (hi - lo) / 2`; it never adds two potentially large indices.

The timestamp keys are `long` and sorted ascending. Both searches assume constant
time indexed access and comparisons. Checking sortedness, sorting and updating the
array are separate work. SQL examples live in the lesson and are not executed by
this console lab. Running reference checks verifies code behavior; practice and
reporting results are optional.

`--observe` prints how many indexed reads a lower boundary makes for 8, 1,024 and
65,536 elements, then searches event records by a timestamp key. It counts element
reads, not CPU time.
