# Bài 02 - Tìm biên: từ mảng có thứ tự đến truy vấn khoảng thời gian

[English](../../../lessons/boundary-search/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/boundary-search/dotnet-lab.zip)

Bài 01 hỏi một ID đã xuất hiện chưa. Bây giờ dữ liệu đã sorted (sắp xếp theo key), và câu hỏi đổi khác: **điều kiện bắt đầu đúng ở vị trí nào?** Vị trí đó giúp đếm event trong một khoảng thời gian mà không phải scan (kiểm tra lần lượt) mọi event cho mỗi query. Cùng ý tưởng này nằm trong time index của Apache Kafka, nhờ đó consumer có thể nói "đọc từ 10:30 trở đi". Thuật toán đầy đủ, lập luận và đáp án có lời giải đều nằm trên trang này; ZIP lab và link standard library chỉ là phần thêm.

**Mục tiêu:** implement lower bound (vị trí đầu tiên có key ít nhất bằng target) đúng cho timestamp đã sorted, rồi dùng lại để đếm `start <= timestamp < end`, kể cả duplicate (giá trị trùng) và endpoint (điểm đầu hoặc cuối khoảng) không có trong dữ liệu. Giải thích vì sao số phép so sánh tăng theo log n, vì sao insert vào list dùng array vẫn có thể tốn công tuyến tính, và hệ thống production (Kafka) điều chỉnh boundary search cho storage của nó thế nào. Bạn cần đọc phần tử theo index, so sánh và vòng lặp. Mỗi mục cho biết bạn làm gì và trong bao lâu.

## Khái niệm cần biết (giải thích ngắn)

Đọc ý ngắn trước. Mục 3 mới đưa bản chính xác.

- **Record, key và duplicate.** Một event record (bản ghi sự kiện) có thể chứa timestamp 20 và ID B; timestamp là key dùng để tìm kiếm. Hai record có timestamp duplicate vẫn có thể là hai event khác nhau.
- **Sorted data.** Giá trị xếp theo thứ tự không giảm, như `[10, 10, 20]`. Append-only chỉ nói dữ liệu mới được ghi vào cuối; không bảo đảm timestamp sorted. Binary search cần dữ liệu sorted theo đúng key.
- **Indexed access (đọc theo vị trí).** Đọc một phần tử như `values[3]`. Array và `List<T>` hỗ trợ đọc với chi phí hằng số; riêng interface `IReadOnlyList<T>` không bảo đảm chi phí đó.
- **Binary search (tìm kiếm nhị phân).** Nhìn phần tử ở giữa. Vì dữ liệu đã sorted, một phép so sánh đó cho biết nửa nào không thể chứa đáp án. Bỏ nửa đó và lặp lại. Mỗi bước làm phần còn lại giảm khoảng một nửa.
- **Big-O và cost model (mô hình chi phí).** Big-O cho giới hạn mức tăng công việc khi input lớn lên, bỏ qua hệ số hằng. Ở đây ta đếm lần đọc phần tử và giả định mỗi lần đọc, so sánh có chi phí hằng số.
- **O(log n).** Trong mô hình đó, công việc tăng nhiều nhất theo log n. Ví dụ `log₂(8) = 3` đếm số lần chia đôi `8 -> 4 -> 2 -> 1`; `floor` làm tròn xuống số nguyên. Implementation lower bound có thể còn đọc phần tử cuối đang xét, nên đọc tối đa `floor(log₂(n)) + 1` phần tử với `n >= 1`: tối đa 4 lần cho 8 phần tử và 17 lần cho 65.536 phần tử. Gấp đôi n thêm một vào giới hạn worst case (trường hợp tệ nhất); một query cụ thể có thể đọc ít hơn.
- **Lower bound.** Vị trí đầu tiên có giá trị lớn hơn hoặc bằng `x`. Mọi thứ trước nó nhỏ hơn `x`; từ nó trở đi đều ít nhất bằng `x`. Nếu mọi giá trị đều nhỏ hơn, đáp án là độ dài `n`, nghĩa là "một vị trí sau phần tử cuối".
- **Khoảng nửa mở `[a, b)`.** Gồm `a`, không gồm `b`. `[1, 3)` là vị trí 1 và 2. Time window dùng cách này để hai window liền nhau `[10, 20)` và `[20, 30)` không đếm trùng hay sót một event.
- **Window count.** Số event trong `[start, end)` bằng `lowerBound(end) - lowerBound(start)`. Hai lần tìm thay cho một lần quét.
- **Insertion shift.** Với list dựa trên array, insert gần đầu làm mọi phần tử phía sau dịch một slot. Search nhanh; giữ dữ liệu luôn sorted khi ghi thì không miễn phí.
- **Invariant (điều luôn đúng).** Từ Bài 01: một câu luôn đúng sau mỗi bước và giúp chứng minh code đúng. Với phép tìm này, mọi phần tử trước `lo` nhỏ hơn target.
- **Index và scan.** Index lưu key kèm vị trí để query bỏ qua dữ liệu; scan kiểm tra dữ liệu theo thứ tự. Time index của Kafka là sparse index (index thưa): chỉ lưu một số entry tóm tắt, rồi scan kiểm tra record gốc.
- **Memory page (trang nhớ).** Hệ điều hành chuyển dữ liệu file theo từng block gọi là page. Hai phép tìm có thể so sánh số lần tương tự nhưng phải chờ đọc số page từ đĩa khác nhau.

