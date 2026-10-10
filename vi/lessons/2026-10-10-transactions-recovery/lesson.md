# Bài 06 - Transaction và phục hồi: ghi đúng vẫn có thể dùng quyết định đã cũ

[English](../../../lessons/2026-10-10-transactions-recovery/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/transactions-recovery/dotnet-lab.zip)

Dịch vụ tồn kho có mười đơn vị. Hai request cùng đọc mười, rồi đặt giữ bảy và năm. Mỗi UPDATE thành công, số tồn lưu trong bảng vẫn không âm, nhưng hệ thống đã hứa giao mười hai đơn vị. Ta sẽ tái hiện lịch đó, sửa ranh giới ra quyết định và mở lại database sau khi dừng tiến trình ghi trước hoặc sau commit.

**Mục tiêu:** phân biệt transaction nguyên tử với quyết định nghiệp vụ hợp lệ, phát hiện lần đọc đã cũ, lập luận về phép đặt giữ có kiểm tra và diễn giải trace crash/phục hồi có giới hạn. Planner chọn transaction sau index. Bài kế thừa tham số SQL, đối chiếu kết quả độc lập và cách tách mô hình khỏi quan sát; sẽ bổ sung ranh giới transaction, isolation, snapshot và WAL.

## Khái niệm chính

- **Công việc nguyên tử.** Trừ tồn và lưu bản ghi xác nhận đặt giữ phải đi cùng nhau. Commit công bố cả nhóm; rollback bỏ thay đổi của nhóm. Tính nguyên tử chưa chứng minh số lượng chọn từ lần đọc trước còn hợp lệ.
- **Isolation và lịch thực thi.** Hai client có thể đọc trước khi bên nào ghi. Lịch thực thi mô tả cách xen kẽ đó. Isolation áp dụng cho transaction database, nên trước hết phải xác định lần đọc/ghi nào thuộc cùng transaction.
- **Quyết định đã cũ và kiểm tra version.** Request đọc version 0 không được âm thầm ghi đè tồn đã chuyển sang version 1. Phép ghi có thể kiểm tra cả version dự kiến lẫn số tồn hiện tại, rồi báo xung đột thay vì đoán.
- **Snapshot.** Reader dùng WAL có thể vẫn thấy tồn mười trong khi client khác đã commit tồn ba. Góc nhìn ổn định này hữu ích, nhưng SQLite sẽ từ chối nâng snapshot đọc cũ đó thành bên ghi.
- **Phục hồi và biên commit.** WAL ghi trang đã đổi cùng dấu commit. Sau crash của tiến trình, các trang ngoài biên đã commit hợp lệ cuối cùng không được xuất hiện trong kết quả. Commit khác việc chép trang về file database bằng checkpoint.

Bạn có thể chỉ đọc mọi bảng chạy, chương trình đầy đủ và lời giải. Giới hạn cài đặt trong 15 phút của phần lab rồi chuyển sang đọc nếu cần. Lab tạo database tạm riêng và chỉ dừng tiến trình con do nó tạo; không cần server hay dữ liệu cá nhân.

## 1. Ôn lại và ranh giới còn thiếu

**Ôn tập · 20 phút.** Dựng lại hai cơ chế planner chọn, rồi xác định điều kiện đúng mới. **Hoàn thành khi:** nêu được nhãn plan hay giá trị cũ đã lưu chưa cung cấp bằng chứng gì.

1. Từ Bài 05: vì sao SEARCH có thể tốn hơn SCAN khi tổng hợp trên đoạn rộng không bao phủ?

<details>
<summary>Đáp án</summary>

Seek định vị đoạn; duyệt phần tử khớp và tra Amount còn thiếu vẫn tốn công. Với đoạn rộng, scan có thể bỏ đường đi thêm đó. Độ bao phủ, thứ tự và cache ảnh hưởng phép so, nên nhãn plan chưa xếp hạng runtime. Tương tự, tra tồn nhanh chưa chứng minh giá trị còn mới khi lần ghi sau sử dụng nó.

</details>

2. Từ Bài 03: vì sao heap có thể chứa hai entry cho một đỉnh, và xử lý entry stale thế nào? Nêu các cận.

<details>
<summary>Đáp án</summary>

Mỗi cải thiện nghiêm ngặt thêm chi phí mới thay vì giảm key cũ. Bỏ entry có chi phí khác dist[node]. Tối đa E cải thiện cho thời gian O(V+E log(E+2)), bộ nhớ tìm kiếm O(V+E), với mảng kề và phép toán nguyên có chi phí giới hạn. Điểm nối hôm nay là đối chiếu thông tin cũ với trạng thái hiện tại; kiểm tra version database không phải chứng minh đường đi ngắn nhất.

</details>

3. Nếu transaction trừ tồn và thêm bản ghi xác nhận cùng nhau, chỉ điều đó đã ngăn hai request đặt giữ vượt số tồn ban đầu chưa?

<details>
<summary>Đáp án</summary>

Chưa. Tính nguyên tử giữ từng cặp thay đổi cùng xảy ra hoặc cùng bị bỏ. Điều kiện nghiệp vụ còn đòi hỏi quyết định dùng số tồn hiện tại hợp lệ. Lần đọc cũ nằm ngoài transaction đó vẫn có thể cho phép ghi sai. CHECK giữ Available không âm chưa phát hiện mọi lượng đã hứa trong các dòng khác.

</details>

## 2. Lịch thực thi, bất biến và quyết định có kiểm tra

**Nền tảng · 50 phút.** Chạy ví dụ mười đơn vị và suy ra cách sửa. **Hoàn thành khi:** giải thích được từng commit, xung đột và rollback mà không dựa vào thời gian chờ.

### Chạy nghiệp vụ trước

Database có một dòng Stock: Available=10, Version=0; bảng Reservations rỗng. T1 muốn bảy đơn vị, T2 muốn năm. Mỗi client đọc trước bằng autocommit, giữ giá trị trong bộ nhớ ứng dụng, rồi bắt đầu transaction ghi riêng. Hai việc ghi là cập nhật tồn và thêm bản ghi xác nhận.

Dự đoán tồn cuối và tổng đã đặt giữ khi dùng `Available = oldAvailable - quantity`. Quy tắc nào bị vi phạm?

<details>
<summary>Đáp án</summary>

| Bước | T1 | T2 | Tồn đã commit | Tổng đặt giữ |
|---|---|---|---|---|
| 1 | Đọc (10,0), ngoài transaction ghi | | 10 | 0 |
| 2 | | Đọc (10,0), ngoài transaction ghi | 10 | 0 |
| 3 | Bắt đầu; đặt 10-7=3; xác nhận A=7; commit | | 3 | 7 |
| 4 | | Bắt đầu; đặt từ số cũ 10-5=5; xác nhận B=5; commit | 5 | 12 |

Hai transaction ghi đều nguyên tử và chạy lần lượt. Lần ghi sau dùng giá trị cũ ở ứng dụng để ghi đè phần trừ trước. Đây là mất cập nhật ở mức nghiệp vụ, không chứng minh SQLite âm thầm cho snapshot đọc cũ nâng lên ghi. Tồn không âm vẫn qua CHECK, nhưng 5+12=17 thay vì mười ban đầu. Không thứ tự tuần tự hợp lệ nào nhận cả hai request: phải từ chối một bên.

</details>

### Nêu bất biến và phạm vi transaction

Giả định không nhập thêm hàng, hủy đặt giữ hay ghi ngoài lab trong ca đang xét. Gọi A là tồn hiện tại, S là tổng lượng trong các xác nhận đã commit, I là tồn ban đầu. Ví dụ dẫn tới **A+S=I**, cùng A>=0. Mỗi xác nhận phải tương ứng đúng một lần trừ đã commit. Mọi bên ghi phải theo quy tắc; database không tự suy ra nghĩa nghiệp vụ của UPDATE tùy ý.

