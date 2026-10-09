# Lab C# - Thiết kế thí nghiệm

Dùng SDK 10.0.401, runtime Microsoft.NETCore.App 10.0.12, net10.0; tắt roll-forward và restore locked mode. Không có NuGet dependency ngoài. Chạy từ `dotnet` sau giải nén ZIP.

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Demo cho D=-2, oracle giả lập -4, p sharp null 54/64. Check đối chiếu 64 cách gán với quét hai nhánh độc lập, xét 6561 bảng kết quả tiềm năng nhỏ, phương sai, mức lỗi null, trường hợp bằng nhau và đầu vào. Experiment tạo `assignments.csv`: bốn nhóm, mỗi nhóm đủ 64 mask, tổng 256 dòng dữ liệu. Đây là outcome giả lập gắn đơn vị mili giây, không phải đo latency. Mask 21 chọn sẵn; chương trình liệt kê thiết kế toán học đồng xác suất, chưa chạy hệ thống gán/RNG thực. Không gọi mạng hoặc database.

Bài có đầy đủ code, công thức, bảng chạy từng bước và lời giải đổi ngữ cảnh. Nếu thiếu SDK, đọc chúng và CSV để đối chiếu bằng tay. Không bỏ pin để gọi là cùng thí nghiệm. p-value cần đúng thiết kế cặp và sharp null từng đơn vị; không phải xác suất null đúng, khoảng cho tác động trung bình hay phân tích dùng được cho mọi rollout. Chưa chạy SDK GrowthBook, integration SQL Server, dữ liệu thiếu hay ảnh hưởng chéo production.
