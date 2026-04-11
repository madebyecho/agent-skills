# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Missing Screen Reader Labels (p0)

**Impact:** CRITICAL
**Description:** Images, SVG icons, and icon-only pressable elements without accessibility labels are completely invisible to VoiceOver and TalkBack users. These are the highest-priority fixes.

## 2. Missing Context and Discoverability (p1)

**Impact:** HIGH
**Description:** Interactive elements missing hints, roles, input labels, adequate touch targets, or color-independent information degrade the experience for screen reader, Switch Access, and Voice Control users.

## 3. Visual, Interaction, and System Setting Compliance (p2)

**Impact:** MEDIUM
**Description:** Disabled font scaling breaks Dynamic Type and Android font preferences. Ungrouped elements, missing header roles, decorative elements exposed to the accessibility tree, insufficient contrast, ignored reduce-motion preferences, missing custom actions, unannounced dynamic content, and poor modal focus management all fail WCAG AA requirements.
