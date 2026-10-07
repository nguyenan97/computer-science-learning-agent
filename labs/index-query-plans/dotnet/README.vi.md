# Lab C# - Index và query plan

Dùng .NET SDK **10.0.401**, target **net10.0**, Microsoft.Data.Sqlite **10.0.9** và SQLitePCLRaw.bundle_e_sqlite3 **3.0.3**. Engine đi kèm trả **SQLite 3.50.4**. Project và lock file pin dependency; lần restore đầu cần NuGet. Không cần database server.

Tải [ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/index-query-plans/dotnet-lab.zip), giải nén rồi chạy trong `dotnet`. Nếu dùng checkout, vào `labs/index-query-plans/dotnet`.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Demo in số dòng 18, tổng Amount 198 ở mọi cấu hình: không index phụ cho SCAN, index gọn cho SEARCH USING INDEX, covering cho SEARCH USING COVERING INDEX. Chuỗi plan là chẩn đoán theo phiên bản, không phải API ổn định cho ứng dụng.

`--check` in `PASS: 11416 aggregate comparisons; index maintenance, plans and rollback checked.` Nó đối chiếu cả bốn cách truy cập với phép quét điều kiện C# độc lập, xét biên khoảng, update/delete/insert và rollback batch khi xung đột. `--experiment` in 12 dòng dữ liệu CSV cùng comment cấu hình/plan: chín phép so đọc và ba cấu hình insert. Có median/min/max đo lặp và byte database cấp phát logic. Thời gian thay đổi giữa các lần; kết quả local cache ấm chưa xác lập hiệu năng SQL Server hay p99 production.

Mỗi instance chỉ tạo và xóa thư mục tạm do nó sinh ra. Lab dùng một connection, page_size 4096, journal DELETE, synchronous FULL. ID duy nhất 1-50000, tenant dương, thời điểm nguyên có dấu kiểu long, Amount 0-1000. Các cận giữ tổng an toàn. Khoảng rỗng hợp lệ, mốc đảo thứ tự bị từ chối. Không thể lấy dòng long.MaxValue bằng mốc cuối nửa mở lớn hơn nhưng vẫn biểu diễn được.

Sau restore, lệnh no-restore dùng package đã cache để chạy offline. ZIP chỉ có source và cài đặt, không chứa SDK, binary package hay database. Nếu thiếu môi trường, đọc mã/plan/đáp án đầy đủ trong [bài học](../../../vi/lessons/2026-10-09-index-query-plans/lesson.md). Trong checkout, `python scripts/check_all.py` kiểm tra bản sao tạm và ZIP đã giải nén.

Mã nguồn:

- [Database.cs](LessonLab/Database.cs)
- [Program.cs](LessonLab/Program.cs)
- [Checks.cs](LessonLab/Checks.cs)
- [Experiment.cs](LessonLab/Experiment.cs)
- [LessonLab.csproj](LessonLab/LessonLab.csproj)
- [packages.lock.json](LessonLab/packages.lock.json)
- [global.json](global.json)
- [MIT](LICENSE-MIT.txt)

Code lab tự viết theo MIT; nội dung bài theo CC BY 4.0. Bài phân tích source SQLite tại commit cố định, không sao chép code. Package bên thứ ba giữ điều khoản giấy phép riêng.
