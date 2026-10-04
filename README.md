# Computer Science Learning Agent

An open-source AI learning agent for structured, adaptive, and practice-driven Computer Science education.

The project turns curriculum material into an adaptive learning workflow: select prerequisite-safe topics, avoid unnecessary repetition, generate focused lessons from reliable sources, apply retrieval practice, and persist learning progress across sessions.

## Documentation

The repository includes a Docsify documentation site deployed with GitHub Pages. Markdown files are rendered directly as a searchable web experience without a separate static-site build step.

Once GitHub Pages finishes its first deployment, the documentation is available at:

`https://nguyenan97.github.io/computer-science-learning-agent/`

## Repository structure

```text
computer-science-learning-agent/
├── README.md
├── SKILL.md
├── index.html
├── _sidebar.md
├── references/
│   ├── curriculum-map.md
│   ├── pedagogy.md
│   ├── source-policy.md
│   └── lesson-template.md
├── curricula/
│   └── iuh/
│       ├── master/
│       │   └── Curriculum-v2020.pdf
│       └── phd/
│           └── CTDT-TS-Khoa-hoc-may-tinh-2022-v5.pdf
├── docs/
│   ├── Master-IUH-Agent-Skills.md
│   └── IUH-PhD-CS-Agent-Skills.md
├── state/
│   └── learning-ledger.md
└── .github/workflows/pages.yml
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

Additional universities, certification tracks, self-study roadmaps, or custom Computer Science curricula can be added without changing the core learning model.

## Documentation stack

The web documentation uses [Docsify](https://docsify.js.org/) to render Markdown in the browser and GitHub Actions to deploy the repository to GitHub Pages.

## License

A project license should be selected before encouraging external contributions or redistribution of curriculum materials.
