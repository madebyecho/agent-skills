---
title: Images Without Accessibility Labels
priority: P0
impact: CRITICAL
frameworks: SwiftUI, UIKit
tags: voiceover, images, labels
---

## Images Without Accessibility Labels

**Priority: P0 (CRITICAL)**

Informational images without accessibility labels are completely invisible to VoiceOver users. Every meaningful image must have a label; every decorative image must be hidden.

### Detection

**SwiftUI:**
```
grep -n 'Image(' *.swift
# Flag if no .accessibilityLabel or .accessibilityHidden within 3 lines
```

**UIKit:**
```
grep -n 'UIImageView(' *.swift
grep -n '\.image = UIImage(' *.swift
# Flag if accessibilityLabel is not set on the same object
```

### Fix Logic

1. Determine if image is **informational** or **decorative**:
   - Decorative (backgrounds, separators, ornaments) → add `.accessibilityHidden(true)` / `isAccessibilityElement = false`
   - Informational (icons, photos, meaningful graphics) → add `.accessibilityLabel("description") // [VERIFY]`
2. Infer label from: SF Symbol name, image asset name, surrounding context
3. Always add `[VERIFY]` marker on inferred labels

### SwiftUI Before/After

**Before:**
```swift
Image(systemName: "heart.fill")
Image("product-photo")
```

**After:**
```swift
Image(systemName: "heart.fill")
    .accessibilityLabel("Favorite") // [VERIFY] confirm label matches intent
Image("product-photo")
    .accessibilityLabel("Product photo") // [VERIFY] confirm label matches intent
```

### UIKit Before/After

**Before:**
```swift
let icon = UIImageView(image: UIImage(systemName: "heart.fill"))
```

**After:**
```swift
let icon = UIImageView(image: UIImage(systemName: "heart.fill"))
icon.isAccessibilityElement = true
icon.accessibilityLabel = "Favorite" // [VERIFY] confirm label matches intent
```
