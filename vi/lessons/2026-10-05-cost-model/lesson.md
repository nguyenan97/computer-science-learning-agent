# Bài 01 - Big-O và cấu trúc dữ liệu: loại bỏ duplicate mã đơn hàng bằng C#

[English](../../../lessons/2026-10-05-cost-model/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip)

Một vòng lặp trông đơn giản vẫn có thể làm hàng tỷ phép so sánh. Bài này chỉ ra công việc ẩn đó đến từ đâu, một cấu trúc dữ liệu khác loại bỏ nó thế nào, phải trả giá gì về memory, và quyết định này xuất hiện ở đâu trong code thật (change tracker của EF Core, Azure Service Bus, unique index của SQL Server). Mọi thứ cần để hiểu thuật toán, implementation đầy đủ và đáp án bài tập đều nằm trên trang này. ZIP lab và nguồn chính thức chỉ là phần thêm để chạy thí nghiệm và đọc sâu hơn.

**Mục tiêu:** viết hàm dedupe một batch, giữ lần xuất hiện đầu tiên của mỗi order ID, rồi giải thích khi nào dùng scan và khi nào dùng hashing, dựa trên correctness, số phép đếm và số đo CPU/allocation. Bạn chỉ cần biết vòng lặp và collection cơ bản của C#. Mỗi mục cho biết bạn làm gì và trong bao lâu; tổng số phút vừa đủ một ngày học.

## Khái niệm cần biết (giải thích ngắn)

Đọc phần này trước. Mỗi ý cố tình viết ngắn. Mục 4 mới đưa định nghĩa chính thức, sau khi bạn đã thấy số liệu.

- **Duplicate và dedupe.** Duplicate (trùng lặp) là giá trị xuất hiện nhiều hơn một lần, ví dụ order ID `B2` trong `B2, A1, B2`. Dedupe (deduplicate, loại bỏ trùng lặp) là giữ lại đúng một bản cho mỗi giá trị.
- **n và u.** `n` là số phần tử bạn đọc. `u` là số phần tử *khác nhau*. Với `B2, A1, B2, C3, A1`: n = 5, u = 3.
- **Cost model (mô hình chi phí).** Trước khi so sánh hai cách làm, bạn chọn đếm cái gì. Ở đây ta đếm số lần so sánh bằng nhau giữa hai ID. Nhờ vậy so sánh được thuật toán mà không cần đồng hồ bấm giờ. Đây là bản đơn giản hóa, không phải công việc thật của CPU.
- **Big-O.** Nó mô tả công việc *tăng nhanh cỡ nào* khi input lớn lên, bỏ qua hệ số hằng. O(n): input gấp đôi thì công việc gấp đôi. O(n²): input gấp đôi thì công việc gấp khoảng bốn. Đó là tốc độ tăng, không phải số giây. Θ (theta) là bản chặt: "xấp xỉ chừng này, không ít hơn".
- **Worst case, expected case, amortized.** Worst case (trường hợp tệ nhất) là input xui nhất. Expected case (kỳ vọng) là trung bình dưới một giả định đã nêu (với hashing: key phân bố đều). Amortized là chi phí trung bình trên cả chuỗi thao tác, kể cả khi một thao tác (như resize) tốn kém.
- **Hash table, bucket, collision.** Hash function biến một key thành một số, số đó chọn một nhóm nhỏ các slot gọi là bucket. Bạn chỉ tìm trong bucket đó thay vì kiểm tra tất cả. Collision là khi hai key khác nhau rơi vào cùng bucket. Kết quả vẫn đúng vì equality vẫn được kiểm tra.
- **Invariant.** Một câu luôn đúng sau mỗi bước của vòng lặp. Nếu nó đúng lúc đầu, giữ đúng sau mỗi bước, và đến cuối suy ra được yêu cầu bài toán, thì code đúng.
- **Allocation và peak memory.** Allocation là lượng memory mới mà một thao tác xin cấp. Peak memory là lượng memory đang sống nhiều nhất tại một thời điểm. Hai con số này khác nhau.

## 1. Self-check nhanh

**Block recall · khoảng 20 phút · Việc cần làm:** trả lời theo trí nhớ nếu được, rồi mở từng đáp án. Chưa có bài trước để nhớ lại, nên phần này kiểm tra các kiến thức nền cho hôm nay. **Dừng khi:** bạn biết mình muốn đọc lại câu nào trong bốn câu.

1. Với `B2,A1,B2,C3,A1`, output giữ thứ tự xuất hiện đầu là gì? Sort làm nó đổi thế nào?

<details>
<summary>Đáp án</summary>

`B2,A1,C3`. Sort cho ra `A1,B2,C3`, sai yêu cầu "giữ thứ tự xuất hiện đầu".

</details>

2. Scan tuần tự thực hiện bao nhiêu phép so sánh equality với `A,B,C,D`?

<details>
<summary>Đáp án</summary>

`0+1+2+3 = 6`. Phần tử đầu không so với ai, phần tử thứ hai so với một phần tử, và cứ thế.

