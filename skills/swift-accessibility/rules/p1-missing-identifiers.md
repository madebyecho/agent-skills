---
title: Missing Accessibility Identifiers
priority: P1
impact: HIGH
frameworks: SwiftUI, UIKit
tags: testing, identifiers, xcuitest
---

## Missing Accessibility Identifiers

**Priority: P1 (HIGH)**

Without accessibility identifiers, UI tests cannot reliably locate elements. Identifiers are not read by VoiceOver — they exist solely for test automation.

### Detection

**SwiftUI:**
```
grep -n 'Button\|TextField\|SecureField\|Toggle\|Slider\|Picker\|DatePicker\|Stepper' *.swift
# Flag interactive elements without .accessibilityIdentifier
```

**UIKit:**
```
grep -n 'UIButton()\|UITextField()\|UISwitch()\|UISlider()\|UISegmentedControl()' *.swift
# Flag interactive elements without .accessibilityIdentifier
```

### Fix Logic

1. Generate identifier from: variable name, label text, or view hierarchy position
2. Use camelCase format: `"submitButton"`, `"emailTextField"`, `"darkModeToggle"`
3. Identifiers must be unique within a screen
4. No `[VERIFY]` needed — identifiers are mechanical, not semantic

### SwiftUI Before/After

**Before:**
```swift
TextField("Username", text: $username)
Button("Log In") { login() }
Toggle("Dark Mode", isOn: $darkMode)
```

**After:**
```swift
TextField("Username", text: $username)
    .accessibilityIdentifier("usernameTextField")
Button("Log In") { login() }
    .accessibilityIdentifier("loginButton")
Toggle("Dark Mode", isOn: $darkMode)
    .accessibilityIdentifier("darkModeToggle")
```

### UIKit Before/After

**Before:**
```swift
let emailField = UITextField()
let submitButton = UIButton(type: .system)
```

**After:**
```swift
let emailField = UITextField()
emailField.accessibilityIdentifier = "emailTextField"

let submitButton = UIButton(type: .system)
submitButton.accessibilityIdentifier = "submitButton"
```
