# UIKit Accessibility Patterns

Complete catalog of UIKit accessibility APIs with detection patterns and fix examples.

## Core Properties

### `isAccessibilityElement`

**Purpose**: Marks a view as an accessibility element that VoiceOver can focus on.

**When to use**: Custom `UIView` subclasses that represent meaningful content but aren't standard UIKit controls.

**Detection pattern**:
```
# Custom UIView subclasses that may need accessibility
grep -n 'class.*: UIView' | grep -v 'Controller\|Cell'
```

**Before**:
```swift
class RatingView: UIView {
    var rating: Int = 0
    // draws star icons
}
```

**After**:
```swift
class RatingView: UIView {
    var rating: Int = 0 {
        didSet { updateAccessibility() }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        isAccessibilityElement = true
        accessibilityTraits = .none
    }

    private func updateAccessibility() {
        accessibilityLabel = "\(rating) out of 5 stars" // [VERIFY] confirm label matches intent
        accessibilityValue = "\(rating)"
    }
}
```

---

### `accessibilityLabel`

**Purpose**: VoiceOver description of the element.

**Detection pattern**:
```
# UIImageView without accessibilityLabel
grep -n 'UIImageView()' | grep -v 'accessibilityLabel'

# UIButton with only image, no label
grep -n 'setImage.*for:.*\.normal' | grep -v 'accessibilityLabel\|setTitle'

# UIBarButtonItem with image only
grep -n 'UIBarButtonItem(image:' | grep -v 'accessibilityLabel'
```

**Before**:
```swift
let settingsButton = UIBarButtonItem(
    image: UIImage(systemName: "gear"),
    style: .plain,
    target: self,
    action: #selector(openSettings)
)

let profileImage = UIImageView(image: UIImage(named: "avatar"))
```

**After**:
```swift
let settingsButton = UIBarButtonItem(
    image: UIImage(systemName: "gear"),
    style: .plain,
    target: self,
    action: #selector(openSettings)
)
settingsButton.accessibilityLabel = "Settings" // [VERIFY] confirm label matches intent

let profileImage = UIImageView(image: UIImage(named: "avatar"))
profileImage.isAccessibilityElement = true
profileImage.accessibilityLabel = "Profile photo" // [VERIFY] confirm label matches intent
```

---

### `accessibilityValue`

**Purpose**: Current value of the element (read after the label).

**When to use**: Elements with changeable state — sliders, progress bars, custom controls.

**Before**:
```swift
class ProgressView: UIView {
    var progress: Float = 0.0
}
```

**After**:
```swift
class ProgressView: UIView {
    var progress: Float = 0.0 {
        didSet {
            accessibilityValue = "\(Int(progress * 100)) percent"
        }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        isAccessibilityElement = true
        accessibilityLabel = "Progress" // [VERIFY] confirm label matches intent
        accessibilityTraits = .updatesFrequently
    }
}
```

---

### `accessibilityHint`

**Purpose**: Describes the result of activating the element. Read after a pause.

**Detection pattern**:
```
# UIButtons with accessibilityLabel but no hint
grep -n 'accessibilityLabel.*=\|\.accessibilityLabel' | grep -v 'accessibilityHint'
```

**Before**:
```swift
deleteButton.accessibilityLabel = "Delete"
```

**After**:
```swift
deleteButton.accessibilityLabel = "Delete"
deleteButton.accessibilityHint = "Removes this item permanently"
```

---

### `accessibilityTraits`

**Purpose**: Declares the semantic role (button, header, link, image, etc.).

**When to use**: Custom views acting as standard controls, section headers, and links.

**Detection pattern**:
```
# Labels used as headers without header trait
grep -n '\.font = UIFont.*bold\|\.font = .preferredFont.*headline' | grep -v 'accessibilityTraits'
```

**Before**:
```swift
let headerLabel = UILabel()
headerLabel.font = UIFont.preferredFont(forTextStyle: .headline)
headerLabel.text = "Account Settings"
```

**After**:
```swift
let headerLabel = UILabel()
headerLabel.font = UIFont.preferredFont(forTextStyle: .headline)
headerLabel.text = "Account Settings"
headerLabel.accessibilityTraits = .header
```

---

### `accessibilityIdentifier`

**Purpose**: Stable identifier for UI testing. Not read by VoiceOver.

**Detection pattern**:
```
# Interactive elements without identifier
grep -n 'UIButton()\|UITextField()\|UISwitch()\|UISlider()' | grep -v 'accessibilityIdentifier'
```

**Before**:
```swift
let emailField = UITextField()
let submitButton = UIButton(type: .system)
```

**After**:
```swift
let emailField = UITextField()
emailField.accessibilityIdentifier = "emailTextField"

let submitButton = UIButton(type: .system)
submitButton.accessibilityIdentifier = "submitButton"
```

---

### `accessibilityFrame` / `accessibilityPath`

**Purpose**: Override the accessibility frame when the visual bounds don't match the touch target.

**When to use**: Small touch targets that need enlargement for accessibility, or non-rectangular hit areas.

**Before**:
```swift
let smallButton = UIButton()
smallButton.frame = CGRect(x: 0, y: 0, width: 20, height: 20)
```

**After**:
```swift
let smallButton = UIButton()
smallButton.frame = CGRect(x: 0, y: 0, width: 20, height: 20)
// Expand touch target to meet 44x44pt minimum
smallButton.accessibilityFrame = CGRect(x: -12, y: -12, width: 44, height: 44)
```

---

## Dynamic Type

