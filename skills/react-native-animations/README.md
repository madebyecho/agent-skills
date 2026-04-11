# React Native Animations Skill

A motion design and animation engineering philosophy for React Native apps using **Reanimated**, **Gesture Handler**, and **Skia** — the three libraries that make mobile motion feel native in 2026.

This is a guidance skill, not an audit skill. It encodes taste and a decision framework rather than rule-based detection.

## What It Covers

1. **Foundational philosophy** — motion serves the spatial model, the UI thread is sacred, match device physics
2. **Animation decision framework** — four questions: should this animate? / purpose? / easing? / duration?
3. **The Reanimated mental model** — shared values, worklets, `useAnimatedStyle`, `withTiming` / `withSpring`, layout animations
4. **Gesture-driven animation** — Gesture Handler v2, pan-to-dismiss, bottom sheet snap, pinch+pan+rotate composition
5. **Layout animations** — `FadeIn`, `SlideIn*`, `LinearTransition`, shared element transitions
6. **Skia for advanced motion** — canvas, paths, shaders, `usePathInterpolation`, animated images
7. **Performance rules** — UI thread discipline, transform-only animations, gesture coordination
8. **Accessibility** — `useReducedMotion`, `ReducedMotionConfig`, `.reduceMotion()` modifier, decision matrix
9. **Component patterns** — pressable feedback, toasts, bottom sheets, pull-to-refresh, skeleton shimmer, hero transitions
10. **Anti-patterns** — the common mistakes that sabotage mobile motion

## What It Doesn't Cover

- The legacy `Animated` API from `react-native` core (JS-thread-driven)
- Moti, Lottie, or other animation libraries
- Rule-based audit detection (use `react-native-accessibility` for motion-related WCAG checks)

## How To Use

Invoke the skill in any conversation where you're building or reviewing React Native animation code. The agent will reference this skill's decision framework to choose easing curves, durations, and library primitives, and will produce code that runs on the UI thread by default.

For audit-mode detection of Reduce Motion violations, cross-reference the `react-native-accessibility` skill's `p2-reduce-motion-ignored` rule.

## Installation

**Claude Code:**
```bash
cp -r skills/react-native-animations ~/.claude/skills/
```

**claude.ai:**
Add the skill to project knowledge or paste `SKILL.md` contents into the conversation.

## Supporting Files

- `SKILL.md` — Main skill file
- `references/reanimated-patterns.md` — Reanimated API recipes
- `references/gesture-handler-patterns.md` — Gesture composition recipes
- `references/skia-animation-patterns.md` — Skia canvas animation recipes
- `references/easing-and-timing.md` — Consolidated easing / duration / spring reference
- `references/accessibility.md` — Reduce Motion integration patterns
- `assets/decision-flowchart.md` — One-page decision tree
- `assets/performance-checklist.md` — Pre-ship verification checklist
