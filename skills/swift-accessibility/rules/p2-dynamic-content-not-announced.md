---
title: Dynamic Content Changes Not Announced
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: announcements, notifications, voiceover, dynamic-content
---

## Dynamic Content Changes Not Announced

**Priority: P2 (MEDIUM)**

When content updates dynamically (loading states, errors, live data, toast messages), VoiceOver users have no way to know something changed unless an accessibility notification is posted. Important status changes must be announced.

### Detection

**SwiftUI:**
```
# State changes that update visible content
grep -n '\.task\|\.onAppear\|\.onChange\|\.refreshable' *.swift
# Flag data-loading patterns without AccessibilityNotification.post

# Error/success banners
grep -n 'alert\|toast\|banner\|snackbar\|error.*message\|success.*message' *.swift
```

**UIKit:**
```
# Async data loading without announcement
grep -n 'reloadData\|reloadSections\|performBatchUpdates\|insertRows' *.swift
# Flag if no UIAccessibility.post follows

grep -n 'URLSession\|async.*await\|completion.*Handler' *.swift
# Flag data fetch completions without accessibility notification
```

### Fix Logic

1. Identify state changes that update visible content (data loads, errors, status changes)
2. Post appropriate notification after the change:
   - **Announcement**: Speak a message without moving focus (loading results, errors, confirmations)
   - **Layout Changed**: UI layout updated, optionally move focus to an element
   - **Screen Changed**: Major screen change, move focus to first element
3. SwiftUI (iOS 17+): Use `AccessibilityNotification.Announcement("message").post()`
4. UIKit: Use `UIAccessibility.post(notification:argument:)`
5. iOS 18+: Set announcement priority (`.high` for errors, `.default` for info, `.low` for background updates)

### SwiftUI Before/After

**Before:**
```swift
struct SearchView: View {
    @State private var results: [Item] = []
    @State private var errorMessage: String?

    var body: some View {
        List(results) { item in ItemRow(item: item) }
            .task {
                do {
                    results = try await fetchResults()
                } catch {
                    errorMessage = error.localizedDescription
                }
            }
    }
}
```

**After:**
```swift
struct SearchView: View {
    @State private var results: [Item] = []
    @State private var errorMessage: String?

    var body: some View {
        List(results) { item in ItemRow(item: item) }
            .task {
                do {
                    results = try await fetchResults()
                    AccessibilityNotification.Announcement("\(results.count) results loaded")
                        .post()
                } catch {
                    errorMessage = error.localizedDescription
                    AccessibilityNotification.Announcement("Error: \(error.localizedDescription)")
                        .post()
                }
            }
    }
}
```

### UIKit Before/After

**Before:**
```swift
func loadResults() {
    results = fetchResults()
    tableView.reloadData()
}

func showError(_ message: String) {
    errorLabel.text = message
    errorLabel.isHidden = false
}
```

**After:**
```swift
func loadResults() {
    results = fetchResults()
    tableView.reloadData()
    UIAccessibility.post(
        notification: .announcement,
        argument: "\(results.count) results loaded"
    )
}

func showError(_ message: String) {
    errorLabel.text = message
    errorLabel.isHidden = false
    UIAccessibility.post(
        notification: .layoutChanged,
        argument: errorLabel  // Move VoiceOver focus to the error
    )
}
```

### Notification Types Reference

| Notification | When to Use | Argument |
|-------------|-------------|----------|
| `.announcement` | Speak a message without moving focus | `String` message |
| `.layoutChanged` | UI layout changed, move focus | Target element or `nil` |
| `.screenChanged` | Full screen change (navigation) | First element or `nil` |
| `.pageScrolled` | Scroll position changed | Status string (e.g., "Page 2 of 5") |
