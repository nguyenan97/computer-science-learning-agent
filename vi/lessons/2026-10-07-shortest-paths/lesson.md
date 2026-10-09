# Bài 03 - Đường đi ngắn nhất: chọn BFS hay Dijkstra

[English](../../../lessons/2026-10-07-shortest-paths/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/shortest-paths/dotnet-lab.zip)

Bài 02 chứng minh phép tìm kiếm đúng bằng cách duy trì một phân hoạch. Bài này xét khi nào có thể kết luận một đường đi là tối ưu. Đường trực tiếp có thể ít đoạn hơn nhưng mất nhiều thời gian hơn ba đoạn đường nhỏ. Nếu chọn cấu trúc queue trước khi xác định “ngắn nhất” nghĩa là gì, ta có thể nhận kết quả nhanh nhưng sai.

**Mục tiêu:** chọn BFS khi cần ít cạnh nhất, chọn Dijkstra khi cần tổng chi phí nhỏ nhất và mọi trọng số không âm. Chứng minh khi nào khoảng cách đã tối ưu, dựng lại đường đi, sửa lỗi dừng quá sớm và so sánh số thao tác. Theo lộ trình, đây là phần đồ thị và chọn chiến lược, sau lập luận về chương trình. Kiến thức cần có: mảng, vòng lặp, bất biến và mô hình chi phí ở Bài 01-02; chưa cần học đồ thị trước đó.

## Khái niệm chính

- **Đồ thị có hướng và trọng số cạnh.** Đỉnh biểu diễn địa điểm hoặc trạng thái; cạnh cho phép đi theo một hướng và có chi phí. `A -> B (4)` cho phép đi từ A đến B với chi phí 4, không mặc nhiên có cạnh ngược lại.
- **Đường đi ngắn nhất phụ thuộc mục tiêu.** Có thể cần ít cạnh nhất hoặc tổng chi phí nhỏ nhất. Một cạnh có chi phí 10 ít cạnh hơn ba cạnh có chi phí 1 mỗi cạnh, nhưng tổng chi phí lại cao hơn.
- **BFS (tìm kiếm theo chiều rộng).** Duyệt theo số cạnh tính từ đỉnh xuất phát. Với mọi cạnh có chi phí 1, BFS xét hết các lựa chọn cách một cạnh trước các lựa chọn cách hai cạnh, nên lần tìm thấy đầu tiên cho số cạnh tối thiểu.
- **Dijkstra.** Xét đỉnh có tổng chi phí tạm thời nhỏ nhất, rồi dùng nó để cải thiện khoảng cách tới các đỉnh khác. Khi trọng số không âm, lấy ra ứng viên nhỏ nhất còn hợp lệ sẽ xác định khoảng cách tối ưu; lần tìm thấy đầu tiên chưa đủ.

Mỗi phần đều có lời giải. Bạn có thể đọc bảng chạy từng bước và mã nguồn mà không chạy lab. Nếu cài đặt mất hơn 15 phút trong phần lab, chuyển sang đọc và dùng thời gian còn lại để phân tích; không cần nộp bài hay ghi điểm.

## 1. Ôn lại và bổ sung kiến thức nền

**Ôn lại · 20 phút.** Dựng lại bất biến được chọn từ Bài 02 và kiểm tra hai ý nền tảng. **Hoàn thành khi:** nêu được một điều kiện đầu vào và giải thích vì sao có thể phải xét lại lần tìm thấy đầu tiên.

1. Nêu bất biến của `lower_bound` và giải thích vì sao trả `lo` là đúng.

<details>
<summary>Đáp án</summary>

Với dữ liệu đã sắp xếp, mọi vị trí trước `lo` có giá trị nhỏ hơn giá trị cần tìm; mọi vị trí từ `hi` trở đi có giá trị lớn hơn hoặc bằng giá trị đó. Các vị trí chưa xác định nằm trong `[lo,hi)`. Mỗi nhánh duy trì phân hoạch và thu hẹp khoảng chưa xác định. Khi `lo == hi`, đây là vị trí đầu tiên thỏa điều kiện, hoặc n. Thứ tự đã sắp xếp cho phép loại bỏ vị trí. Trong bài này, trọng số không âm cho phép kết luận khoảng cách đã tối ưu.

</details>

2. `A -> B` có kéo theo `B -> A` không? Hai cạnh nối cùng cặp đỉnh có thể có chi phí khác nhau không?

<details>
<summary>Đáp án</summary>

Đồ thị có hướng không mặc nhiên có cạnh ngược lại. Có thể có cạnh song song: đi từ A đến B bằng một dịch vụ mất 4, bằng dịch vụ khác mất 7. Danh sách kề lưu các cạnh đi ra từ mỗi đỉnh. Muốn biểu diễn kết nối vô hướng, thêm cả hai hướng. Lab chấp nhận cạnh song song và cạnh từ một đỉnh về chính nó.

</details>

3. Từ A, tìm thấy C lần đầu với chi phí 9; sau đó tìm thấy A đến B đến C với chi phí 1+1. Khoảng cách tạm thời và đỉnh cha của C cần thay đổi thế nào?

<details>
<summary>Đáp án</summary>

Đổi khoảng cách từ 9 thành 2 và đổi đỉnh cha thành B. “Đã tìm thấy” chỉ cho biết có đường đi, chưa chứng minh đường đó tối ưu. Nếu chưa rõ, vẽ ba mũi tên, cộng chi phí và so sánh hai đường. Phần nền tảng cần bổ sung là dùng một mảng lưu khoảng cách tốt nhất đã biết và một mảng lưu đỉnh cha, trước khi xét cách chọn queue.

</details>

## 2. Mô hình, chạy từng bước và tính đúng

**Nền tảng · 50 phút.** Chạy hai chiến lược trên giấy, nêu bất biến và dựng phản ví dụ. **Hoàn thành khi:** giải thích được điều kiện dừng và vai trò của trọng số không âm.

### Ví dụ trước công thức

Dùng ID S=0, A=1, B=2, T=3. S có cạnh trực tiếp đến T với chi phí 10, và đường qua A, B gồm ba cạnh có chi phí 1 mỗi cạnh. T không có cạnh đi ra.

Dự đoán đường nào ít cạnh nhất, đường nào có tổng chi phí nhỏ nhất. Dijkstra có được dừng ngay khi S thêm T vào queue lần đầu không?

<details>
<summary>Đáp án</summary>

S đến T có một cạnh nhưng chi phí 10. S đến A đến B đến T có ba cạnh nhưng chi phí 3. Dừng khi thêm T vào queue sẽ trả 10 trước khi xét đường rẻ hơn. BFS trên đồ thị đã thay mọi trọng số bằng 1 trả lời câu hỏi về số cạnh, không trả lời câu hỏi về chi phí của đồ thị gốc.

</details>

