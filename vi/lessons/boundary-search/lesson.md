# Bài 02 - Tìm biên bằng binary search và đếm sự kiện theo khoảng thời gian

[English](../../../lessons/boundary-search/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/boundary-search/dotnet-lab.zip)

Bài 01 xét xem một ID đã xuất hiện hay chưa. Với dữ liệu đã sắp xếp, ta có thể hỏi thêm: **vị trí đầu tiên thỏa một điều kiện nằm ở đâu?** Tìm hai vị trí như vậy giúp đếm sự kiện trong một khoảng thời gian mà không phải duyệt toàn bộ dữ liệu cho mỗi truy vấn. Time index của Apache Kafka cũng dùng binary search, nhưng tìm trên một chỉ mục tóm tắt rồi mới đọc các record gốc.

**Mục tiêu:** viết hàm lower bound cho mảng timestamp đã sắp xếp và dùng nó để đếm `start <= timestamp < end`. Hàm phải xử lý đúng duplicate, khoảng rỗng và giá trị đầu hoặc cuối khoảng không xuất hiện trong dữ liệu. Sau đó, phân tích chi phí tìm kiếm, chi phí chèn phần tử và cách Kafka kết hợp chỉ mục với bước scan. Kiến thức cần có: đọc phần tử theo index, phép so sánh và vòng lặp.

## Khái niệm chính

- **Binary search.** Với mảng đã sắp xếp, so sánh phần tử giữa với giá trị cần tìm để loại bỏ khoảng một nửa vùng đang xét. Lặp lại bước này cho đến khi xác định được kết quả.
- **Biên trái (lower bound).** Vị trí đầu tiên có giá trị lớn hơn hoặc bằng `x`; nếu không có, trả độ dài mảng. Ví dụ, với `[2, 4, 4, 9]` và `x = 4`, biên trái là vị trí 1.
- **Khoảng nửa mở `[a, b)`.** Bao gồm `a`, không bao gồm `b`. Hai khoảng thời gian liền nhau `[10, 20)` và `[20, 30)` sẽ tính sự kiện tại thời điểm 20 đúng một lần.
- **Bất biến vòng lặp (invariant).** Một mệnh đề đúng trước vòng lặp và được bảo toàn sau mỗi bước. Trong thuật toán này, mọi phần tử trước `lo` đều nhỏ hơn giá trị cần tìm; bất biến giúp chứng minh vị trí trả về là đúng.
- **Mô hình chi phí và O(log n).** Ta đếm số lần đọc phần tử, giả định mỗi lần đọc và so sánh có chi phí O(1). Vì vùng tìm kiếm giảm khoảng một nửa mỗi bước, số lần đọc có cận trên O(log n), thay vì tăng tuyến tính theo n; Big-O mô tả cận trên tiệm cận, không phải số lần đọc chính xác của từng truy vấn.

## 1. Ôn lại và kiểm tra kiến thức nền

**Ôn lại · khoảng 20 phút.** Trả lời theo trí nhớ, rồi mở đáp án để đối chiếu. Câu đầu lấy từ Bài 01. **Hoàn thành khi:** xác định được câu nào cần đọc lại.

1. Vì sao một vòng lặp gọi `List.Contains` vẫn có thể mất thời gian bậc hai?

<details>
<summary>Đáp án</summary>

Khi mọi phần tử đều khác nhau, list kết quả tăng từ 0 đến n-1 phần tử. Mỗi lần không tìm thấy, `Contains` phải duyệt hết list hiện tại. Tổng số phép so sánh là `0+1+...+(n-1) = n(n-1)/2`. Chỉ đếm vòng lặp sẽ bỏ sót công việc bên trong `Contains`.

</details>

2. `[lo, hi)` chứa những vị trí nào?

<details>
<summary>Đáp án</summary>

Bao gồm `lo`, không bao gồm `hi`. Ví dụ, `[1, 3)` chứa vị trí 1 và 2.

</details>

3. Chèn một phần tử vào đầu `List<T>` dùng mảng bên dưới sẽ làm gì với các phần tử hiện có?

<details>
<summary>Đáp án</summary>

Mọi phần tử hiện có phải dịch sang phải một vị trí. Tìm được vị trí chèn nhanh không loại bỏ chi phí dịch chuyển này.

</details>

Khởi động: trong `[2, 4, 4, 9]`, vị trí đầu tiên có giá trị lớn hơn hoặc bằng 4 là đâu? Làm lại với `[1, 1, 3]` và giá trị cần tìm là 1.

<details>
<summary>Đáp án</summary>

Với mảng đầu, chỉ vị trí 0 có giá trị nhỏ hơn 4, nên biên là **1**. Với mảng sau, không có giá trị nào nhỏ hơn 1, nên biên là **0**. Nếu chưa rõ, ghi index dưới từng phần tử và vẽ ranh giới giữa hai phần: nhỏ hơn giá trị cần tìm, và lớn hơn hoặc bằng giá trị đó.

</details>

## 2. Bài toán và dự đoán

**Lý thuyết · khoảng 50 phút cho mục 2-4.** Dự đoán kết quả, chạy từng bước trên giấy, rồi viết lại bất biến. **Hoàn thành khi:** giải thích được bất biến ở mục 3 mà không nhìn tài liệu.

Một dịch vụ lưu các timestamp theo thứ tự không giảm:

```text
timestamps = [10, 10, 20, 30, 30, 40]
query       = [10, 30)
```

