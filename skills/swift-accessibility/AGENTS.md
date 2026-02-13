# AGENTS.md

This file provides guidance to AI coding agents working with the swift-accessibility skill.

## Skill Overview

This skill automatically detects and fixes accessibility issues in Swift projects. It supports both SwiftUI and UIKit, detecting the framework per-file.

## File Structure

- `SKILL.md` — Main skill definition with 5-phase workflow
- `rules/` — Individual detection and fix rules, one per issue category
  - `_sections.md` — Section index with priority ordering
  - `_template.md` — Template for adding new rules
  - `p0-*.md` — Critical priority rules
  - `p1-*.md` — High priority rules
  - `p2-*.md` — Medium priority rules
- `assets/` — Templates and checklists
  - `audit-template.swift` — XCTest accessibility audit template
  - `checklist.md` — Manual verification checklist
- `examples/` — Before/after transformation examples

## Adding a New Rule

1. Copy `rules/_template.md` to `rules/{priority}-{rule-name}.md`
2. Fill in all sections: detection patterns, fix logic, before/after examples
3. Add the rule to `rules/_sections.md` under the appropriate priority section
4. Update `SKILL.md` to reference the new rule in the appropriate phase
5. Add a before/after example to the relevant file in `examples/`

## Key Principles

- **Never overwrite** existing accessibility code
- **Add `[VERIFY]`** markers on inferred labels that need human review
- **Preserve formatting** — match the indentation and style of surrounding code
- **Detect framework per-file** — check for `import SwiftUI` vs `import UIKit`
- **Progressive disclosure** — SKILL.md stays concise; rules are loaded on-demand
