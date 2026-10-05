# Bài 01 — Big-O và cấu trúc dữ liệu: loại đơn hàng trùng

**Ngày:** 05/10/2026, Asia/Bangkok · **90 phút**, mở rộng **180+ phút**.
**Topic:** advanced-algorithms.cost-model-membership.l1.
**IUH:** Advanced Algorithms `6001127`; liên hệ Advanced Database `6001111`.
[English](../../../lessons/2026-10-05-cost-model/lesson.md) · [Lab](../../../labs/cost-model/lab.py) · [Lời giải code](../../../labs/cost-model/solution.py) · [Nguồn và xác minh](../../../lessons/2026-10-05-cost-model/sources.json).

**Ý chính:** một vòng lặp nhìn thấy được vẫn có thể tốn O(n²), nếu mỗi vòng tìm trong
một danh sách ngày càng dài. Đổi cách lưu dữ liệu có thể giảm tổng chi phí, nhưng phải
kiểm tra thứ tự kết quả, bộ nhớ và điều kiện của phép hash.

## Vì sao bắt đầu ở đây?

Bạn muốn nền CS, chương trình IUH và kiến thức phục vụ công việc. Curriculum môn
Advanced Algorithms yêu cầu phân tích độ phức tạp, đánh giá hiệu năng thực tế và chọn
thuật toán. Advanced Database có indexing/hashing. Bài này là nền do tutor chọn để nối
hai mục tiêu đó; **không phải tên bài hay prerequisite chính thức của IUH**.

Chưa có bằng chứng về trình độ hay bài học trước của bạn, không có lượt ôn đã ghi.
So với binary search, bài này cần ít kiến thức về invariant/index hơn; so với transaction,
nó ít setup và giúp hình thành cách đánh giá chi phí trước. Không giả định bạn đã biết
Python/C#/SQL. Đây là bài hằng ngày đầu tiên được xuất bản.

Sau bài, bạn có thể tự kiểm:

1. Đếm chi phí membership trong một quá trình loại trùng, thay vì chỉ đếm vòng lặp.
2. Giải thích khi nào set giúp giảm thời gian, và cần thêm bộ nhớ gì.
3. Giữ đúng yêu cầu “lấy lần xuất hiện đầu”, rồi chuyển sang bài toán đếm bản trùng.

Mọi self-check, lab và bài tập đều **tùy chọn, có lời giải xem ngay**. Không cần nộp
bài để đọc bài ngày sau. Đọc code/đáp án là một đường học hợp lệ; không tự coi đó là
bằng chứng thành thạo độc lập.

## Lộ trình 90 phút

| Thời gian | Học gì | Đường chỉ đọc |
|---|---|---|
| 0–10 | Self-check và phần nền ngắn | Đọc câu hỏi/đáp án, chọn đoạn cần đọc chậm |
| 10–35 | Cost model, Big-O, worst/expected/amortized | Làm theo phép đếm và bảng |
| 35–55 | Trace hai cách loại trùng | Đọc từng bước, xem invariant |
| 55–75 | Lab tùy chọn | Đối chiếu output đã xác minh, không cần cài Python |
| 75–85 | Challenge và trade-off | Đọc lời giải đếm duplicate |
| 85–90 | Chốt ý, câu ôn dự kiến | Đọc đáp án và ghi chú nếu muốn |

Thời lượng áp dụng cho **một bản ngôn ngữ**; không bắt đọc cả hai bản dịch.

## 1. Self-check có lời giải

**A.** `['B2','A1','B2']` có mấy phần tử, mấy mã khác nhau?

**Lời giải:** 3 phần tử, 2 mã khác nhau. Độ dài input n khác số giá trị khác nhau u.

**B.** Với `result=['B2','A1']`, để biết `'C3'` đã có chưa, nếu chỉ duyệt tuần tự thì
cần tối đa mấy lần so sánh?

**Lời giải:** 2. Phải đọc hết mới kết luận không có. Nếu tìm B2, có thể dừng ngay.

**C.** `['B2','A1','B2','C3','A1']` sau loại trùng nhưng giữ lần xuất hiện đầu là gì?

**Lời giải:** `['B2','A1','C3']`. `['A1','B2','C3']` có cùng giá trị nhưng sai yêu cầu thứ tự.

