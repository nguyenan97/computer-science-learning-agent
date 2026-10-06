using BoundarySearchLab;

if (args.Length == 1 && args[0] == "--check")
    return Checks.Run();
if (args.Length == 1 && args[0] == "--observe")
    return Observe.Run();
if (args.Length != 0)
{
    Console.Error.WriteLine("Usage: LessonLab [--check | --observe]");
    return 2;
}

long[] values = [10, 10, 20, 30, 30, 40];
int match = Array.BinarySearch(values, 30L);
Console.WriteLine($"Array.BinarySearch(30) found a match: {values[match] == 30}");
Console.WriteLine($"LowerBound(30): {BoundarySearch.LowerBound(values, 30)}");

List<long> list = [.. values];
int result = list.BinarySearch(11L);
int position = result >= 0 ? result : ~result;
Console.WriteLine($"List.BinarySearch(11): {result}; insertion position: {position}");
Console.WriteLine($"Count [10, 30): {BoundarySearch.CountWindow(values, 10, 30)}");
Console.WriteLine($"Count [30, 30): {BoundarySearch.CountWindow(values, 30, 30)}");
Console.WriteLine($"Count [11, 39): {BoundarySearch.CountWindow(values, 11, 39)}");
return 0;
