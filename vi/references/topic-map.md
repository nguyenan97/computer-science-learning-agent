# Bản đồ tự học theo đề cương IUH

<!-- Generated from topics.json and lessons/catalog.json. -->

Map theo danh sách tên học phần trong đề cương IUH thạc sĩ (2020) và tiến sĩ (tháng 10/2022). Prerequisite và mục tiêu tự học do project thiết kế. Độ phủ đếm bài đã xuất bản, không phải mức nắm vững, tín chỉ hay bằng cấp. Có cả tên học phần tự chọn để mở rộng kiến thức; đây không phải kế hoạch tốt nghiệp chính thức.

| Thạc sĩ / Tiến sĩ | Nhóm | Chủ đề có bài / đã hoạch định | Độ phủ |
|---|---|---:|---:|
| Thạc sĩ | AI và học máy | 0/7 | 0.0% |
| Thạc sĩ | Thuật toán | 3/5 | 60.0% |
| Thạc sĩ | Giao tiếp học thuật | 0/1 | 0.0% |
| Thạc sĩ | Dữ liệu và cơ sở dữ liệu | 0/3 | 0.0% |
| Thạc sĩ | Kiến thức chung | 0/1 | 0.0% |
| Thạc sĩ | Thông tin và mô hình | 0/1 | 0.0% |
| Thạc sĩ | Lãnh đạo và rủi ro | 0/2 | 0.0% |
| Thạc sĩ | Phương pháp nghiên cứu | 0/3 | 0.0% |
| Thạc sĩ | Bảo mật | 0/1 | 0.0% |
| Thạc sĩ | Thống kê | 0/2 | 0.0% |
| Thạc sĩ | Hệ thống | 0/4 | 0.0% |
| Thạc sĩ | Trực quan hóa | 0/1 | 0.0% |
| Tiến sĩ | AI và học máy | 0/2 | 0.0% |
| Tiến sĩ | Thông tin và mô hình | 0/1 | 0.0% |
| Tiến sĩ | Phương pháp nghiên cứu | 0/4 | 0.0% |
| Tiến sĩ | Bảo mật | 0/1 | 0.0% |
| Tiến sĩ | Hệ thống | 0/4 | 0.0% |

**Tổng chủ đề đã hoạch định: 3/43.**

[Danh sách học phần và câu hỏi tự học viết mới](topic-notes.md)

## Hợp đồng chương trình và bất biến

- **Đã có bài** · Thạc sĩ · Thuật toán · `build`
- **Nền tảng:** —
- **Mục tiêu:** Trace vòng lặp, nêu bất biến và dựng phản ví dụ cho quy tắc biên sai.
- **Thực hành:** Viết checker theo bảng cho dữ liệu rỗng, trùng lặp và ở biên.

## Dedupe giữ thứ tự và mô hình chi phí

- **Đã có bài** · Thạc sĩ · Thuật toán · `build`
- **Nền tảng:** Hợp đồng chương trình và bất biến
- **Mục tiêu:** Chọn scan hoặc hash theo ràng buộc thứ tự/bằng nhau/bộ nhớ, giải thích số phép tính riêng với thời gian đo.
- **Thực hành:** Implement, kiểm tra collision và benchmark scan với HashSet trên dữ liệu có kiểm soát.

## Tìm biên và truy vấn có thứ tự

- **Đã có bài** · Thạc sĩ · Thuật toán · `build`
- **Nền tảng:** Hợp đồng chương trình và bất biến
- **Mục tiêu:** Suy ra lower/upper bound và đếm cửa sổ nửa mở với số lần truy cập logarithm.
- **Thực hành:** Đọc bisect ở pin, trace dữ liệu trùng, kiểm tra số truy cập và áp dụng cho cửa sổ timestamp.

## Đồ thị và chọn chiến lược

- **Chưa có bài** · Thạc sĩ · Thuật toán · `build`
- **Nền tảng:** Hợp đồng chương trình và bất biến
- **Mục tiêu:** Chọn BFS hay Dijkstra theo giả thiết trọng số và đưa phản ví dụ khi chọn sai.
- **Thực hành:** Viết bộ tìm đường, so sánh node đã thăm và tính đúng đường đi.

## Quy hoạch động và xấp xỉ

- **Chưa có bài** · Thạc sĩ · Thuật toán · `build`
- **Nền tảng:** Đồ thị và chọn chiến lược
- **Mục tiêu:** Định nghĩa state/công thức truy hồi, so phản ví dụ greedy và chặn chất lượng cho một bài tối ưu.
- **Thực hành:** Viết oracle chính xác nhỏ và so heuristic trên dữ liệu sinh.

## Lưu trữ, chỉ mục và query plan

