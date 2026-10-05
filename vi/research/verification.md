# Kiểm chứng và giới hạn

Refactor runtime kiểm cục bộ **2026-10-05**, Python **3.12.14**, jsonschema **4.26.0**, PyYAML **6.0.3**.
Tất cả walkthrough dùng synthetic data/workspace tạm, không tạo lịch sử người học thật.
Thay đổi này chưa push/merge/deploy. Commit main trước đó đã CI/deploy thành công;
không dùng kết quả đó để claim CI của refactor mới. [Bản chính](../../research/verification.md).

| Kiểm tra | Kết quả |
|---|---|
| Generator --check | Map EN/VI unchanged, up to date |
| Navigation | Route mirror/navbar/hash routing pass |
| Learning validator | Template v2 trống, fixture isolation/invariants, contract version/skill metadata/eval ID/sample/local links pass; chặn private workspace đã tracked |
| Unittest | 27 behavioral tests pass, synthetic |
| Lab mentor --stage all | 4 tests pass, gồm access budget window/input preservation |
| Observer | Index 4/512/32768, reads 3/10/16; duplicate 1, missing 3 |
| OpenAI quick_validate | Frontmatter/name/description skill hợp lệ, chưa chứng minh model behavior |
| Pages builder | Không đóng gói private state, legacy state, lesson riêng đã cài marker synthetic; từ chối public symlink |
| Diff | git diff --check pass |

Regression: exit partial không xóa needs_support; repair link cần reassessment independent
non-exit sau đó/cùng topic; lỗi prerequisite chưa completion vẫn visible; reuse generated;
chiếu lifecycle/due theo ngày; retry cùng ngày giữ thứ tự; scan tuyến tính/mutation bị chặn;
init không overwrite; invalid update giữ bytes; artifact không thoát workspace; migrate
v1 giữ nguồn/lỗi unresolved và copy lesson từ artifact root rõ.

Walkthrough CLI 7 ngày synthetic chạy lifecycle, practice/completion, failed recall,
retry cùng ngày, recall/transfer sau delay; giữ ba review attempts và due gốc. Đây là
kiểm script phối hợp, không là bằng chứng học/retention.

[Runtime review](runtime-design-review.md) và [log nguồn](../../research/runtime-source-checks.json)
ghi nguồn engineering Agent Skills/OpenAI và IES/WWC đã đọc. Candidate papers cũ vẫn
chưa independent full-text verified. Không effect size/lịch ôn phổ quát/token saving.
Sáu eval specification chưa chạy model trials phiên riêng so baseline; tests không
chứng minh tutor sẽ tuân thủ skill.

Ngày có append order, không đo intra-day retention; plan chưa audit profile edits/ngày
tạo review. Summary là heuristic, tutor phải chấm relevance/difficulty/explanation/
independence và duplicate nghĩa. Git-ignore không mã hóa; không force-add dữ liệu thật.
Host giữ file/backup/một writer. Migrate không rewrite free-text evidence links; giữ
code/output revisions và kiểm trước resume.

Translation semantic parity, PDF curriculum gốc/quy định IUH live, upstream CPython
suite, SQL/.NET/cloud lab, browser rendering và retention người thật chưa verified.
Starter cố ý chưa điền; mentor solution tách theo quy ước tutor, không access control.
