# Mentor hints - read whenever useful

The full solution and these hints are always available. For an optional independent
attempt, predict the partitions before checking the worked answer.

1. Conceptual: name which timestamps belong on the left and right of each boundary. Draw a half-open interval; empty windows are valid.
2. Structural: count a window by subtracting two insertion positions, without enumerating the window. Which endpoint excludes equality?
3. Implementation-specific: ask `lower_bound` for `start` and `end`; validate reversed endpoints before subtracting. Then try duplicate endpoints and an empty list.

A full Python solution is in `solution.py`; the C# equivalent is in
`../dotnet/LessonLab/BoundarySearch.cs`. An unchanged solution verifies reference
behavior rather than an independent implementation.