Với đường P, chi phí là `cost(P) = tổng w(u,v) trên các cạnh của P`. Gọi `δ(s,v)` là chi phí nhỏ nhất từ s đến v; dùng vô cực nếu không tới được v. `dist[v]` là chi phí tốt nhất đã tìm thấy; ban đầu là vô cực, trừ `dist[s]=0`. Một bước **relaxation** thử đi qua u: nếu `dist[u] + w(u,v) < dist[v]`, cập nhật khoảng cách và `parent[v]=u`. Mỗi giá trị hữu hạn biểu diễn một đường có thật, nên không thể nhỏ hơn chi phí tối ưu.

**Điều kiện của lab:** đồ thị có hướng hữu hạn, không đổi trong lúc tìm kiếm, ID `0..V-1`, chi phí nguyên không âm. Trả một chi phí tối thiểu và dãy đỉnh tương ứng. Không tới được đích thì trả `null` và đường rỗng; nguồn trùng đích thì trả 0 và `[source]`. Chấp nhận cạnh song song và chu trình có chi phí 0. BFS yêu cầu thêm: mọi trọng số bằng 1. Khi tạo đồ thị, từ chối ID sai, trọng số âm và `long.MaxValue`; giá trị cuối dành cho vô cực. Nếu bất kỳ tổng chi phí ứng viên nào được Dijkstra xét đạt hoặc vượt giá trị này, ném `OverflowException`, kể cả khi ứng viên đó không cải thiện kết quả. Đây là giới hạn số học được quy định rõ, không phải khả năng xử lý số nguyên có độ lớn tùy ý.

### BFS: lần tìm thấy đầu tiên đủ khi trọng số bằng 1

Queue FIFO lấy đỉnh ra theo số cạnh không giảm. Khi xử lý lớp k, các đỉnh mới thuộc lớp k+1 được thêm phía sau các đỉnh đang chờ. Đánh dấu ngay khi thêm vào queue để chu trình hoặc nhiều cạnh đi vào cùng đỉnh không làm đỉnh đó được thêm lặp lại.

Bất biến: mỗi khoảng cách đã tìm thấy là số cạnh tối thiểu; queue giữ thứ tự khoảng cách không giảm và chỉ chứa tối đa hai lớp liên tiếp. Ban đầu chỉ có s với khoảng cách 0. Nếu đỉnh v vừa được tìm thấy có đường ngắn hơn k+1 cạnh, đỉnh trước v trên đường đó phải được xử lý ở lớp trước và đã tìm thấy v. Mâu thuẫn này chứng minh lần tìm thấy đầu tiên là tối ưu. Mã lab dừng khi lấy đích ra khỏi queue để thống nhất cách đếm thao tác.

Nếu mọi cạnh có cùng chi phí dương c, đường tối ưu giống trường hợp trọng số 1; nhân số cạnh với c sau khi tìm. Hàm `Bfs` trong lab chỉ nhận trọng số 1. Nếu mọi chi phí bằng 0, bất kỳ đường tới được đích nào cũng tối ưu với chi phí 0. Khi trộn cạnh 0 và cạnh dương, cần chiến lược khác; bài này dùng Dijkstra.

### Dijkstra: lấy ra ứng viên nhỏ nhất còn hợp lệ mới đủ

Trong bảng dưới, mỗi entry của queue là `(cost,node)`. Entry `(10,T)` vẫn còn sau khi khoảng cách tới T giảm thành 3. Đây là entry **stale**: chi phí lưu trong entry không còn bằng khoảng cách hiện tại.

| Entry hợp lệ vừa lấy ra | Cập nhật khoảng cách | Entry còn lại, sắp thứ tự để dễ đọc |
|---|---|---|
| (0,S) | T=10, A=1 | (1,A), (10,T) |
| (1,A) | B=2 | (2,B), (10,T) |
| (2,B) | T=3, parent[T]=B | (3,T), (10,T) |
| (3,T) | Đích đã tối ưu; trả kết quả | Không cần xét (10,T) |

Bất biến: mọi đỉnh đã xác định xong đều có khoảng cách tối ưu; mỗi khoảng cách tạm thời hữu hạn biểu diễn một đường có thật; mỗi đỉnh chưa xác định xong có khoảng cách hữu hạn đều có entry tương ứng trong queue. Chọn u có khoảng cách tạm thời nhỏ nhất. Giả sử có đường rẻ hơn đến u. Trên đường đó, gọi y là đỉnh đầu tiên chưa xác định xong và x là đỉnh ngay trước y đã xác định xong. Khi xử lý x, thuật toán đã đề xuất khoảng cách tới y không lớn hơn chi phí đoạn đầu của đường này. Các cạnh còn lại không âm nên chi phí đoạn đầu không lớn hơn toàn bộ đường được cho là rẻ hơn tới u. Khi đó `dist[y] < dist[u]`, mâu thuẫn với cách chọn u. Riêng nguồn, đường rỗng có chi phí 0 và chu trình không âm không thể cải thiện nó.

Cạnh 0 vẫn giữ được chứng minh: chi phí đoạn còn lại cần “không nhỏ hơn 0”, không cần dương. Chỉ cập nhật đỉnh cha khi chi phí giảm nghiêm ngặt, nên chu trình 0 có chi phí bằng nhau không gây cập nhật lặp. Sau khi xác định khoảng cách tới u, duyệt các cạnh đi ra từ u; đường tìm thấy về sau không thể cải thiện nó. Bỏ qua entry stale **trước** khi đếm đỉnh đã xác định xong hoặc xét điều kiện dừng. Có thể trả đích khi lấy ra entry nhỏ nhất còn hợp lệ, không phải lần đầu thêm đích vào queue.

### Điều gì làm hỏng chứng minh?

Dựng phản ví dụ với `S -> T (2)`, `S -> A (5)`, `A -> T (-10)`. Dijkstra dừng ở đích sẽ trả gì, và bước nào trong chứng minh không còn đúng?

<details>
<summary>Đáp án</summary>

Thuật toán lấy T ở chi phí 2 trước A ở chi phí 5 và trả 2. Đường qua A thực tế có chi phí -5. Đoạn đầu đến A có chi phí 5, lớn hơn toàn bộ đường có chi phí -5, nên lập luận về đoạn còn lại không âm bị phá vỡ. Không phải mọi cạnh âm đều làm kết quả sai, nhưng không còn bảo đảm chung. Bellman-Ford xử lý cạnh âm và phát hiện chu trình âm tới được từ nguồn; nếu chu trình đó nằm trên một đường đến đích, không có chi phí tối thiểu hữu hạn. Lab từ chối mọi cạnh âm khi tạo đồ thị, kể cả cạnh ở thành phần không nối với nguồn.

</details>

### Đếm chi phí theo đúng cách dùng queue

