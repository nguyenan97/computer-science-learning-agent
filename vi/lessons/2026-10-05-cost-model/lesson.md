# Bài 01 — Big-O và cấu trúc dữ liệu: khử trùng mã đơn hàng bằng C#

**Một ngày đầy đủ: 420 phút · 360 phút học + 60 phút nghỉ · Cập nhật 06/10/2026**

[English](../../../lessons/2026-10-05-cost-model/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip)

Một vòng lặp trông đơn giản vẫn có thể thực hiện hàng tỷ phép so sánh. Bài này giải thích công việc đó từ đâu ra, cấu trúc dữ liệu khác thay đổi chi phí thế nào và đánh đổi bộ nhớ ra sao. Nội dung cần để hiểu thuật toán, implementation đầy đủ và bài tập có lời giải nằm ngay trên trang này. Lab tải về và nguồn chính thức bổ sung khả năng chạy thí nghiệm, đọc sâu.

**Mục tiêu:** implement khử trùng batch giữ lần xuất hiện đầu của mỗi ID, rồi giải thích lựa chọn scan hay hashing với phân bố input thay đổi bằng correctness, số đếm và số đo CPU/allocation. Bạn cần vòng lặp và collection C# cơ bản; phân tích độ phức tạp bắt đầu từ trace cụ thể.

## Lộ trình một ngày

| Phút tính từ đầu | Hoạt động | Phút thực hành chủ động |
|---|---|---:|
| 0–20 | Self-check nhanh: phần giải thích được và phần cần xem lại | 10 |
| 20–70 | Contract, mental model, worked trace (§§1–4); tự dựng trace và số đếm | 20 |
| 70–80 | Nghỉ, rời màn hình | 0 |
| 80–125 | Đọc nguồn chọn lọc (§6 và Đọc thêm); trả lời bốn câu hỏi research | 10 |
| 125–170 | Trace implementation (§6): miss, hit và collision | 40 |
| 170–200 | Ăn trưa, nghỉ | 0 |
| 200–275 | Thực hành hướng dẫn (§5): implement, test, debug | 70 |
| 275–285 | Nghỉ | 0 |
| 285–330 | Thí nghiệm có kiểm soát (§6): dự đoán, đo, đối chiếu | 40 |
| 330–340 | Nghỉ | 0 |
| 340–375 | Challenge đổi yêu cầu (§7): đếm duplicate | 35 |
| 375–420 | Giải thích quyết định, sửa lỗi và chọn câu ôn (§8) | 10 |

Lộ trình dành 235/360 phút học cho code, trace, thiết kế test, debug và thí nghiệm. Setup/chờ benchmark chưa phải thực hành. Điều chỉnh block theo công cụ và sức tập trung; nếu setup quá lâu, dùng trace trên trang và report mẫu. Kết thúc bằng một quyết định rõ và một câu hỏi mở, không kéo dài cả ngày để có benchmark đẹp.

## Self-check nhanh

Thử không nhìn ghi chú, hoặc đọc đáp án trước rồi quay lại sau:

1. Với `B2,A1,B2,C3,A1`, output giữ thứ tự đầu là gì? Sort làm đổi nó thế nào?
2. Scan tuần tự có bao nhiêu equality check với `A,B,C,D`?
3. Hash bằng nhau có suy ra ID bằng nhau không? Set ở một process có ngăn duplicate ở process khác không?
4. “Allocated mỗi operation” có phải peak memory không?

**Đáp án:** (1) `B2,A1,C3`; sort thành `A1,B2,C3`, sai yêu cầu thứ tự. (2) `0+1+2+3=6`. (3) Không: equality vẫn phân biệt collision; hai process có set riêng. (4) Không: allocation là lượng mới cấp phát trong operation được đo, chưa phải lượng memory sống lớn nhất.

