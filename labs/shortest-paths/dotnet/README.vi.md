# Lab C# - BFS và Dijkstra

Dùng .NET SDK **10.0.401**, được pin trong `global.json`, với **net10.0**. Không cần package của bên thứ ba hay dịch vụ mạng. Nếu thiếu, cài SDK tương ứng từ [Microsoft](https://dotnet.microsoft.com/en-us/download/dotnet/10.0).

Tải [ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/shortest-paths/dotnet-lab.zip), giải nén và mở terminal trong thư mục `dotnet`. Nếu dùng repository, thư mục chạy là `labs/shortest-paths/dotnet`.

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

Demo so sánh một cạnh chi phí 10 với ba cạnh tổng chi phí 3. Kiểm tra đối chiếu với thuật toán tham chiếu độc lập dùng relaxation lặp, xác minh đường đi, chu trình 0, entry stale, lỗi đầu vào và giới hạn số học. Thí nghiệm in CSV đếm thao tác cho chuỗi trọng số 1 và chuỗi có trọng số kèm cạnh trực tiếp; không đo thời gian hay p99 dịch vụ.

Sau lần build đầu thành công, thêm `--no-restore` vào lệnh chạy để dùng offline. Nếu chưa có SDK, đọc toàn bộ implementation, bảng chạy từng bước và lời giải trong [bài học](../../../vi/lessons/2026-10-07-shortest-paths/lesson.md). Trong repository, chạy `python scripts/check_all.py` từ gốc để chuẩn bị môi trường được hỗ trợ và kiểm tra lab trên bản sao tạm.

Tạo đồ thị sẽ từ chối ID sai hoặc trọng số âm. BFS còn từ chối chi phí khác 1. `long.MaxValue` dành cho đỉnh không tới được; nếu ứng viên Dijkstra được xét đạt hoặc vượt giá trị đó, hàm ném `OverflowException`. Các đường đồng chi phí không bắt buộc có cùng dãy đỉnh; chỉ bảo đảm khoảng cách tối thiểu. Dãy đỉnh chưa xác định cạnh nào đã dùng nếu có cạnh song song.

Mã nguồn:

- [Đồ thị và hàm tìm đường](LessonLab/Routes.cs)
- [Demo](LessonLab/Program.cs)
- [Chương trình kiểm tra](LessonLab/Checks.cs)
- [Thí nghiệm](LessonLab/Experiment.cs)
- [Project](LessonLab/LessonLab.csproj) và [SDK pin](global.json)
- [Giấy phép MIT](LICENSE-MIT.txt)

Mã lab tự viết theo MIT, không chuyển thể mã OSRM. Nội dung bài theo CC BY 4.0. Bài chỉ dẫn link và phân tích OSRM, ghi nguồn theo BSD-2-Clause.
