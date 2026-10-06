# Maintaining the IUH self-study agent

The public inventory maps factual course names from IUH master (2020) and doctoral
(October 2022) outlines to original study objectives. No personal answers or results
are saved. Catalog coverage describes published artifacts, not knowledge or degrees.

## Codex cloud and environment

[AGENTS.md](../AGENTS.md) points to the canonical
[skill](../skills/cs-daily-deep-study/SKILL.md), also discovered through its
`.agents/skills/cs-daily-deep-study` symlink. The [lesson spec](../references/lesson-spec.md)
owns authoring; [study profile](../references/study-profile.json) owns the calendar,
budget and build/paper block schedules.

From a fresh checkout with Python 3.12, run:

```bash
python scripts/check_all.py
```

The command bootstraps a venv and the pinned SDK through `setup_environment.sh` if
needed, then checks the repo with the prepared interpreter. Installs stay under
ignored `work/`. This makes pre-push lab checks usable in fresh Codex sessions without
assuming the cloud image already includes dotnet. CI provisions its own dependencies.
The script is repository automation; it does not modify the external cloud environment
configuration. If configuring that environment's setup command, use
`bash scripts/setup_environment.sh` from the repository root.

## Four-step daily loop

1. The learner manually requests “bài hôm nay”, optionally naming a date or topic.
2. Run `python scripts/daily_plan.py`. It returns the eligible topic, dated recall,
   budget and block schedule. Explicit dates use `--on YYYY-MM-DD`; otherwise the
   date is Asia/Ho_Chi_Minh. Repeat a request for the same day by returning its page.
3. Author complete EN/VI pages and needed labs, regenerate and check them, then open
   a PR. The learner normally merges; an explicit merge instruction authorizes the
   agent to merge after validation and verify Pages.
4. Study the page with its opening recall and immediately available worked answers.
   No submission, attendance or progress log is required.

Master topics precede doctoral topics. Published `topic_ids` satisfy prerequisite
coverage; array order in `topics.json` breaks ties among eligible topics. When all
planned topics have artifacts, propose a new research question rather than a degree
or mastery claim. Course-level names include electives for optional breadth.

## Adding a lesson

Add full pages under `lessons/<id>/lesson.md` and `vi/lessons/<id>/lesson.md`, shared
labs and one catalog entry. Its `date` is the Vietnamese study date; use that date in
new IDs. Required metadata includes `topic_ids`, `day_type` (`build` or `paper`),
bilingual titles, declared public files, related reading and three bilingual recall
question/answer objects. Topic IDs must exist and must actually be taught on the page.

C# is the default lab and T-SQL covers data work. Essential Python ecosystems need a
C# bridge. Paper days can reproduce a derivation analytically; say what was run.
Lab metadata names language, directory, correctness command and a downloadable archive
for C#; optional benchmark commands are diagnostic.

```bash
python scripts/daily_plan.py --on YYYY-MM-DD
python scripts/add_lesson_navigation.py
python scripts/check_all.py
```

The generator updates footers, sidebars, homepage lists and coverage maps. Adding a
lesson needs new assets and its catalog entry, without editing contracts or CI.
Edit topics only when intentionally extending the planned objective inventory.

## Checks, publication and licenses

Required checks cover deterministic planning, catalog metadata, links, EN/VI structure,
public staging, runnable labs and extracted ZIPs. Builds run in temporary copies.
Optional browser/benchmark diagnostics are independent of the Pages validation gate.
A successful diagnostic workflow still requires checking individual step results.

Original prose uses CC BY 4.0 and original code uses MIT. Preserve third-party notices.
See [licensing](licensing.md) and [source scope](content-provenance.md). Former adapted
IUH descriptions are absent from the active notes; historical extracts are outside
project license grants and remain in unchanged Git history.
