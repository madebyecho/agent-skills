# AGENTS.md

This file provides guidance to AI coding agents working with the react-native-accessibility skill.

## Skill Overview

This skill automatically detects and fixes accessibility issues in React Native and Expo projects. It supports both iOS (VoiceOver) and Android (TalkBack), with platform-specific considerations noted per rule.

## File Structure

- `SKILL.md` — Main skill definition with 5-phase workflow
- `rules/` — Individual detection and fix rules, one per issue category
  - `_sections.md` — Section index with priority ordering
  - `_template.md` — Template for adding new rules
  - `p0-*.md` — Critical priority rules (2 rules)
  - `p1-*.md` — High priority rules (5 rules)
  - `p2-*.md` — Medium priority rules (9 rules)
- `assets/` — Templates and checklists
  - `jest-a11y-test-template.tsx` — Jest accessibility test template
  - `checklist.md` — Manual verification checklist for both platforms
- `examples/` — Before/after transformation examples
  - `before-after-expo.md` — Expo managed workflow examples
  - `before-after-bare-rn.md` — Bare React Native examples
- `references/` — API and guideline reference material
  - `react-native-a11y-api.md` — Full React Native accessibility API catalog
  - `platform-differences.md` — iOS vs Android behavior differences
  - `wcag-guidelines.md` — WCAG AA and platform guideline reference

## Adding a New Rule

1. Copy `rules/_template.md` to `rules/{priority}-{rule-name}.md`
2. Fill in all sections: detection patterns, fix logic, before/after examples, platform considerations
3. Add the rule to `rules/_sections.md` under the appropriate priority section
4. Update `SKILL.md` to reference the new rule in the Quick Reference section
5. Add a before/after example to the relevant file in `examples/`

## Key Principles

- **Never overwrite** existing accessibility code
- **Add `[VERIFY]`** markers on inferred labels that need human review
- **Preserve formatting** — match the indentation and style of surrounding code
- **Detect project type** — check for `app.json`/`app.config.js` (Expo) vs bare RN
- **Platform-aware fixes** — include both `accessibilityElementsHidden` (iOS) and `importantForAccessibility` (Android) when hiding elements
- **Progressive disclosure** — SKILL.md stays concise; rules and references are loaded on-demand
- **48x48 dp minimum** — use as the unified touch target minimum (satisfies both iOS 44pt and Android 48dp)