## 1. Nhớ lại và kiểm tra kiến thức nền

**Block recall · khoảng 20 phút · Việc cần làm:** trả lời theo trí nhớ, rồi mở từng đáp án. Câu đầu lấy từ Bài 01. **Dừng khi:** bạn biết mình muốn đọc lại câu nào trong ba câu.

1. Vì sao một vòng lặp gọi `List.Contains` vẫn có thể mất thời gian bậc hai?

<details>
<summary>Đáp án</summary>

Khi mọi phần tử khác nhau, kết quả tăng từ 0 đến n-1 phần tử. Mỗi lần không tìm thấy phải quét toàn bộ kết quả hiện tại, nên tổng so sánh là `0+1+...+(n-1) = n(n-1)/2`. Chỉ đếm số vòng lặp sẽ bỏ sót công việc nằm trong `Contains`.

</details>

2. `[lo, hi)` chứa những vị trí nào?

<details>
<summary>Đáp án</summary>

Gồm `lo`, không gồm `hi`. `[1, 3)` chứa vị trí 1 và 2.

</details>

3. Chuyện gì xảy ra khi insert một phần tử vào đầu list dựa trên array?

<details>
<summary>Đáp án</summary>

Mọi phần tử đang có dịch sang phải một slot. Tìm kiếm nhanh không bỏ được công việc đó.

</details>

Khởi động: trong `[2, 4, 4, 9]`, vị trí đầu tiên có giá trị ít nhất 4 là đâu? Làm lại với `[1, 1, 3]` và target 1.

<details>
<summary>Đáp án</summary>

Với mảng đầu, chỉ index 0 nhỏ hơn 4, nên biên là **1**. Với mảng sau, không có gì nhỏ hơn 1, nên biên là **0**. Nếu chưa rõ, ghi mỗi giá trị phía trên index của nó và kẻ một đường giữa "nhỏ hơn target" và "ít nhất target" trước khi đọc code.

</details>

## 2. Bài toán và dự đoán

**Block foundation · khoảng 50 phút cho mục 2 đến 4 · Việc cần làm:** dự đoán từng đáp án trước khi đọc, rồi tự dựng lại trace trên giấy. **Dừng khi:** bạn nói lại được invariant của mục 3 mà không nhìn.

Một service lưu timestamp đã sorted:

```text
timestamps = [10, 10, 20, 30, 30, 40]
query       = [10, 30)
```

Dự đoán window chứa bao nhiêu event và cần tìm hai biên nào.

<details>
<summary>Đáp án</summary>

Window gồm hai event ở 10 và event ở 20, loại hai event ở 30. Đáp án là **3**. Hai biên là:

- Vị trí đầu tại hoặc sau `start` (10): 0.
- Vị trí đầu tại hoặc sau `end` (30): 3.
- Count: `3 - 0 = 3`.

</details>

Scan đếm đúng nhưng tốn O(n) phép so sánh cho mỗi query. Với nhiều query trên cùng dữ liệu sorted, hai lần boundary search giúp tránh scan lặp lại.

Một phép tìm "tìm 30" thông thường có thể trả vị trí 4, tức là số 30 thứ hai, và đếm nhầm một event ở endpoint bị loại. Bạn cần một **partition boundary** (ranh giới chia phần), không chỉ một kết quả khớp equality. Endpoint không có trong dữ liệu cũng cần đáp án hợp lý: `[11, 39)` chứa 20, 30 và 30, nên count là 3 dù 11 và 39 không xuất hiện.

## 3. Lower bound và khoảng chưa biết

Định nghĩa `lowerBound(values, x)` là index `i` đầu tiên có `values[i] >= x`, hoặc `n` nếu không có. Nó chia mảng sorted thành hai phần:

```text
values[:i]   đều < x
values[i:]   đều >= x
```

Các biểu thức này chỉ mô tả hai phần; code không tạo slice.

### Vì sao giữ khoảng chưa biết [lo, hi)?

Giữ `0 <= lo <= hi <= n` cùng các điều đã biết:

- Mọi vị trí trước `lo` đã biết chứa giá trị `< x`.
- Mọi vị trí từ `hi` trở đi đã biết chứa giá trị `>= x`.
- Chỉ `[lo, hi)` còn chưa biết. Biên có thể nằm đúng tại `hi`.

Lúc đầu `lo = 0` và `hi = n`: chưa biết gì, cả mảng là chưa biết. Lúc cuối `lo == hi`: hai vùng đã biết gặp nhau, và vị trí đó là đáp án. Trả về `n` là an toàn vì bạn trả một index, không đọc `values[n]`.

Tại điểm giữa `mid`:

- Nếu `values[mid] < x`, thứ tự sorted chứng minh mọi vị trí trước đó cũng quá nhỏ. Chuyển `lo` thành `mid + 1`.
- Ngược lại `mid` và mọi vị trí sau nó đều ít nhất bằng `x`. Chuyển `hi` thành `mid`. Giữ `mid` như một đáp án khả dĩ: giá trị bằng nhau có thể còn duplicate ở phía trước.

Mỗi nhánh loại `mid` khỏi vùng chưa biết, nên `hi - lo` giảm thật sự. Điều đó chứng minh vòng lặp dừng. Với n phần tử chưa biết, sau một vòng lặp còn tối đa `floor(n / 2)` phần tử. Vì vậy số lần đọc lớn nhất với `n >= 1` là `floor(log₂(n)) + 1`, thuộc O(log n); input rỗng không đọc phần tử nào. Giả định là indexed access và so sánh có chi phí hằng số. Linked list, key extraction (lấy key từ record) đắt hay lookup (tìm theo key) từ xa sẽ đổi chi phí thật.

