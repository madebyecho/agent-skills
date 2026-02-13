---
title: Gesture-Only Interactions Without Accessible Alternatives
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: gestures, custom-actions, voiceover, voice-control, switch-control
---

## Gesture-Only Interactions Without Accessible Alternatives

**Priority: P2 (MEDIUM)**

Swipe gestures, long presses, drag-and-drop, and hover interactions are invisible to VoiceOver, Voice Control, and Switch Control. Every custom gesture must have an accessible equivalent via custom actions, so assistive technology users can perform the same operations.

### Detection

**SwiftUI:**
```
grep -n '\.onLongPressGesture\|\.gesture(\|\.onDrag\|\.onDrop\|DragGesture\|\.swipeActions' *.swift
# Flag if no .accessibilityAction or .accessibilityActions follows

grep -n '\.onHover\|\.hoverEffect' *.swift
# Flag hover-revealed content without .accessibilityActions equivalent
```

**UIKit:**
```
grep -n 'UILongPressGestureRecognizer\|UISwipeGestureRecognizer\|UIPanGestureRecognizer' *.swift
grep -n 'addGestureRecognizer' *.swift
# Flag if no accessibilityCustomActions is set on the same view

grep -n 'UIContextMenuConfiguration\|contextMenuInteraction' *.swift
# Context menus are automatically accessible — no fix needed
```

### Fix Logic

1. Identify views with gesture recognizers or gesture modifiers
2. For each gesture, add an equivalent `accessibilityAction` or `accessibilityCustomAction`
3. SwiftUI: Use `.accessibilityAction(named:)` or `.accessibilityActions { }` block
4. UIKit: Set `accessibilityCustomActions` array
5. For drag-and-drop: use `.accessibilityDropPoint` (iOS 18+) for multi-target drops
6. For swipe-to-delete/archive: SwiftUI `.swipeActions` are automatically accessible; UIKit requires custom actions
7. Context menus (`contextMenu`) and `accessibilityPerformEscape()` for dismissal are already accessible

### SwiftUI Before/After

**Before:**
```swift
CardView(item: item)
    .onLongPressGesture { showOptions(item) }
    .gesture(
        DragGesture()
            .onEnded { value in
                if value.translation.width < -100 { deleteItem(item) }
            }
    )

// Hover-revealed buttons
MessageView(message: message)
    .onHover { isHovering in showActions = isHovering }
    .overlay {
        if showActions {
            HStack {
                Button("Reply") { reply() }
                Button("Forward") { forward() }
            }
        }
    }
```

**After:**
```swift
CardView(item: item)
    .onLongPressGesture { showOptions(item) }
    .gesture(
        DragGesture()
            .onEnded { value in
                if value.translation.width < -100 { deleteItem(item) }
            }
    )
    .accessibilityAction(named: "Show Options") { showOptions(item) }
    .accessibilityAction(named: "Delete") { deleteItem(item) }

// Hover-revealed buttons — expose as accessibility actions
MessageView(message: message)
    .onHover { isHovering in showActions = isHovering }
    .overlay {
        if showActions {
            HStack {
                Button("Reply") { reply() }
                Button("Forward") { forward() }
            }
        }
    }
    .accessibilityActions {
        Button("Reply") { reply() }
        Button("Forward") { forward() }
    }
```

### UIKit Before/After

**Before:**
```swift
let longPress = UILongPressGestureRecognizer(target: self, action: #selector(handleLongPress))
cellView.addGestureRecognizer(longPress)

let swipe = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipe))
swipe.direction = .left
cellView.addGestureRecognizer(swipe)
```

**After:**
```swift
let longPress = UILongPressGestureRecognizer(target: self, action: #selector(handleLongPress))
cellView.addGestureRecognizer(longPress)

let swipe = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipe))
swipe.direction = .left
cellView.addGestureRecognizer(swipe)

cellView.accessibilityCustomActions = [
    UIAccessibilityCustomAction(name: "Show Options", target: self, selector: #selector(showOptions)),
    UIAccessibilityCustomAction(name: "Delete", target: self, selector: #selector(deleteItem))
]
```
