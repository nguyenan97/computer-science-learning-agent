<!-- contract-version: 1 -->
# Workflow hằng ngày và contract trạng thái

Trang này là bản Việt của [policy chính](../../references/learning-workflow.md), sở hữu cách chọn bài, lifecycle, đánh giá, lịch ôn và persistence. [Pedagogy](pedagogy.md) sở hữu thiết kế dạy học; [source policy](source-policy.md) sở hữu nghiên cứu; [template](lesson-template.md) sở hữu đầu ra. SKILL chỉ điều phối. Schema JSON sở hữu tên và kiểu field; không tạo schema hay ledger riêng bằng tiếng Việt.

## Trước khi soạn bài

1. Đọc và validate **state/learning-state.json**, nguồn trạng thái duy nhất. Xem bài đã giao/đang làm, mục tiêu đã hoàn thành, bằng chứng và tất cả lượt ôn đến/quá hạn theo timezone người học.
2. Hỏi ngắn về thời gian, mục tiêu, nền tảng và công cụ nếu chưa biết. Ledger trống nghĩa là chưa biết trình độ, không đồng nghĩa mới bắt đầu hay chuyên gia. Thu 2–3 câu trả lời prerequisite hoặc bài tập nhỏ; lưu câu trả lời thật. Diagnostic có thể nằm trong phiên remediation đang làm, nối với chủ đề dự kiến, không bịa bài trước đã hoàn thành.
3. Ưu tiên retrieval đến hạn trong ngân sách thời gian; có thể chỉ ôn hôm nay. Một lượt vẫn đến hạn cho tới khi đã thử và đánh giá. Prerequisite yếu → bridge và kiểm tra lại. Bài đã giao → tiếp tục, không sinh bản trùng.
4. Chọn một mục tiêu core từ curriculum và quan hệ suy luận được ghi nhãn riêng. So sánh vài ứng viên theo readiness, mục tiêu, giá trị curriculum/thực hành và mạch nối; ghi lý do chọn, không coi điểm heuristic là khoa học.
5. Kiểm tra cả topic ID lẫn mục tiêu/concepts với bài core đã tạo, đã giao và hoàn thành. Validator chặn core trùng ID; người hướng dẫn vẫn phải kiểm tra semantic duplicate. Độ trùng tag chỉ là dấu hiệu. Review/remediation nêu `related_to`; deepening phải nêu mục tiêu mới hoặc yêu cầu khó hơn.
6. Research lý thuyết nền và hướng dẫn triển khai liên quan trực tiếp, ghi vai trò và mức xác minh. Bài kỹ thuật thường chỉ cần một repo; có thể không dùng khi không giúp mục tiêu, kèm lý do. Kiểm tra fact thay đổi tại thời điểm học, không gắn năm cố định.
7. Chọn chế độ ngắn (~25 phút), tiêu chuẩn (~55), mở rộng (~85), rồi điều chỉnh theo thời gian thật. Đây là mặc định sản phẩm. Giữ một lần thử độc lập và feedback; dời đọc sâu/lab dài sang ngày khác nếu cần.

`python scripts/learning_state.py plan` chỉ gợi ý ưu tiên, không chọn concept hay chứng nhận prerequisite. `--prerequisite ready/weak` phải dựa trên diagnostic đã quan sát. Flag nguồn/lab không truy cập được chỉ hỗ trợ chọn fallback.

## Trạng thái canonical, schema version 1

[Schema](../../state/learning-state.schema.json), Python 3.12 và requirements kiểm tra được ghim. Ngày dùng `learner.timezone`; schema theo ngày chưa phân biệt thứ tự trong cùng một ngày. Không cần database.

