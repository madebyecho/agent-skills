---
title: Hardcoded Font Sizes Break Dynamic Type
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: dynamic-type, fonts, wcag
---

## Hardcoded Font Sizes Break Dynamic Type

**Priority: P2 (MEDIUM)**

Hardcoded font sizes don't scale with Dynamic Type, breaking readability for low-vision users. All text must use semantic font styles or scale via `UIFontMetrics`.

### Detection

**SwiftUI:**
```
grep -n '\.font(\.system(size:' *.swift
grep -n '\.font(\.custom(.*size:' *.swift
```

**UIKit:**
```
grep -n 'UIFont\.systemFont(ofSize:' *.swift
grep -n 'UIFont\.boldSystemFont(ofSize:' *.swift
grep -n 'UIFont(name:.*size:' *.swift
```

### Fix Logic

1. Map hardcoded size to nearest semantic style using the table below
2. SwiftUI: Replace `.font(.system(size: N))` with `.font(.styleName)`
3. UIKit: Replace `UIFont.systemFont(ofSize: N)` with `UIFont.preferredFont(forTextStyle:)`
4. UIKit: Add `adjustsFontForContentSizeCategory = true`
5. Custom fonts: Wrap with `UIFontMetrics` or use `relativeTo:` parameter

### Size Mapping

| Hardcoded Size | SwiftUI Style | UIKit `TextStyle` |
|---------------|---------------|-------------------|
| 34+ | `.largeTitle` | `.largeTitle` |
| 28–33 | `.title` | `.title1` |
| 22–27 | `.title2` | `.title2` |
| 20–21 | `.title3` | `.title3` |
| 17–19 | `.headline` / `.body` | `.headline` / `.body` |
| 15–16 | `.subheadline` / `.callout` | `.subheadline` / `.callout` |
| 13–14 | `.footnote` | `.footnote` |
| 11–12 | `.caption` / `.caption2` | `.caption1` / `.caption2` |

### SwiftUI Before/After

**Before:**
```swift
Text("Welcome")
    .font(.system(size: 24, weight: .bold))
Text("Subtitle")
    .font(.system(size: 14))
Text("Custom")
    .font(.custom("Avenir-Medium", size: 16))
```

**After:**
```swift
Text("Welcome")
    .font(.title2.bold())
Text("Subtitle")
    .font(.footnote)
Text("Custom")
    .font(.custom("Avenir-Medium", size: 16, relativeTo: .body))
```

### UIKit Before/After

**Before:**
```swift
label.font = UIFont.systemFont(ofSize: 16)
titleLabel.font = UIFont.boldSystemFont(ofSize: 24)
customLabel.font = UIFont(name: "Avenir-Medium", size: 16)
```

**After:**
```swift
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true

titleLabel.font = UIFont.preferredFont(forTextStyle: .title2)
titleLabel.adjustsFontForContentSizeCategory = true

let customFont = UIFont(name: "Avenir-Medium", size: 16)!
customLabel.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)
customLabel.adjustsFontForContentSizeCategory = true
```
