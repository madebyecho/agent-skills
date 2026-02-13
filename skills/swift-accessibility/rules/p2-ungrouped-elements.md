---
title: Ungrouped Related Elements
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: voiceover, grouping, navigation
---

## Ungrouped Related Elements

**Priority: P2 (MEDIUM)**

When related elements (icon + label, star + rating text) aren't grouped, VoiceOver announces each one separately. This makes navigation slow and confusing.

### Detection

**SwiftUI:**
```
grep -n 'HStack\|VStack' *.swift
# Flag containers with Image + Text children but no .accessibilityElement(children:)
```

**UIKit:**
```
# Custom container views with multiple subviews that should be a single accessible element
# Check if isAccessibilityElement is set on the container
```

### Fix Logic

1. Identify container views with multiple related children (Image + Text, Icon + Label)
2. SwiftUI: Add `.accessibilityElement(children: .combine)` to merge into single VoiceOver element
3. UIKit: Set `isAccessibilityElement = true` on container and compose `accessibilityLabel` from children
4. Optionally add explicit `.accessibilityLabel` if the combined reading isn't natural

### SwiftUI Before/After

**Before:**
```swift
HStack {
    Image(systemName: "envelope")
    Text("inbox@example.com")
}

HStack {
    Image(systemName: "star.fill")
    Text("4.5")
    Text("(128 reviews)")
}
```

**After:**
```swift
HStack {
    Image(systemName: "envelope")
    Text("inbox@example.com")
}
.accessibilityElement(children: .combine)

HStack {
    Image(systemName: "star.fill")
    Text("4.5")
    Text("(128 reviews)")
}
.accessibilityElement(children: .combine)
.accessibilityLabel("4.5 stars, 128 reviews")
```

### UIKit Before/After

**Before:**
```swift
// Multiple labels in a cell read separately
cell.senderLabel.text = "John"
cell.messageLabel.text = "Hey there!"
cell.timeLabel.text = "2:30 PM"
```

**After:**
```swift
cell.senderLabel.text = "John"
cell.messageLabel.text = "Hey there!"
cell.timeLabel.text = "2:30 PM"

// Combine into single accessible element
cell.isAccessibilityElement = true
cell.accessibilityLabel = "From John. Hey there! 2:30 PM"
```
