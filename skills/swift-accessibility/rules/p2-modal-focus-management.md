---
title: Missing Focus Management for Modals and Navigation
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: focus, modals, navigation, voiceover, escape
---

## Missing Focus Management for Modals and Navigation

**Priority: P2 (MEDIUM)**

When modals, sheets, alerts, or new screens appear, VoiceOver focus must move to the new content. When dismissed, focus must return to a logical element. Background content behind modals must not be reachable by VoiceOver. Custom modals must support the escape gesture for dismissal.

### Detection

**SwiftUI:**
```
# Custom overlays acting as modals
grep -n '\.overlay\|\.fullScreenCover\|\.sheet\|ZStack.*if\s' *.swift
# Flag custom modal patterns without .accessibilityFocused or accessibilityPerformEscape

# Custom popover/dialog implementations
grep -n 'isPresented\|showModal\|showDialog\|showPopover' *.swift
```

**UIKit:**
```
# Custom modal presentations
grep -n 'addSubview.*modal\|addSubview.*overlay\|addSubview.*popup' *.swift
# Flag if accessibilityViewIsModal is not set

grep -n 'present(\|UIViewController.*modal' *.swift
# Standard presentations handle focus automatically — flag custom ones
```

### Fix Logic

1. **Standard SwiftUI sheets/alerts**: Handled automatically — no fix needed
2. **Custom overlays acting as modals**: Add `.accessibilityAddTraits(.isModal)` and manage focus
3. **UIKit custom modals**: Set `accessibilityViewIsModal = true` on the modal view
4. **Focus management**: Use `@AccessibilityFocusState` (SwiftUI) or post `.screenChanged` notification (UIKit)
5. **Dismissal**: Implement `accessibilityPerformEscape()` for custom dismiss-on-swipe behavior
6. **Background content**: Ensure VoiceOver cannot reach elements behind the modal

### SwiftUI Before/After

**Before:**
```swift
struct ContentView: View {
    @State private var showCustomModal = false

    var body: some View {
        ZStack {
            MainContent()

            if showCustomModal {
                Color.black.opacity(0.4)
                CustomModalView(isPresented: $showCustomModal)
            }
        }
    }
}
```

**After:**
```swift
struct ContentView: View {
    @State private var showCustomModal = false
    @AccessibilityFocusState private var isModalFocused: Bool

    var body: some View {
        ZStack {
            MainContent()
                .accessibilityHidden(showCustomModal) // Hide background from VoiceOver

            if showCustomModal {
                Color.black.opacity(0.4)
                    .accessibilityHidden(true)
                CustomModalView(isPresented: $showCustomModal)
                    .accessibilityAddTraits(.isModal)
                    .accessibilityFocused($isModalFocused)
            }
        }
        .onChange(of: showCustomModal) { _, isShowing in
            if isShowing { isModalFocused = true }
        }
    }
}
```

### UIKit Before/After

**Before:**
```swift
func showCustomModal() {
    let modalView = CustomModalView()
    view.addSubview(modalView)
}
```

**After:**
```swift
func showCustomModal() {
    let modalView = CustomModalView()
    modalView.accessibilityViewIsModal = true
    view.addSubview(modalView)

    UIAccessibility.post(notification: .screenChanged, argument: modalView)
}

// In CustomModalView:
override func accessibilityPerformEscape() -> Bool {
    dismiss()
    return true
}
```