Với BFS, mỗi đỉnh vào queue tối đa một lần và mỗi cạnh đi ra được xét tối đa một lần. Khởi tạo mảng vẫn ghi V phần tử dù đích ở gần. Thời gian là O(V+E), bộ nhớ tìm kiếm O(V), ngoài bộ nhớ O(V+E) để lưu đồ thị.

Với Dijkstra trong lab, mỗi lần cải thiện nghiêm ngặt thêm một entry mới thay vì giảm key của entry cũ. Có tối đa E lần cải thiện và E+1 lần thêm; heap có thể giữ O(E+1) entry, gồm cả entry cũ. Mỗi thao tác heap có chi phí O(log(E+2)). Cận trên là `O(V + E log(E+2))` thời gian và O(V+E) bộ nhớ tìm kiếm. Với đồ thị đơn, E không vượt V², nên thường viết `O((V+E) log V)` khi V>=2. Khi có số cạnh song song tùy ý, giữ cận theo E. Dừng sớm có thể giảm số cạnh được xét nhưng không bỏ được chi phí khởi tạo mảng. Chỉ đếm “đỉnh đã thăm” sẽ bỏ sót công việc của queue.

Nghỉ - 10 phút, rời màn hình.

## 3. Đọc nguồn và áp dụng vào dự án

**Đọc tài liệu · 45 phút.** Đọc ba phần tài liệu được giới hạn dưới đây, rồi viết ba dòng nhận định/bằng chứng/giới hạn. **Hoàn thành khi:** mỗi nhận định có giả định hỗ trợ và một kết luận mà nguồn chưa chứng minh.

