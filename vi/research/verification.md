# Kết quả kiểm chứng và giới hạn

Kiểm tra cục bộ **2026-10-05**, Python **3.12.14**, jsonschema **4.26.0**. Không deploy/publish, không đánh giá người học, không build CPython upstream. State thật trống; record mẫu generated nằm ngoài; dữ liệu low-result có `fixture:true`. [Bản kết quả chính](../../research/verification.md).

| Kiểm tra | Kết quả/phạm vi |
|---|---|
| Generator `--check` | Map Anh–Việt đúng, unchanged; không sửa generated thủ công |
| Navigation validator | Route mirror, navbar và hash-routing pass |
| State validate/plan | JSON v1 hợp lệ; diagnostic, không due/pending/mastery bịa, time unknown |
| Learning validator | State/fixture isolation, schema/semantic invariant, contract version, section/target/artifact/local link pass |
| Unittest | 14 behavioral tests pass, tất cả synthetic |
| Lab mentor solution | 3 tests pass: 1.260 case sorted multiset/target, 18 case access budget, window/edge/validation; kiểm input không đổi và không slice search |
| Observer | n=8/1024/65536, index=4/512/32768, reads=3/10/16; duplicate index=1, missing index=3 |
| Source pin | Bốn file CPython ở SHA resolve có hash trùng file release đã đọc |

Starter cố ý TODO/NotImplementedError. Chạy mentor chứng minh bài tham chiếu runnable, không chứng minh người học. Access counts không phải timing/speedup production. CI mới cấu hình các gate tương ứng, chưa claim GitHub Actions đã chạy.

Bảy scenario: mới → diagnostic/unknown; assigned chưa thử → resume, không nhảy completed; nền yếu → bridge; ôn quá hạn → vẫn due tới attempt/assessment và giữ ngày cũ; kết quả thấp → completion có thể có lỗi nhưng cần remediation; độc lập ngày sau recall+transfer → cân nhắc tăng khó, lỗi/partial mới giảm confidence; nguồn/lab thiếu → fallback/offline/defer, không bịa run.

Negative checks: fixture dùng như state thật, link assessment thiếu, completion thiếu practice, score thiếu basis, hinted ghi independent, core trùng và review history sai đều bị từ chối. CLI smoke trên temp fixture chạy add/assign/start/evidence/complete/review/reschedule; rejection giữ nguyên byte file. Planner theo ngày trước không dùng evidence tương lai.

Giới hạn: DOI qua proxy không truy cập nên 12 candidate chưa full-text verified; chỉ đọc trực tiếp DFI/Carpentries, productive failure/mastery tạm thời, không effect size claim. API GitHub thiếu nên dùng HTML field/commit page; pin/raw đã verify, không claim latest/support/adoption định lượng. Validator không chứng minh tác giả artifact/rubric đúng; semantic duplicate và nghĩa bản dịch cần review người thật. Schema theo ngày, không mô hình trong-ngày, không psychometric/decay/scheduler tối ưu phổ quát. State atomic một writer, manual edit vẫn có thể đổi lịch sử. Chưa xác minh PDF curriculum gốc/quy định live/browser rendering/.NET/SQL/cloud lab/upstream tests.

Học hằng ngày: nêu mục tiêu/time/tools → state/due → diagnostic → chọn/research core hoặc review/repair → predict/run/explain → gửi artifact độc lập và feedback → ghi lifecycle/evidence thật → chọn và kiểm tra ôn sau độ trễ. [Workflow](../references/learning-workflow.md), [bài mẫu](../lessons/boundary-search/lesson.md).
