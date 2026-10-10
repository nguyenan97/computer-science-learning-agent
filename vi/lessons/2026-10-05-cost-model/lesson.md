# Bài 01 - Big-O và cấu trúc dữ liệu: dedupe mã đơn hàng bằng C#

[English](../../../lessons/2026-10-05-cost-model/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip)

Một vòng lặp đơn giản có thể thực hiện hàng tỷ phép so sánh nếu mỗi bước lại tìm trong một danh sách dài. Bài này phân tích chi phí đó, dùng `HashSet` để giảm việc tìm kiếm và xem phần bộ nhớ phải trả thêm. Cùng quyết định này xuất hiện trong change tracker của EF Core, duplicate detection của Azure Service Bus và unique index của SQL Server.

**Mục tiêu:** viết hàm dedupe mã đơn hàng, giữ thứ tự xuất hiện đầu tiên. Sau đó, giải thích khi nào nên tìm tuần tự và khi nào nên dùng hash, dựa trên tính đúng đắn, số phép so sánh, thời gian chạy và lượng bộ nhớ cấp phát. Kiến thức cần có: vòng lặp và các collection cơ bản của C#.

## Các ý tưởng chính

- **Mô hình chi phí.** Muốn so sánh thuật toán, trước hết phải chọn đại lượng để đếm. Bài này đếm phép so sánh giữa hai ID; đó là mô hình đơn giản hóa, không phải số lệnh CPU thực thi.
- **Big-O và Θ.** Big-O cho cận trên của mức tăng chi phí khi input đủ lớn, bỏ qua hệ số hằng: O(n) không tăng nhanh hơn tuyến tính, nhưng cũng có thể tăng chậm hơn, chẳng hạn O(1) cũng là O(n). Θ cho cận tiệm cận chặt: cận trên và cận dưới cùng bậc; `3n` là Θ(n), còn `n²` là Θ(n²). Khi n gấp đôi, hai công thức này tăng lần lượt hai và bốn lần, nhưng ký hiệu O không tự cam kết tỷ lệ đó hay thời gian chạy.
- **Worst case và expected case.** Worst case xét input tốn nhiều công việc nhất trong các input cùng kích thước. Expected case xét chi phí kỳ vọng dưới giả định xác suất cụ thể; với hash, phải nêu giả định về phân bố hash thay vì mặc định mọi input đều thuận lợi.
- **Phân tích amortized.** Cộng chi phí của cả chuỗi thao tác rồi phân bổ cho từng thao tác, không cần giả định xác suất. Một lần mở rộng bảng có thể đắt, nhưng không diễn ra ở mọi lần thêm phần tử; phần sau sẽ tính tổng chi phí này.
- **Invariant.** Một tính chất được giữ sau mỗi bước của vòng lặp. Nếu đúng lúc đầu, được mỗi bước bảo toàn và suy ra yêu cầu khi vòng lặp kết thúc, nó giúp chứng minh thuật toán đúng. Ví dụ: sau mỗi bước, kết quả chỉ chứa một bản của mỗi ID đã đọc.

## 1. Kiểm tra kiến thức nền

**Khoảng 20 phút - Kiểm tra kiến thức nền:** thử trả lời rồi mở từng đáp án để đối chiếu. Đây là bài đầu tiên, nên chưa có câu hỏi ôn bài trước. **Dừng khi:** xác định được câu nào cần đọc lại.

1. Với `B2,A1,B2,C3,A1`, kết quả giữ thứ tự xuất hiện đầu là gì? Sắp xếp theo ID sẽ làm kết quả đổi thế nào?

<details>
<summary>Đáp án</summary>

`B2,A1,C3`. Sắp xếp theo ID cho ra `A1,B2,C3`, trái yêu cầu giữ thứ tự xuất hiện đầu.

</details>

2. Nếu dedupe `A,B,C,D` bằng cách so mỗi ID với danh sách kết quả đã có, cần bao nhiêu phép so sánh?

<details>
<summary>Đáp án</summary>

`0+1+2+3 = 6`. Phần tử đầu không so với ai, phần tử thứ hai so với một phần tử, và cứ thế.

</details>

3. Hai ID có cùng hash thì có chắc bằng nhau không? Một set trong process này có ngăn process khác xử lý duplicate không?

<details>
<summary>Đáp án</summary>

Cả hai đều không. Hai ID khác nhau vẫn có thể có cùng hash, nên phải so sánh giá trị để phân biệt. Mỗi process có set riêng; việc một bên đã lưu ID không làm set bên kia thay đổi.

</details>

4. Cột `Allocated` của benchmark có phải là lượng bộ nhớ được sử dụng nhiều nhất cùng lúc không?

<details>
<summary>Đáp án</summary>

Không. `Allocated` đo tổng bộ nhớ mới được cấp phát cho thao tác đang đo. Bộ nhớ còn được sử dụng nhiều nhất cùng lúc là đại lượng khác: các vùng nhớ cấp phát trước đó có thể đã được thu hồi.

</details>

Nếu chưa quen tìm tuần tự, thử với `[B2, A1]`: tìm `B2` dừng sau một phép so sánh, còn tìm `C3` phải kiểm tra cả hai phần tử mới kết luận không có. Dedupe `[X, Y, X]` trả về `[X, Y]` và cần `0+1+1 = 2` phép so sánh. Nếu phần này đã rõ, dành thời gian còn lại cho thí nghiệm và bài tập đổi yêu cầu.

## 2. Yêu cầu từ một tác vụ xử lý đơn hàng

**Yêu cầu · 10 phút.** Nêu quy tắc thứ tự, so sánh ID và null. **Hoàn thành khi:** ví dụ năm ID có một kết quả rõ ràng.

Một tác vụ logistics nhận danh sách mã đơn hàng từ log hoặc từ một batch message. Một mã có thể xuất hiện nhiều lần. Yêu cầu là trả về mỗi ID **một lần, theo thứ tự xuất hiện đầu tiên**.

```text
Input : B2, A1, B2, C3, A1
Output: B2, A1, C3
```

Giữ ba yêu cầu sau khi tối ưu:

- Dùng `StringComparer.Ordinal`: `a` khác `A`. Không tự xóa khoảng trắng hay đổi chữ hoa thành chữ thường.
- Giữ thứ tự xuất hiện đầu. Sắp xếp thành `A1,B2,C3` là sai yêu cầu.
- Không sửa input. Danh sách và từng ID đều phải khác null; code sẽ báo lỗi nếu gặp null. Chuỗi rỗng vẫn hợp lệ trong ví dụ này.

Bài toán chỉ dedupe **trong một batch**, chưa bảo đảm mỗi message được xử lý đúng một lần trên toàn hệ thống. Mục 10 sẽ phân tích giới hạn này. Ký hiệu `n` là số phần tử của input, `u` là số ID khác nhau.

**Thử suy nghĩ:** ví dụ trên có bao nhiêu phần tử và bao nhiêu ID khác nhau? Với output tạm `[B2, A1]`, muốn biết `C3` đã thấy chưa thì phải làm gì?

<details>
<summary>Đáp án</summary>

n = 5 và u = 3. So `C3` với `B2`, rồi với `A1`. Chỉ sau khi kiểm tra hết danh sách mới biết `C3` chưa xuất hiện. Bảng ở mục 3 sẽ theo dõi chi phí của từng bước.

</details>

## 3. Một vòng lặp, rất nhiều công việc ẩn

**Chạy từng bước · 15 phút.** Đếm từng phép so sánh và suy ra tổng khi mọi ID khác nhau. **Hoàn thành khi:** dựng lại được tổng thay vì đếm dòng vòng lặp.

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

Tổng là **6 phép so sánh**, dù `foreach` chỉ chạy 5 lần. Số đếm này thuộc mô hình đã chọn; nó không đo số lệnh CPU của .NET runtime.

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

Trong trường hợp này, input gấp đôi thì số phép so sánh tăng gần gấp bốn. Chưa thể đổi số đếm thành thời gian chạy: kết quả còn phụ thuộc CPU, runtime và dữ liệu.

## 4. Big-O nói gì và không nói gì

**Mô hình chi phí · 10 phút.** Giải thích cận tiệm cận và giả định độ dài ID. **Hoàn thành khi:** bác bỏ được nhận định thời gian chỉ dựa vào Big-O.

**Định nghĩa chính thức.** `T(n)` là `O(n²)` nếu tồn tại hằng số C và n₀ sao cho `T(n) ≤ C·n²` với mọi `n ≥ n₀`. Nghĩa là "tăng không nhanh hơn n²", không phải "chạy n² giây".

Khi mọi ID đều khác nhau, số hạng n² chi phối `n(n-1)/2`, nên chi phí tìm tuần tự là **Θ(n²)**: cận trên và cận dưới cùng bậc. Viết O(n²) vẫn đúng nhưng ít thông tin hơn; một thuật toán O(n) cũng là O(n²). Khi biết cận tiệm cận chặt, nên nêu rõ.

**Nếu mọi ID đều là `A` thì sao?** Sau ID đầu, mỗi lần `Contains` đều tìm thấy ngay: tổng cộng n-1 phép so sánh, tức Θ(n). Kết quả worst case không có nghĩa mọi input đều tốn chi phí như nhau.

Với u ID khác nhau, danh sách kết quả dài tối đa u phần tử, nên chi phí có cận trên `O(n(1+u))`. Khi u nhỏ, tìm tuần tự có thể đủ tốt. Khi u có cùng bậc với n, tức u = Θ(n), worst case là Θ(n²); chẳng hạn khi mọi ID đều khác nhau.

