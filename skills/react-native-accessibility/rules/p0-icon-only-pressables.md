---
title: Icon-Only Pressable Elements Without Labels
priority: P0
impact: CRITICAL
platforms: iOS, Android
tags: voiceover, talkback, buttons, pressable, labels
---

## Icon-Only Pressable Elements Without Labels

**Priority: P0 (CRITICAL)**

Pressable elements (Pressable, TouchableOpacity, TouchableHighlight, TouchableWithoutFeedback) that contain only an icon and no text are announced as "button" with no description. Users cannot determine what the button does.

### Detection

```
grep -n '<Pressable\|<TouchableOpacity\|<TouchableHighlight\|<TouchableWithoutFeedback' **/*.{tsx,jsx,ts,js}
# Flag if the pressable wraps only an icon component (MaterialIcons, Ionicons, Feather, Svg, Image)
# and has no accessibilityLabel prop on the wrapper
```

### Fix Logic

1. Infer label from: icon name, `onPress` handler name, surrounding context
2. Apply `accessibilityLabel` on the **wrapper Pressable**, not the icon inside it
3. Add `accessibilityRole="button"` if missing
4. Add `[VERIFY]` marker on all inferred labels

### Before/After

**Before:**
```tsx
<Pressable onPress={toggleFavorite}>
  <Ionicons name="heart" size={24} color="red" />
</Pressable>

<TouchableOpacity onPress={() => navigation.navigate('Settings')}>
  <MaterialIcons name="settings" size={28} />
</TouchableOpacity>

<TouchableOpacity onPress={handleDelete} style={styles.iconButton}>
  <Svg width={20} height={20} viewBox="0 0 20 20">
    <Path d="M6 6l8 8M14 6l-8 8" stroke="red" />
  </Svg>
</TouchableOpacity>
```

**After:**
```tsx
<Pressable
  onPress={toggleFavorite}
  accessibilityLabel="Toggle favorite" // [VERIFY] confirm label matches intent
  accessibilityRole="button"
>
  <Ionicons name="heart" size={24} color="red" />
</Pressable>

<TouchableOpacity
  onPress={() => navigation.navigate('Settings')}
  accessibilityLabel="Settings" // [VERIFY] confirm label matches intent
  accessibilityRole="button"
>
  <MaterialIcons name="settings" size={28} />
</TouchableOpacity>

<TouchableOpacity
  onPress={handleDelete}
  style={styles.iconButton}
  accessibilityLabel="Delete" // [VERIFY] confirm label matches intent
  accessibilityRole="button"
>
  <Svg width={20} height={20} viewBox="0 0 20 20" accessible={false}>
    <Path d="M6 6l8 8M14 6l-8 8" stroke="red" />
  </Svg>
</TouchableOpacity>
```

### Platform Considerations

- **iOS (VoiceOver):** `accessibilityRole="button"` maps to the UIKit button trait — VoiceOver announces "button" after the label
- **Android (TalkBack):** `accessibilityRole="button"` sets the Android `className` to `android.widget.Button` — TalkBack announces "Double tap to activate"
- **Both platforms:** The label should be on the outermost pressable wrapper; nested icons should be hidden with `accessible={false}` if the parent has the label