Nếu chưa quen tìm tuần tự, vẽ `[B2,A1]`. Tìm B2 dừng sau một so sánh; tìm C3 phải kiểm tra cả hai trước khi kết luận không có. Với `[X,Y,X]`, output là `[X,Y]`, scan có `0+1+1=2` so sánh. Nếu trace này dễ, dành thêm thời gian cho số đo và challenge đổi yêu cầu.

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

**Thử suy nghĩ:** có bao nhiêu phần tử, bao nhiêu mã khác nhau? Với output tạm `[B2,A1]`, muốn biết `C3` đã xuất hiện chưa cần làm gì?

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

**Thử suy nghĩ:** chỉ thấy một `foreach`, có thể kết luận O(n) không?

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

## 5. Thực hành C# hướng dẫn: implementation đầy đủ

Method sau có cả null policy. Đặt trong một class nếu chạy local; logic không cần database hay framework.

```csharp
public static List<string> StableUnique(IReadOnlyList<string> values)
{
    ArgumentNullException.ThrowIfNull(values);
    var seen = new HashSet<string>(StringComparer.Ordinal);
    var result = new List<string>();
    foreach (string id in values)
    {
        if (id is null)
            throw new ArgumentException("Order IDs must not be null.");
        if (seen.Add(id))
            result.Add(id);
    }
    return result;
}
```

`seen` và `result` bắt đầu rỗng ở mỗi batch. Mỗi ID gọi Add đúng một lần. ID mới vào set và append vào List; ID cũ không đổi cả hai. Method đọc input, không sửa input. List giữ reference đến cùng các string, không clone string.

Ví dụ gọi:

```csharp
string[] input = ["B2", "A1", "B2", "C3", "A1"];
var unique = StableUnique(input);
Console.WriteLine(string.Join(", ", unique)); // B2, A1, C3
```

### Thực hiện block thực hành 75 phút

1. **Tự dựng method (20 phút).** Đóng ví dụ, viết lại và giải thích prefix invariant ở §4. Khi vướng, xem method đầy đủ phía trên.
2. **Dự đoán case biên (15 phút).** Viết kỳ vọng trước trace/chạy:

   | Input | Kết quả kỳ vọng |
   |---|---|
   | `[]` | `[]` |
   | `a,A,a` | `a,A` |
   | `A,A,A` | `A` |
   | `"",B2,""` | `"",B2` |
   | input null | `ArgumentNullException` |
   | một ID null | `ArgumentException` |

3. **Test/debug (15 phút).** So output với kỳ vọng, kiểm tra input không đổi. Khi lệch, trace batch fail nhỏ nhất thay vì viết lại cả method.
4. **Cố tình phá một rule (10 phút).** Append mọi ID, sort result hoặc dùng `OrdinalIgnoreCase`. Append tất cả giữ duplicate; sort phá thứ tự đầu; equality không phân biệt hoa thường gộp `a` và `A`. Khôi phục contract trước khi đo.
5. **Khảo sát collision (10 phút).** Giả sử comparer trả hash 1 cho mọi ID nhưng vẫn dùng ordinal equality. Kết quả vẫn đúng, nhưng ID chưa có có thể phải kiểm tra mọi entry trong bucket. Với 128 ID distinct, implementation dạng chain có `128×127/2=8.128` equality check. Key bằng nhau phải có hash bằng nhau; equality/hash phải ổn định khi key được lưu.
6. **Kết thúc (5 phút).** Giải thích một bug đã tránh và một giả định implementation cần.

**Dấu hiệu debug:** còn duplicate → chỉ append khi Add true; thứ tự đổi → giữ List output riêng; gộp `a/A` → xem comparer; hashing chậm bất thường → tìm List.Contains bị giấu; null behavior đổi → giữ validation rõ ràng.

### Đối chiếu Python ngay trên trang

Python set cũng tách membership khỏi output order:

```python
def stable_unique(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

assert stable_unique(["B2", "A1", "B2", "C3", "A1"]) == ["B2", "A1", "C3"]
```

