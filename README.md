# Agent Skills

Echo Studio's official collection of agent skills for AI coding agents. Skills are packaged instructions and reference material that extend agent capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Available Skills

### swift-accessibility

Automatically applies accessibility best practices to Swift projects (SwiftUI and UIKit). Scans code, detects missing VoiceOver labels, Dynamic Type issues, and WCAG violations, then applies fixes and generates XCTest audit code.

**Use when:**
- Working on iOS/macOS projects that need accessibility support
- Adding VoiceOver, Voice Control, or Dynamic Type support
- Running an accessibility audit or preparing for App Store Accessibility Nutrition Labels
- Reviewing Swift code for a11y or WCAG AA compliance issues

**Covers all 9 Apple Accessibility Nutrition Label categories:**
- VoiceOver (labels, hints, traits, grouping, focus, announcements)
- Voice Control (input labels, name matching)
- Larger Text / Dynamic Type (semantic fonts, scaling)
- Sufficient Contrast (WCAG AA ratios, Light/Dark mode, Increase Contrast)
- Dark Interface (contrast in both modes)
- Differentiate Without Color Alone (icons/text alongside color)
- Reduced Motion (animation alternatives)
- Bold Text (custom font adaptation)
- Touch Targets (44x44pt minimum)

**16 rules across 3 priority levels** with auto-detection and fix patterns for both SwiftUI and UIKit.

## Installation

```bash
npx skills add madebyecho/agent-skills
```

## Usage

Skills are automatically available once installed. The agent will use them when relevant tasks are detected.

**Examples:**
```
Make this project accessible
```
```
Add VoiceOver support to my SwiftUI views
```
```
Run an accessibility audit on my iOS app
```
```
Fix Dynamic Type issues
```

## Skill Structure

Each skill contains:
- `SKILL.md` - Instructions for the agent
- `rules/` - Individual detection and fix rules (optional)
- `assets/` - Templates and scripts for automation (optional)
- `examples/` - Before/after transformation examples (optional)

## License

MIT