Dự đoán số sự kiện trong khoảng trên và hai biên cần tìm.

<details>
<summary>Đáp án</summary>

Khoảng này tính hai sự kiện tại thời điểm 10 và một sự kiện tại thời điểm 20, nhưng loại cả hai sự kiện tại thời điểm 30. Kết quả là **3**. Hai biên là:

- Vị trí đầu tiên có timestamp `>= start` (10): 0.
- Vị trí đầu tiên có timestamp `>= end` (30): 3.
- Số sự kiện: `3 - 0 = 3`.

</details>

Duyệt toàn bộ mảng cũng đếm đúng, nhưng tốn O(n) phép so sánh mỗi truy vấn. Khi cần nhiều truy vấn trên cùng dữ liệu đã sắp xếp, tìm hai biên sẽ tránh lặp lại bước duyệt này.

Nếu chỉ tìm một phần tử bằng 30, thuật toán có thể trả vị trí 4, tức số 30 thứ hai. Dùng vị trí đó làm biên cuối sẽ tính thừa một sự kiện đáng lẽ phải loại. Ta cần **ranh giới giữa hai phần của mảng**, không chỉ một phần tử khớp. Giá trị biên không có trong mảng cũng phải xử lý được: `[11, 39)` chứa 20, 30 và 30, nên kết quả vẫn là 3.

## 3. Lower bound và khoảng chưa xác định

Định nghĩa `lowerBound(values, x)` là index `i` đầu tiên có `values[i] >= x`, hoặc `n` nếu không có. Nó chia mảng đã sắp xếp thành hai phần:

```text
values[:i]   đều < x
values[i:]   đều >= x
```

Ký hiệu trên chỉ mô tả hai phần; thuật toán không tạo bản sao hay cắt mảng.

### Vì sao giữ khoảng chưa xác định [lo, hi)?

Duy trì `0 <= lo <= hi <= n` và bất biến sau:

- Mọi vị trí trước `lo` có giá trị `< x`.
- Mọi vị trí từ `hi` trở đi có giá trị `>= x`.
- Chỉ các vị trí trong `[lo, hi)` chưa được phân loại. Biên cần tìm có thể nằm đúng tại `hi`.

Ban đầu, `lo = 0` và `hi = n`: toàn bộ mảng chưa được phân loại. Khi `lo == hi`, hai phần đã xác định gặp nhau; vị trí đó chính là biên cần tìm. Trả `n` hợp lệ vì hàm trả một vị trí, không đọc `values[n]`.

Xét phần tử giữa tại `mid`:

- Nếu `values[mid] < x`, thứ tự của mảng cho biết mọi phần tử trước nó cũng nhỏ hơn `x`. Đặt `lo = mid + 1`.
- Ngược lại, `values[mid] >= x`, nên mọi phần tử sau nó cũng ít nhất bằng `x`. Đặt `hi = mid`. Không loại `mid` khỏi tập vị trí có thể là đáp án, vì đây có thể là phần tử đầu tiên bằng `x`.

Mỗi nhánh loại `mid` khỏi vùng chưa xác định, nên `hi - lo` giảm nghiêm ngặt. Đây là cơ sở chứng minh thuật toán dừng. Nếu vùng đó có n phần tử, sau một vòng lặp còn tối đa `floor(n / 2)` phần tử. Với `n >= 1`, số lần đọc lớn nhất là `floor(log₂(n)) + 1`, thuộc O(log n); mảng rỗng không đọc phần tử nào.

Ở đây, `log₂(8) = 3` tương ứng với ba lần chia đôi `8 -> 4 -> 2 -> 1`; `floor` làm tròn xuống số nguyên. Thuật toán có thể cần đọc thêm phần tử cuối còn lại, nên cận trên là 4 lần đọc với 8 phần tử và 17 lần với 65.536 phần tử. Gấp đôi n tăng cận trên này thêm một; từng truy vấn có thể đọc ít hơn.

Mô hình trên giả định truy cập `values[i]` và phép so sánh đều có chi phí O(1). Array và `List<T>` đáp ứng giả định truy cập này, nhưng interface `IReadOnlyList<T>` không tự bảo đảm chi phí đó. Linked list, hàm lấy key tốn nhiều công hoặc truy cập dữ liệu từ xa sẽ làm thay đổi phân tích chi phí.

### Chạy từng bước trên ví dụ

Với `[1, 3, 3, 8]` và `x = 3`:

| lo | hi | mid | Giá trị | Quyết định và lý do |
|---|---|---|---|---|
| 0 | 4 | 2 | 3 | hi = 2: giá trị bằng x thuộc phần bên phải; có thể còn số 3 trước đó |
| 0 | 2 | 1 | 3 | hi = 1: giữ vị trí khớp sớm hơn |
| 0 | 1 | 0 | 1 | lo = 1: vị trí 0 có giá trị nhỏ hơn x |
| 1 | 1 | - | - | Trả 1; hai phần gặp nhau |

Trả 2 ngay ở lần đầu gặp giá trị bằng `x` chỉ tìm được một phần tử khớp. Nhánh `hi = mid` khi bằng nhau giúp tiếp tục tìm về bên trái, nên mới trả đúng biên đầu tiên.

Với giá trị cần tìm nhỏ hơn phần tử nhỏ nhất, chẳng hạn 0, `hi` liên tục dịch trái và kết quả là 0. Với giá trị lớn hơn phần tử lớn nhất, chẳng hạn 10, `lo` dịch phải và kết quả là 4. Mảng rỗng bắt đầu với `lo == hi == 0`, nên trả 0 mà không đọc phần tử nào.

