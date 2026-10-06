# Kiểm chứng — ngày học sâu theo chủ đề

Bản ghi này mô tả check local trước merge ngày 2026-10-06, baseline `fe74583`. Trạng thái workflow release và deploy được ghi riêng trong GitHub Actions. Không đọc/migrate/sửa state riêng thật; các tình huống state dùng workspace tạm tổng hợp.

## Check đã chạy

- Test hồi quy runtime bao phủ completion cùng topic, kiến thức unknown/tự khai/đã quan sát, ngân sách full-day/ngắn, migration v1/v2 và giữ evidence, artifact riêng, repair link, due review và public/private isolation.
- Kiểm tra cấu hình CI có reusable validation gate, deploy chỉ main, quyền validation tối thiểu và checkout cùng `github.sha`. Đây là check cấu hình local; PR release còn phải pass CI GitHub trước merge.
- Generator chủ đề kiểm tra field song ngữ, ID duy nhất/không rỗng, prerequisite thiếu và cycle. Check drift map, navigation song ngữ và version contract chung.
- Lab Python: 4 check tìm biên và 4 check cost-model pass; quan sát count khớp ví dụ bài học.
- SDK .NET 10.0.401: 8 correctness check C# pass, command quan sát cho đúng output/count đã công bố. BenchmarkDotNet 0.15.8 chạy 12 case Dry. Dry kiểm tra harness, không dùng suy ra tốc độ; không claim ShortRun/production benchmark mới.

Check tích hợp: **47 unit test pass**; map/navigation/learning validator pass; site stage **76 file public**. Chromium kiểm tra **4 trang bài, 4 lần đổi ngôn ngữ, 4 lần bấm trước/sau, 97 link tài liệu nội bộ và 2 asset tải về**, giữ TLS verification. ZIP giải nén chạy **8 check C#** và build benchmark với 0 warning/error không cần repo checkout. Review hình trang chủ/bài học xác nhận nội dung render, navigation, không tràn ngang trang hay exception JavaScript runtime. Docsify phát sinh bốn request 404 khi tìm `_navbar.md`/`_sidebar.md` ở thư mục con, rồi tải menu đúng từ thư mục cha; đã kiểm tra đây không phải link bài học hỏng.

## Review nội dung và skill

[Skill mới](../../skills/cs-daily-deep-study/SKILL.md) cùng contract song ngữ quy định ngày đầy đủ, nộp bài tùy chọn, lời giải truy cập ngay, điều chỉnh theo evidence và không khóa ngày sau. Cả hai bài có giải thích đầy đủ trên trang, ví dụ chạy được, lời giải có lý do và footer liên quan/trước/sau tạo từ catalog. Toàn bộ ví dụ Python inline chạy được; hai method C# inline compile và pass check thứ tự, equality, case biên và null policy. Test navigation bao phủ đổi thứ tự, bài đầu/cuối, target không hợp lệ và symlink file/thư mục bài mà không ghi vào dữ liệu riêng hay cập nhật dở dang. [Bài mẫu cost-model](../lessons/2026-10-05-cost-model/lesson.md) có objective/commands/solutions/rubric/lịch Việt–Anh tương ứng: 420 phút = 360 học + 60 nghỉ; 235 phút active dự kiến (65.3%). Lịch là heuristic thiết kế; chưa đo thời gian học thật.

[Review learning science](learning-science-review.md) và [access log](../../research/deep-study-source-checks.json) tách phần full text đã đọc, abstract-only và nguồn chưa truy cập. [Attribution](content-provenance.md) giữ nguồn cũ mà không áp yêu cầu trường vào chọn bài. [Eval scenarios](../../skills/cs-daily-deep-study/evals/cases.json) là đặc tả tổng hợp, chưa phải benchmark model đã chạy.

## Giới hạn

Chưa có response độc lập của người học, đo retention/transfer sau độ trễ hay nghiên cứu hiệu quả giáo dục. Khớp objective/evidence về ngữ nghĩa, nguồn assistance và chất lượng dịch cần người chấm review; JSON matching không chứng minh được. Sequence chủ đề, tỷ lệ thời gian và nhãn mastery là lựa chọn của project. Không claim full upstream .NET/CPython suite, test Windows/macOS, deploy production live trong bản ghi local này, benchmark tốc độ mới có giá trị thống kê hay systematic literature review đầy đủ. License project chưa được chọn.