**Thử suy nghĩ:** bạn chỉ thấy một `foreach` duyệt n phần tử. Có kết luận được là O(n) không?

<details>
<summary>Đáp án</summary>

Chưa. Phải cộng chi phí của thân vòng lặp qua tất cả các bước. `Contains`, một query database hay một lời gọi service đều có chi phí riêng; số dòng code không cho biết tổng công việc.

</details>

## 5. Tách "đã thấy chưa?" khỏi "thứ tự output"

**Cơ chế · 15 phút.** Chứng minh bất biến tiền tố và tính phần bộ nhớ phụ. **Hoàn thành khi:** phân biệt được kỳ vọng, amortized và trường hợp xấu nhất.

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

`Add` vừa kiểm tra vừa thêm phần tử, nên không cần gọi `Contains` trước rồi mới gọi `Add`. Không dựa vào thứ tự duyệt của `HashSet`; `result.Add` theo thứ tự input mới bảo đảm thứ tự kết quả.

### Vì sao hash giảm chi phí tìm kiếm

Hàm hash biến ID thành một số để chọn bucket chứa các phần tử cần kiểm tra. Thay vì tìm trong cả danh sách, bạn chỉ tìm trong bucket đó. Collision xảy ra khi các ID khác nhau rơi vào cùng bucket. **Cùng hash chưa chắc cùng ID**: runtime vẫn phải so sánh giá trị để phân biệt.

Load factor là số phần tử đang lưu chia cho số bucket: 8 phần tử và 16 bucket cho ra 0,5. Khi bảng tăng kích thước đủ nhanh so với số phần tử, số phần tử trung bình trong mỗi bucket được kiểm soát.

Nếu hash phân bố tốt, kích thước bucket trung bình được kiểm soát và chi phí xử lý ID bị giới hạn, thì chi phí tìm kiếm kỳ vọng là hằng số. Cần phân biệt ba cách phân tích:

- **Expected case** xét chi phí kỳ vọng dưới giả định về phân bố hash. Kết quả này không bảo đảm cho từng input cụ thể.
- **Amortized** tính cả chi phí mở rộng bảng. Một lần resize có thể tốn O(u), nhưng nếu dung lượng tăng theo hệ số nhân, tổng chi phí dạng `1+2+4+...` vẫn là O(u). Đây là nguyên lý phân tích, không phải khẳng định .NET dùng đúng các mức dung lượng đó.
- **Worst case**: hash phân bố kém có thể tạo chuỗi collision dài, khiến cả batch tốn O(n²). .NET có biện pháp bảo vệ với một số string comparer; không thể suy ra comparer tự viết cũng được bảo vệ như vậy.

Dưới các giả định trên, cả batch có **chi phí kỳ vọng O(n)**, đã tính việc resize bằng phân tích amortized. Lab đếm n lần gọi `Add`, nhưng mỗi lần gọi còn có công việc tính hash, so sánh và có thể mở rộng bảng.

Nếu ID dài tối đa L ký tự, tính hash và so sánh có thể tốn O(L). Khi L thay đổi theo input, đưa nó vào mô hình: chi phí kỳ vọng `O(n(1+L))`. Dùng `HashSet` không loại bỏ chi phí đọc các ký tự của ID.

### Chứng minh bằng invariant

Sau mỗi bước, `seen` chứa đúng các ID trong phần input đã đọc; `result` chứa mỗi ID đó một lần, theo thứ tự xuất hiện đầu.

Ban đầu cả hai collection đều rỗng, nên invariant đúng. Với ID đã có, `Add` trả false và kết quả không đổi. Với ID mới, `Add` trả true và ID được thêm vào cuối `result`, giữ đúng thứ tự. Khi đọc hết input, invariant suy ra yêu cầu bài toán. Cách tìm kiếm thay đổi, nhưng kết quả vẫn đúng.

### Bộ nhớ: cùng Big-O không có nghĩa cùng số byte

| Cách | Thời gian theo mô hình | Bộ nhớ phụ, không tính output | Output |
|---|---|---|---|
| Tìm tuần tự trong List | O(n(1+u)); Θ(n²) khi tất cả khác nhau | O(1) | O(u) |
| HashSet + List | Kỳ vọng O(n), dưới các giả định đã nêu | O(u) | O(u) |

`HashSet` cần thêm các mảng bucket và entry. `List` giữ tham chiếu tới string của input, không tạo bản sao của từng string. Khi cần mảng lớn hơn, runtime cấp phát mảng mới và sao chép dữ liệu; mảng cũ có thể chờ GC thu hồi nếu không còn được tham chiếu.

**Tổng bộ nhớ cấp phát, bộ nhớ còn sống và peak working set là ba đại lượng khác nhau.** Peak live memory là lượng bộ nhớ còn sống nhiều nhất cùng lúc; peak working set là lượng bộ nhớ của process đang nằm trong RAM lớn nhất. Cấp phát hai mảng lần lượt không có nghĩa cả hai sẽ cùng tồn tại mãi.

`new HashSet<string>(n, ...)` hoặc `new List<string>(n)` có thể giảm số lần resize nếu biết kích thước phù hợp. Tuy nhiên, n lớn và u nhỏ sẽ làm cấp phát dư. Nếu cấp sẵn theo n, phần bộ nhớ đó là O(n), không phải O(u) khi u nhỏ và độc lập với n. Bản chính chưa áp dụng tối ưu này.

**Nghỉ 10 phút.** Rời màn hình.

## 6. Đọc nguồn và trả lời câu hỏi nghiên cứu

**Khoảng 45 phút - Đọc và đối chiếu nguồn:** trả lời bốn câu hỏi bằng lời của bạn, nêu nhận định và bằng chứng hỗ trợ. **Dừng khi:** mỗi câu có nguồn và giới hạn của nhận định.

