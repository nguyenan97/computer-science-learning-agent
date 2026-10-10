# Lab C# - Đánh giá trung thực

Dùng SDK 10.0.401, runtime Microsoft.NETCore.App 10.0.12 và net10.0, tắt roll-forward SDK/runtime. Không có dependency NuGet bên ngoài. Giải nén ZIP rồi chạy trong `dotnet`. Cài SDK/reference pack hoặc restore đầu có thể cần network; sau restore, các lệnh no-restore dưới đây không cần network.

```bash
dotnet --version
dotnet restore LessonLab
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
dotnet run --no-restore -c Release --project LessonLab -- --transfer
```

Demo học ngưỡng từ hai mươi ticket train, chọn trong bốn ứng viên bằng mười ticket validation, sau đó mới báo mười ticket test. Khách hàng không trùng giữa các tập. Ngưỡng chọn là 5; test TP/FP/FN/TN=2/3/1/4, chi phí 7 với FP=1/FN=4. Baseline ngưỡng 7 đã định trước có chi phí 5; không chọn lại theo test rồi gọi đó là bằng chứng chưa dùng.

Kiểm tra liệt kê 1554 tập nhỏ có thứ tự, hai chi phí và 3108 lần fit, đối chiếu bảng nhầm lẫn độc lập, xét hòa và guard input/cách chia. Thí nghiệm cố tình sao label tương lai vào feature và cho mô hình ghi nhớ thấy khách hàng test; cả hai đường không hợp lệ đều không phải mô hình triển khai. Bài vận dụng đổi trọng số ticket thành trọng số khách hàng bằng nhau.

Dữ liệu hoàn toàn giả lập và tất định. Đếm chính xác chưa chứng minh khả năng khái quát, calibration, tiết kiệm có quan hệ nhân quả hay ích lợi production. Chưa chạy integration sklearn, ML.NET, SQL Server hoặc Azure. Bài có đủ source/config, lập luận, output và đáp án riêng; có thể chỉ đọc nếu thiếu SDK đã pin. Đổi miền feature/bản pin làm đổi thí nghiệm.
