# SwiftUI Accessibility Patterns

Complete catalog of SwiftUI accessibility modifiers with detection patterns and fix examples.

## Core Modifiers

### `.accessibilityLabel(_:)`

**Purpose**: Sets the VoiceOver description for an element.

**When to use**: Any visual element that conveys meaning — images, icons, icon-only buttons, custom shapes.

**API**:
```swift
func accessibilityLabel(_ label: Text) -> ModifiedContent<Self, AccessibilityAttachmentModifier>
func accessibilityLabel(_ labelKey: LocalizedStringKey) -> ModifiedContent<Self, AccessibilityAttachmentModifier>
func accessibilityLabel(_ label: some StringProtocol) -> ModifiedContent<Self, AccessibilityAttachmentModifier>
```

**Detection pattern** (anti-pattern):
```
# Image without label
grep -n 'Image(' | grep -v 'accessibilityLabel\|accessibilityHidden'

# Icon-only Button without label
grep -n 'Button.*{.*Image(' | grep -v 'accessibilityLabel'
```

**Before**:
```swift
Image(systemName: "gear")

Button(action: { showSettings() }) {
    Image(systemName: "gear")
}
```

**After**:
```swift
Image(systemName: "gear")
    .accessibilityLabel("Settings") // [VERIFY] confirm label matches intent

Button(action: { showSettings() }) {
    Image(systemName: "gear")
}
.accessibilityLabel("Settings") // [VERIFY] confirm label matches intent
```

---

### `.accessibilityValue(_:)`

**Purpose**: Communicates the current value of an element (e.g., slider position, toggle state).

**When to use**: Custom controls that have a variable state not already communicated by the control type.

**API**:
```swift
func accessibilityValue(_ valueKey: LocalizedStringKey) -> ModifiedContent<Self, AccessibilityAttachmentModifier>
func accessibilityValue(_ value: some StringProtocol) -> ModifiedContent<Self, AccessibilityAttachmentModifier>
```

**Before**:
```swift
CustomSlider(value: $brightness)
```

**After**:
```swift
CustomSlider(value: $brightness)
    .accessibilityValue("\(Int(brightness * 100)) percent")
```

---

### `.accessibilityHint(_:)`

**Purpose**: Describes what happens when the element is activated. Read after a pause.

**When to use**: Interactive elements where the action isn't obvious from the label alone.

**Detection pattern**:
```
# Buttons/Toggles without hint
grep -n 'Button\|Toggle' | grep 'accessibilityLabel' | grep -v 'accessibilityHint'
```

**Before**:
```swift
Button("Delete") {
    deleteItem()
}
```

**After**:
```swift
Button("Delete") {
    deleteItem()
}
.accessibilityHint("Removes this item permanently")
```

---

### `.accessibilityIdentifier(_:)`

**Purpose**: Sets a stable identifier for UI testing. Not read by VoiceOver.

**When to use**: All interactive and testable elements. Critical for XCUITest automation.

**Detection pattern**:
```
# Interactive elements without identifier
grep -n 'Button\|TextField\|Toggle\|Slider\|Picker' | grep -v 'accessibilityIdentifier'
```

**Before**:
```swift
TextField("Email", text: $email)
Button("Submit") { submit() }
```

**After**:
```swift
TextField("Email", text: $email)
    .accessibilityIdentifier("emailTextField")
Button("Submit") { submit() }
    .accessibilityIdentifier("submitButton")
```

---

### `.accessibilityHidden(_:)`

**Purpose**: Hides decorative elements from VoiceOver.

**When to use**: Decorative images, background elements, redundant text that's already part of another element's label.

**Detection pattern**:
```
# Decorative images (common names suggesting decorative purpose)
grep -n 'Image.*background\|Image.*decoration\|Image.*separator\|Image.*divider'
```

**Before**:
```swift
Image("decorative-banner")
Image(systemName: "circle.fill")
    .foregroundColor(.gray)
    .font(.system(size: 4))
```

**After**:
```swift
Image("decorative-banner")
    .accessibilityHidden(true)
Image(systemName: "circle.fill")
    .foregroundColor(.gray)
    .font(.system(size: 4))
    .accessibilityHidden(true)
```

---

### `.accessibilityElement(children:)`

**Purpose**: Controls how child elements are exposed to accessibility. `.combine` merges children into one element; `.contain` keeps them separate; `.ignore` hides children.

**When to use**: Group related elements to reduce VoiceOver verbosity.

