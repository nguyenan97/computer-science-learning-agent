# Computer Science Learning Agent

[English](README.md) · [Tiếng Việt](vi/README.md)

An open-source AI learning agent for structured, adaptive, and practice-driven Computer Science education.

The project turns curriculum material into an adaptive learning workflow: select prerequisite-safe topics, avoid unnecessary repetition, generate focused lessons from reliable sources, apply retrieval practice, and persist learning progress across sessions.

## Documentation

The bilingual documentation site is built with Docsify and deployed with GitHub Pages.

- **English:** https://nguyenan97.github.io/computer-science-learning-agent/#/
- **Tiếng Việt:** https://nguyenan97.github.io/computer-science-learning-agent/#/vi/

The site intentionally uses Docsify **hash routing** because it is hosted as GitHub Project Pages.

## Localization architecture

English is the canonical authoring language for curriculum facts. Vietnamese documentation is maintained as a reader-facing mirror under `vi/`.

Navigation follows Docsify's native multilingual pattern:

- `_sidebar.md` and `vi/_sidebar.md` contain **documentation navigation only**.
- `_navbar.md` and `vi/_navbar.md` own the **language switcher**.
- `loadNavbar: true` enables the top navigation.
- `navbarPreservePath: true` keeps the corresponding document when changing language.
- Navigation Markdown uses Docsify routes such as `/references/pedagogy` and `/vi/references/pedagogy`; do **not** hard-code `#/...` inside `_sidebar.md` or `_navbar.md`.
- Docsify converts those routes to hash URLs in the browser.
- `fallbackLanguages: ['vi']` lets an untranslated Vietnamese route fall back to the canonical English document instead of failing immediately.

The repository also keeps `404.html` as a GitHub Pages fallback for accidental physical deep links.

## Repository structure

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

## Core workflow

1. Inspect the curriculum and current learning ledger.
2. Select a useful topic whose prerequisites are satisfied.
3. Avoid recently repeated material unless spaced review is due.
4. Build a concise lesson from authoritative sources.
5. Include retrieval practice, self-explanation, and practical exercises.
6. Record learning progress so future lessons can adapt.

## Curriculum implementations

The learning engine is intentionally curriculum-agnostic. IUH Computer Science Master's and PhD curricula are included as the first reference implementations rather than defining the identity of the project.

The original curriculum PDFs have been converted into condensed, learning-oriented Markdown documents. They preserve program structure, course objectives, core content, prerequisite relationships, research components, and relevant source inconsistencies while omitting repetitive administrative material.

- [IUH Master's curriculum](curricula/iuh/master/curriculum.md)
- [IUH PhD curriculum](curricula/iuh/phd/curriculum.md)

## Generated curriculum maps

Regenerate both English and Vietnamese dependency maps with:

```bash
python scripts/generate_curriculum_map.py
```

Validate them with:

```bash
python scripts/generate_curriculum_map.py --check
```

## Navigation validation

Before committing documentation/navigation changes, run:

```bash
python scripts/validate_docs_navigation.py
```

The validator checks that:

- every internal sidebar/navbar route resolves to a real Markdown file;
- language switching exists in the navbar, not the sidebar;
- English and Vietnamese sidebars remain route mirrors;
- Docsify keeps hash routing, navbar loading, and `navbarPreservePath` enabled;
- hard-coded `#/...` links do not re-enter navigation Markdown.

GitHub Actions runs this validation automatically for documentation changes.

## License

A project license should be selected before encouraging external contributions. Curriculum-derived Markdown is a condensed representation of public IUH curriculum material and should retain clear source attribution.