## 4. Cài đặt bằng C#

Đây là mã nguồn trong [lab C#](../../../labs/boundary-search/dotnet/README.vi.md). Hàm nhận array hoặc `List<long>` qua `IReadOnlyList<long>` và truy cập phần tử bằng index.

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

Các quyết định trong cách cài đặt:

- Khi bằng nhau, `hi = mid` giữ lại vị trí có thể là duplicate đầu tiên.
- `lo + (hi - lo) / 2` tránh cộng hai index lớn. Công thức `(lo + hi) / 2` có thể tràn số nguyên trong C#.
- So sánh trực tiếp hai key, thay vì trừ chúng, tránh tràn số với các giá trị `long` cực trị.
- Hàm không thay đổi, sao chép hay sắp xếp dữ liệu. Kiểm tra thứ tự ở mỗi truy vấn cũng tốn O(n), nên phải bảo đảm dữ liệu đã sắp xếp khi tạo hoặc cập nhật nó.

**Vì sao hiệu hai biên cho số lượng đúng?** `LowerBound(start)` bằng số phần tử có giá trị `< start`; `LowerBound(end)` bằng số phần tử có giá trị `< end`. Lấy hiệu loại đúng các phần tử trước `start`, chỉ giữ lại `start <= timestamp < end`. Duplicate tại `start` được tính, duplicate tại `end` bị loại. Nếu hai giá trị biên bằng nhau, hai vị trí cũng bằng nhau và kết quả là 0. Hai lần tìm O(log n) vẫn có tổng chi phí O(log n), với O(1) bộ nhớ phụ.

**Nghỉ 10 phút.** Rời màn hình.

## 5. Đối chiếu với API của .NET

**Đọc tài liệu · khoảng 45 phút.** Đối chiếu hai API tìm kiếm, chạy ví dụ và trả lời ba câu hỏi dưới đây. **Hoàn thành khi:** mỗi câu trả lời có nhận định, nguồn hỗ trợ và giới hạn của nhận định.

Tài liệu cần đọc:

- [`Array.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0) và [`List<T>.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0): điều kiện dữ liệu đã sắp xếp, cách xử lý duplicate và quy tắc trả về khi không tìm thấy.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): điều kiện lọc theo khoảng, lựa chọn index và execution plan; áp dụng ở mục 9.

`BinarySearch` trả **một** vị trí khớp, không bảo đảm đó là duplicate đầu tiên. Cả hai API yêu cầu dữ liệu đã sắp xếp theo đúng comparer dùng khi tìm kiếm. Nếu không tìm thấy, kết quả là bitwise complement của vị trí chèn. Vì vậy, chỉ giải mã kết quả **âm** bằng `~result`.

```csharp
long[] values = [10, 10, 20, 30, 30, 40];
int match = Array.BinarySearch(values, 30L);
Console.WriteLine(values[match]);

List<long> list = [.. values];
int result = list.BinarySearch(11L);
int position = result >= 0 ? result : ~result;
Console.WriteLine($"{result}, {position}");
```

Ví dụ in `30`, rồi `-3, 2`: giá trị 11 sẽ được chèn tại index 2. Dùng `-result` sẽ cho 3 và sai vị trí. Nếu giá trị cần tìm lớn hơn mọi phần tử, vị trí chèn là `Count`; đây là biên hợp lệ nhưng không phải index có thể dùng để đọc phần tử.

Khi key không tồn tại, vị trí giải mã cũng là lower bound. Khi tìm thấy, API không bảo đảm vị trí đầu tiên trong các giá trị bằng nhau. Vì vậy, không được lấy hiệu hai kết quả `BinarySearch` đã tìm thấy để đếm một khoảng có duplicate tại biên.

Ba câu hỏi:

1. Vì sao tìm một phần tử bằng giá trị cần tìm chưa đủ để đếm theo khoảng?

<details>
<summary>Đáp án</summary>

Khi có duplicate, phép tìm có thể trả bất kỳ vị trí khớp nào. Lấy hiệu hai vị trí đó có thể tính thừa hoặc thiếu sự kiện tại biên. Ta cần vị trí đầu tiên có giá trị lớn hơn hoặc bằng từng giá trị biên.

</details>

2. Giải mã kết quả của `List<T>.BinarySearch` thành lower bound thế nào khi key không tồn tại?

<details>
<summary>Đáp án</summary>

Kết quả âm được giải mã bằng `~result`. Đây là vị trí chèn, cũng là vị trí đầu tiên có giá trị lớn hơn key không tồn tại đó.

</details>

3. Phân tích O(log n) phụ thuộc vào những giả định nào?

<details>
<summary>Đáp án</summary>

Dữ liệu đã sắp xếp theo đúng thứ tự dùng khi so sánh; truy cập theo index và so sánh đều có chi phí O(1). Linked list, hàm lấy key tốn nhiều công hoặc truy cập từ xa không còn đáp ứng mô hình chi phí này.

</details>

## 6. Nghiên cứu mã nguồn: time index của Kafka

**Đọc mã nguồn · khoảng 45 phút.** Theo dõi các hàm Kafka được dẫn dưới đây, chạy ví dụ nhỏ và đối chiếu với thuật toán của bài. **Hoàn thành khi:** giải thích được vì sao Kafka tìm trên chỉ mục đã sắp xếp, rồi scan các record có timestamp không nhất thiết theo thứ tự.

