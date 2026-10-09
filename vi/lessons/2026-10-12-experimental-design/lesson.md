# Bài 08 - Thiết kế thí nghiệm: chênh lệch chưa đủ để kết luận nhân quả

[English](../../../lessons/2026-10-12-experimental-design/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/experimental-design/dotnet-lab.zip)

Một nhóm .NET gửi request nhỏ vào implementation mới và request lớn vào bản cũ. Nhánh mới có vẻ nhanh hơn dù không thay đổi gì. Hôm nay ta giữ workload cố định, đổi quy tắc phân nhóm và tách chênh lệch quan sát khỏi tác động nhân quả.

**Mục tiêu:** thiết kế phép so sánh có kiểm soát, chứng minh đại lượng mà ước lượng hướng tới, báo độ bất định do phân nhóm và giới hạn kết luận nhân quả. Planner chọn thiết kế thí nghiệm sau độ bất định khi lấy mẫu. Ta dùng lại kỳ vọng, phương sai, kiểm tra độc lập và khoảng nửa mở. Bài này bổ sung kết quả tiềm năng, yếu tố gây nhiễu, phân nhóm ngẫu nhiên theo cặp và kiểm định ngẫu nhiên hóa cho giả thuyết không tác động ở từng đơn vị.

## Các ý cốt lõi

- **Tác động so cùng một đơn vị dưới hai hành động.** Một request có thể mất 10 khi dùng bản cũ và 6 khi dùng bản mới. Tác động là -4, nhưng request thực chỉ cho kết quả của hành động đã nhận.
- **Phép so sánh cần thiết kế.** So request nhỏ ở nhánh mới với request lớn ở nhánh cũ trộn ảnh hưởng của implementation và kích thước request. Phân nhóm ngẫu nhiên làm việc gán nhánh độc lập với kết quả tiềm năng cố định theo thiết kế đã nêu; một lần phân nhóm vẫn có thể mất cân bằng.
- **Ghép cặp kiểm soát nguồn biến thiên đã biết.** Ghép hai đơn vị tương đồng trước khi phân nhóm, rồi chọn ngẫu nhiên một đơn vị nhận treatment. Mỗi cặp có đúng một treatment và một control, dù kết quả hai đơn vị có thể khác nhau.
- **Độ bất định xét các cách phân nhóm khác.** Cùng một nhóm đơn vị cố định có thể cho chênh lệch khác khi đổi cách gán nhánh. Liệt kê hết thiết kế nhỏ cho thấy độ phân tán đó; chưa phải lấy mẫu traffic tương lai.

Nếu chưa chạy lab, đọc bảng chạy từng bước, bảng bằng chứng và toàn bộ code có lời giải. Giới hạn setup ở 15 phút trong phần lab. Mọi kết quả dưới đây là số nguyên giả lập mang đơn vị mili giây; chương trình không đo latency dịch vụ.

## 1. Ôn lại và xác định phép so sánh

**Ôn lại · 20 phút.** Dựng lại ba đáp án planner chọn, rồi tách phép tính đúng khỏi phép so sánh có cơ sở. **Hoàn thành khi:** nêu được giới hạn mô hình của từng đáp án và thông tin thiết kế còn thiếu ở biểu đồ trước/sau.

1. Từ Bài 07: mức tin cậy danh nghĩa 95% của khoảng Wilson nghĩa là gì?

<details>
<summary>Đáp án</summary>

Trước lấy mẫu, khoảng ngẫu nhiên hướng tới chứa p cố định ở khoảng 95% mẫu mô hình lặp. Độ bao phủ Wilson hữu hạn có thể khác; không phải xác suất hậu nghiệm 0,95 của khoảng đã thấy hay bảo đảm cho dữ liệu lệch/phụ thuộc.

</details>

2. Từ Bài 05: `(Tenant,Occurred,Amount)` có vừa bao phủ tổng vừa bảo đảm thứ tự trang `(Occurred,Id)` không?

<details>
<summary>Đáp án</summary>

Nó bao phủ COUNT/SUM(Amount) theo tenant/thời gian, nhưng Amount phân định thời điểm bằng nhau trước rowid. Muốn đúng thứ tự trang, giữ ORDER BY và xét (Tenant,Occurred,Id,Amount); SQL Server có thể giữ Amount trong included column không thuộc khóa.

</details>

3. Từ Bài 01: giả định nào giúp dedupe có thời gian tuyến tính kỳ vọng, và vì sao benchmark không chứng minh p99 của dịch vụ?

<details>
<summary>Đáp án</summary>

Chi phí tính hash và so sánh khóa bị chặn, phân bố hash phù hợp và tổng chi phí tăng dung lượng tuyến tính cho phép suy ra chi phí kỳ vọng O(n). Nhiều khóa có cùng hash có thể làm tăng số phép so sánh. Benchmark chỉ đo dữ liệu và môi trường đã chọn, chưa phản ánh hàng đợi, phân bố khóa, mức dùng bộ nhớ cao nhất hay thời gian xử lý request của dịch vụ thực tế.

</details>


Query đúng vẫn có thể lấy sai nhóm để so sánh. Benchmark giả lập nhanh hơn chưa xác minh tác động production. Khoảng Wilson mô tả tỷ lệ theo mô hình của nó; chưa sửa được deployment gửi workload khác nhau vào hai nhánh. Câu hỏi tiếp theo là hai nhánh được tạo ra như thế nào.

## 2. Xác định câu hỏi nhân quả trước khi tính

**Nền tảng · 50 phút.** Chú thích bảng sáu cặp, suy ra kỳ vọng và nêu bất biến phân nhóm. **Hoàn thành khi:** giải thích được vì sao một cách gán có thể lệch tác động thật, dù ước lượng đúng theo kỳ vọng trên thiết kế.

### Một đơn vị, hai kết quả tiềm năng

Giả sử u0 cho kết quả 10 dưới control và 6 dưới treatment; u1 cho 14 và 10. Gán treatment cho u0 quan sát 6, còn control cho u1 quan sát 14. Chênh lệch là -8 dù tác động trên mỗi đơn vị đều là -4. Đổi nhánh cho chênh lệch 10-10=0. Trung bình hai chênh lệch có xác suất bằng nhau là -4.

Gọi `Y_i(0)` và `Y_i(1)` là kết quả tiềm năng cố định của đơn vị i dưới hai hành động được định nghĩa rõ. `Z_i` bằng 0 hoặc 1 là nhánh được gán. Kết quả quan sát là `Y_i = Y_i(Z_i)` theo giả định nhất quán: hành động thực sự được thực hiện đúng với hành động đã định nghĩa. Đại lượng đích cho nhóm cố định gồm N đơn vị là:

```text
tau = (1/N) * sum_i [Y_i(1) - Y_i(0)]
```

Ta giả định việc gán treatment cho đơn vị khác không đổi kết quả của đơn vị này. Queue, cache hay database có giới hạn dung lượng dùng chung có thể vi phạm giả định không ảnh hưởng chéo đó. Cần xác định hai phiên bản, cửa sổ quan sát, đơn vị hợp lệ và cách thu kết quả. Một request thường không cho cả hai kết quả cùng lúc; replay sau đó cũng đổi thời gian/trạng thái cache. Chỉ mô phỏng mới cho oracle thấy cả hai kết quả tiềm năng.

Phân nhóm ngẫu nhiên và lấy mẫu ngẫu nhiên trả lời hai câu hỏi khác nhau. Phân nhóm hỗ trợ so hành động trong nhóm đang xét. Lấy mẫu hỗ trợ suy rộng tới quần thể xác định. Gán ngẫu nhiên cho mười hai đơn vị tiện lấy chưa khiến chúng đại diện traffic production tương lai.

### Bất biến và bảng chạy từng bước

Tạo B=6 cặp từ mười hai đơn vị dựa trên thông tin có trước treatment. Trong mỗi cặp, phép chọn độc lập với xác suất bằng nhau quyết định đơn vị nhận treatment; đơn vị còn lại nhận control. Bất biến là mỗi cặp có đúng một treatment và một control. Thiết kế toán học có `2^B=64` cách gán cùng xác suất. Chương trình liệt kê tất cả, không sinh cách gán ngẫu nhiên bằng RNG production.

