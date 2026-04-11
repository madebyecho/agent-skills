---
title: Missing Accessibility Hints on Interactive Elements
priority: P1
impact: HIGH
platforms: iOS, Android
tags: voiceover, talkback, hints, interactive
---

## Missing Accessibility Hints on Interactive Elements

**Priority: P1 (HIGH)**

Without hints, users don't know what will happen when they activate an element. Hints are read after a pause and describe the result of the action. On iOS, VoiceOver reads hints after the label and role. On Android, TalkBack reads them as part of the element description.

### Detection

```
grep -n 'accessibilityLabel=' **/*.{tsx,jsx,ts,js}
# Flag interactive elements (Pressable, Touchable*, Button) with a label but no accessibilityHint
# within the same element's props
```

### Fix Logic

1. Infer hint from: `onPress` handler name, surrounding context, element purpose
2. Hints describe the **result**, not the **gesture** — avoid "Tap to..." or "Double-tap to..."
3. Start with a verb: "Opens...", "Removes...", "Toggles..."
4. Add `[VERIFY]` marker on inferred hints

### Before/After

**Before:**
```tsx
<Pressable
  onPress={deleteItem}
  accessibilityLabel="Delete item"
  accessibilityRole="button"
>
  <Text>Delete</Text>
</Pressable>

<TouchableOpacity
  onPress={() => navigation.navigate('Profile')}
  accessibilityLabel="Profile"
  accessibilityRole="button"
>
  <Ionicons name="person" size={24} />
</TouchableOpacity>
```

**After:**
```tsx
<Pressable
  onPress={deleteItem}
  accessibilityLabel="Delete item"
  accessibilityRole="button"
  accessibilityHint="Removes this item permanently" // [VERIFY] confirm hint accuracy
>
  <Text>Delete</Text>
</Pressable>

<TouchableOpacity
  onPress={() => navigation.navigate('Profile')}
  accessibilityLabel="Profile"
  accessibilityRole="button"
  accessibilityHint="Opens your profile page" // [VERIFY] confirm hint accuracy
>
  <Ionicons name="person" size={24} />
</TouchableOpacity>
```

### Platform Considerations

- **iOS (VoiceOver):** Hints are read after a short delay following the label and role. Users can disable hints in VoiceOver settings, so essential info should always be in the label
- **Android (TalkBack):** `accessibilityHint` is announced as "usage hint" — TalkBack may say "Double tap to [hint]" depending on the element's role
