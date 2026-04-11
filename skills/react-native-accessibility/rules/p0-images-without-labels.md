---
title: Images Without Accessibility Labels
priority: P0
impact: CRITICAL
platforms: iOS, Android
tags: voiceover, talkback, images, labels
---

## Images Without Accessibility Labels

**Priority: P0 (CRITICAL)**

Informational images without accessibility labels are completely invisible to VoiceOver and TalkBack users. Every meaningful image must have a label; every decorative image must be hidden from the accessibility tree.

### Detection

```
grep -n '<Image\b' **/*.{tsx,jsx,ts,js}
grep -n '<ExpoImage\b\|<Image.*from.*expo-image' **/*.{tsx,jsx,ts,js}
grep -n '<Svg\b\|<SvgUri\b\|<SvgXml\b' **/*.{tsx,jsx,ts,js}
# Flag if no accessibilityLabel prop within the element
# Flag if accessible={false} is not set on decorative images
```

### Fix Logic

1. Determine if image is **informational** or **decorative**:
   - Decorative (backgrounds, separators, ornaments) → add `accessible={false}` and platform-specific hiding
   - Informational (icons, photos, meaningful graphics) → add `accessibilityLabel="description"` with `[VERIFY]`
2. Infer label from: image source name, `require()` path, surrounding context
3. Always add `[VERIFY]` marker on inferred labels
4. For `expo-image` `<Image>`, use the same `accessibilityLabel` prop

### Before/After

**Before:**
```tsx
<Image source={require('./assets/product-photo.png')} style={styles.photo} />

<Image source={{ uri: user.avatarUrl }} style={styles.avatar} />

<Svg width={24} height={24} viewBox="0 0 24 24">
  <Path d="M12 2L2 7l10 5 10-5-10-5z" />
</Svg>

<Image source={require('./assets/divider.png')} style={styles.divider} />
```

**After:**
```tsx
<Image
  source={require('./assets/product-photo.png')}
  style={styles.photo}
  accessibilityLabel="Product photo" // [VERIFY] confirm label matches intent
/>

<Image
  source={{ uri: user.avatarUrl }}
  style={styles.avatar}
  accessibilityLabel={`${user.name}'s profile photo`} // [VERIFY] confirm label matches intent
/>

<Svg
  width={24}
  height={24}
  viewBox="0 0 24 24"
  accessibilityLabel="Location pin" // [VERIFY] confirm label matches intent
>
  <Path d="M12 2L2 7l10 5 10-5-10-5z" />
</Svg>

{/* Decorative — hidden from screen readers */}
<Image
  source={require('./assets/divider.png')}
  style={styles.divider}
  accessible={false}
  importantForAccessibility="no"
  accessibilityElementsHidden={true}
/>
```

### Platform Considerations

- **iOS (VoiceOver):** Use `accessibilityElementsHidden={true}` to hide decorative images from VoiceOver
- **Android (TalkBack):** Use `importantForAccessibility="no"` to hide decorative images from TalkBack
- **Both platforms:** `accessible={false}` works cross-platform but adding platform-specific props ensures reliable hiding