</details>

3. Hash bằng nhau có nghĩa là ID bằng nhau không? Set ở một process có chặn được duplicate ở process khác không?

<details>
<summary>Đáp án</summary>

Cả hai đều không. Hash bằng nhau vẫn có thể là hai key khác nhau nên phải kiểm tra equality. Hai process mỗi bên có một set rỗng riêng.

</details>

4. "Allocated mỗi operation" có phải là peak memory không?

<details>
<summary>Đáp án</summary>

Không. Allocation là memory mới được xin cấp trong operation đang đo. Peak memory là lượng memory sống nhiều nhất cùng lúc.

</details>

Chưa quen tìm kiếm tuần tự? Vẽ `[B2, A1]`. Tìm `B2` dừng sau một lần so sánh. Tìm `C3` phải so với cả hai phần tử rồi mới kết luận "không có". Với `[X, Y, X]` output là `[X, Y]` và scan làm `0+1+1 = 2` phép so sánh. Nếu thấy dễ, hãy dành thời gian tiết kiệm được cho phần thí nghiệm và phần đổi yêu cầu phía sau.

## 2. Một yêu cầu production nhỏ

**Block foundation · khoảng 50 phút cho mục 2 đến 5 · Việc cần làm:** đọc từng trace và tự dựng lại bằng tay trước khi nhìn bảng kế tiếp. **Dừng khi:** bạn nói lại được invariant ở mục 5 mà không nhìn.

Một job logistics nhận order ID từ log hoặc từ một message batch. Một ID có thể xuất hiện nhiều lần. Trả về mỗi ID **một lần, theo thứ tự nó xuất hiện lần đầu**.

```text
Input : B2, A1, B2, C3, A1
Output: B2, A1, C3
```

Chốt ba điều trước khi tối ưu:

- So sánh chính xác bằng `StringComparer.Ordinal`: `a` khác `A`. Không tự trim hay lowercase.
- Giữ thứ tự xuất hiện đầu. Sort thành `A1,B2,C3` là sai yêu cầu.
- Không sửa input. Input list và từng ID đều không null; code lab từ chối null. Chuỗi rỗng vẫn là giá trị hợp lệ trong ví dụ này.

Đây là dedupe **trong một batch**. Nó không phải xử lý message exactly-once; mục 10 giải thích sự khác biệt.

**Thử suy nghĩ:** ví dụ trên có bao nhiêu phần tử và bao nhiêu ID khác nhau? Với output tạm `[B2, A1]`, muốn biết `C3` đã thấy chưa thì phải làm gì?

<details>
<summary>Đáp án</summary>

n = 5 phần tử và u = 3 ID khác nhau. Để kiểm tra `C3` với `[B2, A1]` bằng tìm kiếm tuần tự, bạn so với `B2` rồi `A1`, và chỉ khi đó mới biết nó là ID mới. Nếu ý "phải kiểm tra hết mới được nói không có" chưa rõ, hãy đọc lại trace ở mục 3 thật chậm; phần còn lại của bài dựa vào ý này.

</details>

## 3. Một vòng lặp, rất nhiều công việc ẩn

Cách viết quen thuộc:

```csharp
var result = new List<string>();
foreach (string id in values)
{
    if (!result.Contains(id))
        result.Add(id);
}
```

`List.Contains` tìm trong các phần tử đã có trong `result` và dừng khi thấy một ID bằng nhau. Nếu không có, nó phải tìm hết. Một lời gọi API có thể giấu rất nhiều công việc.

| ID đang đọc | `result` trước bước | So sánh tuần tự | `result` sau bước |
|---|---|---|---|
| B2 | [] | 0 | [B2] |
| A1 | [B2] | A1 với B2: 1 | [B2,A1] |
| B2 | [B2,A1] | B2 với B2: 1, dừng | [B2,A1] |
| C3 | [B2,A1] | C3 với B2 và A1: 2 | [B2,A1,C3] |
| A1 | [B2,A1,C3] | A1 với B2, rồi A1: 2, dừng | [B2,A1,C3] |

Tổng là **6 phép so sánh** trong mô hình này, dù `foreach` chỉ chạy 5 lần. Đây là mô hình đếm, không phải số đo lệnh CPU của runtime .NET.

### Trường hợp mọi ID đều khác nhau

Với `A,B,C,D`, số so sánh là `0,1,2,3`. ID thứ k phải so với k-1 ID đứng trước. Với n ID khác nhau:

```text
C(n) = 0 + 1 + 2 + ... + (n-1) = n(n-1)/2
```

Để thấy công thức, viết tổng xuôi rồi viết ngược. Mỗi cặp cùng vị trí cộng lại bằng n-1, có n cặp, nên hai bản tổng bằng `n(n-1)`. Một bản bằng một nửa.

| n, tất cả khác nhau | Số so sánh trong mô hình |
|---:|---:|
| 128 | 8.128 |
| 256 | 32.640 |
| 512 | 130.816 |
| 100.000 | 4.999.950.000 |

