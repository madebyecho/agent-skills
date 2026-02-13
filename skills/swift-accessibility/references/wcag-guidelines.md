# WCAG 2.1 AA & Apple HIG Accessibility Reference

Quick reference for WCAG 2.1 Level AA requirements mapped to iOS/macOS implementation.

---

## WCAG Principles (POUR)

### 1. Perceivable

| Guideline | Requirement | iOS Implementation |
|-----------|-------------|-------------------|
| 1.1.1 Non-text Content | All images need text alternatives | `accessibilityLabel` on images; `.accessibilityHidden(true)` on decorative images |
| 1.3.1 Info and Relationships | Structure conveyed programmatically | `accessibilityTraits = .header`; `.accessibilityElement(children: .combine)` |
| 1.3.4 Orientation | Content not restricted to single orientation | Support both portrait and landscape |
| 1.4.1 Use of Color | Color not sole means of conveying info | Pair color with icons, text, or patterns |
| 1.4.3 Contrast (Minimum) | 4.5:1 for normal text, 3:1 for large text | See contrast section below |
| 1.4.4 Resize Text | Text scales up to 200% | Dynamic Type with `preferredFont` / semantic `.font()` styles |
| 1.4.10 Reflow | Content reflows without horizontal scrolling at 320px | Flexible layouts; avoid fixed widths |
| 1.4.11 Non-text Contrast | 3:1 for UI components and graphics | Borders, icons, and focus indicators meet contrast |

### 2. Operable

| Guideline | Requirement | iOS Implementation |
|-----------|-------------|-------------------|
| 2.1.1 Keyboard | All functionality via keyboard | Full VoiceOver navigation; `accessibilityAction` for custom gestures |
| 2.4.3 Focus Order | Logical navigation order | `.accessibilitySortPriority`; proper view hierarchy |
| 2.4.6 Headings and Labels | Headings describe content | `.accessibilityAddTraits(.isHeader)` on section headings |
| 2.5.5 Target Size | Minimum 44x44 points | Ensure all touch targets meet minimum; use `accessibilityFrame` to expand |

### 3. Understandable

| Guideline | Requirement | iOS Implementation |
|-----------|-------------|-------------------|
| 3.2.1 On Focus | No unexpected changes on focus | Don't trigger actions on VoiceOver focus |
| 3.3.1 Error Identification | Errors described in text | Announce errors via `UIAccessibility.post(notification: .announcement)` |
| 3.3.2 Labels or Instructions | Form inputs have labels | `accessibilityLabel` on all form fields |

### 4. Robust

| Guideline | Requirement | iOS Implementation |
|-----------|-------------|-------------------|
| 4.1.2 Name, Role, Value | Elements have name + role + state | `accessibilityLabel` + `accessibilityTraits` + `accessibilityValue` |
| 4.1.3 Status Messages | Status changes announced | `UIAccessibility.post(notification:)` for dynamic updates |

---

## Contrast Ratios

### Requirements

| Text Type | Minimum Ratio | Definition |
|-----------|--------------|------------|
| Normal text (< 18pt or < 14pt bold) | **4.5:1** | Most body text, labels, buttons |
| Large text (>= 18pt or >= 14pt bold) | **3:1** | Headings, large labels |
| UI components & graphical objects | **3:1** | Icons, borders, form field outlines |

### Common iOS Color Pairs to Flag

These system colors generally pass, but custom colors should be verified:

| Foreground | Background | Approx Ratio | Pass? |
|-----------|------------|-------------|-------|
| `.label` | `.systemBackground` | ~21:1 (light) / ~16:1 (dark) | Yes |
| `.secondaryLabel` | `.systemBackground` | ~5.5:1 (light) / ~5:1 (dark) | Yes |
| `.tertiaryLabel` | `.systemBackground` | ~2.5:1 | **No** for normal text |
| `.quaternaryLabel` | `.systemBackground` | ~1.7:1 | **No** |
| `.systemGray` | `.systemBackground` | ~3.5:1 | **No** for normal text |
| `.systemGray2` | `.systemBackground` | ~2.8:1 | **No** |

### Detection Strategy

