# Phương pháp sư phạm

## Mô hình học tập

Tối ưu cho khả năng ghi nhớ bền vững và chuyển giao kiến thức, không chỉ tạo cảm giác quen thuộc.

Sử dụng:

- retrieval practice
- spaced practice
- interleaving
- self-explanation
- worked example sau đó giảm dần mức hướng dẫn
- deliberate practice tập trung vào lỗi sai
- project/problem-based learning
- phản hồi ngay sau khi người học đã thử làm

## Vòng lặp học hằng ngày

### 1. Retrieve

Bắt đầu mà không xem ghi chú.

Đặt 3-5 câu hỏi ngắn từ nội dung đã học trước đó. Trộn giữa recall và application.

### 2. Gặp một vấn đề trước

Đưa ra một vấn đề thực tế tạo nhu cầu phải hiểu khái niệm mới.

Người học cần biết mình đang cố giải quyết điều gì trước khi đọc phần giải thích.

### 3. Xây mental model

Dạy lượng lý thuyết tối thiểu cần thiết để suy luận về vấn đề.

Dùng diagram, invariant, equation, execution trace hoặc data-flow model khi chúng thực sự hữu ích.

### 4. Guided Practice

Trình bày một worked example và giải thích các quyết định trong quá trình làm.

Tránh đưa nhiều ví dụ gần như giống hệt nhau.

### 5. Independent Practice

Đưa một task với ít scaffolding hơn.

Yêu cầu người học phải đưa ra quyết định, không chỉ lặp lại syntax.

### 6. Feedback

Phân loại lỗi:

- thiếu kiến thức
- mental model sai
- lỗi thực thi do bất cẩn
- dùng sai tool/API
- chưa xem xét design trade-off

Dùng loại lỗi để quyết định hint tiếp theo.

### 7. Explain Back

Yêu cầu người học tự giải thích:

- khái niệm giải quyết vấn đề gì
- nó hoạt động như thế nào
- khi nào nó thất bại
- có alternative nào
- trade-off quan trọng là gì

### 8. Ôn lại sau

Đưa lại khái niệm vào warm-up và mixed problem trong tương lai.

Lịch review mặc định gợi ý là +1 ngày, +3 ngày, +7 ngày và +21 ngày. Đây là scheduling heuristic và có thể điều chỉnh theo performance.

## Phân bổ thời gian luyện tập

Với bài học 60 phút, cấu hình mặc định phù hợp là:

- 5 phút retrieval warm-up
- 10-15 phút theory + worked example
- 20 phút guided / semi-guided lab
- 15 phút independent challenge
- 5 phút explain-back + exit ticket

## Interleaving

Không chỉ luân phiên course một cách ngẫu nhiên.

Hãy interleave những khái niệm buộc người học phải phân biệt, ví dụ:

- index seek vs scan
- optimistic vs pessimistic concurrency
- BFS vs Dijkstra vs A*
- confidence interval vs prediction interval
- precision vs recall vs ROC-AUC
- concurrency vs parallelism
- retry vs circuit breaker

## Productive Failure

Với chủ đề phù hợp, cho người học thử một lời giải có vẻ hợp lý nhưng chưa hoàn chỉnh trước khi dạy canonical approach.

Không để failure trở thành mò mẫm vô định. Giới hạn thời gian và debrief rõ ràng.

## Dấu hiệu mastery

Bằng chứng mạnh cho thấy đã học được:

- giải được một biến thể mới
- dự đoán được system behavior
- giải thích được trade-off
- debug được ví dụ bị lỗi
- chọn được giữa các alternative và biện minh cho lựa chọn
- kết nối được khái niệm sang course/domain khác

Bằng chứng yếu:

- nhận ra terminology
- copy sample
- làm theo step list mà không giải thích
- chỉ trả lời được đúng ví dụ đã thấy trước đó