Input gấp đôi thì công việc tăng gần gấp bốn. Chưa thể đổi những con số này ra milliseconds: CPU, runtime và dữ liệu đều ảnh hưởng thời gian thật.

## 4. Big-O nói gì và không nói gì

**Cost model** nói rõ ta đang đếm gì. Ở đây ta coi việc so sánh hoặc hash một ID có chi phí là hằng số, và n là số phần tử. Đây là giả định để phân tích được, không phải định luật cho mọi chuỗi.

**Định nghĩa chính thức.** `T(n)` là `O(n²)` nếu tồn tại hằng số C và n₀ sao cho `T(n) ≤ C·n²` với mọi `n ≥ n₀`. Nghĩa là "tăng không nhanh hơn n²", không phải "chạy n² giây".

Với các ID đều khác nhau, `n(n-1)/2` bị số hạng n² chi phối, nên mô hình scan là **Θ(n²)**: chặn trên và chặn dưới cùng bậc. Nói O(n²) vẫn đúng nhưng lỏng hơn. Một thuật toán O(n) cũng thỏa chặn O(n²), nên khi giải thích hãy dùng bậc chặt.

**Nếu mọi ID đều là `A` thì sao?** Sau ID đầu, mỗi `Contains` thấy ngay: chỉ n-1 phép so sánh, tức Θ(n). Worst case không có nghĩa mọi input đều chậm.

Với u ID khác nhau, list dài tối đa u phần tử, nên scan bị chặn bởi `O(n(1+u))`. Khi u nhỏ, cách này có thể đủ tốt. Khi u tăng cùng n, worst case thành bậc hai.

**Thử suy nghĩ:** bạn chỉ thấy một `foreach` duyệt n phần tử. Có kết luận được là O(n) không?

<details>
<summary>Đáp án</summary>

Chưa. Phải cộng chi phí của thân vòng lặp ở từng lần lặp. `Contains`, một query database hay một lời gọi service đều có chi phí riêng. Đếm dòng code là không đủ.

</details>

## 5. Tách "đã thấy chưa?" khỏi "thứ tự output"

Có hai việc khác nhau: "ID này đã thấy chưa?" và "output theo thứ tự nào?". Dùng `HashSet` cho việc đầu, `List` cho việc sau.

```csharp
var seen = new HashSet<string>(StringComparer.Ordinal);
var result = new List<string>();
foreach (string id in values)
{
    if (seen.Add(id))   // true: vừa thêm; false: đã có
        result.Add(id);
}
```

`Add` đã kiểm tra trùng, nên không cần `Contains` rồi `Add` (hai lần tìm). Đừng dựa vào thứ tự enumerate của `HashSet`; thứ tự output đến từ `result.Add` chạy theo input.

### Vì sao hashing giúp được

Hình dung một bảng có nhiều bucket. Hash của ID chọn bucket, nên bạn tìm ở đó thay vì quét cả list. **Hash bằng nhau chưa chắc ID bằng nhau**: khi nhiều ID rơi vào cùng bucket, runtime vẫn phải so sánh equality.

Nếu hash phân bố tốt, mỗi bucket nhỏ, và chi phí xử lý một key bị chặn, thì một lần lookup làm lượng việc không đổi trên trung bình. Có ba từ hay bị lẫn, và mỗi từ là một cam kết khác nhau:

- **Expected (kỳ vọng)** nghĩa là "trung bình, dưới một giả định" về cách key phân bố. Nó không hứa gì cho một input cụ thể.
- **Amortized** là tổng chi phí trên nhiều thao tác. Một lần resize có thể tốn O(u), nhưng mỗi lần tăng capacity theo hệ số nhân thì tổng `1+2+4+...` vẫn là O(u). Đây là giải thích nguyên lý, không khẳng định .NET dùng đúng các capacity đó.
- **Worst case**: hash tệ hoặc comparer xui có thể tạo collision chain dài và kéo cả batch về O(n²). .NET có bảo vệ riêng cho một số string comparer. Đừng cho rằng mọi custom comparer đều được bảo vệ.

Vậy cách dùng hash là **expected O(n)** cho cả batch, đã tính amortized resize, dưới các giả định trên. Lab đếm n lần gọi `Add`; con số đó không phải tổng công việc hash, equality và resize.

Nếu ID dài tối đa L ký tự, hash và equality có thể tốn O(L). Khi L thay đổi theo input, hãy đưa nó vào mô hình: expected `O(n(1+L))`. Đừng bỏ qua độ dài key chỉ vì đã dùng `HashSet`.

### Chứng minh bằng invariant

Sau khi đọc bất kỳ prefix nào của input: `seen` chứa đúng các ID đã đọc, và `result` chứa mỗi ID đó một lần, theo thứ tự xuất hiện đầu.

Ban đầu cả hai rỗng. ID cũ khiến `Add` trả false: không gì đổi. ID mới khiến `Add` trả true và được thêm vào cuối `result`, nên thứ tự vẫn đúng. Khi hết input, invariant chính là yêu cầu bài toán. Bạn đổi chi phí mà vẫn giữ nguyên behavior.

