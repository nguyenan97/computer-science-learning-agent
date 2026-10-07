# Lab Bài 02 - Tìm biên bằng C#

[English](README.md) · [Bài tiếng Việt](../../../vi/lessons/boundary-search/lesson.md)

Lab console này tìm vị trí đầu tiên có giá trị lớn hơn hoặc bằng target, rồi đếm
các timestamp trong khoảng `[start,end)`. Input được sắp xếp tăng dần. Code nằm ở
[LessonLab/BoundarySearch.cs](LessonLab/BoundarySearch.cs); test nằm ở
[LessonLab/Checks.cs](LessonLab/Checks.cs). Bạn có thể tự viết lại trong bản sao
để thực hành, rồi đối chiếu code và lập luận với lời giải.

## Chạy

Cài .NET SDK **10.0.401** (target **net10.0**), mở terminal trong thư mục
`dotnet` này, nơi có `global.json`. Lab không cần package bên thứ ba,
package benchmark, Python hay SQL Server.

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --observe
```

Với bản clone, chạy trong thư mục `labs/boundary-search/dotnet`. Với
[lab ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/boundary-search/dotnet-lab.zip),
giải nén và tìm thư mục có `global.json` trước khi chạy các lệnh trên.
Lệnh mặc định in:

```text
Array.BinarySearch(30) found a match: True
LowerBound(30): 3
List.BinarySearch(11): -3; insertion position: 2
Count [10, 30): 3
Count [30, 30): 0
Count [11, 39): 3
```

`--check` in **17/17 checks passed** và trả mã thoát 0 khi mọi kiểm tra thành công;
nếu có kiểm tra thất bại, mã thoát là 1. Các trường hợp gồm input rỗng, duplicate
đầu tiên, target không có trong input, khoảng nằm ngoài dữ liệu, key âm và các giá
trị giới hạn, cách xử lý hai đầu khoảng, khoảng bị đảo, giữ nguyên input, input
null, cách .NET mã hóa kết quả âm, mảng ảo rất lớn và dữ liệu nhỏ được đối chiếu
với thuật toán quét. Tìm kiếm trên mảng ảo chỉ đọc O(log n) phần tử, không cần cấp
phát một mảng có `int.MaxValue` phần tử.

## Cách đọc kết quả

`Array.BinarySearch` và `List<T>.BinarySearch` trả về **một** vị trí khớp khi tìm
thấy target, không bảo đảm đó là duplicate đầu tiên. Khi không tìm thấy, kết quả
là bitwise complement của vị trí chèn target để vẫn giữ thứ tự. Giải mã kết quả
âm bằng `~result`, không dùng `-result`. Trong method tự viết, khi giá trị ở `mid`
lớn hơn hoặc bằng target, `hi` được chuyển về `mid` để tiếp tục tìm về bên trái.
Midpoint `lo + (hi - lo) / 2` tránh cộng hai index có thể gây tràn số.

Timestamp có kiểu `long` và được sắp xếp tăng dần. Hai lần tìm kiếm giả định việc
đọc phần tử theo index và so sánh có chi phí hằng số. Kiểm tra thứ tự, sắp xếp và
cập nhật mảng là công việc riêng, chưa được tính vào chi phí tìm kiếm.
Console lab này không thực thi các ví dụ SQL trong bài học.

`--observe` in số lần đọc phần tử khi tìm biên dưới trên input có 8, 1.024 và
65.536 phần tử, rồi tìm event theo timestamp. Kết quả đếm số lần đọc phần tử,
không đo thời gian CPU.
