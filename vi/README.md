# Computer Science Learning Agent

[English](../README.md) · [Tiếng Việt](README.md)

Một AI learning agent mã nguồn mở dành cho việc học Khoa học Máy tính theo hướng có cấu trúc, thích nghi và tập trung vào thực hành.

Project biến nội dung chương trình đào tạo thành một learning workflow thích nghi: chọn chủ đề đúng prerequisite, tránh lặp lại không cần thiết, tạo bài học tập trung từ nguồn đáng tin cậy, áp dụng retrieval practice và lưu tiến độ học xuyên suốt các phiên.

## Tài liệu

Repository sử dụng Docsify và GitHub Pages để hiển thị tài liệu Markdown dưới dạng website có thể tìm kiếm.

Trang tài liệu:

`https://nguyenan97.github.io/computer-science-learning-agent/`

English là ngôn ngữ mặc định. Phiên bản tiếng Việt nằm dưới route `/vi/`.

## Mô hình ngôn ngữ và source of truth

Để tránh curriculum drift, repository áp dụng quy tắc:

- Các file curriculum tiếng Anh trong `curricula/` là nguồn curriculum canonical.
- Các file trong `vi/` là bản dịch tiếng Việt phục vụ người đọc.
- `references/curriculum-map.md` và `vi/references/curriculum-map.md` được sinh từ cùng một canonical curriculum model.
- Course code, curriculum fact, prerequisite relationship và các source inconsistency phải được cập nhật ở canonical curriculum trước.

## Cấu trúc repository

```text
computer-science-learning-agent/
├── README.md                      # Trang chủ English
├── index.html                     # Docsify bilingual site
├── _sidebar.md                    # Điều hướng English
├── curricula/                     # Canonical curriculum sources (English)
│   └── iuh/
│       ├── master/curriculum.md
│       └── phd/curriculum.md
├── references/
│   ├── curriculum-map.md          # Generated dependency map - English
│   ├── pedagogy.md
│   ├── source-policy.md
│   └── lesson-template.md
├── state/
│   └── learning-ledger.md
├── scripts/
│   └── generate_curriculum_map.py
├── vi/                            # Vietnamese documentation mirror
│   ├── README.md
│   ├── _sidebar.md
│   ├── curricula/iuh/...
│   ├── references/...
│   └── state/learning-ledger.md
└── .github/workflows/
    ├── pages.yml
    └── validate-curriculum-map.yml
```

## Core workflow

1. Đọc curriculum và learning ledger hiện tại.
2. Chọn chủ đề có ích và đã thỏa prerequisite.
3. Tránh lặp lại nội dung gần đây trừ khi đến lịch spaced review.
4. Tạo một bài học ngắn gọn từ các nguồn có thẩm quyền.
5. Bao gồm retrieval practice, self-explanation và bài tập thực hành.
6. Ghi lại tiến độ để các bài học sau có thể thích nghi.

## Curriculum implementations

Learning engine được thiết kế độc lập với một trường cụ thể. Chương trình Thạc sĩ và Tiến sĩ Khoa học Máy tính của IUH là reference implementation đầu tiên, không phải identity cố định của project.

Hai PDF curriculum gốc đã được chuyển thành Markdown rút gọn theo hướng phục vụ học tập. Các file vẫn giữ program structure, course objective, core content, prerequisite relationship, research component và các điểm không nhất quán quan trọng của source; các phần hành chính lặp lại, thông tin liên hệ giảng viên, grading matrix và bibliography dài được lược bỏ.

- [Chương trình Thạc sĩ IUH](curricula/iuh/master/curriculum.md)
- [Chương trình Tiến sĩ IUH](curricula/iuh/phd/curriculum.md)

## Duy trì tài liệu song ngữ

Khi curriculum thay đổi:

1. Cập nhật canonical curriculum tiếng Anh.
2. Cập nhật bản dịch tiếng Việt tương ứng.
3. Chạy `python scripts/generate_curriculum_map.py`.
4. Chạy `python scripts/generate_curriculum_map.py --check`.
5. Review cả hai generated curriculum map trước khi commit.

## Documentation stack

Website dùng [Docsify](https://docsify.js.org/) để render Markdown trực tiếp trong trình duyệt và GitHub Actions để deploy lên GitHub Pages.

## License

Nên chọn project license trước khi khuyến khích đóng góp hoặc redistribution rộng rãi. Các Markdown được dẫn xuất từ curriculum IUH cần giữ attribution rõ ràng cho nguồn công khai ban đầu.