**Nhánh bổ sung nền:** list là dãy có thứ tự; `for value in values` lần lượt lấy từng
phần tử; `==` kiểm bằng nhau; `append` thêm cuối dãy; `in` hỏi có tồn tại. Với set,
`add` lưu một giá trị và không tạo bản sao thứ hai nếu giá trị đã có. `{}` là dict rỗng;
set rỗng viết `set()`. Nếu chưa quen syntax, dùng các định nghĩa này và bảng trace;
không cần hoàn thành diagnostic trước khi đọc tiếp.

## 2. Tình huống công việc và đặc tả

Job nhận mã đơn hàng từ log. Một mã có thể lặp. Muốn tạo danh sách mã khác nhau theo
thứ tự nhận lần đầu, không đổi dữ liệu gốc.

```text
Input : B2, A1, B2, C3, A1
Output: B2, A1, C3
```

Giả định: mã là string, so sánh chính xác, phân biệt hoa/thường. `a` và `A` là hai mã
khác nhau; không tự strip/lowercase. Đổi quy tắc đồng nhất mã là quyết định nghiệp vụ.

**Dự đoán tùy chọn:** “có một vòng for thì chắc O(n)” đúng không?

**Lời giải:** chưa đủ. Phải xem công việc bên trong mỗi vòng. Membership trong list
có thể quét toàn bộ kết quả đã tích lũy.

## 3. Mô hình chi phí và Big-O

**n:** số phần tử input. **u:** số mã khác nhau, 0 ≤ u ≤ n. Trước hết giả định so sánh
mã/hash mã có chi phí giới hạn; tách độ dài mã ra ở phần trade-off.

Big-O nói về một cận trên của tốc độ tăng chi phí khi input lớn, **không phải số giây**.
Nếu n đủ lớn và T(n) ≤ C·n² cho một hằng số C, ta nói T(n) thuộc O(n²). Θ(n²) nói cận
tăng trưởng khớp cả trên/dưới trong mô hình đó; ở đây dùng cho input toàn mã khác nhau.

| Mức tăng | Khi n gấp đôi, biểu thức tăng khoảng | Ví dụ dưới giả định phù hợp |
|---|---:|---|
| O(1) | 1 lần | Một thao tác giới hạn chi phí |
| O(log n) | Tăng thêm một lượng hằng | Tìm nhị phân trên dãy đã sắp |
| O(n) | 2 lần | Một lần quét |
| O(n log n) | Hơn 2 lần một chút | Một số thuật toán sort theo so sánh |
| O(n²) | 4 lần | So mỗi phần tử với nhiều phần tử khác |

Bảng minh họa **biểu thức chi phí**, không đảm bảo tỷ lệ wall-clock đo được.

### Cách 1: tìm trong kết quả bằng quét

```python
result = []
for value in values:
    if value not in result:
        result.append(value)
```

Nếu toàn mã khác nhau, mỗi phần tử phải so với toàn bộ result trước đó:

```text
0 + 1 + 2 + ... + (n-1) = n(n-1)/2
```

Vậy worst case Θ(n²) trong mô hình so sánh đơn vị. Tổng chi phí có thể mô tả theo n/u
là O(n(1+u)); u nhỏ có thể khiến cách này gần tuyến tính. Nếu tất cả cùng một mã,
chỉ n−1 lần so sánh sau phần tử đầu. Không kết luận mọi input luôn tốn n².

### Cách 2: dùng set cho membership, list cho output

```python
result = []
seen = set()
for value in values:
    if value not in seen:
        seen.add(value)
        result.append(value)
```

Set dùng hashing để hướng lookup tới các vị trí trong bảng, thay vì luôn quét từ đầu.
Trong điều kiện hash/so sánh phù hợp và bảng được quản lý tốt, lookup có chi phí kỳ vọng
O(1); insertion có phần phân tích amortized do đôi lúc cần resize. Cả quá trình kỳ vọng
O(n), với giả định chi phí key. **Không bảo đảm mọi lookup O(1)**: collision và key đắt
có thể làm chậm; trường hợp xấu có thể dẫn tới chi phí toàn quá trình O(n²).

- **Worst case:** input/hành vi bất lợi nhất trong mô hình đã nêu.
- **Expected:** kỳ vọng theo giả định phân bố/randomness; không là lời hứa cho mọi input.
- **Amortized:** phân bổ chi phí của nhiều thao tác, kể cả vài lần resize đắt; không
  đồng nghĩa expected và không có nghĩa mọi lần insertion đều nhanh.

Với string dài L, hash lần đầu hoặc equality có thể phụ thuộc L. Cache hash có thể
giảm một số chi phí, nhưng không được coi mọi key/so sánh là O(1) trong workload thật.

### Bộ nhớ và đúng đắn

