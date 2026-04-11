# WCAG 2.1 AA & Mobile Accessibility Reference

Quick reference for WCAG 2.1 Level AA requirements mapped to React Native implementation.

---

## WCAG Principles (POUR)

### 1. Perceivable

| Guideline | Requirement | React Native Implementation |
|-----------|-------------|---------------------------|
| 1.1.1 Non-text Content | All images need text alternatives | `accessibilityLabel` on images; `accessible={false}` on decorative images |
| 1.3.1 Info and Relationships | Structure conveyed programmatically | `accessibilityRole="header"`; `accessible={true}` to group related elements |
| 1.3.4 Orientation | Content not restricted to single orientation | Support both portrait and landscape in `app.json` |
| 1.4.1 Use of Color | Color not sole means of conveying info | Pair color with icons, text, or patterns |
| 1.4.3 Contrast (Minimum) | 4.5:1 for normal text, 3:1 for large text | See contrast section below |
| 1.4.4 Resize Text | Text scales up to 200% | Keep `allowFontScaling={true}` (default); `maxFontSizeMultiplier >= 2.0` |
| 1.4.10 Reflow | Content reflows without horizontal scrolling | Flexible layouts with `flex`; avoid fixed widths |
| 1.4.11 Non-text Contrast | 3:1 for UI components and graphics | Borders, icons, and focus indicators meet contrast |

### 2. Operable

| Guideline | Requirement | React Native Implementation |
|-----------|-------------|---------------------------|
| 2.1.1 Keyboard | All functionality via assistive technology | Full screen reader navigation; `accessibilityActions` for custom gestures |
| 2.4.3 Focus Order | Logical navigation order | Proper component hierarchy; avoid absolute positioning that breaks order |
| 2.4.6 Headings and Labels | Headings describe content | `accessibilityRole="header"` on section headings |
| 2.5.5 Target Size | Minimum 48x48 dp | Ensure all touch targets meet minimum; use `hitSlop` to expand |
| 2.5.8 Target Size (Minimum) | At least 24x24 CSS pixels | Exceeding with 48dp satisfies this criterion |

### 3. Understandable

| Guideline | Requirement | React Native Implementation |
|-----------|-------------|---------------------------|
| 3.2.1 On Focus | No unexpected changes on focus | Don't trigger actions when screen reader focuses an element |
| 3.3.1 Error Identification | Errors described in text | Announce errors via `AccessibilityInfo.announceForAccessibility()` or `accessibilityLiveRegion` |
| 3.3.2 Labels or Instructions | Form inputs have labels | `accessibilityLabel` on all `TextInput` elements |

### 4. Robust

| Guideline | Requirement | React Native Implementation |
|-----------|-------------|---------------------------|
| 4.1.2 Name, Role, Value | Elements have name + role + state | `accessibilityLabel` + `accessibilityRole` + `accessibilityState` |
| 4.1.3 Status Messages | Status changes announced | `accessibilityLiveRegion` or `announceForAccessibility()` for dynamic updates |

---

## Contrast Ratios

### Requirements

| Text Type | Minimum Ratio | Definition |
|-----------|--------------|------------|
| Normal text (< 18pt or < 14pt bold) | **4.5:1** | Most body text, labels, buttons |
| Large text (>= 18pt or >= 14pt bold) | **3:1** | Headings, large labels |
| UI components & graphical objects | **3:1** | Icons, borders, form field outlines |

### Common React Native Color Issues

| Foreground | Background | Approx Ratio | Pass? |
|-----------|------------|-------------|-------|
| `#999` | `#fff` | ~2.8:1 | **No** for normal text |
| `#767676` | `#fff` | ~4.5:1 | Yes (minimum for AA) |
| `#666` | `#fff` | ~5.7:1 | Yes |
| `lightgray` (`#d3d3d3`) | `#fff` | ~1.5:1 | **No** |
| `gray` (`#808080`) | `#fff` | ~3.9:1 | **No** for normal text |
| `#333` | `#fff` | ~12.6:1 | Yes |

### Detection Strategy

```
# Flag custom colors and hardcoded hex values for manual contrast review
grep -n "color.*#[0-9a-fA-F]\{3,8\}\|color.*rgb(" **/*.{tsx,jsx,ts,js}
grep -n "color.*['\"]gray['\"]\\|color.*['\"]lightgray['\"]\\|color.*['\"]silver['\"]" **/*.{tsx,jsx,ts,js}
```

### Recommendation

- Use a design system with pre-validated color tokens
- Test with WebAIM Contrast Checker or Colour Contrast Analyser
- Check both light and dark themes
- Remember that opacity reduces effective contrast

---

## Touch Target Minimums

### Requirements

| Platform | Minimum | Source |
|----------|---------|--------|
| Android | 48x48 dp | Material Design Guidelines |
| iOS | 44x44 pt | Apple Human Interface Guidelines |
| WCAG 2.5.8 | 24x24 CSS px | WCAG 2.2 minimum |
| **Recommendation** | **48x48 dp** | Satisfies all requirements |

### Fix Strategies

```tsx
// Expand tap area without changing visual size
<Pressable
  hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
  style={{ width: 24, height: 24 }}
>
  <Icon size={24} />
</Pressable>

// Or set minimum dimensions
<Pressable style={{ minWidth: 48, minHeight: 48 }}>
  <Icon size={24} />
</Pressable>
```

---

## Mobile-Specific WCAG Considerations

### Orientation (1.3.4)
- Don't lock orientation unless essential (e.g., camera viewfinder)
- In `app.json`: `"orientation": "default"` allows both

### Pointer Gestures (2.5.1)
- All multi-finger and path-based gestures must have single-pointer alternatives
- Swipe-to-delete must have a button or `accessibilityActions` alternative

### Motion Actuation (2.5.4)
- Shake-to-undo and device-tilt interactions must have UI alternatives
- Provide a button for any motion-triggered action

### Status Messages (4.1.3)
- Loading indicators, error messages, and success confirmations must be announced
- Use `accessibilityLiveRegion` or `announceForAccessibility()`
