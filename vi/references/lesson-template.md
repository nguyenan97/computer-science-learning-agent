<!-- contract-version: 4 -->
# Mẫu bài học

Bản Việt của [template chính](../../references/lesson-template.md). [Workflow](learning-workflow.md) sở hữu selection/state, [pedagogy](pedagogy.md) sở hữu instruction, [source policy](source-policy.md) sở hữu research. Co giãn theo thời gian, không sao chép form dài mỗi ngày.

## Header và chọn bài

Session/topic ID, course code và section curriculum; core/review/remediation/deepening; status generated. Vì sao học tiếp, prerequisite với diagnostic thật hoặc unknown, quyết định về ôn đến hạn và semantic duplicate. Có 2–4 outcome đo được, mode/thời gian và hạn chế môi trường.

## Retrieval và kiểm tra prerequisite

Không ghi chú; lấy câu hỏi từ lượt ôn/bài trước. Chưa có lịch sử thì diagnostic, không giả định đã học. Task prerequisite ngắn, có nhánh ready → tiếp tục; weak → bridge/recheck; unknown → thu bằng chứng.

## Vấn đề, nền tảng và cập nhật

Vấn đề cụ thể và dự đoán; mental model tối thiểu với assumption/invariant. Ghi riêng curriculum, theory, guidance theo version và instructor synthesis. Cập nhật chỉ khi liên quan trực tiếp, có ngày kiểm tra và uncertainty. Một worked example giải thích quyết định.

## Lab hướng dẫn

Mục tiêu/prerequisite; OS/runtime/tool version, dependency/data, starter deterministic/setup, working directory và fallback. Mỗi bước có purpose, predict-before, checkpoint observable, self-check và explain-after. Có common errors/debug path; ưu tiên chạy cục bộ, không thêm hạ tầng vô ích.

## Hoạt động repo

Dossier theo source policy hoặc lý do không dùng GitHub. Ghim target cụ thể, yêu cầu suy hành vi từ test, trace hoặc so trade-off. Tách xác minh upstream build và local equivalent.

## Challenge và feedback

Bài tập tùy chọn, đổi constraint/context; mọi task, kể cả self-check/exit, có lời giải đầy đủ sau đề. Có thể dùng mục thu gọn nhưng không khóa theo attempt hay submission. Đánh giá tùy chọn; dùng task mới chưa xem đáp án nếu cần bằng chứng independent. Rubric nối outcome, lưu evidence/independence/error/explanation/correction. Explain-back và exit ticket có câu transfer.

## Nguồn và lịch ôn

Mỗi nguồn có role, contribution, URL/pin, ngày/status/limits. Prompt recall và transfer cho ngày sau. Chọn due sau evidence thực hành/completion theo workflow; review hook dự kiến chưa phải lượt đã ôn.

## Record artifact

JSON generated theo schema riêng, ghi thiết kế, không ghi kết quả. Ngày lifecycle sau null; assessment_ids rỗng. Generation không sinh điểm/mastery/lượt ôn thật. Giao/thử/hoàn thành chỉ persist sự kiện đã quan sát. Xem [bài mẫu](../lessons/boundary-search/lesson.md).

Mặc định 90 phút và nhánh 180+ phút tùy chọn; chỉ rút ngắn khi có giới hạn thời gian thật. Tính cho một bản ngôn ngữ. Đưa setup nhiều dependency, benchmark và đọc upstream vào nhánh sâu nếu chúng lấn thời gian giải thích chính. Setup quá lâu → trace offline hoặc chia phiên. Các thời lượng là heuristic thiết kế.

Lưu artifact riêng relative với thư mục state riêng, không vào public `lessons/`. Giao bài hoàn chỉnh, không chờ diagnostic/task response. Có nhánh prerequisite chưa xác minh; chỉ chờ bài làm thật khi người học yêu cầu đánh giá.

## Bài hằng ngày song ngữ

Có bản Việt và Anh đầy đủ, cùng objective/example/commands/bài tập tùy chọn/lời giải/nguồn. Lưu hai artifact riêng (`lesson.vi.md`, `lesson.en.md`) cho một session/topic, không tạo hai progress record. Mặc định 90 phút, thêm nhánh học sâu 180+ phút tùy chọn; thời lượng tính cho một bản ngôn ngữ, không bắt đọc cả hai. Có đường đọc-only; không cần làm/nộp bài để mở bài ngày sau.

## Kinh nghiệm người học và kiểm tra xuất bản

Dùng kinh nghiệm nghề nghiệp đã xác nhận làm ngữ cảnh, không coi là chứng nhận prerequisite toán/CS. Với kỹ sư có kinh nghiệm: yêu cầu cụ thể → trace nhỏ → mô hình chi phí và suy luận → implementation/invariant → trade-off có số đo → giới hạn production. Giải thích thuật ngữ mới khi dùng lần đầu; tránh dồn jargon hay dạy lại cú pháp đã biết. Chọn ecosystem phù hợp môn học rồi bridge sang stack người học.

Bài công khai có thư mục lab đầy đủ hoặc ZIP, working directory, pin SDK/dependency, output và cách gỡ lỗi. Stage bằng `scripts/build_public_site.py`; kiểm tra link được render, chuyển EN/VI và link trực tiếp tới code/data/download. Kiểm tra chạy lab sau giải nén, không chỉ trong repo. Tách kết quả đã đo, dự đoán và điều chưa chạy.
