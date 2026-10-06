<!-- contract-version: 5 -->
# Phương pháp cho ngày học sâu

Hướng tới nhớ bền vững, suy luận kỹ thuật độc lập và vận dụng khi đổi ngữ cảnh. [Báo cáo nghiên cứu](../research/learning-science-review.md) phân biệt bằng chứng đã đọc với lựa chọn của project; [workflow](learning-workflow.md) quản lý tiến độ. Không có phương pháp hay lịch ngày tốt nhất cho mọi người.

## Dạy đầy đủ ngay trên trang học

Bài học là phần giải thích hoàn chỉnh, không chỉ giao đọc hay báo cáo của agent.
Kể mạch vấn đề, model, quyết định, code và kết quả bằng lời giải thích liền mạch trên
trang. Có toàn bộ code cần cho mỗi task và lời giải đầy đủ cạnh đề. Nguồn ngoài và
download bổ sung, không thay phần giải thích/lời giải thiết yếu. Bản Việt và Anh đều
có thể học độc lập.

Hiển thị objective, prerequisite/self-check, ví dụ hữu ích, lệnh chạy, troubleshooting,
trade-off và câu hỏi suy ngẫm. Session ID nội bộ, bảng truy cập nguồn, quy trình
state/assessment và log agent ở hồ sơ riêng hoặc tài liệu maintainer. Tránh lặp policy
boilerplate; chỉ nêu uncertainty khi ảnh hưởng cách hiểu/dùng kết quả. Cuối bài có
nội dung đọc liên quan và bài trước/sau đã tồn tại, sinh từ catalog theo [template](lesson-template.md).

## Xác định điều đã biết

Phân biệt bốn nhóm cho từng prerequisite và objective:

| Nhóm | Ý nghĩa | Quyết định dạy |
|---|---|---|
| Tự khai | Người học mô tả kinh nghiệm, sự tự tin hoặc nội dung từng đọc | Chọn ví dụ phù hợp, tránh dạy lại cú pháp; không chứng nhận mastery |
| Bằng chứng đã quan sát | Câu trả lời/code/trace thật, có task, ngày, ngữ cảnh và mức trợ giúp | Điều chỉnh trong đúng phạm vi đã thể hiện; bằng chứng cũ có thể không còn đủ |
| Chưa biết / chưa kiểm chứng | Chưa có quan sát liên quan, hoặc chỉ agent thực hiện | Có self-check và nhánh bổ sung nền tảng; thiếu bằng chứng không có nghĩa là thiếu năng lực |
| Hiểu sai đã quan sát | Mô hình sai hoặc lỗi lặp có câu trả lời thật làm căn cứ | Sửa đúng lỗi rồi dùng case mới; giữ nguyên bằng chứng chưa được giải quyết |

Test pass xác nhận artifact trong môi trường được kiểm tra. Đọc bài, chép lời giải, nhận bài, số giờ học và agent chạy test không chứng minh năng lực người học. Ghi đúng độc lập, dùng hint và dùng lời giải. Nếu đã xem đáp án, cần biến thể mới chưa thấy để đánh giá tính độc lập.

## Vòng học

Tự nhớ không xem ghi chú → tìm hiểu yêu cầu cụ thể → xây mental model nhỏ → xem ví dụ có lời giải → trace implementation → code/thí nghiệm → debug → đổi yêu cầu để vận dụng → giải thích kết quả và giới hạn → ôn sau độ trễ.

Khi prerequisite còn mới, minh họa cách làm trước khám phá mở. Nếu có bằng chứng phù hợp, bắt đầu bằng dự đoán/lần thử có giới hạn rồi giải thích lại. Đặt giải thích cạnh code/sơ đồ liên quan và giảm hỗ trợ dần. Một lần thử khó mà không tổng hợp lại không tự động tạo học tập hiệu quả.

Chuyển các nguyên tắc thành hoạt động:

- **Retrieval:** tự tái dựng invariant, quy trình hoặc lựa chọn chiến lược; so với lời giải và sửa. Nhận diện đáp án và đọc lại là hoạt động khác.
- **Spacing:** quay lại lần thử thật vào ngày sau, ghi độ trễ và trợ giúp. Điều chỉnh theo mục tiêu lưu giữ/kết quả; mốc cố định chỉ là heuristic.
- **Interleaving:** sau khi có mô hình, trộn phương án liên quan và yêu cầu chọn/giải thích. Đảo chủ đề không liên quan không thay thế luyện phân biệt chiến lược.
- **Worked examples:** trình bày quyết định, giả định, phản ví dụ; tiếp theo là phần điền còn thiếu và biến thể độc lập. Điều chỉnh scaffolding theo bằng chứng liên quan.
- **Luyện có mục đích:** tách subskill yếu đã quan sát, đặt tiêu chí, đổi case và nhận feedback. Code thông thường hay số giờ không đủ để đáp ứng định nghĩa deliberate practice chặt hơn trong nghiên cứu.
- **Feedback:** sau lần thử thật, chỉ rõ khoảng cách giữa tiêu chí và suy luận, hướng sửa có thể làm ngay, rồi mời thử case mới. Tách lỗi khái niệm với setup/công cụ.
- **Cognitive load:** giảm setup không liên quan, mỗi lần một mô hình, checkpoint rõ, dùng tương đương offline khi công cụ lấn thời gian. Giữ độ khó suy luận hữu ích; cảm thấy nhẹ hơn không tự chứng minh học tốt hơn.

Dùng yêu cầu production và trace nhỏ trước thuật ngữ. Suy ra mô hình/chi phí, nối với implementation và nêu giới hạn đơn giản hóa. Chọn ecosystem phù hợp chủ đề rồi bridge sang stack quen thuộc; không thêm hạ tầng chỉ để khớp profile.

## Ngày học thực hành nhiều hơn giảng giải

Mặc định **420 phút tổng**, gồm **360 phút học và 60 phút nghỉ**, tính cho một bản ngôn ngữ. Khoảng thông thường là 360–480 phút (6–8 giờ); tôn trọng thời gian ngắn hơn được yêu cầu. Lịch và tối thiểu **60% thời gian học chủ động** là yêu cầu thiết kế của project, không phải tỷ lệ tối ưu đã chứng minh.

[Template](lesson-template.md) có lịch chuẩn: 235/360 phút chủ động (65,3%). Chủ động là dự đoán/trace, implementation, thiết kế/chạy thí nghiệm có kiểm soát, debug, kiểm tra claim hoặc giải bài đổi ngữ cảnh. Đọc thụ động, xem video, setup thông thường và nghỉ không tính. Mỗi block tạo artifact/câu hỏi cụ thể; ngân sách bao gồm setup và truy cập nguồn. Không kéo dài giảng lý thuyết thành bảy giờ hoặc tính đọc thụ động là thực hành.

Một objective chính, outcome hỗ trợ đo được và nhánh đào sâu tùy chọn. Sau giới hạn setup, dừng hoặc đổi fallback; dời câu hỏi phụ thay vì thêm objective không liên quan. Giữ phần chưa xong khi hết giờ/mệt. Đường chỉ đọc chỉ rõ phần đọc/xem/bỏ qua, giữ toàn bộ lời giải; người học vẫn được học ngày sau mà không nộp bài hay được gán mastery giả.

## Rubric, sửa lỗi và ôn

Đặt tiêu chí đúng objective trước task: correctness/edge case, model/invariant, tái hiện/kiểm soát thí nghiệm, giả định/trade-off, độc lập và transfer. Dùng đánh giá định tính trừ khi điểm có cơ sở rõ. Kết quả cùng ngày là tạm thời; recall/transfer sau độ trễ chỉ củng cố phạm vi đã đánh giá. Một ngày muộn hơn không phải thời hạn lưu giữ đủ cho mọi trường hợp.

Hint tăng từ khái niệm → cấu trúc → implementation. Mỗi bài tập/diagnostic/exit có lời giải tách khỏi đề và truy cập ngay. Nộp bài không mở khóa đáp án/bài mới. Completion cần bài làm thật liên quan objective; engine kiểm tra topic, tutor kiểm tra liên hệ task/rubric. Completion khác năng lực độc lập và mastery bền vững.

Cuối ngày có bản tổng hợp: mental model mới, claim đã thử, giới hạn, câu hỏi mở và prompt recall/transfer tương lai. Prompt dự kiến chưa phải lượt ôn đã thực hiện. Chỉ ghi assessment từ bằng chứng thật tự nguyện.
