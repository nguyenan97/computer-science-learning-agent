<!-- contract-version: 5 -->
# Mẫu ngày học sâu

Tài liệu này quản lý cấu trúc/thời lượng. [Workflow](learning-workflow.md) quản lý state; [pedagogy](pedagogy.md) quản lý cách dạy; [source policy](source-policy.md) quản lý research. Bài Việt và Anh đều đầy đủ, dùng chung code và một record song ngữ nội bộ. Tính thời gian cho một ngôn ngữ.

## Trang học hoàn chỉnh

Viết phần diễn giải liền mạch dạy trọn objective ngay trên trang. Có nền tảng cần
thiết, ví dụ/trace giải thích từng bước, toàn bộ code task, lệnh copy được, phân tích
thí nghiệm và lời giải đầy đủ. Nguồn/repo/download bổ sung, không thay phần giải
thích, code hoặc đáp án. Trang Việt/Anh đều sử dụng độc lập được.

Chỉ đưa nội dung có ích cho người học lên bài. Session/topic record ID, audit chọn
bài, bảng access/status nguồn, quy trình state/schema/assessment và log agent ở
record riêng hoặc tài liệu maintainer. Trích nguồn ngắn, giải thích uncertainty khi
ảnh hưởng kết quả. Không lặp quy tắc nội bộ/agent boilerplate qua các bài.

## Header, objective và độ sẵn sàng

Trên trang: title có nghĩa, động lực thực tế, một objective chính đo được, 2–4 outcome
hỗ trợ và prerequisite cụ thể. Self-check ngắn giúp chọn nhánh nền tảng/đường chính.
Giải thích prerequisite ngay trong bài; link bài trước chỉ để ôn bổ sung.

Record tác giả/phiên riêng: session/topic ID, kind/status, lý do chọn, kiểm tra trùng
ý nghĩa và evidence tách tự khai/quan sát/unknown/misconception. Không render audit
này trong bài học.

Self-check ngắn, đáp án và nhánh: evidence phù hợp → giảm hướng dẫn dư; câu trả lời yếu → bridge/recheck; không trả lời → bridge có điều kiện và unknown readiness. Giao bài đầy đủ mà không chờ đáp án.

## Kế hoạch cả ngày

Mặc định 420 phút tổng (7 giờ); chỉnh trong 360–480 phút hoặc thời gian ngắn hơn được yêu cầu. Tính cả nghỉ/setup, một objective, output và điểm dừng. Tối thiểu 60% phút học là kỹ thuật chủ động; tách khỏi đọc thụ động/setup. Đây là lựa chọn project, không phải thời lượng tối ưu khoa học.

| Block | Phút tổng | Phút chủ động | Output quan sát được |
|---|---:|---:|---|
| Định hướng, tự nhớ và self-check prerequisite | 20 | 10 | Dự đoán, model nhớ lại, phần chưa biết |
| Nền tảng, mental model và worked trace | 50 | 20 | Trace chú thích, invariant, phản ví dụ |
| Nghỉ | 10 | 0 | Nghỉ |
| Đọc nguồn để trả lời câu hỏi research | 45 | 10 | Bảng claim và dự đoán có thể thử |
| Xem/trace implementation và tests | 45 | 40 | Trace code, behavior dự đoán, phương án khác |
| Ăn trưa/nghỉ | 30 | 0 | Nghỉ |
| Lab implementation/debug có hướng dẫn | 75 | 70 | Artifact chạy được, test case, ghi chú debug |
| Nghỉ | 10 | 0 | Nghỉ |
| Thí nghiệm có kiểm soát và phân tích | 45 | 40 | Số đo, biến kiểm soát, giới hạn |
| Nghỉ | 10 | 0 | Nghỉ |
| Transfer đổi ngữ cảnh và sửa lỗi | 35 | 35 | Biến thể mới và trade-off có lý do |
| Tổng hợp, explain-back, tự đánh giá và kế hoạch ôn | 45 | 10 | Memo, câu hỏi mở, prompt tương lai |
| **Tổng** | **420** | **235** | **360 học + 60 nghỉ; 65,3% học chủ động** |

Co giãn có suy xét, không nhân mọi task máy móc. Bridge thay thế đào sâu, không kéo dài ngày. Giới hạn setup rõ (mặc định 15 phút là heuristic), rồi trace offline/tương đương hoặc dời. Dừng block đúng timebox, giữ artifact và câu hỏi.

## Vấn đề, mental model và ví dụ

Bắt đầu với yêu cầu kỹ thuật và dự đoán. Dạy nền tảng tối thiểu, giả định, chi phí/model/invariant, ví dụ giải thích từng quyết định, phản ví dụ, misconception và ứng dụng thật. Định nghĩa thuật ngữ lúc dùng. Ngữ cảnh lập trình quen thuộc không chứng nhận prerequisite toán.

## Câu hỏi research và đọc nguồn