Bản này cần key hashable, dùng Python equality, không áp null policy của method C#. Key mới có một membership test rồi insertion; C# Add xử lý cả hai trong một lời gọi. Lập luận chi phí tổng quát giống nhau khi hashing phù hợp; hằng số và collision tùy implementation.

## 6. Research, đọc implementation và thí nghiệm có kiểm soát

### Nối mô hình với code collection thật

List.Contains gọi IndexOf, cuối cùng tìm trong array. Runtime .NET có thể specialization cho một số type, cải thiện hằng số nhưng miss vẫn phải xét các candidate trước đó.

HashSet.Add đi theo đường khác:

```text
ID → tính hash → chọn bucket → xem entry trong bucket
   → hash khớp VÀ ID bằng nhau? trả false
   → nếu chưa khớp, đi đến entry tiếp
   → không có entry bằng? cấp slot (resize khi cần), insert, trả true
```

**Bucket** là điểm vào nhóm candidate. **Collision chain** nối entry cùng bucket. Hash lưu sẵn giúp loại candidate nhanh; equality quyết định identity. Resize tạo storage lớn hơn, phân bố lại entry, nên một Add có thể đắt dù chuỗi dài có chi phí khấu hao tốt.

Trace ba case: set rỗng nhận B2; B2 xuất hiện lại; A1 mới có cùng hash B2. Đáp án: insert B2, true; tìm B2 bằng, false; so A1 với B2 thấy khác, insert A1, true. List riêng giữ thứ tự output ở cả ba case.

