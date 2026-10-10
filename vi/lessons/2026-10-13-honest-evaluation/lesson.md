# Bài 09 - Đánh giá trung thực: học quy tắc, không học từ test

[English](../../../lessons/2026-10-13-honest-evaluation/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/honest-evaluation/dotnet-lab.zip)

Dịch vụ hỗ trợ ASP.NET muốn cảnh báo ticket có nguy cơ quá hạn 24 giờ. Quy tắc không cảnh báo gì có thể đạt accuracy cao nhưng bỏ sót mọi ticket trễ. Quy tắc phức tạp hơn có thể đạt điểm tuyệt đối nếu input đã tiết lộ kết quả về sau. Cả hai điểm số đều chưa trả lời được quy tắc có ích lúc ticket vừa đến hay không.

**Mục tiêu:** học một ngưỡng đơn giản, so với hai baseline, bảo vệ ranh giới train/validation/test và giải thích lỗi theo chi phí đã nêu. Planner chọn đánh giá hệ học sau thiết kế thí nghiệm. Bài dùng lại đơn vị quan sát, giả định mô hình, bất biến và đối chiếu độc lập. Feature, label, việc học tham số, đánh giá trên dữ liệu giữ riêng và các metric phân loại được giải thích tại đây; không cần mặc định đã học machine learning.

## Ý cốt lõi

- **Học là chọn quy tắc từ ví dụ.** Ticket lịch sử có điểm lúc tiếp nhận và kết quả về sau giúp chọn ngưỡng. Ngưỡng được học; kết quả của ticket mới vẫn chưa biết khi quy tắc hành động.
- **Đánh giá cần ranh giới thông tin.** Học từ train, chọn ứng viên bằng validation, rồi kiểm tra lựa chọn đã cố định trên test. Sao kết quả quá hạn vào feature lúc tiếp nhận vẫn vượt ranh giới này dù các ID khác nhau.
- **Các loại lỗi có hậu quả khác nhau.** Bỏ sót ticket trễ khác với cảnh báo không cần thiết cho ticket đúng hạn. Chỉ đếm dự đoán đúng sẽ che sự khác biệt đó.
- **Đơn vị quyết định nhận định.** Ticket mới của khách hàng đã biết khác với ticket của khách hàng hoàn toàn mới. Giữ riêng các dòng vẫn có thể để lộ lịch sử của cùng khách hàng.

Có thể chỉ đọc bảng chạy và các đáp án. Giới hạn setup trong 15 phút của phần lab. Toàn bộ ticket và đơn vị chi phí đều giả lập; bài không đo latency production hay tiền tiết kiệm thực tế.

## 1. Ôn ranh giới trước khi thêm mô hình

**Ôn tập · 20 phút.** Dựng lại ba đáp án planner chọn và nối chúng với thông tin có sẵn lúc ra quyết định. **Hoàn thành khi:** mỗi đáp án có giả định và trường hợp biên.

1. Vì sao chênh lệch cặp ngẫu nhiên hướng tới tác động trung bình nhóm cố định nhưng không khôi phục tác động từng đơn vị?

<details>
<summary>Đáp án</summary>

Hai hướng gán cùng xác suất cho nửa tổng tác động cặp; trung bình các cặp cho tau theo kỳ vọng cách gán. Mỗi đơn vị thật chỉ cho kết quả hành động nhận được. Cần thiết kế gán đã nêu, nhất quán/không ảnh hưởng chéo và kết quả đầy đủ; phân nhóm ngẫu nhiên chưa làm nhóm đại diện.

</details>

2. Vì sao transaction đọc WAL cũ phải kết thúc trước khi xét lại phép ghi?

<details>
<summary>Đáp án</summary>

Mốc kết thúc giữ nguyên; sau commit khác, nâng lên ghi có thể trả BUSY_SNAPSHOT. Kết thúc/rollback transaction, đọc mới và xét lại quyết định có cận. Chờ hoặc lặp snapshot cũ chưa làm mới nó.

</details>

3. Đọc kết quả âm của BinarySearch trong .NET như thế nào? Khi có giá trị trùng, kết quả tìm thấy có thay được lower_bound không?

<details>
<summary>Đáp án</summary>

Nếu r<0, vị trí chèn là ~r, không phải -r. Khi tìm thấy, Array.BinarySearch/List<T>.BinarySearch có thể trả bất kỳ vị trí nào có giá trị cần tìm. Vì vậy, cần lower_bound để lấy vị trí đầu tiên hoặc đếm chính xác trong [start,end). Dữ liệu phải được sắp xếp theo cùng comparer dùng khi tìm kiếm.

</details>

Cầu nối là yêu cầu về thông tin, không phải các cơ chế này tương đương nhau. Snapshot transaction quy định dữ liệu database được nhìn thấy. Ranh giới test quy định quan sát nào được ảnh hưởng tới lựa chọn mô hình. Binary search cần quy tắc sắp xếp cụ thể. Phân nhóm ngẫu nhiên xét tác động nhân quả, còn dự đoán ticket trễ xét kết quả chưa biết. Điểm dự đoán chưa xác lập tác động của việc ưu tiên xử lý ticket.

## 2. Từ một ticket tới lập luận về việc học

**Nền tảng · 50 phút.** Hoàn thành bảng dự đoán, dựng lại tìm ngưỡng và nêu hai bất biến. **Hoàn thành khi:** phân biệt được tối ưu loss trên train với đánh giá trung thực trên quan sát mới.

### Nêu điều đã biết và điều cần học

Lúc tiếp nhận, ticket `te7` có điểm workload giả lập bằng 7. Label bằng 1 vì ticket cuối cùng quá hạn. Quy tắc `score >= 5` dự đoán 1 ngay lúc nhận; label chỉ được thu sau cửa sổ kết quả. Điểm ở đây là feature nguyên 0-9, không phải xác suất hay ước lượng rủi ro đã được kiểm chứng. Có thể hình dung đó là phép biến đổi cố định từ backlog lúc tiếp nhận; lab cung cấp điểm trực tiếp, chưa xác minh pipeline feature production.

**Feature** là thông tin dùng để dự đoán, chẳng hạn backlog đã biết lúc nhận. **Label** là kết quả muốn dự đoán, ở đây trễ=1/đúng hạn=0. **Phân loại nhị phân** chọn một trong hai nhãn đó. **Mô hình** gồm quy tắc dự đoán và trạng thái đã học; bài này chỉ lưu một ngưỡng. **Học tham số**, hay fit, chọn trạng thái ấy từ ví dụ có label. Đây là học có giám sát vì mỗi ví dụ đi kèm kết quả. Không cần neural network hay gradient descent.

Ta cho phép ngưỡng 0 tới 10. Ngưỡng 0 cảnh báo mọi điểm hợp lệ; ngưỡng 10 không cảnh báo gì. Baseline theo nhãn phổ biến trên train chọn nhãn xuất hiện nhiều hơn, chọn 0 nếu hòa. Baseline quy tắc cố định dùng ngưỡng 7, không học tham số. Baseline chưa chắc vô ích: nó làm rõ mô hình mới cần cải thiện điều gì.

Trước khi xem validation/test, đặt chi phí cảnh báo nhầm là 1 và bỏ sót là 4. Đây là đơn vị quyết định giả định, không phải tiền. Quyết định đúng có chi phí 0 trong mô hình đơn giản này. Thực tế, xử lý cả cảnh báo đúng cũng có thể tốn nguồn lực, dùng chung công suất và đổi kết quả; loss cộng từng lỗi chưa bao phủ những tác động đó.

### Chạy từng dự đoán trước khi viết tỷ lệ

