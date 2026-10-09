# Bài 07 - Độ bất định khi lấy mẫu: nhiều record chưa chắc có thêm bằng chứng

[English](../../../lessons/2026-10-11-sampling-uncertainty/lesson.md) · [Tải lab C#](https://nguyenan97.github.io/computer-science-learning-agent/labs/sampling-uncertainty/dotnet-lab.zip)

Dịch vụ .NET ghi nhận hai request lỗi trong hai mươi request. Báo 10% là đếm đúng, nhưng hai mươi request khác có thể cho tỷ lệ khác. Nếu retry ghi mỗi request gốc mười lần, 200 dòng chưa cung cấp 200 quan sát độc lập. Ta sẽ lượng hóa hai vấn đề trước khi quyết định dashboard được phép kết luận gì.

**Mục tiêu:** suy ra khoảng ước lượng tỷ lệ, kiểm tra implementation độc lập, xét độ bao phủ qua các lần lấy mẫu và tìm phản ví dụ cho giả định độc lập. Planner chọn xác suất, ước lượng và độ bất định theo catalog hiện tại. Bài kế thừa bất biến, đối chiếu độc lập và nhận định có giới hạn; sẽ bổ sung biến ngẫu nhiên, kỳ vọng, phương sai, phân phối lấy mẫu và khoảng tin cậy.

## Khái niệm chính

- **Mẫu và đối tượng cần ước lượng.** Hai mươi request được chọn là bằng chứng về một luồng đã xác định, không phải mọi deployment. Nêu rõ nhóm request và khoảng thời gian trước khi tính.
- **Kết quả nhị phân và độ bất định.** Mã hóa lỗi là 1, không lỗi là 0. Hai số 1 trong hai mươi cho ước lượng 0,10; mẫu mới chưa chắc có cùng số đếm.
- **Tính độc lập.** Hai mươi quyết định mới khác hai mươi bản sao của một quyết định. Request chung hoặc sự cố chung có thể liên kết kết quả, khiến số dòng danh nghĩa phóng đại lượng thông tin.
- **Quy trình lập khoảng tin cậy.** Khoảng thay đổi theo mẫu. Độ bao phủ là tỷ lệ mẫu lặp mà khoảng chứa xác suất thật cố định dưới mô hình, không phải xác suất gán cho tham số cố định sau khi đã thấy một khoảng.
- **Mô phỏng tái lập.** Seed tái tạo quan sát giả lập, giúp kiểm tra thí nghiệm. Nó chưa làm mô hình đại diện cho production.

Có thể chỉ đọc bảng chạy, code đầy đủ và biểu đồ đã quan sát. Giới hạn cài đặt trong 15 phút của phần lab. Mô phỏng dùng dữ liệu giả lập và tạo CSV tại thư mục chạy.

## 1. Ôn lại và câu hỏi mới

**Ôn tập · 20 phút.** Dựng lại các ranh giới planner chọn, rồi tách tính đúng khỏi bằng chứng thống kê. **Hoàn thành khi:** nêu được phép kiểm tra trước xác minh điều gì và mẫu mới làm đổi điều gì.

1. Từ Bài 06: vì sao transaction ghi nguyên tử chưa sửa workflow mất cập nhật do ghi mù?

<details>
<summary>Đáp án</summary>

Lần đọc diễn ra trước, ngoài từng transaction ghi. Cho các lần ghi sau chạy lần lượt chưa làm mới giá trị ứng dụng. Kiểm tra version/tồn hiện tại và commit phần trừ cùng xác nhận; A+S=I là bất biến một mặt hàng.

</details>

2. Từ Bài 04: vì sao DP 0/1 một hàng phải cập nhật ngân sách giảm dần? Cho phản ví dụ.

<details>
<summary>Đáp án</summary>

Ô thấp hơn phải còn mang ý nghĩa prefix trước. Một công việc chi phí 2, giá trị 3, ngân sách 4: duyệt tăng ghi 3 tại 2 rồi dùng lại để ghi 6 tại 4, dù tối ưu 0/1 là 3. Duyệt giảm giữ lớp cũ tại c-chi phí.

</details>


Oracle database xét một lịch đã chọn; chứng minh DP xét ý nghĩa trạng thái. Chúng chưa biến tần suất lỗi trong một mẫu traffic thành tỷ lệ phổ quát. Hôm nay số đếm có thể đúng mà ước lượng vẫn bất định. Retry transaction cũng gợi ra câu hỏi mới: đơn vị quan sát độc lập là gì?

## 2. Từ số đếm tới mô hình lấy mẫu

**Nền tảng · 50 phút.** Chạy năm quan sát và suy ra độ phân tán của tỷ lệ mẫu. **Hoàn thành khi:** nêu đối tượng cần ước lượng, đơn vị độc lập và bất biến trước khi dùng công thức.

### Bắt đầu từ kết quả đã thấy

Năm kết quả request giả lập là 1,0,1,0,0. Giữ n là số quan sát, k là số kết quả 1. Trước mỗi lần thêm, k bằng tổng prefix và 0<=k<=n. Thêm x đổi k thành k+x và n thành n+1, giữ bất biến đó.

Hoàn thành bảng, gồm tỷ lệ và khoảng đang thay đổi. Giá trị cuối 0,40 đã chứng minh mọi block sau có 40% lỗi chưa?

<details>
<summary>Đáp án</summary>

| n | Kết quả mới | k | h=k/n | Khoảng Wilson, làm tròn |
|---|---|---|---|---|
| 1 | 1 | 1 | 1.0000 | [0.2065,1.0000] |
| 2 | 0 | 1 | 0.5000 | [0.0945,0.9055] |
| 3 | 1 | 2 | 0.6667 | [0.2077,0.9385] |
| 4 | 0 | 2 | 0.5000 | [0.1500,0.8500] |
| 5 | 0 | 2 | 0.4000 | [0.1176,0.7693] |

Bất biến số đếm giữ sau mỗi lần thêm. Các khoảng là phép tính Wilson được giải thích dưới đây, chưa chứng minh năm quan sát xác định p. Block mới có thể khác ngay cả khi p cố định; riêng bảng này chưa xác lập tần suất tương lai.

</details>


### Giải thích mô hình xác suất

Biến ngẫu nhiên gán một số cho kết quả chưa biết. Biến Bernoulli X chỉ có 0 và 1, với P(X=1)=p, P(X=0)=1-p. Ở đây 1 nghĩa là lỗi; từ "success" trong thống kê chỉ sự kiện được đếm, không phải request khỏe. Trên production chưa biết p. Simulator đặt p rõ ràng để kiểm tra độ bao phủ.

IID nghĩa là độc lập và cùng phân phối: các kết quả có cùng p, và biết kết quả trước không làm đổi xác suất kết quả sau trong mô hình. Cùng tỷ lệ riêng lẻ chưa suy ra độc lập. Ví dụ bản sao có cùng p ở mỗi dòng nhưng phụ thuộc hoàn toàn trong nhóm. Lấy mẫu không hoàn lại từ tập hữu hạn hay sự cố thay đổi theo thời gian cần mô hình phù hợp; bài dùng lần lấy mẫu IID như giả định khởi đầu có chủ ý.

Kỳ vọng là trung bình có trọng số xác suất trên các mẫu có thể xảy ra. Phương sai là kỳ vọng của bình phương khoảng cách tới trung bình đó; độ lệch chuẩn là căn phương sai. Vì X^2=X, E[X]=p và Var(X)=p(1-p). Đây là đại lượng mô hình, không phải trung bình quan sát của một lần chạy.

Với K=X1+...+Xn và ước lượng h=K/n, tính tuyến tính cho E[h]=p. Hiệp phương sai đo hai kết quả cùng lệch khỏi trung bình thế nào: Cov(Xi,Xj)=E[(Xi-p)(Xj-p)]. Kết quả độc lập có hiệp phương sai không, còn bản sao của cùng kết quả có hiệp phương sai p(1-p). Khi tính phương sai tổng, tính độc lập vì thế loại các số hạng chéo, cho:

```text
Var(h) = p(1-p)/n
SD(h)  = sqrt(p(1-p)/n)
```

Tỷ lệ mẫu là đại lượng ngẫu nhiên trước khi thu dữ liệu; sau đó giá trị đã cố định. Với p=0,20, độ lệch chuẩn mô hình khoảng 0,0894 khi n=20, 0,0447 khi n=80 và 0,0224 khi n=320. Đó là độ phân tán qua mẫu mới, không phải độ lệch chuẩn của một record nhị phân hay thời gian chạy.

Vì sao tăng n bốn lần làm độ lệch chuẩn mô hình giảm một nửa, và lập luận hỏng ở đâu khi các dòng là bản sao?

<details>
<summary>Đáp án</summary>

sqrt(p(1-p)/(4n)) bằng một nửa sqrt(p(1-p)/n). Cần cùng p và đóng góp độc lập. Dòng liên kết giữ các số hạng hiệp phương sai; sao mỗi kết quả bốn lần không đổi trung bình và không giảm một nửa độ phân tán thật.

</details>


### Lập khoảng bằng cách xét các xác suất ứng viên

Với k=2,n=20, h=0,10. Khoảng Wilson dưới đây xấp xỉ [0,0279;0,3010], cho thấy tỷ lệ điểm chưa đủ. Khoảng giữ các xác suất ứng viên p mà độ lệch đã chuẩn hóa chưa quá lớn. Phân phối chuẩn có đường cong xác suất hình chuông; chuẩn tắc có trung bình không và độ lệch chuẩn một. Dùng z=1.959963984540054, ngưỡng chứa 95% ở giữa của phân phối chuẩn tắc; z là hằng số cho sẵn, không phải tỷ lệ suy ra từ mẫu.

Ứng viên được giữ thỏa `n(h-p)^2 <= z^2 p(1-p)`. Điều kiện score dùng phương sai của ứng viên. Chuyển vế cho `(n+z^2)p^2-(2nh+z^2)p+nh^2 <= 0`. Hệ số bậc hai dương nên tập được giữ nằm giữa hai nghiệm. Chia công thức nghiệm cho n thu được:

```text
d = 1 + z^2/n
center = (h + z^2/(2n))/d
radius = z*sqrt(h(1-h)/n + z^2/(4n^2))/d
interval = [center-radius, center+radius]
```

Giới hạn ứng viên trong [0,1]; khi k=0 hoặc k=n, đầu mút tương ứng đúng bằng 0 hoặc 1. Chính h thỏa điều kiện. Lập luận bậc hai chứng minh phép tính trả khoảng nào, chưa chứng minh độ bao phủ mẫu hữu hạn đúng 95%. Diễn giải ngưỡng dựa vào xấp xỉ chuẩn của score nhị thức; số đếm rời rạc ảnh hưởng độ bao phủ.

"Tin cậy 95%" nghĩa là gì ở đây, và chưa xác lập điều gì cho một khoảng đã quan sát?

<details>
<summary>Đáp án</summary>

Trước lấy mẫu, đầu mút ngẫu nhiên còn p cố định. Quy trình danh nghĩa 95% hướng tới khoảng 95% độ bao phủ qua các mẫu mô hình lặp; độ bao phủ hữu hạn của Wilson có thể khác. Sau khi thấy đầu mút, việc p cố định thuộc khoảng đã cố định, nên phép tính tần suất này không gán xác suất hậu nghiệm 0,95 cho nó. Cũng chưa nói về tỷ lệ request nằm trong khoảng hay độ lệch chọn mẫu.

</details>


Nghỉ - 10 phút, rời màn hình.

## 3. Đọc giả định và kiểm tra một khoảng quen thuộc

**Đọc tài liệu · 45 phút.** Lập bảng nhận định/bằng chứng/giới hạn từ các phần được chỉ định. **Hoàn thành khi:** tách công thức đã suy ra, phép xấp xỉ và trường hợp vi phạm mô hình.

Đọc OpenStax [8.3, A Population Proportion](https://openstax.org/books/introductory-statistics-2e/pages/8-3-a-population-proportion), từ mô hình nhị thức tới xấp xỉ chuẩn và biên sai số tỷ lệ; [7.1, Central Limit Theorem](https://openstax.org/books/introductory-statistics-2e/pages/7-1-the-central-limit-theorem-for-sample-means-averages), phần đầu về trung bình mẫu lặp và độ phân tán. Sách trình bày khoảng chuẩn/Wald thông dụng, không phải implementation Wilson của bài. Ta suy ra Wilson ở trên rồi đọc source dưới đây. Xấp xỉ giới hạn trung tâm xét cỡ mẫu độc lập tăng; riêng "n>=30" chưa sửa sự phụ thuộc hay biên của sự kiện hiếm.

### Phản ví dụ khi không thấy sự kiện

Khoảng Wald thay p trong phương sai bằng h và trả `h +/- z*sqrt(h(1-h)/n)`; lab cắt về [0,1]. Tính hai phương pháp khi không thấy lỗi trong hai mươi request và giải thích vấn đề.

<details>
<summary>Đáp án</summary>

Wald cho [0,0], làm phép tính mất toàn bộ độ bất định. Wilson cho [0,0.1611] vì khi k=0 đầu trên bằng z^2/(n+z^2). p thật dương vẫn có thể không quan sát sự kiện: với p=0,02, P(K=0)=0.98^20, khoảng 0,668. Không khoảng nào chứng minh tỷ lệ production bằng không; Wilson vẫn là quy trình xấp xỉ.

</details>


Cắt đầu mút tránh xác suất ngoài [0,1] nhưng chưa khôi phục độ bất định đã mất tại h=0. Mẫu lớn cũng chưa sửa quy tắc chọn loại lỗi có hệ thống. Ví dụ chỉ đọc 500 dòng khỏe và bỏ 50 lỗi cho h=0; nhóm đủ 550 dòng có tỷ lệ 50/550. Khoảng cho phần khỏe được chọn đang trả lời sai đối tượng.

Đọc [API proportion_ci của SciPy 1.16.2](https://docs.scipy.org/doc/scipy-1.16.2/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html), phần tham số/phương pháp/kết quả, và [Details của R binom.test](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/binom.test.html). R nêu bảo đảm độ bao phủ ít nhất mức danh nghĩa của Clopper-Pearson dưới mô hình nhị thức, cùng đánh đổi độ dài. Bảo đảm đó không chuyển sang Wilson, quan sát phụ thuộc hay mẫu lệch. Bài chưa cài đầu mút khoảng exact; "binomial_sum" phía sau tính độ bao phủ của phương pháp đã chọn.

Lập bảng ba dòng cho độ phân tán giảm theo n, mức danh nghĩa 95% của Wilson và cách xem dòng retry là quan sát.

<details>
<summary>Đáp án</summary>

| Nhận định | Bằng chứng | Giới hạn |
|---|---|---|
| Độ phân tán tỷ lệ IID giảm theo 1/sqrt(n) | Suy ra phương sai Bernoulli; phân phối lấy mẫu OpenStax | Hiệp phương sai/p trôi làm đổi mô hình |
| Wilson dùng ngưỡng danh nghĩa 95% | Suy ra score; nhánh phân vị SciPy | Độ bao phủ rời rạc hữu hạn chưa chắc 0,95 |
| Dòng retry có thể đếm thừa bằng chứng | Nhóm cùng request; ca sao nhóm có kiểm soát | Nhóm thật có thể khác kích thước/kết quả; dedupe chưa chứng minh độc lập |

</details>


## 4. Dashboard dự án và API khoảng tin cậy của SciPy

**Đọc mã nguồn · 45 phút.** Theo nhánh chọn phương pháp và xử lý biên tại commit bất biến. **Hoàn thành khi:** gắn nhánh source với quyết định API mà không nhận là đã chạy integration.

### Áp dụng vào báo cáo vận hành .NET

Dịch vụ ASP.NET có thể báo tỷ lệ request gốc lỗi trong khoảng thời gian xác định. Lưu hoặc truy vấn một kết quả đã thống nhất cho mỗi mã request, kèm số đếm và chính sách lấy mẫu, rồi hiện độ bất định cùng tỷ lệ điểm. SQL Server có thể tổng hợp nhóm đã chọn, nhưng COUNT/SUM chưa xác lập độc lập hay tính đại diện. Các instance Azure cùng chịu sự cố; retry, telemetry bị bỏ và hỗn hợp tenant có thể đổi đối tượng cần ước lượng. Bài không chạy integration SQL Server/dashboard.

Nếu báo cáo mô tả toàn bộ nhóm cố định, k/n là tỷ lệ mô tả chính xác của nhóm. Khoảng có ích khi suy luận theo mô hình về quy trình bên dưới hoặc thời kỳ khác. Cần nêu đối tượng đó. Dedupe bỏ dòng lặp, chưa loại sự cố chung hay làm traffic tương lai ổn định.

### Công cụ thống kê làm rõ phương pháp và giới hạn

SciPy cung cấp đối tượng kết quả có tỷ lệ điểm cùng phương pháp lập khoảng được chọn cho số đếm sự kiện nhị phân, như tác dụng bất lợi hay request lỗi. Input là tóm tắt (k,n), không phải lưu mọi quan sát thô. Nếu thiếu khoảng, cùng một tỷ lệ điểm có thể che lượng bằng chứng rất khác nhau. Đọc tag v1.16.2 tại commit **b1296b9b4393e251511fe8fdd3e58c22a1124899**, chỉ file `scipy/stats/_binomtest.py`:

- [BinomTestResult và proportion_ci, dòng 10-114](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/_binomtest.py#L10-L114): giữ k/n và alternative, kiểm tra phương pháp/mức tin cậy, mặc định exact và chuyển nhánh Wilson riêng.
- [Hàm khoảng exact, dòng 117-159](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/_binomtest.py#L117-L159): giải nghiệm số trên đuôi nhị thức, có nhánh k=0/k=n rõ ràng. Ta xét cách chọn và ý nghĩa biên, chưa đọc toàn bộ bộ giải.
- [Hàm Wilson, dòng 162-199](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/_binomtest.py#L162-L199): lấy phân vị chuẩn, dùng tâm/bán kính Wilson khi không hiệu chỉnh, xử lý một phía và biên.

**Xác minh từ source:** sản phẩm có exact, wilson và wilsoncc; exact là mặc định; Wilson hai phía dùng phân vị chuẩn tại 0.5+0.5*confidence_level; biên không sự kiện/toàn sự kiện được xử lý rõ ràng. **Suy luận thiết kế:** hiện phương pháp trong báo cáo .NET giúp caller tránh coi mọi khoảng có cùng bảo đảm. Lab chỉ cài Wilson hai phía không hiệu chỉnh với z cố định, không phải toàn API, tests, p-value hay đầu mút exact của SciPy. Lab đọc nhưng không cài/chạy SciPy.

Chạy theo nhánh source cho k=7,n=50, hai phía 95%, method='wilson', rồi đối chiếu phương pháp mặc định.

<details>
<summary>Đáp án</summary>

Phương pháp chọn Wilson với correction=false. Hai phía 95% dùng phân vị chuẩn 0,975. h=0,14 đi qua nhánh tâm/bán kính, cho xấp xỉ [0.0695,0.2619] trong C# của bài. Không truyền method chọn exact và giải đuôi nhị thức; ví dụ API chính thức cho khoảng [0.05819,0.26740] với số đếm này. Bài đọc ví dụ đó, không chạy SciPy. Khớp đại số chưa phải đối chiếu toàn runtime hay cài ca một phía/có hiệu chỉnh.

</details>


Cần giải thích đánh đổi nào trước khi chọn phép tính Wilson này cho dashboard?

<details>
<summary>Đáp án</summary>

Wilson tránh biên độ rộng không của Wald và tính gọn từ k/n, nhưng độ bao phủ hữu hạn có thể dưới mức danh nghĩa. Khoảng nhị thức exact có đánh đổi độ bao phủ/độ dài khác dưới mô hình. Không phương pháp nào tự sửa mẫu lệch hay phụ thuộc tùy ý. Hiện phương pháp, đơn vị, nhóm và số đếm là đề xuất thiết kế của bài, không phải nhận định từ tài liệu về động cơ mọi người dùng SciPy.

</details>


Ăn trưa và nghỉ - 30 phút.

## 5. Lab C#: ước lượng, kiểm tra và sửa lỗi

**Lab · 75 phút.** Cài khoảng, kiểm tra đầu mút và chạy thí nghiệm giả lập. **Hoàn thành khi:** công thức khớp oracle và giải thích lỗi mà không nhầm tính đúng với độ bao phủ.

Cài bất biến số đếm và công thức Wilson. Xét mọi k của các n nhỏ bằng cách đối chiếu với giải điều kiện score bằng số, rồi chạy các ca lấy mẫu lặp và phụ thuộc. Dùng đáp án đầy đủ nếu cài đặt vượt thời gian đã dành.

<details>
<summary>Đáp án - toàn bộ lab chạy được</summary>

Dùng SDK **10.0.401**, runtime **Microsoft.NETCore.App 10.0.12**, target **net10.0**; tắt roll-forward cho SDK/runtime. Không có NuGet package ngoài, lock file rỗng vẫn được kiểm tra. Runtime đi cùng SDK đã pin. Cần SDK/ref pack sẵn có để restore lần đầu; không cần database server.

Giải nén ZIP hoặc tạo thư mục `dotnet` với đủ file dưới đây. Chạy từ `dotnet`. Các lệnh chỉ ghi `distribution.csv` ở thư mục đang chạy khi chọn experiment; không truy cập database hoặc gọi mạng.

`global.json`:

```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
}
```

`LessonLab/LessonLab.csproj`:

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

`LessonLab/Stats.cs`. Wilson được suy ra từ bất đẳng thức score. Wald được giữ làm phản ví dụ. Tổng nhị thức dùng tử số BigInteger, không mô phỏng; việc xét đầu mút và chuyển tỷ số vẫn dùng double.

```csharp
// Original MIT teaching code, derived from the score inequality, not copied from SciPy.
using System.Numerics;

public readonly record struct Interval(double Low, double High)
{
    public double Width => High - Low;
    public bool Contains(double p) => Low <= p && p <= High;
}

public static class Stats
{
    public const double Z = 1.959963984540054; // Central 95% of a standard normal distribution.
    private static void Validate(int k, int n)
    {
        if (n < 1 || n > 10000 || k < 0 || k > n) throw new ArgumentOutOfRangeException(nameof(n));
    }
    public static Interval Wilson(int k, int n)
    {
        Validate(k, n);
        double h = (double)k / n, z2 = Z * Z, denominator = 1 + z2 / n;
        double center = (h + z2 / (2 * n)) / denominator;
        double radius = Z * Math.Sqrt(h * (1 - h) / n + z2 / (4 * n * n)) / denominator;
        return new Interval(k == 0 ? 0 : center - radius, k == n ? 1 : center + radius);
    }
    public static Interval Wald(int k, int n)
    {
        Validate(k, n);
        double h = (double)k / n, radius = Z * Math.Sqrt(h * (1 - h) / n);
        return new Interval(Math.Max(0, h - radius), Math.Min(1, h + radius));
    }
    public static BigInteger[] BinomialWeights(int n, int a, int b)
    {
        if (n < 1 || n > 320 || a < 0 || a > b || b < 1 || b > 50)
            throw new ArgumentOutOfRangeException(nameof(n));
        var weights = new BigInteger[n + 1]; BigInteger choose = 1;
        for (int k = 0; k <= n; k++)
        {
            weights[k] = choose * BigInteger.Pow(a, k) * BigInteger.Pow(b - a, n - k);
            if (k < n) choose = choose * (n - k) / (k + 1);
        }
        return weights; // Exact numerator; common denominator is b^n.
    }
    public static double Coverage(int n, int a, int b, Func<int, int, Interval> method, int copies = 1)
    {
        if (copies < 1 || (long)n * copies > 10000) throw new ArgumentOutOfRangeException(nameof(copies));
        var weights = BinomialWeights(n, a, b); BigInteger covered = 0;
        double p = (double)a / b;
        for (int k = 0; k <= n; k++)
            if (method(k * copies, n * copies).Contains(p)) covered += weights[k];
        // Exact integer sums; membership uses double. Scale the ratio before conversion,
        // so large denominators never overflow to infinity. Truncation is below 2^-53.
        BigInteger scale = BigInteger.One << 53;
        return (double)(covered * scale / BigInteger.Pow(b, n)) / (double)scale;
    }
}
```

`LessonLab/Draws.cs`. Generator có trạng thái và seed xác định. Lấy dư sau bước loại bỏ phần thừa tránh lệch modulo nếu đầu ra được xem là đều; điều đó chưa chứng minh các lần gọi độc lập. Không dùng generator này cho bảo mật hay làm chuẩn chất lượng RNG.

```csharp
// Small deterministic generator for reproducible teaching, not for security.
public sealed class Draws
{
    private const long Modulus = 2147483647;
    private long state;
    public Draws(int seed)
    {
        if (seed < 1 || seed >= Modulus) throw new ArgumentOutOfRangeException(nameof(seed));
        state = seed;
    }
    public int NextRaw() { state = 48271 * state % Modulus; return (int)state; }
    public int Below(int bound)
    {
        if (bound < 1 || bound > 10000) throw new ArgumentOutOfRangeException(nameof(bound));
        long limit = (Modulus - 1) - (Modulus - 1) % bound;
        long value;
        do { value = NextRaw() - 1L; } while (value >= limit);
        return (int)(value % bound);
    }
    public int Bernoulli(int a, int b)
    {
        if (b < 1 || b > 10000 || a < 0 || a > b) throw new ArgumentOutOfRangeException(nameof(a));
        return Below(b) < a ? 1 : 0;
    }
}
```

`LessonLab/Checks.cs`. Oracle tìm hai nghiệm bằng binary search trên điều kiện score, không dùng công thức đóng Wilson. Liệt kê mọi chuỗi bit nhỏ để đối chiếu trọng số nhị thức độc lập.

```csharp
using System.Numerics;

public static class Checks
{
    private static void Require(bool test, string why) { if (!test) throw new Exception(why); }
    private static void Throws(Action action)
    {
        try { action(); } catch (ArgumentOutOfRangeException) { return; }
        throw new Exception("Expected argument rejection.");
    }
    // Numerical inversion of the acceptance condition, without Wilson's closed formula.
    private static Interval ScoreRoots(int k, int n)
    {
        double h = (double)k / n;
        bool Accepted(double p) => n * (h - p) * (h - p) <= Stats.Z * Stats.Z * p * (1 - p);
        double low = 0, high = 1;
        if (k != 0)
        {
            double left = 0, right = h;
            for (int i = 0; i < 80; i++) { double mid = (left + right) / 2; if (Accepted(mid)) right = mid; else left = mid; }
            low = (left + right) / 2;
        }
        if (k != n)
        {
            double left = h, right = 1;
            for (int i = 0; i < 80; i++) { double mid = (left + right) / 2; if (Accepted(mid)) left = mid; else right = mid; }
            high = (left + right) / 2;
        }
        return new Interval(low, high);
    }
    public static void Run()
    {
        int cases = 0;
        for (int n = 1; n <= 200; n++)
            for (int k = 0; k <= n; k++)
            {
                var actual = Stats.Wilson(k, n); var oracle = ScoreRoots(k, n);
                Require(Math.Abs(actual.Low - oracle.Low) < 2e-12 && Math.Abs(actual.High - oracle.High) < 2e-12, "Score inversion differs.");
                Require(actual.Low >= 0 && actual.High <= 1 && actual.Contains((double)k / n), "Invalid interval.");
                var complement = Stats.Wilson(n - k, n);
                Require(Math.Abs(actual.Low - (1 - complement.High)) < 2e-12, "Complement differs."); cases++;
            }
        var zero = Stats.Wilson(0, 20);
        Require(zero.Low == 0 && Math.Abs(zero.High - 0.1611251580528194) < 1e-12, "Zero-case fixture differs.");
        Require(Stats.Wald(0, 20).Width == 0, "Wald counterexample missing.");
        // Exhaustive binary sequences give a second, independent count of the binomial weights.
        for (int n = 1; n <= 10; n++)
        {
            var counts = new int[n + 1];
            for (uint bits = 0; bits < (1u << n); bits++) counts[BitOperations.PopCount(bits)]++;
            var weights = Stats.BinomialWeights(n, 1, 2);
            for (int k = 0; k <= n; k++) Require(weights[k] == counts[k], "Sequence oracle differs.");
        }
        foreach (int n in new[] { 20, 80, 320 })
        {
            var weights = Stats.BinomialWeights(n, 1, 5);
            Require(weights.Aggregate(BigInteger.Zero, (s, w) => s + w) == BigInteger.Pow(5, n), "Probability mass differs.");
        }
        Require(Stats.BinomialWeights(3, 1, 5).SequenceEqual(new BigInteger[] { 64, 48, 12, 1 }), "Three-draw fixture differs.");
        Require(double.IsFinite(Stats.Coverage(320, 1, 50, Stats.Wilson)), "Large denominator overflowed.");
        Require(Stats.Coverage(20, 0, 5, Stats.Wilson) == 1 && Stats.Coverage(20, 5, 5, Stats.Wilson) == 1, "Degenerate probability differs.");
        var rng = new Draws(1);
        foreach (int value in new[] { 48271, 182605794, 1291394886, 1914720637, 2078669041 })
            Require(rng.NextRaw() == value, "Generator sequence differs.");
        var same = new Draws(101); var again = new Draws(101);
        for (int i = 0; i < 100; i++) Require(same.Bernoulli(1, 5) == again.Bernoulli(1, 5), "Seed not reproducible.");
        Throws(() => Stats.Wilson(0, 0)); Throws(() => Stats.Wilson(21, 20)); Throws(() => Stats.Wilson(-1, 20));
        Throws(() => Stats.Wilson(0, 10001)); Throws(() => new Draws(0)); Throws(() => rng.Below(0));
        Throws(() => rng.Bernoulli(2, 1)); Throws(() => Stats.Coverage(20, 1, 5, Stats.Wilson, 0));
        Console.WriteLine($"PASS: {cases} score inversions; binary-sequence weights; endpoints; seed; validation.");
    }
}
```

`LessonLab/Experiment.cs`. Mỗi repetition sinh 320 quan sát, lấy prefix 20/80/320 từ cùng chuỗi. So Wilson/Wald trên đúng cùng số đếm. Hai ca rare và cluster dùng seed riêng, là phép thử giả định riêng.

```csharp
using System.Globalization;

public static class Experiment
{
    private const int Repetitions = 2000;
    private sealed record Result(string Case, int Units, int Records, int A, int B, string Method,
        int[] Counts, Func<int, int, Interval> Interval, int Copies = 1);
    public static void Run()
    {
        var results = new List<Result>(); var rng = new Draws(101);
        var prefix = new Dictionary<int, int[]> { [20] = new int[Repetitions], [80] = new int[Repetitions], [320] = new int[Repetitions] };
        for (int r = 0; r < Repetitions; r++)
        {
            int successes = 0;
            for (int i = 1; i <= 320; i++) { successes += rng.Bernoulli(1, 5); if (prefix.ContainsKey(i)) prefix[i][r] = successes; }
        }
        foreach (var (n, counts) in prefix)
            foreach (string method in new[] { "Wilson", "Wald" })
                results.Add(new Result("prefix", n, n, 1, 5, method, counts, method == "Wilson" ? Stats.Wilson : Stats.Wald));
        rng = new Draws(202); var rare = new int[Repetitions];
        for (int r = 0; r < Repetitions; r++) for (int i = 0; i < 20; i++) rare[r] += rng.Bernoulli(1, 50);
        results.Add(new Result("rare", 20, 20, 1, 50, "Wilson", rare, Stats.Wilson));
        results.Add(new Result("rare", 20, 20, 1, 50, "Wald", rare, Stats.Wald));
        rng = new Draws(303); var iid = new int[Repetitions]; var groups = new int[Repetitions];
        for (int r = 0; r < Repetitions; r++)
            for (int i = 0; i < 200; i++) { int x = rng.Bernoulli(1, 5); iid[r] += x; if (i < 20) groups[r] += x; }
        results.Add(new Result("iid", 200, 200, 1, 5, "Wilson", iid, Stats.Wilson));
        results.Add(new Result("cluster-naive", 20, 200, 1, 5, "Wilson", groups.Select(k => 10 * k).ToArray(), Stats.Wilson, 10));
        results.Add(new Result("cluster-unit", 20, 200, 1, 5, "Wilson", groups, Stats.Wilson));
        Console.WriteLine("case,units,records,p,method,covered,repetitions,empirical,binomial_sum,mean_width");
        foreach (var row in results)
        {
            int covered = 0; double width = 0, p = (double)row.A / row.B;
            foreach (int k in row.Counts) { var ci = row.Interval(k, row.Units * row.Copies); if (ci.Contains(p)) covered++; width += ci.Width; }
            double exact = Stats.Coverage(row.Units, row.A, row.B, row.Interval, row.Copies);
            Console.WriteLine(FormattableString.Invariant($"{row.Case},{row.Units},{row.Records},{p:F2},{row.Method},{covered},{Repetitions},{(double)covered / Repetitions:F4},{exact:F6},{width / Repetitions:F6}"));
        }
        using var csv = new StreamWriter("distribution.csv", false);
        csv.WriteLine("n,bin_left,bin_right,count,repetitions");
        foreach (var (n, counts) in prefix)
        {
            var bins = new int[20]; foreach (int k in counts) bins[Math.Min(19, k * 20 / n)]++;
            for (int b = 0; b < bins.Length; b++) csv.WriteLine(FormattableString.Invariant($"{n},{b / 20.0:F2},{(b + 1) / 20.0:F2},{bins[b]},{Repetitions}"));
        }
        Console.WriteLine("# wrote distribution.csv; seeds=101/202/303; no elapsed-time benchmark");
    }
}
```

`LessonLab/Program.cs`. Demo cập nhật số đếm sau từng quan sát. Tham số chỉ chọn check hoặc experiment.

```csharp
using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
if (args.Length == 1 && args[0] == "--check") { Checks.Run(); return; }
if (args.Length == 1 && args[0] == "--experiment") { Experiment.Run(); return; }
if (args.Length != 0) throw new ArgumentException("Use no argument, --check or --experiment.");
Console.WriteLine("n,k,estimate,wilson_low,wilson_high");
int count = 0, n = 0;
foreach (int observation in new[] { 1, 0, 1, 0, 0 })
{
    count += observation; n++; var ci = Stats.Wilson(count, n);
    Console.WriteLine($"{n},{count},{(double)count / n:F4},{ci.Low:F4},{ci.High:F4}");
}
```

Demo dự kiến, đã đối chiếu với lần chạy:

```text
n,k,estimate,wilson_low,wilson_high
1,1,1.0000,0.2065,1.0000
2,1,0.5000,0.0945,0.9055
3,2,0.6667,0.2077,0.9385
4,2,0.5000,0.1500,0.8500
5,2,0.4000,0.1176,0.7693
```

Kết quả `--check` dự kiến:

```text
PASS: 20300 score inversions; binary-sequence weights; endpoints; seed; validation.
```

Kiểm tra 20.300 cặp (k,n) với n=1-200, đầu mút, đối xứng, đầu vào sai, tổng xác suất và seed tái lập. Đối chiếu chuỗi bit chỉ bao phủ n=1-10, p=1/2; fixture n=3, p=1/5 và kiểm tra tổng bổ sung cho các mẫu lớn hơn. Nó không chứng minh độ bao phủ 95%, chất lượng RNG hay tính đại diện của dữ liệu thực. Oracle score độc lập về cách tính nhưng dùng cùng điều kiện toán đã chọn.

</details>


Bài sửa lỗi: thay `double h = (double)k / n` bằng phép chia nguyên `double h = k / n` trong Wilson. Dự đoán một ca thất bại rồi sửa.

<details>
<summary>Đáp án</summary>

Tại k=1,n=2, chia nguyên cho h=0 thay vì 0,5. Wilson trả khoảng không sự kiện thay vì [0.0945,0.9055]; oracle nghiệm cũng phát hiện lệch. Ép kiểu trước phép chia. Gán thương đã cắt vào double chưa khôi phục phần lẻ. Giữ phép chia trong oracle là số thực để hai implementation không cùng mắc lỗi đó.

</details>


Nghỉ - 10 phút, rời màn hình.

## 6. Mô phỏng có kiểm soát, độ bao phủ và phân phối nhìn thấy được

**Thí nghiệm · 45 phút.** Dự đoán các phép so, đọc CSV/biểu đồ và giải thích chỗ lệch mô hình. **Hoàn thành khi:** tách mức tin cậy danh nghĩa, độ bao phủ mô hình hữu hạn và quan sát từ một seed.

### Giữ từng phép so có kiểm soát

Giữ p=1/5, 2.000 lần lặp, generator và seed 101. Mỗi lần sinh 320 kết quả rồi lấy prefix 20,80,320. Wilson/Wald nhận đúng cùng k trong mỗi prefix. Tăng độ dài prefix đổi cỡ mẫu; đổi phương pháp là phép so riêng. Ca sự kiện hiếm đổi p thành 1/50 tại n=20, seed 202. Ca phụ thuộc dùng seed 303: 200 kết quả IID so với hai mươi kết quả ẩn, mỗi kết quả được sao mười lần; kết quả ẩn lấy từ cùng lần sinh 200 kết quả. Đây là các thí nghiệm tách biệt có chủ ý, không phải một phép so đổi mọi yếu tố.

Dự đoán hướng thay đổi độ phân tán, độ rộng khoảng và độ bao phủ khi tăng n, xét sự kiện hiếm và sao nhóm.

<details>
<summary>Đáp án</summary>

Prefix độc lập lớn hơn dự kiến thu hẹp khoảng điển hình và gom ước lượng theo thang gần 1/sqrt(n); chưa có định lý độ bao phủ tăng đơn điệu. Wald dự kiến hỏng rõ ở số đếm không của sự kiện hiếm. Sao nhóm khiến khoảng đếm dòng quá hẹp; đếm nhóm khôi phục n phù hợp trong mô hình giả lập. So độ rộng và độ bao phủ riêng: hẹp hơn chưa tự tốt hơn.

</details>


### Tính độ bao phủ mà không lấy mẫu ngẫu nhiên

Với n=3,p=1/5, số sự kiện K có thể là 0,1,2,3. Số chuỗi tương ứng là 1,3,3,1; xác suất chính xác là 64/125,48/125,12/125,1/125. Ví dụ ba vị trí cho một sự kiện cho `3*(1/5)*(4/5)^2`. Tổng quát có C(n,k) chuỗi nhị phân với k sự kiện, nên:

```text
P(K=k) = C(n,k) p^k (1-p)^(n-k)
coverage(n,p) = sum over k with p in interval(k,n) of P(K=k)
```

C(n,k) đếm cách chọn k vị trí có sự kiện. Công thức đếm nguyên trong C# theo `C(n,k+1)=C(n,k)*(n-k)/(k+1)`. Có thể chứng minh công thức bằng cách đếm lựa chọn k vị trí rồi thêm một vị trí có sự kiện theo hai cách: C(n,k)*(n-k)=C(n,k+1)*(k+1). Đây là liệt kê một mô hình, không phải bằng chứng request thật tuân theo mô hình đó.

Giải thích cách tổng này tách dao động Monte Carlo khỏi vấn đề có hệ thống của khoảng.

<details>
<summary>Đáp án</summary>

Tổng hữu hạn không có sai số do lấy mẫu: mỗi k được cân bằng xác suất của mô hình nhị thức đã chọn. Mô phỏng dao động quanh độ bao phủ mô hình nếu các lần sinh gần mô hình đó. Với p=0,02,n=20, tổng Wilson khoảng 0,940101, nên thấy gần 0,94 không chỉ là lỗi simulator. Đầu mút/làm tròn số vẫn còn; liệt kê đúng chưa nói production có phân phối nhị thức hay không.

</details>


### Output giả lập đã quan sát

Chạy `--experiment` và đối chiếu CSV/phân phối với lần chạy giả lập đã ghi nhận.

<details>
<summary>Đáp án - output và phân phối đã quan sát</summary>

Output sau được tạo bằng runtime C# đã pin, không phải thời gian dự kiến tự đặt. `covered` đếm khoảng chứa p đã biết của simulator. `empirical` chia cho 2.000. `binomial_sum` cộng trọng số mô hình hữu hạn bằng đầu mút double của khoảng, không phải phương pháp Clopper-Pearson. `mean_width` là độ rộng trung bình, chưa phải bảo đảm sai số.


```text
case,units,records,p,method,covered,repetitions,empirical,binomial_sum,mean_width
prefix,20,20,0.20,Wilson,1905,2000,0.9525,0.956328,0.326045
prefix,20,20,0.20,Wald,1836,2000,0.9180,0.920843,0.327257
prefix,80,80,0.20,Wilson,1932,2000,0.9660,0.965245,0.171524
prefix,80,80,0.20,Wald,1854,2000,0.9270,0.932055,0.173177
prefix,320,320,0.20,Wilson,1927,2000,0.9635,0.957630,0.087252
prefix,320,320,0.20,Wald,1901,2000,0.9505,0.945410,0.087479
rare,20,20,0.02,Wilson,1863,2000,0.9315,0.940101,0.187112
rare,20,20,0.02,Wald,678,2000,0.3390,0.331792,0.056121
iid,200,200,0.20,Wilson,1919,2000,0.9595,0.958498,0.109939
cluster-naive,20,200,0.20,Wilson,1164,2000,0.5820,0.598123,0.105257
cluster-unit,20,200,0.20,Wilson,1906,2000,0.9530,0.956328,0.324538
# wrote distribution.csv; seeds=101/202/303; no elapsed-time benchmark
```


![Phân phối lấy mẫu n=20,80,320 với xác suất thật p=0,20](../../../lessons/2026-10-11-sampling-uncertainty/sampling-distribution.png)

[Mở biểu đồ ở độ phân giải đầy đủ](../../../lessons/2026-10-11-sampling-uncertainty/sampling-distribution.png).

Biểu đồ được tạo từ [CSV histogram giả lập đã quan sát](../../../labs/sampling-uncertainty/distribution.csv) của lab. Mỗi cột là tỷ lệ trong 2.000 lần lặp rơi vào bin ước lượng rộng 0,05; các panel dùng chung trục. Trục ngang bao phủ toàn khoảng xác suất 0-1 để vẫn thấy các bin hiếm nằm xa. Ước lượng n=20 nằm trên lưới 0,05; chia bin có thể che chi tiết. Tăng n gom ước lượng quanh 0,20, chưa bảo đảm từng mẫu riêng gần p hơn.

Để tự vẽ mà không thêm dependency code, chạy `--experiment`, nhập distribution.csv vào spreadsheet, lọc từng n và vẽ count/repetitions theo bin_left với trục ngang cố định 0-1, cùng thang trục dọc. Bin cuối gồm 1. Biểu đồ tĩnh trên trang là phương án chỉ đọc; không cần cài Python.

</details>

### Chủ động làm hỏng tính độc lập

Với hai mươi biến Bernoulli ẩn Xg độc lập, sao mỗi kết quả mười lần. Trung bình 200 dòng đúng bằng trung bình hai mươi nhóm: `(10*sum Xg)/200=(sum Xg)/20`. Phương sai là p(1-p)/20, không phải p(1-p)/200. Độ lệch chuẩn vì thế lớn gấp sqrt(10) so với mô hình ngây thơ đếm dòng. Trong ca giả lập này, gộp mỗi nhóm thành một kết quả rồi dùng n=20. Nhóm thật có thể khác kích thước và có kết quả hỗn hợp; không áp dụng cách sửa máy móc cho traffic tùy ý.

Vì sao kết quả nhóm đã quan sát bác bỏ nhận định "thêm dòng là thêm bằng chứng"?

<details>
<summary>Đáp án</summary>

Ca IID 200 dòng bao phủ 1.919/2.000; coi dòng sao là n=200 chỉ bao phủ 1.164/2.000 dù độ rộng trung bình còn hơi nhỏ hơn. Dùng hai mươi nhóm độc lập cho 1.906/2.000, độ rộng khoảng 0,3245. Tổng mô hình nhị thức tương ứng khoảng 0,958498;0,598123;0,956328. Vì vậy lỗi đã thấy có giải thích mô hình; cải thiện chưa phải công thức gộp mọi nhóm hay bảo đảm đúng 95%.

</details>


**Giả định:** p cố định, đơn vị lấy mẫu đã xác định, mô hình Bernoulli giả lập, nhóm ẩn độc lập ở ca đã nêu. **Dự đoán:** các phép so ở trên và tổng mô hình hữu hạn. **Quan sát:** số đếm/độ rộng trong CSV xác định và histogram từ ba seed. **Suy luận:** coi dòng liên kết là độc lập có thể phóng đại độ chính xác; công thức qua kiểm tra tính đúng vẫn có thể chưa đạt độ bao phủ danh nghĩa.

Gần độ bao phủ 0,95, nếu 2.000 lần lặp độc lập thật thì độ lệch chuẩn của ước lượng độ bao phủ khoảng sqrt(0.95*0.05/2000)=0,0049. Đây là thang dao động mô hình, không phải dung sai được chứng nhận cho generator xác định. Wilson sự kiện hiếm có độ bao phủ mô hình hữu hạn 0,940101, dưới 0,95. Tăng số lần Monte Carlo sẽ ước lượng độ bao phủ đó chính xác hơn, chưa sửa nó.

Generator cố định là giả ngẫu nhiên; chưa chứng minh các lần gọi IID. Ba seed được chọn chưa xác lập chất lượng RNG. Chưa thử traffic production, mất mẫu, p trôi, nhóm không đều hay lấy mẫu lại theo sự cố. Không đo latency; giới hạn SQLite/SQL Server về hiệu năng và crash ở bài trước vẫn giữ nguyên.

Nghỉ - 10 phút, rời màn hình.

## 7. Vận dụng: kiểm tra batch thay cho request

**Vận dụng · 35 phút.** Đổi đơn vị quan sát và nêu đối tượng cần ước lượng. **Hoàn thành khi:** kết quả dùng batch độc lập thay vì dòng package lặp và ghi rõ phạm vi.

Mô phỏng kiểm tra chất lượng chọn hai mươi batch độc lập, cùng kích thước. Trong một batch, cả mười package có cùng trạng thái lỗi. Hai batch lỗi tạo hai mươi dòng package lỗi trên 200. Ước lượng xác suất batch mới được chọn có lỗi, so với khoảng ngây thơ đếm dòng package và viết phép kiểm tra. Batch thật không đều nằm ngoài mô hình này.

<details>
<summary>Đáp án - đơn vị batch và chương trình đầy đủ</summary>

Dùng batch làm đơn vị: h=2/20=0,10, Wilson xấp xỉ [0.0279,0.3010]. Coi dòng độc lập cho khoảng [0.0657,0.1494] nhưng chưa biện minh độ chính xác đó. Trong bản sao lab riêng, thay Program.cs bằng toàn bộ chương trình sau, giữ các file khác và chạy cùng lệnh no-restore:
```csharp
using System.Globalization;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
var batches = Stats.Wilson(2, 20);
var rows = Stats.Wilson(20, 200);
if (batches.Width <= rows.Width || Math.Abs(batches.Low - 0.0278664812137682) > 1e-12)
    throw new Exception("Batch-unit result differs.");
Console.WriteLine($"batch estimate=0.1000; interval=[{batches.Low:F4},{batches.High:F4}]");
Console.WriteLine($"naive rows interval=[{rows.Low:F4},{rows.High:F4}]");
```
Kết quả dự kiến:

```text
batch estimate=0.1000; interval=[0.0279,0.3010]
naive rows interval=[0.0657,0.1494]
```
Đối tượng là batch mới cùng kích thước dưới mô hình batch độc lập. Giả định cùng kích thước/cùng trạng thái trong batch cũng làm tỷ lệ batch và package bằng nhau ở đây; tỷ lệ package có trọng số tổng quát cần lập luận khác. Đây là phạm vi giả lập, chưa phải kế hoạch lấy mẫu sản xuất đã xác minh.

</details>


## 8. Tổng hợp và tự kiểm tra

**Tổng hợp · 45 phút.** Viết lại nhận định dashboard cùng đối tượng, bằng chứng và phép thử có thể bác bỏ. **Hoàn thành khi:** tách tính đúng của mẫu, độ bao phủ của khoảng và tính đại diện.

1. Vì sao k/n tính đúng vẫn có thể hỗ trợ suy luận sai?

<details>
<summary>Đáp án</summary>

k/n có thể mô tả đúng nhóm được chọn nhưng không đại diện quy trình cần xét: chỉ lấy phần khỏe, dòng lặp hoặc tỷ lệ thay đổi đều làm đổi suy luận. Đối chiếu số đếm bằng tổng hợp độc lập, rồi xét chọn mẫu/phụ thuộc riêng. Khoảng hẹp chưa chứng nhận các giả định.

</details>

2. Tin cậy 95% có gán xác suất 0,95 cho p chưa biết cố định nằm trong khoảng Wilson cụ thể đã quan sát không?

<details>
<summary>Đáp án</summary>

Không. Sự kiện qua lấy mẫu lặp là khoảng ngẫu nhiên có chứa p cố định không. Khoảng đã quan sát và p nay đều cố định; mức tin cậy danh nghĩa không gán xác suất hậu nghiệm cho p. Độ bao phủ hữu hạn Wilson cũng chưa chắc bằng 0,95. Muốn gán xác suất cho tham số sau khi thấy dữ liệu phải đặt mô hình xác suất cho chính tham số; bài chưa đặt mô hình đó.

</details>

3. Tăng n khác tăng số lần mô phỏng thế nào?

<details>
<summary>Đáp án</summary>

n đếm đơn vị dùng trong mỗi ước lượng và đổi độ phân tán lấy mẫu. Số lần lặp đếm số ước lượng simulator khảo sát và làm phép đo độ bao phủ rõ hơn. Tăng lần lặp chưa sửa khoảng đặt sai mô hình, phụ thuộc hay lệch chọn mẫu; thêm record phụ thuộc chưa chắc tăng n hiệu dụng.

</details>

4. Bằng chứng nào có thể bác bỏ việc dùng khoảng này cho dashboard .NET?

<details>
<summary>Đáp án</summary>

Kiểm tra danh tính request gốc, telemetry mất và các nhóm thời gian/tenant; xét sự cố hay request có liên kết kết quả không. Tỷ lệ trôi hoặc lỗi theo nhóm bác bỏ diễn giải IID đơn giản dù tổng hợp hoàn toàn đúng. Xác minh query/engine đích và mô hình nhóm phù hợp trước khi chọn khoảng production. Lab chưa thử integration SQL Server hay phương pháp nhóm tổng quát.

</details>


## Nguồn và quyền sử dụng

- OpenStax Introductory Statistics 2e, [8.3](https://openstax.org/books/introductory-statistics-2e/pages/8-3-a-population-proportion) và phần đầu [7.1](https://openstax.org/books/introductory-statistics-2e/pages/7-1-the-central-limit-theorem-for-sample-means-averages), hỗ trợ tỷ lệ nhị thức và biến thiên lấy mẫu. Phép suy ra Wilson của bài tách khỏi công thức Wald trong sách.
- [Tài liệu proportion_ci của SciPy](https://docs.scipy.org/doc/scipy-1.16.2/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html) cùng source cố định ở phần 4 hỗ trợ phương pháp API, nhánh chọn và biên. Chỉ đọc các phần đó; bộ giải phân vị, toàn bộ tests và runtime SciPy chưa được xác minh bởi lab C#. [Giấy phép BSD](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/LICENSE.txt).
- [Details của R binom.test](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/binom.test.html) giải thích khác biệt độ bao phủ/độ dài của Clopper-Pearson. Không chạy implementation R. SciPy dẫn paper Wilson, Clopper-Pearson và Newcombe; bài chưa đọc toàn văn và không khẳng định kết quả thực nghiệm riêng của các paper đó.
- Nội dung và biểu đồ tự tạo: CC BY 4.0. C# giảng dạy tự viết: MIT, có trong ZIP. Văn bản/source SciPy, OpenStax và R được dẫn và phân tích, không sao chép hay cấp lại giấy phép.

<!-- LESSON_NAVIGATION_START -->
## Nội dung liên quan

- [Bài 06 - Transaction và phục hồi](../2026-10-10-transactions-recovery/lesson.md) - Tách ca kiểm tra có kiểm soát khỏi nhận định chung; xác định danh tính request.
- [Bài 04 - Quy hoạch động và xấp xỉ](../2026-10-08-dp-approximation/lesson.md) - Ôn ý nghĩa trạng thái và lý do chọn chiều cập nhật.
- [Hướng dẫn lab C#](../../../labs/sampling-uncertainty/dotnet/README.vi.md) - SDK/runtime cố định, số đếm mô phỏng và giới hạn diễn giải.

---

[← Bài trước: Bài 06 - Transaction và phục hồi: ghi đúng vẫn có thể dùng quyết định đã cũ](../2026-10-10-transactions-recovery/lesson.md) · [Danh sách bài học](../../README.md) · [Bài sau: Bài 08 - Thiết kế thí nghiệm: chênh lệch chưa đủ để kết luận nhân quả →](../2026-10-12-experimental-design/lesson.md)
<!-- LESSON_NAVIGATION_END -->