- **Chưa có bài** · Thạc sĩ · Dữ liệu và cơ sở dữ liệu · `build`
- **Nền tảng:** Tìm biên và truy vấn có thứ tự
- **Mục tiêu:** Giải thích seek với scan theo selectivity, thứ tự và chi phí cập nhật bằng query plan thật.
- **Thực hành:** Nạp database cục bộ, đọc plan và đo workload có/không có index.

## Transaction, đồng thời và phục hồi

- **Chưa có bài** · Thạc sĩ · Dữ liệu và cơ sở dữ liệu · `build`
- **Nền tảng:** Lưu trữ, chỉ mục và query plan
- **Mục tiêu:** Tái hiện một anomaly isolation và giải thích cơ chế ngăn chặn/phục hồi đã chọn.
- **Thực hành:** Chạy hai client đồng thời với lịch thực thi ghi lại và trace crash/recovery.

## Xác suất, ước lượng và độ bất định

- **Chưa có bài** · Thạc sĩ · Thống kê · `build`
- **Nền tảng:** —
- **Mục tiêu:** Diễn giải biến thiên lấy mẫu và khoảng tin cậy, không xem một lần chạy là kết quả phổ quát.
- **Thực hành:** Mô phỏng mẫu, vẽ phân phối và kiểm tra giả thiết với seed tái lập.

## Thiết kế thí nghiệm và giới hạn nhân quả

- **Chưa có bài** · Thạc sĩ · Thống kê · `build`
- **Nền tảng:** Xác suất, ước lượng và độ bất định
- **Mục tiêu:** Kiểm soát một thí nghiệm, báo bất định và phân biệt tương quan với kết luận nhân quả.
- **Thực hành:** So baseline/treatment, kiểm tra confound trong notebook tái lập.

## Hệ học và đánh giá trung thực

- **Chưa có bài** · Thạc sĩ · AI và học máy · `build`
- **Nền tảng:** Thiết kế thí nghiệm và giới hạn nhân quả
- **Mục tiêu:** Xây baseline, tránh leakage và giải thích trade-off metric trên tập hold-out.
- **Thực hành:** Fit mô hình nhỏ, đọc lỗi và so với baseline quy tắc đơn giản.

## Mạng neural và tối ưu

- **Chưa có bài** · Thạc sĩ · AI và học máy · `build`
- **Nền tảng:** Hệ học và đánh giá trung thực
- **Mục tiêu:** Chẩn đoán overfitting hoặc lỗi tối ưu bằng loss curve và một can thiệp có kiểm soát.
- **Thực hành:** Implement mạng nhỏ, kiểm tra gradient và làm ablation có mục tiêu.

## Mô hình ngôn ngữ và đánh giá truy hồi

- **Chưa có bài** · Thạc sĩ · AI và học máy · `build`
- **Nền tảng:** Hệ học và đánh giá trung thực
- **Mục tiêu:** Đánh giá một pipeline text/retrieval bằng phân loại lỗi và giới hạn dữ liệu rõ ràng.
- **Thực hành:** So truy hồi lexical với embedding và phân tích query thất bại.

## Xử lý ảnh và thị giác

- **Chưa có bài** · Thạc sĩ · AI và học máy · `build`
- **Nền tảng:** Mạng neural và tối ưu
- **Mục tiêu:** Giải thích lựa chọn biểu diễn và đánh giá robustness cho tác vụ ảnh cụ thể.
- **Thực hành:** So biến đổi cổ điển với baseline học khi perturb có kiểm soát.

## Song song và đồng bộ

- **Chưa có bài** · Thạc sĩ · Hệ thống · `build`
- **Nền tảng:** Hợp đồng chương trình và bất biến
- **Mục tiêu:** Tái hiện race, sửa đồng bộ và giải thích giới hạn scale từ work/overhead đo được.
- **Thực hành:** So implement tuần tự/song song, kiểm tra đúng và contention.

## Dữ liệu phân tán và chịu lỗi

- **Chưa có bài** · Thạc sĩ · Hệ thống · `build`
- **Nền tảng:** Transaction, đồng thời và phục hồi, Song song và đồng bộ
- **Mục tiêu:** Trace failure/retry và giải thích lựa chọn consistency/idempotency.
- **Thực hành:** Chèn giao nhận lặp và process failure vào pipeline cục bộ nhỏ.

## Mạng và truyền thông

- **Chưa có bài** · Thạc sĩ · Hệ thống · `build`
- **Nền tảng:** Hợp đồng chương trình và bất biến
- **Mục tiêu:** Giải thích latency, throughput và hành vi giao thức từ trace request.
- **Thực hành:** Đo client/server cục bộ, kiểm tra retry, timeout và giả thiết congestion.

## Bảo mật và threat modeling