Test giả lập có mỗi điểm 0-9 một lần; label chỉ bằng 1 tại 4,7,9. Hoàn thành số đếm tích lũy cho ngưỡng 5. Chỉ ra một ticket bị cảnh báo không cần thiết và một ticket trễ bị bỏ sót.

<details>
<summary>Đáp án</summary>

| Điểm | Label thật | Label dự đoán | Ô tăng | TP/FP/FN/TN tích lũy |
|---|---|---|---|---|
| 0 | 0 | 0 | TN | 0/0/0/1 |
| 1 | 0 | 0 | TN | 0/0/0/2 |
| 2 | 0 | 0 | TN | 0/0/0/3 |
| 3 | 0 | 0 | TN | 0/0/0/4 |
| 4 | 1 | 0 | FN | 0/0/1/4 |
| 5 | 0 | 1 | FP | 0/1/1/4 |
| 6 | 0 | 1 | FP | 0/2/1/4 |
| 7 | 1 | 1 | TP | 1/2/1/4 |
| 8 | 0 | 1 | FP | 1/3/1/4 |
| 9 | 1 | 1 | TP | 2/3/1/4 |

Điểm 5,6,8 là cảnh báo nhầm; điểm 4 bị bỏ sót. Sáu trong mười dự đoán đúng, hai trong năm cảnh báo đúng và hai trong ba ticket trễ được tìm ra. Chi phí là ba cảnh báo nhầm cộng bốn đơn vị cho một lần bỏ sót, bằng 7. Đây là dữ liệu công khai để học; test cuối trong dự án thật không nên được tiết lộ khi đang phát triển mô hình.

</details>


TP là dự đoán 1/thật 1; FP là dự đoán 1/thật 0; FN là dự đoán 0/thật 1; TN là dự đoán 0/thật 0. Ma trận nhầm lẫn tách bốn số đếm này. Với N quan sát và N>0:

```text
accuracy  = (TP + TN) / N
precision = TP / (TP + FP), khi TP + FP > 0
recall    = TP / (TP + FN), khi TP + FN > 0
loss      = FP + c * FN, với c là chi phí bỏ sót đã nêu
mean loss = loss / N
```

Precision trả lời bao nhiêu cảnh báo là đúng; recall trả lời tìm được bao nhiêu ticket trễ. Mẫu số bằng 0 không phải bằng chứng đạt điểm hoàn hảo. Lab trả null và in `undefined`, không tự đặt một giá trị. Baseline không cảnh báo có accuracy 70%, recall 0 và chi phí 12. Ngưỡng 5 có accuracy 60% nhưng chi phí 7. Một nhóm khác gồm 99 ticket đúng hạn và một ticket trễ sẽ cho baseline đó accuracy 99% dù bỏ sót ticket trễ duy nhất. Cần nêu tần suất nhãn và chi phí lỗi.

Bất biến vòng đếm: sau một prefix, bốn ô đếm đúng các kết quả tương ứng trong prefix và có tổng bằng độ dài prefix. Ban đầu tất cả bằng 0. Mỗi dòng làm tăng đúng một ô trong bốn trường hợp loại trừ nhau; khi kết thúc, bảng chứa toàn bộ số đếm. Lập luận chứng minh cơ chế đếm với input nhị phân hợp lệ, chưa chứng minh label đúng hay hiệu quả tương lai.

### Học bằng tìm kiếm hữu hạn rõ ràng

Train có hai mươi ticket: hai ticket ở mỗi điểm 0-9. Điểm 0-4 không có ticket trễ; mỗi điểm 5,6,7 có một ticket trễ và một ticket đúng hạn; mỗi điểm 8,9 có hai ticket trễ. Với từng ngưỡng, đếm lỗi **chỉ trên train**. Học một ứng viên với c=1 và một ứng viên với c=4. Tìm ngưỡng được chọn theo quy tắc lấy ngưỡng lớn nhất khi hòa loss.

<details>
<summary>Đáp án</summary>

| Ngưỡng | FP train | FN train | Loss c=1 | Loss c=4 |
|---|---|---|---|---|
| 0 | 13 | 0 | 13 | 13 |
| 1 | 11 | 0 | 11 | 11 |
| 2 | 9 | 0 | 9 | 9 |
| 3 | 7 | 0 | 7 | 7 |
| 4 | 5 | 0 | 5 | 5 |
| 5 | 3 | 0 | 3 | 3 |
| 6 | 2 | 1 | 3 | 6 |
| 7 | 1 | 2 | 3 | 9 |
| 8 | 0 | 3 | 3 | 12 |
| 9 | 0 | 5 | 5 | 20 |
| 10 | 0 | 7 | 7 | 28 |

Với c=1, các ngưỡng 5-8 cùng loss 3; chọn 8. Với c=4, ngưỡng 5 là nghiệm tối ưu duy nhất. Việc học chọn tham số từ dữ liệu, không phải tự gán ngưỡng sau khi nhìn test. Loss train nhỏ hơn chưa chắc giữ lợi thế trên validation hoặc test.

</details>


Viết `h_t(x)=1` nếu `x>=t`, ngược lại bằng 0. Mục tiêu thực nghiệm là `L_train(t)=sum_i loss(h_t(x_i),y_i)`. “Thực nghiệm” ở đây nghĩa là tính trên mẫu đã thấy. `Fit` trả t lớn nhất trong các nghiệm tối ưu thuộc `{0,...,10}`. Mọi ngưỡng số thực trên điểm nguyên 0-9 đều cho cùng dự đoán với một trong mười một ứng viên này, kể cả hai quy tắc hằng. Tính đầy đủ này chỉ đúng với miền input và chiều `>=` đã nêu; chưa bao phủ quy tắc nhiều feature tùy ý.

Bất biến tìm kiếm: sau ngưỡng t, `bestCost` là loss nhỏ nhất trên các ngưỡng 0 tới t, còn `best` là ngưỡng lớn nhất đạt loss đó. Ứng viên đầu khởi tạo bất biến. Loss nhỏ hơn thay giá trị tối thiểu; loss bằng nhau thay ngưỡng trước vì ta duyệt tăng. Loss lớn hơn giữ nguyên cả hai tính chất. Kết thúc cho nghiệm tối ưu thực nghiệm trong họ quy tắc đã định. Checker độc lập duyệt ngược và dùng `<`, kiểm tra cùng quy tắc hòa mà không sao chép cách cập nhật tìm kiếm.

Với n dòng và T ứng viên, quét lại tốn O(T*n), cộng phần kiểm tra input; T=11 cố định nên công đếm dòng tuyến tính. Kiểm tra ID bằng hash dùng O(n) bộ nhớ và công kỳ vọng tuyến tính với chi phí khóa bị chặn, phân bố hash phù hợp. ID dài tùy ý hoặc gây collision thêm chi phí như Bài 01. Tìm kiếm này ưu tiên dễ kiểm tra, chưa phải trainer có throughput cao.

### Tách lựa chọn khỏi lần đánh giá cuối

Train có 20 dòng từ 10 khách hàng, validation 10 dòng từ 10 khách hàng khác, test 10 dòng từ 10 khách hàng khác nữa. Không khách hàng nào xuất hiện ở hai tập. Đối tượng cần đánh giá là ticket của **khách hàng chưa từng thấy**, với feature có sẵn lúc nhận và label thu sau 24 giờ. Các tập là dữ liệu cố định để học, không phải mẫu ngẫu nhiên hay bằng chứng khách hàng độc lập.

Train tạo hai ứng viên đã học và baseline nhãn phổ biến. So chúng cùng baseline ngưỡng 7 đã định trước trên validation, dùng chung c=4. Label validation được phép chọn ứng viên, nên validation không còn là bằng chứng cuối chưa đụng tới. Thứ tự ứng viên xử lý trường hợp hòa loss validation. Hoàn thành bảng lựa chọn.

