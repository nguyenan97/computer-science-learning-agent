# Bản đồ chủ đề kỹ thuật

<!-- Generated from topics.json by scripts/generate_topic_map.py. -->

Chọn một câu hỏi thực tế bạn muốn trả lời. Mỗi chủ đề bên dưới nêu nền tảng hữu ích, mục tiêu cụ thể và cách kiểm tra hiểu biết bằng code hoặc thí nghiệm. Nếu chưa quen một nền tảng, bắt đầu bằng trace hoặc ví dụ nhỏ trước bài lớn.

Dùng [ghi chú theo chủ đề](topic-notes.md) để tìm hiểu sâu hơn. Quan hệ gợi ý giúp định hướng học; bạn có thể điều chỉnh theo phần đã hiểu.

## Hợp đồng chương trình và bất biến

- **Nền tảng hữu ích:** kiểm tra nền tảng cần cho tác vụ
- **Mục tiêu học:** Trace vòng lặp, nêu bất biến và dựng phản ví dụ cho quy tắc biên sai.
- **Thực hành:** Viết checker theo bảng cho dữ liệu rỗng, trùng lặp và ở biên.

## Khử trùng giữ thứ tự và mô hình chi phí

- **Nền tảng hữu ích:** Hợp đồng chương trình và bất biến
- **Mục tiêu học:** Chọn scan hoặc hash theo ràng buộc thứ tự/bằng nhau/bộ nhớ, giải thích số phép tính riêng với thời gian đo.
- **Thực hành:** Implement, kiểm tra collision và benchmark scan với HashSet trên dữ liệu có kiểm soát.

## Tìm biên và truy vấn có thứ tự

- **Nền tảng hữu ích:** Hợp đồng chương trình và bất biến
- **Mục tiêu học:** Suy ra lower/upper bound và đếm cửa sổ nửa mở với số lần truy cập logarithm.
- **Thực hành:** Đọc bisect ở pin, trace dữ liệu trùng, kiểm tra số truy cập và áp dụng cho cửa sổ timestamp.

## Đồ thị và chọn chiến lược

- **Nền tảng hữu ích:** Hợp đồng chương trình và bất biến
- **Mục tiêu học:** Chọn BFS hay Dijkstra theo giả thiết trọng số và đưa phản ví dụ khi chọn sai.
- **Thực hành:** Viết bộ tìm đường, so sánh node đã thăm và tính đúng đường đi.

## Quy hoạch động và xấp xỉ

- **Nền tảng hữu ích:** Đồ thị và chọn chiến lược
- **Mục tiêu học:** Định nghĩa state/công thức truy hồi, so phản ví dụ greedy và chặn chất lượng cho một bài tối ưu.
- **Thực hành:** Viết oracle chính xác nhỏ và so heuristic trên dữ liệu sinh.

## Lưu trữ, chỉ mục và query plan

- **Nền tảng hữu ích:** Tìm biên và truy vấn có thứ tự
- **Mục tiêu học:** Giải thích seek với scan theo selectivity, thứ tự và chi phí cập nhật bằng query plan thật.
- **Thực hành:** Nạp database cục bộ, đọc plan và đo workload có/không có index.

## Transaction, đồng thời và phục hồi

- **Nền tảng hữu ích:** Lưu trữ, chỉ mục và query plan
- **Mục tiêu học:** Tái hiện một anomaly isolation và giải thích cơ chế ngăn chặn/phục hồi đã chọn.
- **Thực hành:** Chạy hai client đồng thời với lịch thực thi ghi lại và trace crash/recovery.

## Xác suất, ước lượng và độ bất định

- **Nền tảng hữu ích:** kiểm tra nền tảng cần cho tác vụ
- **Mục tiêu học:** Diễn giải biến thiên lấy mẫu và khoảng tin cậy, không xem một lần chạy là kết quả phổ quát.
- **Thực hành:** Mô phỏng mẫu, vẽ phân phối và kiểm tra giả thiết với seed tái lập.

## Thiết kế thí nghiệm và giới hạn nhân quả

- **Nền tảng hữu ích:** Xác suất, ước lượng và độ bất định
- **Mục tiêu học:** Kiểm soát một thí nghiệm, báo bất định và phân biệt tương quan với kết luận nhân quả.
- **Thực hành:** So baseline/treatment, kiểm tra confound trong notebook tái lập.

## Hệ học và đánh giá trung thực

