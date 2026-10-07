# Lab C# - Transaction và phục hồi

Dùng .NET SDK **10.0.401** (latestPatch), **net10.0**, Microsoft.Data.Sqlite **10.0.9**, SQLitePCLRaw.bundle_e_sqlite3 **3.0.3** và lock file trong repo. Engine là **SQLite 3.50.4**. Restore đầu cần NuGet; các lần no-restore với package đã cache không cần database server.

Tải [ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/transactions-recovery/dotnet-lab.zip), giải nén và chạy trong `dotnet`; checkout dùng `labs/transactions-recovery/dotnet`.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Demo: hai lần đọc ghi mù cùng thấy mười, cả hai request commit, tồn=5 và đặt giữ=12. Retry có kiểm tra để lại ba, đặt giữ bảy và từ chối request năm. `--check` in `PASS: 225 serial-oracle schedules; stale snapshot=517; rollback/replay; 2 crash boundaries.` Kiểm tra có mô hình nhận request tuần tự độc lập, nâng snapshot đang giữ lên ghi, rollback do lỗi chủ động, danh tính request và payload không khớp.

`--experiment` in sáu dòng CSV và hai dòng phục hồi. Nó đếm kết quả/xung đột/retry, không đo thời gian hay throughput. Nhánh Blind cố ý vi phạm quy tắc bảo toàn một mặt hàng. Các task sở hữu connection/cache riêng, dùng cổng xác nhận thay vì sleep. WAL có một writer. DefaultTimeout=1 giới hạn chờ của provider; 0 sẽ chờ không cận.

Ca crash chỉ khởi chạy chính executable làm child, báo trước/sau commit, rồi parent dừng child đó và mở lại. Chuyển mười giữa tài khoản và 64 blob phụ giúp tạo bằng chứng WAL. Trước commit: số dư 100/100, dòng phụ 0. Sau commit: 90/110, dòng phụ 64. Có kiểm tra kích thước WAL nhưng số byte chính xác có thể khác. Hệ điều hành/lưu trữ vẫn hoạt động nên đây là crash tiến trình, chưa chứng nhận mất điện.

Fixture chỉ tạo/xóa thư mục tạm do chính nó sinh, dùng WAL/FULL và tắt autocheckpoint cho thí nghiệm. Tồn 0-1000, lượng 1-1000, mã request không trắng tối đa 100 ký tự. Chưa mô hình hóa nhập thêm/hủy/reset đồng thời; retry có một lần từ dữ liệu mới trong thứ tự hai client đã chọn. Chế độ nội bộ `--child` dành cho parent, không phải lệnh dùng database ứng dụng.

Mã nguồn: [Store.cs](LessonLab/Store.cs), [Schedules.cs](LessonLab/Schedules.cs), [Crash.cs](LessonLab/Crash.cs), [Checks.cs](LessonLab/Checks.cs), [Experiment.cs](LessonLab/Experiment.cs), [Program.cs](LessonLab/Program.cs), [project](LessonLab/LessonLab.csproj), [lock](LessonLab/packages.lock.json), [SDK](global.json), [MIT](LICENSE-MIT.txt).

[Bài đầy đủ](../../../vi/lessons/2026-10-10-transactions-recovery/lesson.md) có code, bảng chạy, đáp án riêng và phương án chỉ đọc khi chưa tạo được tiến trình con hoặc cài đặt. ZIP chứa source/cấu hình, không chứa SDK/binary package/database. C# tự viết theo MIT; nội dung CC BY 4.0; dependency giữ điều khoản riêng. Source SQLite được dẫn tại commit cố định, không sao chép.
