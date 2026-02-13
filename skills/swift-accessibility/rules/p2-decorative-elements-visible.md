---
title: Decorative Elements Not Hidden from VoiceOver
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: voiceover, decorative, hidden
---

## Decorative Elements Not Hidden from VoiceOver

**Priority: P2 (MEDIUM)**

Decorative images, separators, and ornamental elements clutter VoiceOver navigation when they aren't hidden. These add no information and slow down screen traversal.

### Detection

**SwiftUI:**
```
grep -n 'Image.*decorat\|Image.*background\|Image.*separator\|Image.*ornament\|Image.*divider' *.swift
grep -n 'Divider()' *.swift
# Flag decorative patterns not followed by .accessibilityHidden(true)
```

**UIKit:**
```
grep -n 'UIImageView.*separator\|UIImageView.*background\|UIImageView.*decorat' *.swift
# Flag decorative image views without isAccessibilityElement = false
```

### Fix Logic

1. Identify clearly decorative elements: separators, background images, ornamental graphics, dividers
2. SwiftUI: Add `.accessibilityHidden(true)`
3. UIKit: Set `isAccessibilityElement = false`
4. **Err on the side of keeping elements visible** — only hide clearly decorative ones

### SwiftUI Before/After

**Before:**
```swift
Image("wave-pattern")
    .resizable()
    .frame(height: 20)

Image("settings-header-decoration")
    .resizable()
    .frame(height: 40)
```

**After:**
```swift
Image("wave-pattern")
    .resizable()
    .frame(height: 20)
    .accessibilityHidden(true)

Image("settings-header-decoration")
    .resizable()
    .frame(height: 40)
    .accessibilityHidden(true)
```

### UIKit Before/After

**Before:**
```swift
let separator = UIImageView(image: UIImage(named: "divider"))
let background = UIImageView(image: UIImage(named: "gradient-bg"))
```

**After:**
```swift
let separator = UIImageView(image: UIImage(named: "divider"))
separator.isAccessibilityElement = false

let background = UIImageView(image: UIImage(named: "gradient-bg"))
background.isAccessibilityElement = false
```