Baseline cố định là `[10,14,20,28,40,52,60,76,80,100,120,144]`; treatment trừ 4 ở mọi đơn vị. Ghép các giá trị liền nhau. Mask 21 là ví dụ chọn sẵn trong code, không phải lượt rút ngẫu nhiên: bit b=1 gán treatment cho đơn vị bên trái cặp b. Hoàn thành bảng và tổng lũy kế các chênh lệch treatment trừ control.

<details>
<summary>Đáp án</summary>

| Cặp | Baseline trái/phải | Bên nhận treatment | Trái quan sát | Phải quan sát | d_b | Tổng lũy kế |
|---|---|---|---|---|---|---|
| 0 | 10/14 | Trái | 6 | 14 | -8 | -8 |
| 1 | 20/28 | Phải | 20 | 24 | 4 | -4 |
| 2 | 40/52 | Trái | 36 | 52 | -16 | -20 |
| 3 | 60/76 | Phải | 60 | 72 | 12 | -8 |
| 4 | 80/100 | Trái | 76 | 100 | -24 | -32 |
| 5 | 120/144 | Phải | 120 | 140 | 20 | -12 |

Mỗi cặp có đúng một treatment và một control. Ước lượng bằng -12/6=-2; tác động oracle là -4 vì cả mười hai tác động riêng đều bằng -4. Biến tích lũy của bộ ước lượng bằng tổng treatment trừ control trên các cặp đã xử lý. Hướng gán đổi chênh lệch cần cộng nhưng giữ cả hai bất biến. Mask có bit 0,2,4 bật; đọc ký hiệu nhị phân từ trái sang như thứ tự cặp sẽ đảo ý nghĩa đó.

</details>


Gọi `d_b` là treatment trừ control quan sát trong cặp b. Ước lượng là `D = sum_b d_b / B`. Mỗi nhánh đều có B đơn vị nên D cũng bằng trung bình treatment trừ trung bình control. Trọng số cặp bằng nhau cho mọi đơn vị trong 2B đơn vị trọng số bằng nhau; block có kích thước khác cần lập luận trọng số khác.

### Vì sao ước lượng hướng tới tác động của nhóm

Với cặp gồm a và c, hai chênh lệch có thể là `Y_a(1)-Y_c(0)` và `Y_c(1)-Y_a(0)`, mỗi giá trị có xác suất 1/2. Trung bình của chúng bằng nửa tổng tác động riêng của hai đơn vị. Cộng B cặp rồi chia B cho `E_design[D]=tau`. Đây là kỳ vọng theo cách gán với kết quả tiềm năng cố định, chưa khẳng định D quan sát bằng tau. Tính tuyến tính không cần kết quả IID. Phân nhóm độc lập với xác suất bằng nhau ở từng cặp cần cho phép liệt kê đồng xác suất và cộng phương sai cặp.

Điều gì làm đẳng thức mất hiệu lực nếu luôn gán treatment cho đơn vị nhẹ hơn? Nêu phản ví dụ không tác động.

<details>
<summary>Đáp án</summary>

Luôn chọn đơn vị trái/nhẹ chỉ cho `Y_left(1)-Y_right(0)`, không còn hai chênh lệch đồng trọng số. Khi không tác động, chúng bằng -4,-8,-12,-16,-20,-24, trung bình -14 trong khi tau=0. Hai nhánh vẫn có sáu đơn vị nên số đếm bằng nhau chưa sửa yếu tố gây nhiễu. Phân nhóm ngẫu nhiên loại lựa chọn có hệ thống này theo kỳ vọng, chưa ép một chênh lệch ví dụ bằng không.

</details>


Trong dữ liệu có tác động hằng, gọi độ lệch baseline mỗi cặp là `g_b = baseline phải - baseline trái`. Chênh lệch cặp bằng `-4 + g_b` hoặc `-4 - g_b`, nên phương sai bằng `g_b^2`. Các cách chọn ở từng cặp độc lập cho:

```text
Var_design(D) = sum_b g_b^2 / B^2
SD_design(D)  = sqrt(sum_b g_b^2) / B
```

Ở đây các độ lệch là 4,8,12,16,20,24. SD bằng `sqrt(1456)/6`, khoảng 6,3596. Đây là độ phân tán của D trên mọi cách gán trong thiết kế giả lập. Nó không phải SD của kết quả đơn vị hay sai số chuẩn biết được từ dữ liệu thật: dữ liệu thật không cho thấy mọi kết quả tiềm năng. Khi tác động thay đổi theo đơn vị, cần hai chênh lệch có thể của từng cặp; công thức độ lệch trên dựa vào tác động hằng ở dữ liệu này.

Vì sao cộng cùng tác động -4 đổi trung bình nhưng không đổi SD này?

<details>
<summary>Đáp án</summary>

Mọi D có thể đều dịch -4, nên trung bình dịch -4 còn độ lệch so với trung bình giữ nguyên. Toàn bộ phân phối gán dịch mà không đổi độ phân tán. Điều này giả định tác động cộng hằng trên mọi đơn vị; tác động khác nhau cần tính lại. Chưa có kết luận về nhiễu của dịch vụ thật.

</details>


Nghỉ - 10 phút, rời màn hình.

## 3. Đọc giả định thiết kế và xét sự đảo chiều

**Đọc nguồn · 45 phút.** Đọc các phần đã giới hạn và lập bảng nhận định/bằng chứng/giới hạn. **Hoàn thành khi:** tách phân nhóm khỏi lấy mẫu, chỉ ra yếu tố gây nhiễu và chỉnh nhận định rằng phân nhóm ngẫu nhiên cân bằng hai nhóm.

