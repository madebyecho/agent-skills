---
title: Bold Text Setting Not Respected
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: bold-text, vision, system-settings
---

## Bold Text Setting Not Respected

**Priority: P2 (MEDIUM)**

When users enable Bold Text in system settings, all text in the app should become bolder for improved readability. Apps using system fonts via `UIFont.preferredFont` or SwiftUI semantic styles (`.body`, `.headline`) get this automatically. Apps using custom fonts or hardcoded weights need explicit support.

### Detection

**SwiftUI:**
```
# Custom fonts that won't auto-bold
grep -n '\.font(\.custom(' *.swift
# Flag custom fonts without .bold() variant handling

# Check for @Environment(\.legibilityWeight) usage
grep -n 'legibilityWeight' *.swift
# If absent in files with custom fonts, flag for review
```

**UIKit:**
```
# Custom fonts that won't respond to Bold Text
grep -n 'UIFont(name:' *.swift
grep -n 'UIFont(descriptor:' *.swift
# Flag if no UIAccessibility.isBoldTextEnabled check

# Missing notification observer
grep -n 'boldTextStatusDidChangeNotification' *.swift
```

### Fix Logic

1. **System fonts**: Already handle Bold Text automatically — no fix needed
2. **Custom fonts**: Must provide a bold variant and switch based on setting
3. SwiftUI: Read `@Environment(\.legibilityWeight)` and apply `.bold()` when `.bold`
4. UIKit: Check `UIAccessibility.isBoldTextEnabled` and listen for changes
5. Ensure layout doesn't break when text becomes bolder (wider glyphs)

### SwiftUI Before/After

**Before:**
```swift
Text("Section Title")
    .font(.custom("Avenir-Medium", size: 16, relativeTo: .body))
```

**After:**
```swift
struct AdaptiveText: View {
    @Environment(\.legibilityWeight) var legibilityWeight
    let text: String

    var body: some View {
        Text(text)
            .font(.custom(
                legibilityWeight == .bold ? "Avenir-Heavy" : "Avenir-Medium",
                size: 16,
                relativeTo: .body
            ))
    }
}
```

### UIKit Before/After

**Before:**
```swift
label.font = UIFont(name: "Avenir-Medium", size: 16)
```

**After:**
```swift
func updateFont() {
    let fontName = UIAccessibility.isBoldTextEnabled ? "Avenir-Heavy" : "Avenir-Medium"
    let baseFont = UIFont(name: fontName, size: 16)!
    label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)
    label.adjustsFontForContentSizeCategory = true
}

// Listen for Bold Text changes
NotificationCenter.default.addObserver(
    self,
    selector: #selector(boldTextChanged),
    name: UIAccessibility.boldTextStatusDidChangeNotification,
    object: nil
)

@objc func boldTextChanged() {
    updateFont()
}
```
