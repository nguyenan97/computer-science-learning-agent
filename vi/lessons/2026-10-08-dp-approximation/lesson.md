# Bài 04 - Quy hoạch động và xấp xỉ: chọn công việc trong một ngân sách

[English](../../../lessons/2026-10-08-dp-approximation/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/budget-selection/dotnet-lab.zip)

Bài 03 cho thấy một đường đi có vẻ tốt chưa chắc đã tối ưu. Bây giờ, worker ASP.NET có ngân sách xử lý cố định và phải chọn các công việc nguyên vẹn. Chọn công việc có vẻ tốt nhất trước có thể làm mất một tổ hợp tốt hơn. Ta sẽ giữ đủ trạng thái để tìm nghiệm tối ưu, rồi suy ra cách chọn ít tốn công hơn với bảo đảm chất lượng rõ ràng.

**Mục tiêu:** định nghĩa trạng thái cho bài toán chọn 0/1, suy ra và chứng minh công thức truy hồi quy hoạch động, dựng lại danh sách công việc, rồi so sánh với greedy. Chứng minh một biến thể greedy đạt ít nhất một nửa giá trị tối ưu theo các giả định cụ thể. Lộ trình chọn quy hoạch động và xấp xỉ sau đồ thị. Kiến thức cần có: mảng, vòng lặp, Big-O, bất biến và trạng thái ở Bài 01-03; bài này sẽ xây dựng công thức truy hồi và chứng minh xấp xỉ từ đầu.

## Khái niệm chính

- **Chọn 0/1 trong ngân sách.** Mỗi công việc được chọn một lần hoặc bỏ qua; tổng chi phí không được vượt ngân sách. Với ngân sách 6, chọn một công việc chi phí 4 có thể làm mất tổ hợp hai công việc chi phí 3 có tổng giá trị cao hơn.
- **Trạng thái và quy hoạch động (DP).** Giữ thông tin cần cho quyết định tiếp theo, giải trạng thái nhỏ hơn và dùng lại kết quả. “Hai công việc đầu, ngân sách 3” khác “ba công việc đầu, ngân sách 3” vì còn những công việc khác nhau để chọn.
- **Lựa chọn greedy.** Chốt theo một quy tắc cục bộ thay vì giữ các phương án. Tỷ lệ giá trị/chi phí cao nhất có vẻ tốt, nhưng công việc không chia nhỏ được có thể để lại ngân sách thừa mà các bước sau không tận dụng được.
- **Bảo đảm xấp xỉ.** Chấp nhận nghiệm hợp lệ có cận chất lượng đã chứng minh. “Ít nhất một nửa tối ưu” nghĩa là nếu tối ưu bằng 100, kết quả phải đạt ít nhất 50 trên mọi input hợp lệ, không chỉ các ví dụ đã test.

Mỗi phần có lời giải. Bạn có thể chỉ đọc bảng chạy từng bước, chứng minh và mã đầy đủ. Giới hạn cài đặt trong 15 phút của phần lab; nếu thiếu SDK, tiếp tục bằng các giải thích đó. Không cần nộp bài hay lưu kết quả học cá nhân.

## 1. Ôn lại và bổ sung kiến thức nền

**Ôn lại · 20 phút.** Dựng lại hai cơ chế được chọn từ bài trước và kiểm tra ràng buộc 0/1. **Hoàn thành khi:** phân biệt được lựa chọn greedy đã có chứng minh với quy tắc chỉ có vẻ tốt, và nêu được yếu tố phải giữ duy nhất.

1. Từ Bài 03: vì sao Dijkstra có thể dừng khi lấy đích ra với khoảng cách nhỏ nhất còn hợp lệ, nhưng không được dừng ở lần tìm thấy đầu tiên?

<details>
<summary>Đáp án</summary>

Lần tìm thấy đầu tiên chỉ chứng minh có đường: cạnh trực tiếp chi phí 10 có thể được cải thiện bởi ba cạnh chi phí 1. Với khoảng cách nhỏ nhất còn hợp lệ, một đường rẻ hơn phải có đoạn đầu chưa xử lý mang khoảng cách nhỏ hơn; phần còn lại không âm tạo mâu thuẫn. Bỏ entry stale trước khi dừng. Chứng minh này bảo đảm lựa chọn của Dijkstra. Hôm nay, thứ tự giá trị/chi phí cần lập luận riêng, không thể dùng lại chứng minh đường đi ngắn nhất.

</details>

2. Từ Bài 01: HashSet và List giữ thứ tự xuất hiện đầu tiên như thế nào, và cần chọn quy tắc so sánh mã ra sao?

<details>
<summary>Đáp án</summary>

Đọc input theo thứ tự; chỉ thêm vào List khi `HashSet.Add` trả true. HashSet kiểm tra mã đã có, còn List giữ thứ tự kết quả. Comparer phải phù hợp quy tắc xác định hai mã là một; đổi phân biệt hoa thường sẽ đổi kết quả. Lab dùng ID công việc duy nhất và so sánh ordinal, nên hai ID khác nhau có cùng chi phí/giá trị vẫn là hai công việc. Từ chối ID lặp thay vì âm thầm tính cùng công việc hai lần.

</details>

3. Một công việc có chi phí 2, giá trị 3; ngân sách là 4. Tối ưu 0/1 bằng bao nhiêu? Nếu cho phép số bản sao không giới hạn thì sao?

<details>
<summary>Đáp án</summary>

Tối ưu 0/1 bằng 3 vì chỉ được chọn công việc đó một lần. Nếu không giới hạn số bản sao, hai bản cho giá trị 6. Nếu chưa rõ, liệt kê các tập con hợp lệ: tập rỗng hoặc công việc duy nhất. Phần nền tảng cần bổ sung là gắn mỗi quyết định với index công việc và ngân sách còn lại. Chỉ có ngân sách thì chưa biết công việc đó còn được chọn hay không.

</details>

## 2. Xây trạng thái, công thức truy hồi và chứng minh

**Nền tảng · 50 phút.** Hoàn thành bảng DP nhỏ, dựng lại công việc đã chọn và giải thích bất biến. **Hoàn thành khi:** chứng minh được cả hai nhánh và tìm được lỗi dùng lại công việc khi nén bảng.

### Phản ví dụ cụ thể

Ngân sách 6, ba công việc không chia nhỏ được theo thứ tự input:

| Công việc | Chi phí | Giá trị | Giá trị/chi phí |
|---|---|---|---|
| A | 4 | 7 | 1,75 |
| B | 3 | 5 | khoảng 1,67 |
| C | 3 | 5 | khoảng 1,67 |

Dự đoán lựa chọn của greedy theo tỷ lệ và nghiệm tối ưu. B và C có phải duplicate chỉ vì các số giống nhau không?

<details>
<summary>Đáp án</summary>

Greedy theo tỷ lệ chọn A trước, còn ngân sách 2. B và C đều không vừa, nên giá trị là 7. Chọn B,C dùng đủ 6 và đạt 10. Hai công việc có ID khác nhau nên được chọn cả hai. ID lặp vi phạm điều kiện của lab, nhưng các trường số bằng nhau không có nghĩa là cùng công việc.

</details>

### Định nghĩa chính xác ý nghĩa một ô

Gọi `F(i,c)` là giá trị lớn nhất khi chỉ dùng i công việc đầu và tổng chi phí **không vượt** c. Không phải “đúng bằng c”. Được chọn tập rỗng nên `F(0,c)=0`; chi phí dương cho `F(i,0)=0`.

Với công việc i có chi phí w, giá trị v:

- Nếu `w > c`, `F(i,c) = F(i-1,c)`.
- Nếu không, `F(i,c) = max(F(i-1,c), F(i-1,c-w)+v)`.

Nhánh đầu bỏ công việc này. Nhánh sau chọn nó một lần và dùng hàng trước để lấp ngân sách còn lại. Cả hai đều đọc hàng i-1, nên chưa có công việc i trong kết quả được dùng lại. Công thức truy hồi là quy tắc tính trạng thái lớn hơn từ các trạng thái nhỏ hơn.