Đọc Hernán và Robins, [Causal Inference: What If, bản tháng 8/2026 trên trang tác giả](https://miguelhernan.org/s/hernanrobins_WhatIf_19aug26.pdf): mục 1.1-1.2 (trang in 3-6), gồm Fine Point 1.1 về ảnh hưởng chéo; và mục 2.1 (trang in 13-16) về phân nhóm ngẫu nhiên lý tưởng và khả năng hoán đổi. Ta dùng cách diễn đạt bằng kết quả tiềm năng cùng giả định của thí nghiệm lý tưởng, chưa dùng các bộ ước lượng dữ liệu quan sát ở chương sau. Khả năng hoán đổi ở đây nghĩa là cách gán không chọn có hệ thống các đơn vị có kết quả tiềm năng khác nhau theo thiết kế; không đòi kết quả thực tế phải bằng nhau.

Đọc thêm OpenStax [1.4, Experimental Design and Ethics](https://openstax.org/books/introductory-statistics-2e/pages/1-4-experimental-design-and-ethics), phần mở đầu tới ví dụ aspirin và che giấu nhánh được gán. Các ví dụ treatment, đơn vị thí nghiệm và control giải thích điều được thay đổi. Cần chỉnh cách nói rộng rằng mọi yếu tố ẩn được trải đều: phân nhóm hữu hạn cân bằng theo kỳ vọng, và thí nghiệm lý tưởng vẫn có biến thiên do gán nhánh. Che giấu nhánh giảm ảnh hưởng lên hành vi/đo lường; đây là việc khác với phân nhóm.

Lập bảng cho ba nhận định: phân nhóm ngẫu nhiên xác định tác động từng đơn vị; số đơn vị hai nhánh bằng nhau bảo đảm workload bằng nhau; chênh lệch của nhóm có thể hướng tới tác động trung bình dưới thiết kế xác định.

<details>
<summary>Đáp án</summary>

| Nhận định | Bằng chứng | Giới hạn |
|---|---|---|
| Xác định tác động từng đơn vị | What If 1.1 chỉ quan sát Y_i(Z_i) | Thiếu kết quả còn lại; riêng phân nhóm chưa cho biết nó |
| Số đếm bằng nhau nghĩa là workload bằng nhau | Sáu cặp bảo đảm sáu đơn vị mỗi nhánh | Bảng vẫn có tổng baseline khác nhau; còn mất cân bằng ngẫu nhiên |
| Chênh lệch hướng tới tác động trung bình | Hai hướng gán đồng xác suất cho trung bình tác động cặp | Cần cách gán đã nêu, kết quả nhất quán/không ảnh hưởng chéo; suy rộng cần thêm |

Hai nhận định đầu sai khi nói như trên. Nhận định thứ ba có cơ sở từ phép suy ra cho nhóm hữu hạn. Lập luận thí nghiệm lý tưởng của sách và kỳ vọng thiết kế ở đây xét phép so dưới giả định; chưa chứng minh mọi yếu tố ẩn cân bằng tuyệt đối trong một lần phân nhóm hữu hạn.

</details>


### Yếu tố gây nhiễu có thể đảo chiều phép so sánh tổng

Yếu tố gây nhiễu góp phần quyết định cả nhánh được gán lẫn kết quả. Kích thước request làm cả hai khi kỹ sư chủ động đưa request nhỏ vào đường xử lý mới. Xét bảng quan sát về thành công thay vì latency:

| Workload | Control thành công/tổng | Treatment thành công/tổng |
|---|---|---|
| Dễ | 81/90 = 90% | 19/20 = 95% |
| Khó | 1/10 = 10% | 24/80 = 30% |
| Tất cả | 82/100 = 82% | 43/100 = 43% |

Treatment có tỷ lệ quan sát cao hơn ở từng workload nhưng thấp hơn khi gộp. Giải thích sự đảo chiều và tính phép so mô tả đã chuẩn hóa với trọng số dễ/khó bằng nhau. Kết quả có xác minh nhân quả không?

<details>
<summary>Đáp án</summary>

Control có 90% đơn vị dễ còn treatment chỉ 20%, nên tỷ lệ gộp dùng trọng số khác nhau. Trọng số dễ/khó bằng nhau cho control `(0.90+0.10)/2=0.50`, treatment `(0.95+0.30)/2=0.625`, chênh lệch mô tả +0,125, tức 12,5 điểm phần trăm. Cách này chuẩn hóa một yếu tố đã đo, chưa loại lựa chọn ẩn, kết quả thiếu hay yếu tố gây nhiễu khác. Khi chưa có lập luận gán/nhận dạng nhân quả từ dữ liệu quan sát phù hợp, đây vẫn là mối liên hệ. Phải chọn trọng số đích có lý do trước khi tìm kết quả thuận lợi.

</details>


Deploy trước/sau cũng chịu vấn đề này: traffic, sự cố và trạng thái cache có thể đổi theo thời gian. Phân nhóm sau khi loại các record mất telemetry, ghép cặp theo metric bị treatment tác động hoặc dừng khi thấy kết quả thuận lợi sẽ đổi quy trình. Chốt điều kiện hợp lệ, biến ghép cặp, xác suất phân nhóm, metric, cửa sổ quan sát, chính sách dữ liệu thiếu và quy tắc dừng trước khi gán nhánh. Một feature flag ổn định chưa bảo đảm các điều này.

Điều gì đổi nếu mười dòng retry đại diện một tenant được gán nhánh ban đầu thay vì mười tenant?

<details>
<summary>Đáp án</summary>

Đơn vị gán vẫn là tenant; dòng retry không tạo quyết định gán mới. Xác định một kết quả tenant theo quy tắc tổng hợp/cửa sổ định trước, hoặc dùng phân tích tôn trọng cụm tenant. Mười bản sao kết quả tenant dùng cùng nhánh và có thể chung sự cố. Dedupe loại ID lặp nhưng chưa xác minh độc lập giữa tenant hay loại ảnh hưởng chéo.

</details>


## 4. Đường gán variation thực tế trong GrowthBook

**Đọc mã nguồn · 45 phút.** Chạy từng bước đường SDK đã pin và xét biên các khoảng. **Hoàn thành khi:** tách cơ chế gán đã xác minh khỏi thiết kế và telemetry còn cần để báo kết quả nhân quả.

GrowthBook là nền tảng feature flag và thí nghiệm. JavaScript SDK giải quyết việc chọn variation từ danh tính/cấu hình và báo exposure. Chỉ đọc các phần sau ở commit `7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e`:

- [core.ts](https://github.com/growthbook/growthbook/blob/7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e/packages/sdk-js/src/core.ts): khai báo `runExperiment`/kiểm tra số variation đầu tiên (427-447), thiếu danh tính để hash (528-545), hash/khoảng/loại khỏi thí nghiệm (674-730), gọi callback (814-833); `getHashAttribute` (1073-1108) và `onExperimentViewed` (76-113).
- [util.ts](https://github.com/growthbook/growthbook/blob/7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e/packages/sdk-js/src/util.ts): các phiên bản hash (19-46), `inRange`/`chooseVariation` dùng khoảng nửa mở (53-75), và `getBucketRanges` (183-233).

Link trỏ tới code cố định, không phải docs đang thay đổi. [Hướng dẫn JavaScript SDK](https://docs.growthbook.io/lib/js) hiện tại, phần khởi tạo và ví dụ tracking callback, cung cấp ngữ cảnh ứng dụng. Ta chưa chạy SDK, theo dõi lưu trữ/retry mạng hay đọc bộ máy thống kê, bandit và mọi đường override/sticky bucket của nền tảng. Source có giấy phép MIT ngoài các thư mục enterprise đã liệt kê; lab là code tự viết, không phải bản chuyển SDK.

### Đường được đọc xác minh điều gì

Khi đánh giá experiment thông thường và không có gán override/sticky, SDK lấy danh tính để hash (`id` mặc định), kết hợp với seed/key và phiên bản hash, chọn khoảng variation nửa mở, rồi loại trường hợp thiếu danh tính, phiên bản không hợp lệ hoặc bucket nằm ngoài các khoảng. Input/cấu hình cố định làm đường này tất định. Workload là nhiều lần đánh giá feature theo danh tính ứng dụng; phần code này chưa cho kích thước benchmark hay bảo đảm throughput.

Đường này tránh tung đồng xu mới mỗi lần đánh giá feature, vốn có thể đổi variation của người dùng trong cùng lượt truy cập. Tính ổn định phụ thuộc danh tính, seed, phiên bản hash và cấu hình khoảng. Source giữ phiên bản 1 để tương thích; comment gọi phiên bản 2 là không lệch. Code xác minh hai công thức khác nhau, chưa xác minh tính độc lập/đều cho mọi phân bố ID thực tế. Bucket phân bố đều là giả định cần kiểm tra trên danh tính đã chọn, chưa phải định lý từ comment.

Với hai variation có trọng số bằng nhau và coverage 0,8, chạy `getBucketRanges` rồi `chooseVariation`. Các bucket 0.39,0.40,0.50,0.89,0.90 thuộc variation nào? Vì sao coverage không phải khoảng liên tục `[0,0.8)`?

<details>
<summary>Đáp án</summary>

| Bucket n | Thuộc khoảng | Kết quả |
|---|---|---|
| 0.39 | [0,0.4) | Variation 0 |
| 0.40 | Không khoảng nào | Loại (-1) |
| 0.50 | [0.5,0.9) | Variation 1 |
| 0.89 | [0.5,0.9) | Variation 1 |
| 0.90 | Không khoảng nào | Loại (-1) |

Điểm bắt đầu tăng theo toàn bộ trọng số 0,5, còn mỗi khoảng được nhận rộng `coverage*weight=0.4`. Vì vậy có khoảng trống [0.4,0.5) và [0.9,1), tổng độ dài được nhận 0,8. `chooseVariation` quét các khoảng, loại đầu trên. Với mô hình bucket đều, xác suất được nhận là 0,8 và mỗi variation là 0,4; ID thực cố định chưa chắc có đúng tỷ lệ đó. `coverage` ở đây điều khiển điều kiện vào thí nghiệm, khác độ bao phủ tin cậy ở Bài 07. Đây là chạy công thức đã pin bằng tay, chưa chạy SDK.

</details>


### Áp dụng trong dự án .NET/Angular/Azure

Với thí nghiệm checkout, chọn tenant hoặc user làm đơn vị gán trước khi xử lý request, lưu hoặc dựng lại cách gán ổn định theo cấu hình đã chốt, rồi nối kết quả về đơn vị đó. Quyết định hiển thị Angular và hành động ở service .NET phải thống nhất phiên bản experiment và danh tính đơn vị. Ghi riêng nhánh được gán, hành động thực hiện, điều kiện hợp lệ, exposure và outcome. Phân tích mọi đơn vị hợp lệ đã được gán theo chính sách outcome định trước; chỉ giữ những người về sau bấm nút có thể tạo sai lệch chọn mẫu. Khi việc thực hiện không đầy đủ, tác động của gán nhánh khác tác động của thực sự nhận hành động.

Đây là đề xuất thiết kế của bài học, chưa phải deployment đã xác minh hay API GrowthBook .NET. Nếu hành động đổi queue/cache dùng chung, gán theo user có thể vi phạm giả định không ảnh hưởng chéo; cân nhắc tài nguyên tách biệt hoặc thiết kế theo cụm/block thời gian, rồi dùng phân phối gán tương ứng. Lab theo cặp chưa xác minh các thiết kế production đó.

Lập bảng thứ hai: hash, loại ID thiếu và dedupe callback xác minh điều gì, còn thiếu cơ sở cho nhận định nhân quả hoặc delivery nào?

<details>
<summary>Đáp án</summary>

| Đã xác minh trong phần code | Suy luận thiết kế hoặc bằng chứng còn thiếu |
|---|---|
| Danh tính/seed/phiên bản hash cố định quyết định bucket trên đường thông thường | Cần kiểm tra phân bố danh tính và chốt cấu hình trước khi coi là phân nhóm ngẫu nhiên phù hợp |
| Danh tính hash rỗng làm đơn vị bị loại khỏi đánh giá experiment | Các ID bị loại có thể là nhóm được chọn có hệ thống; chưa xác minh tính đại diện |
| `trackedExperiments`, khi tồn tại, chặn dedupe key lặp trong ngữ cảnh user đó | Chưa chứng minh exposure được giao exactly-once bền vững hoặc kết quả đầy đủ |
| Tracking callback nhận experiment/result/ngữ cảnh user | Nối database và phân tích nhân quả là việc thêm của ứng dụng |

Cơ chế đã đọc hỗ trợ thực hiện thí nghiệm. Đề xuất đồng bộ danh tính Angular/.NET và phân tích các đơn vị đã gán là suy luận thiết kế, chưa phải integration đã đo. Set theo dõi cục bộ khác receipt bền vững ở Bài 06.

</details>


Ăn trưa - 30 phút, ăn và nghỉ.

## 5. Implement thiết kế và hai phép kiểm tra độc lập

**Lab C# · 75 phút.** Chạy ví dụ, đọc input của ước lượng, kiểm tra oracle và sửa lỗi dấu. **Hoàn thành khi:** bảng khớp, `--check` qua và giải thích được dữ liệu nào bộ ước lượng thực được phép thấy. Dừng setup sau 15 phút; dùng lời giải nếu thiếu SDK đã pin.

Tạo lab đầy đủ dưới đây hoặc giải nén ZIP. Không đưa kết quả tiềm năng vào bộ ước lượng quan sát: `Observe` chỉ cho thấy kết quả của hành động nhận được, `Estimate` nhận `Seen[]`, còn riêng `Oracle` đọc cả hai kết quả. Liệt kê mọi cách gán theo cặp, so với oracle quét hai nhánh riêng, rồi xét hết các bảng kết quả tiềm năng nhỏ. Chạy demo, kiểm tra và thí nghiệm. Các kiểm tra xác minh được gì?

<details>
<summary>Đáp án - toàn bộ lab chạy được</summary>

Dùng SDK **10.0.401**, runtime **Microsoft.NETCore.App 10.0.12**, target **net10.0**; tắt roll-forward SDK/runtime. Không có NuGet dependency ngoài; lock file rỗng vẫn được kiểm tra. Cần SDK và reference pack đã pin để restore lần đầu. Chương trình không gọi mạng/database, chỉ ghi `assignments.csv` khi chạy experiment.

Giải nén ZIP hoặc tạo `dotnet` với các file sau. Chạy từ thư mục `dotnet`; `cd dotnet` bên dưới giả định đang ở thư mục chứa nó.

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
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
</Project>
```


`LessonLab/packages.lock.json`:
<!-- lab-file: LessonLab/packages.lock.json -->
```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {}
  }
}
```

Lệnh chạy:
```bash
cd dotnet
dotnet --version
dotnet restore LessonLab --locked-mode
dotnet run --no-restore -c Release --project LessonLab
dotnet run --no-restore -c Release --project LessonLab -- --check
dotnet run --no-restore -c Release --project LessonLab -- --experiment
```


`LessonLab/Design.cs`:
<!-- lab-file: LessonLab/Design.cs -->
```csharp
public sealed record Unit(string Id, int Y0, int Y1);
public sealed record Pair(Unit Left, Unit Right);
public sealed record Seen(string LeftId, string RightId, bool LeftTreated,
    int LeftOutcome, int RightOutcome);
public sealed record Tail(int Extreme, int Total)
{
    public double P => (double)Extreme / Total;
}

public static class Design
{
    public static void Validate(Pair[] pairs)
    {
        if (pairs.Length is < 1 or > 10)
            throw new ArgumentOutOfRangeException(nameof(pairs));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var u in pairs.SelectMany(p => new[] { p.Left, p.Right }))
            if (string.IsNullOrWhiteSpace(u.Id) || !ids.Add(u.Id) ||
                u.Y0 is < 0 or > 10000 || u.Y1 is < 0 or > 10000)
                throw new ArgumentException("Invalid unit, outcome or repeated ID.");
    }

    public static Seen[] Observe(Pair[] pairs, int mask)
    {
        Validate(pairs);
        if (mask < 0 || mask >= (1 << pairs.Length))
            throw new ArgumentOutOfRangeException(nameof(mask));
        return pairs.Select((p, b) =>
        {
            bool left = (mask & (1 << b)) != 0;
            return new Seen(p.Left.Id, p.Right.Id, left,
                left ? p.Left.Y1 : p.Left.Y0,
                left ? p.Right.Y0 : p.Right.Y1);
        }).ToArray();
    }

    public static long[] Differences(Seen[] seen)
    {
        if (seen.Length is < 1 or > 10)
            throw new ArgumentOutOfRangeException(nameof(seen));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var s in seen)
            if (string.IsNullOrWhiteSpace(s.LeftId) || !ids.Add(s.LeftId) ||
                string.IsNullOrWhiteSpace(s.RightId) || !ids.Add(s.RightId) ||
                s.LeftOutcome is < 0 or > 10000 || s.RightOutcome is < 0 or > 10000)
                throw new ArgumentException("Invalid observed record.");
        return seen.Select(s => s.LeftTreated
            ? (long)s.LeftOutcome - s.RightOutcome
            : (long)s.RightOutcome - s.LeftOutcome).ToArray();
    }

    public static double Estimate(Seen[] seen) =>
        (double)Differences(seen).Sum() / seen.Length;

    // Only a synthetic oracle can see both potential outcomes.
    public static double Oracle(Pair[] pairs)
    {
        Validate(pairs);
        return pairs.SelectMany(p => new[] { p.Left, p.Right })
            .Average(u => (double)u.Y1 - u.Y0);
    }

    public static double[] Distribution(Pair[] pairs)
    {
        Validate(pairs);
        return Enumerable.Range(0, 1 << pairs.Length)
            .Select(mask => Estimate(Observe(pairs, mask))).ToArray();
    }

    public static Tail SharpNull(Seen[] seen)
    {
        long[] d = Differences(seen);
        long observed = Math.Abs(d.Sum());
        int extreme = 0, total = 1 << d.Length;
        for (int mask = 0; mask < total; mask++)
        {
            long sum = 0;
            for (int b = 0; b < d.Length; b++)
                sum += (mask & (1 << b)) == 0 ? d[b] : -d[b];
            if (Math.Abs(sum) >= observed) extreme++;
        }
        return new Tail(extreme, total);
    }
}
```


`LessonLab/Experiment.cs`:
<!-- lab-file: LessonLab/Experiment.cs -->
```csharp
using System.Globalization;

public static class Experiment
{
    public static Pair[] Cohort(int effect = -4, bool poor = false)
    {
        int[] baseline = [10, 14, 20, 28, 40, 52, 60, 76, 80, 100, 120, 144];
        Unit[] units = baseline.Select((y, i) => new Unit($"u{i}", y, y + effect)).ToArray();
        return Enumerable.Range(0, 6).Select(b => poor
            ? new Pair(units[b], units[b + 6])
            : new Pair(units[2 * b], units[2 * b + 1])).ToArray();
    }

    public static void Demo()
    {
        var pairs = Cohort();
        var seen = Design.Observe(pairs, 21);
        Console.WriteLine("pair,left_treated,left_seen,right_seen,treatment_minus_control");
        var d = Design.Differences(seen);
        for (int b = 0; b < seen.Length; b++)
            Console.WriteLine($"{b},{seen[b].LeftTreated},{seen[b].LeftOutcome},{seen[b].RightOutcome},{d[b]}");
        var p = Design.SharpNull(seen);
        Console.WriteLine($"estimate={Design.Estimate(seen):F4}; synthetic_oracle={Design.Oracle(pairs):F4}; sharp_null={p.Extreme}/{p.Total}={p.P:F4}");
    }

    public static void Run()
    {
        Console.WriteLine("effect,pairing,policy,estimate,design_mean,design_sd,min,max,sharp_null_p");
        using var csv = new StreamWriter("assignments.csv");
        csv.WriteLine("effect,pairing,mask,estimate");
        foreach (int effect in new[] { 0, -4 })
        foreach (bool poor in new[] { false, true })
        {
            var pairs = Cohort(effect, poor);
            double[] values = Design.Distribution(pairs);
            double mean = values.Average();
            double sd = Math.Sqrt(values.Average(x => (x - mean) * (x - mean)));
            string pairing = poor ? "poor" : "close";
            for (int mask = 0; mask < values.Length; mask++)
                csv.WriteLine(FormattableString.Invariant($"{effect},{pairing},{mask},{values[mask]:F8}"));
            var seen = Design.Observe(pairs, 21);
            Console.WriteLine($"{effect},{pairing},random-pair,{Design.Estimate(seen):F4},{mean:F4},{sd:F4},{values.Min():F4},{values.Max():F4},{Design.SharpNull(seen).P:F4}");
            var selected = Design.Observe(pairs, 63);
            // The randomization distribution is invalid for this deterministic policy.
            Console.WriteLine($"{effect},{pairing},select-low,{Design.Estimate(selected):F4},NA,NA,NA,NA,NA");
        }
        Console.WriteLine("# 64 equally weighted assignments per random-pair case; wrote assignments.csv; synthetic milliseconds, not measured latency");
    }
}
```


`LessonLab/Checks.cs`:
<!-- lab-file: LessonLab/Checks.cs -->
```csharp
public static class Checks
{
    private static void Require(bool ok, string message)
    {
        if (!ok) throw new Exception(message);
    }

    private static void Invalid(Action action)
    {
        try { action(); }
        catch (ArgumentException) { return; }
        throw new Exception("Invalid input accepted.");
    }

    private static int Bits(int mask)
    {
        int n = 0;
        while (mask != 0) { n += mask & 1; mask >>= 1; }
        return n;
    }

    public static void Run()
    {
        var pairs = Experiment.Cohort();
        double[] actual = Design.Distribution(pairs);
        // Independent oracle: select 6 of 12, retain one per pair, scan arm totals.
        var independent = new List<double>();
        for (int mask = 0; mask < (1 << 12); mask++)
        {
            if (Bits(mask) != 6) continue;
            long treatment = 0, control = 0;
            bool valid = true;
            for (int b = 0; b < 6; b++)
            {
                bool left = (mask & (1 << (2 * b))) != 0;
                bool right = (mask & (1 << (2 * b + 1))) != 0;
                if (left == right) { valid = false; break; }
                var p = pairs[b];
                treatment += left ? p.Left.Y1 : p.Right.Y1;
                control += left ? p.Right.Y0 : p.Left.Y0;
            }
            if (valid) independent.Add((double)(treatment - control) / 6);
        }
        Require(independent.Count == 64, "Assignment space differs.");
        Require(actual.Order().SequenceEqual(independent.Order()), "Independent arm scan differs.");
        Require(Math.Abs(actual.Average() - Design.Oracle(pairs)) < 1e-12, "Expectation differs.");
        Require(Math.Abs(actual.Average(x => (x + 4) * (x + 4)) - 1456.0 / 36) < 1e-12,
            "Design variance differs.");
        var seen = Design.Observe(pairs, 21);
        Require(Design.Differences(seen).SequenceEqual(new long[] { -8, 4, -16, 12, -24, 20 }),
            "Trace differs.");
        Require(Design.Estimate(seen) == -2, "Estimate differs.");

        // Exhaust all 3^8 potential-outcome tables for four units in two pairs.
        for (int table = 0; table < 6561; table++)
        {
            int code = table;
            var units = new Unit[4];
            for (int i = 0; i < 4; i++)
            {
                int y0 = code % 3; code /= 3;
                int y1 = code % 3; code /= 3;
                units[i] = new Unit($"id{i}", y0, y1);
            }
            Pair[] tiny = [new(units[0], units[1]), new(units[2], units[3])];
            long sum = 0;
            for (int mask = 0; mask < 4; mask++) sum += Design.Differences(Design.Observe(tiny, mask)).Sum();
            long effects = units.Sum(u => (long)u.Y1 - u.Y0);
            Require(sum == 2 * effects, "Unbiasedness identity differs.");
        }
        var nullPairs = Experiment.Cohort(0);
        int rejections = 0;
        for (int mask = 0; mask < 64; mask++)
        {
            var tail = Design.SharpNull(Design.Observe(nullPairs, mask));
            Require(tail.Total == 64 && tail.Extreme is >= 1 and <= 64, "Tail bounds differ.");
            if (20 * tail.Extreme <= tail.Total) rejections++;
        }
        Require(rejections == 2, "Sharp-null size differs.");
        Require(Design.SharpNull(Design.Observe(nullPairs, 63)).Extreme == 2, "Inclusive tails differ.");
        var equal = new[] { new Pair(new Unit("a", 5, 5), new Unit("b", 5, 5)) };
        Require(Design.SharpNull(Design.Observe(equal, 0)).P == 1, "Zero differences differ.");
        var reversed = seen.Select(s => new Seen(s.RightId, s.LeftId, !s.LeftTreated,
            s.RightOutcome, s.LeftOutcome)).ToArray();
        Require(Design.Estimate(reversed) == Design.Estimate(seen), "Pair relabeling differs.");
        Invalid(() => Design.Observe(pairs, -1));
        Invalid(() => Design.Observe(pairs, 64));
        Invalid(() => Design.Validate([]));
        Invalid(() => Design.Validate([new Pair(pairs[0].Left, pairs[0].Left)]));
        Invalid(() => Design.Validate([new Pair(new Unit("x", -1, 2), new Unit("y", 1, 2))]));
        Invalid(() => Design.Validate(Enumerable.Repeat(equal[0], 11).ToArray()));
        Invalid(() => Design.Estimate([]));
        Invalid(() => Design.Estimate([new Seen("a", "a", true, 1, 2)]));
        Console.WriteLine("PASS: 64 independent assignments; 6561 potential tables; variance; sharp-null size 2/64; ties; validation.");
    }
}
```


`LessonLab/Program.cs`:
<!-- lab-file: LessonLab/Program.cs -->
```csharp
using System.Globalization;

CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args.Length == 0) Experiment.Demo();
else if (args.SequenceEqual(new[] { "--check" })) Checks.Run();
else if (args.SequenceEqual(new[] { "--experiment" })) Experiment.Run();
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