Nguồn của bài:

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) và [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0): phép so sánh, giá trị trả về và việc resize.
- [MIT OCW: Hashing II, trang 1-3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf): load factor và phân tích amortized cho việc tăng kích thước bảng.
- [BenchmarkDotNet good practices](https://benchmarkdotnet.org/articles/guides/good-practices.html): thiết kế benchmark công bằng ở chế độ Release.

Bốn câu hỏi:

1. `List.Contains` giấu công việc gì?

<details>
<summary>Đáp án</summary>

Tìm tuần tự trong danh sách: dừng khi tìm thấy ID bằng nhau, hoặc đọc hết danh sách mới kết luận không có.

</details>

2. Vì sao một lần `Add` có thể tốn O(u) nhưng cả batch vẫn có chi phí kỳ vọng O(n)?

<details>
<summary>Đáp án</summary>

Chi phí resize cộng dồn theo dạng `1+2+4+...` nên tổng là O(u). Chi phí tìm kiếm kỳ vọng O(1) còn dựa trên giả định hash phân bố tốt và chi phí xử lý ID bị giới hạn.

</details>

3. Vì sao collision không làm sai kết quả nhưng có thể làm thuật toán chậm hơn?

<details>
<summary>Đáp án</summary>

Phép so sánh giá trị vẫn phân biệt được các ID khác nhau, nên kết quả đúng. Chuỗi collision dài làm mỗi lần tìm kiếm phải so sánh nhiều hơn.

</details>

4. Benchmark với dữ liệu giả lập cho biết gì về một service thực tế?

<details>
<summary>Đáp án</summary>

Nó chỉ cung cấp bằng chứng cho workload và phạm vi đã đo. Phân bố ID, mức sử dụng bộ nhớ và p99 latency của service thực tế cần phép đo riêng.

</details>

## 7. Đọc mã nguồn: collection và EF Core

**Khoảng 45 phút - Theo dõi cách triển khai:** đọc đường xử lý của `HashSet.Add`, rồi đối chiếu với cách EF Core dùng dictionary. **Dừng khi:** giải thích được dictionary của EF Core lưu gì và giải quyết vấn đề nào.

### Mã nguồn collection

`List.Contains` gọi `IndexOf` để tìm trong một mảng. .NET runtime có thể tối ưu riêng cho một số kiểu dữ liệu, làm giảm hệ số hằng; khi không tìm thấy, nó vẫn phải kiểm tra toàn bộ các phần tử.

`HashSet.Add` đi theo đường khác:

```text
ID -> tính hash -> chọn bucket -> xem các entry trong bucket
   -> hash khớp VÀ ID bằng nhau? trả false
   -> nếu chưa, sang entry kế tiếp
   -> không có entry bằng? lấy một slot (resize khi cần), insert, trả true
```

Mỗi bucket là điểm bắt đầu của một chuỗi entry. Các entry cùng bucket được nối thành collision chain. Hash đã lưu giúp loại nhanh nhiều phần tử không khớp; phép so sánh giá trị mới quyết định hai ID có bằng nhau không. Resize tạo các mảng lớn hơn rồi chuyển entry sang, nên một lần `Add` có thể tốn nhiều công việc dù chi phí amortized nhỏ.

Chạy tay ba trường hợp: set rỗng nhận B2; B2 xuất hiện lại; A1 là ID mới nhưng có cùng hash với B2.

<details>
<summary>Đáp án</summary>

B2 được thêm vào set, `Add` trả true. Khi B2 xuất hiện lại, phép so sánh tìm thấy ID bằng nhau và `Add` trả false. A1 được so với B2, thấy khác rồi được thêm vào, `Add` trả true. `List` riêng giữ thứ tự kết quả qua cả ba bước.

</details>

Đọc mã nguồn ở commit .NET 10 đã chọn: [List.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/List.cs#L336) và [HashSet.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/HashSet.cs#L1411). Tìm các bước chọn bucket, so sánh ID, trả false và resize. Không cần build runtime để đọc đoạn code này.

### Ví dụ từ EF Core: dùng dictionary để tìm entity theo khóa

EF Core áp dụng cùng ý tưởng khi quản lý các entity đã tải từ database. Đoạn mã được phân tích thuộc [dotnet/efcore](https://github.com/dotnet/efcore), commit `7adff35c6c583fa6f7aa3939389ab3314be330ab`.

**Vấn đề cần giải quyết.** Trong tracking query, các dòng có cùng khóa phải dùng chung một entity. Nếu 100 post cùng tham chiếu một blog, EF Core cần dùng lại một instance `Blog` để theo dõi thay đổi nhất quán, thay vì giữ 100 instance có cùng khóa. Cơ chế này gọi là identity resolution. Trước khi tạo entity từ mỗi dòng, EF Core phải trả lời: "đã có entity mang khóa này chưa?"

**Đường xử lý trong mã nguồn:**

- Ở [`IdentityMap.cs` dòng 18](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L18), tracker giữ `Dictionary<TKey, InternalEntityEntry> _identityMap`. Khóa là giá trị khóa của entity; giá trị tương ứng là entry mà tracker đang quản lý.
- Ở [dòng 36](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L36), dictionary dùng comparer của khóa được lấy từ model. Cũng như lựa chọn `StringComparer.Ordinal` trong bài, phép so sánh phải khớp với cách ứng dụng xác định hai khóa là một.
- Tracking query tìm theo khóa **trước khi tạo entity**. [`ShapedQueryCompilingExpressionVisitor` dòng 473-513](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/Query/ShapedQueryCompilingExpressionVisitor.cs#L473) sinh lời gọi `QueryContext.TryGetEntry(key, keyValues, ...)`, rồi đi qua state manager tới identity map. Nếu đã có, query dùng lại `entry.Entity`; nếu chưa có, query mới tạo entity. Identity map tìm khóa bằng một lần truy cập dictionary ([dòng 105](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L105)).
- Đăng ký entity mới từ query là bước riêng: [`QueryContext.StartTracking`](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/Query/QueryContext.cs#L148) gọi [`StateManager.StartTrackingFromQuery`](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/StateManager.cs#L324). `TryGetEntry(entity)` ở đầu method kiểm tra tham chiếu object, không phải khóa của dòng dữ liệu; sau đó method tạo entry và đăng ký qua `AddOrUpdate` ([dòng 347](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/StateManager.cs#L347)).
- Attach một instance có khóa trùng với entity đang được theo dõi là một luồng xử lý khác. `IdentityMap.Add` có thể ném identity conflict ([dòng 267-279](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L267)); `AddOrUpdate` của query đặt `updateDuplicate: true` nên bỏ qua nhánh đó. Lỗi xung đột khi attach khác với việc dùng lại entity trong query.

**Chi phí được tài liệu nêu rõ.** Tài liệu [efficient querying](https://learn.microsoft.com/ef/core/performance/efficient-querying#tracking,-no-tracking-and-identity-resolution) cho biết EF giữ dictionary các instance đang theo dõi và kiểm tra theo khóa khi tải dữ liệu mới. Tìm kiếm và duy trì dictionary đều tốn thời gian. Với `AsNoTracking()`, EF không dùng identity resolution, nên trong ví dụ 100 post, cùng một blog được tạo thành 100 instance. [Tài liệu identity resolution](https://learn.microsoft.com/ef/core/change-tracking/identity-resolution#identity-resolution-and-queries) giải thích thêm: phải nhớ các instance đã trả về sẽ làm tăng chi phí khi đọc liên tục một lượng lớn entity.

**Đối chiếu với thuật toán trong bài:**

| Bài học này | EF Core |
|---|---|
| Set `seen` | Dictionary `_identityMap`, dùng khóa của entity |
| Chọn `StringComparer.Ordinal` | Comparer của khóa lấy từ model |
| O(u) bộ nhớ phụ để tránh tìm tuần tự lặp lại | Một entry cho mỗi entity đang theo dõi; detach hoặc xóa dữ liệu của tracker sẽ xóa entry |
| Bỏ set để giảm bộ nhớ phụ | `AsNoTracking`: không có dictionary, nhưng có thể tạo entity trùng khóa |

**Suy luận từ mô hình chi phí.** Giả sử mỗi dòng đều phải tìm trong một danh sách entity đang theo dõi. Khi tải n dòng có u entity khác nhau, số phép so sánh khóa có cận trên O(n·u), cùng dạng với `List.Contains`. Đây là phương án giả định để so sánh với dictionary, không phải cách EF từng triển khai. Suy luận này cũng chưa cho biết thời gian chạy của query.

**Áp dụng trong dự án:**

1. Với danh sách lớn chỉ để đọc, như grid hoặc export, dùng `AsNoTracking()` để bỏ chi phí dictionary và snapshot theo dõi thay đổi. Các dòng tham chiếu cùng một customer có thể nhận những instance khác nhau.
2. Nếu kết quả chỉ để đọc nhưng các dòng phải dùng chung một instance của entity liên quan, dùng `AsNoTrackingWithIdentityResolution()`. Đổi lại, query cần một dictionary tạm.
3. Khi gộp kết quả API hoặc nối dữ liệu theo khóa trên hàng nghìn dòng, cân nhắc `HashSet` hoặc `Dictionary` với comparer phù hợp. Một lần `list.Contains` hay `Any` trong mỗi bước có thể làm chi phí tìm tuần tự lặp lại.
4. Một `DbContext` tồn tại lâu và tải nhiều dữ liệu sẽ giữ identity map lớn theo số entity khác nhau. Nên giới hạn vòng đời context theo một đơn vị công việc.

### Kiểm tra tùy chọn: quan sát identity resolution khi chạy query

Dành 15 phút của phần đọc mã nguồn cho kiểm tra này. Ví dụ dùng .NET SDK 10.0.401, EF Core SQLite 10.0.12 và database SQLite trong RAM, không cần cài database server.

Hai dòng `Post`, ID 1 và 2, cùng có `BlogId = 1`. Với mỗi chế độ query, dự đoán `ReferenceEquals(posts[0].Blog, posts[1].Blog)` trả về true hay false và context theo dõi bao nhiêu entity. Vì sao mỗi query cần một `DbContext` mới? Chạy kiểm tra; nếu không restore được package, chạy tay theo code và đối chiếu đáp án.

<details>
<summary>Đáp án</summary>

ZIP lab có cả `IdentityDemo`. SDK/runtime trong `global.json` dùng chung và project được pin như lab chính; lock file cố định dependency EF Core trực tiếp và gián tiếp. Restore lần đầu cần NuGet. Chạy từ `dotnet` sau giải nén hoặc `labs/cost-model/dotnet` trong checkout:

```bash
dotnet restore IdentityDemo --locked-mode
dotnet run --no-restore -c Release --project IdentityDemo
```

`IdentityDemo/IdentityDemo.csproj`:

<!-- lab-file: IdentityDemo/IdentityDemo.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RuntimeFrameworkVersion>10.0.12</RuntimeFrameworkVersion>
    <RollForward>Disable</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore.Sqlite" Version="10.0.12" />
  </ItemGroup>
</Project>
```

`IdentityDemo/packages.lock.json`:

<!-- lab-file: IdentityDemo/packages.lock.json -->
```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {
      "Microsoft.EntityFrameworkCore.Sqlite": {
        "type": "Direct",
        "requested": "[10.0.12, )",
        "resolved": "10.0.12",
        "contentHash": "rRXkKBWHjtngj2DYqSXOThGpqiR0LQkxk0b0PIVDhVEzfwpgOR7dbKMw1/My8unDCTCwn/blclR7imxntYGvEg==",
        "dependencies": {
          "Microsoft.EntityFrameworkCore.Sqlite.Core": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Configuration.Abstractions": "10.0.12",
          "Microsoft.Extensions.DependencyModel": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12",
          "SQLitePCLRaw.bundle_e_sqlite3": "2.1.12",
          "SQLitePCLRaw.core": "2.1.12"
        }
      },
      "Microsoft.Data.Sqlite.Core": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "2aL9eL5HQr0V4b8V909SD+jQAx6qnTTl7sT/v3D8dIvmr2UGdpZIQxqm1pj2Js3e4EYTvpw0oMH7DjapJJuPPw==",
        "dependencies": {
          "SQLitePCLRaw.core": "2.1.12"
        }
      },
      "Microsoft.EntityFrameworkCore": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "e7OrVN8U5yr4kuwdTHWBHGVQIVsGfMkAr0Ej1/BnrS989Q0XBVANpIzNZ2bc1GvMZ0/XwMt5InTnmKskxGy99Q==",
        "dependencies": {
          "Microsoft.EntityFrameworkCore.Abstractions": "10.0.12",
          "Microsoft.EntityFrameworkCore.Analyzers": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12"
        }
      },
      "Microsoft.EntityFrameworkCore.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "kDrux7T6C3V/YYYe2LXr7x6AEsVyq5Y2YoTE9er1SwbDtap3z1g8RgxNh5eKQVyB4T+DKvBBJ4Ezd/VZzJQJZg=="
      },
      "Microsoft.EntityFrameworkCore.Analyzers": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "Kd4o2oO1A6dfKxjz5LS16QyLtpCFTUiFWwmBABETAXRsSImBdRdWeKjSgbbRhAMiV3a3/nWr95ZtzClT4uaADQ=="
      },
      "Microsoft.EntityFrameworkCore.Relational": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "OiHmr8XzX96dbgMsYGe8qoqg4KxibdZG2r0QUVJBGktFInOp8IrABe8jvcbo5hrqeWfbwpK7fCEBiEPbY/ik4A==",
        "dependencies": {
          "Microsoft.EntityFrameworkCore": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Configuration.Abstractions": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12"
        }
      },
      "Microsoft.EntityFrameworkCore.Sqlite.Core": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "DAGu68RfIDD5d6qYhtQqMUsRS7hKKFqHI6h/9VUa4FjMcQ8+IJA0rK+1pDZtrDJ+yi3YAG0L2TSViZ0csEDM0w==",
        "dependencies": {
          "Microsoft.Data.Sqlite.Core": "10.0.12",
          "Microsoft.EntityFrameworkCore.Relational": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Configuration.Abstractions": "10.0.12",
          "Microsoft.Extensions.DependencyModel": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12",
          "SQLitePCLRaw.core": "2.1.12"
        }
      },
      "Microsoft.Extensions.Caching.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "sI3A6MUAyZwccLnwq0cXuRmC3WBtXieimBWafXSfhRJ4jnM2uGVXrqImDDVyW27u4vVaTOGlJxNJd8d1FGvCNQ==",
        "dependencies": {
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.Caching.Memory": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "fhC3DHcBcFF4bXvHIxFtXJYNut7q7ZItqNFcgWfrIgmpVImlcEKNHhE7ztpNSPJYMHYYStS5QGND2I5mC26yeA==",
        "dependencies": {
          "Microsoft.Extensions.Caching.Abstractions": "10.0.12",
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12",
          "Microsoft.Extensions.Logging.Abstractions": "10.0.12",
          "Microsoft.Extensions.Options": "10.0.12",
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.Configuration.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "8xaGcvS/qZ1otoxPQCEJkNva389CVL/plNcvIETZhQTETYdRkYDPEYhUMoAGONo4FU45ufdfE0j29AfWVVj0wA==",
        "dependencies": {
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.DependencyInjection": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "lXyK2O5GoYvfxW8eCFcD16JFbcoSTM1sJkAM0UHS1jZyl9NYMW64Tqm6OQFT0IDBjZi+xHt95/Zg+nxZhGFhZg==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12"
        }
      },
      "Microsoft.Extensions.DependencyInjection.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "9/qymSh7hVDMGTGwrLz8MRp5zRyXy9adGDOs4HwRdnLil3oZGYuWeZjbmHgCQ9BL1qBroVfgUK3U/nb61617Cw=="
      },
      "Microsoft.Extensions.DependencyModel": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "rDPQVTxh/zMTDF7wHlRqL/jjZbwjAP6315ydBxj51pZW7qkAwGwjoSiMutxYI91xmOE3ZXjAGHbYRqzyJV7Urw=="
      },
      "Microsoft.Extensions.Logging": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "6I46fTPfgYkrjRYfRXbho9WOvOelTnNjWuZws/hzGHDASH1LEJeA4VKK9k3wJvido8o7jJSB5WkMTonX7HM1bA==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection": "10.0.12",
          "Microsoft.Extensions.Logging.Abstractions": "10.0.12",
          "Microsoft.Extensions.Options": "10.0.12"
        }
      },
      "Microsoft.Extensions.Logging.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "+24lC4plfbEDNfLAdTV/SWKS7dW+16X4HdydO3R++134kSNTzcbYA4KpR1Hdh6uWisB8Za3AzwyOn+K+NxWIug==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12"
        }
      },
      "Microsoft.Extensions.Options": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "TDYD33TSRpXKZWlmTXNlj5kCihxatmv2Ec1u6C+bMYLphCS7PoSLE9Pjd/nunDoE7yETk+LLKjVJX78HYtWjpA==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12",
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.Primitives": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "dYfCLR52UA+3DL7C4I/pvSaRPkNqxrUAQmbFL2u0zvYKKzqgrFCJl08Df+F1aYc8leu9JvpC9bsURUdpExcBXQ=="
      },
      "SQLitePCLRaw.bundle_e_sqlite3": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "mAgscpQMLw5/nfA1Q5oJVAT29yROUo1ifZGbbTpx/lwZpSxMUGoYbKfmvdm8oXER+RzxqBmmQzeBEVKfeHv2nw==",
        "dependencies": {
          "SQLitePCLRaw.lib.e_sqlite3": "2.1.12",
          "SQLitePCLRaw.provider.e_sqlite3": "2.1.12"
        }
      },
      "SQLitePCLRaw.core": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "ETpNw9DY3ckWLgRRAeCHj+GKOuPi61aeczkXhgHexUvqoZBAYg8RYESE2J7O1M7+o6QbdSEZwrw9bfqztUVWXg=="
      },
      "SQLitePCLRaw.lib.e_sqlite3": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "fWi8Dbknuhgg72fWinIdjXVaqO1hHL4YBBwVLnr7e1c9TAZwJ0QE38j9syW1hwx6HaqEVTwI+O07WPdZn8Rp0w=="
      },
      "SQLitePCLRaw.provider.e_sqlite3": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "W3oH4XIfCzFrgUSDKHhN6N+dgzA5YHOR2VxX8GB6Qy7CyrJJgxPEG8NirgYWlPQC5P2jz2knSsexWu4tDUL33g==",
        "dependencies": {
          "SQLitePCLRaw.core": "2.1.12"
        }
      }
    }
  }
}
```

`IdentityDemo/Program.cs`:

<!-- lab-file: IdentityDemo/Program.cs -->
```csharp
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

