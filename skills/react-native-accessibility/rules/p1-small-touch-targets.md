---
title: Touch Targets Below 48x48 dp
priority: P1
impact: HIGH
platforms: iOS, Android
tags: touch-targets, motor, wcag, hig
---

## Touch Targets Below 48x48 dp

**Priority: P1 (HIGH)**

Interactive elements must have a minimum touch target of 48x48 density-independent pixels. This satisfies both the Apple HIG minimum (44pt on iOS) and the Android accessibility guideline (48dp). Small targets cause tap errors for all users and are especially problematic for people with motor impairments. This is also a WCAG 2.5.8 requirement.

### Detection

```
grep -n 'width:\s*[0-9]\+\|height:\s*[0-9]\+' **/*.{tsx,jsx,ts,js}
# Flag interactive elements (Pressable, Touchable*, buttons) where width or height < 48
# Check style objects referenced by interactive components

grep -n 'hitSlop' **/*.{tsx,jsx,ts,js}
# Verify hitSlop is sufficient to bring total target to 48x48
```

### Fix Logic

1. Identify interactive elements with dimensions smaller than 48x48
2. **Prefer expanding the tappable area** without changing visual size:
   - Add `hitSlop` to extend the tap region
   - Or increase `minWidth`/`minHeight` to 48 in the element's style
3. Don't change purely visual, non-interactive elements
4. Consider using `hitSlop={{ top: N, bottom: N, left: N, right: N }}` to center the expanded area

### Before/After

**Before:**
```tsx
<Pressable onPress={dismiss} style={styles.closeButton}>
  <Ionicons name="close" size={16} />
</Pressable>

<TouchableOpacity onPress={showInfo} style={{ width: 24, height: 24 }}>
  <Ionicons name="information-circle" size={20} />
</TouchableOpacity>

const styles = StyleSheet.create({
  closeButton: {
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
```

**After:**
```tsx
<Pressable
  onPress={dismiss}
  style={styles.closeButton}
  hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
  accessibilityLabel="Close"
  accessibilityRole="button"
>
  <Ionicons name="close" size={16} />
</Pressable>

<TouchableOpacity
  onPress={showInfo}
  style={{ width: 24, height: 24 }}
  hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
  accessibilityLabel="More information"
  accessibilityRole="button"
>
  <Ionicons name="information-circle" size={20} />
</TouchableOpacity>

const styles = StyleSheet.create({
  closeButton: {
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
    // hitSlop expands tap target to 48x48 without visual change
  },
});
```

### Platform Considerations

- **iOS (VoiceOver):** VoiceOver uses the element's accessibility frame, which includes `hitSlop`. A 44pt minimum is required by Apple HIG — 48pt satisfies both platforms
- **Android (TalkBack):** Android Material Design guidelines require 48dp minimum. `hitSlop` in React Native maps to expanding the touchable area on both platforms
- **Both platforms:** Prefer `hitSlop` over increasing visual size when the design requires a small icon. Ensure adjacent targets don't overlap after `hitSlop` expansion