Demo đã chạy, cũng là kết quả dự kiến khi chạy lại:
```text
pair,left_treated,left_seen,right_seen,treatment_minus_control
0,True,6,14,-8
1,False,20,24,4
2,True,36,52,-16
3,False,60,72,12
4,True,76,100,-24
5,False,120,140,20
estimate=-2.0000; synthetic_oracle=-4.0000; sharp_null=54/64=0.8438
```

Kiểm tra đã chạy:
```text
PASS: 64 independent assignments; 6561 potential tables; variance; sharp-null size 2/64; ties; validation.
```

Phép quét độc lập chọn 6 trong 12 đơn vị bằng mask 12 bit, giữ các cách có đúng một treatment mỗi cặp, rồi cộng hai nhánh trực tiếp; nó không dùng `Observe`/`Differences`. Có 924 tập cân bằng, trong đó 64 tập đúng thiết kế theo cặp. So cả đa tập 64 ước lượng bảo vệ số lần xuất hiện lặp. Kiểm tra 6561 bảng `3^8` xét hết kết quả tiềm năng 0,1,2 của bốn đơn vị trong hai cặp; đẳng thức tổng nguyên kiểm tra tính không lệch, không dựa vào gần đúng double. Kiểm tra phương sai đối chiếu với 1456/36; kiểm tra đổi nhãn, trường hợp bằng nhau, đầu vào và mức lỗi null bổ sung các cơ chế khác.