Trong một hệ thống streaming, consumer có thể hỏi: "Với timestamp này, tôi nên bắt đầu đọc từ offset nào?" Xét cách [apache/kafka](https://github.com/apache/kafka) giải quyết yêu cầu đó ở commit `8ed535f41c2a8a783e64a3b4ff9468ab682959b8`.

**Bài toán thực tế.** Mỗi partition là một dãy message chỉ ghi thêm vào cuối, được chia thành các segment file. Offset đánh dấu vị trí logic của message, không phải vị trí byte trong file. Scan một segment lớn từ đầu cho mỗi truy vấn sẽ tốn công; lập chỉ mục cho mọi record lại tốn thêm dung lượng. Kafka cần tìm message đầu tiên có `timestamp >= target` và `offset >= startingOffset`. Timestamp có thể giảm giữa các record, nên không thể áp dụng binary search trực tiếp lên log. Thay vào đó, Kafka xây dựng một chỉ mục tóm tắt có thứ tự.

Ba bước trong mã nguồn:

1. **Duy trì chỉ mục thưa, có thứ tự.** Khi ghi thêm dữ liệu, [`LogSegment`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java#L261) theo dõi `maxTimestampSoFar`, tức timestamp lớn nhất đã gặp, cùng offset cuối của batch chứa giá trị đó. Khi `bytesSinceLastIndexEntry > indexIntervalBytes`, nó thêm entry vào offset index và gọi `timeIndex().maybeAppend` với giá trị lớn nhất đã gặp. [`TimeIndex.maybeAppend`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java#L180) chỉ ghi entry mới nếu timestamp lớn hơn entry trước. Vì vậy, các timestamp trong time index tăng dần dù timestamp của record gốc có thể không tăng. Chỉ mục này lưu một số mốc tóm tắt, không lưu từng record.
2. **Binary search trên chỉ mục.** [`TimeIndex.lookup`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java#L152) gọi `largestLowerBoundSlotFor` để tìm entry có timestamp lớn nhất nhưng vẫn `<= target`. Khác với hàm của bài tìm biên đầu tiên `>= target`, Kafka tìm mốc phía trước để chọn điểm bắt đầu đọc.
3. **Scan để tìm record phù hợp.** [`LogSegment.findOffsetByTimestamp`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java#L752) dùng offset index để đổi `max(indexedOffset, startingOffset)` thành vị trí byte trong file, rồi gọi [`FileRecords.searchForTimestamp`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/clients/src/main/java/org/apache/kafka/common/record/internal/FileRecords.java#L349). Hàm duyệt các batch, bỏ qua batch có timestamp lớn nhất vẫn nhỏ hơn target, rồi đọc record đến khi cả timestamp và offset thỏa điều kiện. `indexIntervalBytes` không phải cận trên độ dài đoạn scan: time index có thể không thêm entry khi timestamp chưa vượt mức lớn nhất cũ, và kích thước batch có thể khác nhau. Nếu chỉ mục có m entry, bước tìm kiếm trên đó có chi phí so sánh O(log m); truy vấn đầy đủ còn phải tính chi phí scan.

Chạy từng bước trên một time index gồm bốn entry, dạng `timestamp lớn nhất đã gặp -> offset`: `1000 -> 0`, `1500 -> 40`, `2100 -> 85`, `2600 -> 130`. Consumer tìm timestamp 2000 với `startingOffset = 0`.

<details>
<summary>Đáp án</summary>

Thuật toán của Kafka giữ khoảng đóng `[lo, hi]` và chọn `mid = (lo + hi + 1) >>> 1`. Ban đầu, `lo = 0, hi = 3`: mid = 2, timestamp 2100 lớn hơn 2000, nên `hi = 1`. Tiếp theo, `lo = 0, hi = 1`: mid = 1, timestamp 1500 nhỏ hơn 2000, nên `lo = 1`. Khi `lo == hi == 1`, kết quả là entry `1500 -> 40`.

Kafka dùng offset index để tìm vị trí file tương ứng với offset 40, rồi scan từ đó để tìm record đầu tiên có timestamp ít nhất 2000. Nếu target nhỏ hơn timestamp đầu tiên trong chỉ mục, chẳng hạn 500, phép tìm không trả entry nào; `TimeIndex.lookup` trả base offset của segment.

</details>

**Đối chiếu hai cách tìm kiếm.**

| `LowerBound` trong bài | `indexSlotRangeFor` của Kafka |
|---|---|
| Vị trí đầu tiên `>= x` | Vị trí có key lớn nhất `<= x`, rồi scan để tìm record |
| Khoảng nửa mở `[lo, hi)`, `mid = lo + (hi - lo) / 2` | Khoảng đóng `[lo, hi]`, `mid = (lo + hi + 1) >>> 1`, có thể trả ngay khi khớp |
| Timestamp của mọi phần tử trong mảng đã sắp xếp | Giá trị timestamp lớn nhất đã gặp tăng dần trong chỉ mục; timestamp của record có thể không tăng |
| Đếm số phép so sánh trong mô hình chi phí | Cần xét cả các memory page được truy cập |

Kafka ánh xạ file chỉ mục vào bộ nhớ và truy cập qua page cache của hệ điều hành. Dữ liệu được đọc theo các page, nên cùng số phép so sánh chưa chắc dẫn đến cùng thời gian truy vấn.

Comment trong [`AbstractIndex.java`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L340) giải thích: khi file tăng kích thước, binary search thông thường có thể chuyển sang truy cập các page lâu không được dùng. Nếu chúng không còn trong cache, luồng xử lý phải chờ đọc đĩa. Tác giả báo cáo produce latency tăng từ vài millisecond lên khoảng một giây trong thử nghiệm này. Đây là kết quả được báo cáo trong comment, không phải phép đo tái hiện trong bài.

Trong [`indexSlotRangeFor`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L492), Kafka kiểm tra ranh giới của vùng cuối chỉ mục, với `warmEntries() = 8192 / entrySize()` (khoảng 8 KiB entry). Nếu target vượt ranh giới đó, nó chỉ tìm trong vùng cuối; nếu không, tìm trong vùng trước. Vùng cuối được gọi là "warm" vì thường xuyên được truy cập, nên các page có khả năng còn trong cache cao hơn. Số phép so sánh vẫn logarithmic theo số entry; thay đổi nằm ở các page mà thuật toán truy cập.

**Giới hạn khi áp dụng sang bài toán khác.** Với timestamp `[10, 30, 20]`, khoảng `[20, 30)` chứa một sự kiện. Tuy nhiên, hai lần `LowerBound` cùng trả 1, khiến phép trừ cho kết quả sai là 0. Nguyên nhân là dữ liệu chưa sắp xếp theo timestamp. Kafka tìm offset để bắt đầu đọc; record phía sau vẫn có thể mang timestamp nhỏ hơn. Vì vậy, trừ hai offset Kafka không cho số sự kiện trong một khoảng thời gian. Muốn đếm, cần dữ liệu riêng đã sắp xếp theo timestamp hoặc scan với điều kiện lọc tương ứng.

**Suy luận để áp dụng.** Nếu ứng dụng của bạn thường truy vấn dữ liệu gần thời điểm hiện tại, cần xem vùng dữ liệu được truy cập bên cạnh số phép so sánh. Phân tích Big-O mô tả mức tăng chi phí theo kích thước dữ liệu; nó không xác định các page hay cache line cụ thể được đọc. Hiệu quả của cách chia vùng truy cập phải được đo trên dữ liệu và tải truy vấn của ứng dụng.

**Áp dụng vào dự án.**

1. Với nhiều truy vấn theo khoảng trên dữ liệu đã sắp xếp theo key cần tìm, dùng lower bound thay vì duyệt cả list cho từng truy vấn. Chỉ giải mã `BinarySearch` bằng `~result` khi kết quả âm.
2. Với file lớn, chỉ mục thưa có thể giảm dung lượng chỉ mục và chọn điểm bắt đầu scan. Đo cả chi phí tìm trong chỉ mục và phần scan còn lại; mật độ chỉ mục và thứ tự dữ liệu quyết định đánh đổi.
3. Với mảng đã sắp xếp theo timestamp, đếm khoảng `[start, end)` bằng hiệu hai biên. Log không có thứ tự timestamp cần cách xử lý khác.
4. Ghi thêm vào cuối chỉ giữ được thứ tự nếu key mới `>=` key cuối. Nếu không, phải chèn đúng vị trí và dịch phần tử, sắp xếp một batch, hoặc dùng một cấu trúc chỉ mục phù hợp với cập nhật.

**Nghỉ 30 phút, ăn trưa.**

## 7. Thực hành C# có hướng dẫn

**Thực hành · khoảng 75 phút.** Viết lại `LowerBound` từ bất biến, dự đoán kết quả các trường hợp biên, chạy kiểm tra, rồi cố tình tạo lỗi để phân tích. **Hoàn thành khi:** các kiểm tra đều pass, giải thích được một lỗi đã tránh và một giả định của thuật toán.

Chạy từ `labs/boundary-search/dotnet` với .NET SDK 10.0.401:

```bash
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

Lần chạy mặc định trả biên trái của 30 là 3. Số sự kiện trong `[10,30)`, `[30,30)` và `[11,39)` lần lượt là 3, 0 và 3. Bộ kiểm tra gồm 17 nhóm: duplicate, key không tồn tại, khoảng rỗng, hai biên bằng nhau hoặc bị đảo, key âm và cực trị, dữ liệu đầu vào không bị thay đổi, quy tắc mã hóa vị trí chèn của .NET, một mảng ảo có `int.MaxValue` vị trí, và các mảng nhỏ đối chiếu với cách duyệt toàn bộ. Nếu có kiểm tra thất bại, chương trình trả exit code khác 0. Nếu không chạy lab, có thể theo dõi từng bước trên giấy.

Các bước thực hành:

1. **Viết lại thuật toán (20 phút).** Đóng phần mã nguồn, tự viết `LowerBound` và giải thích bất biến ở mục 3. Có thể mở lại mục 4 để đối chiếu.
2. **Dự đoán trường hợp biên (15 phút).** Ghi kết quả trước khi chạy từng bước:

   | Mảng và lời gọi | Câu hỏi |
   |---|---|
   | `[2,4,4,9]`, target 4 | Vị trí đầu tiên? |
   | `[2,4,4,9]`, target 5 | Vị trí chèn? |
   | `[2,4,4,9]`, target 0 và 10 | Kết quả ở hai phía ngoài mảng? |
   | `[]`, target 4 | Có đọc phần tử nào không? |
   | `[10,10,20,30,30,40]`, khoảng `[20,40)` | Số sự kiện? |
   | Cùng mảng, khoảng `[41,50)` | Số sự kiện? |

<details>
<summary>Đáp án</summary>

| Mảng và lời gọi | Kết quả |
|---|---|
| `[2,4,4,9]`, target 4 | 1 |
| `[2,4,4,9]`, target 5 | 3 |
| `[2,4,4,9]`, target 0 và 10 | 0 và 4 |
| `[]`, target 4 | 0, không đọc phần tử nào |
| `[10,10,20,30,30,40]`, khoảng `[20,40)` | 3, từ hai biên 2 và 5 |
| Cùng mảng, khoảng `[41,50)` | 0, từ hai biên 6 và 6 |

Nếu `end < start`, chẳng hạn `[30,10)`, phải từ chối truy vấn trước khi lấy hiệu hai biên.

</details>

3. **Chạy kiểm tra và debug (20 phút).** Khi một trường hợp thất bại, theo dõi mảng nhỏ nhất gây lỗi để tìm bước làm sai bất biến.
4. **Cố tình sửa sai một nhánh (15 phút).** Thử `hi = mid - 1` với `[1, 3]`, target 3, rồi thử `lo = mid` với `[1]`, target 2. Bất biến hoặc lập luận về việc dừng sai ở đâu? Theo dõi thay đổi thứ hai trên giấy để tránh chạy một vòng lặp không dừng.

<details>
<summary>Đáp án</summary>

- Với `hi = mid - 1`, midpoint đầu là 1; đặt `hi = 0` làm mất vị trí đúng là 1. Phải dùng `hi = mid` để giữ vị trí có giá trị bằng target.
- Với `lo = mid`, khi còn một phần tử nhỏ hơn target, `mid == lo`, nên khoảng không thu hẹp. Dùng `lo = mid + 1` để loại vị trí đó và bảo đảm tiến triển.

</details>

5. **Kết thúc (5 phút).** Giải thích một lỗi đã tránh và một giả định cần giữ khi dùng hàm.

**Gợi ý debug:** nếu trả sai duplicate đầu tiên, kiểm tra nhánh xử lý khi bằng nhau. Nếu lỗi với mảng rỗng, kiểm tra việc đọc phần tử có nằm trong vòng lặp `lo < hi` hay không. Nếu lỗi khi target lớn hơn mọi giá trị, kiểm tra xem hàm có cho phép trả `n` hay không.

**Nghỉ 10 phút.** Rời màn hình.

## 8. Quan sát số lần đọc và chi phí cập nhật

**Quan sát · khoảng 45 phút.** Dự đoán số lần đọc phần tử, chạy thí nghiệm và đối chiếu kết quả. **Hoàn thành khi:** giải thích được số lần đọc tăng thế nào và phép đếm này không đo được chi phí nào.

`CountedSequence` tính giá trị khi được truy cập theo index và đếm số lần đọc. Nhờ đó, có thể khảo sát chi phí theo kích thước dữ liệu mà không cấp phát một mảng lớn. Mã nguồn nằm trong `LessonLab/Extras.cs`:

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

Dự đoán số lần đọc với n = 8, 1.024 và 65.536 khi gọi `BoundarySearch.LowerBound(new CountedSequence(n), n)`, rồi chạy:

```bash
dotnet run -c Release --project LessonLab -- --observe
```

Làm lại với target nhỏ hơn mọi key và target lớn hơn mọi key. Số lần đọc thay đổi thế nào? Phép đếm này không cho biết điều gì?

<details>
<summary>Đáp án và kết quả quan sát</summary>

Kết quả với .NET SDK 10.0.401, mỗi dòng theo dạng `n index reads`:

```text
8 4 3
1024 512 10
65536 32768 16
records: 1 3 2
```

Trong các dãy này, target nằm gần giữa miền giá trị. Tăng n từ 1.024 lên 65.536, tức gấp 64 lần, chỉ làm tăng thêm sáu lần đọc. Cận trên số lần đọc là `floor(log₂(n)) + 1`, bằng 17 với n = 65.536. Ở kích thước này, target -1 cần 17 lần đọc; target n và `2L * n` cần 16. Các target khác có thể cần số lần đọc khác nhau nhưng không vượt cận trên đó.

Kiểm tra tăng trưởng trong lab dùng target giữa dãy, không thử mọi input lớn. Phép đếm chỉ đo số lần đọc phần tử; nó không đo số lệnh CPU, thời gian thực thi hay số page phải đọc từ database. Chi phí chờ page từ đĩa trong ví dụ Kafka ở mục 6 không được thể hiện qua phép đếm này.

</details>

Chi phí cập nhật cần được phân tích riêng. Chèn gần đầu list có n phần tử phải dịch khoảng n phần tử. Vì vậy, một `List<long>` đã sắp xếp nhận vị trí chèn bất kỳ có thể tốn O(n) mỗi lần ghi, dù tìm vị trí chỉ tốn O(log n). Sắp xếp một batch chưa có thứ tự tốn O(n log n) trong mô hình so sánh thông thường; đây là chi phí chuẩn bị, tách biệt với chi phí mỗi truy vấn sau đó.

| Ghi trước khi chạy | Ghi sau khi chạy |
|---|---|
| Số lần đọc dự đoán với từng n | Số lần đọc quan sát được |
| Target nào cần nhiều lần đọc nhất? | Kết quả với target nhỏ hơn, nằm trong và lớn hơn miền giá trị |
| Chi phí nào phép đếm chưa đo được? | Một giới hạn của kết quả |

**Nghỉ 10 phút.** Rời màn hình.

## 9. Áp dụng cho record và truy vấn SQL Server

**Áp dụng · khoảng 35 phút.** Chuyển từ timestamp đơn lẻ sang record, dự đoán kết quả, rồi đối chiếu với truy vấn SQL. **Hoàn thành khi:** kiểm tra được hai biên của ví dụ record và giải thích được trường hợp target nằm ngoài dữ liệu.

### Tìm record theo timestamp

Một sự kiện thường có cả timestamp và ID. Nhiều sự kiện có thể trùng timestamp mà vẫn có ID khác nhau:

```csharp
public sealed record Event(long Timestamp, string Id);
```

Đổi `LowerBound` để nhận `IReadOnlyList<T> items`, `long target` và `Func<T, long> key`. List đã sắp xếp theo giá trị do hàm `key` trả về. Với `[(10,A), (20,B), (20,C), (30,D)]`, hãy tìm hai biên của `[20, 30)` và số sự kiện trong khoảng. Kiểm tra thêm target 31, lớn hơn key cuối.

<details>
<summary>Đáp án</summary>

Hàm `key` lấy giá trị từ record trong mảng; target vẫn là một giá trị `long`, không phải record. Giữ bất biến cũ và thay `items[mid]` bằng `key(items[mid])` khi so sánh:

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

`LowerBound(events, 20, e => e.Timestamp)` trả 1; `LowerBound(events, 30, e => e.Timestamp)` trả 3. Hiệu `3 - 1 = 2` tính đúng hai sự kiện B và C. Target 31 trả 4, một vị trí sau phần tử cuối. List phải giữ thứ tự theo đúng hàm `key` đó. Lệnh `--observe` in `records: 1 3 2`; `--check` kiểm tra các vị trí biên trong ví dụ này.

</details>

Dùng thống nhất đơn vị timestamp và quy ước múi giờ. Trộn giây với millisecond có thể làm truy vấn sai mà không gây exception. Hàm `key` chạy mỗi lần đọc một record để so sánh. Nếu việc lấy key tốn nhiều công, có thể tính trước, nhưng phải trả chi phí lưu trữ và đồng bộ khi cập nhật. Với dữ liệu thay đổi thường xuyên, cần cân nhắc cấu trúc cây hoặc chỉ mục có thứ tự thay cho list dùng mảng; chi phí tìm kiếm, cập nhật và lưu trữ sẽ khác nhau.

### Truy vấn theo khoảng thời gian trong SQL Server

Điều kiện tương ứng trong T-SQL là `ts >= @s AND ts < @e`. Ví dụ dưới đây chạy trong database thử nghiệm và lưu các sự kiện có timestamp duplicate thành những dòng riêng:

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

Dự đoán số sự kiện, rồi thử hai giá trị biên bằng nhau. Thay điều kiện bằng `BETWEEN @s AND @e` sẽ đổi kết quả thế nào?

<details>
<summary>Đáp án</summary>

Kết quả dự kiến là **3**: tính hai dòng tại thời điểm đầu và dòng 10:10, loại hai dòng tại thời điểm cuối. Hai giá trị biên bằng nhau cho kết quả 0. `BETWEEN @s AND @e` tính cả thời điểm cuối, nên trả 5 và không còn đúng yêu cầu khoảng nửa mở. Chỉ đặt `ts` là unique nếu nghiệp vụ không cho phép nhiều sự kiện cùng thời điểm; timestamp không thay thế ID của sự kiện.

</details>

Ví dụ SQL cần SQL Server và không được thực thi bởi lab C#. Kết quả trên được suy ra từ dữ liệu và điều kiện lọc, không phải số liệu đo trên database.

Điều kiện này là **sargable**: cột đã lập index được so sánh trực tiếp với parameter có kiểu tương thích, nên SQL Server có thể dùng index seek để định vị khoảng cần đọc. Ngược lại, `DATEPART(year, ts) = @year` tính một giá trị từ cột, không đưa trực tiếp khoảng timestamp để seek. Có thể viết `ts >= @yearStart AND ts < @nextYearStart` để giữ phép so sánh trên cột gốc.

Sargable không bảo đảm optimizer sẽ chọn seek. Lựa chọn còn phụ thuộc vào tỷ lệ dòng thỏa điều kiện, thống kê phân bố dữ liệu và kích thước bảng. Kiểm tra actual execution plan và dùng `SET STATISTICS IO ON` để quan sát chi phí đọc.

Trên mảng, hai lower bound cho số lượng bằng hiệu index. Một index thông thường trong SQL Server không làm `COUNT_BIG` trở thành thao tác O(log n): định vị khoảng có thể nhanh, nhưng đếm vẫn có thể phải đọc từng entry thỏa điều kiện. Đây là hai loại chi phí khác nhau. `datetime2` không lưu múi giờ, nên cần một quy ước như UTC cho cả dữ liệu và parameter. Dùng độ chính xác nhất quán, không cộng một "epsilon" để biến biên cuối bao gồm thành biên cuối không bao gồm.

## 10. Tổng hợp và tự kiểm tra

**Tổng hợp · khoảng 45 phút.** Giải thích thuật toán không nhìn tài liệu, đối chiếu với bảng và giải ví dụ mới. **Hoàn thành khi:** nêu được một lựa chọn thiết kế cùng lý do, và một câu hỏi cần tìm hiểu thêm.

Giải thích vì sao phải cập nhật `hi` khi giá trị bằng target, vì sao trả `n` hợp lệ và vì sao gặp một phần tử khớp chưa đủ để trả kết quả. Nếu thuật toán sai, giữ lại ví dụ nhỏ nhất gây lỗi, sửa quy tắc cập nhật rồi thử một ví dụ khác.

| Nội dung kiểm tra | Lập luận cần có | Nếu chưa rõ, hãy thử |
|---|---|---|
| Tính đúng của cách chia mảng | Hai bất đẳng thức trong bất biến; mảng rỗng, duplicate, key không có và key ngoài miền giá trị | Ghi index dưới từng giá trị và vẽ hai phần |
| Khả năng dừng và chi phí | Mỗi nhánh giảm `hi - lo`; số lần so sánh O(log n) với truy cập theo index O(1) | Theo dõi khoảng chỉ còn một phần tử |
| Đếm theo khoảng | Hai biên; tính start và loại end | Đặt duplicate tại cả hai biên |
| Đánh đổi khi sử dụng | Tìm nhanh không loại bỏ chi phí dịch phần tử, lấy key hay đọc page | Đếm số phần tử dịch khi chèn đầu list |

Ví dụ mới: `[5, 5, 5, 7, 9]`, khoảng `[5, 9)`. Hãy tìm hai biên và số phần tử trong khoảng.

<details>
<summary>Đáp án</summary>

`LowerBound(5) = 0` và `LowerBound(9) = 4`, nên kết quả là 4: cả ba số 5 và số 7. Số 9 không được tính. Phép tìm một phần tử bằng 5 có thể trả vị trí 1; dùng vị trí đó sẽ làm phép trừ sai.

</details>

Bài luyện thêm: tìm biên của `[1,1,3]` với target 1, rồi `[2,4,4,9]` với target 5. Với `[10,10,20,30,30,40]`, đếm `[20,40)` và `[41,50)`. Giải thích cách xử lý khoảng đảo `[30,10)` và điều kiện cần giữ khi tìm record theo key.

<details>
<summary>Đáp án bài luyện thêm</summary>

- `[1,1,3]`, target 1: biên 0; không có phần tử nhỏ hơn target.
- `[2,4,4,9]`, target 5: biên 3; ba phần tử trước đó đều nhỏ hơn target.
- `[10,10,20,30,30,40]`, khoảng `[20,40)`: kết quả 3, từ hai biên 2 và 5.
- Cùng mảng, khoảng `[41,50)`: kết quả 0, từ hai biên 6 và 6.
- Khoảng bị đảo: từ chối truy vấn trước khi lấy hiệu hai biên.
- Tìm record: target là một giá trị key; list phải giữ thứ tự theo cùng key khi cập nhật.

</details>

Khi ôn lại, tự viết thuật toán và theo dõi một target có duplicate mới mà không nhìn tài liệu. Sau đó thay cách biểu diễn record hoặc các giá trị biên và giải thích kết quả. Nếu còn sai lập luận, ôn lại sớm hơn; khi đã chắc, có thể giãn khoảng cách ôn.

Câu hỏi mở rộng: vì sao biên trái và biên phải xử lý giá trị bằng nhau khác nhau? Hàm lấy key thêm chi phí gì? Vì sao chèn vào list đã sắp xếp vẫn tuyến tính? Sau bước tìm trong index của Kafka còn công việc gì?

<details>
<summary>Đáp án</summary>

Biên trái giữ giá trị bằng target ở phần bên phải bằng `hi = mid`. Biên phải đưa chúng sang phần bên trái bằng `lo = mid + 1` khi bằng nhau, để tìm vị trí đầu tiên có giá trị lớn hơn target. Hàm lấy key chạy trên mỗi record được kiểm tra nên thêm chi phí vào mỗi lần so sánh. Tìm vị trí chèn có chi phí O(log n), nhưng dịch các phần tử phía sau có thể tốn O(n). Kafka còn phải đổi offset sang vị trí byte trong file, duyệt batch và record, và có thể chờ đọc page từ đĩa. Số phép so sánh trong chỉ mục chưa mô tả toàn bộ chi phí truy vấn.

</details>

## Đọc thêm

- [Time index của Apache Kafka](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L340): giải thích vùng warm và hàm `indexSlotRangeFor` ở commit dùng trong mục 6.
- [List<T>.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0) và [Array.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0): quy tắc trả về với duplicate và cách mã hóa vị trí chèn bằng bitwise complement.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): điều kiện lọc theo khoảng, lựa chọn index và execution plan.
- [Hướng dẫn lab C#](../../../labs/boundary-search/dotnet/README.vi.md): cài đặt môi trường, lệnh chạy và các kiểm tra.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 01 - Big-O và cấu trúc dữ liệu: dedupe mã đơn hàng bằng C#](../2026-10-05-cost-model/lesson.md) - Ôn cách công việc bên trong vòng lặp quyết định chi phí.
- [Ghi chú theo chủ đề kỹ thuật](../../references/topic-notes.md) - Khám phá chỉ mục có thứ tự, xử lý truy vấn và thiết kế thuật toán.

---

[← Bài trước: Bài 01 - Big-O và cấu trúc dữ liệu: dedupe mã đơn hàng bằng C#](../2026-10-05-cost-model/lesson.md) · [Danh sách bài học](../../README.md)
<!-- LESSON_NAVIGATION_END -->
