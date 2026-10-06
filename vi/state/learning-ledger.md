# Công cụ state v3 đã đưa ra khỏi luồng hằng ngày

Luồng học hằng ngày dùng catalog công khai, không lưu câu trả lời, tiến độ hay
record hoàn thành. Đọc hoặc yêu cầu bài không cần khởi tạo state. Trang này không
chứa record hay counter người học.

`scripts/learning_state.py` được giữ như công cụ bảo trì tùy chọn đã lưu trữ.
Chỉ hỗ trợ [schema v3](../../state/learning-state.schema.json); đã bỏ chuyển đổi
v1/v2. [Example trống](../../state/learning-state.example.json) là template giả lập,
không phải tiến độ người học. Quy trình soạn bài hiện tại nằm trong
[lesson spec](../../references/lesson-spec.md).

Nếu người bảo trì tự dùng công cụ cũ, state thật phải nằm ở
`.learning-private/learning-state.json` hoặc workspace riêng ngoài repo. Không commit
state hay bài làm thật vào repo công khai.
