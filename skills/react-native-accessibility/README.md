# React Native Accessibility Skill

Automatically applies accessibility best practices to React Native and Expo projects.

When invoked, it scans your codebase, detects missing accessibility properties, applies fixes, and generates Jest test code — so your app works with VoiceOver (iOS), TalkBack (Android), and meets WCAG AA standards.

## What It Does

1. **Scans** your React Native/Expo files and detects project type (Expo managed vs bare RN)
2. **Identifies** accessibility issues by priority (P0 Critical → P2 Medium)
3. **Applies fixes** — adds screen reader labels, roles, hints, touch targets, font scaling
4. **Generates tests** — creates a Jest file with `@testing-library/react-native` accessibility queries
5. **Reports** — summary of changes, items needing manual review, and a verification checklist

## Issues Detected

| Priority | Category | Examples |
|----------|----------|---------|
| P0 Critical | Missing labels | Images without labels, icon-only pressable elements |
| P1 High | Missing context | No hints, missing roles, small touch targets, color-only info |
| P2 Medium | Compliance | Disabled font scaling, ungrouped elements, no reduce-motion check |

## Platform Support

- **iOS**: VoiceOver, Dynamic Type, Reduce Motion
- **Android**: TalkBack, Font Size scaling, Remove Animations
- **Expo**: Managed and bare workflows

## Modes

- **Standard** (default): Fixes P0 and P1 issues, reports P2
- **Comprehensive**: Fixes all priority levels

## Safety

- Never overwrites existing accessibility code
- Adds `[VERIFY]` comment markers on inferred labels that need human review
- Preserves your code's formatting and style

## Examples

See the `examples/` directory for full before/after transformations:

- [Expo Examples](examples/before-after-expo.md)
- [Bare React Native Examples](examples/before-after-bare-rn.md)
