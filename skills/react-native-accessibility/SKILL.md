---
name: react-native-accessibility
description: >
  Automatically applies accessibility best practices to React Native and Expo
  projects. Use when working on mobile apps that need VoiceOver (iOS) or
  TalkBack (Android) support, WCAG compliance, or accessibility audits.
  Triggers on React Native accessibility tasks, a11y improvements, or when the
  user mentions accessibility, VoiceOver, TalkBack, or screen reader support.
license: MIT
metadata:
  author: madebyecho
  version: "1.0.0"
---

# React Native Accessibility

Scan, fix, and audit accessibility in React Native and Expo projects. Detects missing screen reader labels, roles, hints, font scaling issues, WCAG violations, and generates Jest test code. Supports both iOS (VoiceOver) and Android (TalkBack) with platform-specific considerations per rule.

## When to Apply

Reference these guidelines when:
- Working on React Native or Expo projects that need accessibility support
- Adding VoiceOver (iOS) or TalkBack (Android) support
- Running an accessibility audit or a11y review
- Fixing font scaling, contrast, or WCAG compliance issues
- Preparing a mobile app for accessibility compliance

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Missing Screen Reader Labels | CRITICAL | `p0-` |
| 2 | Missing Context and Discoverability | HIGH | `p1-` |
| 3 | Visual, Interaction, and System Setting Compliance | MEDIUM | `p2-` |

## Quick Reference

### 1. Missing Screen Reader Labels (CRITICAL)

- `p0-images-without-labels` — Images, ExpoImage, and SVG icons without `accessibilityLabel`
- `p0-icon-only-pressables` — Pressable/TouchableOpacity wrapping only an icon with no label

### 2. Missing Context and Discoverability (HIGH)

- `p1-missing-hints` — Interactive elements without `accessibilityHint`
- `p1-missing-roles` — Pressable/Touchable without `accessibilityRole`
- `p1-missing-input-labels` — `TextInput` without `accessibilityLabel`
- `p1-small-touch-targets` — Interactive elements below 48x48 dp minimum
- `p1-color-only-information` — Color as the sole means of conveying information

### 3. Visual, Interaction, and System Setting Compliance (MEDIUM)

- `p2-font-scaling-disabled` — `allowFontScaling={false}` or low `maxFontSizeMultiplier`
- `p2-ungrouped-elements` — Related elements (icon + text) not grouped for screen readers
- `p2-missing-header-roles` — Section titles without `accessibilityRole="header"`
- `p2-decorative-elements-exposed` — Decorative images/separators in the accessibility tree
- `p2-contrast-insufficient` — Colors that fail WCAG AA contrast ratios
- `p2-reduce-motion-ignored` — Animations without reduce-motion check
- `p2-custom-actions-missing` — Swipe/long-press gestures without `accessibilityActions`
- `p2-live-region-missing` — Dynamic content updates not announced to screen readers
- `p2-modal-focus-management` — Custom modals without focus trapping or background hiding

## WCAG AA Coverage

| WCAG Criterion | Rules Covering It |
|---------------|-------------------|
| 1.1.1 Non-text Content | p0-images-without-labels, p0-icon-only-pressables, p2-decorative-elements-exposed |
| 1.3.1 Info and Relationships | p2-ungrouped-elements, p2-missing-header-roles |
| 1.4.1 Use of Color | p1-color-only-information |
| 1.4.3 Contrast (Minimum) | p2-contrast-insufficient |
| 1.4.4 Resize Text | p2-font-scaling-disabled |
| 2.5.5 Target Size | p1-small-touch-targets |
| 4.1.2 Name, Role, Value | p1-missing-roles, p1-missing-hints, p1-missing-input-labels |
| 4.1.3 Status Messages | p2-live-region-missing |

## Workflow

Execute these 5 phases in order. Load rule files on-demand — only read a rule when its content is needed for the current phase.

### Phase 1: Project Discovery

