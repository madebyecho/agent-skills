---
title: Missing Header Roles on Section Titles
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: voiceover, talkback, headers, navigation, roles
---

## Missing Header Roles on Section Titles

**Priority: P2 (MEDIUM)**

Section titles and headings without `accessibilityRole="header"` cannot be navigated using the screen reader's heading navigation. VoiceOver users use the rotor to jump between headings; TalkBack users use heading navigation gestures. Without header roles, users must swipe through every element to find sections.

### Detection

```
grep -n 'fontSize.*[2-9][0-9]\|fontWeight.*bold\|font.*title\|font.*header\|font.*heading' **/*.{tsx,jsx,ts,js}
# Flag large/bold text elements that visually act as section headers but lack accessibilityRole="header"

grep -n 'SectionHeader\|SectionTitle\|ListHeader' **/*.{tsx,jsx,ts,js}
# Flag custom header components without the header role
```

### Fix Logic

1. Identify text elements that visually function as section headings (large, bold, title text)
2. Add `accessibilityRole="header"` to the heading element
3. Do not add header role to every bold text — only true section/page headings
4. For custom header components, add the role to the outermost text or container

### Before/After

**Before:**
```tsx
<Text style={styles.sectionTitle}>Recent Orders</Text>

<View style={styles.header}>
  <Text style={{ fontSize: 24, fontWeight: 'bold' }}>Settings</Text>
</View>

<Text style={styles.screenTitle}>My Profile</Text>
```

**After:**
```tsx
<Text style={styles.sectionTitle} accessibilityRole="header">
  Recent Orders
</Text>

<View style={styles.header}>
  <Text
    style={{ fontSize: 24, fontWeight: 'bold' }}
    accessibilityRole="header"
  >
    Settings
  </Text>
</View>

<Text style={styles.screenTitle} accessibilityRole="header">
  My Profile
</Text>
```

### Platform Considerations

- **iOS (VoiceOver):** `accessibilityRole="header"` maps to the `.header` trait. Users navigate between headers using the VoiceOver rotor set to "Headings"
- **Android (TalkBack):** `accessibilityRole="header"` sets the heading flag on the node. Users navigate between headers using swipe-up/down gesture with navigation set to "Headings"
- **Both platforms:** React Native does not support heading levels (h1-h6). All headers are treated as the same level. If heading hierarchy matters, include it in the label (e.g., "Settings, heading")
