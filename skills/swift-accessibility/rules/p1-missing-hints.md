---
title: Missing Accessibility Hints on Interactive Elements
priority: P1
impact: HIGH
frameworks: SwiftUI, UIKit
tags: voiceover, hints, interactive
---

## Missing Accessibility Hints on Interactive Elements

**Priority: P1 (HIGH)**

Without hints, users don't know what will happen when they activate an element. Hints are read after a pause and describe the result of the action.

### Detection

**SwiftUI:**
```
grep -n '\.accessibilityLabel' *.swift
# Flag elements with label but no .accessibilityHint within 3 lines
```

**UIKit:**
```
grep -n 'accessibilityLabel\s*=' *.swift
# Flag elements with label but no accessibilityHint set
```

### Fix Logic

1. Infer hint from: action name, surrounding context, element type
2. Hints describe the **result**, not the **gesture** — avoid "Tap to..." or "Double-tap to..."
3. Start with a verb: "Opens...", "Removes...", "Toggles..."
4. Add `[VERIFY]` marker on inferred hints

### SwiftUI Before/After

**Before:**
```swift
Button("Delete") { deleteItem() }
    .accessibilityLabel("Delete item")
```

**After:**
```swift
Button("Delete") { deleteItem() }
    .accessibilityLabel("Delete item")
    .accessibilityHint("Removes this item permanently") // [VERIFY] confirm hint accuracy
```

### UIKit Before/After

**Before:**
```swift
deleteButton.accessibilityLabel = "Delete"
```

**After:**
```swift
deleteButton.accessibilityLabel = "Delete"
deleteButton.accessibilityHint = "Removes this item permanently" // [VERIFY] confirm hint accuracy
```