using var connection = new SqliteConnection("Data Source=:memory:");
connection.Open();
var options = new DbContextOptionsBuilder<BlogDb>()
    .UseSqlite(connection).Options;
using (var seed = new BlogDb(options))
{
    seed.Database.EnsureCreated();
    var blog = new Blog { Id = 1 };
    seed.Posts.AddRange(
        new Post { Id = 1, Blog = blog },
        new Post { Id = 2, Blog = blog });
    seed.SaveChanges();
}

Check("Tracking", 0, expectedSame: true, expectedTracked: 3);
Check("NoTracking", 1, expectedSame: false, expectedTracked: 0);
Check("IdentityResolution", 2, expectedSame: true, expectedTracked: 0);
Console.WriteLine("All checks passed.");

void Check(string name, int mode, bool expectedSame, int expectedTracked)
{
    using var db = new BlogDb(options);
    IQueryable<Post> query = db.Posts.Include(p => p.Blog).OrderBy(p => p.Id);
    query = mode switch
    {
        1 => query.AsNoTracking(),
        2 => query.AsNoTrackingWithIdentityResolution(),
        _ => query
    };
    var posts = query.ToList();
    if (posts.Count != 2 || posts.Any(p => p.Blog.Id != 1))
        throw new InvalidOperationException("Expected two posts for Blog 1.");
    bool same = ReferenceEquals(posts[0].Blog, posts[1].Blog);
    int tracked = db.ChangeTracker.Entries().Count();
    Console.WriteLine($"{name}: sameBlog={same}, tracked={tracked}");
    if (same != expectedSame || tracked != expectedTracked)
        throw new InvalidOperationException($"Unexpected result for {name}.");
}

sealed class BlogDb(DbContextOptions<BlogDb> options) : DbContext(options)
{
    public DbSet<Post> Posts => Set<Post>();
}

sealed class Blog
{
    public int Id { get; set; }
}

sealed class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; }
    public Blog Blog { get; set; } = null!;
}
```

Chạy trong thư mục project:

```bash
dotnet run
```

Kết quả dự kiến:

```text
Tracking: sameBlog=True, tracked=3
NoTracking: sameBlog=False, tracked=0
IdentityResolution: sameBlog=True, tracked=0
All checks passed.
```

Tracking query dùng lại một object `Blog`; context theo dõi ba entity: hai post và một blog. `AsNoTracking()` tạo hai object `Blog` khác nhau có cùng khóa và context không theo dõi entity nào. `AsNoTrackingWithIdentityResolution()` dùng tracker tạm để dùng lại một `Blog` trong query; context cũng không theo dõi entity nào. `ReferenceEquals` kiểm tra hai biến có tham chiếu cùng object hay không: cùng giá trị khóa chưa có nghĩa là cùng object.

Context tạo dữ liệu mẫu được dispose trước khi chạy query; mỗi chế độ dùng một context mới để tránh các object đã được theo dõi ảnh hưởng kết quả. Kết nối SQLite được giữ mở để database trong RAM tồn tại qua các context. Các assertion kiểm tra tính đúng đắn, không đo tốc độ query.

</details>

**Nghỉ trưa 30 phút.**

## 8. Thực hành C# có hướng dẫn

**Khoảng 75 phút - Viết và kiểm tra code:** tự viết method, dự đoán các trường hợp biên, chạy test, cố tình vi phạm một yêu cầu rồi sửa. **Dừng khi:** các kiểm tra đều pass, giải thích được một lỗi đã tránh và một giả định mà code cần.

Viết hàm dedupe theo quy tắc so sánh ordinal, thứ tự và null. Dự đoán ca biên rồi đối chiếu với phép quét tham chiếu. Bạn có thể mở ngay lời giải đầy đủ.

<details>
<summary>Đáp án - môi trường, mã đầy đủ và kết quả</summary>

SDK **10.0.401**, runtime **10.0.12**; tắt roll-forward cho SDK/runtime. Đường dẫn file tính từ `dotnet`. Restore dùng các package đã pin; lock file của benchmark pin cả dependency gián tiếp.

`global.json`:

<!-- lab-file: global.json -->
```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
}
```

`Core/Core.csproj`:

<!-- lab-file: Core/Core.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

`Core/Deduplication.cs`:

<!-- lab-file: Core/Deduplication.cs -->
```csharp
namespace CostModel;