<details>
<summary>Đáp án</summary>

| Ứng viên | Ngưỡng học/cố định | FP/FN validation | Chi phí validation c=4 |
|---|---|---|---|
| Nhãn phổ biến | 10 từ train | 0/4 | 16 |
| Quy tắc cố định | 7 trước khi học | 0/1 | 4 |
| Học với c=1 | 8 từ train | 0/2 | 8 |
| Học với c=4 | 5 từ train | 1/0 | 1 |

Cố định ngưỡng 5. Quy trình này không học lại trên train+validation, nên quy tắc được đánh giá chính là ứng viên đã chọn. Học lại có thể hợp lệ nếu định trước quy trình rồi đánh giá đối tượng mới sau đó; vẫn không được dùng label test.

</details>


Với predictor h đã cố định và quan sát mới độc lập với dữ liệu học/lựa chọn, ta dùng lập luận kỳ vọng từ Bài 07: nếu các quan sát test có cùng phân phối mục tiêu, kỳ vọng loss của từng quan sát bằng rủi ro mục tiêu `R(h)`, nên kỳ vọng mean loss test bằng `R(h)` nhờ tính tuyến tính. Tính độc lập giữa các quan sát test cần cho các phép tính phương sai/khoảng đơn giản thường dùng; riêng kỳ vọng cần các phân phối biên phù hợp. Bảng giả lập cố định ở đây chưa xác lập những giả định đó.

Nếu chọn loss test nhỏ nhất, h lại phụ thuộc vào chính kết quả test. Giá trị tối thiểu đã qua lựa chọn dễ lạc quan, không còn là lần đánh giá chưa đụng tới. Test đếm hoàn toàn đúng vẫn có thể đánh giá sai quy trình. Validation cũng cần thận trọng khi tái sử dụng: nhiều lần tìm kiếm thích nghi có thể overfit nó, tức lựa chọn bám vào đặc điểm riêng của tập đã thấy thay vì quy luật còn giữ trên dữ liệu mới. Dự án lớn có thể cần đánh giá lồng nhau hoặc tập đánh giá mới; bài chưa triển khai hai cách này.

Nghỉ - 10 phút, rời màn hình.

## 3. Đọc xem điểm đánh giá cho phép kết luận gì

**Đọc tài liệu · 45 phút.** Đọc các phần giới hạn và lập bảng nhận định/bằng chứng/giới hạn. **Hoàn thành khi:** bảo vệ được một quy trình đánh giá và chỉ ra điểm số chưa hỗ trợ nhận định triển khai.

