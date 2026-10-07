# Bài 05 - Index và query plan: vì sao seek vẫn có thể tốn nhiều công

[English](../../../lessons/2026-10-09-index-query-plans/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/index-query-plans/dotnet-lab.zip)

Một endpoint báo cáo ASP.NET tính tổng sự kiện của một tenant trong khoảng thời gian. Cùng endpoint đó có thể khớp 18 hoặc 18.000 dòng. Thêm index đổi cách tìm đến các dòng, chưa làm các dòng hay giá trị của chúng biến mất. Ta sẽ đọc plan SQLite thật và so sánh các truy vấn tương đương, gồm cả chi phí duy trì index khi ghi.

**Mục tiêu:** giải thích truy cập theo đoạn index, quét toàn bộ, thứ tự khóa ghép, tra thêm bảng và covering index. Liên hệ plan với tỷ lệ dòng khớp, dung lượng và chi phí đọc/ghi đo được. Lộ trình chọn lưu trữ và index sau tìm biên; cách phân biệt trạng thái và chi phí ở Bài 04 vẫn hữu ích. Cần biết mảng, vòng lặp, so sánh và khoảng nửa mở. Bài sẽ bổ sung trang dữ liệu, B-tree, mã định vị dòng, phép tổng hợp SQL và cách đọc plan.

## Khái niệm chính

- **Trang dữ liệu và cây có thứ tự.** Database lưu các khối gọi là trang; B-tree dẫn tìm khóa qua vài mức trang thay vì so sánh mọi dòng. Một trang chứa nhiều phần tử, nên một phép so sánh không phải một lần đọc đĩa.
- **Index ghép.** Sắp theo trường đầu, phân định khi bằng nhau bằng trường tiếp theo và giữ mã định vị dòng. Với `(Tenant,Occurred)`, các thời điểm của tenant 1 nằm cùng nhóm; thời điểm 5 của mọi tenant chưa chắc nằm trong một đoạn liền nhau.
- **Seek và scan.** Seek định vị khóa bắt đầu; sau đó truy vấn có thể quét nhiều phần tử. Tìm được phần tử đầu trong 18.000 dòng khớp mới chỉ là bước đầu.
- **Bao phủ truy vấn.** Index bao phủ khi có đủ mọi giá trị truy vấn cần. Thêm `Amount` có thể bỏ bước tra từng dòng khớp trong bảng; index vẫn chưa có `Payload`.
- **Selectivity.** Trong 20.000 dòng, khớp 18 dòng là 0,09%, còn 18.000 dòng là 90%. Bài dùng tỷ lệ dòng khớp này, r/N, làm selectivity. Tỷ lệ nhỏ thường có lợi cho truy cập theo đoạn, nhưng còn phải xét độ bao phủ, thứ tự và cách bố trí trang.

Bạn có thể chỉ đọc bảng, plan và mã đầy đủ mà chưa chạy lab. Giới hạn cài đặt trong 15 phút của phần lab; nếu chưa xong, tiếp tục đọc. Không cần nộp bài hay lưu kết quả học cá nhân.

## 1. Ôn lại và nối kiến thức nền

**Ôn tập · 20 phút.** Dựng lại hai cơ chế planner chọn, rồi nối biên trong mảng với truy vấn database. **Hoàn thành khi:** nêu được mỗi cách biểu diễn giữ thông tin gì.

1. Từ Bài 04: F(i,c) giữ thông tin gì khi chọn 0/1?

<details>
<summary>Đáp án</summary>

Đó là giá trị cộng dồn lớn nhất từ i công việc đầu, chi phí không vượt c. Dãy công việc ghi nhận những công việc được dùng; hai nhánh chọn/bỏ đọc dãy trước nên không chọn lặp. Tương tự, khóa index cần giữ các trường để định vị dòng và đáp ứng yêu cầu tiếp theo. Một chi phí ước lượng đơn lẻ không thay được các trường đó.

</details>

2. Từ Bài 02: với `[2,2,4,7,7]`, có bao nhiêu sự kiện trong `[2,7)`, và vì sao hai lower bound là đủ?

<details>
<summary>Đáp án</summary>

Có ba: lower_bound(2)=0, lower_bound(7)=3 nên 3-0=3. Chứa cả hai số 2 và loại cả hai số 7. Vị trí mảng cho biết thứ hạng nên lấy hiệu sẽ đếm được phần tử. Cursor B-tree không cung cấp cùng thứ hạng cố định như mảng; phép tổng hợp SQL có điều kiện thường vẫn duyệt các phần tử khớp.

</details>

3. `SELECT COUNT(*), SUM(Amount)` trả một dòng sự kiện hay một dòng tổng hợp? Trả một dòng có nghĩa là chỉ xét một dòng không?

<details>
<summary>Đáp án</summary>

Không có GROUP BY thì trả một dòng tổng hợp, kể cả khi không có dòng khớp: COUNT bằng 0, SUM bằng NULL; COALESCE đổi NULL đó thành 0 trong lab. Số dòng trả về không nói lên số dòng được xét. Tổng có thể đọc hàng nghìn giá trị Amount. Bài dùng r cho số dòng đầu vào khớp, không phải số dòng output.

</details>

## 2. Lưu trữ, thứ tự khóa và đoạn truy vấn đúng

**Nền tảng · 50 phút.** Chạy từng bước trên đoạn khóa ghép và giải thích những giá trị phải đọc. **Hoàn thành khi:** chứng minh được biên dừng và bác bỏ nhận định “có index thì phép tổng hợp này là O(log N)”.

### Dòng cụ thể trước công thức

Xem `Occurred` là số phút nguyên từ một mốc mô phỏng, không phải chuỗi ngày tháng đã định dạng. `Id` xác định duy nhất sự kiện; tenant là nhóm khách hàng. Mỗi dòng có `Amount` và payload 96 ký tự. Đây là dữ liệu giả lập, không có hồ sơ khách hàng thật.

| Id | Tenant | Occurred | Amount |
|---|---|---|---|
| 1 | 2 | 0 | 1 |
| 2 | 1 | 0 | 2 |
| 3 | 1 | 1 | 3 |
| 4 | 1 | 1 | 4 |
| 5 | 1 | 2 | 5 |
| 6 | 1 | 2 | 6 |
| 7 | 1 | 3 | 7 |
| 8 | 1 | 3 | 8 |

Với bảng rowid thông thường của SQLite, `Id INTEGER PRIMARY KEY` chính là rowid. Index phụ `(Tenant,Occurred)` giữ rowid đó, cho thứ tự phân định tương đương `(Tenant,Occurred,Id)`. Quy tắc này dành cho schema đang xét; bảng WITHOUT ROWID và mã định vị dòng SQL Server có quy tắc khác. So sánh khóa theo thứ tự từ trái sang phải: Tenant, rồi Occurred, rồi rowid khi bằng nhau.

Điều kiện báo cáo là `Tenant=1 AND Occurred>=1 AND Occurred<3`. Thứ tự trong index gọn là `(1,0,2), (1,1,3), (1,1,4), (1,2,5), (1,2,6), (1,3,7), (1,3,8), (2,0,1)`.

Tìm khóa khớp đầu tiên, khóa dừng, các ID và hai giá trị tổng hợp. Điều gì sai nếu đổi so sánh cuối thành `<=3`?

<details>
<summary>Đáp án</summary>

| Bước | Khóa | Việc làm | Số dòng | Tổng Amount |
|---|---|---|---|---|
| Seek | (1,1,3) | Lấy dòng khớp đầu | 1 | 3 |
| Tiếp | (1,1,4) | Lấy cùng phút | 2 | 7 |
| Tiếp | (1,2,5) | Lấy | 3 | 12 |
| Tiếp | (1,2,6) | Lấy | 4 | 18 |
| Biên | (1,3,7) | Dừng trước mốc cuối | 4 | 18 |

Các ID là 3,4,5,6, kết quả (4,18). `<=3` lấy sai cả ID 7,8, thành (6,33). Hai khoảng nửa mở liền nhau sẽ đếm trùng mốc chung. Seek tới khóa đầu tiên không nhỏ hơn `(1,1)` giữ mọi giá trị trùng ở mốc đầu, thay vì chọn tùy ý một khóa bằng nó.

</details>

### Vì sao đoạn này đầy đủ?