Điều kiện đầu vào: danh sách cố định, ID duy nhất và không rỗng, chi phí nguyên dương, giá trị nguyên không âm. Chi phí/ngân sách dùng `int`, giá trị dùng `long`. Chưa xét chia nhỏ công việc, phụ thuộc, giá trị cộng hưởng hay nhiều tài nguyên. Input phải giữ nguyên trong mỗi lần gọi. Từ chối ngân sách âm, ID/chi phí/giá trị sai và tổng giá trị của **mọi** công việc vượt `long.MaxValue`, kể cả công việc quá ngân sách. Kiểm tra bảo thủ này bảo đảm mọi tổng giá trị tập con đều an toàn; ở bài này `long.MaxValue` vẫn là giá trị hợp lệ. DP chính xác còn giới hạn 2.000.000 ô, thuật toán vét cạn giới hạn 22 công việc. Đây là giới hạn lab, không phải giới hạn toán học.

### Bảng và dựng lại nghiệm

| Công việc đã xét | c=0 | c=1 | c=2 | c=3 | c=4 | c=5 | c=6 |
|---|---|---|---|---|---|---|---|
| Chưa có | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| A | 0 | 0 | 0 | 0 | 7 | 7 | 7 |
| A,B | 0 | 0 | 0 | 5 | 7 | 7 | 7 |
| A,B,C | 0 | 0 | 0 | 5 | 7 | 7 | 10 |

Tại `F(2,6)`, chọn B được `F(1,3)+5 = 5`, còn bỏ B giữ 7. Tại `F(3,6)`, chọn C được `F(2,3)+5 = 10`, cải thiện 7. Để dựng nghiệm, bắt đầu ở `(3,6)`. Nếu giá trị khác hàng trước tại cùng ngân sách, chọn công việc đó và trừ chi phí. Nếu bằng nhau, bỏ nó. Khi hòa, bỏ công việc xét sau; yêu cầu là giá trị tối ưu và một tập con hợp lệ, không phải nghiệm duy nhất hay tối ưu thêm một mục tiêu chi phí.

Bài tập: đi ngược từ `(3,6)` để lấy ID đã chọn, rồi làm lại từ `(3,5)`. Vì sao khởi tạo toàn bộ bằng 0 đúng cho “không vượt” nhưng sai cho “đúng bằng” ngân sách?

<details>
<summary>Đáp án</summary>

Tại `(3,6)`, 10 khác `F(2,6)=7`: chọn C, chuyển đến `(2,3)`. Giá trị 5 khác `F(1,3)=0`: chọn B, chuyển đến `(1,0)`. Bỏ A. Trả B,C với chi phí 6, giá trị 10. Tại `(3,5)`, 7 bằng cả `F(2,5)` và `F(1,5)`; bỏ C,B rồi chọn A với chi phí 4, giá trị 7.

“Không vượt” cho phép dùng chi phí 0 ở mọi ngân sách nên 0 là mốc hợp lệ. Với “đúng bằng”, một mức chi phí dương có thể không đạt được; giá trị 0 sẽ đánh dấu sai rằng nó hợp lệ. Cần giá trị riêng cho trạng thái không đạt được, chỉ khởi tạo trạng thái chi phí 0 và không cộng giá trị vào trạng thái không đạt được. Lab chỉ implement “không vượt”.

</details>

### Vì sao công thức truy hồi đúng?

Bất biến: sau khi điền hàng i, mỗi ô là tối ưu với i công việc đầu và ngân sách của ô đó. Hàng 0 đúng vì chỉ có tập rỗng. Giả sử hàng i-1 đúng. Mỗi tập con hợp lệ ở hàng i hoặc bỏ công việc i, khi đó giá trị không vượt `F(i-1,c)`, hoặc chọn nó, khi đó các công việc còn lại vừa c-w và có giá trị không vượt `F(i-1,c-w)+v`. Vì vậy không có nghiệm hợp lệ vượt giá trị lớn nhất của hai nhánh. Ngược lại, mỗi nhánh dựng được tập con hợp lệ từ nghiệm tối ưu hàng trước, nên đạt được giá trị lớn nhất đó. Quy nạp chứng minh cả cận và sự tồn tại; bước dựng lại nghiệm đi theo đúng các lựa chọn này.

Binary search dùng bất biến trên khoảng để chứng minh việc bỏ một vùng. Ở đây, bất biến phải mô tả giá trị tối ưu của cả dãy công việc; bỏ một công việc chỉ vì tỷ lệ thấp hơn cần chứng minh mới. BFS dùng thứ tự lớp khi cạnh có chi phí 1, còn Dijkstra dùng nhãn nhỏ nhất khi chi phí không âm. DP đi theo thứ tự mà mọi trạng thái phụ thuộc đã được giải.

Ta dùng lại ý tưởng trạng thái của Bài 03. Mỗi phép chuyển đi từ một lớp công việc sang lớp tiếp theo, tạo đồ thị có hướng không chu trình. Thứ tự lớp bảo đảm các trạng thái phụ thuộc đã tính xong trước khi dùng, không cần priority queue. Đổi phần thưởng thành chi phí âm sẽ vi phạm điều kiện Dijkstra trước đó; ở đây chính việc không có chu trình bảo đảm thứ tự tính an toàn, không phải trọng số không âm.

### Chi phí và lỗi khi nén bảng

Với n công việc và ngân sách nguyên C, điền n(C+1) ô, ngoài việc khởi tạo 0 cho (n+1)(C+1) ô lưu trữ. Thời gian là O((n+1)(C+1)), dựng nghiệm O(n); bộ nhớ O((n+1)(C+1)). Khi n,C dương thường viết O(nC). Bảng `long` 2.000.000 ô có 16 MB phần giá trị, chưa tính metadata của mảng và object kết quả. Mô hình đếm phép toán số nguyên có chi phí giới hạn, không đếm gọi database.

Nếu chỉ cần giá trị tối ưu, dùng một hàng và duyệt ngân sách **giảm dần**. Trước công việc i, mảng mang ý nghĩa hàng i-1. Tại c, index thấp hơn c-w chưa bị ghi đè nên nhánh chọn vẫn đọc hàng trước. Duyệt tăng dần sẽ dùng lại công việc: chi phí 2/giá trị 3, ngân sách 4, ghi 3 ở c=2 rồi đọc nó để ghi 6 ở c=4. Lab có cả bảng đầy đủ để dựng nghiệm và bản một hàng duyệt giảm dần chỉ trả giá trị.

Nghỉ - 10 phút, rời màn hình.

## 3. Đọc nguồn và suy ra cận chất lượng

**Đọc tài liệu · 45 phút.** Đọc phần nguồn được giới hạn, dựng lại lập luận 1/2 và viết ba dòng nhận định/bằng chứng/giới hạn. **Hoàn thành khi:** chứng minh được bảo đảm mà không dùng thí nghiệm thành công thay cho chứng minh.