Giới hạn 1-10 cặp chặn phép liệt kê tại 1024 cách. Mỗi outcome thuộc 0-10000, ID không rỗng và không lặp. Tổng nguyên `long` cùng so trị tuyệt đối tránh lỗi dấu và sai số ở biên p-value; trung bình/SD in bằng double có làm tròn. `Distribution` có thời gian O(B*2^B), bộ nhớ O(2^B+B); `SharpNull` có thời gian O(B*2^B), bộ nhớ O(B). Đây là liệt kê nhỏ, không phải bộ máy thống kê quy mô lớn. Phân tích giả định phép tính nguyên có chi phí bị chặn, việc hash/so sánh ID bị chặn và phân bố hash phù hợp; ID không giới hạn độ dài sẽ thêm chi phí xử lý riêng.

Các phép kiểm tra bao phủ bảng cố định, mọi bảng nhỏ đã nêu và trường hợp biên được chọn; chưa chứng minh mọi input, mọi thiết kế hoặc mô hình production. Chứng minh kỳ vọng ở phần nền tảng cho lập luận tổng quát theo giả định. Nếu chưa chạy được, đối chiếu sáu dòng demo bằng tay, đọc oracle độc lập, tìm nhánh sửa dấu và diễn giải CSV ở phần sau. Thiếu SDK: cài đúng phiên bản hoặc dùng lối chỉ đọc; lỗi lock file: giữ nguyên file đã cho. Không nâng dependency hay bỏ pin để gọi là cùng thí nghiệm. LICENSE/README trong ZIP là tài liệu bổ sung; code cần chạy đã đầy đủ ở đây.

