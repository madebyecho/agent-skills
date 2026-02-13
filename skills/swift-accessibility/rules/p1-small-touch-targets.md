---
title: Touch Targets Below 44x44 Points
priority: P1
impact: HIGH
frameworks: SwiftUI, UIKit
tags: touch-targets, motor, hig, wcag
---

## Touch Targets Below 44x44 Points

**Priority: P1 (HIGH)**

Apple HIG requires all interactive elements to have a minimum touch target of 44x44 points. Small targets cause tap errors for all users and are especially problematic for people with motor impairments. This is also a WCAG 2.5.5 requirement.

### Detection

**SwiftUI:**
```
grep -n '\.frame(width:.*height:' *.swift
# Flag interactive elements (Button, Toggle, tap gesture views) where width or height < 44

grep -n '\.frame(.*width:\s*[0-9]\+\b' *.swift
# Check if the numeric value is < 44 on a tappable element
```

**UIKit:**
```
grep -n 'CGRect.*width:.*height:' *.swift
grep -n '\.frame = CGRect' *.swift
# Flag UIButton, UIControl subclasses where frame width or height < 44
```

### Fix Logic

1. Identify interactive elements with frames smaller than 44x44
2. **Prefer expanding the tappable area** without changing visual size
3. SwiftUI: Use `.frame(minWidth: 44, minHeight: 44)` or `.contentShape()`
4. UIKit: Override `point(inside:with:)` or set `accessibilityFrame`
5. Don't change purely visual elements — only interactive ones

### SwiftUI Before/After

**Before:**
```swift
Button(action: { dismiss() }) {
    Image(systemName: "xmark")
        .font(.caption)
        .frame(width: 20, height: 20)
}

Image(systemName: "info.circle")
    .frame(width: 16, height: 16)
    .onTapGesture { showInfo() }
```

**After:**
```swift
Button(action: { dismiss() }) {
    Image(systemName: "xmark")
        .font(.caption)
        .frame(width: 20, height: 20)
}
.frame(minWidth: 44, minHeight: 44)

Image(systemName: "info.circle")
    .frame(width: 16, height: 16)
    .contentShape(Rectangle())
    .frame(minWidth: 44, minHeight: 44)
    .onTapGesture { showInfo() }
```

### UIKit Before/After

**Before:**
```swift
let closeButton = UIButton()
closeButton.frame = CGRect(x: 0, y: 0, width: 24, height: 24)
```

**After:**
```swift
let closeButton = UIButton()
closeButton.frame = CGRect(x: 0, y: 0, width: 24, height: 24)

// Option 1: Override in subclass
override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
    bounds.insetBy(dx: -10, dy: -10).contains(point)
}

// Option 2: Expand accessibility frame
closeButton.accessibilityFrame = closeButton.frame.insetBy(dx: -10, dy: -10)
```
