# Bài 01 — Big-O và cấu trúc dữ liệu: khử trùng mã đơn hàng bằng C#

**90 phút · Có nhánh học sâu 180+ phút · Cập nhật 05/10/2026**

[English](../../../lessons/2026-10-05-cost-model/lesson.md) · [Hướng dẫn lab C#](../../../labs/cost-model/dotnet/README.vi.md) · [Tải trọn lab ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip) · [Code có lời giải](../../../labs/cost-model/dotnet/Core/Deduplication.cs)

**Điều cần hiểu hôm nay:** cấu trúc dữ liệu quyết định chi phí của việc tìm kiếm bên trong vòng lặp. Đổi `List.Contains` sang `HashSet.Add` có thể giảm mạnh CPU, nhưng phải giữ đúng yêu cầu nghiệp vụ và kiểm tra chi phí bộ nhớ.

Bài dành cho người đã làm C#/.NET, API và database, đang củng cố nền tảng CS. Không cần học lại cú pháp vòng lặp hay REST. Phần phân tích toán được giải thích từ đầu; kinh nghiệm lập trình không tự chứng minh đã nắm Big-O.

Đây là nền tảng do người hướng dẫn chọn cho **Advanced Algorithms — IUH `6001127`**: phân tích độ phức tạp, hiệu năng và chọn thuật toán. Kết nối sang Advanced Database `6001111`. Không phải giáo án chính thức của IUH. Topic: `advanced-algorithms.cost-model-membership.l1`.

Sau bài, bạn có thể tự kiểm tra ba khả năng: giải thích tổng số phép so sánh; chọn cách khử trùng giữ thứ tự; đọc benchmark CPU/allocation với đúng giới hạn. **Mọi bài tập, lab và nộp bài đều tùy chọn, có lời giải ngay.** Đọc-only cũng là một cách học; không phải bằng chứng thành thạo độc lập.

## Lộ trình 90 phút

| Thời gian | Học gì | Nếu chỉ muốn đọc |
|---|---|---|
| 0–15 | Bài toán, yêu cầu và trace | Đọc ví dụ nhỏ, chưa cần cài gì |
| 15–40 | Đếm chi phí, hiểu Big-O | Theo từng bước suy luận |
| 40–60 | HashSet, correctness, bộ nhớ | Đọc code và invariant |
| 60–80 | Lab C# tùy chọn | Đối chiếu output đã chạy |
| 80–90 | Biến thể, recap | Đọc đề rồi lời giải |

Thời lượng tính cho **một bản ngôn ngữ**. Benchmark và đọc runtime nằm ở nhánh 180+ phút; không cần làm hết để bắt đầu ngày sau. Chưa có bài làm thật được đánh giá hay lượt ôn đến hạn.

## 1. Bắt đầu bằng một yêu cầu production nhỏ

Một job logistics nhận danh sách mã đơn từ log hoặc message batch. Một mã có thể xuất hiện nhiều lần. Trả về mỗi mã **một lần, theo thứ tự nó xuất hiện lần đầu**.

```text
Input : B2, A1, B2, C3, A1
Output: B2, A1, C3
```

Ba điều phải chốt trước khi tối ưu:

- So sánh chính xác bằng `StringComparer.Ordinal`: `a` khác `A`; không tự trim/lowercase.
- Giữ thứ tự xuất hiện đầu; sort thành `A1,B2,C3` là sai yêu cầu.
- Không sửa input. Input không null, mỗi ID không null; code lab từ chối null. Chuỗi rỗng vẫn là một giá trị hợp lệ trong ví dụ này.

Đây là khử trùng **trong một batch**, chưa phải xử lý message exactly-once.

**Tự kiểm tra tùy chọn:** có bao nhiêu phần tử, bao nhiêu mã khác nhau? Với output tạm `[B2,A1]`, muốn biết `C3` đã xuất hiện chưa cần làm gì?

**Lời giải:** có `n=5` phần tử và `u=3` mã khác nhau. Tìm `C3` bằng quét tuần tự phải kiểm tra cả `B2` lẫn `A1`. Nếu ý “phải tìm hết mới kết luận không có” chưa rõ, đọc trace dưới đây chậm một lượt; đó là prerequisite quan trọng của bài.

## 2. Một vòng lặp vẫn có thể làm rất nhiều việc

Cách quen thuộc:

```csharp
var result = new List<string>();
foreach (string id in values)
{
    if (!result.Contains(id))
        result.Add(id);
}
```

`Contains` của List tìm trong các phần tử đã có, dừng khi thấy mã bằng nhau. Khi không thấy, nó phải tìm hết. Một lời gọi API có thể chứa nhiều công việc mà code bên ngoài không hiện ra.

| ID đang đọc | `result` trước bước | Các so sánh tuần tự | `result` sau bước |
|---|---|---|---|
| B2 | [] | 0 | [B2] |
| A1 | [B2] | A1 với B2: 1 | [B2,A1] |
| B2 | [B2,A1] | B2 với B2: 1, dừng | [B2,A1] |
| C3 | [B2,A1] | C3 với B2 và A1: 2 | [B2,A1,C3] |
| A1 | [B2,A1,C3] | A1 với B2 rồi A1: 2, dừng | [B2,A1,C3] |

Tổng là **6 phép so sánh** trong mô hình quét này, dù chỉ có 5 lần đi qua `foreach`. Đây là mô hình thuật toán, chưa phải đo số lệnh CPU của runtime .NET.

### Trường hợp mọi mã khác nhau

Với `A,B,C,D`, số so sánh là `0,1,2,3`. Mã thứ k phải kiểm tra k−1 mã trước nó. Với n mã:

```text
C(n) = 0 + 1 + 2 + ... + (n−1) = n(n−1)/2
```

Có thể thấy công thức bằng cách viết tổng xuôi và ngược: mỗi cặp cùng vị trí cộng thành n−1; có n cặp. Hai tổng bằng `n(n−1)`, nên một tổng bằng một nửa.

| n, tất cả khác nhau | Số so sánh trong mô hình |
|---:|---:|
| 128 | 8.128 |
| 256 | 32.640 |
| 512 | 130.816 |
| 100.000 | 4.999.950.000 |

Đầu vào tăng gấp đôi, công việc gần gấp bốn. Chưa thể đổi những con số này thành milliseconds: CPU, runtime và dữ liệu đều ảnh hưởng thời gian thật.

## 3. Big-O trả lời câu hỏi nào?

**Mô hình chi phí (cost model)** nói rõ ta đang đếm gì. Ở đây, tạm coi một lần so sánh/hash một ID có chi phí bị chặn bởi hằng số; n là số phần tử. Đó là giả định để phân tích, không phải định luật về mọi chuỗi.

Big-O là **chặn trên của tốc độ tăng chi phí**: `T(n)` là `O(n²)` nếu tồn tại hằng số C và n₀ sao cho `T(n) ≤ Cn²` với mọi `n ≥ n₀`. Không có nghĩa “chạy n² giây”.

Với mọi ID khác nhau, `n(n−1)/2` có số hạng chủ đạo n², nên mô hình quét có **Θ(n²)**: cả chặn trên và dưới cùng bậc. Nói O(n²) đúng nhưng kém chặt hơn. Một thuật toán O(n) cũng thỏa chặn O(n²); vì vậy nên dùng bậc chặt khi giải thích.

**Nếu mọi ID đều là A?** Sau ID đầu, mỗi lần `Contains` tìm thấy ngay: chỉ n−1 so sánh, tức Θ(n). Độ phức tạp trường hợp xấu không nói mọi input đều chậm như nhau.

Với u mã khác nhau, List dài tối đa u; toàn bộ cách quét có chặn `O(n(1+u))`. Khi u nhỏ, nó có thể đủ tốt. Khi u tăng cùng n, trường hợp xấu trở thành bậc hai.

**Tự kiểm tra tùy chọn:** chỉ thấy một `foreach`, có thể kết luận O(n) không?

**Lời giải:** chưa. Phải tính tổng chi phí phần thân trên từng lần lặp. `Contains`, query database hoặc gọi service đều có chi phí riêng; đếm dòng code không đủ.

## 4. Tách nhiệm vụ tìm kiếm khỏi nhiệm vụ giữ thứ tự

Ta cần hai việc khác nhau: “đã thấy ID này chưa?” và “output theo thứ tự nào?”. Dùng HashSet cho việc thứ nhất, List cho việc thứ hai.

```csharp
var seen = new HashSet<string>(StringComparer.Ordinal);
var result = new List<string>();
foreach (string id in values)
{
    if (seen.Add(id))   // true: vừa thêm; false: đã tồn tại
        result.Add(id);
}
```

`Add` đã kiểm tra trùng nên không cần `Contains` rồi `Add` thêm một lượt tìm kiếm. Không dựa vào thứ tự enumerate của HashSet; chính `result.Add` theo thứ tự input bảo đảm thứ tự output.

### Vì sao hashing giúp được?

Hình dung bảng có nhiều bucket. Hash của ID giúp chọn bucket để tìm, thay vì quét từ đầu toàn bộ List. **Hash bằng nhau chưa chắc ID bằng nhau**: khi nhiều ID rơi vào cùng bucket, runtime vẫn phải so sánh equality để phân biệt.

Với hash phân bố đủ tốt, số phần tử mỗi bucket được kiểm soát và chi phí key bị chặn, công việc lookup trung bình theo mô hình hashing là hằng số. Tuy nhiên:

- **Expected — kỳ vọng:** dựa vào giả định phân bố/randomness; không bảo đảm từng input.
- **Amortized — khấu hao:** xét tổng chi phí của nhiều thao tác. Một lần resize có thể tốn O(u), nhưng tăng capacity theo cấp số nhân tránh phải copy cả bảng sau mỗi lần thêm. Tổng dạng `1+2+4+...` tăng O(u). Đây là giải thích nguyên lý, không khẳng định capacity .NET đúng các số đó.
- **Worst case — trường hợp xấu:** comparer/hash bất lợi có thể tạo chuỗi collision dài, làm cả batch trở lại O(n²). .NET có bảo vệ riêng cho một số string comparer; không nên suy ra mọi custom comparer được bảo vệ như nhau.

Vì vậy, cách Hash có **expected O(n)** cho toàn bộ batch, đã tính tăng capacity theo khấu hao, dưới các giả định trên. Lab có n lần gọi `Add`; con số đó không phải tổng hash/equality/resize work.

Nếu ID dài tối đa L ký tự, hash hoặc equality có thể phụ thuộc L. Khi L thay đổi theo input, cần đưa nó vào mô hình: chẳng hạn expected O(n(1+L)) cho cách hash dưới các giả định còn lại, tính cả chi phí key và xử lý mỗi phần tử. Không bỏ qua độ dài key chỉ vì dùng HashSet.

### Chứng minh kết quả vẫn đúng bằng invariant

Sau mỗi prefix đã đọc: `seen` chứa đúng các ID đã xuất hiện; `result` chứa mỗi ID một lần, theo thứ tự xuất hiện đầu.

Ban đầu cả hai rỗng. ID cũ khiến `Add` trả false: giữ nguyên. ID mới khiến `Add` trả true: thêm vào cuối output, nên giữ đúng thứ tự. Khi đọc hết input, invariant chính là yêu cầu đầu bài. Tối ưu chi phí mà vẫn bảo toàn hành vi.

### Bộ nhớ: cùng Big-O không có nghĩa cùng số byte

| Cách | Thời gian theo mô hình | Bộ nhớ phụ, không tính output | Output |
|---|---|---|---|
| Quét List | O(n(1+u)); Θ(n²) khi tất cả khác nhau | O(1) | O(u) |
| HashSet + List | Expected O(n), có giả định | O(u) | O(u) |

HashSet giữ thêm bucket/entry array; List giữ reference tới chuỗi. Code này không clone các chuỗi input. Khi array tăng capacity, có allocation và copy; các array cũ có thể cần GC. **Allocation, bộ nhớ còn sống và peak working set là các số đo khác nhau.**

`new HashSet<string>(n, ...)` hoặc `new List<string>(n)` có thể giảm resize khi biết kích thước phù hợp, nhưng n lớn/u nhỏ sẽ cấp dư. Khi preallocate n, không còn được gọi phần storage đó là O(u) nếu u nhỏ độc lập với n. Chưa cần thêm tối ưu này vào bài chính.

## 5. Lab C# tùy chọn: kiểm tra lập luận trước khi đo tốc độ

[Hướng dẫn đầy đủ](../../../labs/cost-model/dotnet/README.vi.md) có ZIP, setup, benchmark và cách gỡ lỗi. Lab chính cần .NET SDK, không cần SQL Server/Docker/Python hay package bên thứ ba. Phiên bản đã chạy: **SDK 10.0.401, runtime 10.0.12, Linux x64**; target net10.0. Không cần đổi target ứng dụng production của bạn.

Từ root repo đã clone/cập nhật:

```bash
cd labs/cost-model/dotnet
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

**Bước 1 — kiểm tra yêu cầu.** Dự đoán output của ví dụ 5 ID rồi đọc/chạy lab. Checkpoint: `B2, A1, C3`, scan comparisons là 6. Lời giải: ID cũ không append; input và thứ tự đầu được giữ.

**Bước 2 — kiểm tra công thức.** Dự đoán n=128/256/512, sau đó đối chiếu:

```text
n,scan_equality_comparisons,hash_add_calls (not hash-table work)
128,8128,128
256,32640,256
512,130816,512
128 identical IDs: 127 scan comparisons
```

Lời giải: cột scan khớp `n(n−1)/2` khi distinct; tất cả giống nhau chỉ cần n−1 so sánh. Cột Add chỉ đếm lời gọi, không chứng minh runtime luôn O(1).

**Bước 3 — kiểm tra hành vi.** Chạy `--check`, kỳ vọng **8 checks passed**. Có empty/singleton, ordinal equality, không sửa input, null, duplicate count và comparer cố tình trả cùng hash. Lời giải cho collision: equality vẫn giữ correctness, nhưng số so sánh tăng thành tổng tam giác. Kết quả pass của code mẫu không chứng minh bạn đã học xong.

Nếu chưa cài SDK, đọc các checkpoint và [code hoàn chỉnh](../../../labs/cost-model/dotnet/Core/Deduplication.cs). Không cần tự viết code để đọc lời giải hoặc yêu cầu ngày tiếp theo.

## 6. Nhánh 180+ phút: đo allocation/CPU và đọc implementation

Thêm khoảng 30 phút setup/chạy benchmark, 30 phút đọc report, 30 phút đọc runtime. Benchmark dùng **BenchmarkDotNet 0.15.8**, cần NuGet và mạng cho lần restore đầu; chạy Release, không gắn debugger:

```bash
# Vẫn ở labs/cost-model/dotnet
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

Input được tạo trong `GlobalSetup`, ngoài phần đo. Mỗi lần gọi tạo output mới; hai cách có cùng equality/output contract. Ma trận n=128/512/2048 và distinct danh nghĩa 10%/100%; độ dài ID cố định. **Dự đoán tùy chọn:** cách nào cấp phát thêm? Nếu u rất nhỏ, lợi thế hash có còn lớn không?

**Lời giải:** Hash giữ thêm bảng nên thường cấp phát nhiều hơn; u nhỏ khiến List ngắn, nên lợi thế thời gian có thể giảm. Thời gian cụ thể phải đo; không đoán ratio từ Big-O.

Agent đã chạy ShortRun đủ **12 case**, 3 warmup và 3 measurement iteration/case. Ví dụ n=512, toàn bộ distinct:

| Cách | Mean | Error, nửa CI 99,9% | Allocated mỗi operation |
|---|---:|---:|---:|
| Scan | 922,355 µs | 2.261,779 µs | 8.384 B |
| Hash | 22,218 µs | 19,147 µs | 42.896 B |

Máy cloud Debian 13, Intel Xeon Platinum 8573C, .NET 10.0.12. Môi trường không cho nâng priority; CI rộng và ShortRun ngắn nên số thời gian chỉ là **minh họa trên workload này**, không là cam kết production. [Report đầy đủ](../../../lessons/2026-10-05-cost-model/benchmark-report.md) và [log thực thi](../../../lessons/2026-10-05-cost-model/benchmark-run.txt) có environment/giới hạn. Allocated không gồm input tạo sẵn; không phải peak memory hay p99 service. Không dùng counter của `CountScan` trong benchmark tốc độ.

### Đọc một lát cắt .NET, không build cả runtime

Repo chính thức `dotnet/runtime`, ghim release v10.0.12 tại commit `4271d88e0aebf3d04f188f1334c2220d80555ef6`:

- [List.Contains](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/List.cs#L336): dự đoán lời gọi nào thực hiện tìm kiếm; đọc tiếp `IndexOf`.
- [HashSet.AddIfNotPresent](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/HashSet.cs#L1411): tìm hash, bucket, equality, `return false` và resize.
- [Test vượt capacity](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Collections/tests/Generic/HashSet/HashSet.Generic.Tests.cs#L552): xem hành vi nào được upstream kiểm tra.

**Lời giải hoạt động đọc:** List.Contains gọi IndexOf → Array.IndexOf. HashSet dùng hash chọn bucket rồi đi theo entry chain, chỉ coi là trùng khi hash và equality phù hợp; ID đã có trả false, bảng đầy có thể resize. Test capacity kiểm tra hành vi khi tăng số phần tử, không tự chứng minh mọi workload có O(1). Agent đọc các phần liên quan và chạy lab cục bộ; **chưa build/chạy bộ test upstream**.

## 7. Chuyển yêu cầu: đếm mã bị lặp, vẫn giữ thứ tự đầu

**Bài tập tùy chọn:** với `B2,A1,B2,C3,A1`, trả `[(B2,2),(A1,2)]`; bỏ mã chỉ xuất hiện một lần. Với input rỗng trả `[]`; `A,A,A` trả `[(A,3)]`.

**Lời giải:** dùng Dictionary để đếm và List riêng để lưu thứ tự ID mới. Sau khi đọc hết, duyệt List thứ tự, chỉ xuất ID có count > 1. Không dựa vào thứ tự enumerate của Dictionary.

```csharp
var counts = new Dictionary<string, int>(StringComparer.Ordinal);
var order = new List<string>();
foreach (string id in values)
{
    if (counts.TryGetValue(id, out int count)) counts[id] = count + 1;
    else { counts.Add(id, 1); order.Add(id); }
}
var duplicates = new List<(string Id, int Count)>();
foreach (string id in order)
    if (counts[id] > 1) duplicates.Add((id, counts[id]));
```

Invariant: counts bằng số lần mỗi ID đã xuất hiện trong prefix, order giữ thứ tự xuất hiện đầu. Expected O(n+u)=O(n), bộ nhớ phụ O(u) theo giả định hashing/key. [Bản chạy có validation và lời giải](../../../labs/cost-model/dotnet/Core/Deduplication.cs) dùng record `OrderCount` thay tuple; hành vi tương đương.

### Production bridge: batch dedup khác idempotency

**Tình huống tùy chọn:** hai instance cùng xử lý message có ID B2; mỗi instance có HashSet riêng. Có ngăn xử lý trùng toàn hệ thống không?

**Lời giải:** không. Mỗi set ban đầu rỗng nên cả hai đều thêm thành công. Muốn bảo đảm identity ở storage, dùng unique constraint/index trên key nghiệp vụ thích hợp (ví dụ tenant + event ID), cùng transaction và xử lý conflict. `SELECT` kiểm tra trước `INSERT` riêng lẻ vẫn có race. Collation SQL Server phải phù hợp quy tắc identity; Ordinal ở C# không tự bảo đảm SQL có cùng equality.

Nếu side effect nằm ngoài transaction database, unique key một mình chưa bảo đảm exactly-once cho side effect đó; cần protocol idempotency/transaction thích hợp. Bài hôm nay chỉ thiết lập ranh giới này, chưa yêu cầu triển khai hệ thống distributed.

## 8. Recap và cách tiếp tục

**Ba câu tự kiểm tra, có đáp án:**

1. Vì sao một `foreach` có thể Θ(n²)? **Đáp án:** phần thân tìm trong List tăng dần; tổng 0+1+…+n−1.
2. Vì sao cần cả HashSet và List? **Đáp án:** set trả lời membership, List bảo đảm thứ tự output; thêm bảng tốn bộ nhớ.
3. Có thể bảo đảm hash luôn nhanh hơn hoặc lưu set trong API singleton để ngăn mọi duplicate không? **Đáp án:** không; workload nhỏ, key/comparer và allocation ảnh hưởng hiệu năng; set cục bộ không giải quyết retry/multiple instances, và tăng mãi còn gây rủi ro bộ nhớ/concurrency.

Muốn nhận feedback, bạn có thể gửi giải thích ngắn, code hoặc report, kèm cho biết đã xem lời giải chưa. Rubric: đúng contract/case biên; lập luận có giả định; phân biệt số đếm với số đo; hiểu giới hạn production. Nếu đã xem đáp án, phản hồi sau đó được ghi là có hỗ trợ; cần task mới nếu muốn đánh giá độc lập.

Hook ôn gợi ý sau 1/3/7 ngày: tái dựng tổng so sánh; giải thích expected/amortized; chuyển sang đếm duplicate hoặc tenant-scoped identity. Câu trả lời cốt lõi nằm ở phần 2/4/7. Đây là đề xuất học, chưa phải lượt ôn đã thực hiện hay lịch tiến độ được xác nhận.

Gọi ngày sau: **“Dùng master-iuh-daily-learning, viết bài hôm nay cho tôi.”** Không cần nộp bài hôm nay. Việc xuất bản/chạy code mẫu không tự ghi bạn đã hoàn thành hay mastery.

## Nguồn và mức độ kiểm chứng

Đã kiểm tra ngày **05/10/2026**. [Dossier nguồn](../../../lessons/2026-10-05-cost-model/sources.json) ghi pin, metadata và phạm vi đọc.

- **Curriculum:** [IUH Master, bản cô đọng trong repo](../../../curricula/iuh/master/curriculum.md), outcome môn 6001127. Chưa xác minh lại PDF/quy định hiện hành của trường.
- **Lý thuyết:** [MIT 6.006, Hashing II, trang 1–3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf): expected cost có giả định hashing và resize/amortization; không phải benchmark .NET.
- **API/implementation:** [List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0), [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0) và code runtime ghim ở trên. Tài liệu API nói O(1) cho lookup thông thường; bài vẫn nêu collision/key-cost assumptions.
- **Đo đạc:** [BenchmarkDotNet getting started](https://benchmarkdotnet.org/articles/guides/getting-started.html), [good practices](https://benchmarkdotnet.org/articles/guides/good-practices.html); report là số đo thật của agent, không phải bằng chứng học tập.
- **Database:** [SQL Server unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17); production bridge là tổng hợp của người hướng dẫn. Chưa chạy lab SQL Server hay workload production.

Đã chạy lab/reference checks và benchmark cục bộ; chưa có thử nghiệm chứng minh hiệu quả học tập của bài này với người học.
