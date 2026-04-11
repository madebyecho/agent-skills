---
title: Missing Labels on Text Inputs
priority: P1
impact: HIGH
platforms: iOS, Android
tags: voiceover, talkback, inputs, forms, labels
---

## Missing Labels on Text Inputs

**Priority: P1 (HIGH)**

`TextInput` elements without `accessibilityLabel` are announced only by their placeholder text (if any) or not announced at all. Placeholder text disappears when the user starts typing, leaving them with no context about what the field is for.

### Detection

```
grep -n '<TextInput\b' **/*.{tsx,jsx,ts,js}
# Flag if no accessibilityLabel prop is set on the TextInput
# Check if a sibling <Text> element could serve as the label
```

### Fix Logic

1. Check if the `TextInput` already has an `accessibilityLabel` — if so, skip
2. Infer label from: `placeholder` prop, sibling `<Text>` content, field name in state
3. Add `accessibilityLabel` with the inferred value
4. Add `[VERIFY]` marker on inferred labels
5. Do not remove `placeholder` — it still serves as visual hint

### Before/After

**Before:**
```tsx
<TextInput
  placeholder="Enter your email"
  value={email}
  onChangeText={setEmail}
  keyboardType="email-address"
/>

<View>
  <Text style={styles.label}>Password</Text>
  <TextInput
    placeholder="••••••••"
    value={password}
    onChangeText={setPassword}
    secureTextEntry
  />
</View>

<TextInput
  value={searchQuery}
  onChangeText={setSearchQuery}
  style={styles.searchInput}
/>
```

**After:**
```tsx
<TextInput
  placeholder="Enter your email"
  value={email}
  onChangeText={setEmail}
  keyboardType="email-address"
  accessibilityLabel="Email address" // [VERIFY] confirm label matches intent
/>

<View>
  <Text style={styles.label}>Password</Text>
  <TextInput
    placeholder="••••••••"
    value={password}
    onChangeText={setPassword}
    secureTextEntry
    accessibilityLabel="Password"
  />
</View>

<TextInput
  value={searchQuery}
  onChangeText={setSearchQuery}
  style={styles.searchInput}
  accessibilityLabel="Search" // [VERIFY] confirm label matches intent
  accessibilityRole="search"
/>
```

### Platform Considerations

- **iOS (VoiceOver):** VoiceOver reads `accessibilityLabel` then "text field". If the field has a value, it reads the value after the label
- **Android (TalkBack):** TalkBack reads the label, then "edit box", then the current value. If `accessibilityLabel` is not set, TalkBack falls back to `placeholder` but this is unreliable across Android versions
- **Both platforms:** For search inputs, also add `accessibilityRole="search"` to convey the field's purpose