### `UIFont.preferredFont(forTextStyle:)`

Always use preferred fonts instead of hardcoded sizes.

**Detection pattern**:
```
grep -n 'UIFont.systemFont(ofSize:'
grep -n 'UIFont(name:.*size:'
grep -n 'UIFont.boldSystemFont(ofSize:'
```

**Before**:
```swift
label.font = UIFont.systemFont(ofSize: 16)
titleLabel.font = UIFont.boldSystemFont(ofSize: 24)
```

**After**:
```swift
label.font = UIFont.preferredFont(forTextStyle: .body)
titleLabel.font = UIFont.preferredFont(forTextStyle: .title2)
```

### `adjustsFontForContentSizeCategory`

Must be set to `true` for labels and text views to auto-scale with Dynamic Type.

**Detection pattern**:
```
grep -n 'preferredFont(forTextStyle:' | grep -v 'adjustsFontForContentSizeCategory'
```

**Before**:
```swift
label.font = UIFont.preferredFont(forTextStyle: .body)
```

**After**:
```swift
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true
```

### Custom Fonts with Dynamic Type Scaling

**Before**:
```swift
label.font = UIFont(name: "Avenir-Medium", size: 16)
```

**After**:
```swift
if let descriptor = UIFontDescriptor.preferredFontDescriptor(withTextStyle: .body)
    .addingAttributes([.name: "Avenir-Medium"]) as? UIFontDescriptor {
    label.font = UIFont(descriptor: descriptor, size: 0)
    label.adjustsFontForContentSizeCategory = true
}
```

Or with `UIFontMetrics`:
```swift
let customFont = UIFont(name: "Avenir-Medium", size: 16)!
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)
label.adjustsFontForContentSizeCategory = true
```

---

## Advanced APIs

### `UIAccessibilityCustomAction`

**Purpose**: Adds custom actions to the VoiceOver actions menu (swipe up/down).

**When to use**: Cells or views with multiple actions (delete, share, archive) that are triggered by swipe gestures.

**Before**:
```swift
class MessageCell: UITableViewCell {
    func deleteMessage() { /* ... */ }
    func archiveMessage() { /* ... */ }
}
```

**After**:
```swift
class MessageCell: UITableViewCell {
    func deleteMessage() { /* ... */ }
    func archiveMessage() { /* ... */ }

    override var accessibilityCustomActions: [UIAccessibilityCustomAction]? {
        get {
            [
                UIAccessibilityCustomAction(name: "Delete", target: self, selector: #selector(deleteAction)),
                UIAccessibilityCustomAction(name: "Archive", target: self, selector: #selector(archiveAction))
            ]
        }
        set { }
    }

    @objc private func deleteAction() -> Bool {
        deleteMessage()
        return true
    }

    @objc private func archiveAction() -> Bool {
        archiveMessage()
        return true
    }
}
```

---

### `accessibilityIncrement()` / `accessibilityDecrement()`

**Purpose**: Handle VoiceOver swipe up/down gestures on adjustable controls.

**When to use**: Custom stepper, slider, or any adjustable value control.

**Before**:
```swift
class QuantityStepper: UIView {
    var quantity: Int = 1
}
```

**After**:
```swift
class QuantityStepper: UIView {
    var quantity: Int = 1 {
        didSet { accessibilityValue = "\(quantity)" }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        isAccessibilityElement = true
        accessibilityLabel = "Quantity"
        accessibilityTraits = .adjustable
        accessibilityValue = "\(quantity)"
    }

    override func accessibilityIncrement() {
        quantity += 1
    }

    override func accessibilityDecrement() {
        guard quantity > 0 else { return }
        quantity -= 1
    }
}
```

---

### `UIAccessibility.post(notification:argument:)`

**Purpose**: Notify VoiceOver of dynamic content changes.

**When to use**: After data loads, error messages appear, or screen content changes without a full navigation event.

**Notification types**:
- `.announcement` — Speak a message (e.g., "3 new results loaded")
- `.screenChanged` — Major screen change; pass the new first element
- `.layoutChanged` — Layout updated; pass the element to focus

**Before**:
```swift
func loadResults() {
    results = fetchResults()
    tableView.reloadData()
}
```

**After**:
```swift
func loadResults() {
    results = fetchResults()
    tableView.reloadData()
    UIAccessibility.post(
        notification: .announcement,
        argument: "\(results.count) results loaded"
    )
}
```

---

### `UIAccessibilityCustomRotor`

**Purpose**: Creates custom VoiceOver rotors for navigating specific content types.

**When to use**: Documents, feeds, or complex screens where users need to jump between specific element types.

```swift
let headingRotor = UIAccessibilityCustomRotor(name: "Headings") { predicate in
    // Find next/previous heading based on predicate.searchDirection
    let headings = self.contentView.subviews.filter { $0.accessibilityTraits.contains(.header) }
    // Return UIAccessibilityCustomRotorItemResult for the target element
    return UIAccessibilityCustomRotorItemResult(targetElement: nextHeading, targetRange: nil)
}
accessibilityCustomRotors = [headingRotor]
```

---

## UIKit Font Style Mapping

| Hardcoded Size | Suggested `UIFont.TextStyle` |
|---------------|------------------------------|
| 34+ | `.largeTitle` |
| 28–33 | `.title1` |
| 22–27 | `.title2` |
| 20–21 | `.title3` |
| 17–19 | `.headline` or `.body` |
| 15–16 | `.subheadline` or `.callout` |
| 13–14 | `.footnote` |
| 11–12 | `.caption1` or `.caption2` |
