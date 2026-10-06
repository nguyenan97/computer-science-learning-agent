# Bài 02 - Tìm biên: từ mảng có thứ tự đến truy vấn khoảng thời gian

**Học theo thời gian của bạn: trace → implement → test → transfer**

[English](../../../lessons/boundary-search/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/boundary-search/dotnet-lab.zip)

Bài trước hỏi một ID đã xuất hiện chưa. Bây giờ dữ liệu đã sorted, ta cần câu trả lời khác: **điều kiện bắt đầu đúng ở vị trí nào?** Biên đó giúp đếm event trong khoảng thời gian mà không quét mọi event cho mỗi query. Thuật toán đầy đủ, lập luận và bài tập có lời giải nằm trên trang; link standard library để đọc sâu.

## Lý do chọn và outcome

**Mục tiêu:** implement biên dưới đúng cho timestamp đã sorted, tái sử dụng để đếm `start <= timestamp < end`, kể cả duplicate và endpoint không có. Giải thích vì sao query logarithmic nhưng insert vào List phẳng vẫn có thể tuyến tính.

Cần indexed access, comparison và loop. Quy ước khoảng nửa mở được giải thích dưới đây. Nếu mới học binary search, bắt đầu bằng ví dụ có index thay vì học thuộc code.

| Block | Hoạt động | Output cụ thể |
|---|---|---|
| 1 | Nhớ cost model và khoảng nửa mở | Giải thích index được tính và chi phí insert đầu |
| 2 | Suy ra partition, tự dựng trace | Ghi rõ hai vùng đã biết và từng update |
| 3 | Dự đoán duplicate, empty và target thiếu | Biên kỳ vọng cho từng case trước khi chạy code |
| 4 | Implement và debug lab C# | Biên dưới và window count đã đối chiếu với case biên |
| 5 | So contract library và đếm element read | Giải thích equality search, insertion encoding và chi phí query/update |
| 6 | Chuyển contract window sang event record và T-SQL | Query cùng ngữ nghĩa endpoint và giải thích index |
| 7 | Explain-back, xem lại một lỗi | Nêu invariant, trả lời case duplicate mới không ghi chú |

Nghỉ và mở rộng phần đọc nguồn theo thời gian research thực tế. Mỗi block có thể trace giấy; chạy lab tùy chọn. Giữ phần cốt lõi ở query đã sorted, rồi dùng phần database để hiểu cách chuyển lập luận, chưa xây database application hôm nay.

## Retrieval và prerequisite

Suy nghĩ ba câu:

1. `[lo,hi)` chứa vị trí nào? **Đáp án:** gồm lo, không gồm hi; `[1,3)` chứa index 1 và 2.
2. Insert đầu array-backed List thay đổi gì? **Đáp án:** phần tử cũ phải dịch một vị trí sang phải; tìm nhanh không bỏ được công việc đó.
3. Vì sao một loop chưa chứng minh tuyến tính ở Bài 01? **Đáp án:** phải tính phần thân. Ở đây, access midpoint và so key cũng cần giả định rõ.

Với `[2,4,4,9]`, giá trị nhỏ hơn 4 chỉ ở index 0. Index đầu có giá trị ít nhất 4 là **1**. Thử `[1,1,3]`, target 1: biên **0**. Nếu chưa rõ, vẽ value trên index, tách “nhỏ hơn target” và “ít nhất target” trước code.

## Vấn đề và dự đoán

Service lưu timestamp sorted:

```text
timestamps = [10, 10, 20, 30, 30, 40]
query       = [10, 30)
```

Khoảng gồm hai event ở 10 và event ở 20, loại hai event ở 30: đáp án **3**. Scan đếm đúng với O(n) comparisons mỗi query. Với nhiều query trên cùng dữ liệu sorted, tìm hai biên:

- Index đầu tại hoặc sau start: 0.
- Index đầu tại hoặc sau end: 3.
- Count: `3−0=3`.

Search trả một 30 bất kỳ có thể trả index 4, sai vì tính thêm một event tại endpoint bị loại. Cần partition boundary, không chỉ equality match. Endpoint thiếu cũng cần đáp án: `[11,39)` gồm 20,30,30 nên count 3 dù 11 và 39 không có trong mảng.

