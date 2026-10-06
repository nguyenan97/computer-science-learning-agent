# Lab Bài 02 - Tìm biên bằng C#

[English](README.md) · [Bài tiếng Việt](../../../vi/lessons/boundary-search/lesson.md)

Console lab độc lập này tìm biên dưới tại duplicate đầu tiên và đếm timestamp số
nguyên đã sorted trong `[start,end)`. Code đầy đủ nằm ở
[LessonLab/BoundarySearch.cs](LessonLab/BoundarySearch.cs); test nằm ở
[LessonLab/Checks.cs](LessonLab/Checks.cs). Tự viết lại trong bản copy để thực hành,
rồi đối chiếu lập luận với lời giải bất cứ khi nào hữu ích.

## Chạy

Cài .NET SDK **10.0.401** (target **net10.0**), mở terminal trong thư mục
`dotnet` này, nơi có `global.json`. Lab không cần package bên thứ ba,
dependency benchmark, Python hay SQL Server.

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --observe
```

Với clone, working directory là `labs/boundary-search/dotnet`. Với
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

`--check` in **17/17 checks passed**, exit 0 khi mọi check thành công;
bất cứ check nào thất bại đều exit 1. Các case gồm empty data, duplicate đầu,
target thiếu, khoảng ngoài dữ liệu, key âm/cực trị, ngữ nghĩa endpoint, biên đảo,
giữ nguyên input, null input, encoding kết quả âm của .NET, mảng ảo rất lớn
và case nhỏ đối chiếu với oracle quét. Mảng ảo chỉ cần số lượt indexed read
logarithmic; không cấp phát `int.MaxValue` phần tử.

## Điều cần giải thích

`Array.BinarySearch` và `List<T>.BinarySearch` trả **một** vị trí matching khi
tìm thấy, không hứa trả duplicate đầu tiên. Target không có trả bitwise complement
của insertion position; giải mã kết quả âm bằng `~result`,
không dùng `-result`. Method tự viết đổi `hi` khi equality để trả biên đầu.
Midpoint an toàn là `lo + (hi - lo) / 2`; không cộng hai index có thể quá lớn.

Key timestamp là `long`, sorted tăng dần. Hai search giả định indexed access và
comparison có chi phí hằng số. Check sortedness, sort và update mảng là công việc
riêng. Ví dụ SQL ở bài học không được console lab này thực thi.
Chạy reference check xác minh hành vi code; thực hành và báo cáo kết quả tùy chọn.

`--observe` in số lượt indexed read mà một lower boundary thực hiện với 8, 1.024 và
65.536 phần tử, rồi tìm event record theo key timestamp. Nó đếm số lần đọc phần tử,
không đo thời gian CPU.
