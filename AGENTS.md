# Working in this repository

Use the repository [cs-daily-deep-study skill](skills/cs-daily-deep-study/SKILL.md) when
the learner requests today's/next lesson, “bài hôm nay”, research, recall or tutoring.
Read its single [lesson spec](references/lesson-spec.md) before authoring.
Codex discovery is provided by `.agents/skills/cs-daily-deep-study`, a symlink to the
canonical skill; edit the canonical files rather than making a second copy.

The learner uses Codex, reads public GitHub Pages lessons and requests each day
manually. Reuse the .NET/data context and full-day research preference. The goal is
progressively deeper graduate-level reasoning, without claims of degrees or mastery.
Do not create learner state, progress logs or scheduled runs. Public catalog dates
drive recall even if the learner skips a day.

Keep English and Vietnamese lessons complete, with answers immediately available.
Use C# by default and T-SQL for data work; an essential Python ecosystem needs a
concrete bridge to C#. Keep generic lessons/labs public and personal content untracked.

In a fresh session without the SDK or Python dependencies, run
`bash scripts/setup_environment.sh` before validation. After adding catalog content, run `python scripts/add_lesson_navigation.py` and
`work/venv/bin/python scripts/check_all.py` after setup. The catalog is the source for navigation, public build,
ZIP downloads and runnable labs. Use `work/` for intermediate checks.

A daily-lesson request authorizes a PR. Merge or push to main only when explicitly
instructed. A successful local check does not establish a live Pages deployment.
For environment setup and verification, see [Maintaining](docs/maintaining.md).
