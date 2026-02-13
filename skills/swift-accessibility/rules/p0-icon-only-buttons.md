---
title: Icon-Only Buttons Without Labels
priority: P0
impact: CRITICAL
frameworks: SwiftUI, UIKit
tags: voiceover, buttons, labels
---

## Icon-Only Buttons Without Labels

**Priority: P0 (CRITICAL)**

Buttons that contain only an image (no text) are announced as "button" with no description. Users cannot determine what the button does.

### Detection

**SwiftUI:**
```
grep -n 'Button' *.swift
# Flag if body contains only Image() and no .accessibilityLabel on the Button
```

**UIKit:**
```
grep -n 'setImage' *.swift
# Flag UIButton with setImage but no setTitle and no accessibilityLabel

grep -n 'UIBarButtonItem(image:' *.swift
# Flag bar button items with image but no accessibilityLabel
```

### Fix Logic

1. Infer label from: SF Symbol name, image name, action method name
2. Apply label to the **Button** (SwiftUI) or the button object (UIKit), not the Image inside it
3. Add `[VERIFY]` marker on all inferred labels

### SwiftUI Before/After

**Before:**
```swift
Button(action: { toggleFavorite() }) {
    Image(systemName: "heart")
}
```

**After:**
```swift
Button(action: { toggleFavorite() }) {
    Image(systemName: "heart")
}
.accessibilityLabel("Toggle favorite") // [VERIFY] confirm label matches intent
```

### UIKit Before/After

**Before:**
```swift
let settingsButton = UIBarButtonItem(
    image: UIImage(systemName: "gear"),
    style: .plain,
    target: self,
    action: #selector(openSettings)
)

editButton.setImage(UIImage(systemName: "pencil"), for: .normal)
```

**After:**
```swift
let settingsButton = UIBarButtonItem(
    image: UIImage(systemName: "gear"),
    style: .plain,
    target: self,
    action: #selector(openSettings)
)
settingsButton.accessibilityLabel = "Settings" // [VERIFY] confirm label matches intent

editButton.setImage(UIImage(systemName: "pencil"), for: .normal)
editButton.accessibilityLabel = "Edit" // [VERIFY] confirm label matches intent
```