**Before**:
```swift
HStack {
    Image(systemName: "star.fill")
    Text("4.5")
    Text("(128 reviews)")
}
```

**After**:
```swift
HStack {
    Image(systemName: "star.fill")
    Text("4.5")
    Text("(128 reviews)")
}
.accessibilityElement(children: .combine)
.accessibilityLabel("4.5 stars, 128 reviews")
```

---

### `.accessibilityAddTraits(_:)`

**Purpose**: Declares the semantic role of an element — header, button, link, image, etc.

**When to use**: Custom views that act as headers, buttons, or links but aren't built from standard components.

**Detection pattern**:
```
# Text used as section headers without header trait
grep -n '\.font(.*\.title\|\.font(.*\.headline' | grep -v 'accessibilityAddTraits'
```

**Before**:
```swift
Text("Account Settings")
    .font(.headline)
```

**After**:
```swift
Text("Account Settings")
    .font(.headline)
    .accessibilityAddTraits(.isHeader)
```

---

### `.accessibilityAction(_:_:)`

**Purpose**: Adds custom accessibility actions (beyond tap).

**When to use**: Elements with swipe gestures, long press, or other custom interactions.

**Before**:
```swift
CardView()
    .onLongPressGesture { showOptions() }
```

**After**:
```swift
CardView()
    .onLongPressGesture { showOptions() }
    .accessibilityAction(named: "Show Options") { showOptions() }
```

---

### `.accessibilitySortPriority(_:)`

**Purpose**: Controls the order VoiceOver navigates elements. Higher values are read first.

**When to use**: When the visual layout order doesn't match the logical reading order.

**Before**:
```swift
ZStack {
    BackgroundView()
    ContentView()
    FloatingActionButton()
}
```

**After**:
```swift
ZStack {
    BackgroundView()
        .accessibilityHidden(true)
    ContentView()
        .accessibilitySortPriority(1)
    FloatingActionButton()
        .accessibilitySortPriority(0)
}
```

---

### `.accessibilityAdjustableAction(_:)`

**Purpose**: Handles VoiceOver swipe-up/down to increment or decrement values.

**When to use**: Custom stepper or adjustable controls.

**Before**:
```swift
CustomStepper(value: $quantity)
```

**After**:
```swift
CustomStepper(value: $quantity)
    .accessibilityValue("\(quantity)")
    .accessibilityAdjustableAction { direction in
        switch direction {
        case .increment: quantity += 1
        case .decrement: quantity -= 1
        @unknown default: break
        }
    }
```

---

### `.accessibilityRotor(_:entries:)`

**Purpose**: Creates custom VoiceOver rotors for navigating specific content types.

**When to use**: Long lists with distinct categories, documents with headings, or any content where quick navigation adds value.

**Before**:
```swift
List(messages) { message in
    MessageRow(message: message)
}
```

**After**:
```swift
List(messages) { message in
    MessageRow(message: message)
}
.accessibilityRotor("Unread Messages") {
    ForEach(messages.filter { !$0.isRead }) { message in
        AccessibilityRotorEntry(message.senderName, id: message.id)
    }
}
```

---

## Dynamic Type

### Preferred Approach — Semantic Fonts

Always use semantic font styles instead of hardcoded sizes.

**Detection pattern**:
```
grep -n '\.font(.system(size:'
grep -n '\.font(.custom.*size:'
```

**Before**:
```swift
Text("Title")
    .font(.system(size: 24, weight: .bold))
Text("Body")
    .font(.system(size: 16))
```

**After**:
```swift
Text("Title")
    .font(.title2.bold())
Text("Body")
    .font(.body)
```

### Custom Fonts with Dynamic Type

When custom fonts are required, use `relativeTo:` to scale with Dynamic Type.

**Before**:
```swift
Text("Custom")
    .font(.custom("Avenir-Medium", size: 16))
```

**After**:
```swift
Text("Custom")
    .font(.custom("Avenir-Medium", size: 16, relativeTo: .body))
```

---

## Semantic Font Style Mapping

| Hardcoded Size | Suggested Style |
|---------------|-----------------|
| 34+ | `.largeTitle` |
| 28–33 | `.title` |
| 22–27 | `.title2` |
| 20–21 | `.title3` |
| 17–19 | `.headline` or `.body` |
| 15–16 | `.subheadline` or `.callout` |
| 13–14 | `.footnote` |
| 11–12 | `.caption` or `.caption2` |

---

## Voice Control and Discoverability

### `.accessibilityInputLabels(_:)`