</details>


### Kiểm định từ kết quả quan sát với giả thuyết không tác động từng đơn vị

Nếu mọi đơn vị cho đúng cùng một kết quả dưới hai hành động, đổi nhãn nhánh giữ nguyên kết quả đã quan sát của nó. **Giả thuyết không tác động từng đơn vị**, gọi là sharp null, là `Y_i(1)=Y_i(0)` với mọi i. Nó mạnh hơn tác động trung bình bằng không, vốn cho phép tác động dương và âm triệt tiêu. Với thiết kế độc lập, xác suất bằng nhau ở từng cặp và sharp null, mọi `2^B` cách đổi nhãn trong cặp có xác suất bằng nhau.

Giữ các chênh lệch cặp quan sát cố định. Với mỗi mẫu đổi dấu, cộng lại các chênh lệch đã đổi dấu. Đếm mẫu có trị tuyệt đối tổng ít nhất bằng trị tuyệt đối tổng đã quan sát, tính cả trường hợp bằng nhau. Chia số đếm cho `2^B` để được p-value hai phía. Mọi mẫu đều chia cùng B nên so trực tiếp tổng nguyên. Không có xấp xỉ Monte Carlo hay hiệu chỉnh +1 vì đã liệt kê mọi cách gán, gồm cách quan sát.

Với một cặp quan sát 6 và 14, phân phối chênh lệch theo null là {-8,+8}; cả hai đều ít nhất cực đoan như -8 nên p=1. Sáu cặp có bước p-value là bội của 1/64. Giải thích vì sao p=54/64 ở demo chưa cho thấy treatment vô hiệu và không phải xác suất null đúng.

<details>
<summary>Đáp án</summary>

Kiểm định đếm mức thường gặp của chênh lệch có trị tuyệt đối ít nhất như quan sát dưới phân phối gán khi null đúng. Ở bảng này 54/64 lượt đổi dấu thỏa điều kiện. Đây là xác suất đuôi dưới sharp null và giả định gán, không phải `P(null | data)`. Không bác bỏ chưa xác minh không tác động: mô phỏng có tác động -4, chỉ sáu cặp và biến thiên do gán rộng. Giả thuyết tác động trung bình bằng không khác với sharp null. SD mô hình 6,3596 dùng kết quả tiềm năng thật trên các cách gán khác; p-value giữ kết quả quan sát cố định dưới mô hình giả định không tác động. Chúng trả lời câu hỏi khác nhau.

</details>


Kiểm định cần xác suất gán thực tế, không ảnh hưởng chéo và kết quả đầy đủ theo quy tắc đã định. Nếu gán theo outcome, thiếu kết quả hoặc xem nhiều lần để dừng, các lượt đổi dấu không biện minh cùng phân phối tham chiếu. p-value cũng không phải khoảng cho tau hay SD trên các cách gán dưới tác động thật. Hôm nay ta chưa xây dựng khoảng đó.

Sửa lỗi sau trong bản sao lab riêng: luôn tính `LeftOutcome - RightOutcome`, bỏ qua bên nào nhận treatment. Giải thích kiểm tra đầu tiên cần thất bại và cách sửa đúng. Chạy lại `--check` sau khi sửa.

<details>
<summary>Đáp án</summary>

Phép so với quét hai nhánh độc lập chạy trước kiểm tra bảng và phát hiện phân phối bị đổi. Cặp có treatment bên phải phải tính phải trừ trái, nên sửa bằng nhánh điều kiện trong `Differences`. Bảng đúng cho [-8,4,-16,12,-24,20], thay vì trái trừ phải ở mọi cặp. Đổi tên trái/phải mà giữ cách gán/kết quả phải giữ nguyên ước lượng; kiểm tra đổi nhãn cũng bảo vệ ý nghĩa này. Dùng trị tuyệt đối không sửa được lỗi vì sẽ bỏ mất hướng cải thiện hay làm xấu metric.

</details>


Nghỉ - 10 phút, rời màn hình.

## 6. Đổi một lựa chọn thiết kế mỗi lần

**Thí nghiệm có kiểm soát · 45 phút.** Ghi dự đoán, chạy liệt kê đầy đủ cách gán và diễn giải CSV. **Hoàn thành khi:** tách sai lệch do chính sách, độ phân tán theo thiết kế và một chênh lệch ví dụ mà không gọi số giả lập là timing production.

### Quy trình trước khi xem kết quả

**Giả định:** mười hai đơn vị cố định, không ảnh hưởng chéo, kết quả đầy đủ, đúng hai hành động và các kết quả tiềm năng đã liệt kê. Thiết kế toán học random-pair cho mỗi cách trong 64 cách gán xác suất 1/64. Code liệt kê thiết kế này; mask 21 là ví dụ cố định, không phải phân nhóm production ngẫu nhiên.

**Biến giữ cố định:** giữ cùng mười hai ID và kết quả tiềm năng trong mỗi phép so. Trước hết so phân nhóm ngẫu nhiên với luôn chọn đơn vị có baseline thấp hơn, giữ cách ghép gần nhau. Tiếp theo chỉ đổi ghép cặp: ghép gần dùng các baseline liền nhau sau sắp xếp; ghép xa nối sáu đơn vị đầu với sáu đơn vị cuối. Giữ quy tắc một treatment/một control. Chạy mỗi thiết kế dưới bảng không tác động và bảng tác động hằng -4 thành hai kịch bản mô hình riêng.

**Dự đoán:** luôn chọn đơn vị nhẹ tạo chênh lệch âm dù không có tác động. Trung bình random-pair bằng oracle với cả hai cách ghép. Ghép gần giảm SD do gán với các kết quả tiềm năng cố định này. Một chênh lệch ví dụ có thể sai dấu. Ghép tốt chưa bảo đảm phổ quát khi outcome/tác động khác.

