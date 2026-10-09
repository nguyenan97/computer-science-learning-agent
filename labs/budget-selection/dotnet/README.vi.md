# Lab C# - Chọn công việc bằng DP và xấp xỉ

Tắt roll-forward cho SDK/runtime: dùng SDK 10.0.401 và runtime 10.0.12.

Dùng .NET SDK **10.0.401**, pin trong `global.json`, target **net10.0**. Không cần package ngoài hay database. Nếu thiếu, cài SDK từ [Microsoft](https://dotnet.microsoft.com/en-us/download/dotnet/10.0).

Tải [ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/budget-selection/dotnet-lab.zip), giải nén rồi chạy trong `dotnet`. Nếu dùng checkout, vào `labs/budget-selection/dotnet`.

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

```text
Exact: value=10, cost=6, ids=B,C
Density: value=7, cost=4, ids=A
HalfApprox: value=7, cost=4, ids=A
PASS: 12226 instances checked against exhaustive optimum, feasibility and half guarantee.
```

Ba dòng đầu là demo; dòng cuối là `--check`. Kiểm tra đối chiếu hai bản DP với vét cạn tập con độc lập, xác minh tập con trả về và bảo đảm 1/2, đồng thời xét lỗi input, số học và tài nguyên. `--experiment` in 52 dòng dữ liệu CSV từ 13 ca có kiểm soát, tách đơn vị thao tác và số lần so sánh tỷ lệ. Chưa đo thời gian, hiệu năng query SQL hay latency worker.

Sau lần build đầu thành công, thêm `--no-restore` để chạy offline. Nếu thiếu SDK, đọc mã đầy đủ, bảng chạy và lời giải trong [bài học](../../../vi/lessons/2026-10-08-dp-approximation/lesson.md). Trong checkout, `python scripts/check_all.py` chuẩn bị môi trường được hỗ trợ và kiểm tra bản sao lab tạm.

ID phải không rỗng và duy nhất khi so sánh ordinal. Chi phí nguyên dương; giá trị không âm; ngân sách không âm. Tổng giá trị mọi công việc, kể cả công việc quá ngân sách, phải vừa `long`. Bảng đầy đủ và mảng nén giới hạn 2.000.000 ô; vét cạn nhận tối đa 22 công việc. Vượt giới hạn sẽ ném lỗi, không âm thầm đổi sang xấp xỉ. Bảo đảm 1/2 giả định một ngân sách, công việc nguyên vẹn, độc lập và giá trị cộng dồn. Khi hòa, các nghiệm không nhất thiết có cùng tập con.

Mã nguồn:

- [Budget.cs](LessonLab/Budget.cs)
- [Oracle.cs](LessonLab/Oracle.cs)
- [Program.cs](LessonLab/Program.cs)
- [Checks.cs](LessonLab/Checks.cs)
- [Experiment.cs](LessonLab/Experiment.cs)
- [LessonLab.csproj](LessonLab/LessonLab.csproj)
- [global.json](global.json)
- [MIT](LICENSE-MIT.txt)

Toàn bộ code lab tự viết theo MIT. Nội dung theo CC BY 4.0. Bài dẫn link và phân tích PostgreSQL cùng sách; không phát hành lại mã của chúng hay PDF sách.