Tính nguyên tử giữ mọi thay đổi cùng xảy ra hoặc cùng bị bỏ. Tính nhất quán đòi hỏi ràng buộc và thao tác ứng dụng giữ các quy tắc đã chọn. Isolation giới hạn tương tác giữa các transaction. Tính bền vững xét tác động đã commit dưới mô hình lỗi đã nêu. Đó là các tính chất ACID. Một mức isolation là bảo đảm được chọn, chưa hứa mọi workflow ứng dụng qua nhiều transaction tương đương chạy tuần tự.

Lịch tuần tự chạy từng nghiệp vụ trọn vẹn. Để giải thích kết quả có kiểm soát, so với thứ tự hợp lệ T1 rồi T2. T1 commit bảy, còn ba; T2 xét lại ba và từ chối năm. Đảo thứ tự có thể cho đáp án hợp lệ khác. Lab kiểm tra thứ tự đã chọn, không chứng minh tính công bằng.

### Đối chiếu thông tin cũ ngay khi ghi

Version là số nguyên ứng dụng tăng sau mỗi thay đổi Stock được nhận. Nó không phải vị trí WAL nội bộ của SQLite hay kiểu rowversion nhị phân của SQL Server. UPDATE có kiểm tra chỉ trừ từ tồn hiện tại khi version dự kiến khớp và Available hiện tại đủ. Thêm xác nhận và UPDATE thuộc cùng transaction.

```sql
UPDATE Stock SET Available=Available-$q,Version=Version+1
WHERE Id=1 AND Version=$v AND Available >= $q;
```

UPDATE không đổi dòng nào nghĩa là điều kiện chưa cho phép ghi. Trong lab, đó là xung đột; đọc mới có thể cho biết tồn không đủ. Không thêm xác nhận sau kết quả không đổi dòng. Rollback, đọc lại và xét lại toàn bộ quyết định trong chính sách retry có cận. Gửi lại nguyên giá trị đã cũ chưa phải xét lại.

Lập luận theo bất biến: ban đầu A=I, S=0. Từ chối/xung đột không đổi chúng. Lượng q được nhận thỏa A>=q; commit đổi A thành A-q và S thành S+q cùng nhau, giữ tổng và A không âm. Lỗi giữa hai lần ghi rollback cả hai. Request lặp đã có xác nhận lưu bền không đổi gì. Tăng Version làm các lần đọc cũ không còn khớp. Lập luận giả định một mặt hàng và mọi thay đổi theo quy tắc transaction này; chưa chứng minh ràng buộc nhiều dòng tùy ý.

Vì sao bắt đầu transaction ghi bằng BEGIN IMMEDIATE chưa sửa được cách ghi mù?

<details>
<summary>Đáp án</summary>

IMMEDIATE lấy quyền ghi trước các statement của nó, nhưng lần đọc trước ở ứng dụng đã nằm ngoài transaction đó. Cho các lần ghi sau chạy lần lượt chưa làm mới giá trị cũ. Điều kiện version/tồn gắn quyền ghi với trạng thái database hiện tại. Bắt đầu transaction trước lần đọc và giữ quyền ghi là cách khác, nhưng chặn các bên ghi lâu hơn.

</details>

Vì sao retry phải đọc lại?

<details>
<summary>Đáp án</summary>

Retry phải dùng trạng thái vừa đọc. Với request năm, đọc tồn ba làm quyết định chuyển sang từ chối; request hai có thể thành công. Dữ liệu cũ chưa hỗ trợ quyết định mới đó. Writer chen vào vẫn có thể gây xung đột tiếp.

</details>

Nghỉ - 10 phút, rời màn hình.

## 3. Đọc bảo đảm isolation và phục hồi

**Đọc tài liệu · 45 phút.** Chú thích bảo đảm chính thức theo các lịch đang xét. **Hoàn thành khi:** mỗi nhận định có nguồn và ranh giới rõ ràng.

