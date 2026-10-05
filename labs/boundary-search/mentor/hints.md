# Mentor hints — disclose progressively on request/after an attempt

Do not open this during an independent assessment. Record each hint actually used.

1. Conceptual: name which timestamps belong on the left and right of each boundary. Draw a half-open interval; empty windows are valid.
2. Structural: count a window by subtracting two insertion positions, without enumerating the window. Which endpoint excludes equality?
3. Implementation-specific: ask `lower_bound` for `start` and `end`; validate reversed endpoints before subtracting. Then try duplicate endpoints and an empty list.

A full solution is in `solution.py`. Only reveal after an attempt, explicit request, or worked review. A correct solution copied from this folder cannot count as independent evidence.
