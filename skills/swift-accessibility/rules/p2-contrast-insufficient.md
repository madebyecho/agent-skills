---
title: Insufficient Color Contrast
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: contrast, wcag, vision, dark-mode, increase-contrast
---

## Insufficient Color Contrast

**Priority: P2 (MEDIUM)**

Text and UI components must meet minimum contrast ratios: 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt bold+), and 3:1 for non-text UI elements (icons, borders, focus indicators). Contrast must be sufficient in both Light and Dark modes, and should improve when the Increase Contrast system setting is enabled.

### Detection

**SwiftUI:**
```
# Custom/hardcoded colors — flag for manual contrast review
grep -n 'Color(red:\|Color(hex:\|Color(#\|Color("\|\.init(red:' *.swift

# Known low-contrast system colors used for text
grep -n '\.tertiaryLabel\|\.quaternaryLabel\|\.systemGray[^2-6]' *.swift

# Placeholder text might have low contrast
grep -n '\.foregroundColor(.*gray\|\.foregroundStyle(.*gray\|\.opacity(0\.[0-4]' *.swift
```

**UIKit:**
```
grep -n 'UIColor(red:\|UIColor(hex:\|UIColor(named:\|#colorLiteral' *.swift
grep -n 'UIColor.systemGray\b\|UIColor.tertiaryLabel\|UIColor.quaternaryLabel' *.swift
```

### Fix Logic

1. Flag all custom/hardcoded colors for **manual contrast verification**
2. Recommend switching to semantic system colors that auto-adapt:
   - Text: `.label`, `.secondaryLabel` (pass AA)
   - Backgrounds: `.systemBackground`, `.secondarySystemBackground`
3. Flag `.tertiaryLabel` and `.quaternaryLabel` when used for normal-sized text (fail 4.5:1)
4. Check both Light Mode and Dark Mode contrast
5. Verify app responds to **Increase Contrast** setting:
   - SwiftUI: `@Environment(\.colorSchemeContrast)`
   - UIKit: `UIAccessibility.isDarkerSystemColorsEnabled`
6. Test with **Bold Text** and **Reduce Transparency** enabled simultaneously

### Contrast Requirements

| Element Type | Minimum Ratio |
|-------------|--------------|
| Normal text (< 18pt / < 14pt bold) | **4.5:1** |
| Large text (>= 18pt / >= 14pt bold) | **3:1** |
| UI components (icons, borders, controls) | **3:1** |
| Focus indicators | **3:1** |
| Disabled elements | Exempt |

### System Color Safety

| Color | vs `.systemBackground` | Normal Text? |
|-------|----------------------|-------------|
| `.label` | ~21:1 / ~16:1 | Yes |
| `.secondaryLabel` | ~5.5:1 / ~5:1 | Yes |
| `.tertiaryLabel` | ~2.5:1 | **No** |
| `.quaternaryLabel` | ~1.7:1 | **No** |
| `.systemGray` | ~3.5:1 | Large only |

### SwiftUI Before/After

**Before:**
```swift
Text("Subtitle")
    .foregroundColor(.gray)

Text("Fine print")
    .foregroundStyle(.tertiary)

Text("Disabled hint")
    .foregroundColor(Color(red: 0.7, green: 0.7, blue: 0.7))
```

**After:**
```swift
Text("Subtitle")
    .foregroundColor(.secondary) // .secondaryLabel meets 4.5:1

Text("Fine print")
    .foregroundStyle(.secondary)

Text("Disabled hint")
    .foregroundColor(.secondary) // [VERIFY] confirm this meets contrast in both modes
```

### Responding to Increase Contrast

**SwiftUI:**
```swift
@Environment(\.colorSchemeContrast) var contrast

var body: some View {
    Text("Status")
        .foregroundColor(contrast == .increased ? .primary : .secondary)
}
```

**UIKit:**
```swift
if UIAccessibility.isDarkerSystemColorsEnabled {
    label.textColor = .label  // Higher contrast variant
} else {
    label.textColor = .secondaryLabel
}

// Listen for changes
NotificationCenter.default.addObserver(
    self,
    selector: #selector(contrastChanged),
    name: UIAccessibility.darkerSystemColorsStatusDidChangeNotification,
    object: nil
)
```