## Nền tảng và cập nhật liên quan

Định nghĩa `lower_bound(values,x)` là index i đầu có `values[i] >= x`; không có thì trả n. Nó chia mảng sorted thành hai phần:

```text
values[:i]   đều < x
values[i:]   đều >= x
```

Ký hiệu mô tả partition; implementation không tạo slice.

### Vì sao dùng đoạn chưa biết [lo,hi)?

Giữ `0 <= lo <= hi <= n` và các sự thật:

- Trước lo đã biết mọi giá trị < x.
- Từ hi trở đi đã biết mọi giá trị >= x.
- Chỉ `[lo,hi)` còn cần kiểm tra; biên có thể ở hi.

Ban đầu lo=0, hi=n: vùng đã biết rỗng, cả mảng chưa biết. Cuối cùng lo==hi: hai vùng biết gặp nhau, vị trí đó là đáp án. Trả n an toàn vì trả index, không đọc `values[n]`.

Tại midpoint mid:

- Nếu `values[mid] < x`, sorted order chứng minh mọi vị trí trước cũng quá nhỏ. Đổi lo thành `mid+1`.
- Ngược lại, mid và mọi vị trí sau ít nhất x. Đổi hi thành mid. Giữ mid làm biên tiềm năng; equality có thể có duplicate trước đó.

Cả hai nhánh loại mid khỏi vùng chưa biết, giảm hi−lo nghiêm ngặt: loop sẽ dừng. Chia gần nửa mỗi bước cho O(log n) comparisons khi n>=2; empty/singleton chỉ cần công việc hằng số. Giả định random-access array và comparison cost bị chặn. Linked list, key extraction đắt hay remote access đổi chi phí thật.

## Worked example nêu quyết định

Với `[1,3,3,8]`, x=3:

| lo | hi | mid | value | Quyết định và lý do |
|---|---|---|---|---|
| 0 | 4 | 2 | 3 | hi=2: equality thuộc partition phải, có thể còn 3 trước |
| 0 | 2 | 1 | 3 | hi=1: giữ candidate biên sớm hơn |
| 0 | 1 | 0 | 1 | lo=1: index 0 quá nhỏ |
| 1 | 1 | — | — | Trả 1; hai partition gặp nhau |

Trả 2 ngay equality đầu tìm được match, chưa là match đầu. Định nghĩa biên quyết định nhánh equality.

Target dưới min, ví dụ 0, liên tục đẩy hi trái và trả 0. Target trên max, ví dụ 10, đẩy lo phải và trả 4. Input rỗng bắt đầu lo==hi==0, trả 0 mà không đọc phần tử.

## Lab hướng dẫn từng bước

Implementation Python đầy đủ chỉ dùng indexing/comparison:

```python
def lower_bound(values, target):
    lo, hi = 0, len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

Midpoint luôn là phần tử hợp lệ khi lo<hi. Code không mutate, copy mảng con hay sort. Input phải sorted theo cùng ordering dùng để so sánh. Check sortedness ở mỗi query tự tốn O(n); thiết lập invariant khi tạo/cập nhật dữ liệu.

### Dự đoán case trước khi chạy hoặc trace

```python
values = [2, 4, 4, 9]
assert lower_bound(values, 4) == 1
assert lower_bound(values, 5) == 3
assert lower_bound(values, 0) == 0
assert lower_bound(values, 10) == 4
assert lower_bound([], 4) == 0
assert values == [2, 4, 4, 9]
```

Giá trị thiếu có vị trí chèn: target 5 nằm giữa 4 cuối và 9. Vì vậy lower_bound vẫn hữu ích dù không có equality match.

Tự dựng method, dự đoán case biên, trace/test, cố tình tạo/debug lỗi nhánh, rồi giải thích correction. Hai lỗi đáng thử:

- `hi=mid-1`: với `[1,3]`, target 3, midpoint đầu là 1; hi=0 làm mất đáp án đúng 1. Invariant nửa mở cần hi=mid.
- `lo=mid`: vùng chưa biết dài một, value quá nhỏ thì mid==lo, đoạn không co lại. Dùng lo=mid+1.

Dấu hiệu khác: sai duplicate đầu → xem equality; empty error → chỉ đọc trong loop nonempty; fail target trên max → cho đáp án n.

### Quan sát chi phí mà không nhầm với timing

Sequence sau tính value khi indexed access và đếm lượt đọc, nên minh họa scaling mà không cấp array lớn:

```python
class Counted:
    def __init__(self, n):
        self.n = n
        self.reads = 0

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        if not 0 <= i < self.n:
            raise IndexError(i)
        self.reads += 1
        return i * 2

