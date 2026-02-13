---
title: Rule Title Here
priority: P0|P1|P2|P3
impact: CRITICAL|HIGH|MEDIUM|LOW
frameworks: SwiftUI, UIKit
tags: tag1, tag2
---

## Rule Title Here

**Priority: P0 (CRITICAL)**

Brief explanation of the rule, why it matters, and what impact it has on accessibility.

### Detection

**SwiftUI:**
```
grep -n 'pattern' *.swift
# Description of what this catches
```

**UIKit:**
```
grep -n 'pattern' *.swift
# Description of what this catches
```

### Fix Logic

1. Step one of the fix
2. Step two of the fix
3. Always add `[VERIFY]` marker if label is inferred

### SwiftUI Before/After

**Before:**
```swift
// Bad code example
```

**After:**
```swift
// Good code example
```

### UIKit Before/After

**Before:**
```swift
// Bad code example
```

**After:**
```swift
// Good code example
```
