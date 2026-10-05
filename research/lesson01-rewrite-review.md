# Lesson 01 review and rewrite — 2026-10-05

Scope: both lesson translations, linked labs/solutions, curriculum fit, sources,
skill/template/workflow, private learning state, public staging and CI. This is an
artifact/runtime review, not a learner study or a full security audit.

## Findings in the previously published revision

1. **High impact — practice and language links were unusable.** In
   [the previous lesson, lines 6–7](https://github.com/nguyenan97/computer-science-learning-agent/blob/c490d6d881fde5c958dfce1be7b1b3699ee8d04f/lessons/2026-10-05-cost-model/lesson.md#L6),
   repository-relative links were sent directly to Docsify. Chromium rendered Lab as
   `#/../../labs/cost-model/lab.py`; clicking it requested
   `https://nguyenan97.github.io/labs/cost-model/lab.py.md` and showed Page not found.
   Tiếng Việt similarly retained `../../` in its hash route. Raw files existed; this
   was a renderer/routing error. The site builder now resolves Markdown routes and
   sends code/data assets outside hash routing. Preview and live browser checks are
   required; a raw Markdown HTTP 200 does not prove usable navigation.
2. **Medium impact — the instruction targeted unknown programming experience.**
   [The old selection and syntax bridge](https://github.com/nguyenan97/computer-science-learning-agent/blob/c490d6d881fde5c958dfce1be7b1b3699ee8d04f/lessons/2026-10-05-cost-model/lesson.md#L21)
   did not use the subsequently supplied professional context. The rewrite uses C#
   and a production contract, deriving the comparison count before terminology.
   Engineering background is self-reported context; CS/math mastery remains unknown.
3. **Medium impact — checks did not cover the user's access path.**
   [Navigation validation](https://github.com/nguyenan97/computer-science-learning-agent/blob/c490d6d881fde5c958dfce1be7b1b3699ee8d04f/scripts/validate_docs_navigation.py) covered sidebars,
   and filesystem link checks accepted repository paths. Neither exercised rendered
   lesson links. The new browser check opens both languages, switches between them,
   visits rendered internal routes and fetches asset/download targets. The complete
   ZIP is also extracted and executed without a repository checkout.
4. **Instructional gap — operation counts needed a bridge to .NET measurements.**
   The former Python model was useful for growth analysis but was not a CPU benchmark.
   The rewrite retains the counting argument, adds .NET implementation/equality and
   memory boundaries, and supplies a separate BenchmarkDotNet deep track with actual
   ShortRun results and uncertainty. No numerical speed promise follows from Big-O.

## What was verified

- The curriculum's course 6001127 includes analysis/performance/algorithm selection.
  This lesson sequence is instructor synthesis; current IUH regulations were not checked.
- C# reference code: eight checks, including stable order, unchanged input, null/equality
  policy, collision correctness and duplicate counts.
- ShortRun: 12 cases on Linux, with three warmup/measurement iterations each. Full
  environment/report and priority limitation accompany the results. Wide confidence
  intervals limit timing conclusions; no production load or SQL Server run was performed.
- Repository validation, state behavior regression tests, legacy reference labs, and
  public/private isolation. Real state still has no learner assessments/completion.
- Staged browser checks and execution/build from the extracted lab. CI repeats the
  browser check and runs a Dry benchmark smoke check; Dry is not a speed measurement.

No upstream .NET test suite, Windows/macOS execution, independent learner response,
retention/transfer outcome or educational effectiveness study is claimed. Skill
evaluation cases remain specifications, not completed model evaluations.

## Kết luận bằng tiếng Việt

Bài cũ chưa đạt yêu cầu sử dụng: link lab/đổi ngôn ngữ bị lỗi khi render, kiểm tra chỉ
nhìn menu hoặc file tồn tại, và chưa dùng background nghề nghiệp mới được cung cấp.
Bản viết lại sửa đường dẫn trong bước build, giải thích từ yêu cầu → trace → tổng
chi phí → HashSet/correctness/bộ nhớ, dùng C# làm lab chính và tách benchmark vào nhánh
180+ phút. Bài tập/lab/nộp bài vẫn tùy chọn, lời giải truy cập ngay, bản Việt–Anh đầy đủ.

Kiểm tra code, website và ZIP xác minh khả năng đọc/chạy artifact. Chúng chưa chứng
minh người học hiểu bài hoặc học hiệu quả. Profile chỉ lưu riêng; không tạo assessment,
completion hay mastery từ việc xuất bản/chạy code mẫu.
