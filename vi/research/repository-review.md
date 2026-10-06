# Review repo — học sâu theo chủ đề

Review 2026-10-06 trên baseline `fe74583`; không có AGENTS.md trong repo. Phạm vi gồm runtime/state cục bộ, phương pháp có nguồn, bài học song ngữ, navigation, staging và cấu hình release. Đây không phải thí nghiệm người học hay audit bảo mật toàn diện.

## Lỗi cụ thể và sửa đổi

- Pages trước đây có thể deploy khi workflow validation khác thất bại. Nay gọi reusable validation và deploy phụ thuộc thành công của job đó. Cả hai checkout `github.sha`; chỉ main được publish. Release phải pass check PR trước merge; main chạy lại validation trước khi deploy cùng commit.
- Completion từng chấp nhận assessment của topic không liên quan chỉ vì link cùng lesson. Nay cần task cùng topic, loại hợp lệ, đã quan sát không muộn hơn completion. Prerequisite topic khác vẫn lưu được. Người chấm phải đọc evidence để xác định khớp objective/rubric và nguồn gốc bài làm; match chuỗi không chứng minh được ngữ nghĩa.
- CDN major tag có thể đổi ngoài commit. Docsify/Prism nay dùng URL version đầy đủ. Browser check kiểm tra candidate đã stage; khả dụng CDN vẫn là dependency bên ngoài.

## Thiết kế mới

State v3 bỏ metadata mã môn. Migrate v1/v2 chỉ ghi đích mới, giữ nguồn/evidence và từ chối completion cũ không đủ evidence mà không bịa quan sát. Planner tách context tự khai, flag caller, evidence đã chấm, bài chưa chấm, prerequisite unknown và misconception đã ghi nhận. Profile ngân sách null mặc định 420 phút gồm nghỉ; ngân sách ngắn hơn do người học chỉ định vẫn hợp lệ.

Danh mục chủ đề song ngữ thay phần quản lý học thuật. Đề cương kỹ thuật giữ lại làm ghi chú đọc có [attribution](content-provenance.md), bản gốc còn trong snapshot lịch sử cố định. [Skill mới](../../skills/cs-daily-deep-study/SKILL.md), contract và bài mẫu full-day ưu tiên thực hành kiểm soát, research tập trung và nộp evidence tùy chọn.

## Giới hạn review

JSON validator kiểm tra cấu trúc, không chứng minh lời đáp thật hay dịch đúng ngữ nghĩa. Quan hệ chủ đề, ngân sách thời gian và nhãn mastery là lựa chọn kỹ thuật thận trọng, chưa phải mô hình giáo dục được thực nghiệm. [Kiểm chứng](verification.md) báo check thật và giới hạn. [Review learning science](learning-science-review.md) tách phần full text đã đọc, abstract và nguồn chưa truy cập.