Cả hai trả list kết quả O(u). Nếu **không tính output**, cách quét cần O(1) state phụ,
cách hash cần O(u) cho seen. Nếu **tính cả output**, cả hai dùng O(u), nhưng hash có
thêm overhead đáng kể. Cùng Big-O không có nghĩa cùng số byte.

Đừng trả `list(set(values))` nếu yêu cầu giữ lần xuất hiện đầu: set **không có cam kết
thứ tự chèn**. Một lần chạy tình cờ đúng thứ tự không chứng minh hợp đồng.

## 4. Worked example và invariant

| value | result sau xử lý | seen sau xử lý — viết như tập, không phải thứ tự |
|---|---|---|
| B2 | [B2] | {B2} |
| A1 | [B2, A1] | {B2, A1} |
| B2 | [B2, A1] | {B2, A1} |
| C3 | [B2, A1, C3] | {B2, A1, C3} |
| A1 | [B2, A1, C3] | {B2, A1, C3} |

**Invariant:** sau mỗi prefix đã xử lý, seen chứa đúng các mã trong prefix; result
chứa mỗi mã đúng một lần, theo thứ tự xuất hiện đầu trong prefix.

Khởi đầu prefix rỗng → cả hai rỗng. Nếu mã đã thấy, giữ nguyên. Nếu mã mới, thêm vào
seen/result cuối dãy → invariant tiếp tục đúng. Xử lý hết input → đúng đặc tả.

**Câu hỏi tùy chọn:** n vòng membership có chứng minh thuật toán luôn O(n) không?

**Lời giải:** không. n là số **lần gọi**; mỗi lời gọi có thể làm nhiều phép hash/equality,
và seen.add cũng có chi phí. Lab cố ý phân biệt hai bộ đếm này.

## 5. Lab tái lập, hoàn toàn tùy chọn

Python standard library, dữ liệu synthetic deterministic, không database server/network
hay package ngoài. Tutor đã chạy trên **Python 3.12.14**, SQLite tích hợp **3.53.1**;
đây là version tái lập, không phải khuyến nghị version production mới nhất.

Từ repo root:

```bash
cd labs/cost-model
python --version
python lab.py
python check.py --module solution.py
```

Không có runtime → đọc trace/output dưới đây. Trace giấy không phải code đã chạy.
Starter cố ý chưa điền; dùng `solution.py` để đọc hoặc chạy lời giải ngay.

**Bước 1 — kiểm đặc tả:** dự đoán output của orders rồi chạy. Checkpoint `[B2,A1,C3]`.
Giải thích sau chạy: result giữ thứ tự, seen chỉ phục vụ membership.

**Bước 2 — đếm mô hình:** `unique_scan` dùng equality tường minh; `unique_hash` đếm
membership calls. Với toàn giá trị khác nhau:

| n | Equality của scan | Membership calls của hash |
|---:|---:|---:|
| 128 | 8.128 | 128 |
| 256 | 32.640 | 256 |
| 512 | 130.816 | 512 |

Đã chạy: input orders có **6 equality checks** của scan, **5 membership calls** của hash.
Input 128 mã A1 giống nhau có **127 equality checks** của scan.

**Lời giải checkpoint:** số scan đúng n(n−1)/2 trên input distinct; gấp đôi n khiến
chi phí này xấp xỉ gấp bốn. Membership calls bằng n, nhưng không phải tổng cost hash.
Đây không là benchmark thời gian hay “nhanh hơn 1.000 lần”. Bộ đếm của thuật toán quét
mô hình không phải số operation của mọi tối ưu bên trong CPython `list.__contains__`.

**Bước 3 — thử viết nếu muốn:** điền `unique_hash` và `duplicate_summary` trong
[starter.py](../../../labs/cost-model/starter.py), rồi:

```bash
python check.py --module starter.py
```

Expected sau implementation đúng: **4 tests pass**. Lời giải trong [solution.py](../../../labs/cost-model/solution.py).
Test kiểm empty/duplicate/case sensitivity/order/input preservation/collision và một
mô hình equality giúp phát hiện dùng quét thay hash. Test không chứng minh mọi workload
production nhanh hay reasoning của người học đúng.

**Debug:** duplicate còn xuất hiện → kiểm cập nhật seen; thứ tự sai → đừng trả set;
`TypeError: unhashable type` → key cần hashable; list/dict nguyên khối không dùng trực
tiếp làm key, hãy chọn string ID ổn định. Module import fail → chạy trong working
directory đã nêu. Starter NotImplementedError là bình thường nếu chưa làm bài.

