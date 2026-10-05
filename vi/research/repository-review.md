# Review repo trước refactor

Ngày 2026-10-05, baseline `fd054f6`, working tree sạch; không có AGENTS.md trong repo. Đã đọc SKILL, curriculum Anh–Việt, references/ledgers, generator, navigation validator, Docsify và ba CI workflow. [Bản chính](../../research/repository-review.md).

Điểm mạnh: curriculum facts canonical và map generated ghi nhãn suy luận; vòng học đã có retrieval/practice/transfer/hint; source policy không chỉ dùng stars; CI kiểm tra navigation song ngữ và map drift.

| Khoảng trống | Hệ quả | Đã sửa |
|---|---|---|
| SKILL lặp policy/contract/ngưỡng điểm | Drift và mâu thuẫn | SKILL điều phối, reference sở hữu contract |
| Hai ledger đều gọi canonical | Tách lịch sử | Một JSON, hai trang chỉ dẫn |
| Ghi record khi tạo bài, không lifecycle | Sinh bài có thể bị hiểu đã học | generated/assigned/in_progress/completed có evidence |
| Thiếu task/hint/misconception/history ôn | Khó chứng minh adaptation/mastery | Assessment và review attempts có lịch sử |
| Due từ generation | Lịch tách lần thực hành | Sau completion, giữ due cũ và reason đổi |
| Giả định trình độ cao, ratio/gate/năm cố định | Quá tải, heuristic như khoa học | Diagnostic, mode theo thời gian, rubric/evidence và verify lúc học |
| Github chưa có dossier tái lập | Link cũ, quá rộng, không pin | Metadata có ngày, SHA, target/activity/unknown |
| Lab chung chưa runnable | Không có kiểm chứng workflow | Starter, checkpoint, independent challenge và mentor solution |
| CI chỉ nav/map | State sai vẫn qua | Schema/semantic check, scenario tests, lesson gate và CI |

Không sửa fact curriculum/generated map, không thêm database/backend, không deploy/publish. State thật giữ trống; không bịa lịch sử. Ledger cũ không có record để migrate. Nếu sau này import record cũ thiếu status, giữ artifact, tạo generated/unassessed và yêu cầu bằng chứng attempt/completion trước khi nâng trạng thái.
