---
title: Color Used as Only Differentiator
priority: P1
impact: HIGH
frameworks: SwiftUI, UIKit
tags: color, differentiate, color-blindness, wcag
---

## Color Used as Only Differentiator

**Priority: P1 (HIGH)**

When color is the only way to convey information (e.g., red = error, green = success), users with color blindness or low vision cannot perceive the distinction. Apple requires apps to "Differentiate Without Color Alone" — always pair color with an icon, text label, shape, or pattern.

### Detection

**SwiftUI:**
```
# Status indicators using only color
grep -n '\.foregroundColor\|\.foregroundStyle\|\.tint' *.swift
# Flag views where color changes convey state but no icon/text accompanies the change

# Conditional color without paired symbol
grep -n 'isError.*\.red\|isSuccess.*\.green\|isWarning.*\.yellow\|isActive.*\.green' *.swift
```

**UIKit:**
```
grep -n '\.textColor = .*red\|\.textColor = .*green\|\.backgroundColor = .*red' *.swift
grep -n 'UIColor.systemRed\|UIColor.systemGreen' *.swift
# Flag conditional color assignments on status elements without accompanying icon/text
```

### Fix Logic

1. Identify elements where color alone indicates status, category, or meaning
2. Add an **icon or SF Symbol** alongside the color (e.g., checkmark for success, xmark for error)
3. Or add a **text label** that communicates the meaning (e.g., "Error", "Success", "Online")
4. Ensure the element is distinguishable in **grayscale** (test with Accessibility > Color Filters > Grayscale)
5. Flag for manual review with `[VERIFY]` — automated detection cannot always distinguish decorative color from informational color

### SwiftUI Before/After

**Before:**
```swift
Circle()
    .fill(user.isOnline ? Color.green : Color.gray)
    .frame(width: 12, height: 12)

Text(errorMessage)
    .foregroundColor(.red)
```

**After:**
```swift
HStack(spacing: 4) {
    Circle()
        .fill(user.isOnline ? Color.green : Color.gray)
        .frame(width: 12, height: 12)
    Text(user.isOnline ? "Online" : "Offline")
        .font(.caption2)
}
// Or use an icon:
Image(systemName: user.isOnline ? "circle.fill" : "circle")
    .foregroundColor(user.isOnline ? .green : .gray)
    .accessibilityLabel(user.isOnline ? "Online" : "Offline")

HStack(spacing: 4) {
    Image(systemName: "exclamationmark.triangle")
    Text(errorMessage)
}
.foregroundColor(.red)
.accessibilityLabel("Error: \(errorMessage)")
```

### UIKit Before/After

**Before:**
```swift
statusDot.backgroundColor = isConnected ? .systemGreen : .systemRed
```

**After:**
```swift
statusDot.backgroundColor = isConnected ? .systemGreen : .systemRed
statusLabel.text = isConnected ? "Connected" : "Disconnected"
statusIcon.image = UIImage(systemName: isConnected ? "checkmark.circle" : "xmark.circle")
```