## 6. Challenge đổi ngữ cảnh, kèm lời giải

**Đề tùy chọn:** thay vì loại trùng, trả các mã xuất hiện trên một lần và số lần xuất
hiện, theo thứ tự xuất hiện đầu. Input orders → `[('B2',2),('A1',2)]`. Không thay input.

**Lời giải:** dict lưu tần suất; key xuất hiện đầu được thêm trước. Python có bảo đảm
insertion order của dict từ 3.7; updating một key không đưa nó xuống cuối.

```python
def duplicate_summary(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [(value, count) for value, count in counts.items() if count > 1]
```

Kỳ vọng O(n+u), rút gọn O(n) vì u≤n, với giả định hash/key; memory O(u). Empty → [];
all unique → []; `['x','x','x']` → `[('x',3)]`. Có test tương ứng trong check.py.

**Rubric nếu bạn muốn tự kiểm hoặc gửi bài:** kết quả đúng với edge cases; giữ input/
thứ tự; giải thích invariant và giả định complexity; phân biệt independence/đọc lời giải;
giải thích khi memory/key/collision làm thay đổi lựa chọn. Không yêu cầu điểm số/nộp bài.

## 7. GitHub và kiến thức đã kiểm tra

Chọn **python/cpython**, implementation chính thức, **77.493 stars**, archived=false,
đọc GitHub API ngày 05/10/2026; main commit quan sát
`182f3231542e84fd1b0c795898f69f61fe35df0e` lúc **10:09:25 Asia/Bangkok**.
Pin teaching release **v3.12.14 → 2abcf904b8dac8c999d2b3aac76681abb333798a**.
Stars là metadata discovery, không là bằng chứng quality/adoption. License file có
PSF license và lịch sử license; API SPDX trả NOASSERTION, không suy ra “không có license”.
Không build upstream hay chạy upstream suite; chỉ đọc slice và chạy lab riêng.

Alternative **dotnet/runtime** official, 18.312 stars, archived=false lúc kiểm tra;
không chọn vì mục tiêu đếm chi phí học được bằng Python standard library ít setup hơn.
Không kết luận chất lượng .NET kém. Usage/downstream survey và benchmark upstream chưa làm.

Các mục đọc tùy chọn, đều có đáp án:

- [listobject.c — list_contains](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Objects/listobject.c#L441):
  tìm vòng for và điều kiện dừng. **Đáp án:** duyệt từ index 0, dừng khi equality đúng
  hoặc hết list; một membership có thể làm nhiều comparisons.
- [setobject.c — set_lookkey](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Objects/setobject.c):
  giải thích vì sao cần loop dù là hash. **Đáp án:** probing/collision có thể cần nhiều
  vị trí; kiểm hash rồi equality, không phải “hash là luôn truy cập một bước”.
- [test_set.py — test_contains/test_add](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Lib/test/test_set.py):
  xem duplicate và unhashable. **Đáp án:** add Q hai lần không tạo hai giá trị; list
  mutable không phải key hợp lệ và có case TypeError.

**Liên hệ hiện hành:** đã đọc Python docs dòng 3.12 về set/hashable và insertion order.
Trang online lúc kiểm tra mang nhãn **3.12.15**, còn lab/pin là 3.12.14; pinned docs
xác nhận các semantics dùng ở đây. Không suy latest support/security từ hai số version.

## 8. Nhánh 180+ phút

Sau đường 90 phút, chọn thêm:

### 25 phút — đọc source và ghi cost model

Dùng ba target trên, viết “outer loop n lần × inner membership cost”.
**Lời giải mẫu:** scan distinct có tổng 0…n−1; set dùng probing và resize nên kỳ vọng/
amortized phải nêu giả định, không đồng nhất count calls với time.

### 25 phút — SQL tương đương trên dữ liệu nhỏ

```bash
python lab.py --sql
```

```sql
SELECT order_id, COUNT(*)
FROM events
GROUP BY order_id
ORDER BY MIN(pos);
```

**Lời giải:** output `B2:2, A1:2, C3:1`. Nếu chỉ muốn duplicate, thêm
`HAVING COUNT(*) > 1` trước ORDER BY → B2:2, A1:2. pos là thứ tự ingest được lưu rõ.
SQL không đảm bảo thứ tự result nếu không có ORDER BY. GROUP BY không chứng minh engine
thực hiện cùng thuật toán Python: có thể dùng sort/index/các phương án khác. Với workload
thật cần query plan, cardinality, index và I/O; không suy tốc độ SQL từ lab này.

### 25 phút — collision có chủ đích

```bash
python lab.py --collisions
```

Lời giải trong lab.py tạo Key có `__hash__` luôn trả 1. Trên runtime đã chạy: 100 calls,
**11.964 equality checks**; output vẫn đúng. Con số equality là observation của runtime
này, không universal guarantee. **Đáp án:** collision ảnh hưởng cost, không nhất thiết
correctness; hash giống nhau không có nghĩa keys bằng nhau.

### 15 phút — quyết định cho một job lớn

**Đề tùy chọn:** 10 triệu records, ID dài, RAM hạn chế. “Dùng set là luôn tốt nhất”?

**Lời giải:** không. Đánh giá u, độ dài ID, object overhead và retention của seen. Nếu
u rất lớn, cân nhắc external sort/dedup, database uniqueness hoặc lưu trạng thái trên
đĩa. Những lựa chọn có chi phí ordering/I/O/concurrency riêng. Set RAM có thể tốt khi
key nhỏ/u vừa và cần lookup nhanh; không có winner chỉ dựa vào n. Lọc trùng trước gọi
API cũng chưa bảo đảm exactly-once: concurrent jobs, crashes và retry cần idempotency/
unique constraints phù hợp, sẽ học sau.

Optional hơn 180 phút: `python lab.py --timing`. Code có timeit repeat và cố định input;
tutor **chưa chạy timing**, không có speedup claim. Kết quả bao gồm instrumentation,
phụ thuộc interpreter/máy/cache/data và không thay benchmark workload công việc.

## 9. Tóm ý và tự ôn có đáp án

1. **Một for có luôn O(n)?** Không; cost mỗi body có thể tăng theo dữ liệu đã tích lũy.
2. **Vì sao giữ cả list và set?** Set giúp membership; list giữ thứ tự output.
3. **Set có luôn O(1)?** Không; kỳ vọng theo giả định, có collisions/resize/key cost.
4. **O(n) có chắc nhanh hơn O(n²) ở n nhỏ?** Không; constant/overhead và input matter.
5. **Đọc đáp án có đồng nghĩa mastered?** Không; vẫn có thể dùng bài để tự học và đọc tiếp.

Prompt ôn dự kiến, chưa tạo lịch ôn thật: ngày khác giải thích lại n(n−1)/2 với input mới;
hoặc đổi bài sang đếm duplicate trên event IDs. Đáp án: cùng lập luận scan distinct và
dict count ở trên. Nếu muốn kiểm independent sau khi đã xem lời giải, dùng task mới.

Bài tiếp theo dự kiến: **binary search và invariant** nếu phần so sánh/loop đã quen;
nếu còn mới, đọc **mảng, truy cập index và loop** trước. Đây là lựa chọn có điều kiện,
không claim prerequisite đã được chứng minh. Gọi cùng skill để nhận bài tiếp; không cần nộp.

## 10. Nguồn, vai trò và phạm vi xác minh

- **Curriculum:** IUH condensed Master 2020, Advanced Algorithms/Advanced Database, đọc
  local 05/10/2026. Phạm vi official trong repo; PDF gốc/quy định mới chưa kiểm lại.
- **Lý thuyết:** MIT OCW 6.006 Fall 2011, [Lecture 9 Hashing II](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf),
  đọc trang 1–3 ngày 05/10/2026: expected lookup, load factor, resize và amortization.
  Chaining minh họa theory; CPython set dùng open addressing, không đồng nhất hai implementation.
- **Official technical:** [Python set/dict docs](https://docs.python.org/3.12/library/stdtypes.html#set-types-set-frozenset),
  [pinned stdtypes.rst](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Doc/library/stdtypes.rst),
  source/test/license CPython ở trên; đọc các phần liên quan ngày 05/10/2026.
- **SQL semantics:** [SQLite SELECT](https://www.sqlite.org/lang_select.html), phần grouping
  và ordering đọc ngày 05/10/2026; local equivalent chạy được, không SQL Server benchmark.
- **Tutor synthesis:** tình huống order IDs, lựa chọn topic, budgets, rubric và lab tự viết.
  Không phải kết luận khoa học về thời lượng tối ưu. Không vendor CPython code.

Agent đã chạy reference lab và 4 tests; chưa có bài làm hay assessment của bạn.
[sources.json](../../../lessons/2026-10-05-cost-model/sources.json) giữ hashes/pin/metadata; [observations](../../../lessons/2026-10-05-cost-model/agent-observations.txt)
chỉ là output của agent, không phải tiến độ người học.
