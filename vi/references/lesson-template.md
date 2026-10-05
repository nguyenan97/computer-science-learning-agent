<!-- contract-version: 2 -->
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

Yêu cầu đổi constraint/context, không có full solution trong đề. Hint/lời giải mentor tách riêng và mở theo policy. Rubric nối outcome, lưu evidence/independence/error/explanation/correction. Explain-back và exit ticket có câu transfer.

## Nguồn và lịch ôn

Mỗi nguồn có role, contribution, URL/pin, ngày/status/limits. Prompt recall và transfer cho ngày sau. Chọn due sau evidence thực hành/completion theo workflow; review hook dự kiến chưa phải lượt đã ôn.

## Record artifact

JSON generated theo schema riêng, ghi thiết kế, không ghi kết quả. Ngày lifecycle sau null; assessment_ids rỗng. Generation không sinh điểm/mastery/lượt ôn thật. Giao/thử/hoàn thành chỉ persist sự kiện đã quan sát. Xem [bài mẫu](../lessons/boundary-search/lesson.md).

Ngân sách heuristic: ngắn 25 = 3 check + 6 model/example + 10 lab + 4 independent + 2 exit; tiêu chuẩn 55 = 5 check + 10 model/example + 20 lab + 10 independent + 5 repo + 5 feedback/exit; mở rộng 85 thêm 15 transfer và 15 source/experiment. Setup quá lâu → trace offline hoặc chia phiên.

Lưu artifact riêng relative với thư mục state riêng, không vào public `lessons/`. Dừng ở diagnostic/task để nhận câu trả lời thật; bản nháp có thể giữ điều kiện chưa xác minh.
