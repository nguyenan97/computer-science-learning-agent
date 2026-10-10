# Học Computer Science qua thực hành

[English](../README.md) · [Tiếng Việt](README.md)

Hiểu cách chương trình hoạt động, chọn thuật toán phù hợp và kiểm tra quyết định kỹ thuật bằng code. Mỗi bài có giải thích, ví dụ, bài thực hành và lời giải. Bạn có thể đọc ngay trong trình duyệt, xem mã nguồn của dự án thực tế và tải lab để tự chạy thí nghiệm.

## Bắt đầu học

<!-- LESSON_LIST_START -->
1. **[Bài 01 - Big-O và cấu trúc dữ liệu: dedupe mã đơn hàng bằng C#](lessons/2026-10-05-cost-model/lesson.md)** - Phân tích chi phí của List và HashSet, giữ thứ tự xuất hiện đầu tiên và kiểm tra giả thuyết về hiệu năng.
2. **[Bài 02 - Tìm biên bằng binary search và đếm sự kiện theo khoảng thời gian](lessons/boundary-search/lesson.md)** - Tìm vị trí đầu tiên thỏa điều kiện, chứng minh thuật toán đúng và đếm sự kiện trong [start,end) bằng C# và T-SQL.
3. **[Bài 03 - Đường đi ngắn nhất: chọn BFS hay Dijkstra](lessons/2026-10-07-shortest-paths/lesson.md)** - Chọn mục tiêu tìm đường, chứng minh điều kiện dừng của BFS/Dijkstra, kiểm tra đường đi C# và diễn giải số thao tác.
4. **[Bài 04 - Quy hoạch động và xấp xỉ: chọn công việc trong một ngân sách](lessons/2026-10-08-dp-approximation/lesson.md)** - Chứng minh truy hồi DP 0/1 và xấp xỉ 1/2, đọc join planner PostgreSQL, kiểm tra bộ chọn C# bằng vét cạn.
5. **[Bài 05 - Index và query plan: vì sao seek vẫn có thể tốn nhiều công](lessons/2026-10-09-index-query-plans/lesson.md)** - Giải thích đoạn khóa ghép và độ bao phủ, đọc source/plan SQLite thật, đo workload đọc/ghi tương đương bằng C#.
6. **[Bài 06 - Transaction và phục hồi: ghi đúng vẫn có thể dùng quyết định đã cũ](lessons/2026-10-10-transactions-recovery/lesson.md)** - Chạy lịch dùng quyết định cũ, kiểm tra đặt giữ, đọc source WAL SQLite và thử hai client/phục hồi crash tiến trình bằng C#.
7. **[Bài 07 - Độ bất định khi lấy mẫu: nhiều record chưa chắc có thêm bằng chứng](lessons/2026-10-11-sampling-uncertainty/lesson.md)** - Suy ra khoảng Wilson, đọc source SciPy và mô phỏng biến thiên lấy mẫu, độ bao phủ hữu hạn, quan sát liên kết bằng C#.
8. **[Bài 08 - Thiết kế thí nghiệm: chênh lệch chưa đủ để kết luận nhân quả](lessons/2026-10-12-experimental-design/lesson.md)** - Suy ra ước lượng theo cặp ngẫu nhiên, đọc đường gán GrowthBook và liệt kê yếu tố gây nhiễu, độ phân tán thiết kế, kiểm định sharp null bằng C#.
9. **[Bài 09 - Đánh giá trung thực: học quy tắc, không học từ test](lessons/2026-10-13-honest-evaluation/lesson.md)** - Học mô hình ngưỡng hữu hạn, giữ ranh giới train/validation/test, đọc search/Pipeline scikit-learn và chất vấn metric bằng phản ví dụ leakage giả lập C#.
<!-- LESSON_LIST_END -->

Bắt đầu với Bài 01 nếu bạn muốn xây nền tảng phân tích chi phí. Bạn cũng có thể mở chủ đề trả lời câu hỏi hiện tại. Cuối mỗi trang có nội dung liên quan và link tới bài trước hoặc bài sau đã có.

## Cách học

[Thiết kế ngày học](../references/study-profile.json) có hai hướng: thực hành lập trình hoặc nghiên cứu bài báo. Hướng thực hành kết hợp phân tích thuật toán, đọc mã nguồn, viết code và thí nghiệm. Hướng nghiên cứu tập trung vào câu hỏi, phương pháp, bằng chứng, tái lập kết quả và đánh giá giới hạn của bài báo. Mỗi phần trong bài đều nêu việc cần làm, thời lượng và điều kiện dừng; bạn có thể điều chỉnh theo nền tảng và thời gian của mình.

Bài mới bắt đầu bằng vài câu ôn lại. Thử dựng lại lập luận hoặc dự đoán kết quả trước khi mở đáp án. Nếu dự đoán sai, tìm một ví dụ nhỏ để xác định giả định còn thiếu. Bạn có thể mở lời giải bất cứ lúc nào và học bài tiếp theo mà không cần nộp bài.

## Khám phá chủ đề

- **[Bản đồ chủ đề](references/topic-map.md):** xem mục tiêu thực hành và kiến thức nền cần có.
- **[Danh sách học phần IUH](references/topic-notes.md):** tên/mã học phần kèm câu hỏi tự học viết mới.

Trong Codex, nhắn **“Bài hôm nay”** hoặc **“Dùng $cs-daily-deep-study để viết bài hôm nay.”** Thêm chủ đề, công cụ đang có hoặc thời lượng mong muốn nếu cần. Công cụ chọn chủ đề thạc sĩ IUH chưa có bài và đã có bài về kiến thức nền, trước khi chuyển sang phần tiến sĩ. Nếu cùng ngày đã có bài, công cụ trả lại bài đó. Agent soạn hai bản tiếng Việt và tiếng Anh với lab C# hoặc T-SQL, chạy kiểm tra rồi mở PR. Bạn có thể tự merge trên GitHub hoặc yêu cầu agent merge. Bài học được tạo khi bạn yêu cầu, không theo lịch tự động.

Chuỗi bài dựa trên danh sách tên học phần IUH thạc sĩ (2020) và tiến sĩ (2022); mục tiêu tự học và yêu cầu kiến thức nền được viết riêng cho dự án. Bản đồ cho biết chủ đề nào đã có bài, không đánh giá mức nắm vững của người học. Bài học và lab được lưu công khai trên GitHub; dự án không lưu câu trả lời hay tiến độ cá nhân. Cách thiết lập repo và kiểm tra bài nằm trong [hướng dẫn bảo trì](https://github.com/nguyenan97/computer-science-learning-agent/blob/main/docs/maintaining.md).

Văn bản gốc: **CC BY 4.0**. Code gốc: **MIT**. Xem [giấy phép và ghi nhận nguồn](docs/licensing.md).
