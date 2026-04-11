---
title: Color Used as the Only Way to Convey Information
priority: P1
impact: HIGH
platforms: iOS, Android
tags: color, wcag, vision, color-blindness
---

## Color Used as the Only Way to Convey Information

**Priority: P1 (HIGH)**

When color is the sole indicator of status, state, or category, users with color vision deficiencies cannot distinguish the information. Approximately 8% of men and 0.5% of women have some form of color blindness. Color must always be paired with a secondary indicator: an icon, text label, pattern, or shape.

### Detection

```
grep -n 'color.*red\|color.*green\|color.*#[fF][0-9a-fA-F]\{5\}\|color.*#[0-9a-fA-F]\{2\}[fF][fF]' **/*.{tsx,jsx,ts,js}
# Flag color-only status indicators (red/green for error/success, colored dots)

grep -n 'backgroundColor.*error\|backgroundColor.*success\|backgroundColor.*warning' **/*.{tsx,jsx,ts,js}
# Flag semantic color usage that may be color-only
```

### Fix Logic

1. Identify elements where color is the only differentiator (e.g., red/green dots, colored badges)
2. Add a secondary indicator:
   - Icon (checkmark for success, X for error)
   - Text label ("Active", "Error", "Pending")
   - Shape variation (filled vs outlined)
3. Ensure the secondary indicator is also accessible (has a label if it's an icon)
4. Add `[VERIFY]` marker when flagging for manual review

### Before/After

**Before:**
```tsx
{/* Status shown only by color */}
<View style={[styles.dot, { backgroundColor: isOnline ? 'green' : 'red' }]} />

{/* Form validation with color only */}
<TextInput
  style={[styles.input, { borderColor: hasError ? 'red' : 'gray' }]}
  value={email}
  onChangeText={setEmail}
/>
```

**After:**
```tsx
{/* Status shown with color + icon + label */}
<View style={styles.statusRow}>
  <View
    style={[styles.dot, { backgroundColor: isOnline ? 'green' : 'red' }]}
    accessible={false}
  />
  <Ionicons
    name={isOnline ? 'checkmark-circle' : 'close-circle'}
    color={isOnline ? 'green' : 'red'}
    size={16}
    accessible={false}
  />
  <Text accessibilityLabel={isOnline ? 'Online' : 'Offline'}>
    {isOnline ? 'Online' : 'Offline'}
  </Text>
</View>

{/* Form validation with color + icon + error text */}
<TextInput
  style={[styles.input, { borderColor: hasError ? 'red' : 'gray' }]}
  value={email}
  onChangeText={setEmail}
  accessibilityLabel="Email address"
/>
{hasError && (
  <View style={styles.errorRow}>
    <Ionicons name="alert-circle" size={14} color="red" accessible={false} />
    <Text style={styles.errorText} accessibilityRole="alert">
      Please enter a valid email address
    </Text>
  </View>
)}
```

### Platform Considerations

- **iOS (VoiceOver):** VoiceOver does not convey color information. The text label and icon provide the essential information
- **Android (TalkBack):** TalkBack similarly cannot convey color. Using `accessibilityRole="alert"` on error messages ensures TalkBack announces errors immediately
- **Both platforms:** Test the app with the platform's grayscale/color filter mode to verify all information is still distinguishable
