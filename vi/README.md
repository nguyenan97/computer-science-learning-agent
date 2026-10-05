# Computer Science Learning Agent

[English](../README.md) · [Tiếng Việt](README.md)

Agent học CS hằng ngày có curriculum, research, thực hành tái lập, ôn sau độ trễ và tiến độ có bằng chứng. IUH Thạc sĩ/Tiến sĩ là triển khai tham chiếu; workflow có thể dùng curriculum khác.

## Học mỗi ngày

1. Yêu cầu dùng [skill](../skills/master-iuh-daily-learning/SKILL.md), nêu mục tiêu, số phút và công cụ. Ví dụ: “Bài 25 phút, tôi biết mảng nhưng chưa chắc loop invariant, có Python.”
2. Agent validate state riêng, xem ôn đến hạn, bài dở và generated chưa giao; thu prerequisite response thật. Chưa biết trình độ không coi đã mastery. Hôm nay có thể chỉ ôn hoặc bổ sung nền.
3. Một core objective có nghiên cứu, worked example, lab từng bước và transfer độc lập; xin hint tăng dần khi cần. Mode ngắn/chuẩn/mở rộng theo thời gian thật.
4. Gửi code/trace, output chạy thật và explain-back. Agent chỉ ghi attempt/hint/misconception/evidence quan sát; sinh bài hoặc agent chạy test không chứng minh bạn đã học.
5. Sau completion chọn due theo kết quả/retention goal. Recall và transfer ngày sau tăng bằng chứng; completion không mastery.

[Workflow](references/learning-workflow.md) có CLI và fallback. [Bài mẫu hoàn chỉnh](lessons/boundary-search/lesson.md) gồm offline lab, repo/test ghim, challenge và rubric; chưa giao và nằm ngoài progress thật.

## Research và contract

- [Review repo trước sửa](research/repository-review.md)
- [Learning science: nguồn, mức bằng chứng và giới hạn](research/learning-science-review.md)
- [Pedagogy](references/pedagogy.md), [source policy](references/source-policy.md), [lesson template](references/lesson-template.md)
- [Ledger chỉ dẫn](state/learning-ledger.md), [schema chung](../state/learning-state.schema.json)
- [Kiểm chứng và giới hạn còn lại](research/verification.md)
- [Thiết kế runtime/skill và nguồn mới](research/runtime-design-review.md)

Mỗi contract một owner; SKILL điều phối, không copy. State hoạt động là `.learning-private/learning-state.json` (Git-ignore) hoặc workspace ngoài repo; [example công khai](../state/learning-state.example.json) chỉ là template trống; hai ledger Anh–Việt hướng dẫn tìm state riêng. Fixture không vào progress thật; chưa cần backend/database.

## Kiểm tra cục bộ

Python 3.12; lab chỉ standard library, validation dùng các dependency dev ghim.

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py init  # một lần, trong workspace riêng bền vững
python scripts/learning_state.py validate
python scripts/learning_state.py plan
python scripts/generate_curriculum_map.py --check
python scripts/validate_docs_navigation.py
python scripts/validate_learning.py
python -m unittest discover -s tests -v
python scripts/learning_state.py --state tests/fixtures/low-result.json --allow-fixture plan --prerequisite ready
```

`starter.py` cố ý chưa hoàn thành. Bài tập tùy chọn, lời giải truy cập ngay sau đề. CI chạy mentor, không ghi completion người học. Số test pass không là mastery score.

## Curriculum, generated và song ngữ

[Thạc sĩ](curricula/iuh/master/curriculum.md), [Tiến sĩ](curricula/iuh/phd/curriculum.md); English sở hữu curriculum facts, Vietnamese là bản dịch. Giữ năm nguồn lịch sử. [Map generated](references/curriculum-map.md) tách official relationships và learning-agent synthesis.

```bash
python scripts/generate_curriculum_map.py
python scripts/generate_curriculum_map.py --check
```

Sửa nguồn/generator, không sửa map thủ công. Đợt này không xác minh PDF gốc/quy định IUH live; curriculum rút gọn không thay quy định hiện hành.

Docsify: [English](https://nguyenan97.github.io/computer-science-learning-agent/#/) · [Tiếng Việt](https://nguyenan97.github.io/computer-science-learning-agent/#/vi/). Push main deploy docs công khai và sample cố định đã stage; không commit state/bài làm thật vào public repo. English sở hữu policy; bản Việt cùng contract version, field/state không đổi ngôn ngữ. Version/nav check chỉ cấu trúc; semantic parity cần review song ngữ. Code/scripts/metadata dùng chung.

Giữ hash routing Project Pages; sidebar chỉ docs, navbar chuyển ngôn ngữ. Route root-relative, không hard-code `#/` trong navigation. Giữ loadNavbar, navbarPreservePath, fallbackLanguages và 404.html. CI cũ kiểm map/nav, CI mới kiểm workflow.

Thư mục: skills điều phối; references contract/map; research nguồn/review/results; state template trống/schema/pointer; lessons đề/record/dossier; labs starter/checkpoint/mentor; tests fixture; scripts validator/CLI; vi bản dịch.

## License

Repo vẫn chưa chọn project license; cần chọn trước khuyến khích đóng góp ngoài. Curriculum giữ attribution. Không tự thêm license hay vendor implementation bên thứ ba.

## Bắt đầu phiên thật

Giữ repo đầy đủ, không copy SKILL.md riêng. Prompt: “Dùng master-iuh-daily-learning, đọc tiến độ riêng, hỏi mục tiêu/time/tools chưa biết, soạn bài Việt–Anh đầy đủ, self-check tùy chọn có lời giải.” Giao bài không chờ nộp; chỉ chấm bài làm thật người học tự nguyện gửi. CLI profile cập nhật giá trị thật; [workflow](references/learning-workflow.md) hướng dẫn migrate v1, repair links và retry cùng ngày. Bảy [eval case](../skills/master-iuh-daily-learning/evals/cases.json) là đặc tả hành vi, chưa claim model benchmark. Copy starter vào workspace phiên riêng để làm bài.

## Gọi mỗi ngày

Dùng $master-iuh-daily-learning để tự soạn bài hôm nay: Việt và Anh đầy đủ, mặc định 90 phút, nhánh sâu 180+ phút tùy chọn. Mọi bài tập có lời giải; làm/nộp bài tùy chọn. Không cần nộp bài hôm trước để đọc bài mới. Tiến độ/mastery vẫn chỉ theo bằng chứng thật.

## Bài học đã xuất bản

- [Bài 01 — Big-O và cấu trúc dữ liệu](lessons/2026-10-05-cost-model/lesson.md)

Bài song ngữ và lab dùng chung có thể commit/publish theo yêu cầu. Catalog công khai liệt kê chính xác các file được deploy; state, bài làm và đánh giá cá nhân luôn ở workspace riêng.