### Trace có lời kể

Với `[1, 3, 3, 8]` và `x = 3`:

| lo | hi | mid | value | Quyết định và lý do |
|---|---|---|---|---|
| 0 | 4 | 2 | 3 | hi = 2: giá trị bằng nhau thuộc phần bên phải; có thể còn số 3 phía trước |
| 0 | 2 | 1 | 3 | hi = 1: giữ ứng viên phía trước |
| 0 | 1 | 0 | 1 | lo = 1: vị trí 0 quá nhỏ |
| 1 | 1 | - | - | Trả 1; hai phần gặp nhau |

Trả 2 ngay ở giá trị bằng nhau đầu tiên sẽ tìm được một kết quả khớp nhưng không phải kết quả khớp đầu tiên. Nhánh equality là thứ biến phép tìm này thành tìm biên.

Target nhỏ hơn giá trị nhỏ nhất (ví dụ 0) cứ dịch `hi` sang trái và trả 0. Target lớn hơn giá trị lớn nhất (ví dụ 10) cứ dịch `lo` sang phải và trả 4. Input rỗng bắt đầu với `lo == hi == 0` và trả 0 mà không đọc phần tử nào.

## 4. Implement bằng C#

Đây là implementation đầy đủ trong [lab C#](../../../labs/boundary-search/dotnet/README.vi.md). Nó nhận array và `List<long>` qua indexed access `IReadOnlyList<long>`.

```csharp
public static class BoundarySearch
{
    public static int LowerBound(IReadOnlyList<long> values, long target)
    {
        ArgumentNullException.ThrowIfNull(values);
        int lo = 0, hi = values.Count;
        while (lo < hi)
        {
            int mid = lo + (hi - lo) / 2;
            if (values[mid] < target)
                lo = mid + 1;
            else
                hi = mid;
        }
        return lo;
    }

    public static int CountWindow(IReadOnlyList<long> timestamps, long start, long end)
    {
        ArgumentNullException.ThrowIfNull(timestamps);
        if (end < start)
            throw new ArgumentException("end precedes start", nameof(end));
        return LowerBound(timestamps, end) - LowerBound(timestamps, start);
    }
}
```

Vì sao viết như vậy:

- Nhánh equality (`hi = mid`) giữ duplicate đầu tiên như một ứng viên.
- `lo + (hi - lo) / 2` tránh cộng hai index lớn; `(lo + hi) / 2` có thể overflow trong C#.
- Key được so sánh, không trừ nhau, nên timestamp `long` cực trị không gây overflow.
- Method không đổi input, không copy slice, không sort. Kiểm tra sorted ở mỗi query tự nó đã tốn O(n), nên hãy đảm bảo thứ tự sorted khi tạo hoặc cập nhật dữ liệu.

**Vì sao trừ hai biên thì ra count đúng.** `LowerBound(start)` là số giá trị nhỏ hơn hẳn `start`. `LowerBound(end)` là số giá trị nhỏ hơn hẳn `end`. Trừ số thứ nhất thì còn đúng những giá trị ít nhất `start` và nhỏ hơn `end`. Duplicate ở `start` được tính, duplicate ở `end` bị loại, endpoint bằng nhau cho hai biên giống nhau và count 0. Hai phép O(log n) vẫn là O(log n), với O(1) bộ nhớ phụ.

**Nghỉ 10 phút.** Rời màn hình.

## 5. Contract của library và các nguồn

**Block sources · khoảng 45 phút · Việc cần làm:** đọc hai tài liệu dưới đây, chạy đoạn snippet và trả lời ba câu hỏi, mỗi câu gồm một nhận định và bằng chứng. **Dừng khi:** mỗi đáp án có nhận định, nguồn và giới hạn.

Nguồn của block này:

- [`Array.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0) và [`List<T>.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0): yêu cầu input sorted, hành vi với duplicate và kết quả dạng complement.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): range predicate, lựa chọn index và query plan (dùng ở mục 9).

`BinarySearch` tìm **một** kết quả khớp, không nhất thiết là duplicate đầu tiên. Cả hai method đều yêu cầu dữ liệu sorted theo cùng comparer dùng để tìm. Tìm thấy thì trả một index khớp, nhưng contract **không** nói đó là cái nào trong nhiều giá trị bằng nhau. Target không có thì trả bitwise complement của vị trí insert, nên giải mã kết quả **âm** bằng `~result`.

```csharp
long[] values = [10, 10, 20, 30, 30, 40];
int match = Array.BinarySearch(values, 30L);
Console.WriteLine(values[match]);

List<long> list = [.. values];
int result = list.BinarySearch(11L);
int position = result >= 0 ? result : ~result;
Console.WriteLine($"{result}, {position}");
```

Đoạn này in `30`, rồi `-3, 2`: 11 sẽ được insert ở index 2. `-result` sẽ cho 3, sai. Target lớn hơn giá trị lớn nhất có vị trí insert là `Count`, một biên hợp lệ nhưng không phải phần tử đọc được. Với key không có, vị trí đã giải mã bằng lower bound. Với kết quả khớp thì không có lời hứa về duplicate đầu tiên, nên đừng trừ hai kết quả `BinarySearch` thành công để đếm window có duplicate ở endpoint.

Ba câu hỏi:

1. Vì sao tìm bằng equality thông thường không đủ để đếm window?

<details>
<summary>Đáp án</summary>

Với duplicate, nó có thể trả bất kỳ vị trí khớp nào, nên trừ hai kết quả có thể tính thừa hoặc thiếu event ở endpoint. Bạn cần vị trí đầu tiên tại hoặc sau mỗi endpoint, tức là một partition boundary.

</details>

2. Làm sao biến kết quả của `List<T>.BinarySearch` thành lower bound khi key không có?

<details>
<summary>Đáp án</summary>

Giải mã kết quả âm bằng `~result`. Đó là vị trí insert, và với key không có thì đúng là vị trí đầu tiên chứa giá trị lớn hơn.

</details>

3. Những giả định nào làm cho nhận định logarithmic đúng?

<details>
<summary>Đáp án</summary>

Dữ liệu sorted theo cùng thứ tự dùng trong phép so sánh, indexed access có chi phí hằng số và so sánh có chi phí hằng số. Linked list, key function đắt hay lookup từ xa sẽ phá nhận định này.

</details>

## 6. Đọc code thật: time index của Kafka

**Block implementation-reading · khoảng 45 phút · Việc cần làm:** đọc đoạn code Kafka, trace (chạy tay từng bước) ví dụ nhỏ và đối chiếu với bài học. **Dừng khi:** bạn giải thích được vì sao Kafka tìm trong phần tóm tắt sorted trước, rồi scan các record có timestamp không nhất thiết sorted.