Đọc phần mô tả, mã giả và độ phức tạp của [Boost BFS](https://www.boost.org/doc/libs/1_85_0/libs/graph/doc/breadth_first_search.html) và [Boost Dijkstra](https://www.boost.org/doc/libs/1_85_0/libs/graph/doc/dijkstra_shortest_paths.html). Sau đó đọc Remarks của [.NET PriorityQueue](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.priorityqueue-2?view=net-10.0). Đây là thuật toán tham chiếu và tài liệu API; lab dùng implementation riêng với cách quản lý queue riêng.

Câu hỏi: khoảng cách của BFS đếm gì? Điều kiện đầu vào nào bảo đảm Dijkstra đúng? Queue của .NET có giữ FIFO khi priority bằng nhau không? Có được dùng thẳng độ phức tạp Dijkstra ghi trong Boost cho lab này không?

<details>
<summary>Đáp án</summary>

| Nhận định | Bằng chứng | Giả định hoặc giới hạn |
|---|---|---|
| BFS tối thiểu hóa số cạnh | Boost định nghĩa khoảng cách là số cạnh và dùng queue, đánh dấu khi tìm thấy | Không tối thiểu hóa thời gian đi đường khi chi phí khác nhau |
| Dijkstra chấp nhận trọng số không âm | Mô tả và mã giả relaxation trong Boost | Cạnh âm làm mất bảo đảm; O(V log V + E) ghi trên trang không phải cận cho heap chứa entry lặp của lab |
| PriorityQueue lấy priority nhỏ nhất | Microsoft mô tả min-heap bậc bốn và không bảo đảm FIFO khi priority bằng nhau | Lab dùng `(cost,node ID)` để xử lý tie nhất quán; không bảo đảm toàn bộ dãy đỉnh nhỏ nhất theo thứ tự từ điển |

Phân tích lab phải dựa trên số lần thêm và kích thước heap thực tế. Một nguồn có thể xác nhận cơ chế nhưng chưa xác nhận mọi implementation hay nhận định hiệu năng dùng cơ chế đó.

</details>

### Ứng dụng: dịch vụ .NET tìm đường trong kho

Giả sử SQL Server lưu vị trí trong kho và các kết nối có hướng, mỗi kết nối có chi phí nguyên `TravelSeconds`. Dịch vụ ASP.NET nạp một phiên bản thành danh sách kề không đổi, tìm đường cho request và trả `{graphVersion, cost, path}`. Angular vẽ đường. Phiên bản xác định chính xác đồ thị đã dùng; khi đóng một lối đi, tạo phiên bản mới thay vì sửa dữ liệu giữa lần tìm kiếm đang chạy.

Dùng BFS khi cần ít lần chuyển tiếp nhất và mỗi kết nối được tính như nhau. Dùng Dijkstra khi cần tổng số giây di chuyển nhỏ nhất. Không cộng giây và tiền phí nếu chưa xác định cách quy đổi và mục tiêu nghiệp vụ. Chỉ dùng lại cache khi phiên bản đồ thị, hai đầu và mục tiêu đều khớp. Tạo và kiểm tra đồ thị tốn O(V+E), nên dùng lại một snapshot cho nhiều truy vấn thay vì gọi SQL Server ở từng bước relaxation.

Nếu chi phí rẽ phụ thuộc hành lang vừa đi qua, chỉ lưu vị trí là chưa đủ. Dùng `(vị trí, hành lang đi vào)` làm trạng thái tìm kiếm. Nếu chi phí phụ thuộc thời điểm khởi hành, giả định cạnh có chi phí cố định không còn đủ. Hệ thống thực tế cần mô hình cho sự phụ thuộc này và thời điểm ghi nhận chi phí; lab chưa giải bài toán đó. Các bộ đếm cũng không tính thời gian chờ request, đọc database hay nạp đồ thị.

Bài tập thiết kế: nhóm muốn thời gian nhỏ nhất, sau đó ít lần chuyển tiếp nhất trong các đường có cùng thời gian. Priority `(cost,node ID)` của lab đã đủ chưa?

<details>
<summary>Đáp án</summary>

Chưa. Node ID chỉ quyết định thứ tự xử lý khi bằng chi phí. Dùng cặp `(tổng số giây, số lần chuyển tiếp)` làm khoảng cách, so sánh theo thứ tự từ điển, và cộng `(số giây của cạnh, 1)` ở mỗi bước. Khi số giây không âm và số lần chuyển tiếp tăng, lập luận rằng đi thêm không làm mục tiêu nhỏ đi vẫn đúng. Phải lưu và so sánh cả cặp mục tiêu khi relaxation và khi bỏ entry stale. Node ID có thể là tiêu chí phụ thứ ba của queue nhưng không thay mục tiêu thứ hai. Đây là thiết kế mở rộng được đề xuất, chưa thuộc điều kiện mà lab đã implement.

</details>

## 4. Case study: truy vấn tìm đường của OSRM

**Đọc mã nguồn · 45 phút.** Chạy một bước relaxation của OSRM và so sánh cách quản lý heap với lab. **Hoàn thành khi:** phân biệt được cơ chế đã xác minh, đánh đổi trong sản phẩm và phần lab không tái hiện.

Open Source Routing Machine cung cấp đường đi trên dữ liệu đường bộ OpenStreetMap. Ta đọc **v5.27.1, commit `4f3ee609ec1af40eb1f445c6706cfa5beb04c990`**, tập trung vào phần tìm đường dùng CH (Contraction Hierarchies). Đây là bài toán sản phẩm: truy vấn cần chọn đường lái xe phù hợp, không chỉ đếm ít đoạn đường nhất. [README](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/README.md#quick-start) minh họa bằng dữ liệu bản đồ Berlin, mô tả các pipeline tiền xử lý và khuyến nghị MLD làm lựa chọn mặc định; CH được nhắc cho ma trận khoảng cách rất lớn. Các mô tả đó không cho phép suy ra số đỉnh đã đo hay latency của truy vấn.

### Phạm vi đọc cụ thể

1. Trong [`profiles/car.lua`](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/profiles/car.lua#L15-L38), `weight_name` mặc định là `routability`; duration và distance là các lựa chọn đang được comment. Hàm xử lý rẽ còn tính chi phí phạt. **Trọng số là mục tiêu của profile, không mặc nhiên là quãng đường hay số giây di chuyển.**
2. Trong [`directShortestPathSearch`, specialization CH](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/src/engine/routing_algorithms/direct_shortest_path.cpp#L20-L64), mã lấy hai heap tìm kiếm xuôi và ngược, thêm các ứng viên đầu/cuối, gọi `search`, giải nén đường và dựng kết quả tuyến đường.
3. Trong [`routingStep`](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/include/engine/routing_algorithms/routing_base_ch.hpp#L117-L186), mã lấy node nhỏ nhất từ heap, xét điểm gặp với tìm kiếm ngược, quản lý cận trên chi phí đường, kiểm tra điều kiện dừng/bỏ qua nhánh rồi relaxation các cạnh đi ra.
4. Trong [`relaxOutgoingEdges`](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/include/engine/routing_algorithms/routing_base_ch.hpp#L51-L83), mã kiểm tra hướng cạnh, assert trọng số dương, tính tổng chi phí ứng viên, thêm node chưa thấy và đổi đỉnh cha cùng `DecreaseKey` khi chi phí giảm nghiêm ngặt. Phần này cho thấy relaxation trực tiếp ảnh hưởng quyết định tìm đường trong sản phẩm.

Bài tập: lấy u ra ở chi phí 2, cạnh từ u đến v có chi phí 3, v đang ở trong heap với chi phí 9. Những gì thay đổi? Nếu v đã có chi phí 5 thì sao?

<details>
<summary>Đáp án</summary>

Ứng viên có chi phí 5. Khi v đang ở 9, đổi đỉnh cha của v thành u, đổi chi phí thành 5 và giảm key trong heap. Nếu v đã ở 5, phép so sánh nghiêm ngặt không thỏa nên giữ nguyên đỉnh cha. Mã kiểm tra cờ hướng trước khi xét cạnh. Trong lab, trường hợp đầu thêm entry `(5,v)` mới và để `(9,v)` được bỏ qua về sau; OSRM sửa entry trong heap có index.

</details>

### Quyết định trong sản phẩm và giới hạn

**Đã xác minh:** phần CH này chọn node nhỏ nhất từ heap và cải thiện khoảng cách theo trọng số; assert trọng số cạnh được duyệt phải dương, xét hướng xuôi/ngược và trả đường đã giải nén. Lab cho phép cạnh 0 nên có phạm vi rộng hơn assert đó. OSRM dùng offset ở hai đầu, gồm cả offset khởi tạo âm: comment gần `routingStep` giải thích điều chỉnh điều kiện dừng. Các offset này không cho phép dùng cạnh đường bộ âm tùy ý trong Dijkstra của lab.

**Suy luận thiết kế:** thay cách chọn theo trọng số bằng các lớp FIFO thường sẽ tối ưu số đoạn và có thể chọn đường chậm hơn hoặc kém phù hợp. Ta suy ra hệ quả từ mục tiêu và thuật toán; không khẳng định maintainer đã ghi nhận một thí nghiệm BFS bị loại. Tiền xử lý và heap có index cần thêm cấu trúc dữ liệu, làm việc bảo trì phức tạp hơn để giảm công việc khi truy vấn. Mã xác nhận có các cơ chế đó; phần đọc này không đo mức cải thiện.

Lab chỉ tái hiện ý tưởng chọn khoảng cách nhỏ nhất và relaxation. Lab không tái hiện điều kiện dừng hai chiều, cạnh rút gọn CH, bỏ qua nhánh, ghép tọa độ vào bản đồ, mô hình rẽ hay benchmark API của OSRM. Với dự án kho, trước hết áp dụng mục tiêu rõ ràng và phiên bản đồ thị không đổi; chỉ chọn công cụ tìm đường phức tạp hơn khi quy mô đồ thị và lượng truy vấn cần đến nó.

Ăn trưa và nghỉ - 30 phút.

## 5. Lab C#: implement, kiểm tra và sửa lỗi

**Lab · 75 phút.** Chạy demo, đọc implementation, chạy kiểm tra và giải thích lỗi cố ý bên dưới. **Hoàn thành khi:** lệnh kiểm tra tính đúng thành công và giải thích được vì sao đích đã tối ưu khi lấy ra, kể cả với cạnh 0.

Viết hai hàm tìm đường theo quy tắc ở mục 2, gồm đỉnh cha, đích không tới được và cập nhật nghiêm ngặt. Chạy demo, kiểm tra và thí nghiệm, rồi giải thích lỗi dưới đây. Nếu cài đặt vượt 15 phút, chuyển sang đọc lời giải.

<details>
<summary>Đáp án - toàn bộ lab chạy được</summary>

Dùng SDK **10.0.401**, runtime **10.0.12**, target **net10.0**; tắt roll-forward cho SDK/runtime. Không cần package ngoài hay database. Giải nén ZIP hoặc tạo mọi file dưới đây tính từ `dotnet`, rồi chạy trong thư mục đó. Cài SDK/reference pack lần đầu có thể cần mạng; sau khi restore thành công, lệnh no-restore chạy được offline.

Graph sao chép mảng kề; ReadOnlySpan cung cấp góc nhìn chỉ đọc. Đỉnh cha dựng lại một đường tối ưu, không phải mọi đường đồng chi phí hay ID cạnh song song. Khoảng cách null biểu diễn không tới được, khác chi phí 0. Cập nhật nghiêm ngặt và các đỉnh đã tối ưu ngăn chu trình đỉnh cha qua cạnh 0.

`global.json`:

<!-- lab-file: global.json -->
```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
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
</Project>
```

`LessonLab/Routes.cs`:

<!-- lab-file: LessonLab/Routes.cs -->
```csharp
// Original teaching code, MIT. This is not adapted from OSRM.
public readonly record struct Link(int From, int To, long Cost);
public readonly record struct Edge(int To, long Cost);

public sealed class Graph
{
    private readonly Edge[][] adjacency;
    public int Count => adjacency.Length;
    public bool UnitCosts { get; }

    public Graph(int count, params Link[] links)
    {
        if (count <= 0) throw new ArgumentOutOfRangeException(nameof(count));
        ArgumentNullException.ThrowIfNull(links);
        var lists = Enumerable.Range(0, count).Select(_ => new List<Edge>()).ToArray();
        bool unit = true;
        foreach (var link in links)
        {
            if ((uint)link.From >= (uint)count || (uint)link.To >= (uint)count)
                throw new ArgumentOutOfRangeException(nameof(links), "Invalid node ID.");
            if (link.Cost < 0 || link.Cost == long.MaxValue)
                throw new ArgumentOutOfRangeException(nameof(links), "Cost must be in [0, long.MaxValue).");
            unit &= link.Cost == 1;
            lists[link.From].Add(new Edge(link.To, link.Cost));
        }
        adjacency = lists.Select(list => list.ToArray()).ToArray();
        UnitCosts = unit;
    }

    public ReadOnlySpan<Edge> Neighbors(int node) => adjacency[node];
}

public sealed record Route(long? Distance, int[] Path, int Settled, long Scanned, long Stale);

public static class Routes
{
    private static void Validate(Graph graph, int source, int target)
    {
        ArgumentNullException.ThrowIfNull(graph);
        if ((uint)source >= (uint)graph.Count || (uint)target >= (uint)graph.Count)
            throw new ArgumentOutOfRangeException(nameof(source), "Invalid source or target.");
    }

    private static Route Finish(long[] distance, int[] parent, int target,
                                int settled, long scanned, long stale)
    {
        if (distance[target] == long.MaxValue)
            return new Route(null, [], settled, scanned, stale);
        var path = new List<int>();
        for (int node = target; node != -1; node = parent[node]) path.Add(node);
        path.Reverse();
        return new Route(distance[target], path.ToArray(), settled, scanned, stale);
    }

    public static Route Bfs(Graph graph, int source, int target)
    {
        Validate(graph, source, target);
        if (!graph.UnitCosts)
            throw new ArgumentException("BFS requires every cost to be 1.", nameof(graph));
        var distance = Enumerable.Repeat(long.MaxValue, graph.Count).ToArray();
        var parent = Enumerable.Repeat(-1, graph.Count).ToArray();
        var queue = new Queue<int>();
        distance[source] = 0;
        queue.Enqueue(source);
        int settled = 0;
        long scanned = 0;
        while (queue.TryDequeue(out int node))
        {
            settled++;
            if (node == target) break;
            foreach (var edge in graph.Neighbors(node))
            {
                scanned++;
                if (distance[edge.To] != long.MaxValue) continue;
                distance[edge.To] = distance[node] + 1;
                parent[edge.To] = node;
                queue.Enqueue(edge.To);
            }
        }
        return Finish(distance, parent, target, settled, scanned, 0);
    }

    public static Route Dijkstra(Graph graph, int source, int target)
    {
        Validate(graph, source, target);
        var distance = Enumerable.Repeat(long.MaxValue, graph.Count).ToArray();
        var parent = Enumerable.Repeat(-1, graph.Count).ToArray();
        var queue = new PriorityQueue<int, (long Cost, int Node)>();
        distance[source] = 0;
        queue.Enqueue(source, (0, source));
        int settled = 0;
        long scanned = 0, stale = 0;
        while (queue.TryDequeue(out int node, out var priority))
        {
            if (priority.Cost != distance[node]) { stale++; continue; }
            settled++;
            if (node == target) break;
            foreach (var edge in graph.Neighbors(node))
            {
                scanned++;
                // long.MaxValue is reserved for unreachable, not a finite distance.
                if (edge.Cost >= long.MaxValue - priority.Cost)
                    throw new OverflowException("Reached candidate exceeds the finite-distance range.");
                long candidate = priority.Cost + edge.Cost;
                if (candidate >= distance[edge.To]) continue;
                distance[edge.To] = candidate;
                parent[edge.To] = node;
                queue.Enqueue(edge.To, (candidate, edge.To));
            }
        }
        return Finish(distance, parent, target, settled, scanned, stale);
    }
}
```

`LessonLab/Program.cs`:

<!-- lab-file: LessonLab/Program.cs -->
```csharp
if (args.Length == 0)
{
    var graph = new Graph(4, new(0, 3, 10), new(0, 1, 1), new(1, 2, 1), new(2, 3, 1));
    var hops = Routes.Bfs(new Graph(4, new(0, 3, 1), new(0, 1, 1), new(1, 2, 1), new(2, 3, 1)), 0, 3);
    var weighted = Routes.Dijkstra(graph, 0, 3);
    Console.WriteLine($"BFS unit projection: hops={hops.Distance}, path={string.Join("->", hops.Path)}");
    Console.WriteLine($"Dijkstra original: cost={weighted.Distance}, path={string.Join("->", weighted.Path)}");
    Console.WriteLine("The BFS path costs 10 in the original graph. Dijkstra costs 3.");
}
else if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

`LessonLab/Checks.cs`:

<!-- lab-file: LessonLab/Checks.cs -->
```csharp
public static class Checks
{
    private static int queries;
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

    public static long PathCost(Graph graph, int[] path)
    {
        long sum = 0;
        for (int i = 1; i < path.Length; i++)
        {
            long best = long.MaxValue;
            foreach (var edge in graph.Neighbors(path[i - 1]))
                if (edge.To == path[i]) best = Math.Min(best, edge.Cost);
            Require(best != long.MaxValue, "Path uses a missing edge.");
            sum = checked(sum + best);
        }
        return sum;
    }

    // Independent oracle for small graphs: repeated relaxation, no priority queue.
    private static long? Oracle(Graph graph, int source, int target)
    {
        var distance = Enumerable.Repeat(long.MaxValue, graph.Count).ToArray();
        distance[source] = 0;
        for (int pass = 0; pass < graph.Count - 1; pass++)
        {
            bool changed = false;
            for (int node = 0; node < graph.Count; node++)
            {
                if (distance[node] == long.MaxValue) continue;
                foreach (var edge in graph.Neighbors(node))
                {
                    long candidate = checked(distance[node] + edge.Cost);
                    if (candidate >= distance[edge.To]) continue;
                    distance[edge.To] = candidate;
                    changed = true;
                }
            }
            if (!changed) break;
        }
        return distance[target] == long.MaxValue ? null : distance[target];
    }

    private static void Compare(Graph graph, int source, int target, bool bfs = false)
    {
        Route route = bfs ? Routes.Bfs(graph, source, target) : Routes.Dijkstra(graph, source, target);
        Require(route.Distance == Oracle(graph, source, target), "Distance differs from oracle.");
        if (route.Distance is null) Require(route.Path.Length == 0, "Unreachable path must be empty.");
        else
        {
            Require(route.Path[0] == source && route.Path[^1] == target, "Wrong path endpoints.");
            Require(route.Path.Length <= graph.Count, "Parent cycle.");
            Require(PathCost(graph, route.Path) == route.Distance, "Path cost differs from distance.");
        }
        queries++;
    }

    public static void Run()
    {
        var trap = new Graph(4, new(0, 3, 10), new(0, 1, 1), new(1, 2, 1), new(2, 3, 1));
        Compare(trap, 0, 3);
        Require(Routes.Dijkstra(trap, 0, 3).Distance == 3, "Early-discovery regression.");
        Throws<ArgumentException>(() => Routes.Bfs(trap, 0, 3));
        var stale = new Graph(5, new(0, 1, 9), new(0, 2, 1), new(2, 1, 1), new(1, 3, 1));
        Compare(stale, 0, 4);
        Require(Routes.Dijkstra(stale, 0, 4).Stale == 1, "Expected a skipped old entry.");
        var zero = new Graph(4, new(0, 1, 0), new(1, 0, 0), new(1, 2, 2), new(0, 2, 9),
                             new(1, 2, 2), new(2, 2, 0));
        Compare(zero, 0, 2); Compare(zero, 0, 0); Compare(zero, 0, 3);
        var single = new Graph(1);
        Compare(single, 0, 0); Compare(single, 0, 0, true);
        var tie = new Graph(4, new(0, 2, 1), new(0, 1, 1), new(1, 3, 1), new(2, 3, 1));
        Compare(tie, 0, 3); Compare(tie, 0, 3, true);
        Require(Routes.Dijkstra(tie, 0, 3).Path.SequenceEqual(new[] { 0, 1, 3 }), "Tuple tie-break.");
        var large = new Graph(3, new(0, 1, long.MaxValue - 1), new(1, 2, 0));
        Require(Routes.Dijkstra(large, 0, 2).Distance == long.MaxValue - 1, "Finite-range boundary.");
        Throws<OverflowException>(() => Routes.Dijkstra(
            new Graph(3, new(0, 1, long.MaxValue - 1), new(1, 2, 1)), 0, 2));
        Throws<ArgumentOutOfRangeException>(() => new Graph(0));
        Throws<ArgumentOutOfRangeException>(() => new Graph(2, new Link(0, 1, -1)));
        Throws<ArgumentOutOfRangeException>(() => new Graph(2, new Link(0, 1, long.MaxValue)));
        Throws<ArgumentOutOfRangeException>(() => new Graph(2, new Link(0, 2, 1)));
        Throws<ArgumentOutOfRangeException>(() => Routes.Dijkstra(single, -1, 0));
        Throws<ArgumentOutOfRangeException>(() => Routes.Bfs(single, 0, 1));
        Throws<ArgumentNullException>(() => Routes.Dijkstra(null!, 0, 0));

        var random = new Random(20261007);
        for (int sample = 0; sample < 80; sample++)
        {
            int n = random.Next(2, 9);
            var links = new List<Link>();
            for (int from = 0; from < n; from++)
                for (int to = 0; to < n; to++)
                    if (random.Next(4) == 0) links.Add(new(from, to, random.Next(0, 8)));
            var graph = new Graph(n, links.ToArray());
            var unit = new Graph(n, links.Select(link => link with { Cost = 1 }).ToArray());
            for (int source = 0; source < n; source++)
                for (int target = 0; target < n; target++)
                {
                    Compare(graph, source, target);
                    Compare(unit, source, target);
                    Compare(unit, source, target, true);
                }
        }
        Console.WriteLine($"PASS: {queries} oracle/path comparisons plus deterministic boundary and rejection checks.");
    }
}
```

`LessonLab/Experiment.cs`:

<!-- lab-file: LessonLab/Experiment.cs -->
```csharp
public static class Experiment
{
    public static void Run()
    {
        Console.WriteLine("n,mode,algorithm,result,originalCost,settled,scanned,stale");
        foreach (int n in new[] { 64, 256, 1024 })
        {
            var unit = new List<Link> { new(0, n - 1, 1) };
            var weighted = new List<Link> { new(0, n - 1, 2L * n) };
            for (int i = 0; i < n - 1; i++)
            {
                unit.Add(new(i, i + 1, 1));
                weighted.Add(new(i, i + 1, 1));
            }
            var unitGraph = new Graph(n, unit.ToArray());
            var weightedGraph = new Graph(n, weighted.ToArray());
            Print(n, "unit", "BFS", Routes.Bfs(unitGraph, 0, n - 1), unitGraph);
            Print(n, "unit", "Dijkstra", Routes.Dijkstra(unitGraph, 0, n - 1), unitGraph);
            // Explicitly changes the objective to fewest edges, not weighted cost.
            Print(n, "weighted-projection", "BFS", Routes.Bfs(unitGraph, 0, n - 1), weightedGraph);
            Print(n, "weighted", "Dijkstra", Routes.Dijkstra(weightedGraph, 0, n - 1), weightedGraph);
        }
    }

    private static void Print(int n, string mode, string algorithm, Route route, Graph original)
    {
        Console.WriteLine($"{n},{mode},{algorithm},{route.Distance},{Checks.PathCost(original, route.Path)}," +
                          $"{route.Settled},{route.Scanned},{route.Stale}");
    }
}
```

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

Kết quả demo dự kiến:

```text
BFS unit projection: hops=1, path=0->3
Dijkstra original: cost=3, path=0->1->2->3
The BFS path costs 10 in the original graph. Dijkstra costs 3.
```

Thuật toán tham chiếu dùng relaxation lặp trên trọng số nhỏ không âm, nhưng không có priority queue. Các ca đối chiếu đường/khoảng cách và BFS trọng số 1 gồm entry stale thực sự được lấy ra, đỉnh không tới được, đường đồng chi phí, cạnh song song/tự nối, chu trình 0 và biên từ chối số học. Các ca có seed là bằng chứng hữu hạn; lập luận ở mục 2 chứng minh kết quả tổng quát. Lệnh kiểm tra in PASS hoặc trả exit code khác 0. Trước hết xem điều kiện nào sai; không để tổng ứng viên tự tràn.

</details>

Bài tập: developer thêm `if (edge.To == target) return ...;` ngay sau khi thêm một khoảng cách được cải thiện vào queue. Giải thích lỗi và cách sửa. Sau đó giải thích vì sao đổi `candidate >= distance[edge.To]` thành `candidate > distance[edge.To]` cũng nguy hiểm.

<details>
<summary>Đáp án</summary>

Thay đổi đầu trả T ở chi phí 10 trong demo trước khi tìm thấy đường chi phí 3. Bỏ câu lệnh dừng đó. Giữ phép kiểm tra đích sau khi lấy entry ra và sau khi bỏ entry stale, như `Routes.cs`. Ca test cố định xác nhận demo phải trả 3, giúp tái hiện hồi quy mà không sửa hàm tìm đường.

Thay đổi thứ hai thêm cả ứng viên đồng chi phí và đổi đỉnh cha khi bằng nhau. Với chu trình 0 tới được từ nguồn, chương trình có thể thêm entry mãi; cạnh 0 tự nối còn có thể đặt đỉnh cha thành chính nó. Chỉ nhận cải thiện nghiêm ngặt: bỏ qua `candidate >= distance[edge.To]`. Test có cả chu trình 0 và cạnh 0 tự nối để kiểm tra điều kiện này. Đánh dấu ngay khi tìm thấy là đúng với điều kiện trọng số 1 của BFS; chép cách đó vào Dijkstra sẽ chặn những lần cải thiện về sau.

</details>

Nghỉ - 10 phút, rời màn hình.

## 6. Thí nghiệm có kiểm soát: ít thao tác vẫn có thể trả lời sai mục tiêu

**Thí nghiệm · 45 phút.** Dự đoán số thao tác, chạy `--experiment`, rồi đổi một trọng số hoặc thứ tự cạnh kề. **Hoàn thành khi:** phân biệt được số đếm quan sát, cận độ phức tạp và nhận định về latency.

Dùng chuỗi có hướng gồm n đỉnh, các cạnh `0 -> 1 -> ... -> n-1`, thêm cạnh trực tiếp `0 -> n-1` được lưu trước. Với n=64, 256, 1024, giữ cấu trúc và đích giống nhau trong mỗi cặp. Ở trường hợp trọng số 1, mọi cạnh có chi phí 1. Ở trường hợp có trọng số khác nhau, chỉ đổi cạnh trực tiếp thành `2*n`; cạnh trên chuỗi vẫn là 1. So sánh Dijkstra trên đồ thị có trọng số với BFS trên một bản đã thay rõ ràng mọi trọng số bằng 1, rồi tính chi phí đường BFS theo đồ thị gốc.

**Giả thuyết:** BFS trên bản trọng số 1 làm ít việc nhưng tối ưu sai mục tiêu của đồ thị có trọng số. Dijkstra phải xử lý chuỗi để xác nhận đường rẻ hơn. Đây là phép đếm thao tác xác định, không phải benchmark thời gian. `Settled` đếm lần lấy entry hợp lệ ra, gồm cả đích; `Scanned` đếm cạnh đi ra đã xét; `Stale` đếm entry cũ bị bỏ qua. Không tính tạo đồ thị, khởi tạo mảng, đảo đường, số phép so sánh trong heap hay công việc SQL/API.

Dự đoán bốn dòng khi n=64 và giải thích vì sao Dijkstra trên đồ thị trọng số 1 có thể xử lý thêm một đỉnh so với BFS.

<details>
<summary>Đáp án</summary>

| Trường hợp | Thuật toán | Kết quả | Chi phí theo đồ thị gốc | Settled | Scanned | Stale |
|---|---|---|---|---|---|---|
| Trọng số 1 | BFS | 1 cạnh | 1 | 2 | 2 | 0 |
| Trọng số 1 | Dijkstra | Chi phí 1 | 1 | 3 | 3 | 0 |
| Bản thay trọng số bằng 1 | BFS | 1 cạnh | 128 | 2 | 2 | 0 |
| Có trọng số | Dijkstra | Chi phí 63 | 63 | 64 | 64 | 0 |

BFS đọc cạnh trực tiếp trước, thêm đích vào queue trước đỉnh 1. Hai ứng viên của Dijkstra đều có chi phí 1, nên priority `(cost,node ID)` lấy đỉnh 1 trước đỉnh 63. Đỉnh 1 xét thêm một cạnh trước khi lấy đích ra. Trong trường hợp có trọng số, khoảng cách tới đích giữ ở 128 cho đến khi chuỗi cải thiện nó thành 63. Entry đích cũ vẫn trong heap lúc trả kết quả, nên `Stale=0` không có nghĩa là chưa tạo entry stale. Ca test đích không tới được chạy hết heap và kiểm tra nhánh bỏ entry cũ.

</details>

Với n=256 và 1024, Dijkstra trả chi phí 255 và 1023; đường BFS trên bản trọng số 1 có chi phí gốc 512 và 2048. Dijkstra xác định xong n đỉnh và xét n cạnh với cấu trúc này. Chạy lệnh để đối chiếu dự đoán với output.

Biến thể: đổi trọng số cạnh trực tiếp thành 0; sau đó khôi phục trọng số và đưa cạnh này xuống cuối danh sách kề. Dự đoán khoảng cách và số thao tác trước khi chạy.

<details>
<summary>Đáp án</summary>

Khi cạnh trực tiếp có chi phí 0, Dijkstra lấy đích ngay sau nguồn: khoảng cách 0, settled 2, scanned 2. BFS trên bản trọng số 1 vẫn chọn một cạnh; tính đường đó trên đồ thị gốc mới cũng được 0, tình cờ trùng tối ưu có trọng số. Điều này không chứng minh BFS đúng cho mọi đồ thị có trọng số khác nhau.

Khi cạnh trực tiếp nằm cuối trong đồ thị trọng số 1, BFS thêm đỉnh 1 trước, rồi mới thêm đích. Nó xử lý 3 đỉnh và xét 3 cạnh; số cạnh tối thiểu vẫn là 1. Thứ tự tuple của Dijkstra giữ số đếm ở 3/3. Tối ưu có trọng số và số đếm n/n không đổi. Thứ tự danh sách kề có thể đổi số thao tác và đường trả về khi hòa, nhưng không đổi khoảng cách tối ưu.

</details>

**Giới hạn diễn giải:** quan sát chỉ xác minh workload và các bộ đếm này. Chưa xếp hạng thời gian chạy, áp lực GC, bộ nhớ heap tối đa hay p99 của dịch vụ. Tăng n chưa làm chuỗi này đại diện cho bản đồ đường bộ: đồ thị thực có nhánh, nhiều đường thay thế, phân bố bậc đỉnh khác nhau và nhiều truy vấn. Muốn đo thời gian, cần cố định cấu trúc cùng mục tiêu hợp lệ, chủ động tách chi phí chuẩn bị, warm up runtime, đo lặp và báo độ biến động. Không dùng kết quả nhanh cho một mục tiêu khác làm mốc so sánh hiệu năng.

Nghỉ - 10 phút, rời màn hình.

## 7. Đổi ngữ cảnh: ràng buộc đường đi làm thay đổi trạng thái

**Bài tập vận dụng · 35 phút.** Giải yêu cầu tìm đường có giới hạn và chỉ ra vì sao một khoảng cách cho mỗi vị trí làm mất thông tin. **Hoàn thành khi:** nêu được trạng thái mới, phép chuyển và điều kiện chấp nhận.

Kho cho phép qua tối đa một hành lang tính phí. Cần thời gian nhỏ nhất trong giới hạn đó. Các kết nối có hướng: S đến X mất 1 giây và dùng một lượt tính phí; S đến Y mất 2 giây, không tính phí; Y đến X mất 0 giây, không tính phí; X đến T mất 1 giây và dùng một lượt tính phí. Dijkstra có được giữ riêng thời gian nhỏ nhất đến X rồi loại mọi lần đến chậm hơn không? Thiết kế lời giải C# dùng hàm đã có và nêu kết quả của đồ thị này.

<details>
<summary>Đáp án</summary>

Không. Đến X nhanh nhất mất 1 giây nhưng đã dùng lượt tính phí, nên không thể đi tiếp tới T. Đi qua Y đến X mất 2 giây nhưng còn lượt; đến T với tổng thời gian 3 giây. Lưu `(vị trí, số lượt đã dùng)` thay vì chỉ vị trí. Với giới hạn K, mã hóa thành `location*(K+1)+usedPaid`. Cạnh dùng p lượt nối `(u,k)` đến `(v,k+p)` chỉ khi `k+p <= K`; trọng số vẫn là số giây không âm. Đồ thị mở rộng có `(K+1)*V` trạng thái và tối đa `(K+1)*E` cạnh, nên giới hạn lớn sẽ tốn thêm bộ nhớ thực sự.

Thêm một đích phụ, nối mọi trạng thái hợp lệ ở T đến đó bằng cạnh 0. Dijkstra hiện có sẽ lấy chi phí nhỏ nhất trên các trạng thái này; bỏ đỉnh phụ cuối khi hiển thị đường. Instance đầy đủ của ví dụ là:

```csharp
// IDs: S0=0,S1=1,X0=2,X1=3,Y0=4,Y1=5,T0=6,T1=7,Goal=8.
var constrained = new Graph(9,
    new(0, 3, 1),                 // S0 -> X1: consume one paid crossing.
    new(0, 4, 2), new(1, 5, 2),  // S -> Y: no paid crossing.
    new(4, 2, 0), new(5, 3, 0),  // Y -> X: no paid crossing.
    new(2, 7, 1),                 // X0 -> T1: consume one paid crossing.
    new(6, 8, 0), new(7, 8, 0)); // Allowed T states -> synthetic goal.
Route answer = Routes.Dijkstra(constrained, 0, 8);
Console.WriteLine($"cost={answer.Distance}, states={string.Join("->", answer.Path)}");
// cost=3, states=0->4->2->7->8
```

Đây là mở rộng mô hình đồ thị, không phải đổi chứng minh Dijkstra. Khoảng cách rẻ nhất theo vị trí chưa đủ vì bước tiếp theo có hợp lệ hay không phụ thuộc số lượt đã dùng. Với K=0, không thêm cạnh tiêu tốn lượt; nếu mọi trạng thái đích hợp lệ đều không tới được, đích phụ cũng không tới được. Bỏ ràng buộc tính phí thì đường nhanh nhất ban đầu là S-X-T với chi phí 2.

</details>

## 8. Tổng hợp và câu hỏi tiếp theo

**Tổng hợp · 45 phút.** Viết ghi chú quyết định ngắn: mục tiêu, bất biến, cách quản lý queue, phạm vi số học và điều mà thí nghiệm chưa chứng minh. **Hoàn thành khi:** ghi chú dùng phản ví dụ để bác bỏ một chiến lược sai và nêu một câu hỏi còn mở.

Dùng đề cuối: đồng nghiệp nói “Hai thuật toán đều tìm được đường; BFS thăm ít đỉnh hơn, nên deploy BFS để tối ưu số giây di chuyển.” Trả lời bằng năm hoặc sáu câu dựa trên bằng chứng trong bài. Sau đó chọn một câu để ôn lại: vì sao Dijkstra xác định được khoảng cách tối ưu, vì sao có entry stale, hoặc vì sao ràng buộc đường đi làm mở rộng trạng thái.

<details>
<summary>Đáp án</summary>

BFS tối thiểu hóa số cạnh; số giây di chuyển cần tối thiểu hóa tổng trọng số. Đường trực tiếp chi phí 10 và đường ba cạnh chi phí 3 là phản ví dụ cho việc dùng lớp FIFO với mục tiêu đó. Dijkstra xác định khoảng cách tối ưu khi lấy ứng viên nhỏ nhất còn hợp lệ vì đoạn còn lại không âm không thể làm đường chưa xử lý rẻ hơn. Heap của lab có thể giữ nhiều entry cho một đỉnh, nên phải bỏ entry stale trước khi xử lý hoặc dừng. Thí nghiệm cho thấy ít thao tác có thể đang giải một bài toán khác; chưa chứng minh latency hay bộ nhớ trong production. Tôi sẽ dùng hàm tìm đường có trọng số trên một phiên bản đồ thị, rồi kiểm tra xem ước lượng thời gian phụ thuộc thời điểm có cần mô hình phong phú hơn không.

</details>

Mô hình cần giữ: xác định mục tiêu và trạng thái trước, rồi chứng minh thứ tự xử lý ứng viên cùng điều kiện dừng. BFS và Dijkstra đều dùng mảng khoảng cách/đỉnh cha nhưng xác nhận tính tối ưu ở thời điểm khác nhau. Câu hỏi tiếp theo là chọn thuật toán thế nào khi giả định thay đổi, chẳng hạn có chi phí âm hoặc có một ước lượng cận dưới hữu ích cho phần đường còn lại.

Nguồn được dẫn ngay tại nhận định tương ứng. [Mã OSRM](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/include/engine/routing_algorithms/routing_base_ch.hpp) thuộc Project OSRM contributors, theo BSD-2-Clause; bài dẫn link và phân tích, không sao chép mã đó. Toàn bộ C# ở đây là mã giảng dạy tự viết theo MIT; nội dung bài tự viết theo CC BY 4.0.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 02 - Tìm biên](../boundary-search/lesson.md) - Ôn cách bất biến và điều kiện đầu vào chứng minh điều kiện dừng.
- [Hướng dẫn lab C#](../../../labs/shortest-paths/dotnet/README.vi.md) - Cài SDK, kiểm tra tính đúng, thí nghiệm và tải mã nguồn.

---

[← Bài trước: Bài 02 - Tìm biên bằng binary search và đếm sự kiện theo khoảng thời gian](../boundary-search/lesson.md) · [Danh sách bài học](../../README.md) · [Bài sau: Bài 04 - Quy hoạch động và xấp xỉ: chọn công việc trong một ngân sách →](../2026-10-08-dp-approximation/lesson.md)
<!-- LESSON_NAVIGATION_END -->