public sealed record OrderCount(string Id, int Count);

// Contract: non-null IDs, ordinal equality, first-occurrence order, unchanged input.
public static class Deduplication
{
    public static List<string> Scan(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            if (!result.Contains(value)) result.Add(value);
        }
        return result;
    }

    public static List<string> Hash(IReadOnlyList<string> values,
        IEqualityComparer<string>? comparer = null)
    {
        ArgumentNullException.ThrowIfNull(values);
        var seen = new HashSet<string>(comparer ?? StringComparer.Ordinal);
        var result = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            // Add is false for an existing equal ID; no separate Contains lookup.
            if (seen.Add(value)) result.Add(value);
        }
        return result;
    }

    public static List<OrderCount> DuplicateSummary(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var counts = new Dictionary<string, int>(StringComparer.Ordinal);
        var order = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            if (counts.TryGetValue(value, out int count)) counts[value] = count + 1;
            else { counts.Add(value, 1); order.Add(value); }
        }
        var result = new List<OrderCount>();
        foreach (string id in order)
            if (counts[id] > 1) result.Add(new OrderCount(id, counts[id]));
        return result;
    }

    // Explicit equality-count model; do not benchmark this instrumented method.
    public static (List<string> Result, long Comparisons) CountScan(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        long comparisons = 0;
        foreach (string value in values)
        {
            RejectNull(value);
            bool found = false;
            foreach (string previous in result)
            {
                comparisons++;
                if (StringComparer.Ordinal.Equals(previous, value)) { found = true; break; }
            }
            if (!found) result.Add(value);
        }
        return (result, comparisons);
    }

    private static void RejectNull(string? value)
    {
        if (value is null) throw new ArgumentException("Order IDs must not be null.");
    }

    // Count only calls in the explicit model, not hash/equality/resize work.
    public static (List<string> Result, int AddCalls) CountHash(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        int calls = 0;
        foreach (string value in values)
        {
            RejectNull(value);
            calls++;
            if (seen.Add(value)) result.Add(value);
        }
        return (result, calls);
    }
}

public static class Dataset
{
    public static string[] Make(int n, int distinct)
    {
        if (n <= 0 || distinct <= 0 || distinct > n) throw new ArgumentOutOfRangeException();
        return Enumerable.Range(0, n).Select(i => $"ORD-{i % distinct:D8}").ToArray();
    }
}
```

`LessonLab/LessonLab.csproj`:

<!-- lab-file: LessonLab/LessonLab.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RuntimeFrameworkVersion>10.0.12</RuntimeFrameworkVersion>
    <RollForward>Disable</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup><ProjectReference Include="../Core/Core.csproj" /></ItemGroup>
</Project>
```

`LessonLab/Program.cs`:

<!-- lab-file: LessonLab/Program.cs -->
```csharp
using CostModel;

if (args.Contains("--check")) { Checks.Run(); return; }

string[] example = ["B2", "A1", "B2", "C3", "A1"];
Console.WriteLine($"Stable result: {string.Join(", ", Deduplication.Hash(example))}");
Console.WriteLine($"Example scan comparisons: {Deduplication.CountScan(example).Comparisons}");
Console.WriteLine("n,scan_equality_comparisons,hash_add_calls (not hash-table work)");
foreach (int n in new[] { 128, 256, 512 })
{
    string[] values = Dataset.Make(n, n);
    var hashed = Deduplication.CountHash(values);
    Console.WriteLine($"{n},{Deduplication.CountScan(values).Comparisons},{hashed.AddCalls}");
}
Console.WriteLine($"128 identical IDs: {Deduplication.CountScan(Dataset.Make(128, 1)).Comparisons} scan comparisons");
Console.WriteLine($"Duplicates: {string.Join(", ", Deduplication.DuplicateSummary(example).Select(x => $"{x.Id}={x.Count}"))}");
```

`LessonLab/Checks.cs`:

<!-- lab-file: LessonLab/Checks.cs -->
```csharp
using CostModel;

internal static class Checks
{
    public static void Run()
    {
        int passed = 0;
        void Check(string name, Action test) { test(); passed++; Console.WriteLine($"PASS {name}"); }
        void Equal<T>(IEnumerable<T> actual, IEnumerable<T> expected)
        { if (!actual.SequenceEqual(expected)) throw new Exception("Sequence mismatch"); }
        void Throws<T>(Action action) where T : Exception
        { try { action(); } catch (T) { return; } throw new Exception($"Expected {typeof(T).Name}"); }

        Check("stable order and unchanged input", () => {
            string[] input = ["B2", "A1", "B2", "C3", "A1"]; var before = input.ToArray();
            Equal(Deduplication.Scan(input), new[] { "B2", "A1", "C3" });
            Equal(Deduplication.Hash(input), new[] { "B2", "A1", "C3" }); Equal(input, before);
        });
        Check("empty, singleton and repeated input", () => {
            foreach (var (input, expected) in new[] {
                (Array.Empty<string>(), Array.Empty<string>()),
                (new[] { "A" }, new[] { "A" }), (new[] { "A", "A", "A" }, new[] { "A" }) })
            { Equal(Deduplication.Scan(input), expected); Equal(Deduplication.Hash(input), expected); }
        });
        Check("ordinal identity and explicit alternative comparer", () => {
            string[] input = ["a", "A", "a", " a ", ""];
            Equal(Deduplication.Scan(input), new[] { "a", "A", " a ", "" });
            Equal(Deduplication.Hash(input), new[] { "a", "A", " a ", "" });
            Equal(Deduplication.Hash(input, StringComparer.OrdinalIgnoreCase), new[] { "a", " a ", "" });
        });
        Check("null policy", () => {
            Throws<ArgumentNullException>(() => Deduplication.Scan(null!));
            Throws<ArgumentNullException>(() => Deduplication.Hash(null!));
            Throws<ArgumentException>(() => Deduplication.Scan(new[] { "A", null! }));
            Throws<ArgumentException>(() => Deduplication.Hash(new[] { "A", null! }));
            Throws<ArgumentException>(() => Deduplication.DuplicateSummary(new string[] { null! }));
        });
        Check("triangular count and repeated-ID count", () => {
            foreach (int n in new[] { 1, 128, 256, 512 }) {
                var input = Dataset.Make(n, n);
                var hashModel = Deduplication.CountHash(input);
                Equal(hashModel.Result, Deduplication.Hash(input));
                if (hashModel.AddCalls != n) throw new Exception("Wrong Add-call model");
                if (Deduplication.CountScan(Dataset.Make(n, n)).Comparisons != (long)n * (n - 1) / 2)
                    throw new Exception("Wrong distinct count model");
                if (Deduplication.CountScan(Dataset.Make(n, 1)).Comparisons != n - 1)
                    throw new Exception("Wrong repeated count model");
            }
        });
        Check("hash path avoids a membership scan on this workload", () => {
            var comparer = new CountingComparer(); var input = Dataset.Make(512, 512);
            Equal(Deduplication.Hash(input, comparer), input);
            if (comparer.Equalities >= 512) throw new Exception("Unexpected equality scan");
        });
        Check("forced collisions preserve correctness and expose quadratic work", () => {
            var comparer = new CountingComparer(constantHash: true); var input = Dataset.Make(128, 128);
            Equal(Deduplication.Hash(input, comparer), input);
            if (comparer.Equalities != 128L * 127 / 2) throw new Exception("Collision chain not exercised");
            Equal(Deduplication.Hash(new[] { "B", "A", "B" }, comparer), new[] { "B", "A" });
        });
        Check("duplicate counts and first-occurrence order", () => {
            Equal(Deduplication.DuplicateSummary(new[] { "B2", "A1", "B2", "C3", "A1" }),
                new[] { new OrderCount("B2", 2), new OrderCount("A1", 2) });
            Equal(Deduplication.DuplicateSummary(Array.Empty<string>()), Array.Empty<OrderCount>());
            Equal(Deduplication.DuplicateSummary(new[] { "A", "B" }), Array.Empty<OrderCount>());
            Equal(Deduplication.DuplicateSummary(new[] { "A", "A", "A" }), new[] { new OrderCount("A", 3) });
        });
        Console.WriteLine($"{passed} checks passed.");
    }

    private sealed class CountingComparer(bool constantHash = false) : IEqualityComparer<string>
    {
        public long Equalities { get; private set; }
        public bool Equals(string? x, string? y) { Equalities++; return StringComparer.Ordinal.Equals(x, y); }
        public int GetHashCode(string value) => constantHash ? 1 : StringComparer.Ordinal.GetHashCode(value);
    }
}
```

`Benchmarks/Benchmarks.csproj`:

<!-- lab-file: Benchmarks/Benchmarks.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RuntimeFrameworkVersion>10.0.12</RuntimeFrameworkVersion>
    <RollForward>Disable</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Core/Core.csproj" />
    <PackageReference Include="BenchmarkDotNet" Version="0.15.8" />
  </ItemGroup>
</Project>
```

`Benchmarks/Program.cs`:

<!-- lab-file: Benchmarks/Program.cs -->
```csharp
using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Running;
using CostModel;

BenchmarkSwitcher.FromAssembly(typeof(DedupeBenchmarks).Assembly).Run(args);

