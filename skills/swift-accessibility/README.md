# Swift Accessibility Skill

Automatically applies accessibility best practices to Swift projects (SwiftUI and UIKit).

When invoked, it scans your codebase, detects missing accessibility properties, applies fixes, and generates XCTest audit code — so your app works with VoiceOver, Dynamic Type, and meets WCAG AA standards.

## What It Does

1. **Scans** your Swift files and detects SwiftUI vs UIKit
2. **Identifies** accessibility issues by priority (P0 Critical → P3 Low)
3. **Applies fixes** — adds VoiceOver labels, hints, identifiers, Dynamic Type support
4. **Generates tests** — creates an XCTest file with `performAccessibilityAudit()` calls
5. **Reports** — summary of changes, items needing manual review, and a verification checklist

## Issues Detected

| Priority | Category | Examples |
|----------|----------|---------|
| P0 Critical | Missing labels | Images without labels, icon-only buttons |
| P1 High | Missing context | No hints on interactive elements, no test identifiers |
| P2 Medium | Compliance | Hardcoded font sizes, ungrouped elements, missing header traits |
| P3 Low | Polish | Missing VoiceOver announcements, custom rotor opportunities |

## Modes

- **Standard** (default): Fixes P0 and P1 issues, reports P2 and P3
- **Comprehensive**: Fixes all priority levels

## Safety

- Never overwrites existing accessibility code
- Adds `[VERIFY]` comment markers on inferred labels that need human review
- Preserves your code's formatting and style

## Examples

See the `examples/` directory for full before/after transformations:

- [SwiftUI Examples](examples/before-after-swiftui.md)
- [UIKit Examples](examples/before-after-uikit.md)