Đọc [Isolation](https://www.sqlite.org/isolation.html) của SQLite, phần connection riêng và ví dụ WAL; [WAL, mục 2.1-2.3](https://www.sqlite.org/wal.html), về checkpoint, đồng thời và hiệu năng; [transaction, mục 2.1-2.2](https://www.sqlite.org/lang_transaction.html), về đọc/ghi và DEFERRED/IMMEDIATE. Đọc [deferred transaction của Microsoft.Data.Sqlite](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/transactions#deferred-transactions). Shared cache kết hợp read_uncommitted là ngoại lệ về khả năng thấy thay đổi giữa connection của SQLite; lab dùng cache riêng.

### Góc nhìn ổn định chưa phải phép ghi từ dữ liệu mới

Transaction DEFERRED hoãn lấy quyền ghi. SELECT đầu tiên xác lập góc nhìn đọc. Với WAL, bên ghi có thể nối thêm trang đã commit trong khi reader giữ snapshot cũ. Transaction đọc của lab thấy mười trước và sau khi writer commit tồn ba. Nâng transaction cũ đó lên ghi bị SQLITE_BUSY_SNAPSHOT, mã mở rộng 517 trên engine đã pin. Kết thúc transaction cũ rồi mới retry; chờ thêm chưa làm snapshot của nó mới hơn.

Chạy từng bước ca này và giải thích khác biệt với đặt giữ ghi mù.

<details>
<summary>Đáp án</summary>

| Bước | Reader R | Writer W | Tồn đã commit hiện tại |
|---|---|---|---|
| 1 | BEGIN DEFERRED; SELECT -> 10 | | 10 |
| 2 | Giữ transaction mở | Đặt giữ 7 có kiểm tra; commit | 3 |
| 3 | SELECT -> vẫn 10 | | 3 |
| 4 | Thử UPDATE -> lỗi 517 | | 3 |
| 5 | ROLLBACK; SELECT mới -> 3 | | 3 |

Khác ví dụ ghi mù, lần đọc và thử ghi của R thuộc cùng transaction database còn mở. SQLite từ chối nâng snapshot cũ lên ghi. Workflow ghi mù đã kết thúc lần đọc trước, rồi mở transaction ghi mới và chỉ mang theo giá trị ứng dụng chưa kiểm tra. Hai tình huống cùng tồn tại mà không mâu thuẫn bảo đảm SQLite. SQLITE_BUSY do tranh quyền ghi và SQLITE_BUSY_SNAPSHOT do góc nhìn cũ không phải cùng tình huống retry.

</details>

### Trang đã đổi, commit và checkpoint

WAL (Write-Ahead Log) của SQLite là file log riêng giữ các trang đã đổi. Trang thay đổi còn giữ trong bộ nhớ gọi là trang bẩn; có thể đẩy vào WAL trước commit. Một frame WAL lưu một trang như vậy cùng phần header. Frame commit hợp lệ ghi kích thước database sau transaction. Phục hồi nhận biết biên đã commit hợp lệ cuối cùng; phần đuôi chưa hoàn tất không phải transaction đã commit. Checkpoint sau đó chép các trang đã commit đủ điều kiện vào file database. Commit có thể thành công trong WAL trước lần chép đó.

Reader giữ một mốc kết thúc nên lần đọc dài có thể cản checkpoint và giữ dung lượng WAL. SQLite WAL cho reader chạy cùng một writer, không cho nhiều writer đồng thời. Nó cần phối hợp qua bộ nhớ chia sẻ trên máy; không phải giao thức filesystem mạng hay replication phân tán.

Viết một dòng nhận định/bằng chứng/giới hạn cho snapshot, nâng snapshot cũ lên ghi và phục hồi phần đã commit.

<details>
<summary>Đáp án</summary>

| Nhận định | Bằng chứng | Giới hạn |
|---|---|---|
| Reader WAL giữ góc nhìn của mình | Ví dụ Isolation và mốc kết thúc trong WAL 2.2 | Có thể cũ so với request sau; đọc dài ảnh hưởng checkpoint |
| Góc nhìn đọc cũ không nâng lên ghi sau commit khác | Ví dụ BUSY_SNAPSHOT của Isolation | Transaction ứng dụng mới dùng giá trị cũ vẫn cần kiểm tra riêng |
| Nhóm WAL đã commit có thể phục hồi sau crash tiến trình | Mô tả commit/checkpoint của WAL và lab dưới đây | Hai điểm dừng chưa kiểm tra mất điện, ghi bị xé, mọi VFS hay thiết bị |

Microsoft.Data.Sqlite hướng dẫn retry toàn bộ deferred transaction sau khi nâng lên ghi thất bại. [Pragma synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous) của SQLite nêu điều kiện bền vững theo mode và đồng bộ. Lab chọn FULL, nhưng dừng tiến trình vẫn để hệ điều hành hoạt động; chưa kiểm tra thiết bị lưu trữ lỗi.

</details>

## 4. Quyết định trong dự án và đọc source SQLite tại commit cố định

**Đọc mã nguồn · 45 phút.** Đưa đặt giữ vào API và đọc ba phần WAL có giới hạn. **Hoàn thành khi:** tách điều source bảo đảm khỏi quy tắc ứng dụng mà source không tự suy ra.

### Endpoint tồn kho ASP.NET

Gắn tham số cho mã request, mặt hàng và số lượng, kiểm tra chúng, rồi đặt thay đổi tồn cùng xác nhận lưu bền trong một transaction database. Không giữ transaction khi chờ người dùng Angular hay dịch vụ thanh toán ngoài. Giá trị UI đã cũ là đề nghị, không phải số tồn có thẩm quyền. Server phải xét lại ngay khi ghi.

SQL Server có thể dùng UPDATE có điều kiện, xét số dòng thay đổi và lưu xác nhận nguyên tử. [Hướng dẫn transaction](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17), phần ACID, kiểm soát đồng thời và isolation theo phiên bản dòng, phân biệt góc nhìn mỗi statement của READ COMMITTED với RCSI và góc nhìn transaction của SNAPSHOT. Phải xét cấu hình database và bảo đảm của engine; chép mã lỗi 517 hay định dạng WAL SQLite chưa xác lập hành vi SQL Server.

Diễn đạt phép ghi có kiểm tra bằng T-SQL thế nào, và điều gì chưa được xác minh?

<details>
<summary>Đáp án</summary>

Đây là phần phác thảo thiết kế, không phải lab chạy được. Nó cần bảng/tham số có kiểu phù hợp và khóa request duy nhất; chưa chạy trên SQL Server. Phải xét @@ROWCOUNT ngay sau UPDATE. Code production còn cần tra request lặp, xử lý payload không khớp, lỗi, quyền truy cập và chính sách isolation đã chọn.

```tsql
SET XACT_ABORT ON;
BEGIN TRANSACTION;
UPDATE dbo.Stock SET Available=Available-@Quantity, Version=Version+1
WHERE Id=@ItemId AND Version=@ExpectedVersion AND Available>=@Quantity;
IF @@ROWCOUNT = 1
    INSERT dbo.Reservations(RequestId,Quantity) VALUES(@RequestId,@Quantity);
ELSE
BEGIN
    ROLLBACK TRANSACTION;
    THROW 50001, 'Conflict or insufficient stock', 1;
END;
COMMIT TRANSACTION;
```

XACT_ABORT làm nhiều lỗi runtime hủy transaction, chưa thay thế xử lý exception đúng ở ứng dụng. Version nguyên này là lựa chọn thiết kế, không phải rowversion tự động của SQL Server. Plan, chặn lẫn nhau, retry và throughput còn cần chạy trên SQL Server. Implementation đã kiểm tra dưới đây dùng C# và SQLite để thí nghiệm transaction/crash chạy được khi chưa có server.

</details>

### Vì sao database nhúng cần cơ chế này?

WAL của SQLite cho ứng dụng nhúng giữ reader hoạt động trong khi writer commit. [Phần tổng quan source](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L15-L133) mô tả frame, dấu commit, mốc kết thúc của reader và wal-index để tránh quét WAL có thể lớn nhiều megabyte cho mỗi trang cần đọc. Đó là bài toán sản phẩm: đọc nhanh vẫn phải chọn phiên bản đã commit. Wal-index suy ra từ log giúp tra cứu, không phải nguồn lưu bền quyết định dữ liệu.

Dùng commit bất biến **8ed5e7365e6f12f427910188bbf6b254daad2ef6**, tag version-3.50.4, trùng phiên bản engine:

1. [sqlite3WalBeginWriteTransaction, dòng 3664-3725](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L3664-L3725) lấy khóa writer duy nhất, so header WAL của reader với header hiện tại và từ chối snapshot cũ.
2. [walFrames, dòng 4138-4188](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L4138-L4188) đặt dấu kích thước database ở frame commit cuối và xử lý đồng bộ commit theo cấu hình. Nó chưa nói mọi lần đẩy trang bẩn vào WAL đều là commit.
3. [walIndexRecover, dòng 1481-1528](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L1481-L1528) đọc/giải mã frame, dừng khi dữ liệu không hợp lệ và tiến header đã commit khi nTruncate khác 0. [walDecodeFrame, dòng 1000-1045](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/src/wal.c#L1000-L1045) kiểm tra salt, số trang và checksum tích lũy.

**Đã xác minh:** một writer, từ chối header cũ, đánh dấu commit và dựng lại biên đã commit. **Suy luận thiết kế:** transaction ngắn giảm thời gian endpoint giữ tài nguyên; điều kiện version bảo vệ quyết định đã cũ ở ngoài transaction. Các đoạn này chưa chứng minh mọi đường lỗi pager/VFS hay bất biến nghiệp vụ của ta. SQLite chấp nhận đánh đổi một writer/phối hợp local; lab chưa đo concurrency tối đa.

Sau crash có frame chưa hoàn tất, vì sao chỉ chiều dài file chưa cho biết phải trả số dư nào?

<details>
<summary>Đáp án</summary>

Chiều dài cho biết số byte, chưa cho biết biên đã commit hợp lệ. Frame cần được kiểm tra; chỉ dấu commit hợp lệ mới tiến trạng thái đã commit có thể đọc. Trang đã đẩy ra từ transaction chưa commit có thể tồn tại vật lý nhưng không xuất hiện sau khi mở lại. Lab kiểm tra trạng thái SQL kết quả và quan sát WAL tồn tại, không tự giải mã/kiểm tra mọi frame nhị phân. SQLite thực hiện việc phục hồi đó.

</details>

Ăn trưa và nghỉ - 30 phút.

## 5. Lab C#: hai client và tiến trình ghi bị dừng

**Lab · 75 phút.** Chạy lịch có kiểm soát, sửa lỗi dùng giá trị cũ và kiểm tra rollback/phục hồi. **Hoàn thành khi:** kiểm tra qua và xác định được chính xác ranh giới transaction/lỗi.

Implement thao tác tồn cùng xác nhận, rồi để hai client đọc trước khi T1 commit và T2 ghi. Chỉ giữ xác nhận khi phần trừ tồn commit. Kiểm tra transaction đọc còn mở và cả hai điểm crash. Dùng lời giải đầy đủ nếu cài đặt hoặc implementation vượt thời gian đã dành.

<details>
<summary>Đáp án - toàn bộ lab chạy được</summary>

Dùng SDK **10.0.401** (tắt roll-forward cho SDK/runtime), **net10.0**, **Microsoft.Data.Sqlite 10.0.9**, **SQLitePCLRaw.bundle_e_sqlite3 3.0.3** và lock file trong repo. Engine trả **SQLite 3.50.4**. Restore đầu cần NuGet; các lần no-restore sau có thể dùng package đã cache. Không cần database server.

Giải nén vào `dotnet`, hoặc dùng `labs/transactions-recovery/dotnet` trong checkout. Muốn dựng từ bài cần mọi file dưới đây. [Hướng dẫn lab](../../../labs/transactions-recovery/dotnet/README.vi.md) có link từng source. Database nằm trong thư mục tạm tự sinh; ZIP chỉ chứa mã và cấu hình.

Task.Run khởi chạy task của mỗi client; mỗi bên sở hữu connection riêng. Các cổng TaskCompletionSource kiểm soát read1, read2 và written1. Await chờ bước đã được xác nhận, không chờ một khoảng đoán trước. Hai client cùng tồn tại trong khi các statement theo R1,R2,W1,W2; chưa có hai writer SQLite ghi đồng thời. Timeout của cổng phát hiện phối hợp lỗi, không phải chính sách retry khóa.

`dotnet/global.json`:

<!-- lab-file: global.json -->
```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
}
```

`dotnet/LessonLab/LessonLab.csproj`:

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

<!-- lab-file: LessonLab/packages.lock.json -->
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

Lab giới hạn tồn ban đầu 0-1000, số lượng 1-1000 và mã request không trắng, tối đa 100 ký tự. Cấu hình rõ cache riêng, Pooling=false, WAL, synchronous=FULL, wal_autocheckpoint=0. DefaultTimeout=1 giới hạn chờ busy của provider; 0 nghĩa là không timeout. Schema giới hạn Version; số lần trừ có kiểm tra thành công không vượt tồn ban đầu. Reset chỉ chạy ngoài task client; chưa mô hình hóa nhập thêm hoặc hủy đặt giữ.

Retry có kiểm soát cho phép một lần thử từ dữ liệu mới. Nó đủ cho thứ tự hai client này, chưa là thuật toán tranh chấp tổng quát. Conflict không phải thành công; bên gọi production cần chính sách có cận và cách báo kết quả chưa giải quyết. Exec/Scalar chỉ nhận SQL cố định trong bài; giá trị request là tham số.

`LessonLab/Store.cs`. Store tạo schema, gắn tham số và giữ phần trừ cùng xác nhận trong transaction ghi IMMEDIATE. Nhánh ghi mù cố ý sai; nhánh có kiểm tra xét version/tồn hiện tại. Tra xác nhận đã có trước khi xét nhận request để request lặp khớp không trừ thêm.

<!-- lab-file: LessonLab/Store.cs -->
```csharp
// Original MIT teaching code; SQLite implementation is linked, not copied.
using Microsoft.Data.Sqlite;

public readonly record struct StockView(int Available, int Version);
public enum Outcome { Committed, Rejected, Conflict, Replayed }
public enum Strategy { Blind, Guarded, Retry }

public sealed class Store : IDisposable
{
    private readonly string directory = Path.Combine(Path.GetTempPath(), "cs-tx-lab-" + Guid.NewGuid().ToString("N"));
    public string FilePath { get; }
    public Store(int initial = 10)
    {
        if (initial < 0 || initial > 1000) throw new ArgumentOutOfRangeException(nameof(initial));
        Directory.CreateDirectory(directory);
        FilePath = Path.Combine(directory, "stock.db");
        using var c = Open(FilePath);
        Exec(c, """
            PRAGMA page_size=4096; PRAGMA journal_mode=WAL;
            CREATE TABLE Stock(Id INTEGER PRIMARY KEY CHECK(Id=1),
              Available INTEGER NOT NULL CHECK(Available BETWEEN 0 AND 1000),
              Version INTEGER NOT NULL CHECK(Version BETWEEN 0 AND 1000));
            CREATE TABLE Reservations(Request TEXT PRIMARY KEY NOT NULL,
              Quantity INTEGER NOT NULL CHECK(Quantity BETWEEN 1 AND 1000));
            CREATE TABLE Accounts(Id INTEGER PRIMARY KEY, Balance INTEGER NOT NULL CHECK(Balance BETWEEN 0 AND 200));
            INSERT INTO Accounts VALUES(1,100),(2,100);
            CREATE TABLE Noise(Id INTEGER PRIMARY KEY, Payload BLOB NOT NULL);
            """);
        Reset(initial);
    }
    public static SqliteConnection Open(string path)
    {
        var c = new SqliteConnection(new SqliteConnectionStringBuilder {
            DataSource = path, Pooling = false, Cache = SqliteCacheMode.Private, DefaultTimeout = 1 }.ToString());
        c.Open();
        Exec(c, "PRAGMA synchronous=FULL; PRAGMA wal_autocheckpoint=0;");
        return c;
    }
    public static void Exec(SqliteConnection c, string sql, SqliteTransaction? tx = null)
    {
        using var cmd = c.CreateCommand(); cmd.Transaction = tx; cmd.CommandText = sql; cmd.ExecuteNonQuery();
    }
    public static long Scalar(SqliteConnection c, string sql, SqliteTransaction? tx = null)
    {
        using var cmd = c.CreateCommand(); cmd.Transaction = tx; cmd.CommandText = sql;
        return Convert.ToInt64(cmd.ExecuteScalar());
    }
    public static string Engine(SqliteConnection c)
    {
        using var cmd = c.CreateCommand(); cmd.CommandText = "SELECT sqlite_version()";
        return (string)cmd.ExecuteScalar()!;
    }
    public void Reset(int initial)
    {
        if (initial < 0 || initial > 1000) throw new ArgumentOutOfRangeException(nameof(initial));
        using var c = Open(FilePath); using var tx = c.BeginTransaction(deferred: false);
        Exec(c, "DELETE FROM Reservations; DELETE FROM Stock", tx);
        using var cmd = c.CreateCommand(); cmd.Transaction = tx;
        cmd.CommandText = "INSERT INTO Stock VALUES(1,$n,0)"; cmd.Parameters.AddWithValue("$n", initial);
        cmd.ExecuteNonQuery(); tx.Commit();
    }
    public static StockView Read(SqliteConnection c, SqliteTransaction? tx = null)
    {
        using var cmd = c.CreateCommand(); cmd.Transaction = tx;
        cmd.CommandText = "SELECT Available,Version FROM Stock WHERE Id=1";
        using var r = cmd.ExecuteReader();
        if (!r.Read()) throw new InvalidOperationException("Missing stock row.");
        return new StockView(r.GetInt32(0), r.GetInt32(1));
    }
    public static Outcome Reserve(SqliteConnection c, string request, int quantity, StockView expected,
        bool guarded = true, bool failAfterUpdate = false)
    {
        if (string.IsNullOrWhiteSpace(request) || request.Length > 100) throw new ArgumentException("Invalid request.");
        if (quantity < 1 || quantity > 1000) throw new ArgumentOutOfRangeException(nameof(quantity));
        // IMMEDIATE serializes these writes; it cannot make an earlier application read current.
        using var tx = c.BeginTransaction(deferred: false);
        using (var existing = c.CreateCommand())
        {
            existing.Transaction = tx; existing.CommandText = "SELECT Quantity FROM Reservations WHERE Request=$id";
            existing.Parameters.AddWithValue("$id", request); object? value = existing.ExecuteScalar();
            if (value is not null)
            {
                if (Convert.ToInt32(value) != quantity) throw new ArgumentException("Request reused with different quantity.");
                tx.Commit(); return Outcome.Replayed;
            }
        }
        if (expected.Available < quantity) { tx.Commit(); return Outcome.Rejected; }
        using (var update = c.CreateCommand())
        {
            update.Transaction = tx;
            update.CommandText = guarded ? """
                UPDATE Stock SET Available=Available-$q,Version=Version+1
                WHERE Id=1 AND Version=$v AND Available >= $q
                """ : "UPDATE Stock SET Available=$left,Version=Version+1 WHERE Id=1";
            update.Parameters.AddWithValue("$q", quantity); update.Parameters.AddWithValue("$v", expected.Version);
            update.Parameters.AddWithValue("$left", expected.Available - quantity);
            if (update.ExecuteNonQuery() != 1) return Outcome.Conflict; // Disposal rolls back; no receipt is inserted.
        }
        if (failAfterUpdate) throw new InvalidOperationException("Injected failure before receipt.");
        using (var insert = c.CreateCommand())
        {
            insert.Transaction = tx; insert.CommandText = "INSERT INTO Reservations VALUES($id,$q)";
            insert.Parameters.AddWithValue("$id", request); insert.Parameters.AddWithValue("$q", quantity);
            insert.ExecuteNonQuery();
        }
        tx.Commit(); return Outcome.Committed;
    }
    public static long Reserved(SqliteConnection c) => Scalar(c, "SELECT COALESCE(SUM(Quantity),0) FROM Reservations");
    public void Dispose() => Directory.Delete(directory, true); // Only this fixture's generated directory.
}
```

`LessonLab/Schedules.cs`. Schedules ghi lịch của hai task sở hữu connection thật với các cổng xác nhận, rồi chạy trace giữ snapshot riêng. Thứ tự statement được chủ động kiểm soát; không dùng sleep để tạo race.

<!-- lab-file: LessonLab/Schedules.cs -->
```csharp
using System.Collections.Concurrent;

public sealed record RunResult(Outcome First, Outcome Second, int Conflicts, int Retries,
    int Remaining, long Reserved, int Version, string[] Trace);

public static class Schedules
{
    private static TaskCompletionSource<bool> Gate() => new(TaskCreationOptions.RunContinuationsAsynchronously);
    public static async Task<RunResult> Run(string path, int q1, int q2, Strategy strategy)
    {
        if (!Enum.IsDefined(strategy)) throw new ArgumentOutOfRangeException(nameof(strategy));
        var read1 = Gate(); var read2 = Gate(); var written1 = Gate();
        var log = new ConcurrentQueue<string>(); int conflicts = 0, retries = 0;
        var first = Task.Run(async () => {
            using var c = Store.Open(path); var s = Store.Read(c);
            log.Enqueue($"T1 READ available={s.Available} version={s.Version}"); read1.SetResult(true);
            await read2.Task.WaitAsync(TimeSpan.FromSeconds(20));
            var result = Store.Reserve(c, "A", q1, s, strategy != Strategy.Blind);
            log.Enqueue($"T1 {result}"); written1.SetResult(true); return result;
        });
        var second = Task.Run(async () => {
            await read1.Task.WaitAsync(TimeSpan.FromSeconds(20));
            using var c = Store.Open(path); var s = Store.Read(c);
            log.Enqueue($"T2 READ available={s.Available} version={s.Version}"); read2.SetResult(true);
            await written1.Task.WaitAsync(TimeSpan.FromSeconds(20));
            var result = Store.Reserve(c, "B", q2, s, strategy != Strategy.Blind);
            log.Enqueue($"T2 {result}");
            if (result == Outcome.Conflict)
            {
                conflicts++;
                if (strategy == Strategy.Retry)
                {
                    retries++; s = Store.Read(c);
                    log.Enqueue($"T2 READ available={s.Available} version={s.Version}");
                    result = Store.Reserve(c, "B", q2, s);
                    if (result == Outcome.Conflict) conflicts++;
                    log.Enqueue($"T2 {result}");
                }
            }
            return result;
        });
        var results = await Task.WhenAll(first, second).WaitAsync(TimeSpan.FromSeconds(25));
        using var final = Store.Open(path); var stock = Store.Read(final);
        return new RunResult(results[0], results[1], conflicts, retries,
            stock.Available, Store.Reserved(final), stock.Version, log.ToArray());
    }
    public static int Snapshot(string path)
    {
        using var reader = Store.Open(path); using var writer = Store.Open(path);
        using var tx = reader.BeginTransaction(deferred: true);
        var old = Store.Read(reader, tx);
        if (Store.Reserve(writer, "snapshot-writer", 7, Store.Read(writer)) != Outcome.Committed)
            throw new Exception("Writer did not commit.");
        if (Store.Read(reader, tx) != old) throw new Exception("Snapshot changed.");
        int code;
        try { Store.Exec(reader, "UPDATE Stock SET Available=Available-1 WHERE Id=1", tx);
            throw new Exception("Stale snapshot unexpectedly wrote."); }
        catch (Microsoft.Data.Sqlite.SqliteException ex) when (ex.SqliteErrorCode == 5)
        { code = ex.SqliteExtendedErrorCode; }
        tx.Rollback();
        if (Store.Read(reader).Available != 3 || code != 517) throw new Exception("Unexpected pinned-version snapshot result.");
        return code;
    }
}
```

`LessonLab/Crash.cs`. Crash chỉ khởi chạy chính executable này làm tiến trình con. Tiến trình con chuyển mười giữa hai tài khoản trong một transaction và thêm 64 blob phụ, mỗi blob 4096 byte, với cache mười trang để đẩy trang bẩn ra WAL. Dữ liệu phụ chỉ giúp kiểm tra WAL tồn tại, không phải workload nghiệp vụ. Nó báo trước commit hoặc sau khi Commit trả về rồi chờ; parent dừng nó, đợi thoát và mở connection mới. Không còn connection cài đặt nào mở tại lúc dừng.

<!-- lab-file: LessonLab/Crash.cs -->
```csharp
using System.Diagnostics;
using System.Reflection;
using Microsoft.Data.Sqlite;

public readonly record struct RecoveryResult(long A, long B, long Noise, long WalBytes);

public static class Crash
{
    public static void Child(string path, string point)
    {
        if (point is not ("before" or "after")) throw new ArgumentException("Unknown crash point.");
        using var c = Store.Open(path);
        Store.Exec(c, "PRAGMA cache_size=10; PRAGMA cache_spill=ON;");
        using var tx = c.BeginTransaction(deferred: false);
        Store.Exec(c, "UPDATE Accounts SET Balance=Balance-10 WHERE Id=1; UPDATE Accounts SET Balance=Balance+10 WHERE Id=2;", tx);
        // Force dirty page spill, so the before-commit case really leaves WAL frames.
        using (var insert = c.CreateCommand())
        {
            insert.Transaction = tx; insert.CommandText = "INSERT INTO Noise VALUES($id,zeroblob(4096))";
            var id = insert.Parameters.Add("$id", SqliteType.Integer);
            for (int i = 1; i <= 64; i++) { id.Value = i; insert.ExecuteNonQuery(); }
        }
        if (point == "after") tx.Commit();
        Console.WriteLine("READY " + point); Console.Out.Flush();
        Console.ReadLine(); // Parent kills this process at the acknowledged boundary.
    }
    public static async Task<RecoveryResult> Run(string point)
    {
        using var store = new Store(); // No connection remains open after setup.
        string executable = Environment.ProcessPath ?? throw new Exception("Missing process path.");
        var info = new ProcessStartInfo(executable) {
            RedirectStandardOutput = true, RedirectStandardError = true, RedirectStandardInput = true,
            UseShellExecute = false };
        if (string.Equals(Path.GetFileNameWithoutExtension(executable), "dotnet", StringComparison.OrdinalIgnoreCase))
            info.ArgumentList.Add(Assembly.GetExecutingAssembly().Location);
        foreach (string arg in new[] { "--child", store.FilePath, point }) info.ArgumentList.Add(arg);
        using var child = Process.Start(info) ?? throw new Exception("Could not start child.");
        var errors = child.StandardError.ReadToEndAsync();
        try
        {
            string? signal = await child.StandardOutput.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(20));
            if (signal != "READY " + point) throw new Exception("Child did not acknowledge crash boundary.");
            string wal = store.FilePath + "-wal";
            long size = File.Exists(wal) ? new FileInfo(wal).Length : 0;
            if (size <= 32) throw new Exception("Expected spilled or committed WAL frames.");
            child.Kill(entireProcessTree: true);
            await child.WaitForExitAsync().WaitAsync(TimeSpan.FromSeconds(20));
            using var recovered = Store.Open(store.FilePath);
            return new RecoveryResult(Store.Scalar(recovered, "SELECT Balance FROM Accounts WHERE Id=1"),
                Store.Scalar(recovered, "SELECT Balance FROM Accounts WHERE Id=2"),
                Store.Scalar(recovered, "SELECT COUNT(*) FROM Noise"), size);
        }
        finally
        {
            if (!child.HasExited) child.Kill(entireProcessTree: true);
            await child.WaitForExitAsync();
            string stderr = await errors;
            if (!string.IsNullOrWhiteSpace(stderr)) Console.Error.WriteLine(stderr);
        }
    }
}
```

`LessonLab/Checks.cs`. Checks dùng mô hình nhận request tuần tự độc lập cho 225 tổ hợp tồn đầu 0-8, lượng 1-5. Nó đối chiếu tồn, tổng xác nhận, version và quyết định, cùng snapshot cũ, rollback do lỗi chủ động, request lặp, input sai và hai điểm crash.

<!-- lab-file: LessonLab/Checks.cs -->
```csharp
public static class Checks
{
    private static void Require(bool ok, string why) { if (!ok) throw new Exception(why); }
    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); } catch (T) { return; }
        throw new Exception($"Expected {typeof(T).Name}.");
    }
    public static async Task Run()
    {
        using var store = new Store();
        using (var c = Store.Open(store.FilePath)) Require(Store.Engine(c) == "3.50.4", "Unexpected engine version.");
        var broken = await Schedules.Run(store.FilePath, 7, 5, Strategy.Blind);
        Require(broken.Remaining == 5 && broken.Reserved == 12, "Lost-update witness missing.");
        int cases = 0;
        for (int initial = 0; initial <= 8; initial++)
            for (int a = 1; a <= 5; a++)
                for (int b = 1; b <= 5; b++)
                {
                    store.Reset(initial); var actual = await Schedules.Run(store.FilePath, a, b, Strategy.Retry);
                    // Independent serial business model: no SQL, version predicate or retry state.
                    int left = initial, total = 0, commits = 0;
                    bool acceptA = a <= left; if (acceptA) { left -= a; total += a; commits++; }
                    bool acceptB = b <= left; if (acceptB) { left -= b; total += b; commits++; }
                    Require(actual.Remaining == left && actual.Reserved == total && actual.Version == commits, "Serial oracle differs.");
                    Require(actual.First == (acceptA ? Outcome.Committed : Outcome.Rejected)
                        && actual.Second == (acceptB ? Outcome.Committed : Outcome.Rejected), "Wrong admission decision.");
                    Require(actual.Remaining + actual.Reserved == initial, "Conservation failed."); cases++;
                }
        store.Reset(10); Require(Schedules.Snapshot(store.FilePath) == 517, "Stale snapshot not rejected.");
        store.Reset(10);
        using (var c = Store.Open(store.FilePath))
        {
            var old = Store.Read(c);
            Throws<InvalidOperationException>(() => Store.Reserve(c, "fail", 7, old, failAfterUpdate: true));
            Require(Store.Read(c) == old && Store.Reserved(c) == 0, "Rollback left half a reservation.");
            Require(Store.Reserve(c, "same", 7, old) == Outcome.Committed, "Initial request failed.");
            Require(Store.Reserve(c, "same", 7, old) == Outcome.Replayed, "Replay consumed stock.");
            Require(Store.Read(c).Available == 3 && Store.Reserved(c) == 7, "Replay changed the result.");
            Throws<ArgumentException>(() => Store.Reserve(c, "same", 6, old));
            Throws<ArgumentException>(() => Store.Reserve(c, " ", 1, old));
            Throws<ArgumentOutOfRangeException>(() => Store.Reserve(c, "bad", 0, old));
            Throws<ArgumentOutOfRangeException>(() => store.Reset(1001));
        }
        store.Reset(1000);
        using (var c = Store.Open(store.FilePath))
        {
            Require(Store.Reserve(c, new string('x', 100), 1000, Store.Read(c)) == Outcome.Committed, "Upper-bound reservation failed.");
            Require(Store.Read(c) == new StockView(0, 1) && Store.Reserved(c) == 1000, "Upper-bound totals differ.");
            Require(Store.Reserve(c, "empty", 1, Store.Read(c)) == Outcome.Rejected, "Empty stock admitted a request.");
            Throws<ArgumentOutOfRangeException>(() => Store.Reserve(c, "large", 1001, Store.Read(c)));
            Throws<ArgumentException>(() => Store.Reserve(c, new string('x', 101), 1, Store.Read(c)));
        }
        var before = await Crash.Run("before"); var after = await Crash.Run("after");
        Require(before.A == 100 && before.B == 100 && before.Noise == 0, "Uncommitted work became visible.");
        Require(after.A == 90 && after.B == 110 && after.Noise == 64, "Acknowledged commit lost.");
        Console.WriteLine($"PASS: {cases} serial-oracle schedules; stale snapshot=517; rollback/replay; 2 crash boundaries.");
    }
}
```

`LessonLab/Experiment.cs`. Experiment đổi chiến lược trong cùng lịch, rồi đổi lượng T2 ở ca riêng. Nó đếm xung đột/retry và xét kết quả nghiệp vụ. Không benchmark throughput hay thời gian.

<!-- lab-file: LessonLab/Experiment.cs -->
```csharp
public static class Experiment
{
    public static async Task Run()
    {
        using var store = new Store();
        Console.WriteLine("strategy,q2,remaining,reserved,conflicts,retries,first,second,conserves");
        foreach (int q2 in new[] { 5, 2 })
            foreach (var strategy in Enum.GetValues<Strategy>())
            {
                store.Reset(10); var r = await Schedules.Run(store.FilePath, 7, q2, strategy);
                Console.WriteLine($"{strategy},{q2},{r.Remaining},{r.Reserved},{r.Conflicts},{r.Retries}," +
                    $"{r.First},{r.Second},{r.Remaining + r.Reserved == 10}");
            }
        foreach (string point in new[] { "before", "after" })
        {
            var r = await Crash.Run(point);
            Console.WriteLine($"# crash={point}; A={r.A}; B={r.B}; noise={r.Noise}; walFramesPresent={r.WalBytes > 32}");
        }
    }
}
```

`LessonLab/Program.cs`. Program chọn demo, kiểm tra, thí nghiệm hoặc chế độ con nội bộ. Các lệnh thông thường không nhận đường dẫn database ngoài.

<!-- lab-file: LessonLab/Program.cs -->
```csharp
if (args.Length == 3 && args[0] == "--child") { Crash.Child(args[1], args[2]); return; }
if (args.Length == 1 && args[0] == "--check") { await Checks.Run(); return; }
if (args.Length == 1 && args[0] == "--experiment") { await Experiment.Run(); return; }
if (args.Length != 0) throw new ArgumentException("Use no argument, --check or --experiment.");
using var store = new Store();
using (var c = Store.Open(store.FilePath)) Console.WriteLine("SQLite " + Store.Engine(c));
foreach (var strategy in new[] { Strategy.Blind, Strategy.Retry })
{
    store.Reset(10); var r = await Schedules.Run(store.FilePath, 7, 5, strategy);
    Console.WriteLine(strategy);
    foreach (string line in r.Trace) Console.WriteLine(line);
    Console.WriteLine($"remaining={r.Remaining}; reserved={r.Reserved}; conserves={r.Remaining + r.Reserved == 10}");
}
```

Demo dự kiến:

```text
SQLite 3.50.4
Blind
T1 READ available=10 version=0
T2 READ available=10 version=0
T1 Committed
T2 Committed
remaining=5; reserved=12; conserves=False
Retry
T1 READ available=10 version=0
T2 READ available=10 version=0
T1 Committed
T2 Conflict
T2 READ available=3 version=1
T2 Rejected
remaining=3; reserved=7; conserves=True
```

Kết quả `--check` dự kiến:

```text
PASS: 225 serial-oracle schedules; stale snapshot=517; rollback/replay; 2 crash boundaries.
```

Oracle hữu hạn kiểm tra dữ liệu này và thứ tự T1 trước T2 được ép, chưa xét mọi lịch xen kẽ hay mọi engine. Lập luận bất biến giải thích vì sao transaction có kiểm tra giữ quy tắc một mặt hàng. Kiểm tra cần khả năng tạo/dừng tiến trình con; nếu chưa có, đọc trace và kết quả dự kiến, không coi đó là quan sát đã chạy.

</details>

Bài sửa lỗi: sau khi T2 nhận Conflict, retry bằng StockView cũ không đổi. Lần thử giống hệt có cho phép request năm đơn vị không? Sửa ranh giới đó.

<details>
<summary>Đáp án</summary>

Không. Version 0 vẫn khác version 1 hiện tại. Vòng lặp giữ nguyên giá trị đó có thể xung đột mãi; vòng lặp không cận chưa có lập luận tiến triển. Cách sửa là nhánh Retry: kết thúc transaction thất bại, gọi Store.Read lại rồi Store.Reserve với dữ liệu mới. Ca năm đơn vị bị từ chối khi tồn ba; ca hai thành công. Nếu writer khác chen vào tiếp, vẫn có thể xung đột và không được báo thành công.

</details>

Nghỉ - 10 phút, rời màn hình.

## 6. Lịch có kiểm soát và quan sát phục hồi

**Thí nghiệm · 45 phút.** Dự đoán sáu dòng lịch và hai kết quả crash, rồi so với `--experiment`. **Hoàn thành khi:** tách quan sát bất biến khỏi nhận định hiệu năng/bền vững chưa thử.

### Giữ lịch cố định

Giữ tồn đầu mười, lượng T1 bảy, cùng schema/engine và thứ tự R1,R2,W1,W2. Reset giữa các lần chạy. Trong mỗi ca lượng T2, chỉ đổi Blind, Guarded (không retry) hoặc Retry (một lần từ dữ liệu mới). Input là dữ liệu giả lập. Lượng năm so với hai là biến thể riêng, không phải đổi chiến lược.

Dự đoán tồn cuối, tổng xác nhận đã commit, số xung đột/retry và quyết định cuối cho cả sáu dòng.

<details>
<summary>Đáp án</summary>

| Lượng T2 | Chiến lược | Tồn cuối | Đặt giữ | Xung đột | Retry | Kết quả T2 | Giữ tổng mười? |
|---|---|---|---|---|---|---|---|
| 5 | Blind | 5 | 12 | 0 | 0 | Committed | Không |
| 5 | Guarded | 3 | 7 | 1 | 0 | Conflict | Có |
| 5 | Retry | 3 | 7 | 1 | 1 | Rejected | Có |
| 2 | Blind | 8 | 9 | 0 | 0 | Committed | Không |
| 2 | Guarded | 3 | 7 | 1 | 0 | Conflict | Có |
| 2 | Retry | 1 | 9 | 1 | 1 | Committed | Có |

T1 commit ở mọi dòng. Ca ghi mù hai đơn vị vẫn mất phần trừ dù chưa hứa quá tồn: 8+9=17. Có kiểm tra nhưng không retry giữ bất biến, song để T2 chưa giải quyết dù tồn đủ. Retry có thể đổi cả trạng thái và quyết định; ít xung đột hơn chưa tốt nếu kết quả nghiệp vụ sai.

</details>

### Thí nghiệm crash của tiến trình

Giữ số dư hai tài khoản đều 100 và chuyển mười trong một transaction. Chỉ đổi vị trí lỗi theo tín hiệu trước/sau commit mà child xác nhận. Cấu hình cache/đẩy trang và 64 dòng phụ giống nhau. Nhận tín hiệu bảo đảm đã tới biên cần thử; parent chỉ dừng child đó và mở lại sau khi nó thoát. Tắt autocheckpoint để còn bằng chứng WAL trước lúc dừng.

Dự đoán hai số dư, số dòng phụ và WAL có dữ liệu lớn hơn header hay không. Chỉ giữ tổng số dư đã chứng minh phục hồi nguyên tử chưa?

<details>
<summary>Đáp án</summary>

| Biên dừng | A sau mở lại | B sau mở lại | Dòng phụ | Byte WAL trước khi dừng |
|---|---|---|---|---|
| Trước commit | 100 | 100 | 0 | Lớn hơn header; có trang bẩn đã đẩy ra |
| Sau khi Commit trả về | 90 | 110 | 64 | Lớn hơn header; có frame đã commit |

Cả hai tổng đều 200 nên chỉ tổng chưa phân biệt trạng thái cũ và mới. Phải xét số dư chính xác cùng số dòng phụ. Áp dụng một nửa như (90,100) hoặc (100,110) sẽ sai. Code kiểm tra file tồn tại/kích thước và để SQLite kiểm tra/phục hồi frame; số byte WAL chính xác có thể khác và không phải output cố định.

</details>

### Phạm vi đã quan sát và giới hạn

Sáu dòng CSV và hai trạng thái phục hồi đã được quan sát khi viết bài bằng runtime Linux đã pin. Kiểm tra cũng tái hiện mã 517. Đây là bằng chứng theo lịch xác định, không phải benchmark race ngẫu nhiên hay chứng minh mọi cách xen kẽ. Cổng chọn lịch và tín hiệu tiến trình chọn biên lỗi; chưa đo công bằng, tranh khóa, throughput hoặc p99.

Giả định gồm cache riêng, một mặt hàng, không reset/nhập thêm đồng thời, mọi bên ghi đúng dùng quy tắc, filesystem local và hệ điều hành vẫn hoạt động. Dự đoán là các bảng trên. Quan sát gồm kết quả SQL, trace, mã lỗi và WAL tồn tại. Suy luận là các cơ chế tái hiện hành vi đọc cũ/biên commit đã mô hình hóa ở đây. Nguồn hỗ trợ cơ chế; lần chạy hữu hạn hỗ trợ các ca này.

Chưa thử mất điện, cache thiết bị báo sai, ghi bị xé, vị trí dừng tùy ý, crash lúc checkpoint hay SQL Server. FULL yêu cầu đồng bộ qua SQLite/VFS; dừng tiến trình chưa xóa cache hệ điều hành. Không coi đây là chứng nhận bền vững vật lý hay kết quả tranh chấp chung.

Nghỉ - 10 phút, rời màn hình.

## 7. Vận dụng: commit thành công nhưng mất response

**Vận dụng · 35 phút.** Đổi từ hai đơn tranh nhau sang gửi lại cùng request. **Hoàn thành khi:** retry khớp tạo đúng một xác nhận lưu bền và một lần trừ; dữ liệu không khớp bị từ chối.

Response HTTP bị mất sau khi R-42 đặt giữ bảy đã commit. Client gửi lại R-42. HashSet trong một tiến trình mất khi khởi động lại và không phối hợp nhiều instance. Thiết kế danh tính lưu bền cùng ranh giới nguyên tử, rồi kiểm tra connection mới nhận lại request đó. Nếu retry đổi lượng thành sáu thì sao?

<details>
<summary>Đáp án - thiết kế request lặp và chương trình đầy đủ</summary>

Dùng mã request làm khóa xác nhận duy nhất và lưu cùng số lượng. Tra bản ghi đó trong transaction ghi trước khi trừ tồn. Xác nhận khớp trả Replayed kể cả khi chỉ còn ba; cùng danh tính nhưng lượng khác là lỗi. Phần trừ và thêm bản ghi dùng cùng commit nên lỗi không để tồn đã trừ mà thiếu xác nhận.

Trong bản sao lab riêng, thay Program.cs bằng chương trình đầy đủ dưới đây, giữ các file khác. Sau restore, chạy cùng lệnh no-restore. Bỏ qua kết quả đầu mô phỏng mất phản hồi; chưa chủ động làm lỗi transport HTTP thật.

```csharp
using var store = new Store(10);
using (var first = Store.Open(store.FilePath))
{
    var result = Store.Reserve(first, "R-42", 7, Store.Read(first));
    if (result != Outcome.Committed) throw new Exception("Initial request failed.");
    // Pretend its HTTP response never reached the caller.
}
using (var retry = Store.Open(store.FilePath))
{
    if (Store.Reserve(retry, "R-42", 7, Store.Read(retry)) != Outcome.Replayed)
        throw new Exception("Matching retry was not recognized.");
    bool mismatch = false;
    try { Store.Reserve(retry, "R-42", 6, Store.Read(retry)); }
    catch (ArgumentException) { mismatch = true; }
    if (!mismatch) throw new Exception("Changed payload was accepted.");
    if (Store.Read(retry).Available != 3 || Store.Reserved(retry) != 7
        || Store.Scalar(retry, "SELECT COUNT(*) FROM Reservations") != 1)
        throw new Exception("Duplicate business effect.");
}
Console.WriteLine("PASS: R-42 replayed; remaining=3; reserved=7; receipts=1; mismatch rejected.");
```

Kết quả dự kiến: `PASS: R-42 replayed; remaining=3; reserved=7; receipts=1; mismatch rejected.` So danh tính/payload nằm trong cùng transaction ghi; khóa duy nhất củng cố danh tính. Đây là idempotency cho đặt giữ thành công trong một database, không phải HTTP giao đúng một lần hay transaction thanh toán phân tán. Lab chưa lưu xác nhận cho request bị từ chối, nên chưa có chính sách lưu bền kết quả từ chối. Fixture xóa database khi kết thúc; dịch vụ phải giữ database qua các lần khởi động lại. Với nhiều mặt hàng hoặc tenant, cũng lưu và so các trường đó trong payload request. Không xóa xác nhận khi chưa định nghĩa quy tắc lưu giữ/tái sử dụng mã.

</details>

## 8. Tổng hợp và tự kiểm tra

**Tổng hợp · 45 phút.** Tự dựng các ranh giới khi đóng trang, rồi viết quyết định cùng phép thử có thể bác bỏ. **Hoàn thành khi:** nhận định nêu quy tắc nghiệp vụ, bằng chứng, mô hình lỗi và điều chưa chắc.

1. Vì sao tính nguyên tử và CHECK không âm chưa đủ cho lịch ghi mù?

<details>
<summary>Đáp án</summary>

Mỗi cặp trừ/xác nhận có thể commit nguyên tử nhưng dùng số tồn ứng dụng cũ. CHECK xét một giá trị lưu, chưa xét tổng lượng đã hứa. Kết quả 5+12 vi phạm A+S=10. Đặt lần đọc/kiểm tra đúng chỗ và transaction giữ cả hai thay đổi là hai yêu cầu riêng.

</details>

2. Vì sao lặp phép ghi trong transaction đọc WAL cũ chưa làm mới quyết định?

<details>
<summary>Đáp án</summary>

Mốc kết thúc đọc giữ nguyên tới khi transaction kết thúc. Sau commit của writer khác, nâng lên ghi có thể trả BUSY_SNAPSHOT. Rollback/kết thúc transaction cũ rồi xét lại nghiệp vụ từ lần đọc mới. Retry có cận vẫn có thể xung đột; không tính nó là đặt giữ đã commit.

</details>

3. Hai quan sát crash xác minh điều gì và còn để ngỏ điều gì?

<details>
<summary>Đáp án</summary>

Tại hai biên dừng tiến trình đã chọn, đọc SQL mới cho trạng thái cũ (100,100,0 dòng phụ) hoặc đã commit (90,110,64 dòng phụ), với WAL tồn tại trước lúc dừng. Chúng hỗ trợ các ca hiển thị/phục hồi nguyên tử này. Chưa chứng nhận bền vững khi mất điện, hỏng tùy ý, mọi vị trí dừng, crash checkpoint, hành vi flush thiết bị hay engine khác.

</details>

4. Đề xuất phép kiểm tra production có thể làm đổi khuyến nghị đặt giữ có kiểm tra.

<details>
<summary>Đáp án</summary>

Dùng engine đích cùng tranh chấp request, retry, quy tắc nhiều mặt hàng và danh tính giao lại đại diện. Trước hết xét bất biến/xác nhận, rồi đo chặn, throughput và kết quả chưa giải quyết với retry có cận. Xung đột cao, giữ quyền ghi quá lâu, tác động thanh toán ngoài ranh giới nguyên tử hay bất biến nhiều dòng chưa được bảo vệ có thể đòi thiết kế khác. Phải xác minh isolation và xử lý lỗi trên SQL Server; bộ đếm local chưa chọn thay được.

</details>

## Nguồn và quyền sử dụng

- [Isolation](https://www.sqlite.org/isolation.html), [WAL 2.1-2.3](https://www.sqlite.org/wal.html), [transaction 2.1-2.2](https://www.sqlite.org/lang_transaction.html) và [synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous) của SQLite hỗ trợ các ranh giới hiển thị/phục hồi đã nêu.
- Source SQLite tại commit `8ed5e7365e6f12f427910188bbf6b254daad2ef6`, tag version-3.50.4; link có giới hạn dòng ở phần 4. [Thông báo public domain](https://github.com/sqlite/sqlite/blob/8ed5e7365e6f12f427910188bbf6b254daad2ef6/LICENSE.md). Hash mirror GitHub khác mã Fossil của sqlite_source_id; trùng phiên bản engine chưa biến số đo thành nhận định từ source.
- [Transaction của Microsoft.Data.Sqlite](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/transactions), phần deferred transaction, hỗ trợ cầu nối provider. [Hướng dẫn transaction SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17), phần ACID, kiểm soát đồng thời và isolation theo phiên bản dòng, hỗ trợ thảo luận ứng dụng riêng. Đoạn T-SQL chưa được chạy.
- Nội dung tự viết theo CC BY 4.0; mã C# giảng dạy tự viết theo MIT, có giấy phép trong ZIP. Source SQLite được phân tích, không sao chép. Package giữ giấy phép riêng.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 05 - Index và query plan](../2026-10-09-index-query-plans/lesson.md) - Tách chi phí truy cập, tính đúng và giả định snapshot khi phân trang.
- [Bài 03 - Đường đi ngắn nhất](../2026-10-07-shortest-paths/lesson.md) - Ôn đối chiếu thông tin cũ với trạng thái hiện tại.
- [Hướng dẫn lab C#](../../../labs/transactions-recovery/dotnet/README.vi.md) - Cấu hình được pin, lịch thực thi, kiểm tra crash tiến trình và giới hạn.

---

[← Bài trước: Bài 05 - Index và query plan: vì sao seek vẫn có thể tốn nhiều công](../2026-10-09-index-query-plans/lesson.md) · [Danh sách bài học](../../README.md) · [Bài sau: Bài 07 - Độ bất định khi lấy mẫu: nhiều record chưa chắc có thêm bằng chứng →](../2026-10-11-sampling-uncertainty/lesson.md)
<!-- LESSON_NAVIGATION_END -->