[MemoryDiagnoser]
public class DedupeBenchmarks
{
    [Params(128, 512, 2048)] public int N { get; set; }
    [Params(10, 100)] public int UniquePercent { get; set; }
    private string[] values = [];

    [GlobalSetup]
    public void Setup() => values = Dataset.Make(N, Math.Max(1, N * UniquePercent / 100));

    [Benchmark(Baseline = true)] public List<string> Scan() => Deduplication.Scan(values);
    [Benchmark] public List<string> Hash() => Deduplication.Hash(values);
}
```

`Benchmarks/packages.lock.json`:

<!-- lab-file: Benchmarks/packages.lock.json -->
```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {
      "BenchmarkDotNet": {
        "type": "Direct",
        "requested": "[0.15.8, )",
        "resolved": "0.15.8",
        "contentHash": "paCfrWxSeHqn3rUZc0spYXVFnHCF0nzRhG0nOLnyTjZYs8spsimBaaNmb3vwqvALKIplbYq/TF393vYiYSnh/Q==",
        "dependencies": {
          "BenchmarkDotNet.Annotations": "0.15.8",
          "CommandLineParser": "2.9.1",
          "Gee.External.Capstone": "2.3.0",
          "Iced": "1.21.0",
          "Microsoft.CodeAnalysis.CSharp": "4.14.0",
          "Microsoft.Diagnostics.Runtime": "3.1.512801",
          "Microsoft.Diagnostics.Tracing.TraceEvent": "3.1.21",
          "Microsoft.DotNet.PlatformAbstractions": "3.1.6",
          "Perfolizer": "[0.6.1]",
          "System.Management": "9.0.5"
        }
      },
      "BenchmarkDotNet.Annotations": {
        "type": "Transitive",
        "resolved": "0.15.8",
        "contentHash": "hfucY0ycAsB0SsoaZcaAp9oq5wlWBJcylvEJb9pmvdYUx6PD6S4mDiYnZWjdjAlLhIpe/xtGCwzORfzAzPqvzA=="
      },
      "CommandLineParser": {
        "type": "Transitive",
        "resolved": "2.9.1",
        "contentHash": "OE0sl1/sQ37bjVsPKKtwQlWDgqaxWgtme3xZz7JssWUzg5JpMIyHgCTY9MVMxOg48fJ1AgGT3tgdH5m/kQ5xhA=="
      },
      "Gee.External.Capstone": {
        "type": "Transitive",
        "resolved": "2.3.0",
        "contentHash": "2ap/rYmjtzCOT8hxrnEW/QeiOt+paD8iRrIcdKX0cxVwWLFa1e+JDBNeECakmccXrSFeBQuu5AV8SNkipFMMMw=="
      },
      "Iced": {
        "type": "Transitive",
        "resolved": "1.21.0",
        "contentHash": "dv5+81Q1TBQvVMSOOOmRcjJmvWcX3BZPZsIq31+RLc5cNft0IHAyNlkdb7ZarOWG913PyBoFDsDXoCIlKmLclg=="
      },
      "Microsoft.CodeAnalysis.Analyzers": {
        "type": "Transitive",
        "resolved": "3.11.0",
        "contentHash": "v/EW3UE8/lbEYHoC2Qq7AR/DnmvpgdtAMndfQNmpuIMx/Mto8L5JnuCfdBYtgvalQOtfNCnxFejxuRrryvUTsg=="
      },
      "Microsoft.CodeAnalysis.Common": {
        "type": "Transitive",
        "resolved": "4.14.0",
        "contentHash": "PC3tuwZYnC+idaPuoC/AZpEdwrtX7qFpmnrfQkgobGIWiYmGi5MCRtl5mx6QrfMGQpK78X2lfIEoZDLg/qnuHg==",
        "dependencies": {
          "Microsoft.CodeAnalysis.Analyzers": "3.11.0"
        }
      },
      "Microsoft.CodeAnalysis.CSharp": {
        "type": "Transitive",
        "resolved": "4.14.0",
        "contentHash": "568a6wcTivauIhbeWcCwfWwIn7UV7MeHEBvFB2uzGIpM2OhJ4eM/FZ8KS0yhPoNxnSpjGzz7x7CIjTxhslojQA==",
        "dependencies": {
          "Microsoft.CodeAnalysis.Analyzers": "3.11.0",
          "Microsoft.CodeAnalysis.Common": "[4.14.0]"
        }
      },
      "Microsoft.Diagnostics.NETCore.Client": {
        "type": "Transitive",
        "resolved": "0.2.510501",
        "contentHash": "juoqJYMDs+lRrrZyOkXXMImJHneCF23cuvO4waFRd2Ds7j+ZuGIPbJm0Y/zz34BdeaGiiwGWraMUlln05W1PCQ==",
        "dependencies": {
          "Microsoft.Extensions.Logging": "6.0.0"
        }
      },
      "Microsoft.Diagnostics.Runtime": {
        "type": "Transitive",
        "resolved": "3.1.512801",
        "contentHash": "0lMUDr2oxNZa28D6NH5BuSQEe5T9tZziIkvkD44YkkCGQXPJqvFjLq5ZQq1hYLl3RjQJrY+hR0jFgap+EWPDTw==",
        "dependencies": {
          "Microsoft.Diagnostics.NETCore.Client": "0.2.410101"
        }
      },
      "Microsoft.Diagnostics.Tracing.TraceEvent": {
        "type": "Transitive",
        "resolved": "3.1.21",
        "contentHash": "/OrJFKaojSR6TkUKtwh8/qA9XWNtxLrXMqvEb89dBSKCWjaGVTbKMYodIUgF5deCEtmd6GXuRerciXGl5bhZ7Q==",
        "dependencies": {
          "Microsoft.Diagnostics.NETCore.Client": "0.2.510501",
          "System.Reflection.TypeExtensions": "4.7.0"
        }
      },
      "Microsoft.DotNet.PlatformAbstractions": {
        "type": "Transitive",
        "resolved": "3.1.6",
        "contentHash": "jek4XYaQ/PGUwDKKhwR8K47Uh1189PFzMeLqO83mXrXQVIpARZCcfuDedH50YDTepBkfijCZN5U/vZi++erxtg=="
      },
      "Microsoft.Extensions.DependencyInjection": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "k6PWQMuoBDGGHOQTtyois2u4AwyVcIwL2LaSLlTZQm2CYcJ1pxbt6jfAnpWmzENA/wfrYRI/X9DTLoUkE4AsLw==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "6.0.0"
        }
      },
      "Microsoft.Extensions.DependencyInjection.Abstractions": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "xlzi2IYREJH3/m6+lUrQlujzX8wDitm4QGnUu6kUXTQAWPuZY8i+ticFJbzfqaetLA6KR/rO6Ew/HuYD+bxifg=="
      },
      "Microsoft.Extensions.Logging": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "eIbyj40QDg1NDz0HBW0S5f3wrLVnKWnDJ/JtZ+yJDFnDj90VoPuoPmFkeaXrtu+0cKm5GRAwoDf+dBWXK0TUdg==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection": "6.0.0",
          "Microsoft.Extensions.DependencyInjection.Abstractions": "6.0.0",
          "Microsoft.Extensions.Logging.Abstractions": "6.0.0",
          "Microsoft.Extensions.Options": "6.0.0"
        }
      },
      "Microsoft.Extensions.Logging.Abstractions": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "/HggWBbTwy8TgebGSX5DBZ24ndhzi93sHUBDvP1IxbZD7FDokYzdAr6+vbWGjw2XAfR2EJ1sfKUotpjHnFWPxA=="
      },
      "Microsoft.Extensions.Options": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "dzXN0+V1AyjOe2xcJ86Qbo233KHuLEY0njf/P2Kw8SfJU+d45HNS2ctJdnEnrWbM9Ye2eFgaC5Mj9otRMU6IsQ==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "6.0.0",
          "Microsoft.Extensions.Primitives": "6.0.0"
        }
      },
      "Microsoft.Extensions.Primitives": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "9+PnzmQFfEFNR9J2aDTfJGGupShHjOuGw4VUv+JB044biSHrnmCIMD+mJHmb2H7YryrfBEXDurxQ47gJZdCKNQ=="
      },
      "Perfolizer": {
        "type": "Transitive",
        "resolved": "0.6.1",
        "contentHash": "CR1QmWg4XYBd1Pb7WseP+sDmV8nGPwvmowKynExTqr3OuckIGVMhvmN4LC5PGzfXqDlR295+hz/T7syA1CxEqA==",
        "dependencies": {
          "Pragmastat": "3.2.4"
        }
      },
      "Pragmastat": {
        "type": "Transitive",
        "resolved": "3.2.4",
        "contentHash": "I5qFifWw/gaTQT52MhzjZpkm/JPlfjSeO/DTZJjO7+hTKI+0aGRgOgZ3NN6D96dDuuqbIAZSeA5RimtHjqrA2A=="
      },
      "System.CodeDom": {
        "type": "Transitive",
        "resolved": "9.0.5",
        "contentHash": "cuzLM2MWutf9ZBEMPYYfd0DXwYdvntp7VCT6a/wvbKCa2ZuvGmW74xi+YBa2mrfEieAXqM4TNKlMmSnfAfpUoQ=="
      },
      "System.Management": {
        "type": "Transitive",
        "resolved": "9.0.5",
        "contentHash": "n6o9PZm9p25+zAzC3/48K0oHnaPKTInRrxqFq1fi/5TPbMLjuoCm/h//mS3cUmSy+9AO1Z+qsC/Ilt/ZFatv5Q==",
        "dependencies": {
          "System.CodeDom": "9.0.5"
        }
      },
      "System.Reflection.TypeExtensions": {
        "type": "Transitive",
        "resolved": "4.7.0",
        "contentHash": "VybpaOQQhqE6siHppMktjfGBw1GCwvCqiufqmP8F1nj7fTUNtW35LOEt3UZTEsECfo+ELAl/9o9nJx3U91i7vA=="
      },
      "core": {
        "type": "Project"
      }
    }
  }
}
```

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

Kết quả demo dự kiến:

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

Lệnh kiểm tra báo `8 checks passed`. Các ca quét và đối chiếu kiểm tra thứ tự, so sánh ID, input rỗng, từ chối null và số phần tử trùng; chưa kiểm tra mọi comparer hay việc giao message trong production.

</details>

Các bước:

1. **Tự viết method (20 phút).** Đóng ví dụ, viết lại method và giải thích invariant ở mục 5. Có thể mở lại code mẫu khi cần.
2. **Dự đoán các trường hợp biên (15 phút).** Viết kết quả dự kiến trước khi chạy tay hoặc chạy code:

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

3. **Test và debug (15 phút).** Đối chiếu output với dự đoán và kiểm tra input không đổi. Nếu sai, thu nhỏ input gây lỗi rồi chạy tay từng bước để tìm nguyên nhân.
4. **Cố tình vi phạm một yêu cầu (10 phút).** Thêm mọi ID vào kết quả, sắp xếp kết quả hoặc dùng `OrdinalIgnoreCase`. Ba thay đổi này lần lượt giữ lại duplicate, làm sai thứ tự xuất hiện đầu và gộp `a` với `A`. Sửa để đáp ứng yêu cầu trước khi đo hiệu năng.
5. **Khảo sát collision (10 phút).** Giả sử comparer trả hash 1 cho mọi ID nhưng vẫn so sánh bằng Ordinal. Kết quả vẫn đúng, nhưng một ID mới có thể phải so với mọi entry trong bucket. Với 128 ID khác nhau, cách triển khai dùng chuỗi cần `128×127/2 = 8.128` phép so sánh. Hai khóa bằng nhau phải có cùng hash; kết quả tính hash và so sánh phải ổn định trong suốt thời gian khóa được lưu.
6. **Kết thúc (5 phút).** Giải thích một lỗi đã tránh và một giả định mà cách triển khai cần.

**Gợi ý debug:** nếu còn duplicate, kiểm tra chỉ thêm vào kết quả khi `Add` trả true. Nếu thứ tự sai, giữ một danh sách kết quả riêng. Nếu `a` và `A` bị gộp, xem lại comparer. Nếu cách dùng hash chậm bất thường, tìm lời gọi `List.Contains` trong vòng lặp. Nếu xử lý null thay đổi, kiểm tra các điều kiện báo lỗi.




**Nghỉ 10 phút.** Rời màn hình.

## 9. Thí nghiệm có kiểm soát

**Khoảng 45 phút - Đo một thay đổi:** chọn một yếu tố, nêu giả thuyết, đo rồi đối chiếu với dự đoán. **Dừng khi:** nêu được một quyết định có bằng chứng hỗ trợ và một điều chưa thể kết luận.

**So sánh công bằng.** Hai thuật toán phải dùng cùng input, cùng phép so sánh và cùng yêu cầu về thứ tự. Tạo input trước phần đo; mỗi lần gọi thuật toán phải tạo kết quả mới. Nếu chỉ một bên được tái sử dụng dữ liệu từ lần chạy trước, chi phí cấp phát và xử lý của hai bên không còn tương đương.

Lab dùng BenchmarkDotNet 0.15.8 với N = 128, 512, 2048; tỷ lệ ID khác nhau danh nghĩa là 10% và 100%. Độ dài ID cố định. Với N = 128 và tỷ lệ 10%, số ID khác nhau thực tế là `floor(128×0.10) = 12`. Giả thuyết cần kiểm tra: ít ID khác nhau làm danh sách kết quả ngắn hơn, nên tìm tuần tự tốn ít công việc hơn; hash table thường cấp phát thêm bộ nhớ. Big-O không cho biết thuật toán nào nhanh hơn bao nhiêu lần.

Chạy ở chế độ Release, không gắn debugger. Đọc ba cột `Mean`, `Error` và `Allocated` cùng nhau. `Error` là nửa độ rộng khoảng tin cậy 99,9% của BenchmarkDotNet, không phải cận sai số được bảo đảm. `Allocated` gồm bộ nhớ cấp phát cho kết quả và bảng mới, không gồm input đã tạo sẵn; nó không đo peak working set hay bộ nhớ còn sống trên heap.

Benchmark này đo thời gian xử lý một batch, không đo latency của request trong service. Nếu p99 latency là 100 ms, khoảng 99% request đã đo hoàn thành trong 100 ms; thời gian trung bình của batch không đủ để suy ra đại lượng này.

Từ thư mục `dotnet` của lab, chạy:

```bash
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

