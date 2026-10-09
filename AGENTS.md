# Working in this repository

Use the canonical [cs-daily-deep-study skill](skills/cs-daily-deep-study/SKILL.md)
for today's/next lesson, “bài hôm nay”, paper study and tutoring. Read its single
[lesson spec](references/lesson-spec.md). `.agents/skills/cs-daily-deep-study`
links to that same skill; never maintain a second copy.

The learner uses Codex cloud and self-studies from IUH master (2020) and doctoral
(2022) course-name outlines. The planner counts public lesson artifacts, rather than
learner knowledge. Save no answers, scores, progress logs or automatic schedules.

Run `python scripts/daily_plan.py --next` for the next lesson, before editing the
catalog; use `--on YYYY-MM-DD` for an explicit date, or no date flag for today.
The date is the learner's study
date in Asia/Ho_Chi_Minh, or an explicitly requested date. The public inventory selects
an uncovered master topic with covered prerequisites before doctoral topics. Reuse
an existing same-day lesson. The budget and build/paper blocks live in the study profile.

Write complete EN/VI explanations and immediately accessible worked answers.
Use C# by default, T-SQL for data, and a C# bridge for essential Python ecosystems.

After editing the catalog, run `python scripts/add_lesson_navigation.py` to regenerate
navigation and coverage. Run `python scripts/check_all.py`; this command automatically
runs `scripts/setup_environment.sh` when a fresh session lacks Python dependencies or
.NET. Build labs only in temporary copies. Use `work/` for intermediate files.

“Bài hôm nay” authorizes public files and a PR. The learner normally merges; an explicit
request to merge authorizes that action for the current work. Verify CI and Pages.
Original prose uses CC BY 4.0, original code MIT; preserve third-party attribution.
See [Maintaining](docs/maintaining.md) for implementation and verification commands.
