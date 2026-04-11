---
title: Ungrouped Related Elements
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: voiceover, talkback, grouping, navigation
---

## Ungrouped Related Elements

**Priority: P2 (MEDIUM)**

When related elements (e.g., an icon and its text label, or a profile image and a name) are not grouped, screen readers announce them as separate items. This creates excessive swipe/navigation steps and loses the relationship between elements.

### Detection

```
grep -n '<View\b\|<HStack\|<Row' **/*.{tsx,jsx,ts,js}
# Flag containers with an icon/image + text that don't have accessible={true}
# Look for patterns: <Icon> followed by <Text> inside a <View> without grouping
```

### Fix Logic

1. Identify containers with related visual elements (icon + text, image + name, etc.)
2. Add `accessible={true}` on the container `<View>` to group children
3. Add a composed `accessibilityLabel` that combines the children's content
4. Children inside a grouped container are automatically hidden from the accessibility tree
5. If children have interactive elements, don't group — only group non-interactive related content

### Before/After

**Before:**
```tsx
<View style={styles.statusRow}>
  <Ionicons name="checkmark-circle" size={16} color="green" />
  <Text>Order Confirmed</Text>
</View>

<View style={styles.userRow}>
  <Image source={{ uri: user.avatar }} style={styles.avatar} />
  <Text>{user.name}</Text>
  <Text style={styles.subtitle}>{user.role}</Text>
</View>
```

**After:**
```tsx
<View
  style={styles.statusRow}
  accessible={true}
  accessibilityLabel="Order Confirmed"
  accessibilityRole="text"
>
  <Ionicons name="checkmark-circle" size={16} color="green" />
  <Text>Order Confirmed</Text>
</View>

<View
  style={styles.userRow}
  accessible={true}
  accessibilityLabel={`${user.name}, ${user.role}`}
>
  <Image source={{ uri: user.avatar }} style={styles.avatar} />
  <Text>{user.name}</Text>
  <Text style={styles.subtitle}>{user.role}</Text>
</View>
```

### Platform Considerations

- **iOS (VoiceOver):** `accessible={true}` on a `<View>` creates a single accessibility element. VoiceOver reads the `accessibilityLabel` in one swipe instead of multiple
- **Android (TalkBack):** `accessible={true}` sets `importantForAccessibility="yes"` and groups children. TalkBack announces the entire group as one element
- **Both platforms:** Do not group elements that contain interactive children (buttons, links) — grouping would make them unreachable. Only group purely informational content
