# Lab C# - độ bất định khi lấy mẫu

Dùng SDK **10.0.401**, runtime **10.0.12**, target **net10.0**; không cho roll-forward. Không có NuGet package ngoài; restore kiểm tra lock file. Chạy từ thư mục `dotnet` sau khi giải nén ZIP.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Demo chạy prefix 1,0,1,0,0; kiểm tra in `PASS: 20300 score inversions; binary-sequence weights; endpoints; seed; validation.` Experiment in 11 dòng so phương pháp/cỡ mẫu/nhóm và ghi `distribution.csv` ở thư mục hiện tại. Seed 101/202/303 tái lập dữ liệu giả lập, chưa chứng minh độc lập hoặc chất lượng RNG. Không dùng generator cho bảo mật.

Không đo latency và không chạy SQL Server/SciPy/R. Mô hình dùng p cố định, đơn vị đã xác định và nhóm cùng kích thước/cùng kết quả khi được nêu. Độ bao phủ Wilson hữu hạn có thể dưới 95%. Đối chiếu score kiểm tra công thức, chưa chứng nhận độ bao phủ production. Nếu chưa chạy được, đọc code, bảng và biểu đồ trong bài; không coi kết quả đọc là quan sát tự chạy.

Mã nguồn: [Stats.cs](LessonLab/Stats.cs), [Draws.cs](LessonLab/Draws.cs), [Checks.cs](LessonLab/Checks.cs), [Experiment.cs](LessonLab/Experiment.cs), [Program.cs](LessonLab/Program.cs), [project](LessonLab/LessonLab.csproj), [lock](LessonLab/packages.lock.json), [SDK](global.json), [MIT](LICENSE-MIT.txt).

[Bài đầy đủ](../../../vi/lessons/2026-10-11-sampling-uncertainty/lesson.md)