### Memory: cùng Big-O không có nghĩa cùng số byte

| Cách | Thời gian theo mô hình | Memory phụ, không tính output | Output |
|---|---|---|---|
| Scan một List | O(n(1+u)); Θ(n²) khi tất cả khác nhau | O(1) | O(u) |
| HashSet + List | Expected O(n), có giả định | O(u) | O(u) |

`HashSet` giữ thêm các array bucket và entry. `List` giữ reference tới các string; code này không clone string của input. Khi một array tăng capacity sẽ có allocation và copy, và array cũ có thể chờ GC. **Allocation, memory đang sống và peak working set là ba số đo khác nhau.**

`new HashSet<string>(n, ...)` hoặc `new List<string>(n)` có thể giảm resize khi bạn biết kích thước, nhưng với n lớn và u nhỏ thì bạn cấp dư. Nếu preallocate theo n, đừng gọi phần storage đó là O(u) khi u nhỏ và độc lập với n. Tạm thời chưa đưa tối ưu này vào bản chính.

**Nghỉ 10 phút.** Rời màn hình.

## 6. Nguồn và câu hỏi research

**Block sources · khoảng 45 phút · Việc cần làm:** đọc các nguồn dưới đây và trả lời bốn câu hỏi bằng lời của bạn, mỗi câu gồm một nhận định và bằng chứng. **Dừng khi:** mỗi câu có nhận định, nguồn và giới hạn.