1. Check for `app.json` or `app.config.js`/`app.config.ts` to determine if this is an Expo project
2. Glob for `**/*.{tsx,jsx,ts,js}` to find all React Native source files
3. Identify navigation library: `@react-navigation/*`, `expo-router`, etc.
4. Grep for existing accessibility usage to understand current coverage:
   - `accessibilityLabel`, `accessibilityHint`, `accessibilityRole`
   - `accessibilityState`, `accessibilityValue`, `accessibilityActions`
   - `accessibilityLiveRegion`, `accessibilityViewIsModal`
   - `accessible={false}`, `importantForAccessibility`
5. Report: total files, Expo vs bare RN, navigation library, current accessibility coverage percentage

### Phase 2: Issue Detection

Scan files for anti-patterns. Read rules from `rules/` directory for detection patterns.

For each issue found, record: file path, line number, priority, description, and suggested fix.

### Phase 3: Automated Fixes

Apply fixes using Edit tool, following these rules:

1. **Never overwrite** existing accessibility code — only add missing properties
2. **Add `[VERIFY]` comment markers** on generated labels where semantic accuracy needs human review:
   ```tsx
   accessibilityLabel="Settings icon" // [VERIFY] confirm label matches intent
   ```
3. **Preserve formatting** — match the indentation and style of surrounding code
4. **Group related fixes** — apply all fixes to a single element together

Fix application order:
1. P0 Critical fixes first
2. P1 High fixes
3. P2 Medium fixes (comprehensive mode only)

### Phase 4: Test Generation

Load `assets/jest-a11y-test-template.tsx` and generate a Jest test file for the project.

1. Create `accessibility.test.tsx` in the project's test directory
2. Add a test case for each screen/component that was modified
3. Use `@testing-library/react-native` with accessibility queries
4. Include setup for navigation context if needed

Match the project's existing test framework and patterns.

### Phase 5: Report

Output a structured summary:

```
## Accessibility Audit Report

### Issues Found
| Priority | Category | Count |
|----------|----------|-------|
| P0 Critical | ... | ... |
| P1 High | ... | ... |
| P2 Medium | ... | ... |

### Changes Applied
- **Files modified**: [list]
- **Issues fixed**: [count] of [total]
- **Test file generated**: [path]

### Platform Coverage
| Feature | iOS (VoiceOver) | Android (TalkBack) |
|---------|-----------------|-------------------|
| Screen reader labels | Ready / Needs Work | Ready / Needs Work |
| Roles and hints | Ready / Needs Work | Ready / Needs Work |
| Touch targets | Ready / Needs Work | Ready / Needs Work |
| Font scaling | Ready / Needs Work | Ready / Needs Work |
| Reduce motion | Ready / Needs Work | Ready / Needs Work |

### Manual Review Required
Items marked with [VERIFY] that need human confirmation:
- [list of VERIFY items with file:line references]

### Next Steps
- [ ] Run VoiceOver testing on iOS (see assets/checklist.md)
- [ ] Run TalkBack testing on Android (see assets/checklist.md)
- [ ] Review [VERIFY] markers and update labels
- [ ] Run generated accessibility tests
- [ ] Test with maximum system font size on both platforms
- [ ] Test with Reduce Motion enabled on both platforms
- [ ] Verify color contrast with a contrast checker tool
```

## Configuration

- **Standard mode** (default): Fixes P0 and P1 issues, reports P2
- **Comprehensive mode**: Fixes all priority levels — invoke with "comprehensive" or "full audit"

## Supporting Files

Loaded on-demand during execution:

- `rules/` — Individual detection and fix rules per issue category (16 rules)
- `references/react-native-a11y-api.md` — Full React Native accessibility API catalog
- `references/platform-differences.md` — iOS vs Android accessibility behavior differences
- `references/wcag-guidelines.md` — WCAG AA and platform guideline reference
- `assets/jest-a11y-test-template.tsx` — Jest accessibility test template
- `assets/checklist.md` — Manual verification checklist for both platforms