**Purpose**: Provides alternative names for Voice Control. Users say "Tap [name]" — these labels define what names work.

**When to use**: Elements where the visible text doesn't match what users would naturally say (icons, abbreviations, symbols).

**Before**:
```swift
Button(action: { compose() }) {
    Image(systemName: "square.and.pencil")
}
.accessibilityLabel("Compose")
```

**After**:
```swift
Button(action: { compose() }) {
    Image(systemName: "square.and.pencil")
}
.accessibilityLabel("Compose")
.accessibilityInputLabels(["Compose", "New Message", "Write"])
```

---

## Focus Management

### `@AccessibilityFocusState`

**Purpose**: Programmatically moves VoiceOver focus to a specific element.

**When to use**: After navigation, modal presentation, error display, or dynamic content load.

```swift
@AccessibilityFocusState private var isErrorFocused: Bool

var body: some View {
    VStack {
        if let error = errorMessage {
            Text(error)
                .accessibilityFocused($isErrorFocused)
        }
    }
    .onChange(of: errorMessage) { _, newValue in
        if newValue != nil { isErrorFocused = true }
    }
}
```

### `.accessibilityFocused(_:)`

**Purpose**: Binds an element's accessibility focus state to a boolean.

```swift
TextField("Search", text: $query)
    .accessibilityFocused($isSearchFocused)
```

---

## Accessibility Notifications (iOS 17+)

### `AccessibilityNotification`

**Purpose**: Post notifications to assistive technologies from SwiftUI.

**Types**:
```swift
// Speak a message without moving focus
AccessibilityNotification.Announcement("5 results loaded").post()

// Layout changed — move focus to element
AccessibilityNotification.LayoutChanged(element).post()

// Full screen changed
AccessibilityNotification.ScreenChanged(firstElement).post()

// Page scrolled
AccessibilityNotification.PageScrolled("Page 2 of 5").post()
```

**Announcement Priority** (iOS 18+):
```swift
// High: interrupts speech, can't be interrupted
AccessibilityNotification.Announcement("Error: payment failed")
    .post(priority: .high)

// Low: queued, spoken when current speech finishes
AccessibilityNotification.Announcement("Download complete")
    .post(priority: .low)
```

---

## Conditional Modifiers (iOS 18+)

### `isEnabled` Parameter

**Purpose**: Conditionally apply accessibility modifiers, falling back to SwiftUI defaults when disabled.

```swift
Button(action: favorite) {
    Image(systemName: isSuperFavorite ? "sparkles" : "star.fill")
}
.accessibilityLabel("Super Favorite", isEnabled: isSuperFavorite)
// When isSuperFavorite is false, uses SwiftUI's default label for the symbol
```

### Label View Builder (iOS 18+)

**Purpose**: Append content to an existing label without overriding it.

```swift
TripView(trip: trip)
    .accessibilityLabel { existingLabel in
        if let rating = trip.rating {
            Text(rating)
        }
        existingLabel
    }
```

---

## Drag and Drop (iOS 18+)

### `.accessibilityDropPoint(_:description:)`

**Purpose**: Defines discrete drop zones for drag-and-drop operations.

```swift
DropTargetView()
    .onDrop(of: [.audio], delegate: delegate)
    .accessibilityDropPoint(.leading, description: "Set Sound 1")
    .accessibilityDropPoint(.center, description: "Set Sound 2")
    .accessibilityDropPoint(.trailing, description: "Set Sound 3")
```

---

## System Settings

### Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var body: some View {
    ContentView()
        .animation(reduceMotion ? .none : .spring(), value: isVisible)
}
```

### Bold Text / Legibility Weight

```swift
@Environment(\.legibilityWeight) var legibilityWeight

var body: some View {
    Text("Title")
        .font(.custom(
            legibilityWeight == .bold ? "Avenir-Heavy" : "Avenir-Medium",
            size: 16, relativeTo: .body
        ))
}
```

### Increase Contrast

```swift
@Environment(\.colorSchemeContrast) var contrast

var body: some View {
    Text("Status")
        .foregroundColor(contrast == .increased ? .primary : .secondary)
}
```

### Reduce Transparency

```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

var body: some View {
    overlay
        .opacity(reduceTransparency ? 1 : 0.8)
}
```

### Differentiate Without Color

```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor

var body: some View {
    if differentiateWithoutColor {
        // Add shapes/icons alongside color
        Label("Online", systemImage: "checkmark.circle.fill")
    } else {
        Circle().fill(.green)
    }
}
```