Cố định Tenant cho một nhóm tiền tố liền nhau. Trong nhóm đó, thời điểm không giảm. Seek tới biên dưới bỏ đúng các thời điểm sớm hơn; duyệt tiếp đi qua từng phần tử theo thứ tự khóa. Trước thời điểm đầu tiên không nhỏ hơn mốc cuối, mọi thời điểm được lấy đều thuộc khoảng. Sau đó không thể quay lại khoảng vì thời điểm không giảm. Cũng dừng khi sang tenant khác. Lập luận chứng minh cả việc lấy đủ và loại đúng, không cần thời điểm duy nhất. Trong lab, SQL chịu trách nhiệm thực thi điều kiện; phép quét C# độc lập kiểm tra kết quả.

Index ghép không sắp riêng theo mọi cột. Với `(Occurred,Tenant)`, một khoảng thời gian chứa các nhóm tenant xen kẽ theo thời điểm. Với `(Tenant,Occurred,Amount)`, Amount phân định thời điểm bằng nhau trước Id; điều này có thể ảnh hưởng `ORDER BY Occurred,Id`. Thứ tự index không thay thế yêu cầu ORDER BY rõ ràng trong SQL.

### Trang dữ liệu và chi phí

B-tree của bảng SQLite lưu dòng theo rowid; index phụ là B-tree riêng chứa khóa và rowid. Trang bên trong dẫn tìm khóa, còn cursor duyệt theo thứ tự. Phần tử index SQLite có thể nằm ở cả trang trong và trang lá: không coi nó giống hệt cách tổ chức B+ tree của SQL Server với phần tử ở lá. Bảng ví dụ đã lược bỏ chi tiết implementation này. Index rowstore trên đĩa của SQL Server dùng B+ tree, theo tài liệu thiết kế chính thức.

B-tree cân bằng giữ các trang lá cùng độ sâu; khóa phân cách dẫn tìm kiếm tới khoảng khóa của trang con. Nếu giả định mỗi trang chứa ít phần tử, tám khóa có thể được bố trí như sau:

| Trang | Khóa được lưu | Vai trò |
|---|---|---|
| Gốc | (1,2,5) | Phân cách khóa trước/sau; đây cũng là một phần tử index |
| Con trái | (1,0,2), (1,1,3), (1,1,4) | Khóa trước phần tử gốc |
| Con phải | (1,2,6), (1,3,7), (1,3,8), (2,0,1) | Khóa sau phần tử gốc |

Tìm thời điểm 1 trong tenant 1 sẽ đi sang trái. Duyệt theo thứ tự còn lấy phần tử gốc rồi đi sang phải; duyệt index chưa chỉ là đi qua lá. Đây là bố trí để học, không phải file đã đọc: tám phần tử thật có thể vừa một trang. Một trang có nhiều nhánh nên thêm một mức cây chứa được nhiều phần tử hơn, giúp hiểu mô hình độ cao logarithm.

Index gọn thiếu Amount nên phải theo rowid tới bản ghi trong bảng. Index `(Tenant,Occurred,Amount)` có thể đọc Amount ngay trong index, bỏ lần truy cập cây thứ hai. Nó bao phủ phép tổng hợp này, chưa bao phủ mọi endpoint hay Payload.

Gọi N là số dòng bảng, r là số dòng khớp và B là số nhánh điển hình của một trang. Với khóa có kích thước giới hạn và cây cân bằng có mức lấp đầy phù hợp, định vị đoạn đi qua khoảng O(log_B N) mức trang; duyệt r phần tử cần công việc tỷ lệ với r cùng việc chuyển trang. Mô hình đếm so sánh/phần tử cho tổng hợp qua covering index là O(log N+r); tra cây bảng riêng từng dòng có thể cho O(log N+r log N). Dùng lại cache và các dòng gần nhau có thể làm số lần đọc thực tế nhỏ hơn nhiều. Đây là mô hình, chưa dự đoán mili giây hay số I/O chính xác.

Khác ngân sách C gây độ phức tạp giả đa thức ở Bài 04, các cận này dùng số phần tử lưu trữ N với khóa nguyên cố định. Xây và duy trì cây có chi phí riêng. Insert thường tìm vị trí khóa và có thể tách trang; thêm index hoặc làm khóa rộng hơn tăng dung lượng và công việc duy trì. Chi phí wrapper SQL, transaction và flush cũng nằm ngoài cận đếm so sánh đơn giản.


Vì sao chỉ thêm index thông thường chưa làm truy vấn SUM này thành O(log N) với các Amount tùy ý?

<details>
<summary>Đáp án</summary>

Nếu không có tổng đã lưu sẵn, đổi một Amount khớp chưa đọc có thể đổi đáp án mà không đổi biên khóa. Tổng chính xác phải xét mọi giá trị khớp, tạo yêu cầu đọc giá trị Ω(r) trong mô hình này. Trả một dòng tổng hợp chưa bỏ được việc đó. Tổng tiền tố, bảng tổng hợp sẵn hoặc cây bổ sung thống kê làm đổi cách biểu diễn và trách nhiệm cập nhật; lab chưa implement các cách này.

</details>

Nghỉ - 10 phút, rời màn hình.

## 3. Đọc plan và đối chiếu nhận định với nguồn

**Đọc tài liệu · 45 phút.** Đọc các mục chính thức có giới hạn và chú thích một plan cho mỗi cách truy cập. **Hoàn thành khi:** mỗi cách giải thích có nhận định, bằng chứng và giới hạn.