- **Chưa có bài** · Thạc sĩ · Bảo mật · `build`
- **Nền tảng:** Mạng và truyền thông
- **Mục tiêu:** Nêu tài sản/trust boundary và kiểm tra một biện pháp với tình huống tấn công tái lập.
- **Thực hành:** Viết harness cô lập cho authorization, xử lý input hoặc sử dụng crypto sai.

## Pipeline cloud và observability

- **Chưa có bài** · Thạc sĩ · Hệ thống · `build`
- **Nền tảng:** Dữ liệu phân tán và chịu lỗi
- **Mục tiêu:** Lập luận delivery, chi phí và recovery của pipeline từ sự kiện đo được.
- **Thực hành:** Prototype cục bộ trước, chèn fault và ghi giả thiết latency/chi phí trước cloud tùy chọn.

## Lý thuyết thông tin và mô phỏng

- **Chưa có bài** · Thạc sĩ · Thông tin và mô hình · `paper`
- **Nền tảng:** Xác suất, ước lượng và độ bất định
- **Mục tiêu:** Nối entropy hoặc mô hình ngẫu nhiên với một câu hỏi kỹ thuật đo được.
- **Thực hành:** Mô phỏng kênh hoặc queue, so phân phối dự đoán với quan sát.

## Đọc, tái lập và tổng hợp nghiên cứu

- **Chưa có bài** · Thạc sĩ · Phương pháp nghiên cứu · `paper`
- **Nền tảng:** Thiết kế thí nghiệm và giới hạn nhân quả
- **Mục tiêu:** Nêu câu hỏi có thể bác bỏ, tái lập claim có giới hạn và tách evidence với suy luận.
- **Thực hành:** Đọc methods/code, chạy tái lập nhỏ và viết log claim–evidence–giới hạn.

## Khám phá dữ liệu và trình bày

- **Chưa có bài** · Thạc sĩ · Trực quan hóa · `build`
- **Nền tảng:** Xác suất, ước lượng và độ bất định
- **Mục tiêu:** Chọn cách trực quan hóa trung thực và chẩn đoán biểu diễn gây hiểu lầm.
- **Thực hành:** Vẽ EDA, kiểm tra missing/outlier và giải thích một quyết định dựa trên dữ liệu.

## Triết học

- **Chưa có bài** · Thạc sĩ · Kiến thức chung · `paper`
- **Nền tảng:** —
- **Mục tiêu:** Giả định nào khiến một nhận định khoa học kiểm chứng được, và bằng chứng nào bác bỏ nó?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Tiếng Anh

- **Chưa có bài** · Thạc sĩ · Giao tiếp học thuật · `paper`
- **Nền tảng:** —
- **Mục tiêu:** Viết lại một nhận định kỹ thuật bằng tiếng Anh thế nào để không nói quá bằng chứng?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Trí tuệ nhân tạo nâng cao

- **Chưa có bài** · Thạc sĩ · AI và học máy · `build`
- **Nền tảng:** Xác suất, ước lượng và độ bất định
- **Mục tiêu:** Khi nào bằng chứng đổi dự đoán xác suất, và kiểm tra phép cập nhật ra sao?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Phân tích văn bản và web

- **Chưa có bài** · Thạc sĩ · AI và học máy · `build`
- **Nền tảng:** Mô hình ngôn ngữ và đánh giá truy hồi
- **Mục tiêu:** Tài liệu trùng và thiên lệch thu thập làm lệch thí nghiệm truy xuất ra sao?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Phát triển năng lực lãnh đạo

- **Chưa có bài** · Thạc sĩ · Lãnh đạo và rủi ro · `paper`
- **Nền tảng:** —
- **Mục tiêu:** Nhóm quyết định kỹ thuật thế nào để giữ ý kiến khác biệt và trách nhiệm?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Phân tích rủi ro

- **Chưa có bài** · Thạc sĩ · Lãnh đạo và rủi ro · `paper`
- **Nền tảng:** Xác suất, ước lượng và độ bất định
- **Mục tiêu:** Quyết định nào thay đổi khi xác suất và thiệt hại của lỗi đều bất định?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Chuyên đề

- **Chưa có bài** · Thạc sĩ · Phương pháp nghiên cứu · `paper`
- **Nền tảng:** Đọc, tái lập và tổng hợp nghiên cứu
- **Mục tiêu:** Giới hạn một câu hỏi kỹ thuật mới ra sao để reproduce được một kết quả liên quan?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Nhận dạng và phân tích mẫu

- **Chưa có bài** · Thạc sĩ · AI và học máy · `build`
- **Nền tảng:** Hệ học và đánh giá trung thực
- **Mục tiêu:** Điều gì đổi khi chi phí false positive khác false negative?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Ứng dụng phân tích dữ liệu

