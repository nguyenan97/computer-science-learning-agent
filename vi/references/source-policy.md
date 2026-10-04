# Chính sách nguồn

## Mục tiêu

Dùng nguồn để tạo một bài học có thể bảo vệ được về mặt học thuật/kỹ thuật, không phải để tối đa số lượng citation.

## Phân tầng nguồn

### Tier A — Project Ground Truth

Các source Master IUH của project xác định phạm vi curriculum, terminology, course outcome và institutional framing.

Ưu tiên dùng chúng khi quyết định chương trình yêu cầu điều gì.

### Tier B — Primary Technical Authority

Ví dụ:

- Microsoft Learn / tài liệu .NET
- Azure Architecture Center / Well-Architected Framework
- tài liệu sản phẩm chính thức
- standard / RFC
- official framework design document
- official source repository

Dùng các nguồn này cho current behavior, API semantics, architecture guidance, support status, giới hạn và recommended pattern.

### Tier C — Rigorous Academic Sources

Ưu tiên:

- textbook được curriculum nêu
- peer-reviewed paper
- MIT OpenCourseWare
- tài liệu từ Stanford / CMU / Berkeley / Harvard / Cornell và các trường tương đương
- lecture note / problem set có thẩm quyền

Dùng cho theory, proof, problem set, experimental method và mental model bền vững.

### Tier D — Production OSS Evidence

Dùng mature repository để cho thấy khái niệm được triển khai thế nào trong hệ thống thực tế.

Đánh giá:

1. mức độ liên quan với bài học
2. authority của maintainer
3. độ mới của commit / release
4. chất lượng test / benchmark
5. chất lượng thảo luận issue và PR
6. mức độ adoption thực tế
7. stars / forks / contributors như tín hiệu phụ

Với community repository, >= 5k stars là discovery threshold hữu ích, không phải bảo đảm chất lượng.

Chỉ đọc phần nhỏ nhất cần thiết:

- implementation file
- unit / integration test
- benchmark
- design note
- issue
- merged PR

Không yêu cầu người học browse một repository lớn mà không có target cụ thể.

### Tier E — Secondary Sources

Blog, tutorial, video, Q&A site.

Chỉ dùng khi chúng có cách giải thích hoặc reproduction thực tế đặc biệt rõ mà primary source không cung cấp.

Không để Tier E ghi đè một primary source hiện hành.

## Quy tắc về tính hiện hành

Các fact bên ngoài có thể thay đổi phải được verify tại thời điểm tạo bài học:

- version và feature của .NET / C# / Angular / SQL Server / Azure
- package API
- cloud service behavior / limit
- GitHub stars / activity
- security guidance
- AI model / SDK behavior

Ưu tiên nguồn mới, nhưng không loại bỏ foundational theory cũ chỉ vì nó cũ.

## Source Triangulation

Với claim ảnh hưởng production, cố gắng triangulate:

- curriculum dạy gì
- official docs hiện nay khuyến nghị gì
- source code / test thực tế cho thấy gì

Nếu chúng khác nhau, giải thích nguyên nhân.

## Search pattern gợi ý

- `<concept> site:learn.microsoft.com`
- `<concept> site:github.com/dotnet`
- `<concept> site:ocw.mit.edu problem set`
- `<concept> Stanford course notes`
- `<concept> paper survey`
- `<concept> benchmark GitHub`

## Anti-pattern

Tránh:

- dùng SEO listicle làm bằng chứng chính
- dùng Stack Overflow answer cũ cho current framework behavior
- dùng star count làm tiêu chí duy nhất đánh giá repository
- tóm tắt paper mà không đọc methodology / evaluation
- đưa benchmark number mà không nêu environment và workload context
- dùng generated code làm bằng chứng rằng một API tồn tại