Chạy `dotnet run --no-restore -c Release --project LessonLab -- --experiment` từ `dotnet`. Giải thích các dòng nào tách chính sách, các dòng nào tách ghép cặp và ý nghĩa `NA`. Kiểm tra `assignments.csv` có 256 dòng dữ liệu, bốn nhóm mỗi nhóm đủ 64 mask và trung bình đồng trọng số từng nhóm khớp oracle.

<details>
<summary>Đáp án - kết quả và giới hạn thí nghiệm</summary>

**Quan sát đã chạy:** output sau được tạo từ đúng chương trình trên. `estimate` là mask 21 với random-pair, mask 63 với select-low. `design_mean`, `design_sd`, `min`, `max` là các đại lượng đồng trọng số trên đủ 64 cách gán, không phải số đo wall-clock hay khoảng tin cậy. `sharp_null_p` dùng kết quả quan sát của mask 21 dưới sharp null, không dùng bảng kết quả tiềm năng thật.

```text
effect,pairing,policy,estimate,design_mean,design_sd,min,max,sharp_null_p
0,close,random-pair,2.0000,0.0000,6.3596,-14.0000,14.0000,0.8438
0,close,select-low,-14.0000,NA,NA,NA,NA,NA
0,poor,random-pair,6.0000,0.0000,28.8637,-69.3333,69.3333,0.8125
0,poor,select-low,-69.3333,NA,NA,NA,NA,NA
-4,close,random-pair,-2.0000,-4.0000,6.3596,-18.0000,10.0000,0.8438
-4,close,select-low,-18.0000,NA,NA,NA,NA,NA
-4,poor,random-pair,2.0000,-4.0000,28.8637,-73.3333,65.3333,0.9062
-4,poor,select-low,-73.3333,NA,NA,NA,NA,NA
# 64 equally weighted assignments per random-pair case; wrote assignments.csv; synthetic milliseconds, not measured latency
```

[Dữ liệu CSV tái lập](../../../labs/experimental-design/assignments.csv). Thư mục chạy cũng tạo file này. Mỗi nhóm `(effect,pairing)` có mask 0-63; cột estimate là treatment trừ control ở đơn vị mili giây giả lập. Cộng 64 estimate rồi chia 64 cho trung bình; lấy căn trung bình bình phương độ lệch cho SD, không chia 63 vì đây là toàn bộ phân phối thiết kế, không phải mẫu 64 lượt rút.

So close/random-pair với close/select-low giữ cặp và bảng outcome, chỉ đổi chính sách; select-low báo `NA` vì không có phân nhóm đồng xác suất để áp phân phối tham chiếu/p-value đó. So close/random-pair với poor/random-pair giữ đơn vị và effect, chỉ đổi cặp. SD tăng từ 6,3596 lên 28,8637, còn trung bình vẫn khớp effect. Với effect=-4, mask 21 ghép xa cho +2 dù tác động thật âm. Dấu một ví dụ chưa xác minh dấu tác động; với effect=0, select-low ghép gần cho -14 là sai lệch chọn đơn vị. Thay effect 0 bằng -4 giữ cùng thiết kế và dịch trung bình -4.

**Suy luận:** thiết kế đúng bảo vệ kỳ vọng; ghép cặp tốt theo thông tin trước treatment giảm phương sai ở dữ liệu này. Liệt kê chính xác bốn nhóm hỗ trợ nhận định hữu hạn đó, chưa chứng minh matching luôn tốt hay implementation production giảm 4 ms.

</details>


### Giới hạn và phép phân tích cần bác bỏ

Dữ liệu được tạo sẵn, không phải thời gian request đã đo. Liệt kê toàn bộ loại bỏ sai số Monte Carlo cho các thiết kế nhỏ này; chưa loại sai mô hình. Chỉ xét 12 đơn vị, hai kịch bản tác động và hai cách ghép. Chưa thử chất lượng RNG, ảnh hưởng mạng, thuật toán ghép thực, dừng lặp, telemetry thiếu, tính đại diện production hoặc ảnh hưởng chéo do tài nguyên chung. Ta chưa chạy SDK GrowthBook hay integration SQL Server/dashboard.

Giả sử ai đó gọi `SharpNull` cho kịch bản không tác động `select-low` tất định rồi báo p=2/64 để chứng minh implementation mới có tác dụng. Sai ở đâu, và kiểm tra lab xét lỗi loại I dưới thiết kế ngẫu nhiên thực như thế nào?

<details>
<summary>Đáp án</summary>

Chính sách tất định thực gán xác suất 1 cho mask mọi đơn vị trái nhận treatment, không phải 1/64 cho từng mask. Khi không tác động nó luôn chọn kết quả thấp hơn, nên chênh lệch -14 là do chọn đơn vị, không do treatment. Áp phân phối cặp đồng xác suất vào đó là dựng một quy trình ngẫu nhiên chưa diễn ra. Thí nghiệm báo `NA` cho p-value thiếu cơ sở đó là đúng. Với thiết kế null thực sự chọn hai bên đồng xác suất, xét hết mask, dựng dữ liệu quan sát từng mask rồi tính p kể cả trường hợp bằng nhau; đúng hai cách có p<=0,05. Xác suất bác bỏ là 2/64=0,03125. Điều này chỉ kiểm tra mức lỗi cho dữ liệu cố định, chưa chứng minh chính sách tất định hợp lệ.

</details>


Lỗi loại I là bác bỏ null khi null đúng. Xác suất lỗi được xét trên thiết kế gán thực khi null đúng. Tính rời rạc và các giá trị bằng nhau có thể làm mức lỗi thấp hơn danh nghĩa; kiểm tra thiết kế hữu hạn đã chạy chưa chứng minh mức lỗi phổ quát cho mọi dữ liệu/cách gán.

Nghỉ - 10 phút, rời màn hình.

## 7. Đổi ngữ cảnh từ latency sang đóng gói

**Vận dụng · 35 phút.** Xác định đơn vị gán, chạy ví dụ kết quả nhị phân và tách chênh lệch tỷ lệ khỏi mili giây. **Hoàn thành khi:** nêu đúng đích là tám đơn vị đóng gói cố định và điều cản suy rộng tới mọi kho.

Kho hàng so hai quy trình đóng gói. Bốn cặp ghép trước treatment gồm tám đơn vị gán; bốn phép chọn theo cặp độc lập, còn hai cách gán trong một cặp bổ sung nhau. Kết quả bằng 1 nếu hư hại, 0 nếu không, trong cửa sổ theo dõi cố định. Kết quả tiềm năng giả lập `(Y0,Y1)` là a=(0,0), b=(1,0), c=(1,0), d=(1,1), e=(0,0), f=(0,1), g=(1,0), h=(0,0). Ghép (a,b),(c,d),(e,f),(g,h), rồi xét mask 5. Xác định tác động đích, tính chênh lệch quan sát, p của sharp null và đối chiếu độc lập trung bình thiết kế. Dùng bản sao lab riêng, chỉ thay `Program.cs`, giữ các file khác.

<details>
<summary>Đáp án - ngữ cảnh đóng gói và chương trình đầy đủ</summary>

Đích là trung bình tác động trên tám đơn vị cố định: tổng tác động -2 chia 8 bằng -0,25, tức giảm 25 điểm phần trăm tỷ lệ hư hại của nhóm giả lập nếu mọi đơn vị đổi hành động. Mask 5 có chênh lệch cặp [-1,0,0,-1], cho D=-0,5; đây là giảm quan sát 50 điểm phần trăm, không phải 0,5 ms. Hai chênh lệch khác 0 tạo bốn tổ hợp dấu; hai tổ hợp cùng dấu đạt trị tuyệt đối 2, nên p=8/16=0,5 khi tính các dấu của hai cặp bằng không.