Project benchmark cần restore NuGet và chạy 12 trường hợp. Báo cáo nằm trong `BenchmarkDotNet.Artifacts/results`. Nếu phần cài đặt vượt thời gian dành cho thí nghiệm, dùng báo cáo mẫu dưới đây.

Diễn giải bản ShortRun đã ghi: khoảng ước lượng và bộ nhớ cấp phát hỗ trợ kết luận nào, còn điều gì chưa rõ?

<details>
<summary>Đáp án - benchmark đã ghi</summary>

Kết quả ShortRun ngày 05/10/2026, n = 512 và mọi ID đều khác nhau:

| Cách | Mean | Error | Allocated mỗi lần gọi |
|---|---:|---:|---:|
| Scan | 922,355 µs | 2.261,779 µs | 8.384 B |
| Hash | 22,218 µs | 19,147 µs | 42.896 B |

Môi trường đo là Debian 13, Intel Xeon Platinum 8573C và .NET 10.0.12; mỗi trường hợp có ba vòng khởi động và ba vòng đo. Khoảng tin cậy rất rộng, nên chưa đủ bằng chứng để khẳng định mức tăng tốc trong service. Số byte cấp phát cho thấy phần chi phí bộ nhớ tăng thêm, không phải bộ nhớ của cả ứng dụng. [Báo cáo đầy đủ](../../../lessons/2026-10-05-cost-model/benchmark-report.md) liệt kê toàn bộ các trường hợp đo.

</details>

### Ghi chép thí nghiệm

Chỉ thay đổi một yếu tố: n, tỷ lệ ID khác nhau, độ dài ID hoặc dung lượng ban đầu. Giữ nguyên yêu cầu về kết quả và kiểm tra tính đúng đắn trước khi đo. Không so thời gian của method có bộ đếm phép so sánh với method không có bộ đếm; việc tăng biến đếm đã thêm công việc vào một bên.

| Viết trước khi chạy | Viết sau khi chạy |
|---|---|
| Kích thước input, u thực tế, độ dài và phân bố ID | Tham số và môi trường đo |
| Giả thuyết và cơ chế giải thích | Mean, khoảng tin cậy, Allocated |
| Một yếu tố sẽ đổi | Dự đoán có đúng không |
| Kết quả đúng cần thu được | Lỗi hoặc quan sát ngoài dự đoán |
| Điều gì khiến bạn chưa thể kết luận? | Quyết định được hỗ trợ và giới hạn còn lại |

Nếu không chạy benchmark, diễn giải báo cáo mẫu và để trống phần số đo của bạn. Nếu kết quả thiếu hoặc quá nhiễu, ghi rõ chưa đủ bằng chứng để khẳng định tăng tốc. Khi tỷ lệ thời gian khác dự đoán, kiểm tra cách tạo input, comparer, chế độ build và khoảng tin cậy trước khi giải thích nguyên nhân. Chế độ Dry chỉ kiểm tra code chạy được, không cung cấp phép đo hiệu năng đáng tin cậy.

**Nghỉ 10 phút.** Rời màn hình.

## 10. Đổi yêu cầu: báo cáo duplicate

**Khoảng 35 phút - Giải bài toán đổi yêu cầu:** thiết kế lời giải, đối chiếu đáp án rồi chạy tay theo bảng. **Dừng khi:** đã chạy tay hoặc chạy code với bốn input.

Bộ phận hỗ trợ cần biết số lần mỗi ID xuất hiện, thay vì chỉ cần danh sách ID khác nhau. Với `B2,A1,B2,C3,A1`, trả về `[(B2,2),(A1,2)]` và bỏ các ID chỉ xuất hiện một lần. Vẫn dùng Ordinal, giữ thứ tự xuất hiện đầu, không sửa input và từ chối null như trước.

Hãy thiết kế method và dự đoán output cho các input sau trước khi mở đáp án. Kiểm tra thêm input rỗng và việc từ chối null.

| Input để thử | Điều cần kiểm tra |
|---|---|
| `A,B,B,A,C` | Số lần xuất hiện và thứ tự kết quả |
| `a,A,a` | Phân biệt chữ hoa và chữ thường |
| `X,Y` | ID chỉ xuất hiện một lần |
| `A,A,A` | Mỗi lần xuất hiện đều được tính |

<details>
<summary>Đáp án</summary>

Dùng dictionary để lưu số lần xuất hiện và một danh sách riêng để giữ thứ tự. Gặp ID thì tăng số đếm; chỉ thêm ID vào danh sách ở lần xuất hiện đầu.

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