Có 2–4 câu hỏi giới hạn và diễn giải finding/model liên quan ngay trong bài. Giải
thích suy luận và implementation slice, code task/giả định. Chỉ cách tạo claim, dự
đoán case và thử. Nguồn đọc tùy chọn có section cụ thể và câu hỏi sâu hơn giúp trả
lời. Trích nguồn ngắn; audit access/version/dossier repo ở record tác giả. Nêu giới
hạn/mâu thuẫn có ý nghĩa trong diễn giải, không bằng bảng audit.

## Lab/thí nghiệm tái hiện được

Ghi objective, prerequisite, pin OS/runtime/dependency/data, working directory, lệnh,
output và fallback offline. Đặt starter deterministic, implementation thiết yếu và
lời giải ngay trong trang, có tên file để người học tự lắp/chạy mà không phải tải
ZIP. Download là bản tiện dùng. Giải thích purpose, dự đoán, checkpoint, self-check
và debug path từng bước. Thí nghiệm có diễn giải câu hỏi/giả thuyết, biến, controls,
case/seed, cách đo, kết quả và giới hạn. Tách lỗi khái niệm, implementation, môi
trường. Log kiểm tra của agent ở ngoài bài.

## Transfer, lời giải và rubric

Đổi dữ liệu/yêu cầu/cách biểu diễn và giải thích vì sao kiểm tra objective. Mọi bài tập/self-check/exit có lời giải đầy đủ ngay sau đề hoặc mục thu gọn; không cần nộp. Thử trước tùy chọn. Nếu đã đọc đáp án, đánh giá độc lập sau dùng biến thể mới liên quan chưa thấy.

Tiêu chí người học hiểu được: correctness/edge case, reasoning/invariant,
controls/tái hiện, giải thích trade-off và transfer. Diễn giải lỗi thường gặp, sửa
đúng lỗi và case mới. Explain-back hỏi cơ chế, giả định, phản ví dụ, kết quả lệch,
giới hạn model. Mức trợ giúp/formal assessment lưu riêng, không đưa thủ tục state lên bài.

## Tổng hợp, uncertainty và ngày sau

Cuối bài có memo: model trước → sau; claim kiểm chứng → evidence/limits; tự khai so với demonstrated/unknown; câu hỏi mở; quyết định dừng/resume. Có prompt tự tái dựng và đổi ngữ cảnh sau độ trễ. Hook chưa là ôn đã làm/mastery; chọn lịch dựa evidence thật theo workflow.

Có đường chỉ đọc qua model, worked traces, section nguồn, giải thích lab, lời giải và tổng hợp. Thực hành/nộp bài tùy chọn. Không trả lời vẫn được học ngày sau; giữ unknown completion/mastery.

## Cuối trang: đọc liên quan và bài trước/sau

Sau phần tổng hợp, có **Đọc thêm liên quan**, tiếp theo **Bài trước/Bài tiếp theo**
đã tồn tại. Sinh footer từ `lessons/catalog.json` bằng
`python scripts/add_lesson_navigation.py`, đặt block giữa
`<!-- LESSON_NAVIGATION_START -->` và `<!-- LESSON_NAVIGATION_END -->`. Chọn link có
lý do đọc ngắn. Trang Việt link Việt, trang Anh link Anh. Catalog quyết định thứ tự
và mục liên quan; không bịa trang tương lai hoặc đưa tài liệu audit/state nội bộ vào
gợi ý người học.

Thứ tự hiện tại: `2026-10-05-cost-model` → `boundary-search`. Bài đầu chỉ có link
tiếp; bài cuối chỉ có link trước. Khi catalog đổi, sinh lại cả hai ngôn ngữ. Không
có bài liền kề thì bỏ link đó. Nguồn/download là bổ sung; footer không khóa theo
tiến độ hoặc nộp bài.

## Artifact và kiểm tra chất lượng

Lưu riêng `lesson.vi.md`, `lesson.en.md` dưới thư mục state. Record generated schema-v3 chỉ ghi thiết kế: ngày lifecycle tương lai null, assessment IDs rỗng, không metadata môn học. Code/nguồn dùng chung; so outcome, lịch, prompt, lời giải, limits và troubleshooting để bảo đảm ý nghĩa tương đương.

Ví dụ chung có thể ở `lessons/`, `vi/lessons/`, shared labs/catalog downloads. Xuất bản cần yêu cầu rõ. Trước tuyên bố sử dụng tốt, xem bài inline đầy đủ, footer đọc liên quan/trước/sau được sinh, chuyển ngôn ngữ, download trực tiếp và chạy lab đã giải nén. Checks/log/metadata nội bộ ở record maintainer/riêng; chỉ nêu giới hạn có ích cho người học. [Ví dụ full-day](../lessons/2026-10-05-cost-model/lesson.md) minh họa template; ví dụ ngắn cũ không là daily default.
