---
title: Missing Header Traits
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: voiceover, headers, navigation, rotor
---

## Missing Header Traits

**Priority: P2 (MEDIUM)**

Without header traits, VoiceOver users cannot navigate by headings using the rotor. This makes long screens difficult to scan — users must swipe through every element instead of jumping between sections.

### Detection

**SwiftUI:**
```
grep -n '\.font(.*\.title\|\.font(.*\.headline\|\.font(.*\.largeTitle' *.swift
# Flag text with heading-style fonts missing .accessibilityAddTraits(.isHeader)
```

**UIKit:**
```
grep -n 'preferredFont.*headline\|preferredFont.*title' *.swift
# Flag labels with heading-style fonts missing accessibilityTraits = .header
```

### Fix Logic

1. Identify text elements with heading-style fonts (title, headline, largeTitle)
2. Confirm they serve as section headers (not just bold styling)
3. SwiftUI: Add `.accessibilityAddTraits(.isHeader)`
4. UIKit: Set `accessibilityTraits = .header` (or add `.header` to existing traits)

### SwiftUI Before/After

**Before:**
```swift
Text("Payment Methods")
    .font(.title2)
    .bold()

Text("Account Settings")
    .font(.headline)
```

**After:**
```swift
Text("Payment Methods")
    .font(.title2)
    .bold()
    .accessibilityAddTraits(.isHeader)

Text("Account Settings")
    .font(.headline)
    .accessibilityAddTraits(.isHeader)
```

### UIKit Before/After

**Before:**
```swift
let headerLabel = UILabel()
headerLabel.font = UIFont.preferredFont(forTextStyle: .headline)
headerLabel.text = "Account Settings"
```

**After:**
```swift
let headerLabel = UILabel()
headerLabel.font = UIFont.preferredFont(forTextStyle: .headline)
headerLabel.text = "Account Settings"
headerLabel.accessibilityTraits = .header
```
