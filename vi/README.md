# Computer Science Learning Agent

[English](../README.md) · [Tiếng Việt](README.md)

Một AI learning agent mã nguồn mở dành cho việc học Khoa học Máy tính theo hướng có cấu trúc, thích nghi và tập trung vào thực hành.

Project biến nội dung chương trình đào tạo thành một learning workflow thích nghi: chọn topic đúng prerequisite, tránh lặp lại không cần thiết, tạo bài học tập trung từ nguồn đáng tin cậy, áp dụng retrieval practice và lưu tiến độ học xuyên suốt các phiên.

## Tài liệu

Website tài liệu song ngữ sử dụng Docsify và được deploy bằng GitHub Pages.

- **English:** https://nguyenan97.github.io/computer-science-learning-agent/#/
- **Tiếng Việt:** https://nguyenan97.github.io/computer-science-learning-agent/#/vi/

Website chủ động sử dụng Docsify **hash routing** vì được host dưới dạng GitHub Project Pages.

## Kiến trúc đa ngôn ngữ

English là canonical authoring language cho curriculum facts. Tài liệu tiếng Việt được duy trì như bản mirror dành cho người đọc trong thư mục `vi/`.

Navigation tuân theo cơ chế multilingual native của Docsify:

- `_sidebar.md` và `vi/_sidebar.md` **chỉ chứa navigation của tài liệu**.
- `_navbar.md` và `vi/_navbar.md` chịu trách nhiệm cho **language switcher**.
- `loadNavbar: true` bật top navigation.
- `navbarPreservePath: true` giữ trang tương ứng khi đổi ngôn ngữ.
- Markdown navigation sử dụng Docsify route như `/references/pedagogy` và `/vi/references/pedagogy`; **không hard-code `#/...`** trong `_sidebar.md` hoặc `_navbar.md`.
- Docsify tự chuyển các route này thành hash URL trên browser.
- `fallbackLanguages: ['vi']` cho phép route tiếng Việt chưa có bản dịch fallback về canonical English document.

Repository vẫn giữ `404.html` để xử lý các physical deep link vô tình được mở trực tiếp trên GitHub Pages.

## Cấu trúc repository

```text
computer-science-learning-agent/
├── README.md
├── index.html
├── 404.html
├── _404.md
├── _sidebar.md
├── _navbar.md
├── curricula/
│   └── iuh/
│       ├── master/curriculum.md
│       └── phd/curriculum.md
├── references/
│   ├── curriculum-map.md
│   ├── pedagogy.md
│   ├── source-policy.md
│   └── lesson-template.md
├── state/
│   └── learning-ledger.md
├── scripts/
│   ├── generate_curriculum_map.py
│   └── validate_docs_navigation.py
├── vi/
│   ├── README.md
│   ├── _404.md
│   ├── _sidebar.md
│   ├── _navbar.md
│   ├── curricula/iuh/
│   │   ├── master/curriculum.md
│   │   └── phd/curriculum.md
│   ├── references/
│   │   ├── curriculum-map.md
│   │   ├── pedagogy.md
│   │   ├── source-policy.md
│   │   └── lesson-template.md
│   └── state/
│       └── learning-ledger.md
└── .github/workflows/
    ├── pages.yml
    ├── validate-curriculum-map.yml
    └── validate-docs-navigation.yml
```

## Workflow học tập cốt lõi

1. Đọc curriculum và learning ledger hiện tại.
2. Chọn topic hữu ích có prerequisite đã được đáp ứng.
3. Tránh lặp lại nội dung gần đây trừ khi đến lịch spaced review.
4. Tạo bài học ngắn gọn từ nguồn có thẩm quyền.
5. Bao gồm retrieval practice, self-explanation và bài tập thực hành.
6. Ghi lại tiến độ để các bài học sau có thể thích nghi.

## Curriculum implementations

Learning engine được thiết kế curriculum-agnostic. Chương trình Thạc sĩ và Tiến sĩ Khoa học Máy tính IUH là các reference implementation đầu tiên, không phải identity cố định của project.

Các PDF curriculum ban đầu đã được chuyển thành Markdown rút gọn theo hướng phục vụ learning agent. Nội dung giữ lại program structure, course objective, core content, prerequisite, research component và các inconsistency đáng chú ý trong source.

- [IUH Master's curriculum](curricula/iuh/master/curriculum.md)
- [IUH PhD curriculum](curricula/iuh/phd/curriculum.md)

## Generated curriculum maps

Sinh lại đồng thời curriculum map English và Vietnamese bằng:

```bash
python scripts/generate_curriculum_map.py
```

Kiểm tra drift bằng:

```bash
python scripts/generate_curriculum_map.py --check
```

## Kiểm tra navigation

Trước khi commit thay đổi tài liệu/navigation, chạy:

```bash
python scripts/validate_docs_navigation.py
```

Validator kiểm tra:

- mọi internal route trong sidebar/navbar đều trỏ tới Markdown file thực tế;
- language switch nằm ở navbar, không nằm ở sidebar;
- sidebar English và Vietnamese luôn là route mirror của nhau;
- Docsify vẫn giữ hash routing, navbar loading và `navbarPreservePath`;
- không đưa hard-coded `#/...` trở lại navigation Markdown.

GitHub Actions tự động chạy validation này khi documentation thay đổi.

## License

Nên chọn project license trước khi khuyến khích external contribution. Các Markdown dẫn xuất từ curriculum công khai của IUH cần giữ source attribution rõ ràng.
