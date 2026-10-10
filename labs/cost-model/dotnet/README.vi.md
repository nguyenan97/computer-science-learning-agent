# Lab Bài 01 - C# / .NET

Tắt roll-forward cho SDK/runtime: dùng SDK 10.0.401 và runtime 10.0.12.

[English](README.md) · [Bài tiếng Việt](../../../vi/lessons/2026-10-05-cost-model/lesson.md)

Lab này dùng C# để loại bỏ duplicate, kiểm tra tính đúng và đo thời gian chạy,
lượng bộ nhớ cấp phát. Code lời giải nằm ở
[Core/Deduplication.cs](Core/Deduplication.cs). Bạn có thể sửa code trong bản sao
riêng để thực hành hoặc đọc code, trace và đáp án trong bài học khi chưa cài được lab.

## Chạy lab

Cài **.NET SDK**, không chỉ runtime. Phiên bản dùng để tái lập: SDK **10.0.401**,
runtime **10.0.12**, target **net10.0**. Có thể dùng Windows, macOS hoặc Linux;
lab đã được kiểm tra trên Linux. Không cần SQL Server, Docker hay Python.
Lab chính không dùng package bên thứ ba. Benchmark cần tải BenchmarkDotNet
**0.15.8** và các dependency qua NuGet, nên cần mạng khi restore lần đầu.

Clone repo hoặc tải trọn lab:

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

Nếu đã clone, chạy `git pull --ff-only` ở thư mục gốc repo trước. Nếu dùng ZIP,
giải nén và mở terminal trong thư mục `dotnet` có `global.json`, rồi chạy ba lệnh
`dotnet` ở trên.

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

Tám kiểm tra bao gồm: giữ thứ tự kết quả và không sửa input, các trường hợp biên,
comparer, cách xử lý null, số phép so sánh, chi phí tìm kiếm trên một bộ dữ liệu,
collision do test chủ động tạo ra và số lần xuất hiện của duplicate.
`CountScan` đếm phép so sánh theo mô hình chi phí của bài học; nó không đo toàn bộ
lệnh runtime bên trong `List.Contains`.

## Benchmark tùy chọn

Cũng ở thư mục `dotnet`, chạy bản Release và không gắn debugger:

```bash
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

PowerShell và bash đều nhận dấu nháy đơn này. Lần restore/build đầu tiên và 12
trường hợp benchmark có thể mất vài phút. `--job short` phù hợp cho thí nghiệm
trong bài học, chưa đủ để đánh giá tải production. Khi kiểm tra pipeline, có thể
đổi `short` thành `dry` để xem benchmark có chạy được không; không dùng số đo Dry
để kết luận tốc độ. Nếu sửa code, chạy lại kiểm tra tính đúng trước khi benchmark.

Input được tạo trong `GlobalSetup`, ngoài method được đo. Mỗi lần gọi method tạo
output và `HashSet` mới, không sửa input; BenchmarkDotNet sử dụng giá trị trả về.
Cả hai cách dùng `StringComparer.Ordinal` và giữ thứ tự xuất hiện đầu tiên.
Benchmark dùng N=128/512/2048 và tỷ lệ phần tử khác nhau danh nghĩa 10/100%; số
phần tử khác nhau thực tế là `max(1, floor(N * UniquePercent / 100))`. ID có độ dài
cố định. Dữ liệu thật có thể khác độ dài ID, tỷ lệ và thứ tự duplicate, cũng như
hành vi CPU/cache.

Đọc các cột Mean, Error, Ratio và Allocated cùng nhau. Allocated tính bộ nhớ cấp
phát cho output và hash table mới ở mỗi lần gọi, không tính input đã tạo sẵn.
Nó không đo mức bộ nhớ sử dụng cao nhất, lượng bộ nhớ còn sống sau GC hay GC/p99
của cả ứng dụng. Gen0 là tần suất thu gom thế hệ 0 được BenchmarkDotNet chuẩn hóa,
không phải số byte cấp phát.

Kết quả nằm ở `BenchmarkDotNet.Artifacts/results`. Khi chia sẻ, giữ phần thông tin
môi trường và các tham số input để người khác biết số đo đến từ đâu. Tỷ lệ tốc độ
trên một máy không bảo đảm hiệu năng của service. Không so sánh benchmark
`CountScan` với `Hash`: bộ đếm trong `CountScan` làm tăng công việc cần thực hiện.

## Gỡ lỗi và đọc khi chưa cài được lab

| Triệu chứng | Cách xử lý |
|---|---|
| Không tìm thấy `dotnet` | Cài SDK từ [Microsoft](https://dotnet.microsoft.com/download/dotnet/10.0), mở terminal mới, chạy `dotnet --list-sdks` |
| Thiếu SDK của `global.json` | Cài 10.0.401 hoặc patch tương thích mới hơn trong feature band 10.0.4xx; không cần đổi target của ứng dụng production |
| Không tìm thấy project | Kiểm tra thư mục hiện tại có Core, LessonLab, Benchmarks và global.json |
| NuGet restore lỗi | Kiểm tra kết nối mạng và NuGet; nếu offline, đọc code và kết quả mẫu trước |
| Benchmark không có kết quả hợp lệ | Đọc lỗi build và thông tin môi trường; dùng Release, không gắn debugger và chạy trong thư mục có quyền ghi |

Nếu chưa cài được lab, bạn vẫn có thể đọc trace, công thức và code lời giải trong
bài học. Chỉ dùng kết quả từ benchmark đã chạy để nhận xét về hiệu năng.

## Kiểm tra identity resolution tùy chọn

[Project](IdentityDemo/IdentityDemo.csproj), [mã đầy đủ](IdentityDemo/Program.cs), [lock file](IdentityDemo/packages.lock.json). Chạy từ `dotnet` với cùng SDK/runtime đã pin:

```bash
dotnet restore IdentityDemo --locked-mode
dotnet run --no-restore -c Release --project IdentityDemo
```
