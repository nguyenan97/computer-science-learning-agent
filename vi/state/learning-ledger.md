# Sổ tiến độ học

Nguồn trạng thái duy nhất là [learning-state.json](../../state/learning-state.json), có phiên bản và [schema](../../state/learning-state.schema.json). Kiểm tra bằng `python scripts/learning_state.py validate`.

Trang này không chứa bộ đếm hay LESSON_RECORD riêng. Bản Anh và Việt cùng trỏ đến một JSON. Xem [workflow hằng ngày](../references/learning-workflow.md) để phân biệt bài đã tạo, đã giao, đang làm, đã hoàn thành; lưu bằng chứng và từng lần ôn. Chạy `python scripts/learning_state.py plan` để xem ôn đến/quá hạn, bài còn dở và mức bằng chứng theo chủ đề.

Trạng thái khởi đầu trống vì chưa quan sát được lần thực hành nào của người học. Bài mẫu và fixture nằm ngoài tiến độ thật. Ledger Markdown cũ không có record cần chuyển đổi.
