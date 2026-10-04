# Computer Science Learning Agent

[English](README.md) · [Tiếng Việt](vi/README.md)

An open-source AI learning agent for structured, adaptive, and practice-driven Computer Science education.

The project turns curriculum material into an adaptive learning workflow: select prerequisite-safe topics, avoid unnecessary repetition, generate focused lessons from reliable sources, apply retrieval practice, and persist learning progress across sessions.

## Documentation

The repository includes a bilingual Docsify documentation site deployed with GitHub Pages.

- **English:** https://nguyenan97.github.io/computer-science-learning-agent/#/
- **Tiếng Việt:** https://nguyenan97.github.io/computer-science-learning-agent/#/vi/

English is the default documentation language. The site uses **Docsify hash routing** because it is hosted as a GitHub Project Pages site. Documentation routes therefore use `#/...` rather than physical paths such as `/vi/`.

A custom GitHub Pages `404.html` also redirects accidental physical deep links back into the Docsify hash router.

## Language model

To avoid curriculum drift, the repository uses this ownership model:

- English curriculum files under `curricula/` are the canonical curriculum sources.
- Vietnamese files under `vi/` are maintained translations for readers.
- `references/curriculum-map.md` and `vi/references/curriculum-map.md` are generated from the same canonical curriculum model.
- Course codes, curriculum facts, prerequisite relationships, and documented source inconsistencies should be updated in the canonical curriculum first.

## Repository structure

```text
computer-science-learning-agent/
├── README.md                      # English home
├── index.html                     # Docsify bilingual site + EN/VI switcher
├── 404.html                       # GitHub Pages deep-link fallback
├── _404.md                        # English in-app not-found page
├── _sidebar.md                    # English navigation
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
    ├── README.md                  # Vietnamese home
    ├── _404.md
    ├── _sidebar.md               # Vietnamese navigation
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

## Core workflow

1. Inspect the curriculum and current learning ledger.
2. Select a useful topic whose prerequisites are satisfied.
3. Avoid recently repeated material unless spaced review is due.
4. Build a concise lesson from authoritative sources.
5. Include retrieval practice, self-explanation, and practical exercises.
6. Record learning progress so future lessons can adapt.

## Curriculum implementations

The learning engine is intentionally curriculum-agnostic. IUH Computer Science Master's and PhD curricula are included as the first reference implementations and source material, rather than defining the identity of the project.

The original curriculum PDFs have been converted into condensed, learning-oriented Markdown documents. They preserve program structure, course objectives, core content, prerequisite relationships, research components, and relevant source inconsistencies while intentionally omitting repetitive administrative material, lecturer contact details, grading matrices, and long bibliography sections.

- [IUH Master's curriculum](curricula/iuh/master/curriculum.md)
- [IUH PhD curriculum](curricula/iuh/phd/curriculum.md)

Additional universities, certification tracks, self-study roadmaps, or custom Computer Science curricula can be added without changing the core learning model.

## Generated curriculum maps

Run:

```bash
python scripts/generate_curriculum_map.py
```

to regenerate both English and Vietnamese dependency maps.

Validate committed maps with:

```bash
python scripts/generate_curriculum_map.py --check
```

GitHub Actions runs this check automatically when curriculum/model files change.

## Documentation stack

The web documentation uses [Docsify](https://docsify.js.org/) to render Markdown in the browser and GitHub Actions to deploy the repository to GitHub Pages. The `EN | VI` selector preserves the equivalent documentation path when switching languages.

## License

A project license should be selected before encouraging external contributions. Curriculum-derived Markdown is a condensed/transformative representation of public IUH curriculum material and should retain clear source attribution.