```
# Flag custom colors and hardcoded hex values for manual contrast review
grep -n 'UIColor(red:\|UIColor(hex:\|Color(red:\|Color(hex:\|#[0-9a-fA-F]{6}' *.swift
grep -n '\.tertiaryLabel\|\.quaternaryLabel\|\.systemGray[^2-6]' *.swift
```

### Recommendation

- Use semantic system colors (`.label`, `.secondaryLabel`, `.systemBackground`) which auto-adapt to Dark Mode and Increase Contrast settings
- Flag all custom/hardcoded colors for manual contrast verification
- Test with Settings > Accessibility > Increase Contrast enabled

---

## Touch Target Minimums

### Requirements

- **Minimum**: 44x44 points (Apple HIG)
- **WCAG 2.5.5 Enhanced**: 44x44 CSS pixels (equivalent to points on iOS)

### Detection

```
# Small frame sizes that may violate minimum
grep -n '\.frame(width:.*height:' *.swift
# Check if width or height < 44 on interactive elements
```

### Fix Strategies

**SwiftUI**:
```swift
// Expand tap area without changing visual size
Button(action: { }) {
    Image(systemName: "xmark")
        .font(.caption)
}
.frame(minWidth: 44, minHeight: 44)

// Or use contentShape
Image(systemName: "xmark")
    .frame(width: 16, height: 16)
    .contentShape(Rectangle().size(width: 44, height: 44))
```

**UIKit**:
```swift
// Override point(inside:with:) or expand accessibilityFrame
button.accessibilityFrame = largerFrame
```

---

## Apple Human Interface Guidelines — Accessibility Principles

### Best Practices Summary

1. **Support VoiceOver**: Every meaningful element has a label; every interactive element has a hint
2. **Support Dynamic Type**: All text uses preferred fonts or scales with `UIFontMetrics`
3. **Don't rely on color alone**: Use icons, patterns, or text alongside color indicators
4. **Provide sufficient contrast**: 4.5:1 for normal text, 3:1 for large text and UI components
5. **Respect user settings**: Honor Bold Text, Reduce Motion, Reduce Transparency, Increase Contrast
6. **Support full keyboard access**: Ensure all features work with external keyboards and Switch Control
7. **Use semantic traits**: Mark headers, buttons, links, and adjustable controls with appropriate traits
8. **Group related content**: Combine related elements to reduce VoiceOver navigation complexity

### Motion and Animation

```swift
// Respect Reduce Motion
if UIAccessibility.isReduceMotionEnabled {
    // Use simple transitions instead of complex animations
}

// SwiftUI
@Environment(\.accessibilityReduceMotion) var reduceMotion
```

### Bold Text

```swift
// UIKit: Respond to bold text changes
NotificationCenter.default.addObserver(
    self,
    selector: #selector(boldTextChanged),
    name: UIAccessibility.boldTextStatusDidChangeNotification,
    object: nil
)
```

### Increase Contrast

```swift
// Check and respond to Increase Contrast
if UIAccessibility.isDarkerSystemColorsEnabled {
    // Use higher contrast color variants
}

// SwiftUI
@Environment(\.colorSchemeContrast) var contrast
```

---

## Comprehensive Checklist

Use this checklist for manual verification after automated fixes:

### VoiceOver
- [ ] Every screen is fully navigable with VoiceOver
- [ ] All interactive elements announce their purpose
- [ ] All images have appropriate labels or are hidden
- [ ] Navigation order is logical
- [ ] No duplicate or redundant announcements
- [ ] Dynamic content changes are announced
- [ ] Custom gestures have accessible alternatives

### Dynamic Type
- [ ] All text scales from xSmall to AX5 (largest accessibility size)
- [ ] No text is truncated or clipped at large sizes
- [ ] Layout adapts (e.g., HStack becomes VStack at large sizes)
- [ ] Images and icons scale appropriately

### Color and Contrast
- [ ] All text meets 4.5:1 (normal) or 3:1 (large) contrast ratio
- [ ] Color is not the only way to convey information
- [ ] UI works in both Light and Dark modes
- [ ] UI works with Increase Contrast enabled

### Touch Targets
- [ ] All interactive elements are at least 44x44 points
- [ ] Adequate spacing between adjacent targets

### System Settings
- [ ] Bold Text is respected
- [ ] Reduce Motion is respected (no unnecessary animation)
- [ ] Reduce Transparency is respected
- [ ] Switch Control navigation works
