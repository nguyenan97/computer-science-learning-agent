# Lab Bài 01 - C# / .NET

[English](README.md) · [Bài tiếng Việt](../../../vi/lessons/2026-10-05-cost-model/lesson.md)

Bài học dùng lab này để implement C# có hướng dẫn, debug và thí nghiệm
CPU/allocation. Lời giải đầy đủ ở [Core/Deduplication.cs](Core/Deduplication.cs).
Giữ attempt và ghi chú thí nghiệm trong bản riêng tư; lệnh chưa sửa chạy code mẫu,
chưa chứng minh người học làm độc lập. Thực hành/nộp bài đều tùy chọn, không nộp
vẫn được học ngày sau. Bài học có implementation C# đầy đủ, trace được giải thích
và đáp án thu gọn để đọc offline.

## Chạy lab nhỏ

Cài **.NET SDK**, không chỉ runtime. Phiên bản tái lập: SDK **10.0.401**, runtime
**10.0.12**, target **net10.0**. Windows, macOS hoặc Linux có SDK đó; không cần SQL
Server, Docker hay Python. Đã chạy trên Linux; chưa xác minh trên các OS khác.
Lab chính không dùng package bên thứ ba. Benchmark cần tải BenchmarkDotNet **0.15.8**
và dependency qua NuGet, nên cần mạng.

Clone repository hoặc tải trọn lab:

- [Repository](https://github.com/nguyenan97/computer-science-learning-agent)
- [ZIP của lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip)

Với bản clone:

```bash
git clone https://github.com/nguyenan97/computer-science-learning-agent.git
cd computer-science-learning-agent/labs/cost-model/dotnet
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

Nếu đã clone, chạy `git pull --ff-only` ở root repo trước. Nếu dùng ZIP, giải nén và
mở terminal trong thư mục `dotnet` chứa `global.json`; chạy ba lệnh `dotnet` như trên.

Kết quả để đối chiếu:

```text
Stable result: B2, A1, C3
Example scan comparisons: 6
n,scan_equality_comparisons,hash_add_calls (not hash-table work)
128,8128,128
256,32640,256
512,130816,512
128 identical IDs: 127 scan comparisons
Duplicates: B2=2, A1=2
```

Tám kiểm tra bao phủ thứ tự/input, case biên, comparer, chính sách null, mô hình đếm,
chi phí tìm kiếm ở một workload, collision cưỡng bức và đếm duplicate. Pass xác minh
code mẫu; không xác nhận người học đã thành thạo. `CountScan` là mô hình đếm phép
so sánh, không đo tất cả lệnh runtime bên trong `List.Contains`.

## Benchmark tùy chọn

Cũng ở thư mục `dotnet`, dùng Release và không gắn debugger:

```bash
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

PowerShell và bash đều nhận dấu nháy đơn này. Restore/build đầu tiên và 12 case có
thể mất vài phút. `--job short` dùng cho thí nghiệm học; chưa phải kiểm tra tải production.
Kiểm tra pipeline có thể đổi `short` thành `dry`; không dùng số đo Dry để kết luận
tốc độ. Nếu sửa code, chạy correctness check trước benchmark.

Input tạo trong `GlobalSetup`, ngoài phương thức được đo. Mỗi invocation tạo output
và HashSet mới, không sửa input; harness nhận giá trị trả về. Cả hai cách dùng cùng
ordinal equality và giữ thứ tự xuất hiện đầu. Ma trận có N=128/512/2048, phần trăm
distinct danh nghĩa 10/100; distinct thật là `max(1, floor(N * UniquePercent / 100))`.
ID có độ dài cố định. Dữ liệu thật có thể khác độ dài, phân bố/thứ tự duplicate và
hành vi CPU/cache.

Đọc Mean, Error, Ratio và Allocated cùng nhau. Allocated gồm output và bảng mới mỗi
invocation, không gồm input tạo sẵn. Nó **không phải** peak working set, heap sống sau
GC hay số đo GC/p99 của cả ứng dụng. Gen0 là tần suất collection được harness chuẩn
hóa, không phải số byte cấp phát.

Report ở `BenchmarkDotNet.Artifacts/results`. Giữ environment header và input khi
chia sẻ; không lấy ratio ở một máy làm cam kết hiệu năng service. Không benchmark
`CountScan` với Hash không có counter: instrumentation đã đổi workload.

## Gỡ lỗi và cách đọc không cần cài đặt

| Triệu chứng | Cách xử lý |
|---|---|
| Không tìm thấy `dotnet` | Cài SDK từ [Microsoft](https://dotnet.microsoft.com/download/dotnet/10.0), mở terminal mới, chạy `dotnet --list-sdks` |
| Thiếu SDK của `global.json` | Cài 10.0.401 hoặc patch tương thích mới hơn trong feature band 10.0.4xx; không cần đổi target ứng dụng production |
| Không tìm thấy project | Kiểm tra thư mục hiện tại có Core, LessonLab, Benchmarks và global.json |
| NuGet restore lỗi | Kiểm tra mạng/NuGet; có thể đọc code và kết quả lab nếu offline; benchmark chưa chạy không phải số đo |
| Benchmark không có kết quả hợp lệ | Đọc lỗi build/environment header; dùng Release, không debugger và thư mục có quyền ghi |

Nếu chưa cài được, trace, công thức và code có lời giải trong bài vẫn đủ cho đường
đọc-only. Benchmark cung cấp bằng chứng thực thi tùy chọn, không phải đánh giá người học.
