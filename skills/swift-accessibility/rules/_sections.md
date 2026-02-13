# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Missing VoiceOver Labels (p0)

**Impact:** CRITICAL
**Description:** Images and icon-only buttons without accessibility labels are completely invisible to VoiceOver users. These are the highest-priority fixes.

## 2. Missing Context and Discoverability (p1)

**Impact:** HIGH
**Description:** Interactive elements missing hints, test identifiers, Voice Control input labels, adequate touch targets, or color-independent differentiation degrade the experience across VoiceOver, Voice Control, and Switch Control.

## 3. Visual, Interaction, and System Setting Compliance (p2)

**Impact:** MEDIUM
**Description:** Hardcoded font sizes break Dynamic Type. Insufficient contrast, ignored Reduce Motion and Bold Text settings, ungrouped elements, missing header traits, decorative elements exposed to VoiceOver, unannounced dynamic content, gesture-only interactions without accessible alternatives, and poor modal focus management all fail WCAG AA and Apple Accessibility Nutrition Label requirements.