Đọc [EXPLAIN QUERY PLAN, mục 1.1](https://www.sqlite.org/eqp.html#table_and_index_scans), [Query Planning, mục 1.4, 1.6 và 1.7](https://www.sqlite.org/queryplanner.html), cùng [optimizer overview, mục 2](https://www.sqlite.org/optoverview.html#where_clause_analysis) của SQLite. Nguồn đầu định nghĩa nhãn plan; nguồn thứ hai giải thích tra rowid, thứ tự khóa ghép và độ bao phủ; nguồn thứ ba giới hạn tiền tố khóa và điều kiện theo khoảng có thể dùng. Phạm vi đọc đã giới hạn, không cần đọc mọi cách tối ưu.

### Ba truy vấn tương đương, khác cách truy cập

Giá trị điều kiện là tham số SQL; tenant và hai mốc không được ghép vào chuỗi SQL. `SUM` trả NULL khi không có dòng khớp nên `COALESCE` cho kết quả (0,0) của lab. SQL tổng hợp giống nhau ở mọi cách truy cập; chỉ chỉ thị truy cập chọn từ enum thay đổi.

```sql
SELECT COUNT(*),COALESCE(SUM(Amount),0) FROM Events
WHERE Tenant=$tenant AND Occurred >= $start AND Occurred < $end;

CREATE INDEX ix_thin ON Events(Tenant,Occurred);
CREATE INDEX ix_cover ON Events(Tenant,Occurred,Amount);
```

Với 2.000 dòng sinh ra, tenant 1 và `[0,10)`, demo trả số dòng 18, tổng Amount 198 ở cả ba cấu hình. Plan quan sát từ demo SQLite 3.50.4:

| Cấu hình | Chi tiết plan | Ý nghĩa |
|---|---|---|
| Không có index phụ | `SCAN Events` | Duyệt dòng bảng và xét điều kiện |
| Index gọn | `SEARCH Events USING INDEX ix_thin (Tenant=? AND Occurred>? AND Occurred<?)` | Giới hạn theo tenant/thời gian, rồi đọc Amount từ bảng |
| Covering index | `SEARCH Events USING COVERING INDEX ix_cover (Tenant=? AND Occurred>? AND Occurred<?)` | Giới hạn theo tenant/thời gian và đọc Amount từ index |

Chuỗi chi tiết tóm tắt hai điều kiện biên; ký hiệu `>` trong đó không đổi nghĩa `>=` của SQL. Test kiểm tra kết quả tại biên. Đây là mô tả plan mức cao, chưa đếm dòng, I/O hay thời gian. SQLite ghi rõ định dạng có thể đổi giữa phiên bản; ứng dụng production không nên phân tích chuỗi này như API ổn định. Kiểm tra nhãn của lab là chẩn đoán dành riêng cho phiên bản đã pin.

Khi không ép cách truy cập, planner chọn từ các ứng viên dựa vào ước lượng và thống kê. `ANALYZE` cung cấp thống kê, chưa bảo đảm dữ liệu tương lai giống thế. Thí nghiệm dùng `NOT INDEXED` và `INDEXED BY` để giữ cách truy cập cố định. [Tài liệu INDEXED BY](https://www.sqlite.org/lang_indexedby.html) của SQLite mô tả đây là yêu cầu bắt buộc, không phải gợi ý; thiếu index hoặc không dùng được index đã nêu có thể làm lỗi bước chuẩn bị. Bài dùng nó để so sánh có kiểm soát, không khuyến nghị ép index cho production.

SCAN có thể dùng index không, và SEARCH có nghĩa là truy vấn ít tốn công không?

<details>
<summary>Đáp án</summary>

Có. SCAN có thể là duyệt toàn bộ index thay vì bảng; một covering index gọn có thể giúp cách đó hiệu quả. SEARCH mô tả truy cập có giới hạn, nhưng đoạn đó vẫn có thể chứa 90% số dòng bảng. Cần đọc điều kiện nào giới hạn tìm kiếm và có phải tra thêm bảng không. Không nhãn nào chứng minh thứ hạng runtime.

</details>

Viết ba dòng nhận định/bằng chứng/giới hạn cho truy cập theo đoạn, độ bao phủ và tiền tố khóa ghép. Thiếu điều kiện bằng ở cột đầu có nghĩa là không bao giờ dùng được index không?

<details>
<summary>Đáp án</summary>

| Nhận định | Bằng chứng | Giới hạn |
|---|---|---|
| Seek định vị đoạn, rồi duyệt các phần tử | Query Planning 1.4 và các điều kiện theo khoảng trong demo | Tổng hợp vẫn xét các dòng đầu vào; chuỗi plan chưa phải I/O đo được |
| Bao phủ bỏ bước lấy giá trị từ dòng bảng | Query Planning 1.7 và demo covering | Chỉ bao phủ các cột truy vấn này cần; index rộng tốn thêm dung lượng |
| Điều kiện bằng ở đầu rồi điều kiện theo khoảng tạo đoạn liền nhau đơn giản | Optimizer overview 2 | Skip-scan và cách khác là ngoại lệ của quy tắc tuyệt đối “thiếu cột đầu thì không thể” |

Với `(Tenant,Occurred)`, truy vấn chỉ theo thời gian không có một đoạn đơn giản trong nhóm tenant cố định. SQLite có thể quét index hoặc dùng skip-scan khi thống kê và số khóa đầu trùng làm cách đó có lợi. Không biến quy tắc thiết kế hữu ích thành nhận định không thể dùng index. Tương tự, cột bên phải cột theo khoảng thường không thu hẹp thêm đoạn cơ bản này; chúng vẫn có thể cung cấp giá trị để bao phủ hay lọc.

</details>

## 4. Ứng dụng dự án và implementation SQLite tại commit cố định

**Đọc mã nguồn · 45 phút.** Lần theo phần tìm đoạn và ước lượng chi phí dưới đây, rồi liên hệ với endpoint báo cáo. **Hoàn thành khi:** tách cơ chế đã xác minh khỏi khuyến nghị production còn cần đo.

### Ứng dụng: báo cáo tenant bằng .NET và SQL Server

Dịch vụ ASP.NET nhận tenant và hai timestamp của `[start,end)`, tính số dòng/tổng Amount rồi trả cho Angular. Dùng tham số và kiểm tra khoảng. SQL Server rowstore có thể dùng index nonclustered với tenant ở đầu, sau đó là thời gian, cùng Amount được INCLUDE để bao phủ phép tổng hợp. Cần xác định đơn vị thời gian, cách đổi timezone và kiểu giá trị; phút nguyên trong lab chỉ là mô phỏng.

Ứng viên bao phủ trong SQL Server có thể là `(TenantId,OccurredUtc) INCLUDE(Amount)`. INCLUDE giữ giá trị không thuộc khóa, chưa biến nó thành trường phân định khi sắp; `ix_cover` của SQLite đưa Amount vào chính khóa. Hai cách cùng nhằm bao phủ nhưng khác thứ tự và lưu trữ. Không dùng số trang, hằng số chi phí hay cú pháp ép truy cập SQLite để kết luận về SQL Server. [Tài liệu thiết kế index](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17) giải thích B+ tree, mã định vị dòng, included column và đánh đổi đọc/ghi.

Trước khi so hiệu năng, phải giữ cùng kết quả nghiệp vụ. Đo các kích thước tenant, khoảng thời gian, cột cần trả và tỷ lệ insert/update đại diện. Tra bảng nhiều qua index không bao phủ có thể kém scan; plan bao phủ có thể làm đổi lựa chọn đó. Tránh thêm Payload chỉ để mọi truy vấn đều được bao phủ: index rộng tăng dung lượng và công việc ghi. Tính đúng, hiệu năng và quyền truy cập là trách nhiệm riêng; lab dùng tenant giả lập và chưa implement authorization của API.

### Database dùng ý tưởng này để thực thi truy vấn

Source SQLite tại tag `version-3.50.4`, commit GitHub cố định **`8ed5e7365e6f12f427910188bbf6b254daad2ef6`**, là case study. SQLite là database thực chạy trong lab C#, không chỉ chứa một hàm tìm kiếm tự viết.

1. [`sqlite3BtreeIndexMoveto`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/btree.c#L6044-L6195) so sánh ô khóa trong trang, cập nhật biên tìm kiếm và đi xuống trang con được chọn khi cần. Phần này nối binary search trong trang với cây nhiều trang; chưa phải chứng minh mọi trường hợp biên của cursor.
2. [`sqlite3BtreeNext`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/btree.c#L6317-L6337) tăng vị trí ô và chuyển xử lý biên trang cho `btreeNext`. Sau seek vẫn phải duyệt; seek chưa tự trả kết quả tổng hợp.
3. [Tạo chi phí trong `whereLoopAddBtreeIndex`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/where.c#L3440-L3480) ước lượng rõ việc tìm phần tử đầu, duyệt phần tử tiếp theo và, khi không bao phủ, tìm dòng bảng tương ứng. Kích thước khóa/dòng ước lượng cũng tham gia mô hình. Đây là ước lượng theo thang logarithm của SQLite, chưa phải mili giây đo được hay tỷ lệ chuyển chiến lược dùng cho mọi trường hợp.
4. [`OP_DeferredSeek`](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/vdbe.c#L6587-L6665) nối rowid của index với cursor bảng và có thể hoãn seek thật tới lúc đọc giá trị. Vì thế “tra một lần cho mỗi ứng viên” là mô hình hữu ích, chưa có nghĩa mỗi ứng viên tạo một I/O vật lý.

**Đã xác minh trong source:** tìm khóa trong trang, duyệt cursor tiếp theo, thành phần chi phí phụ thuộc độ bao phủ và việc hoãn tra bảng. **Suy luận thiết kế:** đổi cột cần đọc làm mất độ bao phủ có thể tăng công việc và đổi plan. Không gán số đo của lab cho maintainer hay khẳng định optimizer luôn chọn plan nhanh nhất. Phạm vi đọc chỉ gồm các hàm này; chưa reproduce toàn bộ optimizer, cache hay pager.

Phần nào của đoạn mã chi phí thể hiện việc thêm khi index không bao phủ? Nó có hứa mỗi dòng khớp gây một lần đọc đĩa không?

<details>
<summary>Đáp án</summary>

Source đặt rRun từ ước lượng tìm/duyệt index, rồi cộng thành phần theo nOut khi các cờ không xác định truy cập chỉ index/IPK/expression-index. Nó mô hình hóa việc tìm dòng bảng khớp. DeferredSeek và trang đã cache giải thích vì sao đó chưa phải số lần đọc đĩa nguyên văn. Đọc công thức xác minh cấu trúc mô hình, chưa xác minh độ chính xác trên workload mới.

</details>

Ăn trưa và nghỉ - 30 phút.

## 5. Lab C#: plan thật và đối chiếu kết quả độc lập

**Lab · 75 phút.** Tạo database tạm, chạy các cách truy cập và kiểm tra việc duy trì index sau khi đổi dữ liệu. **Hoàn thành khi:** kiểm tra tính đúng qua và giải thích được một lỗi hiệu năng không làm sai kết quả.

Implement truy vấn báo cáo, đọc plan khi không ép, rồi đối chiếu scan/index gọn/covering được ép với phép quét điều kiện C# độc lập. Giữ `[start,end)`, tách tenant và cùng số dòng/tổng Amount. Dùng lời giải đầy đủ nếu cài đặt hoặc implementation vượt thời gian đã dành.

<details>
<summary>Đáp án - toàn bộ lab chạy được</summary>

Dùng **.NET SDK 10.0.401**, **net10.0**, **Microsoft.Data.Sqlite 10.0.9** và **SQLitePCLRaw.bundle_e_sqlite3 3.0.3**. Engine đi kèm trả **SQLite 3.50.4**, trùng phiên bản case study. `packages.lock.json` pin phiên bản và hash dependency gián tiếp. ZIP chỉ có mã nguồn, không chứa .NET, binary NuGet hay database.

Giải nén ZIP rồi chạy trong `dotnet`; nếu dùng checkout, vào `labs/index-query-plans/dotnet`. Lần restore đầu cần mạng tới NuGet. Khi dependency đã cache, chạy no-restore không cần database server hay dịch vụ mạng. Nếu dựng từ bài, tạo các file dưới đây đúng đường dẫn. [Hướng dẫn lab](../../../labs/index-query-plans/dotnet/README.vi.md) cũng có link từng file.

`dotnet/global.json`:

```json
{
  "sdk": { "version": "10.0.401", "rollForward": "latestPatch" }
}
```

`dotnet/LessonLab/LessonLab.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.Data.Sqlite" Version="10.0.9" />
    <PackageReference Include="SQLitePCLRaw.bundle_e_sqlite3" Version="3.0.3" />
  </ItemGroup>
</Project>
```

`dotnet/LessonLab/packages.lock.json`:

```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {
      "Microsoft.Data.Sqlite": {
        "type": "Direct",
        "requested": "[10.0.9, )",
        "resolved": "10.0.9",
        "contentHash": "/eBwiZPcNisn0qZX+Zk4YCftlK/vnoWqv7hHnmSk8MjPxFdYYkmPObpogT0MfCCWN6oAIZnMCo0SoOtZlbbmgQ==",
        "dependencies": {
          "Microsoft.Data.Sqlite.Core": "10.0.9",
          "SQLitePCLRaw.bundle_e_sqlite3": "2.1.11",
          "SQLitePCLRaw.core": "2.1.11"
        }
      },
      "SQLitePCLRaw.bundle_e_sqlite3": {
        "type": "Direct",
        "requested": "[3.0.3, )",
        "resolved": "3.0.3",
        "contentHash": "Zt8jmSL5zcDWGk8rmzhWBJ6IRyLWh1yWS04Pg72+GIvo3Ba4E/rG4Y/4l7AWlSEogEbzyKRTCXUAs1v/O7Pkkg==",
        "dependencies": {
          "SQLitePCLRaw.config.e_sqlite3": "3.0.3",
          "SourceGear.sqlite3": "3.50.4.5"
        }
      },
      "Microsoft.Data.Sqlite.Core": {
        "type": "Transitive",
        "resolved": "10.0.9",
        "contentHash": "iZrONyMKPjxfVZnUktqO30QjzNwAGH+AxM61s8lKQnVhgbQ3bn0hiXI129ZmVicEbIcwljyy2OVsIYUR51ZHKQ==",
        "dependencies": {
          "SQLitePCLRaw.core": "2.1.11"
        }
      },
      "SourceGear.sqlite3": {
        "type": "Transitive",
        "resolved": "3.50.4.5",
        "contentHash": "UtnipXhJYZKQOQIfpws/msLK7IRhMplE1CZCaZLIQXRnGD474QVpO/J9nMlQQY8NZueGz1aidjoxDRnrC1NT3Q=="
      },
      "SQLitePCLRaw.config.e_sqlite3": {
        "type": "Transitive",
        "resolved": "3.0.3",
        "contentHash": "caP/ap0X2fyVmstCXu5ueOmcr2XWAxA2XyKghV7H4bOAFmq3nWcsGl9q44iY1HYG+i8Qr4G9XEqdfti0rV6/ZQ==",
        "dependencies": {
          "SQLitePCLRaw.provider.e_sqlite3": "3.0.3"
        }
      },
      "SQLitePCLRaw.core": {
        "type": "Transitive",
        "resolved": "3.0.3",
        "contentHash": "bjm6FY4lZyP+t7GmiuvSM0QXpFihAvyE0Y9O2yibm3g95AAWJPNnHOKVNJGyPTGIKuK7Pr4Wh8Rd8/aOtAclQw=="
      },
      "SQLitePCLRaw.provider.e_sqlite3": {
        "type": "Transitive",
        "resolved": "3.0.3",
        "contentHash": "wd+fGvZTrr3BJNe48opSczmC176Okd61ZgoZNQcdvZwkek6to978ccdpcFmNo5GHxCnk29KwT+f+lAZYgfLVZg==",
        "dependencies": {
          "SQLitePCLRaw.core": "3.0.3"
        }
      }
    }
  }
}
```

Chạy trong `dotnet`:

```bash
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```

Mỗi Database tạo và chỉ xóa thư mục tạm do chính instance đó sinh ra. Không trỏ lab vào dữ liệu ứng dụng. Lab dùng một connection, trang 4096 byte, journal DELETE và synchronous FULL. Phép đo chưa benchmark concurrency hay cấu hình bảo đảm lưu bền của production.

Dòng có ID duy nhất từ 1-50000, tenant dương, phút nguyên có dấu kiểu `long`, Amount từ 0-1000. Cận ID giới hạn số dòng lưu, giữ tổng trong `long`. Khoảng rỗng hợp lệ; mốc cuối nhỏ hơn mốc đầu bị từ chối. Không thể lấy dòng ở `long.MaxValue` bằng khoảng nửa mở có mốc cuối lớn hơn nhưng vẫn biểu diễn được. Batch insert lỗi được rollback; wrapper chưa phải lớp truy cập database tổng quát.

`LessonLab/Database.cs` tạo schema/dữ liệu, gắn tham số, đọc plan và có phép quét điều kiện độc lập. `Exec` chỉ nhận SQL cố định trong bài, không nhận input tùy ý của người dùng. SQLite duy trì index, không có hàm tự cập nhật cây trong lab.

```csharp
// Original MIT teaching code; SQLite source is linked, not copied.
using Microsoft.Data.Sqlite;

public readonly record struct EventRow(int Id, int Tenant, long Occurred, int Amount);
public readonly record struct Totals(long Count, long Amount);
public enum AccessPath { Auto, Scan, Thin, Covering }
public enum IndexLayout { None, Thin, Covering, Both }

public sealed class Database : IDisposable
{
    public const int MaxRows = 50_000;
    private readonly string directory;
    public SqliteConnection Connection { get; }

    public Database()
    {
        directory = Path.Combine(Path.GetTempPath(), "cs-index-lab-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        Connection = new SqliteConnection(new SqliteConnectionStringBuilder {
            DataSource = Path.Combine(directory, "events.db"), Pooling = false }.ToString());
        Connection.Open();
        Exec("PRAGMA page_size=4096; PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL;");
        Exec("""
            CREATE TABLE Events(
                Id INTEGER PRIMARY KEY CHECK(Id BETWEEN 1 AND 50000),
                Tenant INTEGER NOT NULL CHECK(Tenant > 0),
                Occurred INTEGER NOT NULL,
                Amount INTEGER NOT NULL CHECK(Amount BETWEEN 0 AND 1000),
                Payload TEXT NOT NULL);
            """);
    }

    public void Exec(string sql)
    {
        using var cmd = Connection.CreateCommand();
        cmd.CommandText = sql;
        cmd.ExecuteNonQuery();
    }

    public static EventRow[] Generate(int n)
    {
        if (n < 0 || n > MaxRows) throw new ArgumentOutOfRangeException(nameof(n));
        return Enumerable.Range(0, n).Select(i =>
            new EventRow(i + 1, i % 10 == 0 ? 2 : 1, i / 2, 1 + i % 97)).ToArray();
    }

    public void Insert(IReadOnlyList<EventRow> rows)
    {
        ArgumentNullException.ThrowIfNull(rows);
        if (rows.Count > MaxRows) throw new ArgumentOutOfRangeException(nameof(rows));
        var ids = new HashSet<int>();
        foreach (var row in rows)
            if (row.Id < 1 || row.Id > MaxRows || row.Tenant <= 0 || row.Amount < 0 || row.Amount > 1000
                || !ids.Add(row.Id)) throw new ArgumentException("Invalid or duplicate row.", nameof(rows));
        using var transaction = Connection.BeginTransaction();
        using var cmd = Connection.CreateCommand();
        cmd.Transaction = transaction;
        cmd.CommandText = "INSERT INTO Events VALUES($id,$tenant,$time,$amount,$payload)";
        foreach (string name in new[] { "$id", "$tenant", "$time", "$amount" })
            cmd.Parameters.Add(name, SqliteType.Integer);
        cmd.Parameters.AddWithValue("$payload", new string('x', 96));
        cmd.Prepare();
        foreach (var row in rows)
        {
            cmd.Parameters["$id"].Value = row.Id;
            cmd.Parameters["$tenant"].Value = row.Tenant;
            cmd.Parameters["$time"].Value = row.Occurred;
            cmd.Parameters["$amount"].Value = row.Amount;
            cmd.ExecuteNonQuery();
        }
        transaction.Commit();
    }

    public void SetIndexes(IndexLayout layout)
    {
        if (!Enum.IsDefined(layout)) throw new ArgumentOutOfRangeException(nameof(layout));
        Exec("DROP INDEX IF EXISTS ix_thin; DROP INDEX IF EXISTS ix_cover;");
        if (layout is IndexLayout.Thin or IndexLayout.Both)
            Exec("CREATE INDEX ix_thin ON Events(Tenant,Occurred)");
        if (layout is IndexLayout.Covering or IndexLayout.Both)
            Exec("CREATE INDEX ix_cover ON Events(Tenant,Occurred,Amount)");
        Exec("ANALYZE");
    }

    public SqliteCommand Query(AccessPath path, int tenant, long start, long end)
    {
        if (tenant <= 0) throw new ArgumentOutOfRangeException(nameof(tenant));
        if (start > end) throw new ArgumentException("Window must satisfy start <= end.");
        string hint = path switch {
            AccessPath.Auto => "", AccessPath.Scan => "NOT INDEXED",
            AccessPath.Thin => "INDEXED BY ix_thin", AccessPath.Covering => "INDEXED BY ix_cover",
            _ => throw new ArgumentOutOfRangeException(nameof(path)) };
        var cmd = Connection.CreateCommand();
        // Only enum-selected identifiers are interpolated; all predicate values are parameters.
        cmd.CommandText = $"""
            SELECT COUNT(*),COALESCE(SUM(Amount),0) FROM Events {hint}
            WHERE Tenant=$tenant AND Occurred >= $start AND Occurred < $end
            """;
        cmd.Parameters.AddWithValue("$tenant", tenant);
        cmd.Parameters.AddWithValue("$start", start);
        cmd.Parameters.AddWithValue("$end", end);
        return cmd;
    }

    public static Totals Read(SqliteCommand cmd)
    {
        using var reader = cmd.ExecuteReader();
        if (!reader.Read()) throw new InvalidOperationException("Missing aggregate row.");
        return new Totals(reader.GetInt64(0), reader.GetInt64(1));
    }

    public Totals Run(AccessPath path, int tenant, long start, long end)
    {
        using var cmd = Query(path, tenant, start, end);
        return Read(cmd);
    }

    public string Plan(AccessPath path, int tenant, long start, long end)
    {
        using var cmd = Query(path, tenant, start, end);
        cmd.CommandText = "EXPLAIN QUERY PLAN " + cmd.CommandText;
        using var reader = cmd.ExecuteReader();
        var lines = new List<string>();
        while (reader.Read()) lines.Add(reader.GetString(3));
        return string.Join(" | ", lines);
    }

    public long Scalar(string sql)
    {
        using var cmd = Connection.CreateCommand(); cmd.CommandText = sql;
        return Convert.ToInt64(cmd.ExecuteScalar());
    }

    public long AllocatedBytes => checked(Scalar("PRAGMA page_count") * Scalar("PRAGMA page_size"));

    public string Version
    {
        get { using var cmd = Connection.CreateCommand(); cmd.CommandText = "SELECT sqlite_version()";
            return (string)cmd.ExecuteScalar()!; }
    }

    public static Totals Reference(IEnumerable<EventRow> rows, int tenant, long start, long end)
    {
        long count = 0, total = 0;
        foreach (var row in rows)
            if (row.Tenant == tenant && row.Occurred >= start && row.Occurred < end)
            { count++; total = checked(total + row.Amount); }
        return new Totals(count, total);
    }

    public void Dispose()
    {
        Connection.Dispose();
        Directory.Delete(directory, true); // Only this instance's generated temporary directory.
    }
}
```

`LessonLab/Program.cs` chọn demo, kiểm tra hoặc thí nghiệm.

```csharp
if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else if (args.Length == 0)
{
    using var db = new Database();
    db.Insert(Database.Generate(2000));
    Console.WriteLine($"SQLite {db.Version}");
    foreach (var layout in new[] { IndexLayout.None, IndexLayout.Thin, IndexLayout.Covering })
    {
        db.SetIndexes(layout);
        var result = db.Run(AccessPath.Auto, 1, 0, 10);
        Console.WriteLine($"{layout}: count={result.Count}, amount={result.Amount}");
        Console.WriteLine(db.Plan(AccessPath.Auto, 1, 0, 10));
    }
}
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

`LessonLab/Checks.cs` đối chiếu mọi khoảng trên dữ liệu nhỏ với điều kiện C# trực tiếp, qua cả bốn cách truy cập. Sau đó xét duy trì index khi update/delete/insert, mốc cực trị, input sai và rollback nguyên batch khi xung đột ID đã có. Thuật toán tham chiếu không dùng SQL hay tìm biên, giảm khả năng bỏ sót cùng một lỗi biên.

```csharp
using Microsoft.Data.Sqlite;

public static class Checks
{
    private static int comparisons;
    private static void Require(bool condition, string message)
    { if (!condition) throw new InvalidOperationException(message); }
    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); } catch (T) { return; }
        throw new InvalidOperationException($"Expected {typeof(T).Name}.");
    }

    private static void Compare(Database db, EventRow[] rows, int tenant, long start, long end)
    {
        var expected = Database.Reference(rows, tenant, start, end);
        foreach (var path in Enum.GetValues<AccessPath>())
        {
            Require(db.Run(path, tenant, start, end) == expected, "Database differs from independent predicate scan.");
            comparisons++;
        }
    }

    public static void Run()
    {
        using var db = new Database();
        db.SetIndexes(IndexLayout.Both);
        Compare(db, [], 1, 0, 10);
        EventRow[] rows = Database.Generate(80);
        db.Insert(rows);
        foreach (int tenant in new[] { 1, 2, 3 })
            for (int start = -1; start <= 41; start++)
                for (int end = start; end <= 41; end++) Compare(db, rows, tenant, start, end);
        Compare(db, rows, 1, long.MinValue, long.MaxValue);
        db.Exec("UPDATE Events SET Tenant=2,Occurred=100,Amount=999 WHERE Id=2");
        rows[1] = new EventRow(2, 2, 100, 999);
        db.Exec("DELETE FROM Events WHERE Id=3");
        rows = rows.Where(r => r.Id != 3).ToArray();
        EventRow[] extra = [new(81, 1, 5, 42), new(82, 1, 5, 0)];
        db.Insert(extra); rows = rows.Concat(extra).ToArray();
        foreach (int tenant in new[] { 1, 2, 3 })
            foreach (var range in new[] { (0L, 40L), (5L, 6L), (100L, 101L), (0L, 0L) })
                Compare(db, rows, tenant, range.Item1, range.Item2);
        db.Insert([new(83, 1, long.MaxValue, 1)]);
        rows = rows.Append(new EventRow(83, 1, long.MaxValue, 1)).ToArray();
        Compare(db, rows, 1, long.MaxValue, long.MaxValue); // Empty, even at the largest endpoint.
        Compare(db, rows, 1, long.MinValue, long.MaxValue); // MaxValue itself is excluded.
        Require(db.Plan(AccessPath.Scan, 1, 0, 10).Contains("SCAN Events"), "Missing forced scan.");
        Require(db.Plan(AccessPath.Thin, 1, 0, 10).Contains("USING INDEX ix_thin"), "Missing thin index.");
        Require(db.Plan(AccessPath.Covering, 1, 0, 10).Contains("USING COVERING INDEX ix_cover"), "Missing covering index.");
        Throws<ArgumentException>(() => db.Run(AccessPath.Auto, 1, 10, 0));
        Throws<ArgumentOutOfRangeException>(() => db.Run(AccessPath.Auto, 0, 0, 1));
        Throws<ArgumentOutOfRangeException>(() => db.Run((AccessPath)100, 1, 0, 1));
        Throws<ArgumentException>(() => db.Insert([new(90, 1, 1, 1), new(90, 1, 2, 1)]));
        Throws<ArgumentException>(() => db.Insert([new(90, 1, 1, 1001)]));
        Throws<ArgumentOutOfRangeException>(() => Database.Generate(Database.MaxRows + 1));
        // A database-level duplicate after a successful insert must roll back the whole batch.
        long before = db.Scalar("SELECT COUNT(*) FROM Events");
        Throws<SqliteException>(() => db.Insert([new(90, 1, 1, 1), new(2, 1, 2, 1)]));
        Require(db.Scalar("SELECT COUNT(*) FROM Events") == before, "Failed batch was partly committed.");
        Require(db.Scalar("SELECT COUNT(*) FROM Events WHERE Id=90") == 0, "Rollback left first row.");
        Console.WriteLine($"PASS: {comparisons} aggregate comparisons; index maintenance, plans and rollback checked.");
    }
}
```

`LessonLab/Experiment.cs` đo cùng truy vấn tổng hợp đã chuẩn bị, luân phiên thứ tự chạy. Thí nghiệm thứ hai dùng database mới với không hoặc một index; thời gian mỗi batch gồm toàn bộ lời gọi Insert, kiểm tra input, transaction và commit. Tạo schema/index và xác minh kết quả nằm ngoài khoảng đo ghi.

```csharp
using System.Diagnostics;
using System.Globalization;

public static class Experiment
{
    private static string F(double value) => value.ToString("F4", CultureInfo.InvariantCulture);
    private static double Median(double[] values) { var copy = values.Order().ToArray(); return copy[copy.Length / 2]; }

    public static void Run()
    {
        EventRow[] rows = Database.Generate(20_000);
        using (var db = new Database())
        {
            db.Insert(rows); db.SetIndexes(IndexLayout.Both);
            Console.WriteLine($"# SQLite={db.Version}; query warmups=3, rounds=9; pageSize=4096; journal=DELETE; synchronous=FULL");
            Console.WriteLine("kind,case,path,n,matches,amount,medianMs,minMs,maxMs,allocatedDbBytes");
            foreach (int end in new[] { 10, 1000, 10000 })
            {
                AccessPath[] paths = [AccessPath.Scan, AccessPath.Thin, AccessPath.Covering];
                var expected = Database.Reference(rows, 1, 0, end);
                var commands = paths.Select(p => db.Query(p, 1, 0, end)).ToArray();
                try
                {
                    foreach (var cmd in commands)
                    { cmd.Prepare(); for (int warmup = 0; warmup < 3; warmup++) Database.Read(cmd); }
                    var times = paths.Select(_ => new double[9]).ToArray();
                    for (int round = 0; round < 9; round++)
                        for (int slot = 0; slot < paths.Length; slot++)
                        {
                            int i = (slot + round) % paths.Length; // Rotate execution order.
                            var watch = Stopwatch.StartNew();
                            Totals result = Database.Read(commands[i]);
                            watch.Stop();
                            if (result != expected) throw new InvalidOperationException("Measured query changed the answer.");
                            times[i][round] = watch.Elapsed.TotalMilliseconds;
                        }
                    for (int i = 0; i < paths.Length; i++)
                    {
                        Console.WriteLine($"query,end={end},{paths[i]},{rows.Length},{expected.Count},{expected.Amount}," +
                            $"{F(Median(times[i]))},{F(times[i].Min())},{F(times[i].Max())},{db.AllocatedBytes}");
                        Console.WriteLine($"# plan end={end} {paths[i]}: {db.Plan(paths[i], 1, 0, end)}");
                    }
                }
                finally { foreach (var cmd in commands) cmd.Dispose(); }
            }
        }
        EventRow[] writeRows = Database.Generate(5000);
        // Fresh databases; schema/index creation excluded, transaction+inserts+commit included.
        IndexLayout[] layouts = [IndexLayout.None, IndexLayout.Thin, IndexLayout.Covering];
        var writes = layouts.Select(_ => new double[5]).ToArray();
        var sizes = new long[layouts.Length];
        for (int round = -1; round < 5; round++) // One unrecorded batch per layout.
            for (int slot = 0; slot < layouts.Length; slot++)
            {
                int i = (slot + Math.Max(round, 0)) % layouts.Length;
                using var db = new Database(); db.SetIndexes(layouts[i]);
                var watch = Stopwatch.StartNew(); db.Insert(writeRows); watch.Stop();
                if (db.Run(AccessPath.Scan, 1, 0, 2500) != Database.Reference(writeRows, 1, 0, 2500))
                    throw new InvalidOperationException("Write experiment changed the answer.");
                if (round >= 0) writes[i][round] = watch.Elapsed.TotalMilliseconds;
                sizes[i] = db.AllocatedBytes;
            }
        for (int i = 0; i < layouts.Length; i++)
            Console.WriteLine($"insert,batch,{layouts[i]},{writeRows.Length},4500," +
                $"{Database.Reference(writeRows, 1, 0, 2500).Amount},{F(Median(writes[i]))}," +
                $"{F(writes[i].Min())},{F(writes[i].Max())},{sizes[i]}");
    }
}
```

Kết quả demo và kiểm tra dự kiến:

```text
SQLite 3.50.4
None: count=18, amount=198
SCAN Events
Thin: count=18, amount=198
SEARCH Events USING INDEX ix_thin (Tenant=? AND Occurred>? AND Occurred<?)
Covering: count=18, amount=198
SEARCH Events USING COVERING INDEX ix_cover (Tenant=? AND Occurred>? AND Occurred<?)
PASS: 11416 aggregate comparisons; index maintenance, plans and rollback checked.
```

Bảy dòng đầu từ demo; dòng cuối từ `--check`. Cả bốn file mã và các khối cài đặt đều đầy đủ. Test cung cấp bằng chứng cho dữ liệu và cách chạy đang xét, chưa chứng minh engine SQLite hay mọi SQL query. Lập luận theo đoạn ở phần 2 giải thích kết quả cần có; SQLite thực thi truy vấn thật.

</details>

Bài sửa lỗi: thay hai phép so sánh Occurred bằng so sánh `(Occurred+0)`. Trên dữ liệu nguyên này, tổng còn đúng không? Plan index gọn có thể mất điều gì, và sửa thế nào?

<details>
<summary>Đáp án</summary>

Cộng số nguyên 0 giữ các giá trị này nên kiểm tra kết quả vẫn có thể qua. Với index thường `(Tenant,Occurred)`, SQLite 3.50.4 không còn dùng biểu thức như khóa thời gian gốc để giới hạn đoạn này: plan ép index gọn còn `(Tenant=?)`, mất biên Occurred. Nhãn vẫn là SEARCH nhưng có thể duyệt cả nhóm tenant rồi mới xét thời gian. Khôi phục so sánh trên khóa gốc bằng Query ở trên. Kiểm tra cả kết quả và điều kiện theo khoảng; test tính đúng chưa bắt mọi lỗi hiệu năng. Index biểu thức có thể hỗ trợ biểu thức cụ thể, nhưng là thiết kế khác cần kiểm tra riêng.

</details>

Nghỉ - 10 phút, rời màn hình.

## 6. Thí nghiệm có kiểm soát: tỷ lệ khớp, bao phủ và ghi

**Thí nghiệm · 45 phút.** Dự đoán tổng xác định, chạy `--experiment`, rồi so thời gian đo lặp mà giữ cùng mục tiêu. **Hoàn thành khi:** tách được ảnh hưởng lên truy vấn khỏi đánh đổi ghi/dung lượng và nêu một yếu tố chưa kiểm soát.

### Thí nghiệm đọc

Giữ cùng database 20.000 dòng, thứ tự dòng, Amount, độ rộng payload, tham số và phép tổng hợp. Dòng sinh có thời điểm `i/2`, tenant 2 khi `i%10==0`, còn lại tenant 1, Amount là `1+i%97`. Cả hai index đã tồn tại; tạo index nằm ngoài đo đọc. Truy vấn không sắp output; thêm ORDER BY sẽ đổi workload.

Với tenant 1 và mốc đầu 0, chỉ đổi mốc cuối 10,1000,10000 giữa các ca. Trong một ca chỉ đổi cách truy cập được ép. Chuẩn bị mọi command, warm up ba lần mỗi command, rồi đo chín lần mỗi cách với thứ tự luân phiên. Thời gian gồm thực thi, đọc hai giá trị tổng hợp và đóng reader. Không tính prepare, tạo database/index, đối chiếu kết quả hay in output. Warm up chủ động tạo thí nghiệm cache ấm, không phải I/O lưu trữ lạnh.

Dự đoán số dòng khớp, tổng Amount và r/N. Dự đoán xu hướng có thể xảy ra, không dự đoán mili giây chính xác.

Dự đoán xác định là gì, và vì sao truy vấn rộng qua index gọn có thể kém scan?

<details>
<summary>Đáp án</summary>

| Mốc cuối | Số dòng khớp r | Tổng Amount | r/N |
|---|---|---|---|
| 10 | 18 | 198 | 0,09% |
| 1000 | 1800 | 87228 | 9% |
| 10000 | 18000 | 881310 | 90% |

Đoạn nhỏ bỏ được hầu hết dòng. Ở 90%, index gọn vừa duyệt index vừa lấy phần lớn dòng bảng; scan có thể bỏ phần tìm cây thêm đó. Bao phủ bỏ bước tra Amount nên kết quả hiệu năng có thể khác index gọn. Đây là dự đoán từ mô hình chi phí, chưa bảo đảm thứ tự thời gian. Chương trình đối chiếu từng kết quả được đo với phép tham chiếu độc lập.

</details>

### Một lần chạy đã quan sát, không phải thời gian bắt buộc

Các median dưới đây được quan sát trong một lần chạy Linux, với runtime đã pin và đúng dữ liệu này. Số dòng/tổng ở trên đều khớp. Đây là ví dụ để diễn giải; máy của bạn và các lần chạy khác có thể cho số khác.

| Mốc cuối | Median scan ms | Median index gọn ms | Median covering ms |
|---|---|---|---|
| 10 | 1,2817 | 0,0176 | 0,0083 |
| 1000 | 1,2587 | 0,2193 | 0,1253 |
| 10000 | 1,8831 | 2,4323 | 1,1849 |

Truy vấn rộng qua index gọn chậm hơn scan trong lần này. CSV còn báo min/max: index gọn rộng 2,1426-2,8583 ms và scan 1,5982-2,7117 ms có phần giao nhau. Bao phủ có lợi trong lần này, nhưng phép đo chưa tìm được ngưỡng đổi chiến lược chung hay latency kỳ vọng. INDEXED BY kiểm soát cách truy cập; nó chưa chứng minh planner không bị ép sẽ chọn gì ở mọi khoảng.

### Thí nghiệm ghi và dung lượng

Dùng database mới với cùng 5.000 dòng, lần lượt không index, chỉ index gọn hoặc chỉ covering. Tạo schema/index nằm ngoài đo. Insert mọi dòng trong một transaction; tính cả kiểm tra input, chuẩn bị command, thực thi và commit. Chạy một batch không ghi số đo cho mỗi cấu hình rồi năm batch được đo, luân phiên thứ tự cấu hình. So median/min/max và dung lượng database cấp phát logic (`page_count*page_size`), không phải RAM tối đa hay toàn bộ journal.

Ví dụ đã quan sát:

| Cấu hình | Median insert ms | Byte database logic |
|---|---|---|
| Không index | 14,0416 | 581632 |
| Index gọn | 16,9022 | 647168 |
| Covering | 15,8131 | 659456 |

Mọi batch cho 4.500 dòng tenant 1 và tổng 219489 trên `[0,2500)`. Thêm index chiếm nhiều dung lượng và có median insert cao hơn không index trong lần này. Dù rộng hơn, covering không chậm hơn index gọn theo median. Năm batch với khoảng số đo giao nhau chưa đủ suy ra thứ hạng ổn định giữa chúng. Database thí nghiệm đọc có cả hai index; dung lượng 2793472 byte lặp lại cho mọi cách đọc, nên các số đó chưa đo kích thước tăng thêm của từng index.

Biến thể: muốn xét đọc lạnh hoặc quyết định triển khai index thì cần đổi gì? Chỉ có median nhỏ hơn đã chứng minh khuyến nghị chưa?

<details>
<summary>Đáp án</summary>

Cần quy trình đọc lạnh riêng kiểm soát cache SQLite, cache hệ điều hành và lưu trữ; chỉ mở lại connection chưa xóa cache trang hệ điều hành. Dùng phân bố tenant, nhóm truy vấn, cột trả về, ghi, kích thước file và concurrency đại diện. Giữ kết quả giống nhau, tính tổng chi phí đọc/ghi/dung lượng và đo lặp cùng độ bất định. Lab chưa kiểm soát lịch CPU, loại trang khỏi cache hệ điều hành, implementation flush hay workload đồng thời. Thời gian chỉ mô tả database local nhỏ, cache ấm; chưa xác lập plan SQL Server, p99 production, bảo đảm lưu bền hay chính sách index nghiệp vụ.

</details>

Nghỉ - 10 phút, rời màn hình.

## 7. Vận dụng: phân trang có thứ tự cần yêu cầu khác

**Vận dụng · 35 phút.** Đổi endpoint từ tổng hợp sang trả hai sự kiện mỗi trang, sắp theo `(Occurred,Id)`. **Hoàn thành khi:** thời điểm trùng không làm bỏ sót hay lặp dòng, và index đáp ứng cả thứ tự lẫn cột cần đọc.

Dùng tám dòng phần 2, tenant 1 và mỗi trang hai dòng. Trang đầu là ID 2,3, kết thúc ở thời điểm 1/ID 3. Vì sao chỉ nhớ thời điểm rồi dùng `Occurred>1` sai? Thiết kế cursor, index và điều kiện trang tiếp. Giải thích điều cần giữ cố định giữa các request.

<details>
<summary>Đáp án - cursor, mã đầy đủ và kiểm tra</summary>

Trang tiếp phải bắt đầu bằng ID 4, cũng ở thời điểm 1. Điều kiện chỉ theo thời điểm bỏ nó, trả 5,6. Giữ `(lastTime,lastId)` và yêu cầu cặp tiếp theo lớn hơn nghiêm ngặt theo thứ tự từ trái sang phải. Id duy nhất tạo thứ tự đầy đủ. Chứng minh cần dữ liệu/snapshot cố định qua các trang; insert/update/delete đồng thời có thể đổi các sự kiện xuất hiện.

Index `(Tenant,Occurred,Id,Amount)` vừa bao phủ trang vừa sắp thời điểm bằng nhau theo Id trước Amount. Index tổng hợp `(Tenant,Occurred,Amount)` chưa cho cùng thứ tự phân định đó. Id được đưa rõ vào khóa dù rowid vẫn được giữ. Điều kiện dưới đây dùng `Occurred>=lastTime` làm biên thô rồi lọc phần thời điểm bằng nhau theo Id; chưa hứa một seek khóa ghép lý tưởng cho mọi cursor. Không cộng thêm vào timestamp nên tránh tràn số.

Trong bản sao lab riêng, giữ Database.cs và thay Program.cs bằng mã đầy đủ dưới đây. Sau restore, chạy `dotnet run --no-restore -c Release --project LessonLab`. Quét/sắp danh sách là tham chiếu độc lập.

```csharp
using Microsoft.Data.Sqlite;

using var db = new Database();
EventRow[] rows = Database.Generate(8);
db.Insert(rows);
db.Exec("CREATE INDEX ix_page ON Events(Tenant,Occurred,Id,Amount)");
var seen = new List<int>();
long lastTime = long.MinValue;
int lastId = 0;
while (true)
{
    using var cmd = PageCommand(db, lastTime, lastId);
    using var reader = cmd.ExecuteReader();
    var page = new List<(int Id, long Time, int Amount)>();
    while (reader.Read()) page.Add((reader.GetInt32(0), reader.GetInt64(1), reader.GetInt32(2)));
    if (page.Count == 0) break;
    foreach (var item in page)
    {
        if (rows.Single(r => r.Id == item.Id).Amount != item.Amount) throw new Exception("Wrong Amount.");
        seen.Add(item.Id);
    }
    (lastId, lastTime, _) = page[^1];
    if (seen.Count > rows.Length) throw new Exception("Cursor repeated a page.");
}
int[] expected = rows.Where(r => r.Tenant == 1).OrderBy(r => r.Occurred).ThenBy(r => r.Id)
    .Select(r => r.Id).ToArray();
if (!seen.SequenceEqual(expected)) throw new Exception("Missing or repeated event.");
using (var plan = PageCommand(db, 1, 3))
{
    plan.CommandText = "EXPLAIN QUERY PLAN " + plan.CommandText;
    using var reader = plan.ExecuteReader();
    var detail = new List<string>();
    while (reader.Read()) detail.Add(reader.GetString(3));
    if (!detail.Any(s => s.Contains("USING COVERING INDEX ix_page")) || detail.Any(s => s.Contains("TEMP B-TREE")))
        throw new Exception("Unexpected pinned-version page plan.");
}
Console.WriteLine($"PASS: keyset pages ids={string.Join(",", seen)}; no skipped duplicate timestamp.");

static SqliteCommand PageCommand(Database db, long time, int id)
{
    var cmd = db.Connection.CreateCommand();
    cmd.CommandText = """
        SELECT Id,Occurred,Amount FROM Events INDEXED BY ix_page
        WHERE Tenant=$tenant AND Occurred >= $time AND (Occurred > $time OR Id > $id)
        ORDER BY Occurred,Id LIMIT $take
        """;
    cmd.Parameters.AddWithValue("$tenant", 1);
    cmd.Parameters.AddWithValue("$time", time);
    cmd.Parameters.AddWithValue("$id", id);
    cmd.Parameters.AddWithValue("$take", 2);
    return cmd;
}
```

Kết quả dự kiến: `PASS: keyset pages ids=2,3,4,5,6,7,8; no skipped duplicate timestamp.` Điều kiện theo khoảng cùng so sánh cursor nghiêm ngặt lấy mỗi cặp còn lại đúng một lần, không trả lại cặp cursor. ORDER BY rõ ràng xác định yêu cầu; LIMIT chỉ cắt đoạn sau đã sắp đó. Snapshot ổn định là giả định, chưa được implement qua các HTTP request. Kiểm tra plan theo phiên bản lab không phải bộ phân tích plan cho production.

Với SQL Server, khóa tương ứng có thể là `(TenantId,OccurredUtc,EventId) INCLUDE(Amount)` vì Amount không cần tham gia sắp. Đây là ứng viên thiết kế, chưa là execution plan SQL Server đã xác minh. Đổi từ tổng hợp sang phân trang có thứ tự cho thấy phải xét lại trạng thái, điều kiện, cột cần đọc và index cùng nhau.

</details>

## 8. Tổng hợp và tự kiểm tra

**Tổng hợp · 45 phút.** Tự dựng lại mô hình khi đóng trang, rồi viết một quyết định index và một phép thử có thể bác bỏ. **Hoàn thành khi:** quyết định nêu workload, yêu cầu kết quả, bằng chứng và điều chưa chắc.

1. Vì sao hai lần tìm biên đếm nhanh khoảng trong mảng, còn phép tổng hợp của lab vẫn xét các Amount khớp?

<details>
<summary>Đáp án</summary>

Vị trí trong mảng cho thứ hạng nên lấy hiệu đếm được phần tử mà chưa duyệt chúng. Cursor index SQLite thông thường không cung cấp cách biểu diễn đó; tổng còn phụ thuộc các giá trị khớp thật. Không có tổng lưu sẵn thì seek chỉ tìm nơi bắt đầu, vẫn cần duyệt và tra bảng nếu thiếu giá trị.

</details>

2. Phản ví dụ nào bác bỏ “SEARCH luôn nhanh hơn SCAN”?

<details>
<summary>Đáp án</summary>

Phép tổng hợp qua index gọn khớp 90% có median lớn hơn scan được ép trên cùng input/output trong lần quan sát. Nó duyệt index rồi lấy Amount từ bảng; scan bỏ bước đi qua index thêm đó. Đây là phản ví dụ đo được cho nhận định tuyệt đối, chưa là định lý scan thắng trên 90% ở mọi hệ thống. Đổi độ bao phủ hoặc thứ tự có thể đổi kết quả.

</details>

3. Tách giả định, dự đoán, quan sát và suy luận của thí nghiệm.

<details>
<summary>Đáp án</summary>

Giả định: dữ liệu giả lập cố định, số nguyên có cận, một connection, cấu hình trang/journal đã nêu và cùng nghĩa tổng hợp. Dự đoán: tổng xác định, lợi ích của đoạn nhỏ và khả năng tốn thêm khi đoạn rộng không bao phủ. Quan sát: plan thật, tổng CSV đã đối chiếu, thời gian đo lặp và trang cấp phát. Suy luận: implementation tái hiện các cơ chế và đánh đổi đọc/ghi trên workload này. Chưa xác lập I/O lạnh, concurrency production hay hành vi SQL Server.

</details>

4. Viết một quyết định triển khai có căn cứ và phép thử có thể làm đổi quyết định đó.

<details>
<summary>Đáp án</summary>

Với tổng hợp theo tenant/thời gian, thử index bao phủ bắt đầu bằng tenant nếu lợi ích đọc trên dữ liệu đại diện bù được dung lượng và công việc ghi. Xác minh cùng tổng, đọc plan thật không bị ép, so với scan/index đã có bằng phép đo lặp. Bỏ hoặc sửa ứng viên nếu throughput ghi, ngân sách bộ nhớ/dung lượng, latency khoảng rộng hay cột cần đọc mới không chấp nhận được. Index phân trang cần yêu cầu thứ tự riêng. Không biến kết quả lab hay bảo đảm knapsack 1/2 của Bài 04 thành bảo đảm chất lượng optimizer.

</details>

## Nguồn và quyền sử dụng

- Tài liệu SQLite: [Query Planning](https://www.sqlite.org/queryplanner.html), mục 1.4, 1.6, 1.7; [EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html), mục 1.1; [optimizer overview](https://www.sqlite.org/optoverview.html), mục 2 và skip-scan; [INDEXED BY](https://www.sqlite.org/lang_indexedby.html); [file format, trang B-tree](https://www.sqlite.org/fileformat.html#b_tree_pages).
- Source SQLite tag `version-3.50.4` tại commit GitHub `8ed5e7365e6f12f427910188bbf6b254daad2ef6`; link implementation có giới hạn dòng ở phần 4. Hash bản mirror GitHub khác hash Fossil do `sqlite_source_id()` trả; phiên bản engine ở đây trùng tag. [Thông báo public domain của SQLite](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/LICENSE.md). Lab không sao chép code SQLite.
- [Tài liệu thiết kế index SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17) hỗ trợ phần ứng dụng, khác biệt B+ tree và nghĩa INCLUDE. Chưa reproduce plan hay số đo SQL Server.
- [Giới thiệu Microsoft.Data.Sqlite](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/) giải thích provider C#. Project và lock file pin phiên bản package; dependency giữ điều khoản giấy phép riêng.
- Nội dung bài tự viết theo CC BY 4.0; mã C# giảng dạy tự viết theo MIT, có trong ZIP.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 02 - Tìm biên](../boundary-search/lesson.md) - Ôn khoảng nửa mở, biên trùng và phép lấy hiệu thứ hạng.
- [Bài 04 - Quy hoạch động và xấp xỉ](../2026-10-08-dp-approximation/lesson.md) - Ôn yêu cầu trạng thái, tách mô hình khỏi số đo.
- [Hướng dẫn lab C#](../../../labs/index-query-plans/dotnet/README.vi.md) - Dependency được pin, kiểm tra, phép đo và mã nguồn.

---

[← Bài trước: Bài 04 - Quy hoạch động và xấp xỉ: chọn công việc trong một ngân sách](../2026-10-08-dp-approximation/lesson.md) · [Danh sách bài học](../../README.md)
<!-- LESSON_NAVIGATION_END -->