Bài toán quen thuộc với mọi event stream: consumer hỏi "với timestamp này, tôi có thể bắt đầu đọc từ offset nào?" Project là [apache/kafka](https://github.com/apache/kafka), đọc ở commit `8ed535f41c2a8a783e64a3b4ff9468ab682959b8`.

**Bài toán của sản phẩm.** Một partition là một dãy message chỉ append, chia thành các segment file; offset là vị trí của message trong dãy đó. Scan một segment lớn từ đầu cho mỗi query sẽ tốn công, còn index mọi record sẽ tốn thêm storage. Kafka tìm message đầu tiên có `timestamp >= target` và `offset >= startingOffset`. Timestamp của record có thể đi lùi, nên áp dụng binary search của bài trực tiếp lên log là sai. Kafka tạo một phần tóm tắt sorted để tìm kiếm.

**Code làm gì** (đã xác minh trong source đã pin):

1. **Phần tóm tắt sparse và sorted.** Khi append, [`LogSegment`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java#L261) theo dõi `maxTimestampSoFar`, timestamp lớn nhất đã thấy, cùng offset cuối của batch (nhóm record) đó. Sau khi `bytesSinceLastIndexEntry > indexIntervalBytes`, nó thêm offset-index entry và gọi `timeIndex().maybeAppend` với giá trị lớn nhất này. [`TimeIndex.maybeAppend`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java#L180) chỉ ghi time entry nếu timestamp lớn hơn entry trước. Vì vậy time index sorted ngay cả khi timestamp của record gốc không sorted. Điều kiện sorted ở mục 3 được áp dụng lên phần tóm tắt, không phải log gốc.
2. **Binary search trong index.** [`TimeIndex.lookup`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java#L152) gọi `largestLowerBoundSlotFor`: entry có timestamp lớn nhất mà vẫn `<=` target. Đây là hình ảnh phản chiếu của lower bound của chúng ta.
3. **Scan để hoàn tất query.** [`LogSegment.findOffsetByTimestamp`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java#L752) dùng offset index đổi `max(indexedOffset, startingOffset)` thành vị trí file, rồi gọi [`FileRecords.searchForTimestamp`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/clients/src/main/java/org/apache/kafka/common/record/internal/FileRecords.java#L349). Method này đi qua các batch, bỏ qua batch có timestamp lớn nhất quá nhỏ, rồi kiểm tra record đến khi cả timestamp và offset thỏa query. Index giúp chọn điểm bắt đầu scan, nhưng `indexIntervalBytes` không giới hạn cứng độ dài đoạn scan: time entry có thể không tăng khi timestamp nằm dưới mức lớn nhất trước đó, và kích thước batch khác nhau. Query đầy đủ còn có bước scan này; chỉ lookup trong index có số phép so sánh logarithmic.

Hãy trace một time index nhỏ với bốn entry tóm tắt, dạng `timestamp lớn nhất đã thấy -> offset`: `1000 -> 0`, `1500 -> 40`, `2100 -> 85`, `2600 -> 130`. Consumer hỏi timestamp 2000, với `startingOffset = 0`.

<details>
<summary>Đáp án</summary>

Search của Kafka giữ một khoảng đóng `[lo, hi]` và chọn `mid = (lo + hi + 1) >>> 1`. Bắt đầu với `lo = 0, hi = 3`: mid = 2, entry 2100 lớn hơn 2000 nên `hi = 1`. Tiếp theo `lo = 0, hi = 1`: mid = 1, entry 1500 nhỏ hơn 2000 nên `lo = 1`. Giờ `lo == hi == 1`, kết quả là slot 1, entry `1500 -> 40`. Kafka sau đó tra vị trí file của offset 40 trong offset index (một lần tra sparse nữa), đọc log từ đó và trả record đầu tiên có timestamp ít nhất 2000. Nếu target nhỏ hơn entry đầu (500), search không trả slot nào và `TimeIndex.lookup` trả base offset của segment.

</details>

**Điểm khác với phép tìm của bài, và vì sao quan trọng.**

| `LowerBound` của chúng ta | `indexSlotRangeFor` của Kafka |
|---|---|
| Vị trí đầu tiên `>= x` | Slot lớn nhất `<= x`, rồi scan hoàn tất công việc |
| Nửa mở `[lo, hi)`, `mid = lo + (hi - lo) / 2` | Đóng `[lo, hi]`, `mid = (lo + hi + 1) >>> 1`, có thể trả sớm khi khớp đúng |
| Mọi timestamp sorted trong mảng | Timestamp lớn nhất đã thấy sorted trong index; timestamp của record không nhất thiết sorted |
| Chi phí tính bằng số phép so sánh | Còn tính xem mỗi phép so sánh chạm vào memory page nào |

Dòng cuối là bài học rút ra từ code. Một comment trong [`AbstractIndex.java`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L340) giải thích rằng binary search thông thường trên file memory-mapped (file được ánh xạ vào memory) chạm các page khác nhau khi file lớn lên. Page lâu không dùng có thể phải đọc lại từ đĩa ngay trên luồng xử lý thường xuyên. Tác giả báo cáo trong comment đó rằng điều này làm produce latency (thời gian hoàn thành request ghi) tăng từ vài millisecond lên khoảng một giây trong test của họ; bài này không tái hiện phép đo đó. Cách sửa trong [`indexSlotRangeFor`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L492) kiểm tra biên của vùng "warm" cuối index, với `warmEntries() = 8192 / entrySize()` (khoảng 8 KiB entry). Target lớn hơn biên đó được tìm trong vùng cuối; target khác được tìm trong vùng trước. Các page cuối được truy cập thường xuyên nên có khả năng còn trong memory cao hơn. Lookup trong index vẫn O(log n); cách truy cập page thay đổi.

**Giới hạn của ví dụ so sánh.** Với timestamp của record là `[10, 30, 20]`, window `[20, 30)` chứa một event, nhưng hai phép tìm của bài cùng trả 1 và đếm sai thành 0. Input đã vi phạm điều kiện sorted. Seek của Kafka tìm một offset bắt đầu đọc; record phía sau vẫn có thể mang timestamp nhỏ hơn. Trừ hai offset Kafka không cho count của một time window. Khi cần count đó, dùng một view riêng sorted theo timestamp hoặc scan với điều kiện window.

**Suy luận của người dạy, chưa xác minh trong code.** Nếu bạn tự viết cho service của mình (ví dụ một bảng sắp theo thời gian được load vào memory), quyết định tương đương là: khi query chủ yếu hỏi về thời gian gần đây, phần dữ liệu mà chúng chạm tới quan trọng không kém số phép so sánh. Big-O cho biết nó scale thế nào; nó không cho biết bạn đọc những page hay cache line nào.

**Áp dụng vào project của bạn.**

1. Với nhiều range query trên dữ liệu sorted theo key tìm kiếm, dùng lower bound thay vì scan toàn list mỗi query. Chỉ giải mã `BinarySearch` bằng `~result` khi key không có.
2. Với file lớn, sparse index sorted có thể giảm storage và chọn điểm bắt đầu scan. Đo cả lookup trong index và phần scan còn lại; mật độ index và thứ tự dữ liệu quyết định đánh đổi.
3. Với window count trên array sorted theo timestamp, dùng nửa mở `[start, end)` và trừ hai biên. Log không sorted cần cách khác.
4. Append chỉ giữ thứ tự sorted khi key mới ít nhất bằng key cuối. Nếu không, insert đúng vị trí và trả chi phí dịch phần tử, sort một batch, hoặc chọn ordered index phù hợp với cập nhật.

**Nghỉ 30 phút (ăn trưa).** Ăn và nghỉ.

## 7. Thực hành C# có hướng dẫn

**Block lab · khoảng 75 phút · Việc cần làm:** tự dựng lại `LowerBound` từ invariant, dự đoán edge case, chạy check, cố tình phá một nhánh rồi sửa. **Dừng khi:** các check pass và bạn giải thích được một bug đã tránh và một giả định code cần.

Chạy từ `labs/boundary-search/dotnet` với SDK 10.0.401:

```bash
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

Lần chạy mặc định cho biên dưới của 30 là 3 và count của window `[10,30)`, `[30,30)`, `[11,39)` lần lượt là 3, 0 và 3. 17 check bao gồm duplicate đầu, target không có, window rỗng, bằng nhau và bị đảo, key âm và cực trị, giữ nguyên input, encoding insert của .NET, một mảng ảo có `int.MaxValue` vị trí, và các case nhỏ đối chiếu với phép scan. Check thất bại sẽ exit khác 0. Bạn cũng có thể học mà không chạy gì: mọi bước đều trace được trên giấy.

Các bước:

1. **Tự dựng lại (20 phút).** Đóng code, viết lại `LowerBound` và nói to invariant của mục 3. Nếu bí, xem mục 4.
2. **Dự đoán edge case (15 phút).** Viết đáp án trước khi trace:

   | Mảng và lời gọi | Câu hỏi |
   |---|---|
   | `[2,4,4,9]`, target 4 | Vị trí đầu tiên? |
   | `[2,4,4,9]`, target 5 | Vị trí insert? |
   | `[2,4,4,9]`, target 0 và 10 | Hai đầu? |
   | `[]`, target 4 | Có đọc phần tử nào không? |
   | `[10,10,20,30,30,40]`, window `[20,40)` | Count? |
   | cùng mảng, window `[41,50)` | Count? |

<details>
<summary>Kết quả kỳ vọng</summary>

| Mảng và lời gọi | Kết quả |
|---|---|
| `[2,4,4,9]`, target 4 | 1 |
| `[2,4,4,9]`, target 5 | 3 |
| `[2,4,4,9]`, target 0 và 10 | 0 và 4 |
| `[]`, target 4 | 0, không đọc phần tử nào |
| `[10,10,20,30,30,40]`, window `[20,40)` | 3 (hai biên là 2 và 5) |
| cùng mảng, window `[41,50)` | 0 (hai biên là 6 và 6) |

Window bị đảo như `[30,10)` phải bị từ chối trước khi trừ.

</details>

3. **Chạy và debug (20 phút).** Chạy các check. Khi một check lỗi, trace mảng nhỏ nhất gây lỗi thay vì viết lại cả method.
4. **Cố tình phá một nhánh (15 phút).** Thử `hi = mid - 1` với `[1, 3]`, target 3, rồi thử `lo = mid` với `[1]`, target 2. Invariant hoặc lập luận về việc dừng sai ở đâu? Trace thay đổi thứ hai trên giấy để tránh chạy vòng lặp không dừng.

<details>
<summary>Đáp án</summary>

- Với `hi = mid - 1`, midpoint đầu là 1; đặt `hi = 0` làm mất đáp án đúng là 1. Invariant nửa mở cần `hi = mid`: giá trị bằng target vẫn có thể là đáp án.
- Với `lo = mid`, khi còn một phần tử và nó quá nhỏ, `mid == lo` và khoảng không co lại. Dùng `lo = mid + 1` để loại vị trí đó.

</details>

5. **Kết thúc (5 phút).** Giải thích một bug đã tránh và một giả định code cần.

**Gợi ý debug:** sai duplicate đầu -> xem nhánh equality; lỗi với input rỗng -> chỉ đọc phần tử bên trong vòng lặp không rỗng; target lớn hơn max bị lỗi -> cho phép đáp án `n`.

**Nghỉ 10 phút.** Rời màn hình.

## 8. Quan sát chi phí

**Block experiment · khoảng 45 phút · Việc cần làm:** dự đoán số lần đọc phần tử, chạy quan sát, rồi so sánh. **Dừng khi:** bạn có một câu về cách số lần đọc tăng và một điều mà phép đếm này không cho biết.

Dãy này tính giá trị tại mỗi lần indexed read và đếm số lần đọc, nên cho thấy cách chi phí scale mà không cần cấp phát một mảng lớn. Nó nằm trong lab ở `LessonLab/Extras.cs`:

```csharp
public sealed class CountedSequence(int n) : IReadOnlyList<long>
{
    public int Reads { get; private set; }
    public int Count => n;

    public long this[int index]
    {
        get
        {
            if ((uint)index >= (uint)n) throw new ArgumentOutOfRangeException(nameof(index));
            Reads++;
            return index * 2L;
        }
    }

    public IEnumerator<long> GetEnumerator() => throw new NotSupportedException();
    System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator() => GetEnumerator();
}
```

Dự đoán số lần đọc cho n = 8, 1.024 và 65.536 với `BoundarySearch.LowerBound(new CountedSequence(n), n)`, rồi chạy:

```bash
dotnet run -c Release --project LessonLab -- --observe
```

Làm lại với target nhỏ hơn mọi key và target lớn hơn mọi key. Số lần đọc thay đổi thế nào, và phép đếm này không đo được gì?

<details>
<summary>Đáp án và output quan sát được</summary>

Output quan sát được với .NET SDK 10.0.401 của lab (dạng mỗi dòng là `n index reads`):

```text
8 4 3
1024 512 10
65536 32768 16
records: 1 3 2
```

Target nằm gần giữa các dãy tổng hợp này. Tăng n từ 1.024 lên 65.536 làm kích thước gấp 64 lần nhưng chỉ thêm sáu lần đọc. Giới hạn worst case chính xác là `floor(log₂(n)) + 1`, tức 17 với n = 65.536. Với n đó, target -1 cần 17 lần đọc; target n và `2L * n` cần 16. Target khác có thể có số lần đọc khác nhưng vẫn nằm trong giới hạn. Check logarithmic của lab dùng target giữa dãy; nó không thử mọi input lớn. Đây là đếm số lần đọc phần tử, không phải lệnh CPU, thời gian thật hay số page database đọc; câu chuyện page cache của Kafka ở mục 6 đúng là loại chi phí mà phép đếm này không thấy.

</details>

Giờ đếm phía bên kia. Insert gần đầu một list dựa trên array có n phần tử dịch khoảng n phần tử, nên `List<long>` sorted nhận insert ngẫu nhiên tốn O(n) cho mỗi lần ghi dù mỗi lần tìm là O(log n). Sort một batch chưa sorted một lần tốn O(n log n) theo mô hình so sánh thông thường; bước chuẩn bị đó tách biệt với chi phí của từng query về sau.

| Viết trước khi chạy | Viết sau khi chạy |
|---|---|
| Số lần đọc dự đoán cho từng n | Số lần đọc quan sát được |
| Target nào cho nhiều lần đọc nhất? | Điều bạn thấy với target nhỏ hơn, nằm trong và lớn hơn dãy |
| Phép đếm này không đo được gì | Một câu về giới hạn |

**Nghỉ 10 phút.** Rời màn hình.

## 9. Transfer: event record, rồi SQL Server

**Block transfer · khoảng 35 phút · Việc cần làm:** đổi cách biểu diễn, dự đoán kết quả window, rồi đọc phần SQL. **Dừng khi:** bạn đã chạy đáp án của mình với hai check bên dưới.

### Record có key là timestamp

Event thật mang nhiều thứ hơn một timestamp:

```csharp
public sealed record Event(long Timestamp, string Id);
```

Đổi `LowerBound` để nhận `IReadOnlyList<T> items`, `long target` và `Func<T, long> key`. List sorted theo key mà function trả về. Thử với `[(10,A), (20,B), (20,C), (30,D)]`: tìm hai biên của `[20, 30)` và count của window đó. Kiểm tra thêm target 31, lớn hơn key cuối.

<details>
<summary>Đáp án</summary>

Key function chạy trên record trong mảng, không chạy trên target. Giữ invariant cũ, thay `items[mid]` bằng `key(items[mid])` trong phép so sánh:

```csharp
public static class RecordSearch
{
    public static int LowerBound<T>(IReadOnlyList<T> items, long target, Func<T, long> key)
    {
        ArgumentNullException.ThrowIfNull(items);
        ArgumentNullException.ThrowIfNull(key);
        int lo = 0, hi = items.Count;
        while (lo < hi)
        {
            int mid = lo + (hi - lo) / 2;
            if (key(items[mid]) < target)
                lo = mid + 1;
            else
                hi = mid;
        }
        return lo;
    }
}
```

`LowerBound(events, 20, e => e.Timestamp)` là 1 và `LowerBound(events, 30, e => e.Timestamp)` là 3, nên count là `3 - 1 = 2` (B và C). Target 31 trả 4, một vị trí sau phần tử cuối. Target là một giá trị key (20), không phải cả event. List phải sorted theo đúng key đó. `--observe` của lab in `records: 1 3 2`, và `--check` kiểm tra các biên record này.

</details>

Dùng một đơn vị và một cách hiểu timezone. Trộn giây và millisecond có thể làm hỏng query mà không báo lỗi. Key function chạy trên từng record được kiểm tra; key đắt có thể đáng để tính trước, đổi lại tốn storage và phải đồng bộ khi cập nhật. Với dữ liệu ghi thường xuyên, list sorted phẳng có thể không hợp; ordered index hoặc tree có chi phí query, cập nhật và storage riêng.

### SQL Server: time window trên một index

Cùng contract đó là `ts >= @s AND ts < @e` trong T-SQL. Trong một scratch database, ví dụ này giữ timestamp duplicate như các event riêng:

```sql
CREATE TABLE dbo.Events
(
    event_id bigint IDENTITY(1, 1) NOT NULL PRIMARY KEY,
    ts datetime2(7) NOT NULL
);
CREATE INDEX IX_Events_ts ON dbo.Events(ts);

INSERT dbo.Events(ts) VALUES
('2026-10-06T10:00:00'),
('2026-10-06T10:00:00'),
('2026-10-06T10:10:00'),
('2026-10-06T10:30:00'),
('2026-10-06T10:30:00'),
('2026-10-06T10:40:00');

DECLARE @s datetime2(7) = '2026-10-06T10:00:00';
DECLARE @e datetime2(7) = '2026-10-06T10:30:00';
IF @e < @s THROW 50001, 'end precedes start', 1;

SELECT COUNT_BIG(*) AS event_count
FROM dbo.Events
WHERE ts >= @s AND ts < @e;
```

Dự đoán count, rồi thử bounds bằng nhau. Thay điều kiện bằng `BETWEEN @s AND @e` sẽ đổi kết quả thế nào?

<details>
<summary>Đáp án</summary>

Count kỳ vọng là **3**: hai row ở thời điểm đầu và row 10:10 được tính; hai row ở thời điểm cuối bị loại. Bounds bằng nhau trả 0. `BETWEEN @s AND @e` sẽ tính cả điểm cuối, cho count 5 và đổi contract. Đừng đặt `ts` là unique trừ khi domain cấm event đồng thời: timestamp và identity của event trả lời hai câu hỏi khác nhau.

</details>

Ví dụ SQL này cần SQL Server và không được chạy bởi lab C#; kết quả là dự đoán từ các row và điều kiện, không phải phép đo database.

Predicate (điều kiện lọc) này là **sargable**: cột có index được so sánh trực tiếp với parameter cùng kiểu tương thích, nên SQL Server có thể dùng index để seek (định vị trong index) tới khoảng đó. Điều kiện như `DATEPART(year, ts) = @year` tính giá trị từ cột thay vì đưa một khoảng trực tiếp để seek; hãy dùng `ts >= @yearStart AND ts < @nextYearStart`. Sargable cho phép seek nhưng không hứa sẽ seek: selectivity (tỷ lệ row thỏa điều kiện), statistics (thống kê phân bố dữ liệu), kích thước bảng và optimizer quyết định plan, nên hãy xem actual execution plan và dùng `SET STATISTICS IO ON`.

Hai lower bound trên một array cho count bằng cách trừ index. Một index SQL Server thông thường không biến `COUNT_BIG` thành thao tác O(log n): tìm khoảng thì rẻ, nhưng đếm vẫn có thể phải đi qua mọi index entry thỏa điều kiện. Định vị một khoảng và đếm khoảng đó có chi phí riêng. `datetime2` không có timezone, nên dùng một quy ước (ví dụ UTC) cho cả giá trị lưu và bound, và khớp độ chính xác thay vì cộng một "epsilon" vào endpoint bao gồm.

## 10. Tổng hợp và xem lại

**Block synthesis · khoảng 45 phút · Việc cần làm:** giải thích phép tìm không cần ghi chú, tự kiểm tra theo bảng, rồi trả lời case mới. **Dừng khi:** bạn có một câu quyết định và một câu hỏi còn mở.

Giải thích bằng lời của bạn vì sao equality làm `hi` dịch, vì sao trả `n` là hợp lệ, và vì sao một midpoint khớp bất kỳ là chưa đủ. Nếu một case lỗi, giữ ví dụ nhỏ nhất, sửa quy tắc và thử một ví dụ mới. Cách này hiệu quả hơn học thuộc hai dòng cập nhật.

| Mục kiểm | Lời giải thích tốt gồm | Nếu chưa rõ, thử |
|---|---|---|
| Partition đúng | Cả hai bất đẳng thức; case rỗng, duplicate, thiếu và ngoài khoảng | Vẽ giá trị có đánh số và hai phần |
| Dừng và chi phí | Mỗi nhánh làm `hi - lo` giảm; so sánh logarithmic khi truy cập ngẫu nhiên | Trace một khoảng chưa biết có một phần tử |
| Hành vi window | Hai biên; bao gồm start, loại end | Duplicate ở cả hai endpoint |
| Đánh đổi | Query nhanh không loại được insertion shift, chi phí key hay chi phí truy cập page | Đếm số lần dịch khi insert đầu |

Case mới để trả lời không ghi chú: `[5, 5, 5, 7, 9]`, window `[5, 9)`.

<details>
<summary>Đáp án</summary>

`LowerBound(5) = 0` và `LowerBound(9) = 4`, nên count là 4: cả ba số 5 và số 7. Số 9 ở cuối bị loại. So với tìm equality thông thường cho 5, có thể trả vị trí 1 và làm phép trừ sai.

</details>

Bài luyện tùy chọn: tìm biên cho `[1,1,3]`, target 1, rồi `[2,4,4,9]`, target 5. Với `[10,10,20,30,30,40]`, đếm `[20,40)` và `[41,50)`. Giải thích cách xử lý endpoint đảo `[30,10)` và dữ liệu nào phải giữ sorted khi tìm record theo key.

<details>
<summary>Đáp án cho danh sách luyện</summary>

- `[1,1,3]`, target 1: biên 0; không phần tử nào thuộc phần nhỏ hơn.
- `[2,4,4,9]`, target 5: biên 3; cả ba phần tử trước đó đều nhỏ hơn.
- `[10,10,20,30,30,40]`, window `[20,40)`: count 3, từ hai biên 2 và 5.
- Cùng mảng, window `[41,50)`: count 0, từ hai biên 6 và 6.
- Endpoint bị đảo: từ chối query trước khi trừ hai biên.
- Tìm theo record: target là một giá trị key; giữ cùng thứ tự khi cập nhật list.

</details>

Sau một khoảng thời gian, tự dựng lại phép tìm và trace một target duplicate mới mà không ghi chú; rồi đổi cách biểu diễn record hoặc endpoint và giải thích kết quả window. Sau một lỗi thì ôn sớm hơn, và giãn dài hơn khi lập luận đã chắc.

Câu hỏi để mang theo: vì sao biên trái và biên phải khác nhau khi gặp equality? Key function thêm công việc gì? Vì sao insert vào list sorted vẫn tuyến tính dù có binary search? Sau lookup trong index của Kafka còn công việc gì?

<details>
<summary>Đáp án</summary>

Biên trái giữ giá trị bằng target ở phần bên phải (`hi = mid`); biên phải đưa chúng vào phần bên trái (`lo = mid + 1` khi bằng nhau) để tìm giá trị đầu tiên lớn hơn target. Key function chạy trên mỗi record được kiểm tra, nên chi phí đó cộng vào mỗi lần so sánh. Tìm vị trí insert có số bước logarithmic nhưng dịch các phần tử phía sau vẫn tuyến tính. Kafka còn phải đổi offset thành vị trí file, scan batch và record, và có thể chờ đọc page từ đĩa. Chỉ đếm phép so sánh của sparse index không mô tả chi phí toàn query.

</details>

## Đọc thêm

- [Time index của Apache Kafka](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L340): comment về vùng warm và `indexSlotRangeFor`, đã pin theo commit đọc ở mục 6.
- [List<T>.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0) và [Array.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0): contract khi gặp duplicate và vị trí insert dạng complement.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): range predicate, lựa chọn index và query plan.
- [Hướng dẫn lab C#](../../../labs/boundary-search/dotnet/README.vi.md): setup, lệnh chạy và các check.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 01 - Big-O và cấu trúc dữ liệu: loại bỏ duplicate mã đơn hàng bằng C#](../2026-10-05-cost-model/lesson.md) - Ôn cách công việc bên trong vòng lặp quyết định chi phí.
- [Ghi chú theo chủ đề kỹ thuật](../../references/topic-notes.md) - Khám phá chỉ mục có thứ tự, xử lý truy vấn và thiết kế thuật toán.

---

[← Bài trước: Bài 01 - Big-O và cấu trúc dữ liệu: loại bỏ duplicate mã đơn hàng bằng C#](../2026-10-05-cost-model/lesson.md) · [Danh sách bài học](../../README.md)
<!-- LESSON_NAVIGATION_END -->