Đọc [common pitfalls của scikit-learn, dòng 15-224](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/common_pitfalls.rst#L15-L224), tập trung vào tiền xử lý không nhất quán, leakage và chỉ học bước chọn feature trên train. Ví dụ label ngẫu nhiên/feature nhiều chiều cho thấy chọn feature có giám sát trước khi chia tập có thể tạo vẻ ngoài dự đoán được. Các số trong tài liệu là ví dụ của nguồn, không phải số đo được lab C# này tái hiện.

Chỉ đọc [accuracy, dòng 575-599](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/modules/model_evaluation.rst#L575-L599), [quy ước ma trận nhầm lẫn, dòng 769-800](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/modules/model_evaluation.rst#L769-L800) và [công thức precision/recall, dòng 1030-1064](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/doc/modules/model_evaluation.rst#L1030-L1064). Thư viện có nhiều metric khác; bài chỉ cài số đếm nhị phân, các tỷ lệ này và chi phí đã định. Chính sách trả null khi mẫu số 0 được nêu rõ; không nhận là tương thích mọi tùy chọn metric scikit-learn.

Lập một bảng ba dòng cho các nhận định: tiền xử lý học từ mọi dòng vô hại vì không dùng label test; mô hình accuracy 99% chắc chắn bắt được ticket trễ hiếm; accuracy dự đoán chứng minh ưu tiên xử lý làm giảm trễ.

<details>
<summary>Đáp án</summary>

| Nhận định | Bằng chứng | Ranh giới/cách sửa |
|---|---|---|
| Tiền xử lý mọi dòng vô hại | Common pitfalls nêu cả scaling đã học cũng có thể dùng thông tin phân phối của tập giữ riêng | Học tiền xử lý trong ranh giới train; không dùng label chưa nghĩa là không dùng thông tin đánh giá |
| Accuracy 99% bắt được sự kiện hiếm | Phản ví dụ 99 đúng hạn/một trễ | Báo số lượng nhãn, các ô nhầm lẫn, recall và chi phí đã nêu; quy tắc luôn dự đoán 0 có thể bỏ sót tất cả |
| Dự đoán chứng minh can thiệp có ích | Bài 08 tách liên hệ quan sát với tác động theo kết quả tiềm năng | Label có thể phản ánh workflow cũ; đánh giá dự đoán đã cố định chưa phải bằng chứng can thiệp ngẫu nhiên |

Nguồn hỗ trợ giữ ranh giới, không khẳng định mọi phép biến đổi bị leak đều làm tăng mọi điểm số. Leakage vi phạm quy trình thông tin dù tác động đo được nhỏ hoặc âm.

</details>


Nếu phép biến đổi đã học chia cho trung bình train, phải giữ trung bình đó khi xử lý validation/test. Cùng một phép biến đổi đã học áp dụng cho mọi tập; học lại trên từng tập tạo các quy tắc dự đoán không nhất quán. Đổi đơn vị bằng hằng số không học gì từ dữ liệu là trường hợp khác, nhưng vẫn cần kiểm tra thông tin sẵn có, đơn vị và version. Lab ngưỡng không có scaling đã học; đây là phần mở rộng có nguồn, chưa phải thí nghiệm scaler đã chạy riêng.

## 4. Công cụ làm ranh giới thành luồng xử lý

**Đọc mã nguồn · 45 phút.** Theo clone, chia tập, fit và predict trong một đường triển khai. **Hoàn thành khi:** bảng chạy chỉ rõ dòng nào được ảnh hưởng trạng thái đã học và công cụ không phát hiện được gì.

scikit-learn là công cụ học và đánh giá được dùng rộng rãi. API tìm kiếm của nó giải quyết việc so các cấu hình tham số qua nhiều lần chia dữ liệu mà không dùng lại trạng thái đã fit của một estimator cho mọi tác vụ. Với C ứng viên và K lần chia, source đã đọc tạo C*K lần fit và cho phép lập lịch song song; phải trả chi phí học lặp lại và nguồn lực thay vì chỉ học một lần rồi chấm đối tượng đó ở mọi nơi. Bài chưa benchmark runtime/bộ nhớ của đánh đổi này.

Đọc commit **102e5daf66759cf896beeee229d1bf7c80ab2ba4**, giới hạn ở:

- [`_search.py`, phân phối ứng viên, dòng 1014-1103](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/model_selection/_search.py#L1014-L1103): clone estimator gốc, liệt kê cặp ứng viên/lần chia, gọi `_fit_and_score` với clone và chỉ số train/test.
- [`_validation.py`, `_fit_and_score`, dòng 792-872](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/model_selection/_validation.py#L792-L872): lấy riêng train/test, fit trên train, rồi chấm estimator đã học trên test. Phạm vi đọc gồm nhánh callback/lỗi; chưa phân tích toàn bộ metadata routing.
- [`pipeline.py`, `_fit`, dòng 519-578](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/pipeline.py#L519-L578), [fit estimator cuối, dòng 630-658](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/pipeline.py#L630-L658) và [predict, dòng 793-811](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/sklearn/pipeline.py#L793-L811): học các bước biến đổi từ dữ liệu train được truyền vào, học estimator cuối từ train đã biến đổi, về sau transform/predict mà không gọi fit trong đường dự đoán đã xét.

**Xác minh từ source:** tác vụ nhận chỉ số riêng và gọi `clone(base_estimator)` cho từng cặp ứng viên/lần chia; đường fit/score dùng phần train để học và phần còn lại để chấm; đường predict của Pipeline gọi transform rồi predict. **Suy luận thiết kế:** đặt tiền xử lý đã học trong đối tượng fit giảm cơ hội vượt ranh giới do thao tác thủ công. Chưa xác minh timestamp feature, khách hàng độc lập, label, splitter hay hành vi estimator tự viết.

“Test” trong `_fit_and_score` là phần giữ riêng của tác vụ đánh giá đó. Khi tìm tham số, điểm các fold chọn ứng viên nên chúng đóng vai trò validation. Chúng không phải test cuối chưa đụng tới của toàn quy trình tìm kiếm. Với thuật ngữ mới: đánh giá K-fold luân phiên giữ riêng một trong K phần, dùng các phần còn lại để học; mỗi lượt là một tác vụ train/validation. Splitter theo khách hàng phải giữ cả khách hàng ở một phía trong từng tác vụ. Lab dùng một lần chia ba tập cố định, không chạy cross-validation hay sklearn.

Chạy theo một ứng viên ở một lần chia và giải thích vì sao bọc classifier trong Pipeline chưa sửa ma trận feature đã được chọn bằng toàn bộ label.

<details>
<summary>Đáp án</summary>

| Bước | Dữ liệu/trạng thái | Việc xảy ra |
|---|---|---|
| Phân phối | Cấu hình tham số và chỉ số chia | Clone nhận tham số của tác vụ |
| Lấy phần dữ liệu | Train và phần giữ riêng | `_safe_split` chuẩn bị hai input |
| Fit Pipeline | Input/label train | Các bước biến đổi học trước; estimator cuối học từ train đã biến đổi |
| Chấm | Input/label giữ riêng | Dự đoán dùng phép biến đổi đã học; scorer so dự đoán với label |
| Tổng hợp tìm kiếm | Điểm các tác vụ ứng viên/lần chia | Điểm ảnh hưởng lựa chọn, vẫn cần lần đánh giá cuối riêng |

Nếu ma trận input đã chọn feature bằng mọi label, clone nhận biểu diễn đã nhiễm thông tin ấy. Pipeline không biết lịch sử và không hoàn tác được. Tương tự, ID dòng khác nhau chưa tiết lộ khách hàng trùng nếu splitter/guard không dùng metadata khách hàng. Đường xử lý thực thi ranh giới caller cung cấp, chưa phải bộ phát hiện mọi leakage.

</details>


### Áp dụng vào dịch vụ hỗ trợ ASP.NET/Azure

Lúc nhận, lưu ID ticket, ID khách hàng, timestamp feature, version định nghĩa feature và version mô hình. Dựng snapshot lịch sử chỉ từ giá trị đã có lúc đó. Thu label trễ/đúng hạn sau cửa sổ đã nêu, có chính sách rõ cho kết quả thiếu hoặc đến muộn. Chia retry của cùng ticket ngẫu nhiên chưa tạo bằng chứng mới giữ riêng; SQL COUNT hay transaction đúng chưa sửa thời điểm feature.

Với mục tiêu khách hàng chưa thấy, giữ riêng toàn bộ khách hàng. Với ticket tương lai của khách hàng đã biết, chia theo thời gian với mốc feature/label phù hợp có thể thích hợp hơn; trùng khách hàng chưa tự động là lỗi với mục tiêu khác này. Nêu mục tiêu trước khi chia. Nếu quan tâm dữ liệu trôi theo thời gian, chỉ chia khách hàng riêng chưa kiểm tra được điều đó.

Lưu quy tắc/tiền xử lý đã học và bản đánh giá cùng version. Dashboard Angular có thể hiện số đếm, precision, recall và chi phí thay cho một huy hiệu accuracy. Đây là đề xuất thiết kế của bài, chưa chạy integration ML.NET/SQL Server/Azure. Họ ngưỡng nhỏ chưa cài feature store production, xử lý outcome thiếu hay chính sách ưu tiên có bảo đảm nhân quả.

Ăn trưa và nghỉ - 30 phút.

## 5. Lab: cố định mô hình rồi chất vấn kết quả

**Lab · 75 phút.** Viết tìm ngưỡng/vòng đếm, chạy kiểm tra độc lập và sửa một lỗi. **Hoàn thành khi:** code chọn ngưỡng 5 từ validation, khớp oracle và giải thích được vì sao accuracy test vẫn giảm dù học đúng.

Viết `Fit`, `Count`, `Select` và guard khách hàng không trùng theo yêu cầu phần 2. Mỗi tập có 1-10000 dòng, ID dòng duy nhất và không rỗng, ID khách hàng không rỗng, điểm 0-9; cùng khách hàng được phép lặp trong một tập. Chi phí là số nguyên 1-1000; ngưỡng là 0-10. Từ chối input rỗng/không hợp lệ. Không dùng test để tạo ứng viên hay chọn winner. Hàm dự đoán nhận điểm, không nhận label tương lai.

Tạo các file bên dưới hoặc giải nén ZIP. Dừng setup sau 15 phút nếu chưa có đúng SDK; dùng bảng chạy, bảng tìm kiếm và oracle để chỉ đọc. Sản phẩm là demo, kết quả kiểm tra và giải thích một lỗi ngắn.

<details>
<summary>Đáp án - lab đầy đủ chạy được</summary>

Dùng **.NET SDK 10.0.401**, runtime **Microsoft.NETCore.App 10.0.12**, `net10.0`, tắt roll-forward cho SDK/runtime. Không có dependency NuGet bên ngoài nên không cần lock file gói bắc cầu của bên thứ ba. Cài SDK/reference pack hoặc restore đầu tiên có thể cần network. Sau restore thành công, các lệnh `--no-restore` dưới đây không cần network, database hay Python.

Mọi đường dẫn dưới đây tính từ `dotnet`. ZIP có thư mục gốc đó. Nếu tạo thủ công, tạo thư mục và toàn bộ file được trình bày. Chạy lệnh **bên trong `dotnet`**; `cd dotnet` giả sử đang ở thư mục cha.

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

`LessonLab/Checks.cs`:

<!-- lab-file: LessonLab/Checks.cs -->
```csharp
public static class Checks
{
    static void Require(bool condition) { if (!condition) throw new Exception("Check failed."); }
    static void Reject(Action action)
    {
        try { action(); } catch (ArgumentException) { return; }
        throw new Exception("Expected rejection.");
    }
    // Independent 2x2 table indexed by actual and prediction; no Count call.
    static Matrix Oracle(Ticket[] rows, Rule rule)
    {
        var cells = new long[2, 2];
        foreach (var x in rows) cells[x.Late ? 1 : 0, x.Risk >= rule.Threshold ? 1 : 0]++;
        return new(cells[1, 1], cells[0, 1], cells[1, 0], cells[0, 0]);
    }
    public static void Run()
    {
        int fits = 0;
        // All ordered datasets of length 1-4, risks 0-2, labels 0/1.
        for (int n = 1; n <= 4; n++)
        for (int code = 0; code < (int)Math.Pow(6, n); code++)
        {
            int state = code;
            var rows = new Ticket[n];
            for (int i = 0; i < n; i++)
            {
                int value = state % 6; state /= 6;
                rows[i] = new($"id{i}", $"group{i}", value / 2, value % 2 == 1);
            }
            foreach (int missedCost in new[] { 1, 4 })
            {
                // Reverse enumeration, direct per-row loss; no Fit/Count/Cost.
                int expected = -1; long minimum = long.MaxValue;
                for (int t = 10; t >= 0; t--)
                {
                    long loss = rows.Sum(x => x.Risk >= t
                        ? (x.Late ? 0L : 1L) : (x.Late ? missedCost : 0L));
                    if (loss < minimum) { minimum = loss; expected = t; }
                    var rule = new Rule("oracle", t);
                    Require(Evaluation.Count(rows, rule) == Oracle(rows, rule));
                }
                Require(Evaluation.Fit(rows, missedCost).Threshold == expected);
                fits++;
            }
        }
        var sets = Data.Split(); Evaluation.Disjoint(sets);
        var candidates = Evaluation.Candidates(sets[0]);
        Require(candidates.Select(x => x.Threshold).SequenceEqual(new[] { 10, 7, 8, 5 }));
        var selected = Evaluation.Select(candidates, sets[1], 4);
        Require(selected.Threshold == 5);
        Require(Evaluation.Count(sets[2], selected) == new Matrix(2, 3, 1, 4));
        Require(Evaluation.Count(sets[2], candidates[0]).Precision is null);
        Require(Evaluation.Count([new("z", "Z", 9, false)], new("zero", 10)).Recall is null);
        Require(Evaluation.Majority([new("a", "A", 0, true), new("b", "B", 9, false)]).Threshold == 10);
        Require(Evaluation.Select([new("first", 10), new("second", 10)], sets[1], 4).Name == "first");
        var flippedTest = sets[2].Select(x => x with { Late = !x.Late }).ToArray();
        Evaluation.Disjoint(sets[0], sets[1], flippedTest);
        Require(Evaluation.Select(candidates, sets[1], 4) == selected);
        // Risk 0/9 and all labels also exercise full-domain boundaries.
        foreach (int risk in new[] { 0, 9 }) foreach (bool y in new[] { false, true })
            Require(Evaluation.Fit([new("edge", "edge", risk, y)], 4).Threshold == (y ? risk : 10));
        Reject(() => Evaluation.Fit([], 4));
        Reject(() => Evaluation.Fit(sets[0], 0));
        Reject(() => Evaluation.Count([new("bad", "G", 10, false)], selected));
        Reject(() => Evaluation.Count([new("bad", "G", 0, false)], new("bad", 11)));
        Reject(() => Evaluation.Count([new("x", "G", 0, false), new("x", "H", 1, true)], selected));
        Reject(() => Evaluation.Disjoint(sets[0], [sets[0][0] with { Id = "other" }]));
        Reject(() => Evaluation.Disjoint(sets[0], [sets[0][0] with { Group = "other" }]));
        Console.WriteLine($"PASS: {fits} fits; independent confusion tables; split/tie/boundary guards.");
    }
}
```

`LessonLab/Data.cs`:

<!-- lab-file: LessonLab/Data.cs -->
```csharp
public static class Data
{
    public static Ticket[][] Split()
    {
        var train = Enumerable.Range(0, 20).Select(i =>
        {
            int risk = i / 2;
            bool late = risk >= 8 || (risk >= 5 && i % 2 == 0);
            return new Ticket($"tr{i}", $"train-customer-{risk}", risk, late);
        }).ToArray();
        var validation = Enumerable.Range(0, 10).Select(i =>
            new Ticket($"va{i}", $"validation-customer-{i}", i, i >= 6)).ToArray();
        var test = Enumerable.Range(0, 10).Select(i =>
            new Ticket($"te{i}", $"test-customer-{i}", i, i is 4 or 7 or 9)).ToArray();
        return [train, validation, test];
    }
}
```

`LessonLab/Evaluation.cs`:

<!-- lab-file: LessonLab/Evaluation.cs -->
```csharp
// Original teaching code, MIT. Not adapted from scikit-learn.
public sealed record Ticket(string Id, string Group, int Risk, bool Late);
public sealed record Rule(string Name, int Threshold)
{
    public bool Predict(int risk) => risk >= Threshold;
}
public readonly record struct Matrix(long TP, long FP, long FN, long TN)
{
    public long N => TP + FP + FN + TN;
    public double Accuracy => (double)(TP + TN) / N;
    public double? Precision => TP + FP == 0 ? null : (double)TP / (TP + FP);
    public double? Recall => TP + FN == 0 ? null : (double)TP / (TP + FN);
    public long Cost(int missedCost) => checked(FP + missedCost * FN);
}
public static class Evaluation
{
    public static void Validate(Ticket[] rows)
    {
        if (rows.Length is < 1 or > 10000)
            throw new ArgumentException("Require 1-10000 rows.");
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in rows)
            if (row is null || string.IsNullOrWhiteSpace(row.Id)
                || string.IsNullOrWhiteSpace(row.Group) || row.Risk is < 0 or > 9
                || !ids.Add(row.Id))
                throw new ArgumentException("Require unique IDs, nonempty groups and risk 0-9.");
    }
    public static void Disjoint(params Ticket[][] sets)
    {
        var ids = new HashSet<string>(StringComparer.Ordinal);
        var groups = new HashSet<string>(StringComparer.Ordinal);
        foreach (var set in sets)
        {
            Validate(set);
            var localGroups = set.Select(x => x.Group).Distinct(StringComparer.Ordinal);
            if (set.Any(x => !ids.Add(x.Id)) || localGroups.Any(x => !groups.Add(x)))
                throw new ArgumentException("Overlapping row IDs or customer groups.");
        }
    }
    public static Matrix Count(Ticket[] rows, Rule rule)
    {
        Validate(rows);
        if (rule.Threshold is < 0 or > 10) throw new ArgumentException("Threshold 0-10.");
        long tp = 0, fp = 0, fn = 0, tn = 0;
        foreach (var row in rows)
        {
            bool prediction = rule.Predict(row.Risk);
            if (prediction && row.Late) tp++;
            else if (prediction) fp++;
            else if (row.Late) fn++;
            else tn++;
        }
        return new Matrix(tp, fp, fn, tn);
    }
    public static Rule Majority(Ticket[] train)
    {
        Validate(train);
        return new Rule("majority", train.Count(x => x.Late) > train.Length / 2 ? 0 : 10);
    }
    public static Rule Fit(Ticket[] train, int missedCost)
    {
        Validate(train);
        if (missedCost is < 1 or > 1000) throw new ArgumentException("FN cost 1-1000.");
        var best = new Rule($"fit-FN{missedCost}", 0);
        long bestCost = long.MaxValue;
        for (int threshold = 0; threshold <= 10; threshold++)
        {
            var candidate = new Rule(best.Name, threshold);
            long cost = Count(train, candidate).Cost(missedCost);
            // Ascending candidates plus <= implements largest-threshold ties.
            if (cost <= bestCost) { best = candidate; bestCost = cost; }
        }
        return best;
    }
    public static Rule Select(Rule[] candidates, Ticket[] validation, int missedCost)
    {
        Validate(validation);
        if (candidates.Length == 0 || missedCost is < 1 or > 1000)
            throw new ArgumentException("Require candidates and FN cost 1-1000.");
        return candidates.OrderBy(r => Count(validation, r).Cost(missedCost)).First();
    }
    public static Rule[] Candidates(Ticket[] train) =>
        [Majority(train), new Rule("fixed-rule", 7), Fit(train, 1), Fit(train, 4)];
}
```

`LessonLab/Experiment.cs`:

<!-- lab-file: LessonLab/Experiment.cs -->
```csharp
public static class Experiment
{
    public static void Run()
    {
        var sets = Data.Split();
        Evaluation.Disjoint(sets);
        var clean = Evaluation.Fit(sets[0], 4);
        var cleanResult = Evaluation.Count(sets[2], clean);
        // Deliberately invalid: Late is only known after the outcome window.
        var leaked = sets.Select(s => s.Select(x => x with
            { Risk = x.Late ? 9 : 0 }).ToArray()).ToArray();
        var invalid = Evaluation.Fit(leaked[0], 4);
        var invalidResult = Evaluation.Count(leaked[2], invalid);
        Console.WriteLine($"Feature availability: clean accuracy={cleanResult.Accuracy:F3} cost={cleanResult.Cost(4)}; leaked accuracy={invalidResult.Accuracy:F3} cost={invalidResult.Cost(4)}");

        // Same four held-out customers, four training rows and balanced labels.
        var target = Enumerable.Range(4, 4).Select(i =>
            new Ticket($"new-{i}", $"c{i}", 0, i % 2 == 1)).ToArray();
        var proper = Enumerable.Range(0, 4).Select(i =>
            new Ticket($"old-{i}", $"c{i}", 0, i % 2 == 1)).ToArray();
        var overlap = target.Select(x => x with { Id = "prior-" + x.Id }).ToArray();
        Evaluation.Disjoint(proper, target);
        double Score(Ticket[] train)
        {
            var learned = train.ToDictionary(x => x.Group, x => x.Late, StringComparer.Ordinal);
            int correct = target.Count(x =>
                (learned.TryGetValue(x.Group, out bool y) && y) == x.Late);
            return (double)correct / target.Length;
        }
        Console.WriteLine($"Customer exposure: disjoint accuracy={Score(proper):F3}; overlap accuracy={Score(overlap):F3}");
        try { Evaluation.Disjoint(overlap, target); }
        catch (ArgumentException) { Console.WriteLine("Group guard rejects overlap despite unique row IDs."); }
    }
}
```

`LessonLab/Program.cs`:

<!-- lab-file: LessonLab/Program.cs -->
```csharp
using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else if (args is ["--transfer"]) Transfer.Run();
else if (args.Length == 0)
{
    var sets = Data.Split();
    Evaluation.Disjoint(sets);
    var candidates = Evaluation.Candidates(sets[0]);
    var winner = Evaluation.Select(candidates, sets[1], 4);
    Console.WriteLine($"Selected on validation: {winner.Name}, threshold={winner.Threshold}");
    foreach (var rule in candidates)
    {
        var m = Evaluation.Count(sets[2], rule);
        string precision = m.Precision?.ToString("F3") ?? "undefined";
        string recall = m.Recall?.ToString("F3") ?? "undefined";
        Console.WriteLine($"{rule.Name}: t={rule.Threshold} TP={m.TP} FP={m.FP} FN={m.FN} TN={m.TN} accuracy={m.Accuracy:F3} precision={precision} recall={recall} cost={m.Cost(4)}");
    }
}
else throw new ArgumentException("Use no args, --check, --experiment or --transfer.");
```

`LessonLab/Transfer.cs`:

<!-- lab-file: LessonLab/Transfer.cs -->
```csharp
public static class Transfer
{
    public static void Run()
    {
        // One customer contributes four errors; another contributes one success.
        Ticket[] rows = [new("a1", "A", 0, true), new("a2", "A", 0, true),
            new("a3", "A", 0, true), new("a4", "A", 0, true), new("b1", "B", 0, false)];
        var rule = new Rule("never-alert", 10);
        var rowMatrix = Evaluation.Count(rows, rule);
        double macroCost = rows.GroupBy(x => x.Group).Average(g =>
            (double)Evaluation.Count(g.ToArray(), rule).Cost(4) / g.Count());
        if (rowMatrix.Cost(4) != 16 || Math.Abs(macroCost - 2) > 1e-12)
            throw new InvalidOperationException("Wrong unit weighting.");
        Console.WriteLine($"Row mean cost={(double)rowMatrix.Cost(4) / rows.Length:F3}; equal-customer mean cost={macroCost:F3}");
    }
}
```

```bash
cd dotnet
dotnet --version
dotnet restore LessonLab
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
dotnet run --no-restore -c Release --project LessonLab -- --transfer
```

SDK dự kiến in `10.0.401`. Các output demo/check tất định sau đã được quan sát trong môi trường đã pin:

```text
Selected on validation: fit-FN4, threshold=5
majority: t=10 TP=0 FP=0 FN=3 TN=7 accuracy=0.700 precision=undefined recall=0.000 cost=12
fixed-rule: t=7 TP=2 FP=1 FN=1 TN=6 accuracy=0.800 precision=0.667 recall=0.667 cost=5
fit-FN1: t=8 TP=1 FP=1 FN=2 TN=6 accuracy=0.700 precision=0.500 recall=0.333 cost=9
fit-FN4: t=5 TP=2 FP=3 FN=1 TN=4 accuracy=0.600 precision=0.400 recall=0.667 cost=7
```

```text
PASS: 3108 fits; independent confusion tables; split/tie/boundary guards.
```

Baseline nhãn phổ biến và quy tắc cố định được định trước; cả bốn ứng viên đã cố định trước khi báo test. Quy trình minh họa này cho phép báo các so sánh ấy, không cho phép chọn winner thay thế từ kết quả test. Ngưỡng 7 có chi phí test thấp hơn ngưỡng 5 đã chọn. Chênh lệch được giữ rõ: chọn bằng validation chưa bảo đảm điểm tốt nhất ở một test cụ thể. Không lặng lẽ đổi sang 7 rồi gọi test cũ là bằng chứng chưa dùng.

Trên test, mô hình đã chọn bỏ sót điểm 4 và cảnh báo nhầm 5,6,8. Train gắn điểm cao với trễ, còn test nhỏ có ticket trễ tại 4 và ticket đúng hạn tại 5,6,8. Dạng lỗi gợi ý kiểm tra feature đủ thông tin hay phân phối đổi bằng dữ liệu phát triển mới; dữ liệu minh họa chưa xác định nguyên nhân production. Bài không nhận train/test là IID.

`Checks` liệt kê mọi tập có thứ tự dài 1-4, điểm 0-2 và label nhị phân: 1554 tập, hai chi phí, 3108 lần fit. Oracle duyệt ngưỡng ngược và cộng loss từng dòng trực tiếp, không gọi `Fit`, `Count` hay `Matrix.Cost`. Bảng ô 2x2 độc lập kiểm tra cả mười một ngưỡng cho từng tập/chi phí. Hai phía dùng chung biểu diễn input, phép so điểm và họ ngưỡng hữu hạn. Các ca 0/9 toàn miền, tỷ lệ không xác định, hòa nhãn/lựa chọn, ID/khách hàng trùng và điểm/chi phí sai bổ sung kiểm tra biên. Có assertion cho lựa chọn và các ô test của demo.

Chữ ký `Select` không có tham số test. Ca đổi label test kiểm tra lựa chọn từ train/validation vẫn giữ nguyên; chưa phải chứng minh không ảnh hưởng cho mọi pipeline chuẩn bị dữ liệu bên ngoài. Liệt kê hết ca nhỏ chưa bao phủ ID dài tùy ý, mọi cỡ dữ liệu hay label thật sai. Lập luận bất biến xác lập tính đúng của tìm kiếm hữu hạn; checker chưa chứng minh khả năng khái quát hay ích lợi production.

Nếu thiếu bản pin, cài đúng version hoặc dùng phương án chỉ đọc. Exception trùng nhóm yêu cầu dựng lại cách chia, không xóa guard. Exception điểm 10 nghĩa là miền feature đổi; cần sửa yêu cầu và họ ứng viên có chủ đích, không âm thầm cắt điểm. ZIP chỉ chứa source và [hướng dẫn lab](../../../labs/honest-evaluation/dotnet/README.vi.md) bổ sung cho lời giải đầy đủ này.

</details>

Một người sửa cập nhật fit từ `cost <= bestCost` thành `cost < bestCost`. Điều gì đổi theo yêu cầu đã nêu?

<details>
<summary>Đáp án</summary>

Duyệt tăng với `<` giữ nghiệm tối ưu đầu, nên c=1 chọn ngưỡng 5 thay vì 8. Vẫn tối ưu thực nghiệm nhưng vi phạm chính sách lấy ngưỡng lớn nhất khi hòa, vốn ưu tiên ít cảnh báo hơn khi loss bằng nhau. Oracle duyệt ngược giữ 8 và bắt lỗi này. Khôi phục `<=`, hoặc sửa rõ chính sách cùng mọi kết quả dự kiến; đừng coi trường hợp hòa không tồn tại.

</details>


Một người nối validation với test trước khi gọi `Select`, trong khi `Fit` vẫn chỉ dùng train. Đánh giá này trung thực chưa?

<details>
<summary>Đáp án</summary>

Chưa. Lựa chọn ứng viên đã phụ thuộc label test dù bước học tham số không dùng test. Với dữ liệu này, chi phí gộp là 28,9,17,8 và vẫn chọn ngưỡng 5; winner không đổi chưa làm việc dùng thông tin trở nên hợp lệ. Ranh giới giữ riêng bao phủ quyết định feature, tiền xử lý, ngưỡng và lựa chọn ứng viên, không chỉ method mang tên Fit. Chọn trên validation rồi chấm lựa chọn đã cố định trên test. Nếu test đã hướng dẫn sửa, cần bằng chứng mới chưa dùng để đánh giá quy trình sửa; đổi tên các dòng cũ không khôi phục tính độc lập.

</details>


Nghỉ - 10 phút, rời màn hình.

## 6. Thí nghiệm có kiểm soát: điểm tăng vì lý do sai

**Thí nghiệm · 45 phút.** Chạy hai phản ví dụ đổi một yếu tố, ghi riêng giả định, dự đoán, quan sát và suy luận. **Hoàn thành khi:** tái hiện được hai output và nêu điều mỗi kết quả chưa xác lập.

### Thí nghiệm A: đổi thời điểm thông tin sẵn có

Giả định quyết định diễn ra lúc nhận và `Late` chỉ biết sau 24 giờ. Dự đoán sao label vào điểm sẽ tách hoàn hảo dữ liệu cụ thể này. Chỉ đổi định nghĩa feature từ điểm lúc nhận được cung cấp thành `Late ? 9 : 0`; giữ dòng, label, cách chia, họ ngưỡng, loss học và thuật toán. Học mỗi biểu diễn trên train với c=4 rồi chấm kết quả đã cố định trên cùng test. Thí nghiệm tách việc nhiễm thông tin trong biểu diễn, không chọn mô hình mới thích nghi theo test.

Chạy `dotnet run --no-restore -c Release --project LessonLab -- --experiment` trong `dotnet`. Giải thích so sánh feature và liệu 100% có hỗ trợ triển khai không.

<details>
<summary>Đáp án - phản ví dụ feature đã chạy</summary>

```text
Feature availability: clean accuracy=0.600 cost=7; leaked accuracy=1.000 cost=0
```

**Quan sát:** ngưỡng của feature được cung cấp là 5, chi phí 7; feature lấy từ label cho ngưỡng 9, không lỗi. **Suy luận:** điểm hoàn hảo đo thông tin outcome tương lai, chưa có lúc predictor nhận ticket. Nó chưa cho thấy học tốt hơn hay tiết kiệm hơn. Chia dòng ngẫu nhiên/không trùng chưa sửa leak ngay trong từng dòng.

**Giới hạn:** label/feature được dựng tất định; chưa kiểm tra clock thu thập thật, độ trễ label, outcome nhiễu hay outage. Đây là phản ví dụ cho việc tin điểm số, không phải ước lượng mức leakage production. Cần review ý nghĩa thông tin vì cả hai biểu diễn đều qua kiểm tra miền điểm. Code dùng sai có chủ đích được ghi rõ không hợp lệ và không phải ứng viên triển khai.

</details>


### Thí nghiệm B: đổi việc đã biết khách hàng mục tiêu

Giả định mục tiêu là khách hàng chưa thấy và mỗi khách hàng có outcome nhị phân cố định trong ví dụ này. Bốn khách hàng giữ riêng c4-c7 có mỗi người một dòng mới, gồm hai trễ/hai đúng hạn. Mô hình ghi nhớ lưu label khách hàng trong train, dự đoán 0 cho khách hàng chưa biết. So bốn dòng train từ c0-c3 với bốn dòng trước đó từ c4-c7. Hai train có cùng cỡ, điểm giả cố định và tỷ lệ nhãn; giữ nguyên dòng test, label, fallback và mô hình ghi nhớ. Chỉ đổi việc khách hàng mục tiêu đã xuất hiện hay chưa.

Dự đoán hai accuracy và kiểm tra guard nhóm. Chỉ từ chối ID dòng trùng có phát hiện vấn đề không?

<details>
<summary>Đáp án - phản ví dụ khách hàng đã chạy</summary>

```text
Customer exposure: disjoint accuracy=0.500; overlap accuracy=1.000
Group guard rejects overlap despite unique row IDs.
```

**Quan sát:** khách hàng chưa biết nhận dự đoán hằng 0, đúng hai trong bốn; khách hàng đã biết được tra label đúng cả bốn. ID dòng train/test đều khác, nhưng ID khách hàng trùng ở đường không hợp lệ. **Suy luận:** với nhận định khách hàng chưa thấy, điểm tăng do đã tiếp xúc khách hàng, chưa phải hành vi tốt hơn trên khách hàng mới. Guard của lab chính từ chối tiếp xúc đó.

**Giới hạn:** label khách hàng cố định do ta dựng, mẫu rất nhỏ/cân bằng và mô hình ghi nhớ khác mô hình ngưỡng. Phản ví dụ thứ hai chưa đo độ nhạy leakage của mô hình ngưỡng. Chưa xác lập tính độc lập, dữ liệu trôi theo thời gian, hiệu ứng khách hàng thực tế hay hiệu quả tương lai với khách hàng đã biết. Trùng khách hàng có thể phù hợp mục tiêu khách hàng đã biết với thời điểm đúng; nó vi phạm mục tiêu khách hàng chưa thấy đang được xét.

Không có số đo thời gian. Quan sát là số đếm chính xác từ phản ví dụ giả lập, không phải ước lượng độ tin cậy hay so hiệu quả phổ quát.

</details>


Nghỉ - 10 phút, rời màn hình.

## 7. Vận dụng: đổi đối tượng được tính ngang nhau

**Vận dụng · 35 phút.** Đổi loss theo ticket thành loss theo khách hàng và kiểm tra trường hợp tăng số dòng. **Hoàn thành khi:** công thức nêu rõ đơn vị mục tiêu và giữ nguyên khi lặp các dòng giống nhau của một khách hàng.

Khách hàng A có bốn ticket trễ, B có một ticket đúng hạn; mọi điểm bằng 0. Dùng quy tắc không cảnh báo, c=4. Nghiệp vụ muốn chi phí ticket trung bình của một khách hàng trung bình, thay vì chi phí của một ticket trung bình. Suy ra hai cách tổng hợp, cài phép tính mới bằng `Transfer.Run` được cung cấp và giải thích vì sao một ma trận nhầm lẫn chung chưa xác định kết quả trọng số khách hàng bằng nhau.

<details>
<summary>Đáp án</summary>

Tổng chi phí A là 16, trung bình ticket của A là 4; tổng/trung bình của B là 0. Trung bình theo ticket là 16/5=3,2. Trung bình với khách hàng ngang nhau là `(4+0)/2=2`. Với G khách hàng, tính `sum_g (loss_g / n_g) / G`, giữ riêng số dòng và chi phí mỗi người. Bảng chung làm mất thông tin khách hàng nào đóng góp lỗi.

`Transfer.Run` gom nhóm, dùng cùng quy tắc đếm trong mỗi nhóm, chia cho số dòng của nhóm rồi lấy trung bình các giá trị ấy. Assertion kiểm tra tổng chi phí 16 và trung bình theo khách hàng 2. Chạy trong `dotnet`:

```bash
dotnet run --no-restore -c Release --project LessonLab -- --transfer
```

Output đã quan sát:

```text
Row mean cost=3.200; equal-customer mean cost=2.000
```

Lặp tất cả dòng giống nhau của A làm cả tử/mẫu của A tăng gấp đôi, nên trung bình A vẫn 4 và trung bình khách hàng vẫn 2. Trung bình ticket thành 32/9, khoảng 3,556. Bất biến này đúng khi lặp theo cùng tỷ lệ toàn bộ tập của khách hàng, không phải chỉ lặp các lỗi.

Bài đổi đại lượng cần đánh giá và trọng số, không chỉ đổi tên biến. Nhớ Bài 08: trọng số cặp bằng nhau được biện minh bằng cỡ cặp bằng nhau; nhóm không đều cần nêu mục tiêu trọng số. Nếu mục tiêu triển khai là các khách hàng ngang nhau, học/validation cũng nên dùng mục tiêu đó khi so chính sách. Chỉ đổi dashboard cuối sau khi chọn bằng loss theo dòng chưa tối ưu loss theo khách hàng. Phần mở rộng tổng hợp dự đoán cố định, chưa học lại mô hình theo khách hàng hay bảo đảm công bằng với mọi khách hàng.

</details>


## 8. Tổng hợp quyết định có căn cứ

**Tổng hợp · 45 phút.** Trả lời riêng bốn câu rồi viết ghi chú quyết định ngắn. **Hoàn thành khi:** ghi chú có mục tiêu, feature sẵn có, quy tắc chọn, bằng chứng, điều chưa rõ và kiểm tra tiếp theo có thể đổi quyết định.

Ngưỡng đã chọn có thể được gọi là đúng khi baseline quy tắc cố định có chi phí test thấp hơn không?

<details>
<summary>Đáp án</summary>

Tìm kiếm train và lựa chọn validation có thể đúng theo yêu cầu, trong khi hiệu quả test kém hơn baseline. Tính đúng thuật toán, tối ưu thực nghiệm và ích lợi trên quan sát tương lai là ba nhận định khác nhau. Báo kết quả thay vì chọn winner mới từ lần đánh giá. Thu dữ liệu phát triển/đánh giá mới theo quy trình sửa đã nêu trước khi đề xuất production.

</details>


Khoảng Wilson cho accuracy test có sửa leakage hay chứng minh can thiệp của mô hình có ích không?

<details>
<summary>Đáp án</summary>

Không. Với predictor cố định và kết quả đúng/sai nhị phân IID phù hợp, Wilson từ Bài 07 mô tả độ bất định tỷ lệ accuracy với giới hạn coverage hữu hạn. Nó không xóa lựa chọn theo test, feature chưa có lúc dự đoán, outcome khách hàng liên kết hay phân phối trôi. Chi phí có trọng số không phải tỷ lệ Bernoulli. Độ bất định dự đoán cũng chưa xác định tác động nhân quả của ưu tiên ticket; cần thiết kế can thiệp phù hợp từ Bài 08.

</details>


Điểm 7 có nghĩa là xác suất trễ 70% không, và lab có kiểm tra calibration chưa?

<details>
<summary>Đáp án</summary>

Không. Đây là feature thứ tự tùy chọn trong miền đã nêu. Mô hình ngưỡng trả quyết định nhị phân, không ước lượng xác suất. Calibration xét xác suất dự đoán có khớp tần suất outcome theo một thiết kế đánh giá đã nêu hay không; bài chưa cài bộ ước lượng xác suất hoặc kiểm tra calibration. Chia feature cho 10 chưa biến nó thành xác suất đã được kiểm chứng.

</details>


Từ dữ liệu đã chạy, nên viết ghi chú quyết định thế nào?

<details>
<summary>Đáp án</summary>

Mục tiêu: ticket của khách hàng chưa thấy, dự đoán lúc nhận, cửa sổ outcome 24 giờ. Input sẵn có: điểm lúc tiếp nhận có version, không phải kết quả trễ về sau. Quy trình: khách hàng không trùng giữa train/validation/test; học trên train, chọn bằng validation theo FP+4*FN rồi cố định trước test. Ngưỡng được chọn: 5. Bằng chứng: test TP/FP/FN/TN=2/3/1/4, chi phí 7 so với nhãn phổ biến 12 và baseline ngưỡng 7 là 5. Dữ liệu giả lập nhỏ hỗ trợ quy trình đánh giá chạy được, chưa hỗ trợ triển khai hay tuyên bố tiết kiệm.

Điều chưa rõ: khách hàng/thời gian có đại diện không, label/outcome thiếu, feature sẵn có, chi phí/công suất và độ ổn định. Câu hỏi tiếp theo: trên dữ liệu phát triển mới có ngày rõ, cùng quy trình đã định có giảm loss theo ticket/khách hàng so với quy tắc cố định không? Giữ dữ liệu đánh giá mới chưa dùng và kiểm tra ranh giới thời gian/nhóm trước khi so. Câu hỏi rollout nhân quả về tác động ưu tiên là câu hỏi riêng.

</details>


Mô hình tư duy mới tuy nhỏ nhưng đầy đủ: việc học tìm trong họ quy tắc đã định, đánh giá bảo vệ ranh giới thông tin, đơn vị/loss quyết định ý nghĩa điểm số. Các hướng còn lại gồm mô hình phong phú hơn, chia theo thời gian, tiền xử lý đã học và đánh giá lồng nhau. Chưa có hướng nào cho phép khẳng định chất lượng mô hình phổ quát hôm nay.

## Nguồn và sử dụng lại

- Tài liệu/source scikit-learn tại commit đã dẫn hỗ trợ định nghĩa metric, ranh giới tiền xử lý và đường đánh giá đã đọc. [Giấy phép BSD-3-Clause](https://github.com/scikit-learn/scikit-learn/blob/102e5daf66759cf896beeee229d1bf7c80ab2ba4/COPYING). Không phân phối lại đoạn source; toàn bộ code C# là code giảng dạy viết mới.
- [Bài 07](../2026-10-11-sampling-uncertainty/lesson.md) hỗ trợ cầu nối kỳ vọng/độ bất định; [Bài 08](../2026-10-12-experimental-design/lesson.md) giới hạn nhận định nhân quả và trọng số đơn vị.
- Lời bài viết mới: CC BY 4.0. Code lab viết mới: MIT; ZIP có giấy phép.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 08 - Thiết kế thí nghiệm: chênh lệch chưa đủ để kết luận nhân quả](../2026-10-12-experimental-design/lesson.md) - Tách đánh giá dự đoán khỏi nhận định can thiệp.
- [Bài 07 - Độ bất định khi lấy mẫu: nhiều record chưa chắc có thêm bằng chứng](../2026-10-11-sampling-uncertainty/lesson.md) - Ôn đơn vị quan sát và giả định về độ bất định.
- [Hướng dẫn lab C#](../../../labs/honest-evaluation/dotnet/README.vi.md) - Môi trường đã pin, oracle và giới hạn thí nghiệm giả lập.

---

[← Bài trước: Bài 08 - Thiết kế thí nghiệm: chênh lệch chưa đủ để kết luận nhân quả](../2026-10-12-experimental-design/lesson.md) · [Danh sách bài học](../../README.md)
<!-- LESSON_NAVIGATION_END -->
