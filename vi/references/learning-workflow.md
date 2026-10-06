<!-- contract-version: 5 -->
# Workflow hằng ngày và state riêng

Quản lý selection, lifecycle, evidence, ôn và persistence. [Pedagogy](pedagogy.md), [source policy](source-policy.md), [template](lesson-template.md) quản lý dạy, research và output. [Skill](../../skills/cs-daily-deep-study/SKILL.md) triển khai workflow. Việt/Anh cùng contract version.

## Bắt đầu và chọn

1. Validate state riêng; xem ôn đến hạn, bài assigned/in_progress, draft generated và assessment chưa giải quyết. Giữ evidence.
2. Dùng lại goal, thời gian, công cụ, nghề nghiệp và timezone đã khai. Background/readiness tự khai khác evidence thật theo objective. Unknown giữ nguyên; thiếu evidence không có nghĩa chưa biết lập trình.
3. Có 2–3 self-check prerequisite tùy chọn với đáp án/bridge. Phản hồi thật liên quan cho phép điều chỉnh; không trả lời vẫn giao có điều kiện, không bịa diagnostic. Topic cũ tốt không chứng nhận objective khác.
4. Xem retrieval, sửa lỗi, bài dở trước tăng khó; tái dùng draft phù hợp. Yêu cầu ngày mới khi bài cũ chưa xong vẫn được nhận objective giới hạn, ghi unknown. Planner không khóa truy cập.
5. So objective trong [topic map](topic-map.md) theo prerequisite, liên tục, goal và giá trị thực tế. Thứ tự là thiết kế project. Kiểm tra ID/trùng ý nghĩa với mọi core, cả draft. Deepening cần objective đổi; review/remediation nêu topic liên quan.
6. Research bộ nguồn nhỏ hữu ích rồi giao cả ngày song ngữ. Mặc định 420 phút gồm nghỉ (360 học, 235 chủ động); tôn trọng thời gian ngắn được yêu cầu. Bridge thay đào sâu, setup có điểm dừng, câu hỏi để sau được.

`plan` báo evidence/lời khuyên; flag readiness/profile không là chứng nhận. Xem observation chưa giải quyết, kể cả prerequisite chưa có bài completed.

## Trang học và phiên nội bộ

Giao trang học có diễn giải đầy đủ, code task, thí nghiệm và lời giải ngay trong bài.
Trích nguồn ngắn; link đọc/download là bổ sung. Tổ chức theo câu hỏi thực tế của
người học. Audit chọn bài, session/topic record ID, bảng evidence cá nhân, state
transition, source access log và thủ tục assessment ở phiên riêng/tài liệu maintainer.
Không biến quy tắc workflow nội bộ thành boilerplate lặp ở bài học.

Trang công khai kết thúc bằng đọc liên quan và bài trước/sau đang có trong
`lessons/catalog.json`, do `scripts/add_lesson_navigation.py` render giữa footer
markers trong template. Giữ ngôn ngữ/thứ tự catalog, không bịa bài tiếp. Navigation
là truy cập nội dung, không khóa theo tiến độ/assessment. Quy tắc evidence/privacy
bên dưới vẫn phải thực hiện đầy đủ.

## Lưu riêng và bắt đầu dùng

State mặc định **.learning-private/learning-state.json** bị Git ignore hoặc external `--state`. Giữ lesson/code/notes research/thí nghiệm/evidence dưới thư mục cha state, artifact path relative. [Example công khai](../../state/learning-state.example.json) là khởi tạo rỗng, không là tiến độ. Không commit personal state/artifact, đưa vào Pages/fixture/sample. Một writer: atomic replace không là khóa/backup. Không nói persistence khi host không giữ file.

