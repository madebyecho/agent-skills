---
title: Font Scaling Disabled or Restricted
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: dynamic-type, font-scaling, vision, wcag
---

## Font Scaling Disabled or Restricted

**Priority: P2 (MEDIUM)**

React Native respects the system font size by default, but developers sometimes disable scaling with `allowFontScaling={false}` or restrict it with a low `maxFontSizeMultiplier`. This prevents users with low vision from enlarging text to a readable size. WCAG 1.4.4 requires text to scale to at least 200% without loss of content.

### Detection

```
grep -n 'allowFontScaling.*false\|allowFontScaling={false}' **/*.{tsx,jsx,ts,js}
# Flag any Text or TextInput with font scaling disabled

grep -n 'maxFontSizeMultiplier' **/*.{tsx,jsx,ts,js}
# Flag if maxFontSizeMultiplier < 2.0

grep -n 'Text.defaultProps.*allowFontScaling\|TextInput.defaultProps.*allowFontScaling' **/*.{tsx,jsx,ts,js}
# Flag global disabling of font scaling via defaultProps
```

### Fix Logic

1. Remove `allowFontScaling={false}` from `<Text>` and `<TextInput>` elements
2. If `maxFontSizeMultiplier` is set below 2.0, increase it to at least 2.0
3. Remove any global `Text.defaultProps.allowFontScaling = false` statements
4. If layout breaks at large font sizes, fix the layout (use flex, ScrollView) instead of disabling scaling
5. Exception: fixed-size UI elements like tab bars or toolbars may use `maxFontSizeMultiplier={1.5}` — add a comment explaining why

### Before/After

**Before:**
```tsx
// Global override — disables font scaling everywhere
Text.defaultProps = { ...Text.defaultProps, allowFontScaling: false };

<Text style={styles.title} allowFontScaling={false}>
  Welcome Back
</Text>

<TextInput
  style={styles.input}
  placeholder="Search"
  maxFontSizeMultiplier={1.2}
/>

<Text style={styles.price} maxFontSizeMultiplier={1.0}>
  $29.99
</Text>
```

**After:**
```tsx
// Removed global font scaling override

<Text style={styles.title}>
  Welcome Back
</Text>

<TextInput
  style={styles.input}
  placeholder="Search"
  maxFontSizeMultiplier={2.0}
/>

<Text style={styles.price} maxFontSizeMultiplier={2.0}>
  $29.99
</Text>
```

### Platform Considerations

- **iOS (VoiceOver/Dynamic Type):** iOS users adjust text size in Settings > Accessibility > Display & Text Size > Larger Text. React Native's `allowFontScaling` maps to Dynamic Type support
- **Android (TalkBack):** Android users adjust font size in Settings > Accessibility > Font size. React Native respects this when `allowFontScaling` is true (the default)
- **Both platforms:** Test at the maximum system font size to ensure layouts don't break. Use `ScrollView` for content that may overflow, and flexible layouts that reflow instead of truncating
