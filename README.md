# Master IUH Computer Science Learning Agent

A reusable learning agent for the IUH Master's program in Computer Science.

This repository packages the curriculum, pedagogy, source-selection rules, lesson template, and learning-state conventions used by the agent. The goal is to generate one focused lesson at a time, avoid unnecessary repetition, adapt difficulty to the learner, and keep a persistent learning history.

## What is included

- `SKILL.md` — core agent instructions and lesson-selection workflow.
- `curriculum-map.md` — curriculum topics, prerequisites, and coverage map.
- `pedagogy.md` — learning-science principles used to design lessons.
- `source-policy.md` — source hierarchy and verification rules.
- `lesson-template.md` — standard lesson structure.
- `learning-ledger.md` — persistent learning-state template.
- `Master-IUH-Agent-Skills.md` — detailed Master's learning-agent specification.
- `IUH-PhD-CS-Agent-Skills.md` — PhD-oriented learning-agent specification.
- `Thạc-sĩ-Khoa-học-Máy-tính.txt` — program reference notes.
- `Curriculum-v2020.pdf` — Master's curriculum reference.
- `CTDT TS Khoa hoc may tinh 2022_v5.pdf` — PhD curriculum reference.

## Purpose

The project is designed as an AI-assisted learning system rather than a static collection of notes. The agent should:

1. Inspect the curriculum and learning ledger.
2. Select a topic that is useful, prerequisite-safe, and not recently repeated.
3. Build a concise lesson using reliable sources.
4. Include retrieval practice and practical exercises.
5. Record progress so future lessons can adapt.

## Usage

Use `SKILL.md` as the primary entry point for an Agent Skills-compatible coding agent. Keep the supporting Markdown files available in the same project so the agent can consult the curriculum, pedagogy, source policy, and learning ledger when generating lessons.

## Scope

The initial curriculum references are based on IUH Computer Science Master's and PhD programs, but the learning-agent structure is intended to be reusable and adaptable to other Computer Science curricula.