Thay `Program.cs` bằng toàn bộ code sau, restore/chạy cùng lệnh của lab:
```csharp
using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
Pair[] pairs = [
    new(new Unit("a", 0, 0), new Unit("b", 1, 0)),
    new(new Unit("c", 1, 0), new Unit("d", 1, 1)),
    new(new Unit("e", 0, 0), new Unit("f", 0, 1)),
    new(new Unit("g", 1, 0), new Unit("h", 0, 0))
];
var seen = Design.Observe(pairs, 5);
var tail = Design.SharpNull(seen);
// Independent expectation: directly sum all eight unit effects.
double direct = pairs.SelectMany(p => new[] { p.Left, p.Right })
    .Sum(u => (double)u.Y1 - u.Y0) / 8;
if (Design.Estimate(seen) != -0.5 || direct != -0.25 || tail.P != 0.5 ||
    Design.Distribution(pairs).Average() != direct)
    throw new Exception("Packing result differs.");
Console.WriteLine($"observed={Design.Estimate(seen):F4}; cohort_effect={direct:F4}; sharp_null={tail.Extreme}/{tail.Total}={tail.P:F4}");
```

Kết quả dự kiến đã chạy lại:

```text
observed=-0.5000; cohort_effect=-0.2500; sharp_null=8/16=0.5000
```

Tổng trực tiếp tác động là phép đối chiếu độc lập cho trung bình liệt kê. Một đơn vị có tác động +1, nên tau không bằng không ở đây nhưng tác động riêng không đồng nhất. Chỉ kiểm định sharp null từng đơn vị đã cài đặt; không thay nó bằng kiểm định tác động trung bình không. Mô hình này không xác minh quy trình đóng gói thật, không đảm bảo mọi kho hay mọi ngày.

</details>


Giờ mỗi đơn vị đóng gói là batch mười package. Cả mười kết quả trong batch liên kết và quy trình được gán theo batch. Có thể coi là 80 lần gán độc lập không, và điều gì đổi nếu batch hư hại ở một nhánh mất record?

<details>
<summary>Đáp án</summary>

Có tám đơn vị batch được gán, không phải tám mươi lần phân nhóm độc lập. Batch cùng kích thước và một kết quả tổng hợp được định nghĩa rõ có thể giữ đích dễ diễn giải; tác động có trọng số package khi kích thước khác cần xác định đích và trọng số. Kết quả thiếu liên quan hư hại và nhánh có thể chọn lệch phép so dù phân nhóm ban đầu đúng. Đếm cách gán và kết quả thiếu theo nhánh, tìm nguyên nhân, áp chính sách định trước/phân tích độ nhạy. Tự bỏ batch hư hại không phải cách sửa hợp lệ. Kiểm định với kết quả đầy đủ chưa bảo đảm cho cơ chế dữ liệu thiếu đó.

</details>


## 8. Viết nhận định chịu được các giả định

**Tổng hợp · 45 phút.** Viết đề xuất thí nghiệm ngắn và đoạn kết quả có giới hạn theo mẫu lời giải. **Hoàn thành khi:** cả hai tách đích, phân nhóm, quan sát, độ bất định và phạm vi chưa xác minh. Không cần nộp bài; lời giải luôn mở được.

Viết đề xuất 150-200 từ cho phép so service .NET: nhóm đích/đơn vị, phiên bản chốt, ghép cặp/điều kiện hợp lệ có trước treatment, xác suất gán, metric/cửa sổ chính, quy tắc dừng, xử lý dữ liệu thiếu và kiểm tra ảnh hưởng chéo. Vì sao rollout 50/50 dựa trên hash có thể cần phân tích khác với lab gán đúng một đơn vị mỗi cặp?

<details>
<summary>Đáp án</summary>

Thí điểm giả lập nhắm tới tenant hợp lệ đã ghi danh trước khi bắt đầu, không phải mọi traffic tương lai. Chốt hai phiên bản cùng cửa sổ bảy ngày. Ghép cặp bằng lượng request và vùng đã đo trước treatment. Trong mỗi cặp, chọn độc lập một tenant nhận treatment với xác suất một nửa; ghi phiên bản experiment và nhánh một lần cho mỗi tenant. Metric chính là trung bình tỷ lệ request lỗi theo tenant. Dừng khi hết cửa sổ, không dừng vì p-value thuận lợi. Giữ mọi tenant đã gán, báo telemetry thiếu theo nhánh và tìm nguyên nhân; không âm thầm bỏ tenant thiếu kết quả. Nếu không phục hồi được, báo phép so chưa đầy đủ và phân tích độ nhạy đã định trước. Kiểm tra tài nguyên giới hạn dùng chung; tách tài nguyên hoặc đổi thiết kế khi có ảnh hưởng chéo. Đối chiếu phiên bản thực, danh tính, exposure và phép nối kết quả trước khi kết luận tác động của gán nhánh. Đích chỉ là nhóm đã ghi danh; suy rộng cần thêm bằng chứng.

Rollout dựa trên hash có thể gán không, một hoặc hai tenant treatment trong mỗi cặp đã chọn. Không gian/xác suất gán khác; kiểm định đổi dấu một-mỗi-cặp chưa tự động hợp lệ. Cấu hình 50/50 cũng chưa bảo đảm số đếm thực bằng nhau.

</details>


Viết đoạn kết quả cho tác động hằng -4 với ghép gần. Tách giả định, dự đoán, quan sát và suy luận. Nêu cả SD mô hình và kết quả sharp null với cách diễn giải khác nhau.

<details>
<summary>Đáp án</summary>

Giả định mười hai đơn vị giả lập cố định, kết quả đầy đủ, không ảnh hưởng chéo và gán độc lập đồng xác suất trong sáu cặp ghép gần. Ta dự đoán trung bình chênh lệch theo cách gán bằng -4. Liệt kê cho trung bình -4,0000, SD 6,3596 và khoảng giá trị [-18,10]. Mask 21 chọn sẵn cho -2,0000; kiểm định sharp null từ kết quả quan sát cho 54/64=0,84375. Ước lượng hướng tới tác động nhóm theo kỳ vọng; một cách gán chưa khôi phục đúng nó. SD mô tả độ phân tán do gán khi biết kết quả tiềm năng, không phải khoảng production. p-value chưa cho cơ sở bác bỏ sharp null tại 0,05 trong ví dụ này, nhưng chưa xác minh không tác động. Kết quả thuộc bốn kịch bản giả lập đã liệt kê, chưa nói về latency production, nhóm tương lai, bộ máy thống kê GrowthBook hay SQL Server.

</details>


Kết thúc bằng một câu hỏi tiếp theo giúp phép so thực có cơ sở hơn. Nêu kiểm tra đầu tiên khả thi và điều nó còn chưa giải quyết.

<details>
<summary>Đáp án</summary>

Hỏi liệu treatment có đổi queue mà tenant control cùng dùng không. Trước hết kiểm tra tài nguyên chung và ghi tải queue cùng nhánh/phiên bản/thời gian trong sandbox với workload cố định. Nếu hai nhánh cùng tác động queue, mô hình đơn vị độc lập không phù hợp; tách tài nguyên hoặc thiết kế gán theo cụm/block thời gian trước khi phân tích. Kiểm tra này có thể tìm cơ chế ảnh hưởng chéo, chưa xác minh mọi kiểu traffic production, tính ổn định dài hạn hay thiết kế thay thế nếu thiếu kiểm tra thêm. Không biến tau biết sẵn ở oracle giả lập thành kết luận về hệ thống đã deploy.

</details>

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 07 - Độ bất định khi lấy mẫu: nhiều record chưa chắc có thêm bằng chứng](../2026-10-11-sampling-uncertainty/lesson.md) - Dùng lại kỳ vọng, phương sai và phân biệt dòng dữ liệu với đơn vị độc lập.
- [Bài 05 - Index và query plan: vì sao seek vẫn có thể tốn nhiều công](../2026-10-09-index-query-plans/lesson.md) - Query/thứ tự đúng chưa xác minh hai nhóm so sánh tương đồng.
- [Bài 01 - Big-O và cấu trúc dữ liệu: dedupe mã đơn hàng bằng C#](../2026-10-05-cost-model/lesson.md) - Ôn workload và giới hạn mô hình của benchmark.
- [Hướng dẫn lab C#](../../../labs/experimental-design/dotnet/README.vi.md) - Môi trường cố định, liệt kê cách gán và giới hạn suy luận.

---

[← Bài trước: Bài 07 - Độ bất định khi lấy mẫu: nhiều record chưa chắc có thêm bằng chứng](../2026-10-11-sampling-uncertainty/lesson.md) · [Danh sách bài học](../../README.md)
<!-- LESSON_NAVIGATION_END -->
