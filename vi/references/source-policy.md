<!-- contract-version: 1 -->
# Chính sách nguồn

Bản dịch của [policy chính](../../references/source-policy.md), là nguồn duy nhất cho nghiên cứu và đánh giá repo. Curriculum xác định phạm vi; tài liệu kỹ thuật gốc xác định hành vi triển khai; nghiên cứu học thuật xác định claim lý thuyết/học tập; OSS cho thấy một implementation; instructor synthesis đề xuất kết nối. Ghi nhãn cả năm vai trò; prerequisite suy luận không phải quy định IUH.

## Research mỗi bài

Đọc curriculum trước, nghiên cứu nền tảng và một cập nhật liên quan trực tiếp. Ưu tiên systematic review/meta-analysis và nghiên cứu gốc cho pedagogy; xem đối tượng, task, control, độ trễ, outcome, uncertainty và moderator trước claim hiệu quả. API ưu tiên docs/standard/source/test chính thức. Theory cũ vẫn có giá trị; mới không đồng nghĩa bằng chứng tốt hơn.

Chọn bộ nguồn đủ nhỏ hỗ trợ mục tiêu (thường 3–6, heuristic). Ghi title/author, URL, role, claim/section dùng, ngày kiểm tra, version/commit, trạng thái read/metadata_only/unavailable và giới hạn/conflict. Đọc abstract/citation không phải đọc methods; không bịa kết quả từ nguồn không truy cập được. Tách theory ổn định, hành vi đã xác minh theo version, hướng dẫn hiện hành chưa xác minh và nhận định người hướng dẫn.

Fact thay đổi phải kiểm tra lúc học: dependency/tool version, support, cloud limit, security, API, stars/activity. Version ghim để tái lập tách khỏi version mới nhất/khuyến nghị production. Access thất bại → nguồn ổn định đã kiểm tra hoặc hoãn; không gắn năm hiện hành cố định.

## Quy trình GitHub

1. Query hẹp theo mục tiêu/stack; khám phá repo nhiều star và lựa chọn chính thức/chuyên sâu. Thường chọn một, đôi lúc hai; chủ đề không phù hợp thì giải thích bỏ GitHub.
2. Ghi stars chính xác nếu lấy được, thời điểm, maintainer, archived, commit branch mặc định và release. API ưu tiên; HTML có provenance được chấp nhận. Chưa biết → null và lý do, không ước lượng. Ngưỡng stars chỉ giúp discovery.
3. Đánh giá fit, authority, usage có bằng chứng, maintenance/release, code/test/benchmark/docs, license, chi phí chạy và độ phức tạp học. Stars không chứng minh adoption; ghi điều chưa biết, không bịa điểm tổng hợp.
4. Chọn lát cắt vừa đủ; giải thích lựa chọn ít star hơn khi tốt cho mục tiêu, ghi ngắn alternative bị loại. Archived cần xác minh trực tiếp; không thấy banner là bằng chứng yếu hơn field rõ.
5. Ghim SHA hoặc release với SHA đã resolve; link file/function/test/benchmark/issue/PR cụ thể. Thiết kế predict, trace, fix, experiment hoặc comparison nối theory với trade-off.
6. Ghi version/data/commands, observation dự kiến và việc đã chạy thật. Có thể đọc code ghim rồi chạy bản cục bộ tương đương, nhưng không gọi đó là upstream build. License không tự cho quyền phân phối mọi dependency/curriculum.

Không README-only link dump, không stars-as-quality, không benchmark thiếu workload/environment, không dùng API sinh ra làm bằng chứng. Stack mặc định C#/.NET/T-SQL/TypeScript/Azure dùng khi hợp mục tiêu; không ép GitHub/công cụ.
