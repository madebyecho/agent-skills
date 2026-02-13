---
title: Missing Voice Control Input Labels
priority: P1
impact: HIGH
frameworks: SwiftUI, UIKit
tags: voice-control, input-labels, discoverability
---

## Missing Voice Control Input Labels

**Priority: P1 (HIGH)**

Voice Control users speak "Tap [name]" to activate elements. If the visible text doesn't match the accessibility label, Voice Control fails silently. `accessibilityInputLabels` provides alternative names that Voice Control recognizes, supporting multiple ways users might refer to an element.

### Detection

**SwiftUI:**
```
# Buttons/controls with icons or abbreviated text that users might call by different names
grep -n 'Button\|NavigationLink\|.onTapGesture' *.swift
# Flag elements where visible text is ambiguous, abbreviated, or icon-only
```

**UIKit:**
```
grep -n 'accessibilityLabel' *.swift
# Flag where label doesn't match visible text
```

### Fix Logic

1. For elements where visible text matches what users would say → no change needed
2. For elements with icons, abbreviations, or multiple possible names → add `accessibilityInputLabels`
3. Order labels from most to least specific
4. First label is used as the default VoiceOver label if no `accessibilityLabel` is set

### SwiftUI Before/After

**Before:**
```swift
Button(action: { compose() }) {
    Image(systemName: "square.and.pencil")
}
.accessibilityLabel("Compose")

Button("DL Report") {
    downloadReport()
}
```

**After:**
```swift
Button(action: { compose() }) {
    Image(systemName: "square.and.pencil")
}
.accessibilityLabel("Compose")
.accessibilityInputLabels(["Compose", "New Message", "Write"])

Button("DL Report") {
    downloadReport()
}
.accessibilityInputLabels(["Download Report", "DL Report", "Export"])
```

### UIKit Before/After

**Before:**
```swift
composeButton.accessibilityLabel = "Compose"
```

**After:**
```swift
composeButton.accessibilityLabel = "Compose"
composeButton.accessibilityUserInputLabels = ["Compose", "New Message", "Write"]
```