| Collection/field | Ý nghĩa |
|---|---|
| learner | timezone, số phút, mục tiêu, nền tảng; null/rỗng là chưa biết |
| lessons | session ID duy nhất, topic ID ổn định (`course-slug.concept.depth`), course code, objective, concepts, prerequisites; kind core/review/remediation/deepening; related_to; artifact, review_prompts, constraints |
| lifecycle | generated: bài tồn tại; assigned: đã giao/chấp nhận; in_progress: người học báo đã thử thật; completed: hoàn tất phần việc đã thống nhất và có bằng chứng task (practice, retrieval, transfer hoặc prerequisite). Vẫn có thể sai/chưa chấm; completion không phải mastery |
| assessments | task, bằng chứng thật (câu trả lời, file + revision, output, trace), người đánh giá/ngày quan sát; outcome needs_support/developing/independent/unassessed; score/basis nullable; hint thực sự dùng, misconception, chất lượng giải thích nullable; feedback và next_action |
| reviews | prompt nối bài gốc đã hoàn thành, ngày hẹn đầu/hiện tại, từng attempt nối assessment retrieval/transfer; giữ scheduled_for, next_due_on và lý do |

Chưa biết kết quả → null/unassessed. Điểm cần cơ sở rubric rõ; dùng hint không tính independent. Agent chạy lab không phải bằng chứng người học. Giữ lời giải thích nguyên văn hoặc trỏ artifact trước khi chấm. Assessment có thể ghi topic prerequisite; lesson_id vẫn là phiên thật nơi diagnostic diễn ra. Task đổi ngữ cảnh dùng kind transfer, không tự coi mọi test pass là transfer.

Script suy ra mức bằng chứng, không ghi mastery thủ công: unknown → developing/needs_remediation → provisional khi thực hành độc lập → retained_and_transferred khi có recall và transfer độc lập ở ngày sau. Đây là heuristic thận trọng theo mục tiêu, không phải ước lượng tâm trắc. Một ngày sau chỉ là độ trễ tối thiểu quan sát được, không chứng minh nhớ bền vững; xem khoảng cách thật, độ khó, rubric và bằng chứng trái chiều mới nhất.

## Ghi dữ liệu cục bộ

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py validate
python scripts/learning_state.py plan
python scripts/learning_state.py add lessons /tmp/generated-lesson.json
python scripts/learning_state.py transition session-id assigned
python scripts/learning_state.py transition session-id in_progress
python scripts/learning_state.py add assessments /tmp/observed-assessment.json
python scripts/learning_state.py transition session-id completed
python scripts/learning_state.py add reviews /tmp/review-prompt.json
python scripts/learning_state.py review review-id assessment-id --next-due YYYY-MM-DD --reason 'Kết quả recall thực tế và mục tiêu lưu giữ'
```

Người hướng dẫn chuẩn bị JSON theo schema; chỉ ghi sự kiện đã quan sát. CLI validate trước khi thay file atomically; chỉ một writer, chưa hỗ trợ khóa nhiều agent. Record generated có ngày lifecycle sau null, assessment_ids rỗng. Thêm assessment không tự hoàn thành bài. Lưu cả bài dở; nếu chưa hoàn thành thì dùng next_action và tiếp tục/sửa lỗi, không bịa lịch ôn từ bài đã hoàn thành.

Tạo lịch ôn sau completion; chỉ cập nhật khi đã có assessment thật: sai → sửa misconception và retry sớm hơn; dùng hint/chưa ổn → giữ hoặc giảm khoảng cách; độc lập và transfer tốt → cân nhắc tăng khoảng cách theo mục tiêu. Không tự áp lịch cố định hay điền các lượt đã bỏ lỡ. Thêm attempt, không ghi đè lịch sử hay sửa điểm cũ để đẹp hơn.

Fixture trong tests/fixtures có `fixture:true`, chỉ dùng CLI với `--allow-fixture --state ...`. Bài mẫu chưa giao cũng nằm ngoài trạng thái thật. Ledger Markdown chỉ là trang điều hướng, không có counter/history riêng.

## Feedback và fallback

Phân loại thiếu kiến thức, mental model sai, lỗi thực thi, dùng sai tool/API hoặc thiếu trade-off. Feedback gắn lỗi, yêu cầu sửa và thử case mới. Chỉ giảm scaffolding/tăng khó theo bằng chứng độc lập có độ trễ, không chỉ vì completion.

Nguồn không truy cập được → ghi unavailable, dùng nguồn ghim đã xác minh cho fact ổn định hoặc dời claim thay đổi. Lab không chạy → trace offline/bản nhỏ tương đương, ghi giới hạn, không nói đã chạy. Hết thời gian → giữ in_progress và chia lab. State invalid → dừng ghi và sửa với lịch sử còn nguyên, không reset âm thầm.