- **Chưa có bài** · Thạc sĩ · Dữ liệu và cơ sở dữ liệu · `build`
- **Nền tảng:** Thiết kế thí nghiệm và giới hạn nhân quả
- **Mục tiêu:** Phân tích tái lập có tách được quyết định làm sạch dữ liệu khỏi kết luận cuối không?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Luận văn thạc sĩ

- **Chưa có bài** · Thạc sĩ · Phương pháp nghiên cứu · `paper`
- **Nền tảng:** Đọc, tái lập và tổng hợp nghiên cứu
- **Mục tiêu:** Có thể nêu câu hỏi nghiên cứu khả thi, baseline và quy trình đánh giá trong đề xuất không?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Học sâu

- **Chưa có bài** · Tiến sĩ · AI và học máy · `paper`
- **Nền tảng:** Mạng neural và tối ưu
- **Mục tiêu:** Ablation nào thách thức cơ chế mà paper học sâu tuyên bố?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Phân tích dữ liệu lớn

- **Chưa có bài** · Tiến sĩ · Hệ thống · `build`
- **Nền tảng:** Dữ liệu phân tán và chịu lỗi
- **Mục tiêu:** Kết quả phân tán có tái lập được khi đổi cỡ workload và điều kiện lỗi không?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Công nghệ mạng và truyền thông hiện đại

- **Chưa có bài** · Tiến sĩ · Hệ thống · `paper`
- **Nền tảng:** Mạng và truyền thông
- **Mục tiêu:** Giả định về workload và độ trễ nào giới hạn nhận định nghiên cứu mạng?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Thị giác máy tính nâng cao

- **Chưa có bài** · Tiến sĩ · AI và học máy · `paper`
- **Nền tảng:** Xử lý ảnh và thị giác, Học sâu
- **Mục tiêu:** Kết quả thị giác có đứng vững khi đổi cảnh, camera hoặc phân bố đánh giá không?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## An toàn hệ thống thông tin hiện đại

- **Chưa có bài** · Tiến sĩ · Bảo mật · `paper`
- **Nền tảng:** Bảo mật và threat modeling
- **Mục tiêu:** Thay đổi threat model nào làm mất hiệu lực phép so sánh của paper bảo mật?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Tính toán hiệu năng cao

- **Chưa có bài** · Tiến sĩ · Hệ thống · `build`
- **Nền tảng:** Song song và đồng bộ
- **Mục tiêu:** Nút thắt phần cứng nào giải thích khả năng mở rộng, và tách nó khỏi nhiễu đo ra sao?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Lập trình song song cho hệ đa lõi

- **Chưa có bài** · Tiến sĩ · Hệ thống · `build`
- **Nền tảng:** Song song và đồng bộ, Tính toán hiệu năng cao
- **Mục tiêu:** Thiết kế đồng bộ có giữ tính đúng và giảm tranh chấp khi đổi lịch chạy không?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Kỹ thuật mô hình hóa và mô phỏng

- **Chưa có bài** · Tiến sĩ · Thông tin và mô hình · `build`
- **Nền tảng:** Lý thuyết thông tin và mô phỏng
- **Mục tiêu:** Quan sát nào xác thực bộ mô phỏng, và dự đoán nào nằm ngoài miền đã hiệu chỉnh?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Tổng quan tài liệu

- **Chưa có bài** · Tiến sĩ · Phương pháp nghiên cứu · `paper`
- **Nền tảng:** Đọc, tái lập và tổng hợp nghiên cứu
- **Mục tiêu:** Tổ chức các paper mâu thuẫn theo giả định và bằng chứng thay vì ngày xuất bản ra sao?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Chuyên đề nghiên cứu 1

- **Chưa có bài** · Tiến sĩ · Phương pháp nghiên cứu · `paper`
- **Nền tảng:** Tổng quan tài liệu
- **Mục tiêu:** Reproduce baseline đủ sát để xác định một câu hỏi chưa giải quyết ra sao?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Chuyên đề nghiên cứu 2

- **Chưa có bài** · Tiến sĩ · Phương pháp nghiên cứu · `paper`
- **Nền tảng:** Chuyên đề nghiên cứu 1
- **Mục tiêu:** Thí nghiệm nào có thể bác bỏ cải tiến đề xuất, kể cả kết quả không đổi hoặc âm?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.

## Luận án tiến sĩ

- **Chưa có bài** · Tiến sĩ · Phương pháp nghiên cứu · `paper`
- **Nền tảng:** Chuyên đề nghiên cứu 2
- **Mục tiêu:** Đóng góp nào còn đứng vững sau so sánh, tái lập và nêu rõ giới hạn?
- **Thực hành:** Dựng một trường hợp có lời giải, đối chiếu với phản ví dụ và viết giới hạn của lập luận thu được.