Invariant gồm hai phần: `counts` lưu đúng số lần xuất hiện trong phần input đã đọc; `order` chứa mỗi ID đã gặp một lần, theo thứ tự xuất hiện đầu. Lượt duyệt cuối giữ các ID có số đếm lớn hơn một. Dưới các giả định về hash và chi phí xử lý ID đã nêu, chi phí kỳ vọng là O(n+u) = O(n), với O(u) bộ nhớ phụ. Thứ tự kết quả đến từ `order`, không dựa vào thứ tự duyệt dictionary.

| Input | Kết quả |
|---|---|
| `A,B,B,A,C` | `[(A,2),(B,2)]` |
| `a,A,a` | `[(a,2)]` |
| `[]` hoặc `X,Y` | `[]` |
| `A,A,A` | `[(A,3)]` |

Sắp xếp theo số đếm sẽ làm sai thứ tự báo cáo. Nếu chỉ tăng số đếm cho ID mới, `A,A,A` sẽ cho kết quả sai. Chạy tay với `A,B,B,A,C`: `order` là `A,B,C`; `counts` lưu A=2, B=2, C=1; lượt cuối trả A rồi B.

</details>

### Trong hệ thống thực tế: từ dedupe đến idempotency

Idempotency nghĩa là xử lý lại cùng event không tạo thêm tác động nghiệp vụ. Hai instance của service đều có thể nhận B2, vì mỗi bên có set riêng. Một `HashSet` trong batch không ngăn bên kia xử lý lại event. Cần khóa được database bảo đảm duy nhất, chẳng hạn tenant + event ID, và **ghi dấu event đã xử lý cùng cập nhật nghiệp vụ trong một transaction**. Transaction phải commit cả hai lần ghi hoặc rollback cả hai.

```sql
-- Ví dụ minh họa; chưa chạy trên SQL Server.
CREATE UNIQUE INDEX UX_OrderEvents_Tenant_Event
    ON dbo.OrderEvents (TenantId, EventId);

-- Duplicate (TenantId, EventId) sẽ lỗi 2601
-- (hoặc 2627 với unique constraint). Lỗi chỉ chứng minh key đã tồn tại.
```

Consumer bắt đầu transaction, ghi event vào `OrderEvents`, cập nhật đơn hàng rồi commit. Chỉ xác nhận đã xử lý message sau commit. Nếu lỗi trước commit, cả hai lần ghi rollback và lần thử lại có thể xử lý tiếp. Nếu đã commit nhưng chưa xác nhận message thì lần thử lại tìm thấy event đã ghi và không cập nhật nghiệp vụ lần nữa.

Khi gặp lỗi duplicate key, rollback lần thử bị lỗi và kiểm tra xung đột nằm trên **đúng khóa của event này**, không phải unique index khác. Chỉ khi việc ghi event và cập nhật nghiệp vụ nằm trong cùng transaction nguyên tử, bản ghi event mới có nghĩa là đã xử lý xong. Các lỗi database khác vẫn cần được xử lý hoặc thử lại. Nếu commit bản ghi event riêng rồi process dừng trước khi cập nhật đơn hàng, lần thử lại sẽ bỏ qua công việc chưa hoàn thành. [Mẫu Idempotent Consumer](https://learn.microsoft.com/azure/architecture/patterns/idempotent-consumer) giải thích vì sao hai lần ghi phải nằm trong cùng transaction.

`SELECT` trước rồi mới `INSERT` vẫn có race condition: hai instance có thể cùng thấy chưa có bản ghi trước khi một bên thêm vào. Phép so sánh của database cũng phải khớp với cách nghiệp vụ xác định hai ID là một; collation của SQL Server có thể so sánh string khác với Ordinal của C#.

Azure Service Bus cũng phải cân bằng khả năng phát hiện duplicate với chi phí lưu ID. [Duplicate detection](https://learn.microsoft.com/azure/service-bus-messaging/duplicate-detection) nhớ `MessageId` trong một khoảng thời gian cấu hình được và loại message gửi lặp. Tài liệu cho biết khoảng thời gian lớn hơn sẽ ảnh hưởng throughput do phải đối chiếu với các ID đã lưu, nên cần chọn khoảng nhỏ nhất vẫn đáp ứng yêu cầu. Có thể hình dung đây là set `seen` với thời hạn lưu để giới hạn bộ nhớ.

Cơ chế này ngăn gửi trùng, nhưng không thay thế xử lý idempotent ở consumer, như [mẫu Idempotent Consumer](https://learn.microsoft.com/azure/architecture/patterns/idempotent-consumer#problems-and-considerations) lưu ý. Nếu tác động nghiệp vụ nằm ngoài transaction database, một khóa duy nhất trong database chưa đủ bảo đảm tác động đó chỉ xảy ra một lần.

Trong Angular, có thể áp dụng cùng ý tưởng bằng TypeScript:

```typescript
// Set giữ thứ tự insert nên lần xuất hiện đầu thắng. String so sánh phân biệt hoa thường.
const unique = [...new Set(orderIds)];
```

## 11. Tổng hợp và xem lại

**Khoảng 45 phút - Giải thích và tự kiểm tra:** trình bày quyết định bằng lời hoặc viết ra mà không nhìn ghi chú, rồi đối chiếu. **Dừng khi:** có một câu nêu quyết định và một câu hỏi chưa giải quyết.

Đóng các ví dụ và giải thích:

1. Vì sao một `foreach` có thể là Θ(n²)?

<details>
<summary>Đáp án</summary>

Thân vòng lặp tìm trong một list ngày càng dài, nên tổng là `0+1+...+(n-1)` khi input toàn ID khác nhau.

</details>

2. Vì sao cần cả `HashSet` và `List`?

<details>
<summary>Đáp án</summary>

Kiểm tra ID đã có và giữ thứ tự kết quả là hai nhiệm vụ khác nhau. Hash table giải quyết nhiệm vụ đầu nhưng cần thêm bộ nhớ.

</details>

3. Dùng hash có luôn nhanh hơn không?

<details>
<summary>Đáp án</summary>

Không. Kết quả còn phụ thuộc kích thước batch, số ID khác nhau, chi phí tính hash và so sánh ID, cấp phát bộ nhớ và cache.

</details>

4. Dedupe `A,B,A,B` bằng cách tìm tuần tự cần bao nhiêu phép so sánh?

<details>
<summary>Đáp án</summary>

`0+1+1+2 = 4`, so với sáu khi bốn ID khác nhau.

</details>

Khi trình bày quyết định, nêu yêu cầu, đặc điểm dữ liệu, cấu trúc đã chọn, bằng chứng hỗ trợ và giới hạn. Ví dụ: "Với nhiều ID khác nhau có độ dài giới hạn, tôi chọn HashSet cùng List. Invariant chứng minh thứ tự kết quả được giữ nguyên; cách tìm tuần tự tốn số phép so sánh bậc hai. Cách dùng hash có chi phí kỳ vọng tuyến tính dưới các giả định đã nêu, nhưng cần thêm bộ nhớ. Benchmark cho thấy phần bộ nhớ tăng thêm; khoảng tin cậy của thời gian còn quá rộng để khẳng định mức tăng tốc. Cần đo phân bố ID, bộ nhớ và latency trên dữ liệu thực tế trước khi cam kết hiệu năng."

Tự kiểm tra bốn điểm: các trường hợp biên và invariant; giả định về n, u và chi phí xử lý ID; tính công bằng và giới hạn của phép đo; thứ tự kết quả trong bài đếm duplicate. Nếu lập luận chưa rõ, thử tìm một phản ví dụ nhỏ. Sau một thời gian, tính lại số phép so sánh hoặc viết lại biến thể mà không nhìn ghi chú. Nếu còn sai, ôn sớm hơn; nếu nhớ dễ, giãn khoảng ôn. Các mốc 1, 3 và 7 ngày chỉ là gợi ý để điều chỉnh.

Câu hỏi tiếp theo: ID dài làm chi phí thay đổi thế nào? Một batch có thể dùng bao nhiêu bộ nhớ? Cách so sánh của database phải đáp ứng yêu cầu định danh theo tenant ra sao? Chọn một câu để nghiên cứu tiếp.

## Đọc thêm

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) và [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0): phép so sánh, giá trị trả về và việc resize.
- [EF Core: Efficient querying](https://learn.microsoft.com/ef/core/performance/efficient-querying#tracking,-no-tracking-and-identity-resolution) và [Identity resolution](https://learn.microsoft.com/ef/core/change-tracking/identity-resolution): dictionary trong change tracker.
- [Azure Service Bus duplicate detection](https://learn.microsoft.com/azure/service-bus-messaging/duplicate-detection): lưu ID message trong một khoảng thời gian để phát hiện duplicate.
- [SQL Server unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17): ràng buộc duy nhất do database thực thi.
- [Hướng dẫn lab C#](../../../labs/cost-model/dotnet/README.vi.md): cài đặt, chạy benchmark và xử lý lỗi.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bản đồ chủ đề](../../references/topic-map.md) - Chọn phần nền tảng hoặc chủ đề muốn học sâu tiếp theo.
- [Hướng dẫn lab C#](../../../labs/cost-model/dotnet/README.vi.md) - Cài SDK, lệnh chạy và cách xử lý lỗi benchmark.

---

[Danh sách bài học](../../README.md) · [Bài sau: Bài 02 - Tìm biên bằng binary search và đếm sự kiện theo khoảng thời gian →](../boundary-search/lesson.md)
<!-- LESSON_NAVIGATION_END -->
