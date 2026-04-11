---
title: Rule Title Here
priority: P0|P1|P2
impact: CRITICAL|HIGH|MEDIUM
platforms: iOS, Android
tags: tag1, tag2
---

## Rule Title Here

**Priority: P0 (CRITICAL)**

Brief explanation of the rule, why it matters, and what impact it has on accessibility.

### Detection

```
grep -n 'pattern' **/*.{tsx,jsx,ts,js}
# Description of what this catches
```

### Fix Logic

1. Step one of the fix
2. Step two of the fix
3. Always add `[VERIFY]` marker if label is inferred

### Before/After

**Before:**
```tsx
// Bad code example
```

**After:**
```tsx
// Good code example
```

### Platform Considerations

- **iOS (VoiceOver):** Note any iOS-specific behavior or props
- **Android (TalkBack):** Note any Android-specific behavior or props
