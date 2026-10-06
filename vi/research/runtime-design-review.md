> Review thiết kế lịch sử ngày 2026-10-05. Skill full-day, state v3 và check hiện tại ở [review repo](repository-review.md) và [kiểm chứng](verification.md).

# Review thiết kế runtime và skill

Ngày 2026-10-05. [Bản chính](../../research/runtime-design-review.md) và
[log nguồn/hashes](../../research/runtime-source-checks.json) ghi phạm vi/giới hạn.
Đây là review kỹ thuật có mục tiêu, không phải systematic review hay thử nghiệm hiệu quả.

Đã đọc đặc tả/best practices/evaluation của Agent Skills, hướng dẫn skill-creator và
interface metadata của OpenAI, cùng evidence table và các recommendation liên quan
trong practice guide IES/WWC 2007. Guide chấm spacing/example xen problem moderate,
retrieval re-exposure 5b và deep explanation 7 strong, prequestion 5a và study allocation
6a/6b low theo framework của họ. Đối tượng trường học/đại học không chứng minh hiệu quả
AI tutor CS sau đại học; không suy effect size/lịch ôn phổ quát.

Skill giữ ngắn, khai báo phụ thuộc repo đầy đủ, tải reference theo chặng. Orient →
diagnose → select → teach → assess → repair → persist/review phải chờ câu trả lời/bài
làm thật. Draft-only giữ điều kiện, không tạo learner events. Sáu eval case là specification;
chưa chạy benchmark model với/không skill trong phiên riêng, không claim pass rate.

Needs_support chỉ được gỡ qua reassessment independent, non-exit, sau đó, cùng topic
và explicit repair link; tutor vẫn phải đánh giá task mới sửa đúng lỗi. Array append order
phân biệt cùng ngày; ngày thật đo độ trễ. Retry cùng ngày không là delayed retention.
Đây là hợp đồng kỹ thuật thận trọng, chưa là mô hình mastery đã xác thực.

State mặc định workspace Git-ignore; có init/profile/migrate không ghi đè. Pages chỉ
đóng gói docs/template trống/sample cố định. Ignore không mã hóa hay access control;
không force-add dữ liệu thật vào public repo. Host chịu trách nhiệm giữ file/backup,
một writer. Walkthrough CLI 7 ngày synthetic kiểm state/scheduling, không chứng minh
người học nhớ kiến thức. Hiệu quả thực tế/model eval/timing/token cần đo riêng.
