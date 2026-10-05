<!-- contract-version: 2 -->
# Workflow hằng ngày và state riêng

Bản dịch [policy chính](../../references/learning-workflow.md). Trang này sở hữu selection,
lifecycle, evidence, lịch ôn và persistence; pedagogy/source policy/template sở hữu
thiết kế dạy học/nguồn/đầu ra. Skill điều phối theo từng chặng tương tác.

## Bắt đầu và chọn bài

1. Chọn workspace riêng và validate state. Xem ôn đến hạn, bài đã giao/đang làm,
   bản generated chưa giao và ID assessment lỗi chưa giải quyết.
2. Hỏi ngắn mục tiêu/time/background/tools/timezone chưa biết. State trống nghĩa là
   chưa biết trình độ. Hỏi 2–3 task prerequisite, chờ câu trả lời và lưu response thật.
   Diagnostic có thể nằm trong phiên remediation; không bịa completion trước đó.
   Nếu chỉ yêu cầu soạn nháp, ghi prerequisite fit có điều kiện.
3. Ưu tiên retrieval đến hạn trong time budget. Prerequisite yếu → bridge/recheck;
   assigned/in_progress → tiếp tục; generated → xem lại rồi giao khi phù hợp.
   Lỗi chưa sửa phải được xử lý trước tăng khó. Mở nội dung không xóa due.
4. So sánh vài mục tiêu curriculum theo readiness, goal fit, continuity và giá trị
   thực hành. Tách quan hệ official và suy luận. Kiểm ID cùng nghĩa objective/concepts
   với mọi bài core, kể cả generated. Review/remediation nêu related_to; deepening
   có mục tiêu thực sự thay đổi.
5. Research bộ nguồn/lát cắt nhỏ. Mode ~25/55/85 phút chỉ là thiết kế, điều chỉnh theo
   time thật; giữ attempt quan sát được và feedback, chia setup/đọc sâu khi cần.

`plan` chỉ gợi ý, không chọn curriculum hoặc chứng nhận prerequisite. Flag ready/weak
phải từ diagnostic thật. Xem lỗi của cả prerequisite topic chưa có bài completed.
Bằng chứng tốt của topic cũ không chứng nhận sẵn sàng cho topic khác.

## Workspace riêng và lần đầu

State hoạt động duy nhất mặc định **.learning-private/learning-state.json**, được Git
ignore, hoặc đường dẫn ngoài repo chọn bằng `--state`. Bài riêng/code/evidence nằm
cùng workspace; artifact relative với thư mục chứa state. [Example công khai](../../state/learning-state.example.json)
chỉ là mẫu khởi tạo trống. Ledger là pointer. Không commit tiến độ/bài làm thật vào
repo công khai; loại khỏi Pages không bảo vệ dữ liệu đã push lên GitHub.

Dùng workspace bền vững, một writer. Atomic replacement chưa là locking/backup.
Nếu host không giữ file qua phiên, nói rõ chưa có persistence.