for n in (8, 1024, 65536):
    values = Counted(n)
    index = lower_bound(values, n)
    print(n, index, values.reads)
```

Output có lời giải:

```text
8 4 3
1024 512 10
65536 32768 16
```

Target gần giữa sequence giả lập. n từ 1.024 lên 65.536 tăng 64 lần nhưng chỉ thêm sáu read. Target khác có thể có read count khác; tốc độ tăng worst-case vẫn logarithmic. Đây là element access, chưa phải CPU instruction, wall-clock hay database page read.

## Chuyển sang C#: contract search và lab chạy được

C# là ngôn ngữ implementation của lab chạy được trong bài này. Ví dụ Python được giữ vì CPython công khai implementation `bisect_left` ngắn, dễ đọc và test: so contract partition giữa các ngôn ngữ, không thêm dependency Python vào công việc .NET.

### BinarySearch tìm match, không hứa trả duplicate đầu tiên

Cả [`Array.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0) và [`List<T>.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0) yêu cầu dữ liệu sorted theo comparer dùng để search. Search thành công trả một index matching, nhưng contract **không** đảm bảo duplicate đầu hoặc cuối. Target thiếu trả bitwise complement của insertion position: giải mã kết quả **âm** bằng `~result`.

```csharp
long[] values = [10, 10, 20, 30, 30, 40];
int match = Array.BinarySearch(values, 30L);
Console.WriteLine(values[match]);

List<long> list = [.. values];
int result = list.BinarySearch(11L);
int position = result >= 0 ? result : ~result;
Console.WriteLine($"{result}, {position}");
```

Code in `30`, rồi `-3, 2`: 11 sẽ được chèn tại index 2. `-result` cho 3, là sai. Khi target trên max, insertion position là `Count`: biên hợp lệ nhưng không phải phần tử để đọc. Key không có thì không có duplicate cần phân biệt, nên vị trí giải mã này bằng lower boundary. Equality search thành công không hứa trả duplicate đầu. Không trừ hai kết quả `BinarySearch` thành công để đếm window có endpoint duplicate.

### Implement partition bằng C#

Đây là implementation đầy đủ trong [lab C#](../../../labs/boundary-search/dotnet/README.vi.md). Nó nhận array và `List<long>` qua indexed access của `IReadOnlyList<long>`:

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

Nhánh equality giữ duplicate đầu làm candidate. `lo + (hi - lo) / 2` tránh cộng hai index `int` lớn; `(lo + hi) / 2` có thể overflow trong C#, còn integer Python không có giới hạn fixed-width đó. Method so key `long` mà không trừ chúng, nên timestamp cực trị không gây arithmetic overflow. Kết luận comparisons logarithmic vẫn giả định `Count`, indexing và comparison có chi phí hằng số; implementation `IReadOnlyList` bất kỳ không nhất thiết thỏa các giả định này.

Từ `labs/boundary-search/dotnet`, với SDK 10.0.401:

```bash
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

Lệnh mặc định cho lower boundary 3 với 30, window count 3, 0 và 3 cho `[10,30)`, `[30,30)` và `[11,39)`. Check gồm duplicate đầu, target thiếu, window empty/equal/reversed, key âm/cực trị, giữ nguyên input và insertion encoding của .NET. Chúng còn search mảng ảo có `int.MaxValue` vị trí mà không cấp phát mảng, so case nhỏ với phép quét. Check fail thì exit khác 0. Tự implement trước khi đối chiếu nếu hữu ích; lời giải luôn xem được và hoàn thành lab tùy chọn.

## Đọc implementation standard library

Implementation `bisect` chính thức của Python dùng ý tưởng partition này. Source slice sau ghim để so implementation ổn định thay vì branch di chuyển:

- [Lib/bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/bisect.py): tìm bisect_left, so nhánh equality với bisect_right.
- [Lib/test/test_bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/test/test_bisect.py): chọn một case duplicate và một case missing; dự đoán partition trước khi xem expected.
- [Tài liệu bisect chính thức](https://docs.python.org/3/library/bisect.html): đọc định nghĩa partition, key semantics và Performance Notes.

**Đáp án đọc:** bisect_left trả biên trước các value bằng, bisect_right trả biên sau. Module Python có thể dùng implementation C nội bộ; interpreter đã cài không nhất thiết chạy body source Python từng dòng. Contract là điểm so sánh hữu ích.

Trong experiment chi phí, so read count khi target dưới, trong và trên sequence; dự đoán bound đổi ra sao khi n gấp đôi. Sau đó đếm entry phải dịch nếu insert gần đầu. Search O(log n), insert array-backed List O(n) vì phải dịch storage. Sort batch chưa có thứ tự một lần tốn O(n log n) theo mô hình so sánh thường dùng; preprocessing tách khỏi chi phí từng query sau đó.

## Challenge độc lập và biến thể transfer

Implement `count_window(timestamps,start,end)` cho timestamp integer sorted. Đếm start-inclusive/end-exclusive, không sửa input, chấp nhận empty data/endpoint bằng nhau, ValueError khi end<start. Không scan, copy slice hay sort mỗi query.

Lời giải đầy đủ trừ hai lower boundary:

```python
def count_window(timestamps, start, end):
    if end < start:
        raise ValueError("end precedes start")
    return lower_bound(timestamps, end) - lower_bound(timestamps, start)

values = [10, 10, 20, 30, 30, 40]
assert count_window(values, 10, 30) == 3
assert count_window(values, 30, 30) == 0
assert count_window(values, 11, 39) == 3
assert count_window([], 10, 30) == 0
```

**Vì sao trừ đúng:** lower_bound(start) là số value nhỏ hơn start; lower_bound(end) là số value nhỏ hơn end. Bỏ phần trước để còn đúng value ít nhất start, nhỏ hơn end. Duplicate ở start được tính, ở end bị loại. Endpoint bằng nhau tạo cùng biên, count zero. Hai search logarithmic vẫn O(log n), bộ nhớ phụ O(1).

### Đổi representation: event record và key

Event thật có thêm thuộc tính. Key của bisect áp vào record trong array, **không áp vào search target**:

```python
from bisect import bisect_left

events = [
    {"timestamp": 10, "id": "A"},
    {"timestamp": 20, "id": "B"},
    {"timestamp": 20, "id": "C"},
    {"timestamp": 30, "id": "D"},
]
key = lambda event: event["timestamp"]
left = bisect_left(events, 20, key=key)
right = bisect_left(events, 30, key=key)
assert (left, right, right - left) == (1, 3, 2)
```

Truyền 20, không truyền full record, làm target. List phải sorted theo timestamp. Dùng đơn vị và cách hiểu timezone nhất quán; trộn seconds/milliseconds hay representation không tương thích có thể làm query sai âm thầm. Key extraction chạy trên record được kiểm tra; key đắt có thể cần precomputed key, tốn storage và đồng bộ lúc update.

Nếu write thường xuyên, sorted List phẳng có thể không phù hợp. Ordered index/tree có chi phí query/update/storage riêng. Lập luận partition chuyển sang được, nhưng số so sánh in-memory chưa dự đoán database I/O, concurrency, collation hay query plan.

## Chuyển sang SQL Server: time window trên index

Cùng contract membership chuyển trực tiếp sang T-SQL: `ts >= @s AND ts < @e`. Trong database thử nghiệm, ví dụ này giữ timestamp duplicate thành các event riêng:

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

Count kỳ vọng là **3**: tính hai row ở start và row 10:10; loại hai row ở end. Biên bằng nhau trả zero. `BETWEEN @s AND @e` sẽ tính end, đổi contract. Không dùng unique index trên `ts` trừ khi domain cấm event đồng thời; timestamp và định danh event trả lời hai câu hỏi khác nhau.

Range predicate là **sargable**: so trực tiếp cột có index với parameter có kiểu tương thích, cho phép SQL Server dùng biên index seek. Function như `CAST(ts AS date)` bọc cột có thể cản range access trực tiếp này; tính query bound trước query. Sargability cho phép seek, không đảm bảo seek: selectivity, statistics, kích thước table và optimizer quyết định plan. Xem actual execution plan và `SET STATISTICS IO ON` khi chạy ví dụ SQL tùy chọn.

Hai lower boundary trên random-access array cho count bằng phép trừ index. Index SQL Server thông thường không biến `COUNT_BIG` thành phép O(log n) tương đương: execution vẫn có thể phải đọc mọi index entry thỏa điều kiện để aggregate count. Tìm range và đếm range có chi phí riêng. `datetime2` không lưu timezone; dùng quy ước UTC nhất quán hoặc representation đã normalize rõ cho cả value lưu và bound. Khớp unit và precision, không cộng “epsilon” tùy ý vào endpoint inclusive. Console lab check logic integer-window, không thực thi ví dụ SQL này.

## Rubric, feedback và exit

Dùng các câu sau để review implementation:

| Tiêu chí | Giải thích tốt cần gì | Chưa rõ thì thử |
|---|---|---|
| Partition correctness | Hai inequality; empty, duplicate, missing, beyond-range | Vẽ value có index và hai partition |
| Termination/cost | Mỗi nhánh giảm hi−lo; logarithmic với random access | Trace vùng chưa biết dài một |
| Window behavior | Hai biên; gồm start, loại end | Duplicate cả hai endpoint |
| Trade-off | Query nhanh chưa bỏ dịch insert hay key cost | Đếm move cho insert đầu |

Giải thích bằng lời mình vì sao equality đổi hi, vì sao trả n hợp lệ, vì sao midpoint matching bất kỳ chưa đủ. Case fail → giữ ví dụ nhỏ nhất, sửa rule, thử ví dụ mới. Hữu ích hơn học thuộc hai câu update.

## Câu hỏi mở và kế hoạch ôn lại

Sau một khoảng, tự dựng partition và trace duplicate target mới không ghi chú. Sau đó đổi event representation hay endpoint, giải thích window result. Sai thì ôn sớm hơn; lập luận ổn thì tăng khoảng.

Ba câu để đọc sâu: Vì sao left/right boundary khác ở equality? Key function thêm công việc gì? Vì sao insort vẫn tuyến tính dù binary search? Implementation và docs được link trả lời các câu này.

## Bài tập tùy chọn và lời giải

- `[1,1,3]`, target 1: biên 0; partition nhỏ hơn không có phần tử.
- `[2,4,4,9]`, target 5: biên 3; cả ba phần tử trước nhỏ hơn.
- `[10,10,20,30,30,40]`, window `[20,40)`: count 3, từ biên 2 và 5.
- Cùng mảng, window `[41,50)`: count 0, từ biên 6 và 6.
- Endpoint đảo: từ chối query trước khi trừ biên.
- Record search: target là giá trị key; giữ cùng ordering khi update List.

## Đọc thêm

- [Tài liệu Python bisect](https://docs.python.org/3/library/bisect.html): contract partition left/right chính xác, key behavior và insert cost.
- [CPython bisect source](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/bisect.py) và [tests](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/test/test_bisect.py): so quyết định implementation với trace và test tự thiết kế.
- [Python sorting how-to](https://docs.python.org/3/howto/sorting.html): chuẩn bị dữ liệu sorted, key function và stable ordering trước query.
- [List<T>.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0) và [Array.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0): contract duplicate match và insertion position được complement.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): range predicate, lựa chọn index và query plan.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 01 - Big-O và cấu trúc dữ liệu: loại bỏ duplicate mã đơn hàng bằng C#](../2026-10-05-cost-model/lesson.md) - Ôn cách công việc bên trong vòng lặp quyết định chi phí.
- [Ghi chú theo chủ đề kỹ thuật](../../references/topic-notes.md) - Khám phá chỉ mục có thứ tự, xử lý truy vấn và thiết kế thuật toán.

---

[← Bài trước: Bài 01 - Big-O và cấu trúc dữ liệu: loại bỏ duplicate mã đơn hàng bằng C#](../2026-10-05-cost-model/lesson.md) · [Danh sách bài học](../../README.md)
<!-- LESSON_NAVIGATION_END -->
