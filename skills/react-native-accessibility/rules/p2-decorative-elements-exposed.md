---
title: Decorative Elements Exposed to Accessibility Tree
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: voiceover, talkback, decorative, hidden
---

## Decorative Elements Exposed to Accessibility Tree

**Priority: P2 (MEDIUM)**

Decorative images, separators, background graphics, and ornamental elements that are exposed to the accessibility tree create noise for screen reader users. They must swipe through meaningless elements, slowing navigation and causing confusion.

### Detection

```
grep -n '<View.*style.*separator\|<View.*style.*divider\|<View.*style.*line' **/*.{tsx,jsx,ts,js}
# Flag separator/divider elements not hidden from accessibility

grep -n '<Image.*background\|<Image.*decoration\|<Image.*ornament\|<Image.*pattern' **/*.{tsx,jsx,ts,js}
# Flag decorative images not hidden

grep -n 'opacity:\s*0\|pointerEvents.*none' **/*.{tsx,jsx,ts,js}
# Flag invisible elements that may still be in the accessibility tree
```

### Fix Logic

1. Identify decorative elements: separators, dividers, background images, ornamental icons, spacer views
2. Add `accessible={false}` to remove from the accessibility tree
3. Add platform-specific hiding for reliable behavior:
   - `importantForAccessibility="no"` for Android
   - `accessibilityElementsHidden={true}` for iOS
4. Do not hide elements that convey meaning — only purely decorative ones

### Before/After

**Before:**
```tsx
<View style={styles.separator} />

<Image
  source={require('./assets/wave-bg.png')}
  style={styles.backgroundDecoration}
/>

<View style={styles.spacer} />

<Ionicons name="sparkles" size={12} color="#ccc" />
```

**After:**
```tsx
<View
  style={styles.separator}
  accessible={false}
  importantForAccessibility="no"
  accessibilityElementsHidden={true}
/>

<Image
  source={require('./assets/wave-bg.png')}
  style={styles.backgroundDecoration}
  accessible={false}
  importantForAccessibility="no"
  accessibilityElementsHidden={true}
/>

<View
  style={styles.spacer}
  accessible={false}
  importantForAccessibility="no"
/>

<Ionicons
  name="sparkles"
  size={12}
  color="#ccc"
  accessible={false}
  importantForAccessibility="no"
  accessibilityElementsHidden={true}
/>
```

### Platform Considerations

- **iOS (VoiceOver):** `accessibilityElementsHidden={true}` hides the element and all its children from VoiceOver. This is the most reliable method on iOS
- **Android (TalkBack):** `importantForAccessibility="no"` hides the element from TalkBack. Use `"no-hide-descendants"` to also hide all children
- **Both platforms:** `accessible={false}` works cross-platform but combining it with platform-specific props ensures consistent behavior across OS versions