Đọc Williamson và Shmoys, [The Design of Approximation Algorithms, mục 3.1, trang in 65-67, và bài tập 3.1 ở trang 77](https://www.designofapproxalgs.com/book.pdf#page=65). Mục này giải thích DP knapsack bằng các cặp chi phí/giá trị không bị trội và vì sao độ lớn ngân sách ảnh hưởng độ phức tạp. Lab dùng bảng theo ngân sách, không chép biểu diễn đó. Với cùng dãy công việc đã xét, cặp chi phí/giá trị (2,5) trội hơn (3,4): dùng ít ngân sách và đạt giá trị cao hơn. Thêm bất kỳ tập công việc còn lại nào cũng không làm cặp sau tốt hơn trong mô hình cộng dồn. Bài tập nêu ý tưởng greedy theo tỷ lệ kết hợp công việc đơn tốt nhất; lập luận dưới đây giải thích vì sao có bảo đảm. Sách giả định giá trị dương; công việc giá trị 0 trong lab không cải thiện tập con nên không đổi lập luận.

### Độ lớn số khác độ dài input

Ngân sách 1.000.000 cần khoảng gấp đôi số bit của 1.000, nhưng bảng theo ngân sách cần khoảng 1.000 lần số cột. Đây là thuật toán **giả đa thức (pseudopolynomial)**: đa thức theo giá trị số C, chưa chắc đa thức theo độ dài mã hóa nhị phân của C. Nếu C có b bit, nó có thể gần `2^b`, nên O(nC) có thể tăng theo hàm mũ của b. Nén còn một hàng tiết kiệm bộ nhớ nhưng không bỏ sự phụ thuộc C. DP theo giá trị hoặc tập trạng thái thưa có thể hữu ích với những cận khác; vẫn cần implementation và phân tích riêng.

### Từ greedy sai đến xấp xỉ có chứng minh

Loại công việc có chi phí riêng vượt C vì không thể có trong nghiệm hợp lệ. Sắp phần còn lại theo tỷ lệ giá trị/chi phí giảm dần. G là giá trị khi lần lượt chọn công việc còn vừa ngân sách và bỏ công việc không vừa. B là giá trị lớn nhất của một công việc riêng lẻ hợp lệ. Trả tập tốt hơn trong hai tập, nên `A = max(G,B)`.

Để thấy riêng G không có bảo đảm dương cố định, dùng ngân sách W>2 và hai công việc: công việc nhỏ chi phí 1/giá trị 2, công việc lớn chi phí W/giá trị W. Greedy chọn công việc nhỏ trước rồi không còn đủ cho công việc lớn. Tỷ lệ chất lượng là `2/W`, tiến về 0 khi W tăng. Bảo vệ bằng công việc đơn sẽ chọn công việc lớn.

Trong chứng minh, tạm cho phép chia nhỏ công việc: một phần của công việc chi phí 3/giá trị 6 có thể dùng chi phí 1 và nhận giá trị 2. Bài toán **nới lỏng** này chứa mọi tập con nguyên, nên tối ưu U là cận trên của tối ưu 0/1 OPT. Với công việc chia nhỏ được, thứ tự theo tỷ lệ là tối ưu: chuyển một ít ngân sách từ công việc tỷ lệ thấp sang phần chưa lấy của công việc tỷ lệ cao không làm giảm giá trị. Lặp phép đổi này sẽ cho một đoạn đầu được lấy hết và tối đa một công việc tiếp theo được lấy một phần.

Gọi P là đoạn đầu được lấy hết trước công việc đầu tiên không còn vừa; công việc tiếp theo có giá trị t. Khi đó `U <= value(P)+t`. Greedy bỏ qua rồi tiếp tục của lab giữ nguyên đoạn đầu đó và có thể thêm công việc sau, nên `G >= value(P)`. Công việc bị bỏ vẫn vừa ngân sách khi đứng riêng sau bước lọc, nên `B >= t`. Vì vậy:

`OPT <= U <= value(P)+t <= G+B <= 2*max(G,B) = 2*A`.

Suy ra `A >= OPT/2`. Nếu toàn bộ công việc sau khi lọc cùng vừa ngân sách, greedy đã tối ưu. Nếu không công việc nào vừa, OPT và A đều bằng 0. Bài tập trong sách dừng ở công việc đầu tiên không vừa; tiếp tục thêm công việc hợp lệ có giá trị không âm chỉ làm cận theo đoạn đầu mạnh hơn. Đây là giải thích biến thể của lab, không gán một thuật toán khác cho nguồn.

Bài tập: giả định nào cần cho cận trên? Định lý có hứa nghiệm tối ưu chính xác, hay áp dụng được khi công việc phụ thuộc nhau không? Viết bảng nhận định ngắn.

<details>
<summary>Đáp án</summary>

| Nhận định | Bằng chứng | Giả định hoặc giới hạn |
|---|---|---|
| DP giữ nghiệm tốt nhất cho từng bài toán con | Mục 3.1 và quy nạp hai trường hợp ở mục 2 | Trạng thái lab có một chi phí nguyên cộng dồn và các công việc 0/1 độc lập |
| DP theo ngân sách là giả đa thức | Sách so độ lớn số với mã hóa nhị phân | Bộ nhớ một hàng không làm O(nC) thành đa thức theo log C |
| Greedy có bảo vệ trả ít nhất OPT/2 | Chiến lược bài tập 3.1 và lập luận nới lỏng ở trên | Chi phí dương, giá trị không âm và cộng dồn, công việc độc lập và đứng riêng đều vừa sau khi lọc |

Định lý bảo đảm giá trị trong trường hợp xấu nhất, không hứa tối ưu chính xác, latency hay kết quả trung bình. Phụ thuộc, nhiều tài nguyên hoặc giá trị cộng hưởng làm đổi tập nghiệm hay mục tiêu; không được dùng lại chứng minh nếu chưa có lập luận mới. Tỷ lệ trên 1/2 ở mọi input đã test phù hợp với chứng minh, không thay được chứng minh.

</details>

## 4. Ứng dụng dự án và case study PostgreSQL

**Đọc mã nguồn · 45 phút.** Lần theo cách dựng một mức của planner và liên hệ cách chọn trạng thái với bộ chọn batch .NET. **Hoàn thành khi:** nhận ra các phương án được giữ và phân biệt chi phí ước lượng với hiệu năng đo được.

### Ứng dụng: chọn batch xử lý bằng .NET

Worker ASP.NET đọc các công việc export hoặc kiểm tra đủ điều kiện từ SQL Server. Mỗi công việc có ID ổn định, chi phí ước lượng dương theo slot nguyên và giá trị nghiệp vụ cộng dồn. Tạo danh sách cố định có phiên bản rồi chọn tập con trong ngân sách slot. Dùng DP chính xác khi C và n vừa giới hạn bộ nhớ/thời gian; dùng phương pháp có bảo đảm 1/2 khi chấp nhận cận giá trị thấp hơn. Trả ID đã chọn, tổng chi phí/giá trị ước lượng, thuật toán và phiên bản input để Angular giải thích lựa chọn.

Nếu một công việc xuất hiện hai lần, từ chối hoặc dedupe theo quy tắc nghiệp vụ rõ ràng trước khi tối ưu. Chọn ID trong bộ nhớ khác việc giữ quyền xử lý: worker phải kiểm tra lại và nhận công việc một cách nguyên tử, chẳng hạn trong transaction database. Nếu không, worker khác có thể lấy cùng công việc. Lab implement bước chọn, chưa xử lý transaction hay tính công bằng khi lập lịch.

Nếu chi phí ước lượng có phần lẻ, làm tròn từng chi phí lên số slot giữ được ràng buộc ngân sách ước lượng nhưng có thể loại tổ hợp hữu ích. Làm tròn xuống có thể khiến tổng chi phí gốc vượt ngân sách. Cả hai đều chưa bảo đảm hoàn thành đúng hạn nếu ước lượng sai. Phụ thuộc và giá trị cộng hưởng cũng nằm ngoài mô hình công việc độc lập, giá trị cộng dồn.

### Đọc một optimizer thực tế tại commit cố định

PostgreSQL 17.6 dùng DP để dựng các phương án join. Ta đọc commit **`7885b94dd81b98bbab9ed878680d156df7bf857f`**, tag `REL_17_6`. Đây là ứng dụng dùng lại bài toán con trong sản phẩm, không phải implementation knapsack của lab. Với truy vấn join Orders, Customers, Regions, cặp join đầu tiên làm thay đổi dữ liệu trung gian và chi phí về sau; chọn một cặp có vẻ tốt chưa xét được mọi phương án hữu ích.

1. [`standard_join_search`](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/allpaths.c#L3381-L3493) đặt mức 1 là các quan hệ ban đầu, rồi xử lý mức 2 đến `levels_needed`. Sau khi tạo path cho mỗi mức, gọi `set_cheapest` trên từng quan hệ join. Comment DP và các vòng lặp là phạm vi đọc chính.
2. [`join_search_one_level`](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/joinrels.c#L60-L205) mở rộng join nhỏ hơn và xét cách ghép hợp lệ từ hai nhóm nhỏ. Mỗi mức là **danh sách các tập quan hệ**, không phải một “cặp tốt nhất” cho kích thước đó. Các điều kiện join và ràng buộc thứ tự giới hạn ứng viên được tạo.
3. [`make_join_rel`](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/joinrels.c#L693-L789) hợp ID quan hệ, kiểm tra tính hợp lệ và thêm path thực thi vào quan hệ đại diện tập đó. Cùng một tập có thể nhận path từ nhiều cách phân rã.
4. [Chính sách được mô tả ở `add_path`](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/util/pathnode.c#L361-L415) giữ phương án theo chi phí, thứ tự, tham số hóa, số dòng và khả năng chạy song song an toàn. Chỉ có một path rẻ chưa chắc giữ đủ thông tin cho join sau.

Bài tập đọc mã: với bốn quan hệ inner join thông thường A,B,C,D, nhóm ở mức thấp nào có thể tạo mức 4? Vì sao chỉ giữ một path rẻ nhất cho mỗi kích thước làm mất thông tin?

<details>
<summary>Đáp án</summary>

Mức 4 có thể mở rộng nhóm ba quan hệ bằng một quan hệ, hoặc ghép hai nhóm hai quan hệ không giao nhau, nếu điều kiện join hay ràng buộc cho phép tạo ứng viên đó. Ví dụ AB với CD khác AC với BD; cả hai hợp thành ABCD. Ở mức 2, AB và AC là trạng thái khác nhau dù đều có hai quan hệ, vì các quan hệ còn lại và điều kiện join khác nhau. Các path cho cùng một tập cũng có thể khác thứ tự hữu ích hoặc cách tham số hóa. Danh sách và chính sách path trong mã giữ sự khác biệt đó. Đây là phân tích cơ chế, không khẳng định mã xét mọi cây join có thể viết về mặt cú pháp.

</details>

### Workload và đánh đổi

**Đã xác minh:** mã xây các mức join từ dưới lên, thêm path từ nhiều phương án và có tiêu chí giữ path rõ ràng. Lựa chọn giữa `standard_join_search` và GEQO nằm [ngay phía trên](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/allpaths.c#L3361-L3378). [Tài liệu cấu hình PostgreSQL 17](https://www.postgresql.org/docs/17/runtime-config-query.html#RUNTIME-CONFIG-QUERY-GEQO) ghi `geqo_threshold` mặc định là 12 mục FROM và giải thích đánh đổi thời gian lập kế hoạch với kế hoạch kém tối ưu; nhóm FULL OUTER JOIN và các cấu hình khác ảnh hưởng cách đếm. Đây là ngưỡng workload trong tài liệu, không phải số đỉnh hay latency đã đo.

**Suy luận thiết kế:** thay các phương án này bằng một cặp greedy ở mỗi mức có thể loại một kế hoạch hữu ích về sau. Ta suy ra từ khác biệt trạng thái và mã, không khẳng định maintainer chạy thí nghiệm knapsack của bài. Optimizer kiểm soát độ lớn tìm kiếm bằng kiểm tra tính hợp lệ, loại path và một chiến lược tìm kiếm thay thế. Khác bảng DP đơn giản của lab, chi phí planner là ước lượng và path giữ thêm thuộc tính. Phần đọc này không suy ra bảo đảm knapsack 1/2 cho GEQO.

Trong dịch vụ chọn batch, trước hết xác định thông tin nào ảnh hưởng tính hợp lệ hoặc giá trị về sau. Không thể giấu nhóm phụ thuộc hay tài nguyên thứ hai vào một giá trị đơn nếu chưa có chứng minh. Ta đã đọc mã, chưa chạy query plan PostgreSQL hay tái hiện hiệu năng của nó. Cũng không khẳng định SQL Server dùng cùng planner; SQL Server là nguồn dữ liệu trong ví dụ ứng dụng.

Ăn trưa và nghỉ - 30 phút.

## 5. Lab C#: implement, kiểm tra và sửa lỗi

**Lab · 75 phút.** Implement công thức theo trạng thái và hai cách greedy, chạy kiểm tra tính đúng, rồi sửa lỗi bảng nén. **Hoàn thành khi:** lệnh kiểm tra qua và giải thích được vì sao không chọn cùng công việc hai lần.

Implement `Exact`, `DensityGreedy`, `HalfApprox` theo điều kiện mục 2. Trả giá trị, chi phí và index trong input gốc; mỗi index tối đa một lần. Dùng thuật toán vét cạn độc lập cho input nhỏ. Lời giải chạy được bên dưới có cách chuẩn bị và cả năm file mã nguồn.

<details>
<summary>Đáp án - toàn bộ lab chạy được</summary>

Dùng **.NET SDK 10.0.401**, target **net10.0**, không có package ngoài. Giải nén ZIP và chạy trong thư mục `dotnet`. Nếu dùng checkout, thư mục là `labs/budget-selection/dotnet`. Hoặc tạo project với các file dưới đây, không cần tải riêng mã nguồn. [Hướng dẫn lab](../../../labs/budget-selection/dotnet/README.vi.md) có link tải từng file khi cần.

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
  </PropertyGroup>
</Project>
```

Chạy trong thư mục `dotnet`:

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

Demo dự kiến in:

```text
Exact: value=10, cost=6, ids=B,C
Density: value=7, cost=4, ids=A
HalfApprox: value=7, cost=4, ids=A
```

Nếu cần, cài đúng SDK từ Microsoft. Sau khi build, `dotnet run --no-restore -c Release --project LessonLab -- --check` chạy offline, không restore package bên thứ ba. Nếu chưa cài được SDK, dùng bảng và đọc mã. Không cần instance SQL Server hay PostgreSQL.

`LessonLab/Budget.cs`: `Validate` từ chối ID lặp, không âm thầm dedupe. `Exact` chỉ đọc hàng trước và dựng nghiệm khi cải thiện nghiêm ngặt. `ExactValueRolling` chỉ trả giá trị. Comparer theo tỷ lệ dùng tích chéo số nguyên với `BigInteger` để tránh tỷ lệ bị làm tròn và phép nhân `long` bị tràn; giá trị/chi phí ở đây có cận 64/32 bit cố định. Khi tỷ lệ bằng nhau, dùng index gốc để phân định. Các hàm không sửa input.

```csharp
// Original MIT teaching code. No PostgreSQL or textbook code is copied.
using System.Numerics;

public readonly record struct Job(string Id, int Cost, long Value);
public sealed record Choice(long Value, int Cost, int[] Indices, long Work, long RatioComparisons = 0);

public static class Budget
{
    public const long MaxCells = 2_000_000;

    public static void Validate(Job[] jobs, int capacity)
    {
        ArgumentNullException.ThrowIfNull(jobs);
        if (capacity < 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        long total = 0;
        foreach (var job in jobs)
        {
            if (string.IsNullOrWhiteSpace(job.Id) || !ids.Add(job.Id))
                throw new ArgumentException("IDs must be nonempty and unique (ordinal).", nameof(jobs));
            if (job.Cost <= 0 || job.Value < 0)
                throw new ArgumentException("Costs must be positive; values nonnegative.", nameof(jobs));
            total = checked(total + job.Value);
        }
    }

    public static Choice Exact(Job[] jobs, int capacity)
    {
        Validate(jobs, capacity);
        long cells = (jobs.Length + 1L) * (capacity + 1L);
        if (cells > MaxCells)
            throw new ArgumentOutOfRangeException(nameof(capacity), "DP table exceeds the lab cell limit.");
        var best = new long[jobs.Length + 1, capacity + 1];
        long work = 0;
        for (int i = 1; i <= jobs.Length; i++)
        {
            Job job = jobs[i - 1];
            for (int c = 0; c <= capacity; c++)
            {
                work++;
                best[i, c] = best[i - 1, c];
                if (job.Cost <= c)
                    best[i, c] = Math.Max(best[i, c], checked(best[i - 1, c - job.Cost] + job.Value));
            }
        }
        var selected = new List<int>();
        int remaining = capacity;
        for (int i = jobs.Length; i > 0; i--)
        {
            if (best[i, remaining] == best[i - 1, remaining]) continue;
            selected.Add(i - 1);
            remaining -= jobs[i - 1].Cost;
        }
        selected.Reverse();
        return new Choice(best[jobs.Length, capacity], capacity - remaining, selected.ToArray(), work);
    }

    public static long ExactValueRolling(Job[] jobs, int capacity)
    {
        Validate(jobs, capacity);
        if (capacity + 1L > MaxCells)
            throw new ArgumentOutOfRangeException(nameof(capacity), "Rolling array exceeds the lab cell limit.");
        var best = new long[capacity + 1];
        foreach (var job in jobs)
            for (int c = capacity; c >= job.Cost; c--)
                best[c] = Math.Max(best[c], checked(best[c - job.Cost] + job.Value));
        return best[capacity];
    }

    public static Choice DensityGreedy(Job[] jobs, int capacity) => Density(jobs, capacity, false);
    public static Choice HalfApprox(Job[] jobs, int capacity) => Density(jobs, capacity, true);

    private static Choice Density(Job[] jobs, int capacity, bool protectSingle)
    {
        Validate(jobs, capacity);
        var order = Enumerable.Range(0, jobs.Length).Where(i => jobs[i].Cost <= capacity).ToList();
        long comparisons = 0;
        order.Sort((a, b) =>
        {
            comparisons++;
            // Descending value/cost without floating-point rounding or long overflow.
            int comparison = ((BigInteger)jobs[b].Value * jobs[a].Cost)
                .CompareTo((BigInteger)jobs[a].Value * jobs[b].Cost);
            return comparison != 0 ? comparison : a.CompareTo(b);
        });
        var selected = new List<int>();
        int used = 0, bestSingle = -1;
        long value = 0, work = 0;
        foreach (int index in order)
        {
            work++;
            if (bestSingle < 0 || jobs[index].Value > jobs[bestSingle].Value) bestSingle = index;
            if (jobs[index].Cost > capacity - used) continue;
            selected.Add(index);
            used += jobs[index].Cost;
            value = checked(value + jobs[index].Value);
        }
        if (protectSingle && bestSingle >= 0 && jobs[bestSingle].Value > value)
            return new Choice(jobs[bestSingle].Value, jobs[bestSingle].Cost, [bestSingle], work, comparisons);
        selected.Sort();
        return new Choice(value, used, selected.ToArray(), work, comparisons);
    }
}
```

`LessonLab/Oracle.cs`: xét mọi tập con. Nó dùng chung bước kiểm tra input nhưng không dùng công thức DP hay thứ tự tỷ lệ, nên độc lập khi đối chiếu tối ưu trên miền được chấp nhận. Với n>=1, thời gian O(n·2^n), bộ nhớ tìm kiếm thêm O(n). Giới hạn 22 công việc chặn lần chạy tham chiếu quá lớn ngoài ý muốn.

```csharp
// Exhaustive independent reference for small instances, original MIT code.
public static class Oracle
{
    public static Choice Solve(Job[] jobs, int capacity)
    {
        Budget.Validate(jobs, capacity);
        if (jobs.Length > 22) throw new ArgumentOutOfRangeException(nameof(jobs), "Oracle limit is 22 jobs.");
        long best = 0, work = 0;
        int bestMask = 0, bestCost = 0;
        for (int mask = 0; mask < (1 << jobs.Length); mask++)
        {
            work++;
            long cost = 0, value = 0;
            for (int i = 0; i < jobs.Length; i++)
                if ((mask & (1 << i)) != 0)
                {
                    cost += jobs[i].Cost;
                    value = checked(value + jobs[i].Value);
                }
            if (cost <= capacity && value > best)
            {
                best = value;
                bestCost = (int)cost;
                bestMask = mask;
            }
        }
        int[] indices = Enumerable.Range(0, jobs.Length).Where(i => (bestMask & (1 << i)) != 0).ToArray();
        return new Choice(best, bestCost, indices, work);
    }
}
```

`LessonLab/Program.cs`:

```csharp
if (args.Length == 0)
{
    Job[] jobs = [new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)];
    foreach (var entry in new[] {
        (Name: "Exact", Result: Budget.Exact(jobs, 6)),
        (Name: "Density", Result: Budget.DensityGreedy(jobs, 6)),
        (Name: "HalfApprox", Result: Budget.HalfApprox(jobs, 6)) })
        Console.WriteLine($"{entry.Name}: value={entry.Result.Value}, cost={entry.Result.Cost}, " +
                          $"ids={string.Join(",", entry.Result.Indices.Select(i => jobs[i].Id))}");
}
else if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

`LessonLab/Checks.cs`: kiểm tra tính hợp lệ, không lặp index, tối ưu chính xác, kết quả bảng nén, input không đổi và bất đẳng thức 1/2. Xét hết các bộ ba công việc có chi phí 1-3, giá trị 0-3, ngân sách 0-6; thêm ca ngẫu nhiên có seed và biên số học. Phép so `2*A >= OPT` dùng `BigInteger` vì hai lần một kết quả `long` hợp lệ có thể vượt `long.MaxValue`. Ca tỷ lệ rất gần nhau với giá trị lớn phát hiện lỗi so thứ tự bằng số thực.

```csharp
using System.Numerics;

public static class Checks
{
    private static int instances;
    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T) { return; }
        throw new InvalidOperationException($"Expected {typeof(T).Name}.");
    }

    private static void Feasible(Job[] jobs, int capacity, Choice result)
    {
        Require(result.Indices.Distinct().Count() == result.Indices.Length, "Reused job.");
        long cost = 0, value = 0;
        foreach (int index in result.Indices)
        {
            Require((uint)index < (uint)jobs.Length, "Invalid result index.");
            cost += jobs[index].Cost;
            value = checked(value + jobs[index].Value);
        }
        Require(cost <= capacity && cost == result.Cost && value == result.Value, "Invalid choice totals.");
    }

    private static void Compare(Job[] jobs, int capacity)
    {
        var snapshot = jobs.ToArray();
        var oracle = Oracle.Solve(jobs, capacity);
        var exact = Budget.Exact(jobs, capacity);
        var greedy = Budget.DensityGreedy(jobs, capacity);
        var approx = Budget.HalfApprox(jobs, capacity);
        foreach (var choice in new[] { oracle, exact, greedy, approx }) Feasible(jobs, capacity, choice);
        Require(exact.Value == oracle.Value, "DP differs from exhaustive optimum.");
        Require(Budget.ExactValueRolling(jobs, capacity) == oracle.Value, "Rolling DP differs from optimum.");
        Require(greedy.Value <= oracle.Value && approx.Value <= oracle.Value, "Value exceeds optimum.");
        Require(approx.Value >= greedy.Value, "Single-item protection reduced the value.");
        Require((BigInteger)2 * approx.Value >= oracle.Value, "Half guarantee violated.");
        Require(jobs.SequenceEqual(snapshot), "Input changed.");
        instances++;
    }

    public static void Run()
    {
        Compare([], 0); Compare([], 4);
        Compare([new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)], 6);
        Compare([new("single", 2, 3)], 4); // An ascending rolling loop would incorrectly return 6.
        Compare([new("heavy", 100, 1000), new("zero", 1, 0), new("small", 2, 3)], 3);
        Compare([new("a", 1, 0), new("b", 2, 0)], 2);
        Compare([new("A", 1, 2), new("B", 1000, 1000)], 1000);
        Compare([new("A", 1, 2), new("B", 1000, 1000), new("C", 1000, 1000)], 2000);
        Compare([new("maximum", 1, long.MaxValue)], 1);
        Job[] close = [new("low", 1, long.MaxValue / 2), new("high", 1, long.MaxValue / 2 + 1)];
        Compare(close, 1);
        Require(Budget.DensityGreedy(close, 1).Indices.SequenceEqual(new[] { 1 }), "Rounded ratio ordering.");
        Throws<ArgumentNullException>(() => Budget.Exact(null!, 1));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([], -1));
        Throws<ArgumentException>(() => Budget.HalfApprox([new("x", 0, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", -1, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", 1, -1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("", 1, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", 1, 1), new("x", 2, 1)], 2));
        Throws<OverflowException>(() => Budget.Exact([new("x", 1, long.MaxValue), new("y", 1, 1)], 1));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([new("x", 1, 1)], 1_000_000));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([], int.MaxValue));
        Throws<ArgumentOutOfRangeException>(() => Budget.ExactValueRolling([], int.MaxValue));
        Throws<ArgumentOutOfRangeException>(() => Oracle.Solve(
            Enumerable.Range(0, 23).Select(i => new Job($"id{i}", 1, 1)).ToArray(), 1));

        // Exhaust all three-job inputs with costs 1-3, values 0-3, capacities 0-6.
        for (int encoded = 0; encoded < 12 * 12 * 12; encoded++)
        {
            var jobs = new Job[3];
            int rest = encoded;
            for (int i = 0; i < jobs.Length; i++)
            {
                int code = rest % 12; rest /= 12;
                jobs[i] = new Job($"j{i}", code / 4 + 1, code % 4);
            }
            for (int capacity = 0; capacity <= 6; capacity++) Compare(jobs, capacity);
        }
        var random = new Random(20261008);
        for (int sample = 0; sample < 120; sample++)
        {
            Job[] jobs = Enumerable.Range(0, random.Next(0, 11))
                .Select(i => new Job($"j{i}", random.Next(1, 16), random.Next(0, 31))).ToArray();
            Compare(jobs, random.Next(0, 31));
        }
        Console.WriteLine($"PASS: {instances} instances checked against exhaustive optimum, feasibility and half guarantee.");
    }
}
```

`LessonLab/Experiment.cs`: sinh workload có kiểm soát ở mục 6. `Work` dùng đơn vị được ghi rõ riêng cho từng thuật toán. Đếm so sánh tỷ lệ riêng, không tính bước sắp index kết quả. Chất lượng được làm tròn bằng decimal khi in; comparer và bất đẳng thức kiểm tra dùng số học chính xác. Khi OPT bằng 0, quy ước in chất lượng 1 vì nghiệm hợp lệ giá trị 0 đã tối ưu, không phải tính 0/0.

```csharp
using System.Globalization;

public static class Experiment
{
    public static void Run()
    {
        Console.WriteLine("case,n,capacity,algorithm,value,quality,workUnit,work,ratioComparisons");
        Case("demo", [new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)], 6);
        foreach (int capacity in new[] { 10, 40, 1000 })
            Case("density-trap", [new("tiny", 1, 2), new("large", capacity, capacity)], capacity);
        foreach (int k in new[] { 4, 20, 1000 })
            Case("near-half", [new("tiny", 1, 2), new("left", k, k), new("right", k, k)], 2 * k);
        foreach (int n in new[] { 8, 12, 16 }) Case("n-scaling", Generate(n), 25);
        foreach (int capacity in new[] { 20, 40, 80 }) Case("capacity-scaling", Generate(16), capacity);
    }

    private static Job[] Generate(int n) => Enumerable.Range(0, n)
        .Select(i => new Job($"j{i}", 1 + i * 7 % 11, 1 + i * 13 % 19)).ToArray();

    private static void Case(string name, Job[] jobs, int capacity)
    {
        var exact = Budget.Exact(jobs, capacity);
        var oracle = Oracle.Solve(jobs, capacity);
        if (exact.Value != oracle.Value) throw new InvalidOperationException("Experiment oracle mismatch.");
        Print(name, jobs.Length, capacity, "Exact", exact, exact.Value, "cells");
        Print(name, jobs.Length, capacity, "Oracle", oracle, exact.Value, "subsets");
        Print(name, jobs.Length, capacity, "Density", Budget.DensityGreedy(jobs, capacity), exact.Value, "items");
        Print(name, jobs.Length, capacity, "HalfApprox", Budget.HalfApprox(jobs, capacity), exact.Value, "items");
    }

    private static void Print(string name, int n, int capacity, string algorithm, Choice choice, long optimum, string unit)
    {
        decimal quality = optimum == 0 ? 1 : (decimal)choice.Value / optimum;
        Console.WriteLine($"{name},{n},{capacity},{algorithm},{choice.Value}," +
            $"{quality.ToString("F4", CultureInfo.InvariantCulture)},{unit},{choice.Work},{choice.RatioComparisons}");
    }
}
```

Lệnh kiểm tra in dòng `PASS` sau 12.226 input, cùng các ca từ chối input sai, quá giới hạn kích thước và tràn tổng giá trị. Công việc có cùng chi phí/giá trị nhưng ID khác vẫn được giữ riêng. Các thuật toán có thể trả tập con khác nhau khi hòa; so tính hợp lệ và giá trị thay vì bắt index giống nhau. Test hữu hạn hỗ trợ chứng minh, không thay được chứng minh.

</details>

Bài tập sửa lỗi: developer đổi vòng lặp bảng nén thành `for (int c = job.Cost; c <= capacity; c++)`. Giải thích kết quả sai đầu tiên và cách sửa. Vì sao lỗi kích thước bảng không nên âm thầm chuyển sang greedy?

<details>
<summary>Đáp án</summary>

Với một công việc chi phí 2/giá trị 3, ngân sách 4, mã mới ghi `best[2]=3`, rồi đọc giá trị của chính công việc hiện tại ở `best[2]` để ghi `best[4]=6`. Nó đã giải bài toán có bản sao không giới hạn. Khôi phục vòng lặp giảm dần trong `ExactValueRolling`: tại c=4, `best[2]` còn là 0 của hàng trước, nên kết quả chỉ là 3. Test một công việc đối chiếu cả bảng đầy đủ và bảng nén với vét cạn.

Từ chối vì giới hạn ô là không đáp ứng chính sách tài nguyên, không cho phép đổi yêu cầu nghiệm chính xác. Bên gọi có thể chủ động chọn `HalfApprox` và báo bảo đảm giá trị, giảm hoặc đổi mô hình ngân sách, hay dùng phương pháp chính xác khác. Lab ném lỗi thay vì tự đổi chất lượng kết quả. Tràn tổng giá trị cũng bị từ chối thay vì trả điểm bị tràn số.

</details>

Nghỉ - 10 phút, rời màn hình.

## 6. Thí nghiệm có kiểm soát: chi phí tính và chất lượng là hai việc riêng

**Thí nghiệm · 45 phút.** Dự đoán CSV, chạy `--experiment`, rồi thay số công việc, độ lớn ngân sách và phản ví dụ greedy riêng từng nhóm. **Hoàn thành khi:** báo được tỷ lệ chất lượng và giải thích phần bị bỏ khỏi từng bộ đếm.

Mã sinh giữ chi phí/giá trị cố định và chỉ đổi biến đã nêu trong mỗi nhóm. Mọi ca chạy DP chính xác và vét cạn trên cùng input trước khi đánh giá greedy theo tỷ lệ và `HalfApprox`. Nhờ đó giữ cùng mục tiêu và kiểm tra OPT. Chỉ đếm thao tác, không dùng đồng hồ hay suy ra latency production.

- **Bẫy theo tỷ lệ:** chi phí/giá trị `(1,2)` và `(W,W)`, ngân sách W, với W=10,40,1000. Dự đoán G/OPT và A/OPT khi W tăng.
- **Gần cận 1/2:** `(1,2),(k,k),(k,k)`, ngân sách 2k, với k=4,20,1000. Dự đoán vì sao bản có bảo vệ không thể hứa cao hơn 1/2 đáng kể trong trường hợp tổng quát.
- **Tăng n:** lấy 8,12,16 công việc đầu từ cùng một dãy xác định, ngân sách 25. So số tập con của vét cạn với số ô DP; đây là đơn vị công việc khác nhau.
- **Tăng ngân sách:** giữ cùng 16 công việc, đổi C=20,40,80. Xét số ô và giá trị riêng: bảng lớn hơn không có nghĩa giá trị tăng cùng tỷ lệ.

Dự đoán hai nhóm đầu và chỉ ra quan sát nào có thể bác bỏ việc implement định lý.

<details>
<summary>Đáp án</summary>

| Nhóm | Tham số | OPT | Greedy tỷ lệ | Bản có bảo vệ | Greedy/OPT | Bản bảo vệ/OPT |
|---|---|---|---|---|---|---|
| Bẫy theo tỷ lệ | W=10 | 10 | 2 | 10 | 0,2000 | 1,0000 |
| Bẫy theo tỷ lệ | W=40 | 40 | 2 | 40 | 0,0500 | 1,0000 |
| Bẫy theo tỷ lệ | W=1000 | 1000 | 2 | 1000 | 0,0020 | 1,0000 |
| Gần cận 1/2 | k=4 | 8 | 6 | 6 | 0,7500 | 0,7500 |
| Gần cận 1/2 | k=20 | 40 | 22 | 22 | 0,5500 | 0,5500 |
| Gần cận 1/2 | k=1000 | 2000 | 1002 | 1002 | 0,5010 | 0,5010 |

Với nhóm gần cận và k>2, OPT chọn hai công việc chi phí k, được 2k. Greedy chọn công việc nhỏ và một công việc chi phí k, được k+2; công việc đơn tốt nhất chỉ có giá trị k nên giữ greedy. Tỷ lệ là `1/2 + 1/k`, tiến về 1/2. Với bẫy tỷ lệ, greedy đơn thuần tiến về 0 còn bản bảo vệ trả OPT. Đây là ca chủ động chọn để minh họa hành vi trường hợp xấu nhất, không phải phân bố ngẫu nhiên của batch thực.

Nếu một nghiệm bảo vệ hợp lệ thấp hơn OPT/2 trên input được chấp nhận, nó sẽ mâu thuẫn với nhận định implementation có bảo đảm và cần debug thuật toán, comparer chính xác hoặc thuật toán tham chiếu. Giá trị vượt OPT báo tập con sai, công việc bị lặp, tham chiếu sai hoặc mục tiêu khác. Không thể coi các kết quả đó là nhiễu đo trong thí nghiệm số nguyên xác định này.

</details>

Dự đoán hai nhóm còn lại trước khi đối chiếu.

<details>
<summary>Đáp án</summary>

| Biến | Tham số | Ô DP được điền | Tập con vét cạn | OPT | Greedy/bản bảo vệ |
|---|---|---|---|---|---|
| n, C=25 | 8 | 208 | 256 | 55 | 49 |
| n, C=25 | 12 | 312 | 4096 | 79 | 79 |
| n, C=25 | 16 | 416 | 65536 | 89 | 89 |
| C, n=16 | 20 | 336 | 65536 | 74 | 74 |
| C, n=16 | 40 | 656 | 65536 | 118 | 118 |
| C, n=16 | 80 | 1296 | 65536 | 146 | 146 |

</details>

`Work` của DP đếm ô được điền, không gồm hàng cơ sở đã khởi tạo; vét cạn đếm tập con, mỗi tập còn xét n công việc. Greedy đếm công việc hợp lệ trong vòng duyệt sau khi sắp. Không tính kiểm tra input, lọc, khởi tạo, dựng nghiệm và sắp index kết quả; so sánh tỷ lệ có cột riêng. Không coi một ô và một tập con là cùng số lệnh CPU. Cận độ phức tạp tối ưu giả định phép toán số có chi phí giới hạn sau khi kiểm tra input; xử lý ID và đọc input có chi phí riêng. Với mô hình đó, các hàm theo tỷ lệ sắp trong O(n log n), dùng thêm O(n) bộ nhớ.

Biến thể: đổi ngân sách demo từ 6 thành 3, rồi thành 7; cuối cùng nhân mọi chi phí và ngân sách với 10, giữ nguyên giá trị. Dự đoán lựa chọn hợp lệ, giá trị và công việc DP trước khi chạy.

<details>
<summary>Đáp án</summary>

Ở ngân sách 3, DP và cả hai greedy chọn một trong B,C, được 5. Ở ngân sách 7, A cùng một trong B,C vừa ngân sách và đạt 12; mọi hàm đều đạt được. DP đầy đủ điền 12 ô tại C=3 và 24 tại C=7. C=6 ban đầu điền 21 ô.

Nhân mọi chi phí và ngân sách với 10 giữ nguyên tập con hợp lệ và tối ưu 10, nhưng DP điền `3*(60+1)=183` ô, thay vì 21. Giới hạn bảng có thể từ chối khi nhân quá lớn dù bài toán chọn về mặt toán học tương đương. Chia chi phí/ngân sách cho một thừa số chung chính xác có thể bỏ mức tăng giả tạo này; làm tròn tùy ý cần phân tích tính hợp lệ riêng. Thứ tự tỷ lệ không đổi khi cùng nhân mọi chi phí.

</details>

**Giới hạn:** số đếm và tỷ lệ xác minh các instance này, chưa đo runtime, bộ nhớ tối đa, concurrency, tính công bằng hay p99 worker. Chất lượng trung bình trên mẫu công việc không làm định lý trường hợp xấu nhất mạnh hơn. Giá trị ước lượng, phụ thuộc và nhiều ngân sách trong thực tế có thể làm mô hình không còn đúng. Muốn đo thời gian, giữ cùng mục tiêu, tách bước chuẩn bị, warm up runtime, đo lặp và báo độ biến động. Lab chưa có benchmark thời gian hay thí nghiệm database.

Nghỉ - 10 phút, rời màn hình.

## 7. Vận dụng: thêm một ràng buộc

**Vận dụng · 35 phút.** Đổi yêu cầu batch thành “tối đa K công việc” và suy ra trạng thái trước khi viết code. **Hoàn thành khi:** implementation loại được tổ hợp sai và khớp vét cạn trên input nhỏ.

Trạng thái ban đầu quên số công việc đã chọn. Xét ngân sách 6, K=1 và A=(6,8), B=(3,5), C=(3,5). Vì sao giữ nguyên bảng rồi cắt bớt danh sách kết quả không an toàn? Định nghĩa công thức truy hồi, nêu độ phức tạp và implement hàm chỉ trả giá trị. Test K=0,1,2, ngân sách 0 và K lớn hơn n.

<details>
<summary>Đáp án - mô hình, mã đầy đủ và kiểm tra</summary>

Bảng cũ chọn B+C, được 10. Cắt còn một công việc được 5, trong khi A riêng lẻ được 8. Dù tính lại điểm của danh sách đúng, việc cắt không lấy lại được phương án đã bị trạng thái bỏ mất.

Đặt H(i,c,k) là giá trị lớn nhất từ i công việc đầu, chi phí tối đa c và số lượng tối đa k. Dãy rỗng, ngân sách 0 và k=0 có giá trị 0 theo điều kiện chi phí dương. Với k>0, bỏ công việc lấy H(i-1,c,k); nếu chi phí vừa, chọn nó lấy giá trị cộng H(i-1,c-chi phí,k-1). Lớp công việc trước và số lượng giảm ngăn chọn lặp, đồng thời giữ cả hai giới hạn. Chứng minh quy nạp theo hai trường hợp chọn/bỏ vẫn áp dụng. Giới hạn K về n; thời gian và bộ nhớ bảng là O((n+1)(C+1)(min(K,n)+1)). Hàm chỉ trả giá trị, chưa dựng danh sách ID.

Giữ `Budget.cs` của lab và thay `Program.cs` trong một bản sao riêng bằng chương trình đầy đủ dưới đây. Có thể xóa các file lab khác; chúng không cần thiết. Chạy `dotnet run -c Release --project LessonLab`. Vét cạn độc lập xét cả số lượng và chi phí mỗi tập con. Giới hạn bảng là chính sách tài nguyên, không phải xấp xỉ.

```csharp
using System.Numerics;

var demo = new[] { new Job("A", 6, 8), new Job("B", 3, 5), new Job("C", 3, 5) };
if (CountLimited.Solve(demo, 6, 1) != 8) throw new Exception("Transfer example failed.");
var random = new Random(20261008);
int checkedCases = 0;
for (int sample = 0; sample < 60; sample++)
{
    var jobs = Enumerable.Range(0, random.Next(0, 9))
        .Select(i => new Job($"J{i}", random.Next(1, 8), random.Next(0, 16))).ToArray();
    foreach (int capacity in new[] { 0, 5, 12 })
        foreach (int limit in new[] { 0, 1, 2, jobs.Length + 3 })
        {
            long expected = CountLimited.Oracle(jobs, capacity, limit);
            if (CountLimited.Solve(jobs, capacity, limit) != expected)
                throw new Exception("Count-limited value differs from exhaustive optimum.");
            checkedCases++;
        }
}
try { CountLimited.Solve(demo, 6, -1); throw new Exception("Negative limit accepted."); }
catch (ArgumentOutOfRangeException) { }
try { CountLimited.Solve(demo, int.MaxValue, 1); throw new Exception("Large table accepted."); }
catch (ArgumentOutOfRangeException) { }
Console.WriteLine($"PASS: {checkedCases} count-limited cases; demo value=8.");

public static class CountLimited
{
    public static long Solve(Job[] jobs, int capacity, int maxJobs)
    {
        Budget.Validate(jobs, capacity);
        if (maxJobs < 0) throw new ArgumentOutOfRangeException(nameof(maxJobs));
        int limit = Math.Min(maxJobs, jobs.Length);
        BigInteger cells = (BigInteger)(jobs.Length + 1L) * (capacity + 1L) * (limit + 1L);
        if (cells > Budget.MaxCells) throw new ArgumentOutOfRangeException(nameof(capacity));
        var best = new long[jobs.Length + 1, capacity + 1, limit + 1];
        for (int i = 1; i <= jobs.Length; i++)
            for (int c = 0; c <= capacity; c++)
                for (int k = 1; k <= limit; k++)
                {
                    best[i, c, k] = best[i - 1, c, k];
                    Job job = jobs[i - 1];
                    if (job.Cost <= c)
                        best[i, c, k] = Math.Max(best[i, c, k],
                            checked(best[i - 1, c - job.Cost, k - 1] + job.Value));
                }
        return best[jobs.Length, capacity, limit];
    }

    public static long Oracle(Job[] jobs, int capacity, int maxJobs)
    {
        Budget.Validate(jobs, capacity);
        if (maxJobs < 0) throw new ArgumentOutOfRangeException(nameof(maxJobs));
        if (jobs.Length > 22) throw new ArgumentOutOfRangeException(nameof(jobs));
        long best = 0;
        for (int mask = 0; mask < (1 << jobs.Length); mask++)
        {
            long cost = 0, value = 0;
            int count = 0;
            for (int i = 0; i < jobs.Length; i++)
                if ((mask & (1 << i)) != 0)
                {
                    count++;
                    cost += jobs[i].Cost;
                    value = checked(value + jobs[i].Value);
                }
            if (cost <= capacity && count <= maxJobs) best = Math.Max(best, value);
        }
        return best;
    }
}
```

Kết quả dự kiến: `PASS: 720 count-limited cases; demo value=8.` Các test dùng input nhỏ xác định; chứng minh quy nạp, không phải 720 lần thành công, hỗ trợ nhận định tổng quát. Chứng minh xấp xỉ 1/2 ban đầu không tự áp dụng khi thêm giới hạn số lượng: phải xét lại cận trên chia nhỏ theo ngân sách và cách tạo nghiệm ứng viên.

</details>

## 8. Tổng hợp và tự kiểm tra

**Tổng hợp · 45 phút.** Đóng trang, tự dựng lại lập luận rồi đối chiếu đáp án. **Hoàn thành khi:** xác định được trạng thái cần giữ, điều kiện làm nó đúng và điều thí nghiệm thực sự quan sát được.

1. Vì sao cần lớp công việc, và vì sao chỉ được cập nhật một hàng theo chiều giảm?

<details>
<summary>Đáp án 1</summary>

Lớp công việc ghi nhận công việc nào còn dùng được; cả hai nhánh đọc dãy trước. Với một hàng, duyệt ngân sách giảm giữ ý nghĩa dãy trước ở ô thấp hơn được tra cứu. Duyệt tăng có thể chọn lại công việc hiện tại. Giới hạn số lượng thêm chiều số lượng; thay ràng buộc có thể phải thay trạng thái.

</details>

2. Khi nào gọi O(nC) là “đa thức” gây hiểu nhầm?

<details>
<summary>Đáp án 2</summary>

C là độ lớn ngân sách, không phải số bit biểu diễn. Nhân đôi C làm công việc bảng tăng đôi dù biểu diễn chỉ thêm một bit. Đây là giả đa thức; giới hạn bảng có thể từ chối input hợp lệ về toán học. Chỉ giảm bộ nhớ chưa bỏ phụ thuộc thời gian vào C.

</details>

3. Điều gì bảo vệ greedy theo tỷ lệ, và vì sao GEQO của PostgreSQL không có bảo đảm đó từ bài này?

<details>
<summary>Đáp án 3</summary>

Chọn nghiệm tốt hơn giữa greedy theo tỷ lệ và công việc đơn hợp lệ có giá trị cao nhất. Với chi phí dương, giá trị cộng được không âm và một ngân sách, cận chia nhỏ chứng minh đạt ít nhất OPT/2. GEQO tìm trong không gian kế hoạch có ràng buộc khác, dùng chi phí ước lượng; cách tạo nghiệm và chứng minh này không mô tả GEQO.

</details>

4. Tách giả định, dự đoán, quan sát và suy luận cho lab. Nhận định nào về production còn cần bằng chứng?

<details>
<summary>Đáp án 4</summary>

**Giả định:** công việc nguyên vẹn, độc lập, ID duy nhất, chi phí nguyên dương, giá trị cộng được không âm, một ngân sách cố định và điều kiện số học/tài nguyên của lab. **Dự đoán:** giá trị DP và công thức số thao tác; các nhóm cố ý làm greedy kém. **Quan sát sau khi chạy:** các dòng CSV và kiểm tra trên tập hữu hạn. **Suy luận:** các input đó khớp và tái hiện được kiểu sai đã chọn. Nhận định tối ưu/xấp xỉ tổng quát dựa vào chứng minh cùng implementation đã review. Latency worker, độ đúng của chi phí ước lượng, an toàn transaction, công bằng, hiệu năng truy vấn PostgreSQL và chất lượng batch thực còn cần bằng chứng riêng. Đọc source xác nhận cấu trúc chương trình ở commit đã dẫn, chưa phải đo hành vi runtime trên database của ta.

</details>

Buổi sau nên tự nhớ lại ý nghĩa trạng thái, phản ví dụ cập nhật tăng và giả định của cận 1/2 trước khi đổi mục tiêu hay ràng buộc.

## Nguồn và quyền sử dụng

- David P. Williamson và David B. Shmoys, [The Design of Approximation Algorithms](https://www.designofapproxalgs.com/book.pdf), Mục 3.1, trang in 65-67 và Bài tập 3.1, trang in 77. Giải thích trong bài được tự viết; chỉ dẫn link, không phát hành lại PDF sách.
- Source PostgreSQL tại commit `7885b94dd81b98bbab9ed878680d156df7bf857f`, tag `REL_17_6`: link có giới hạn dòng ở Phần 4. [Giấy phép PostgreSQL](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/COPYRIGHT). Lab không sao chép code PostgreSQL.
- [Cấu hình GEQO của PostgreSQL 17](https://www.postgresql.org/docs/17/runtime-config-query.html#RUNTIME-CONFIG-QUERY-GEQO) cung cấp ngưỡng và đánh đổi được tài liệu mô tả; không cung cấp bảo đảm xấp xỉ knapsack.
- Nội dung bài theo CC BY 4.0. Toàn bộ mã lab tự viết theo MIT; ZIP có kèm giấy phép.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 03 - Đường đi ngắn nhất](../2026-10-07-shortest-paths/lesson.md) - Ôn trạng thái và lập luận chốt khoảng cách.
- [Hướng dẫn lab C#](../../../labs/budget-selection/dotnet/README.vi.md) - Cài SDK, kiểm tra, thí nghiệm và mã nguồn.

---

[← Bài trước: Bài 03 - Đường đi ngắn nhất: chọn BFS hay Dijkstra](../2026-10-07-shortest-paths/lesson.md) · [Danh sách bài học](../../README.md) · [Bài sau: Bài 05 - Index và query plan: vì sao seek vẫn có thể tốn nhiều công →](../2026-10-09-index-query-plans/lesson.md)
<!-- LESSON_NAVIGATION_END -->