Từ root repo (Python 3.12):

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py init
python scripts/learning_state.py validate
python scripts/learning_state.py plan
# Chỉ đổi sang dữ liệu người học thật sự cung cấp:
python scripts/learning_state.py profile --minutes 420 --goal 'Mục tiêu người học đã khai'
python scripts/learning_state.py add lessons /tmp/generated-lesson.json
python scripts/learning_state.py transition session-id assigned
python scripts/learning_state.py transition session-id in_progress
python scripts/learning_state.py add assessments /tmp/observed-assessment.json
python scripts/learning_state.py transition session-id completed
python scripts/learning_state.py add reviews /tmp/review-prompt.json
python scripts/learning_state.py review review-id assessment-id --next-due YYYY-MM-DD --reason 'Bằng chứng thật và mục tiêu lưu giữ'
```

Global `--state /private/path/learning-state.json` đặt trước subcommand. `init` không overwrite. Plan dùng 420 phút khi chưa biết thời gian; đây không phải sở thích tự bịa của người học.

## Schema v3 và migration

[Schema](../../state/learning-state.schema.json) quản lý fields/types. V3 bỏ metadata môn, giữ topic/session ID và evidence.

| Collection | Ý nghĩa |
|---|---|
| learner | Timezone, minutes/goals/background tự khai; rỗng/null là unknown; tự khai không là assessment |
| lessons | Session/topic, objective, concepts, prerequisite, topic liên quan, artifact riêng, constraints, review hooks |
| lifecycle | generated: có artifact; assigned: thật sự giao/nhận; in_progress: lần thử thật; completed: xong phần đã thống nhất liên quan objective, có evidence đủ loại |
| assessments | Response/revision/output/trace thật, assessor/date/kind, score/basis nullable, trợ giúp, lỗi, giải thích, feedback, next action và repair links |
| reviews | Source completed, prompt, due ban đầu/hiện tại, append-only attempts thật với assessment ID/lý do |

Completion cần practice/retrieval/transfer/prerequisite được tham chiếu **cùng topic bài**, trong khoảng started/completed. Có thể lưu prerequisite khác topic nhưng không hoàn thành objective này. Engine kiểm tra cấu trúc; **tutor phải kiểm tra liên hệ ý nghĩa objective/task/rubric/evidence**. Cùng ID không chứng minh phù hợp. Assisted work/needs_support có thể là xong phần thống nhất, không là proficiency độc lập. Exit-only, đọc bài, agent runs và generation không hoàn thành bài.

Migrate v1/v2:

```bash
python scripts/learning_state.py --state /private/new-state.json migrate --from-state /private/old-state.json --artifact-root /original/workspace
```

Migration viết v3 mới, giữ source/evidence, copy lesson artifact không overwrite. Giữ repair links v2; v1 thiếu thì rỗng, không suy repairs. Giữ code/output revisions, kiểm tra link evidence tự do vì không rewrite tự động. Completion cũ sai linkage thất bại trước khi ghi destination. Xem originals, chỉ sửa riêng khi có căn cứ hoặc giữ source chờ review; không bịa assessment/xóa observation/evidence. Metadata cũ chỉ bỏ ở state mới; original vẫn là archive.

## Quan sát, đánh giá và sửa

Giữ nguyên response hoặc link revision bất biến. Agent tests kiểm artifact, không learner attempt. Ghi trợ giúp riêng; unknown là unassessed/null. Điểm có rubric; dùng lời giải không independent. Transfer cần đổi ngữ cảnh có ý nghĩa, không chỉ input mới.

Ngày theo timezone người học. Append assessment không reorder, thứ tự phân biệt trong ngày. Mỗi needs_support chưa giải quyết tới assessment sau independent/non-exit/cùng topic nêu ID trong `resolves_assessment_ids`. Kiểm tra case mới sửa đúng lỗi; cùng topic/hết thấy lỗi không đủ. Giữ hai observations.

Summary bảo thủ, giới hạn phạm vi: unknown → developing/needs_remediation → provisional independent practice → retained_and_transferred khi recall/transfer independent sau completion, không unresolved errors. Xem độ khó, delay thật, explanation/hints. Sửa cùng ngày không delayed retention; ngày sau là tách biệt tối thiểu, không ngưỡng khoa học. `plan --on YYYY-MM-DD` dự chiếu lesson/review events, không toàn bộ lịch sử profile/review creation.

## Lịch, liên tục và phục hồi

Sau completion/attempt thật, đề xuất prompt/due theo retention goal. Ghi từng lượt ôn thật cả fail/sớm/muộn. Fail → sửa/check gần; assisted → giữ/rút gap; delayed independent → có thể kéo dài. Khoảng cách là thiết kế. Next due có thể bằng ngày quan sát cho retry; review observation sau completion source.

Giữ phần dở in_progress/next action. Đọc/xem lời giải/generation/publication không tạo assessments/completion/repairs/ôn đã làm. Task/submission tùy chọn; đáp án EN/VI/đường chỉ đọc luôn có. Ngày sau không đòi submission trước.

Fixture cần `fixture:true`, path riêng, `--allow-fixture`, không tiến độ thật. Ghi source fail/lab unrun cùng trace/local equivalent và giới hạn. Giữ state sai khi sửa nguyên nhân. Chỉ publish generic assets được phép khi có yêu cầu rõ; không tự deploy hoặc xuất bản thông tin riêng.