- **Nền tảng hữu ích:** Thiết kế thí nghiệm và giới hạn nhân quả
- **Mục tiêu học:** Xây baseline, tránh leakage và giải thích trade-off metric trên tập hold-out.
- **Thực hành:** Fit mô hình nhỏ, đọc lỗi và so với baseline quy tắc đơn giản.

## Mạng neural và tối ưu

- **Nền tảng hữu ích:** Hệ học và đánh giá trung thực
- **Mục tiêu học:** Chẩn đoán overfitting hoặc lỗi tối ưu bằng loss curve và một can thiệp có kiểm soát.
- **Thực hành:** Implement mạng nhỏ, kiểm tra gradient và làm ablation có mục tiêu.

## Mô hình ngôn ngữ và đánh giá truy hồi

- **Nền tảng hữu ích:** Hệ học và đánh giá trung thực
- **Mục tiêu học:** Đánh giá một pipeline text/retrieval bằng phân loại lỗi và giới hạn dữ liệu rõ ràng.
- **Thực hành:** So truy hồi lexical với embedding và phân tích query thất bại.

## Xử lý ảnh và thị giác

- **Nền tảng hữu ích:** Mạng neural và tối ưu
- **Mục tiêu học:** Giải thích lựa chọn biểu diễn và đánh giá robustness cho tác vụ ảnh cụ thể.
- **Thực hành:** So biến đổi cổ điển với baseline học khi perturb có kiểm soát.

## Song song và đồng bộ

- **Nền tảng hữu ích:** Hợp đồng chương trình và bất biến
- **Mục tiêu học:** Tái hiện race, sửa đồng bộ và giải thích giới hạn scale từ work/overhead đo được.
- **Thực hành:** So implement tuần tự/song song, kiểm tra đúng và contention.

## Dữ liệu phân tán và chịu lỗi

- **Nền tảng hữu ích:** Transaction, đồng thời và phục hồi, Song song và đồng bộ
- **Mục tiêu học:** Trace failure/retry và giải thích lựa chọn consistency/idempotency.
- **Thực hành:** Chèn giao nhận lặp và process failure vào pipeline cục bộ nhỏ.

## Mạng và truyền thông

- **Nền tảng hữu ích:** Hợp đồng chương trình và bất biến
- **Mục tiêu học:** Giải thích latency, throughput và hành vi giao thức từ trace request.
- **Thực hành:** Đo client/server cục bộ, kiểm tra retry, timeout và giả thiết congestion.

## Bảo mật và threat modeling

- **Nền tảng hữu ích:** Mạng và truyền thông
- **Mục tiêu học:** Nêu tài sản/trust boundary và kiểm tra một biện pháp với tình huống tấn công tái lập.
- **Thực hành:** Viết harness cô lập cho authorization, xử lý input hoặc sử dụng crypto sai.

## Pipeline cloud và observability

- **Nền tảng hữu ích:** Dữ liệu phân tán và chịu lỗi
- **Mục tiêu học:** Lập luận delivery, chi phí và recovery của pipeline từ sự kiện đo được.
- **Thực hành:** Prototype cục bộ trước, chèn fault và ghi giả thiết latency/chi phí trước cloud tùy chọn.

## Lý thuyết thông tin và mô phỏng

- **Nền tảng hữu ích:** Xác suất, ước lượng và độ bất định
- **Mục tiêu học:** Nối entropy hoặc mô hình ngẫu nhiên với một câu hỏi kỹ thuật đo được.
- **Thực hành:** Mô phỏng kênh hoặc queue, so phân phối dự đoán với quan sát.

## Đọc, tái lập và tổng hợp nghiên cứu

- **Nền tảng hữu ích:** Thiết kế thí nghiệm và giới hạn nhân quả
- **Mục tiêu học:** Nêu câu hỏi có thể bác bỏ, tái lập claim có giới hạn và tách evidence với suy luận.
- **Thực hành:** Đọc methods/code, chạy tái lập nhỏ và viết log claim–evidence–giới hạn.

## Khám phá dữ liệu và trình bày

- **Nền tảng hữu ích:** Xác suất, ước lượng và độ bất định
- **Mục tiêu học:** Chọn cách trực quan hóa trung thực và chẩn đoán biểu diễn gây hiểu lầm.
- **Thực hành:** Vẽ EDA, kiểm tra missing/outlier và giải thích một quyết định dựa trên dữ liệu.
