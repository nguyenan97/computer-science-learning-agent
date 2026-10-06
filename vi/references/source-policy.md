<!-- contract-version: 5 -->
# Chính sách nguồn

Chọn phạm vi từ mục tiêu, prerequisite và [bản đồ chủ đề](topic-map.md). Nguồn học thuật hỗ trợ claim lý thuyết/học tập; tài liệu/chuẩn chính thức mô tả hành vi kỹ thuật; implementation/test được ghim cho thấy một cách triển khai; tổng hợp của tutor đề xuất kết nối. Ghi rõ vai trò. Topic map là thiết kế project, không chứng minh năng lực hay là yêu cầu đào tạo bên ngoài.

## Research mỗi bài

Bắt đầu với một objective đo được và 2–4 câu hỏi có thể trả lời. Tách claim nền tảng ổn định với implementation thay đổi. Ưu tiên nghiên cứu gốc, systematic review/meta-analysis và tổng hợp học thuật cho phương pháp học; tài liệu, chuẩn và code/test chính thức cho kỹ thuật. Mới/cũ không tự quyết định chất lượng.

Dùng bộ nguồn nhỏ hữu ích, thường 3–6 (heuristic). Ghi title/tác giả, URL, vai trò, claim/section dùng, ngày kiểm tra, version/commit, trạng thái (`read`, `metadata_only`, `unavailable`) và **phạm vi đọc**: abstract, một số phần full text, toàn văn hay metadata. Tải PDF không có nghĩa đã đọc; abstract không phải review methods. Giữ attribution gốc khi tổ chức lại. Không chép lượng lớn văn bản nguồn vào bài.

Với claim nghiên cứu, xem population, task, comparison, độ trễ, outcome và giới hạn trong mức truy cập thật. Tách finding của paper với suy luận áp dụng sang học lập trình. Không bịa effect size, nhân quả, khuyến nghị hay tuyên bố review đầy đủ. Ghi correction/retraction nếu phát hiện; khi chưa đọc thì không dùng số liệu có thể bị ảnh hưởng. Nêu nguồn mâu thuẫn và điều gì có thể phân biệt chúng.

[Review learning science](../research/learning-science-review.md) và [log truy cập chung](../../research/deep-study-source-checks.json) cung cấp bằng chứng kiểm tra ban đầu. Chúng không chứng minh hiệu quả agent, lịch phổ quát hay tỷ lệ thực hành tối ưu.

## Đọc để trả lời và kiểm tra câu hỏi

Giải thích ý chính có nguồn hỗ trợ, ví dụ và code bằng lời của bài ngay trên trang.
Không buộc người học mở paper/repo/download để lấy phần giải thích hay lời giải
chính. Đọc bổ sung có section, câu hỏi và output: bảng claim, dự đoán, trace chú thích,
so sánh hoặc thí nghiệm. Giới hạn lướt mở; giữ câu hỏi chưa trả lời cho sau. Tách kết
quả đã quan sát, dự đoán, suy luận và claim chưa xác minh.

Ngày/status kiểm tra, hash, access log, dossier đánh giá repo và log agent ở artifact
riêng hoặc tài liệu maintainer. Trang cho người học có trích dẫn ngắn liên quan và
footer đọc bổ sung chọn lọc, mô tả mỗi nguồn giúp gì. Giữ attribution. Chỉ đưa giới
hạn truy cập/xác minh lên bài khi cần hiểu kết quả hoặc chạy code; không chép bảng
audit nội bộ hay lặp disclaimer trong mọi bài.

Kiểm tra thông tin thay đổi khi viết bài: API/dependency, hỗ trợ, hạn mức cloud, hướng dẫn bảo mật và hoạt động repo. Pin version tái hiện riêng; ví dụ cũ tái hiện được không tự là khuyến nghị production mới nhất. Truy cập thất bại thì ghi giới hạn thật, dùng nguồn ổn định đã xác minh/tương đương cục bộ hoặc dời claim. Hai ngôn ngữ cùng nêu uncertainty.

## Quy trình implementation/repo

1. Tìm hẹp từ objective. So implementation chính thức/chuyên môn với phương án phổ biến liên quan khi hữu ích. GitHub tùy chọn nếu chuẩn, local implementation hoặc paper trace dạy tốt hơn.
2. Ghi maintainer, license, archive, release/default branch và stars với thời điểm nếu lấy được. Trường thiếu/mơ hồ dùng null kèm lý do. Phổ biến chỉ giúp discovery, không bảo đảm chất lượng học hay mức sử dụng.
3. Đánh giá độ khớp objective, thẩm quyền, bảo trì, code/test, docs, setup và độ phức tạp. Chọn phần nhỏ, thường một repo; giải thích phương án không chọn, không bịa điểm tổng hợp.
4. Pin commit SHA bất biến (hoặc release có SHA đã giải quyết), link file/function/test/benchmark chính xác. Giao dự đoán, trace, sửa lỗi hoặc so sánh có kiểm soát nối behavior với model.
5. Ghi working directory, runtime/dependency/data, seed, lệnh, observation kỳ vọng và phần agent thật sự chạy. Tách upstream execution, local equivalent và đọc code. Benchmark có workload/môi trường; một máy không chứng minh ưu thế tốc độ phổ quát.
6. Giữ notice/license và attribution code phân phối; kiểm tra dependency riêng. Giữ riêng submissions và source artifact có thông tin nhận dạng.

Không link dump chỉ README, API do model bịa, xếp stars thành chất lượng hay benchmark giả. Hỗ trợ offline. Nguồn không truy cập/lab chưa chạy giữ rõ trong research record, giải thích hệ quả liên quan người học khi cần.