Nguồn của bài:

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) và [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0): kiểm tra equality, giá trị trả về và resize.
- [MIT OCW: Hashing II, trang 1-3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf): giả định load factor và việc tăng bảng theo amortized.
- [BenchmarkDotNet good practices](https://benchmarkdotnet.org/articles/guides/good-practices.html): benchmark Release công bằng.

Bốn câu hỏi:

1. `List.Contains` giấu công việc gì?

<details>
<summary>Đáp án</summary>

Tìm kiếm tuần tự. Hit thì dừng sớm; miss thì đọc hết các phần tử phía trước.

</details>

2. Vì sao một lần `Add` có thể tốn O(u) nhưng cả batch vẫn expected O(n)?

<details>
<summary>Đáp án</summary>

Chi phí resize cộng dồn theo dạng `1+2+4+...` nên tổng là O(u). Việc lookup expected O(1) còn cần hash tốt và chi phí key bị chặn, đó là các giả định.

</details>

3. Vì sao collision giữ kết quả đúng nhưng đe dọa performance?

<details>
<summary>Đáp án</summary>

Equality vẫn phân biệt được các key khác nhau nên kết quả đúng. Chain dài nghĩa là mỗi lookup phải so sánh nhiều hơn.

</details>

4. Benchmark tổng hợp nói được gì về một service thật?

<details>
<summary>Đáp án</summary>

Chỉ nói được về workload và phạm vi bạn đã đo. Phân bố key, peak memory và p99 latency của production cần đo riêng.

</details>

## 7. Đọc code thật: collection và EF Core

**Block implementation-reading · khoảng 45 phút · Việc cần làm:** trace đường đi của `HashSet.Add`, rồi đọc case study EF Core và ánh xạ nó vào bài học. **Dừng khi:** bạn giải thích được bằng lời của mình EF Core lưu gì trong dictionary và vì sao.

### Source của collection

`List.Contains` gọi `IndexOf`, cuối cùng tìm trong một array. Runtime .NET có thể specialize một số type và làm hằng số nhỏ đi, nhưng miss vẫn phải kiểm tra mọi candidate phía trước.

`HashSet.Add` đi theo đường khác:

```text
ID -> tính hash -> chọn bucket -> xem các entry trong bucket
   -> hash khớp VÀ ID bằng nhau? trả false
   -> nếu chưa, sang entry kế tiếp
   -> không có entry bằng? lấy một slot (resize khi cần), insert, trả true
```

**Bucket** là điểm vào một nhóm candidate. **Collision chain** nối các entry cùng bucket. Hash đã lưu giúp loại phần lớn candidate rất rẻ; equality quyết định identity. Resize tạo storage lớn hơn rồi chuyển entry sang, nên một lần `Add` có thể đắt dù chi phí amortized nhỏ.

Hãy trace ba trường hợp: set rỗng nhận B2; B2 xuất hiện lại; A1 là ID mới và có cùng hash với B2.

<details>
<summary>Đáp án</summary>

B2 được insert và `Add` trả true. B2 lần nữa được thấy bằng nhau và `Add` trả false. A1 được so với B2, thấy khác, rồi insert và `Add` trả true. `List` riêng giữ thứ tự output trong cả ba trường hợp.

</details>

Source cần đọc, đã pin vào một commit .NET 10: [List.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/List.cs#L336) và [HashSet.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/HashSet.cs#L1411). Tìm chỗ chọn bucket, chỗ kiểm tra equality, chỗ trả false và chỗ resize. Bạn không cần build runtime.

### Case study: EF Core dùng dictionary để load row không phải scan

Bạn đã dùng EF Core, nên đây là nơi tốt nhất để thấy cùng một quyết định trong một sản phẩm thật. Project là [dotnet/efcore](https://github.com/dotnet/efcore), đọc ở commit `7adff35c6c583fa6f7aa3939389ab3314be330ab`.

**Bài toán của sản phẩm.** Một tracking query phải trả về đúng một object cho mỗi key của row trong database. Nếu 100 post cùng trỏ tới một blog, bạn phải nhận một instance `Blog`, không phải 100 bản sao, nếu không EF không biết bản nào cần lưu. Docs của EF gọi đây là identity resolution. Mỗi lần một row được chuyển thành entity, EF phải trả lời đúng câu hỏi ở mục 2: "key này đã thấy chưa?"

**Code làm gì** (đã xác minh trong source đã pin):

- Ở [`IdentityMap.cs` dòng 18](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L18), tracker giữ `Dictionary<TKey, InternalEntityEntry> _identityMap`. Key là giá trị key của entity; value là entry đang được track.
- Ở [dòng 36](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L36), dictionary được tạo với equality comparer của chính key lấy từ model. Đây là cùng quy tắc với `StringComparer.Ordinal` của bạn: equality dùng cho "đã thấy" phải khớp với identity bạn muốn.
- Lookup theo key là một lần đọc dictionary ([dòng 105](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L105)). Khi thêm entry, [dòng 267](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L267) kiểm tra cùng dictionary đó trước. Một instance khác có cùng key sẽ ném identity conflict thay vì lặng lẽ giữ cả hai.
- Kết quả query đi vào đường này qua [`QueryContext.StartTracking`](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/Query/QueryContext.cs#L148), gọi [`StateManager.StartTrackingFromQuery`](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/StateManager.cs#L324). Method này trả về entry có sẵn nếu có, nếu không thì tạo entry và đăng ký vào identity map của từng key ([dòng 347](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/StateManager.cs#L347)).

**Docs chính thức bổ sung gì.** Docs EF về [efficient querying](https://learn.microsoft.com/ef/core/performance/efficient-querying#tracking,-no-tracking-and-identity-resolution) nói EF giữ một dictionary các instance đang track và kiểm tra nó theo key khi load dữ liệu mới, và việc lookup cùng duy trì dictionary này "take up some time". Docs cũng nói no-tracking query không làm identity resolution, nên cùng một blog sẽ bị tạo 100 lần. [Trang identity resolution](https://learn.microsoft.com/ef/core/change-tracking/identity-resolution#identity-resolution-and-queries) nêu lý do: identity resolution phải nhớ mọi instance đã trả về, và điều đó làm chậm việc stream số lượng lớn entity.

**Ánh xạ vào bài học.**

| Bài học này | EF Core |
|---|---|
| Set `seen` | Dictionary `_identityMap`, key là key của entity |
| Chủ động chọn Ordinal equality | Key comparer lấy từ model |
| O(u) memory phụ để khỏi scan lặp lại | Một entry cho mỗi entity đang track, tồn tại suốt đời `DbContext` |
| Bỏ set để tiết kiệm memory | `AsNoTracking`: không có dictionary, nhưng có duplicate |

**Suy luận của người dạy, chưa xác minh trong code.** Nếu EF tìm trong một list entity đang track cho mỗi row, thì load n row có u entity khác nhau sẽ tốn O(n·u) phép so sánh key, cùng dạng với `List.Contains`. Bài này không khẳng định lịch sử của EF; đây chỉ là tình huống giả định để cho thấy vì sao dictionary là lựa chọn tự nhiên. Bài này không đo thời gian của EF.

**Áp dụng vào project của bạn.**

1. Danh sách lớn chỉ để đọc (grid hoặc export): dùng `AsNoTracking()`. Bạn bỏ được dictionary và snapshot. Đừng trông chờ "cùng một customer thì cùng một instance", vì parent sẽ bị lặp.
2. Kết quả chỉ đọc nhưng parent dùng chung phải là cùng một object: dùng `AsNoTrackingWithIdentityResolution()`. Bạn trả giá bằng một dictionary tạm trong lúc chạy query.
3. Code của bạn cần "key này đã thấy chưa?" trên hàng nghìn row (gộp kết quả API, dựng lookup cho một phép join): dùng `HashSet` hoặc `Dictionary` với comparer chỉ định rõ, như EF làm. Đừng gọi `list.Contains` hay `Any` trong vòng lặp.
4. Nếu một `DbContext` sống lâu và load nhiều, identity map của nó lớn theo số entity khác nhau. Ưu tiên một context ngắn hạn cho mỗi unit of work.

**Nghỉ 30 phút (ăn trưa).** Ăn và nghỉ.

## 8. Thực hành C# có hướng dẫn

**Block lab · khoảng 75 phút · Việc cần làm:** tự dựng method, dự đoán edge case, test, cố tình phá một rule rồi sửa. **Dừng khi:** các check pass và bạn giải thích được một bug đã tránh và một giả định code cần.

Method dưới đây có cả null policy. Đặt trong một class nếu chạy local; logic không cần database hay framework.

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

`seen` và `result` bắt đầu rỗng ở mỗi batch. Mỗi ID gọi `Add` đúng một lần. ID mới vào set và được thêm vào cuối list; ID cũ không đổi gì. Method chỉ đọc input, không sửa. List giữ reference tới cùng các string, không clone.

Ví dụ gọi:

```csharp
string[] input = ["B2", "A1", "B2", "C3", "A1"];
var unique = StableUnique(input);
Console.WriteLine(string.Join(", ", unique)); // B2, A1, C3
```

Các bước:

1. **Tự dựng method (20 phút).** Đóng ví dụ, viết lại method và giải thích prefix invariant ở mục 5. Nếu bí, xem method đầy đủ ở trên.
2. **Dự đoán edge case (15 phút).** Viết kết quả bạn kỳ vọng trước khi trace hoặc chạy:

   | Input | Câu hỏi |
   |---|---|
   | `[]` | Trả về gì? |
   | `a,A,a` | `a` và `A` có bị gộp không? |
   | `A,A,A` | Còn lại mấy phần tử? |
   | `"",B2,""` | Chuỗi rỗng có hợp lệ không? |
   | input là null | Exception nào? |
   | một ID là null | Exception nào? |

<details>
<summary>Kết quả kỳ vọng</summary>

| Input | Kết quả kỳ vọng |
|---|---|
| `[]` | `[]` |
| `a,A,a` | `a,A` |
| `A,A,A` | `A` |
| `"",B2,""` | `"",B2` |
| input là null | `ArgumentNullException` |
| một ID là null | `ArgumentException` |

</details>

3. **Test và debug (15 phút).** So output với kỳ vọng và kiểm tra input không đổi. Khi lệch, trace batch lỗi nhỏ nhất thay vì viết lại cả method.
4. **Cố tình phá một rule (10 phút).** Append mọi ID, sort result, hoặc dùng `OrdinalIgnoreCase`. Append tất cả thì giữ duplicate; sort thì phá thứ tự xuất hiện đầu; comparer không phân biệt hoa thường gộp `a` và `A`. Khôi phục contract trước khi đo.
5. **Khảo sát collision (10 phút).** Giả sử một comparer trả hash 1 cho mọi ID nhưng vẫn dùng ordinal equality. Kết quả vẫn đúng, nhưng một ID mới có thể phải so với mọi entry trong bucket. Với 128 ID khác nhau, implementation dạng chain làm `128×127/2 = 8.128` lần kiểm tra equality. Key bằng nhau phải có hash bằng nhau, và hash cùng equality phải ổn định trong lúc key được lưu.
6. **Kết thúc (5 phút).** Giải thích một bug đã tránh và một giả định implementation cần.

**Gợi ý debug:** còn duplicate -> chỉ append khi `Add` trả true; thứ tự đổi -> giữ một output list riêng; `a` và `A` bị gộp -> xem comparer; hashing chậm bất thường -> tìm `List.Contains` bị giấu; null behavior đổi -> giữ các check tường minh.

**Nghỉ 10 phút.** Rời màn hình.

## 9. Thí nghiệm có kiểm soát

**Block experiment · khoảng 45 phút · Việc cần làm:** đổi một yếu tố, dự đoán, đo, rồi so với dự đoán. **Dừng khi:** bạn có một quyết định và một điều vẫn chưa thể kết luận.

**So sánh công bằng.** Đo scan và hash trên cùng input, cùng equality và cùng contract thứ tự. Tạo input trước phần đo, và mỗi lần gọi đo phải tạo result mới. Nếu không, một đường có thể dùng lại state đã nóng hoặc bỏ allocation trong khi đường kia vẫn phải cấp phát.

Lab tải về dùng BenchmarkDotNet 0.15.8, N = 128, 512, 2048, tỷ lệ distinct danh nghĩa 10% và 100%, ID có độ dài cố định. Với N = 128 và 10%, số distinct thật là `floor(128×0.10) = 12`. Dự đoán trước khi chạy: ít ID distinct thì List scan ngắn hơn; hash table thường cấp phát nhiều hơn. Big-O không cho ra tỷ lệ tốc độ.

Chạy bản Release, không gắn debugger. Đọc Mean, Error và Allocated cùng nhau. Ở đây Error là nửa khoảng tin cậy 99,9% của BenchmarkDotNet, không phải một chặn sai số được bảo đảm. Allocated gồm storage output và table mới nhưng không gồm input tạo sẵn; nó không đo peak working set, heap đang sống hay p99 của service.

ShortRun mẫu ngày 05/10/2026, n = 512 và mọi ID distinct:

| Cách | Mean | Error | Allocated mỗi operation |
|---|---:|---:|---:|
| Scan | 922,355 µs | 2.261,779 µs | 8.384 B |
| Hash | 22,218 µs | 19,147 µs | 42.896 B |

Lần chạy dùng Debian 13, Intel Xeon Platinum 8573C, .NET 10.0.12, ba warmup và ba measurement iteration cho mỗi case. Khoảng sai số rất rộng, nên thời gian chỉ để minh họa, không phải mức tăng tốc đáng tin cho service. Số byte cấp thêm cho thấy trade-off, không phải memory của cả ứng dụng. [Report đầy đủ](../../../lessons/2026-10-05-cost-model/benchmark-report.md) có ma trận workload.

### Sổ thí nghiệm của bạn

Đổi một yếu tố (n, tỷ lệ distinct, độ dài key hoặc initial capacity) và giữ nguyên output contract. Kiểm tra correctness trước khi đo thời gian. Đừng benchmark một method có counter so sánh với một method không có: counter đã làm thay đổi công việc.

| Viết trước khi chạy | Viết sau khi chạy |
|---|---|
| Kích thước input, u thật, độ dài và phân bố key | Tham số và môi trường thật |
| Dự đoán và cơ chế giải thích | Mean, interval, allocation |
| Một yếu tố sẽ đổi | Dự đoán có đúng không |
| Kết quả correctness kỳ vọng | Lỗi hoặc điều bất ngờ |
| Điều gì khiến bạn chưa thể kết luận? | Quyết định được hỗ trợ và giới hạn còn lại |

Nếu không chạy benchmark, dùng report mẫu để luyện cách diễn giải và để trống phần số đo của bạn. Nếu thiếu kết quả hoặc quá nhiễu, kết luận "chưa đủ số đo để khẳng định tăng tốc". Kiểm tra cách tạo input, comparer, build mode và interval trước khi bịa lý do cho một tỷ lệ bất ngờ. Harness Dry chỉ kiểm tra code chạy được; nó không phải số đo performance.

**Nghỉ 10 phút.** Rời màn hình.

## 10. Đổi yêu cầu: báo cáo duplicate

**Block transfer · khoảng 35 phút · Việc cần làm:** thiết kế trước, rồi đọc lời giải, rồi trace bảng. **Dừng khi:** bạn đã chạy lời giải của mình với bốn input.

Team support cần count thay cho danh sách ID unique. Với `B2,A1,B2,C3,A1` trả `[(B2,2),(A1,2)]` và bỏ các ID chỉ xuất hiện một lần. Giữ ordinal identity, thứ tự xuất hiện đầu, input không đổi và null policy như cũ.

Hãy thiết kế trước khi đọc tiếp. Bạn cần một lookup cho count và một list riêng để giữ thứ tự. Mỗi lần xuất hiện thì tăng count; chỉ lần đầu mới thêm ID vào list.

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

Invariant gồm hai phần: `counts` bằng số lần xuất hiện trong prefix đã đọc, và `order` chứa mỗi ID đã gặp một lần theo thứ tự xuất hiện đầu. Lượt duyệt `order` cuối cùng giữ các count lớn hơn một. Expected O(n+u) = O(n), thêm O(u) storage, dưới cùng các giả định về hashing và key. Đừng dựa vào thứ tự enumerate của `Dictionary`.

<details>
<summary>Lời giải cho bảng</summary>

| Input | Kết quả |
|---|---|
| `A,B,B,A,C` | `[(A,2),(B,2)]` |
| `a,A,a` | `[(a,2)]` |
| `[]` hoặc `X,Y` | `[]` |
| `A,A,A` | `[(A,3)]` |

Sort theo count sẽ đổi thứ tự báo cáo. Chỉ tăng count cho ID mới sẽ fail với `A,A,A`. Trace `A,B,B,A,C`: `order` vẫn là `A,B,C`, counts thành A=2, B=2, C=1, và lượt cuối trả A rồi B.

</details>

### Production: dedupe một batch không phải là idempotency

Hai service instance đều có thể nhận B2, vì set của mỗi instance bắt đầu rỗng. Một `HashSet` trong một batch không bảo đảm identity cho cả hệ thống. Bạn cần một key mà storage thực thi, ví dụ tenant + event ID, với unique index và cách xử lý conflict.

```sql
-- Chưa chạy trong session này; key là identity mà nghiệp vụ quan tâm.
CREATE UNIQUE INDEX UX_OrderEvents_Tenant_Event
    ON dbo.OrderEvents (TenantId, EventId);

-- INSERT lần thứ hai với cùng (TenantId, EventId) sẽ lỗi 2601
-- (hoặc 2627 với unique constraint). Coi lỗi đó là "đã xử lý rồi".
```

`SELECT` rồi mới `INSERT` vẫn có race. Equality của storage cũng phải khớp identity bạn muốn: collation của SQL Server có thể coi string khác với Ordinal của C#.

Cùng kiểu đánh đổi này xuất hiện trên Azure. [Duplicate detection của Service Bus](https://learn.microsoft.com/azure/service-bus-messaging/duplicate-detection) nhớ các `MessageId` trong một time window cấu hình được và bỏ message gửi lặp. Docs nói window lớn hơn ảnh hưởng throughput vì mọi ID đã ghi đều phải được so khớp, nên hãy giữ window nhỏ nhất có thể. Đó lại là set `seen` của bạn, thêm giới hạn thời gian để chặn memory. Nó chống gửi trùng, nhưng [pattern Idempotent Consumer](https://learn.microsoft.com/azure/architecture/patterns/idempotent-consumer#problems-and-considerations) cảnh báo nó không thay thế việc xử lý idempotent ở consumer. Nếu side effect nằm ngoài transaction database, một unique key riêng không đủ để bảo đảm exactly-once.

Phía Angular, cùng ý tưởng bằng TypeScript:

```typescript
// Set giữ thứ tự insert nên lần xuất hiện đầu thắng. String so sánh phân biệt hoa thường.
const unique = [...new Set(orderIds)];
```

## 11. Tổng hợp và xem lại

**Block synthesis · khoảng 45 phút · Việc cần làm:** giải thích quyết định thành lời hoặc viết ra mà không nhìn ghi chú, rồi tự review. **Dừng khi:** bạn có một câu quyết định và một câu hỏi còn mở.

Đóng các ví dụ và giải thích:

1. Vì sao một `foreach` có thể là Θ(n²)?

<details>
<summary>Đáp án</summary>

Thân vòng lặp tìm trong một list ngày càng dài, nên tổng là `0+1+...+(n-1)` khi input toàn ID khác nhau.

</details>

2. Vì sao cần cả `HashSet` và `List`?

<details>
<summary>Đáp án</summary>

Membership và thứ tự output là hai việc khác nhau. Hash table tốn thêm storage.

</details>

3. Hashing có luôn nhanh hơn không?

<details>
<summary>Đáp án</summary>

Không. Batch nhỏ, u thấp, chi phí key, allocation và cache đều ảnh hưởng.

</details>

4. Với `A,B,A,B`, scan làm bao nhiêu phép so sánh?

<details>
<summary>Đáp án</summary>

`0+1+1+2 = 4`, so với sáu khi bốn ID khác nhau.

</details>

Một lời giải thích cuối tốt nêu contract, workload kỳ vọng, cấu trúc đã chọn, lập luận ủng hộ và một giới hạn. Ví dụ: "Với nhiều ID khác nhau có độ dài bị chặn, tôi dùng HashSet cùng List. Invariant giữ thứ tự xuất hiện đầu, còn số lần scan tăng bậc hai. Hashing là expected tuyến tính dưới các giả định phù hợp và tốn thêm storage. Benchmark mẫu minh họa trade-off nhưng độ bất định của thời gian rất lớn. Tôi cần số liệu thật về phân bố key và memory trước khi hứa latency production."

Tự review bốn điểm: edge case và invariant; giả định về n, u và chi phí key; số đo có công bằng không và giới hạn của nó; biến thể đếm duplicate có giữ thứ tự không. Nếu giải thích chưa rõ, quay lại một counterexample nhỏ và thử một ID mới. Sau một khoảng thời gian, tự dựng lại các phép đếm hoặc biến thể mà không nhìn ghi chú. Sai thì ôn sớm hơn, nhớ dễ thì giãn dài hơn. Lịch 1/3/7 ngày chỉ là điểm bắt đầu, bạn điều chỉnh được.

Câu hỏi để mang theo: identifier dài thì thay đổi gì? Một batch có thể dùng bao nhiêu memory? Identity theo tenant nên khớp với equality của storage thế nào? Chọn một câu; đừng mở rộng mục tiêu hôm nay mãi.

## Đọc thêm

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) và [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0): kiểm tra equality, giá trị trả về và resize.
- [EF Core: Efficient querying](https://learn.microsoft.com/ef/core/performance/efficient-querying#tracking,-no-tracking-and-identity-resolution) và [Identity resolution](https://learn.microsoft.com/ef/core/change-tracking/identity-resolution): change tracker như một dictionary.
- [Azure Service Bus duplicate detection](https://learn.microsoft.com/azure/service-bus-messaging/duplicate-detection): seen set có giới hạn thời gian ở mức message.
- [SQL Server unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17): uniqueness do storage thực thi.
- [Hướng dẫn lab C#](../../../labs/cost-model/dotnet/README.vi.md): setup, lệnh benchmark và troubleshooting tùy chọn.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bản đồ chủ đề](../../references/topic-map.md) - Chọn phần nền tảng hoặc chủ đề muốn học sâu tiếp theo.
- [Hướng dẫn lab C#](../../../labs/cost-model/dotnet/README.vi.md) - Cài SDK, lệnh chạy và cách xử lý lỗi benchmark.

---

[Danh sách bài học](../../README.md) · [Bài sau: Bài 02 - Tìm biên và cửa sổ thời gian →](../boundary-search/lesson.md)
<!-- LESSON_NAVIGATION_END -->