Từ repo root, Python 3.12:

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py init
python scripts/learning_state.py validate
python scripts/learning_state.py plan
# Chỉ ghi giá trị người học đã cung cấp:
python scripts/learning_state.py profile --minutes 25 --goal 'Mục tiêu người học nêu'
python scripts/learning_state.py add lessons /tmp/generated-lesson.json
python scripts/learning_state.py transition session-id assigned
python scripts/learning_state.py transition session-id in_progress
python scripts/learning_state.py add assessments /tmp/observed-assessment.json
python scripts/learning_state.py transition session-id completed
python scripts/learning_state.py add reviews /tmp/review-prompt.json
python scripts/learning_state.py review review-id assessment-id --next-due YYYY-MM-DD --reason 'Bằng chứng thật và mục tiêu lưu giữ'
```

Global `--state /private/path/learning-state.json` đứng trước subcommand. `init`
không ghi đè. Migrate v1: `python scripts/learning_state.py migrate --from-state /private/old-v1.json`.
Đích v2 phải mới; giữ nguyên nguồn/lịch sử, thêm repair links rỗng, không tự suy lỗi
đã sửa. Kiểm nội dung trước khi bỏ bản cũ.
Nếu v1 có bài thật, thêm `--artifact-root /original/repository-or-workspace`; copy
lesson files không ghi đè. Giữ code/output revisions tham chiếu cùng workspace và kiểm
evidence links trước resume; tham chiếu free-text không được tự viết lại.

## Schema version 2 và ý nghĩa sự kiện

[Schema](../../state/learning-state.schema.json) sở hữu tên/kiểu field.

| Collection | Ý nghĩa |
|---|---|
| learner | timezone, minutes, goals, background; null/rỗng là chưa biết |
| lessons | session duy nhất, topic/course/objective/concepts ổn định, prerequisites/related_to, private artifact, review hooks và constraints |
| lifecycle | generated: artifact tồn tại; assigned: đã giao/chấp nhận; in_progress: attempt thật; completed: xong phần việc thống nhất, có practice/retrieval/transfer/prerequisite evidence. Có thể còn sai/chưa chấm |
| assessments | response/code revision/output/trace thật, người chấm/ngày/outcome, score/basis nullable, hints/misconceptions/explanation/feedback/next_action; resolves_assessment_ids nối observation needs_support đã sửa |
| reviews | bài gốc completed, prompt, due đầu/hiện tại, attempts append-only; giữ assessment ID, ngày đã hẹn, next due và reason |

Lưu lời giải nguyên văn hoặc artifact revision bất biến. Agent chạy test không phải
attempt người học. Chưa biết → unassessed/null; score cần rubric; hinted/copied không
independent. Chỉ dùng transfer khi task thực sự đổi ngữ cảnh.

Ngày theo timezone. Thứ tự assessment array phân biệt attempt cùng ngày; append,
không reorder lịch sử. Sửa cùng ngày được phép nhưng không là delayed retention.
Review phải sau completion gốc; next due có thể bằng ngày quan sát để retry ngay,
khi đó item vẫn due. Giữ thứ tự và ghi quyết định làm sớm/muộn thật.

## Bằng chứng và sửa lỗi

Mỗi needs_support còn unresolved tới khi một assessment independent, non-exit,
sau đó trên cùng topic ghi rõ ID trong resolves_assessment_ids. Tutor phải kiểm task
mới sửa đúng lỗi bằng case mới; cùng topic thôi không chứng minh liên quan. Exit
không liên quan, partial hoặc không có lỗi mới không xóa lỗi cũ. Giữ cả evidence gốc/sửa.

Summary theo mục tiêu: unknown → developing/needs_remediation → provisional practice
độc lập → retained_and_transferred khi recall/transfer độc lập sau completion và không
lỗi unresolved. Xem interval, difficulty, explanation, hint; ngày sau chỉ là độ trễ tối
thiểu quan sát, không chứng minh retention horizon đủ. `plan --on` chiếu lifecycle/
review events tới ngày chọn, chưa là audit lịch sử profile edits hoặc ngày tạo review.

## Feedback, lịch ôn và recovery

Feedback sau attempt thật; phân loại knowledge/model/execution/tool/trade-off, yêu cầu
sửa và case mới. Tạo ôn sau completion; phiên partial giữ assessment/next_action rồi
resume, không bịa completion. Sai → correction/retry sớm; assisted → giữ/giảm gap;
recall/transfer độc lập sau delay → cân nhắc tăng theo retention goal. Không lịch offset
phổ quát hay bịa các lần bỏ lỡ.

Fixture cần fixture:true, --allow-fixture và path riêng, không vào progress thật.
Sample công khai là thiết kế. Nguồn unavailable → ghi rõ/dùng stable verified/defer;
lab chưa chạy → trace/equivalent và limits; hết giờ → in_progress; state invalid →
giữ nguyên, sửa theo evidence, không reset âm thầm.
