---
title: Missing Accessibility Roles on Interactive Elements
priority: P1
impact: HIGH
platforms: iOS, Android
tags: voiceover, talkback, roles, interactive
---

## Missing Accessibility Roles on Interactive Elements

**Priority: P1 (HIGH)**

Without `accessibilityRole`, screen readers cannot communicate the type of element to the user. A Pressable without a role is announced as a generic element — users don't know they can activate it. Roles also affect the gestures and actions screen readers expose.

### Detection

```
grep -n '<Pressable\|<TouchableOpacity\|<TouchableHighlight\|<TouchableWithoutFeedback' **/*.{tsx,jsx,ts,js}
# Flag if no accessibilityRole prop is set on the element

grep -n '<Switch\b\|<Checkbox\b' **/*.{tsx,jsx,ts,js}
# Flag custom Switch/Checkbox components without accessibilityRole="switch" or "checkbox"
```

### Fix Logic

1. Determine the correct role from the element's purpose:
   - Navigation actions → `"button"` or `"link"`
   - Toggles → `"switch"` or `"checkbox"`
   - Tab bars → `"tab"`
   - Expandable sections → `"button"` (with `accessibilityState={{ expanded }}`
   - Headers → `"header"`
   - Search fields → `"search"`
   - Adjustable controls → `"adjustable"`
2. Apply `accessibilityRole` to the outermost interactive wrapper
3. Do not apply roles to non-interactive elements unless they are headers or images

### Before/After

**Before:**
```tsx
<Pressable onPress={handleSubmit}>
  <Text>Submit</Text>
</Pressable>

<TouchableOpacity onPress={() => setEnabled(!enabled)}>
  <View style={[styles.toggle, enabled && styles.toggleOn]} />
</TouchableOpacity>

<Pressable onPress={() => setExpanded(!expanded)}>
  <Text>Show Details</Text>
  <Ionicons name={expanded ? 'chevron-up' : 'chevron-down'} />
</Pressable>
```

**After:**
```tsx
<Pressable
  onPress={handleSubmit}
  accessibilityRole="button"
>
  <Text>Submit</Text>
</Pressable>

<TouchableOpacity
  onPress={() => setEnabled(!enabled)}
  accessibilityRole="switch"
  accessibilityState={{ checked: enabled }}
  accessibilityLabel="Enable notifications" // [VERIFY] confirm label matches intent
>
  <View style={[styles.toggle, enabled && styles.toggleOn]} />
</TouchableOpacity>

<Pressable
  onPress={() => setExpanded(!expanded)}
  accessibilityRole="button"
  accessibilityState={{ expanded }}
>
  <Text>Show Details</Text>
  <Ionicons name={expanded ? 'chevron-up' : 'chevron-down'} />
</Pressable>
```

### Platform Considerations

- **iOS (VoiceOver):** Roles map to UIKit accessibility traits. `"button"` → `.button`, `"header"` → `.header`, `"link"` → `.link`, `"switch"` → `.switchButton`
- **Android (TalkBack):** Roles map to Android accessibility class names. `"button"` → `android.widget.Button`, `"switch"` → `android.widget.Switch`
- **Both platforms:** Always pair `accessibilityRole="switch"` or `"checkbox"` with `accessibilityState={{ checked: value }}` so screen readers announce the current state