Đọc sâu tại [List.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/List.cs#L336) và [HashSet.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/HashSet.cs#L1411) chính thức, ghim một implementation .NET 10 để đọc lại được. Tìm chọn bucket, equality, return false và resize. Không cần build runtime để hiểu đường đi.

### Bốn câu hỏi research

| Câu hỏi | Câu trả lời cần tìm |
|---|---|
| List.Contains giấu công việc gì? | Tìm tuần tự; hit dừng sớm, miss quét hết. |
| Vì sao một Add O(u) nhưng cả chuỗi expected O(n)? | Chi phí resize cộng theo cấp số nhân; expected lookup còn cần hashing phù hợp, key cost bị chặn. |
| Vì sao collision giữ correctness nhưng đe dọa performance? | Equality đúng phân biệt key; chain dài thêm so sánh. |
| Benchmark giả lập nói gì về service? | So workload/scope allocation đã đo; phân bố production, peak memory, p99 cần đo riêng. |

### So sánh công bằng

Đo scan/hash trên cùng input, equality và contract thứ tự. Tạo input trước phần đo, mỗi lần gọi đo tạo result mới. Nếu không, một đường có thể nhận state đã làm nóng hay bỏ allocation trong khi đường kia vẫn phải cấp phát.

Lab tải về dùng BenchmarkDotNet 0.15.8, N=128/512/2048, tỷ lệ distinct danh nghĩa 10%/100%, ID có độ dài cố định. Với N=128 và 10%, distinct thật là `floor(128×0.10)=12`. Dự đoán trước chạy: u giảm làm List scan ngắn hơn; hash table thường cấp phát nhiều hơn. Big-O chưa cho ratio tốc độ.

Chạy Release, không debugger. Đọc Mean, Error, Allocated cùng nhau. Error của BenchmarkDotNet ở đây là nửa confidence interval 99,9%, chưa là chặn sai số được bảo đảm. Allocated gồm storage output/table mới, bỏ input tạo sẵn; không đo peak working set, heap sống hay p99 service.

ShortRun mẫu ngày 05/10/2026, n=512 và mọi ID distinct:

| Cách | Mean | Error | Allocated mỗi operation |
|---|---:|---:|---:|
| Scan | 922,355 µs | 2.261,779 µs | 8.384 B |
| Hash | 22,218 µs | 19,147 µs | 42.896 B |

Lần chạy dùng Debian 13, Intel Xeon Platinum 8573C, .NET 10.0.12, ba warmup và ba measurement iteration mỗi case. Interval rất rộng: thời gian chỉ minh họa, chưa phải speedup service đáng tin. Byte cấp thêm thể hiện trade-off, chưa phải memory cả ứng dụng. [Report đầy đủ](../../../lessons/2026-10-05-cost-model/benchmark-report.md) có ma trận workload.

### Sổ thí nghiệm của bạn

Dùng block 45 phút đổi một yếu tố—n, tỷ lệ distinct, key length hoặc initial capacity—và giữ contract output. Correctness trước timing. Không benchmark method có counter so sánh với method không instrument: counter đã thay đổi công việc.

| Viết trước chạy | Viết sau chạy |
|---|---|
| Input size, u thật, độ dài/phân bố key | Tham số và môi trường thật |
| Dự đoán, cơ chế giải thích | Mean, interval, allocation |
| Một yếu tố sẽ đổi | Dự đoán có khớp không |
| Kết quả correctness kỳ vọng | Failure hay quan sát bất ngờ |
| Điều gì khiến chưa thể kết luận? | Quyết định được hỗ trợ, giới hạn còn lại |

Nếu không chạy benchmark, dùng report mẫu để luyện diễn giải, để số đo của bạn trống. Thiếu kết quả hay quá nhiễu → kết luận “chưa đủ số đo để khẳng định tốc độ”. Kiểm tra tạo input, comparer, build mode và interval trước khi bịa lý do cho ratio bất ngờ. Harness Dry chỉ check thực thi, chưa đo performance hữu ích.

## 7. Challenge đổi yêu cầu: báo cáo đếm duplicate

Báo cáo support cần count thay cho ID unique. Với `B2,A1,B2,C3,A1`, trả `[(B2,2),(A1,2)]`, bỏ ID chỉ xuất hiện một lần. Giữ ordinal identity, thứ tự đầu, input không đổi và null policy như cũ.

Thử thiết kế trước khi đọc tiếp. Cần counts để lookup và List riêng để giữ thứ tự. Mỗi lần xuất hiện tăng count; chỉ lần đầu thêm ID vào List.

```csharp
public sealed record OrderCount(string Id, int Count);

public static List<OrderCount> DuplicateSummary(IReadOnlyList<string> values)
{
    ArgumentNullException.ThrowIfNull(values);
    var counts = new Dictionary<string, int>(StringComparer.Ordinal);
    var order = new List<string>();
    foreach (string id in values)
    {
        if (id is null)
            throw new ArgumentException("Order IDs must not be null.");
        if (counts.TryGetValue(id, out int count))
            counts[id] = count + 1;
        else
        {
            counts.Add(id, 1);
            order.Add(id);
        }
    }
    var result = new List<OrderCount>();
    foreach (string id in order)
        if (counts[id] > 1)
            result.Add(new OrderCount(id, counts[id]));
    return result;
}
```

Invariant gồm hai phần: counts bằng số lần xuất hiện trong prefix đã đọc; order chứa mỗi ID đã gặp một lần theo thứ tự đầu. Lượt duyệt order sau lọc count lớn hơn một. Expected O(n+u)=O(n), thêm O(u) storage theo giả định hashing/key cũ. Không dựa vào thứ tự enumerate của Dictionary.

| Input | Lời giải |
|---|---|
| `A,B,B,A,C` | `[(A,2),(B,2)]` |
| `a,A,a` | `[(a,2)]` |
| `[]` hoặc `X,Y` | `[]` |
| `A,A,A` | `[(A,3)]` |

Sort theo count làm đổi thứ tự báo cáo. Chỉ increment ID mới sẽ fail với `A,A,A`. Trace `A,B,B,A,C`: order vẫn `A,B,C`, counts thành A=2/B=2/C=1; lượt cuối trả A rồi B.

### Nối với production: batch deduplication và idempotency

Hai service instance đều có thể nhận B2 vì set của mỗi instance bắt đầu rỗng. HashSet trong batch không thực thi identity toàn hệ thống. Dùng key storage phù hợp, ví dụ tenant + event ID, với unique constraint/index và transaction/xử lý conflict. SELECT-before-INSERT riêng lẻ vẫn race.

Equality storage phải khớp identity mong muốn: collation SQL Server có thể coi string khác C# Ordinal. Nếu side effect nằm ngoài transaction database, unique key chưa đủ bảo đảm exactly-once cho side effect. Cần protocol idempotency/transaction phù hợp.

## 8. Giải thích quyết định và xem lại

Đóng ví dụ rồi giải thích:

1. Vì sao một foreach có thể Θ(n²)? **Đáp án:** thân tìm trong List dài dần, tổng `0+1+…+n−1` khi input distinct.
2. Vì sao cần cả HashSet và List? **Đáp án:** membership và thứ tự output là hai việc; hash table tốn storage thêm.
3. Hashing có luôn nhanh hơn không? **Đáp án:** không; batch nhỏ, u thấp, key cost, allocation và cache đều ảnh hưởng.
4. Với `A,B,A,B`, scan có bao nhiêu so sánh? **Đáp án:** `0+1+1+2=4`, so với sáu khi bốn ID distinct.

Giải thích cuối hữu ích nêu contract, workload kỳ vọng, cấu trúc chọn, lập luận hỗ trợ và một giới hạn. Ví dụ: “Với nhiều ID distinct có độ dài bị chặn, tôi chọn HashSet cùng List. Invariant giữ thứ tự đầu, số scan tăng bậc hai. Hashing expected tuyến tính theo giả định phù hợp và tốn thêm storage. Benchmark mẫu minh họa trade-off nhưng timing bất định lớn. Cần đo key distribution và memory thật trước khi hứa latency production.”

Tự review bốn điểm: case biên/invariant; giả định n/u/key-cost; số đo công bằng/giới hạn; biến thể đếm duplicate có giữ order không. Nếu giải thích chưa rõ, quay lại counterexample nhỏ và thử ID mới. Sau một khoảng, tự dựng số đếm hoặc implement biến thể không ghi chú. Sai thì ôn sớm hơn, recall ổn thì tăng khoảng; 1/3/7 ngày là điểm bắt đầu điều chỉnh được.

Câu hỏi để sau: Identifier dài làm đổi gì? Batch có thể dùng bao nhiêu memory? Identity theo tenant nên khớp equality storage thế nào? Chọn một câu, không mở rộng mục tiêu hôm nay mãi.

## Đọc thêm

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) và [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0): kiểm tra equality, giá trị trả về và resize.
- [MIT OCW: Hashing II, trang 1–3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf): suy ra giả định load factor và tăng table theo khấu hao.
- [BenchmarkDotNet good practices](https://benchmarkdotnet.org/articles/guides/good-practices.html): chuẩn bị benchmark Release công bằng, tránh ngoại suy từ một môi trường.
- [SQL Server unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17): mở rộng ví dụ batch sang uniqueness do storage thực thi.
- [Hướng dẫn lab C#](../../../labs/cost-model/dotnet/README.vi.md): setup, lệnh benchmark và troubleshooting tùy chọn khi muốn chạy thí nghiệm.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bản đồ chủ đề](../../references/topic-map.md) — Chọn phần nền tảng hoặc chủ đề muốn học sâu tiếp theo.
- [Hướng dẫn lab C#](../../../labs/cost-model/dotnet/README.vi.md) — Cài SDK, lệnh chạy và cách xử lý lỗi benchmark.

---

[Danh sách bài học](../../README.md) · [Bài sau: Bài 02 — Tìm biên và cửa sổ thời gian →](../boundary-search/lesson.md)
<!-- LESSON_NAVIGATION_END -->
