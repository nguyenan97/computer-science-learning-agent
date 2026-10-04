# Computer Science Learning Agent

[English](../README.md) · [Tiếng Việt](README.md)

Một AI learning agent mã nguồn mở dành cho việc học Khoa học Máy tính theo hướng có cấu trúc, thích nghi và tập trung vào thực hành.

Project biến nội dung chương trình đào tạo thành một learning workflow thích nghi: chọn chủ đề đúng prerequisite, tránh lặp lại không cần thiết, tạo bài học tập trung từ nguồn đáng tin cậy, áp dụng retrieval practice và lưu tiến độ học xuyên suốt các phiên.

## Tài liệu

Repository sử dụng Docsify và GitHub Pages để hiển thị tài liệu Markdown dưới dạng website có thể tìm kiếm.

- **English:** https://nguyenan97.github.io/computer-science-learning-agent/#/
- **Tiếng Việt:** https://nguyenan97.github.io/computer-science-learning-agent/#/vi/

English là ngôn ngữ mặc định. Vì website được host dưới dạng **GitHub Project Pages**, Docsify sử dụng **hash routing**. Do đó route đúng của bản tiếng Việt là `#/vi/`, không phải physical path `/vi/`.

Repository cũng có `404.html` để redirect các physical deep link bị mở nhầm trở lại Docsify router.

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
├── index.html                     # Docsify bilingual + EN/VI switcher
├── 404.html                       # Fallback cho GitHub Pages deep link
├── _404.md                        # Trang not-found English trong Docsify
├── _sidebar.md                    # Điều hướng English
├── curricula/                     # Canonical curriculum sources (English)
│   └── iuh/
│       ├── master/curriculum.md
│       └── phd/curriculum.md
├── references/
│   ├── curriculum-map.md          # Generated English dependency map
│   ├── pedagogy.md
│   ├── source-policy.md
│   └── lesson-template.md
├── state/
│   └── learning-ledger.md
├── scripts/
│   └── generate_curriculum_map.py
└── vi/
    ├── README.md                  # Trang chủ Tiếng Việt
    ├── _404.md
    ├── _sidebar.md               # Điều hướng Tiếng Việt
    ├── curricula/iuh/
    │   ├── master/curriculum.md
    │   └── phd/curriculum.md
    ├── references/
    │   ├── curriculum-map.md      # Generated Vietnamese dependency map
    │   ├── pedagogy.md
    │   ├── source-policy.md
    │   └── lesson-template.md
    └── state/
        └── learning-ledger.md
```

## Workflow học tập cốt lõi

1. Đọc curriculum và learning ledger hiện tại.
2. Chọn topic hữu ích có prerequisite đã được đáp ứng.
3. Tránh lặp lại nội dung gần đây trừ khi đến lịch spaced review.
4. Tạo bài học ngắn gọn từ nguồn có thẩm quyền.
5. Bao gồm retrieval practice, self-explanation và bài tập thực hành.
6. Ghi lại tiến độ để các bài học sau có thể thích nghi.

## Curriculum implementations

Learning engine được thiết kế curriculum-agnostic. Chương trình Thạc sĩ và Tiến sĩ Khoa học Máy tính IUH là các implementation/reference đầu tiên, không phải identity cố định của project.

Các PDF curriculum ban đầu đã được chuyển thành Markdown rút gọn theo hướng phục vụ learning agent. Nội dung giữ lại program structure, course objective, core content, prerequisite, research component và các inconsistency đáng chú ý trong source; các phần hành chính lặp lại, thông tin giảng viên, grading matrix và bibliography dài được loại bỏ.

- [IUH Master's curriculum](curricula/iuh/master/curriculum.md)
- [IUH PhD curriculum](curricula/iuh/phd/curriculum.md)

Trong website Docsify, các link điều hướng tiếng Việt sử dụng explicit hash route `#/vi/...` để không thoát khỏi GitHub Project Pages base path.

## Generated curriculum maps

Chạy:

```bash
python scripts/generate_curriculum_map.py
```

để sinh lại đồng thời curriculum map English và Vietnamese.

Kiểm tra drift bằng:

```bash
python scripts/generate_curriculum_map.py --check
```

GitHub Actions tự động chạy check này khi curriculum/model thay đổi.

## Documentation stack

Website dùng Docsify để render Markdown trực tiếp trên browser và GitHub Actions để deploy GitHub Pages. Selector `EN | VI` giữ nguyên trang tài liệu tương ứng khi chuyển ngôn ngữ.

## License

Nên chọn project license trước khi khuyến khích external contribution. Các Markdown được dẫn xuất từ curriculum công khai của IUH cần giữ source attribution rõ ràng.
