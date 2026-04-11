---
title: Custom Actions Missing for Gesture-Only Interactions
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: voiceover, talkback, gestures, custom-actions
---

## Custom Actions Missing for Gesture-Only Interactions

**Priority: P2 (MEDIUM)**

Swipe-to-delete, long-press menus, drag-and-drop, and other gesture-only interactions are inaccessible to screen reader users who navigate with single-finger swipes. These interactions must be exposed as `accessibilityActions` so screen readers can present them as alternatives.

### Detection

```
grep -n 'onLongPress\|Swipeable\|PanGestureHandler\|GestureDetector.*Pan\|onSwipe' **/*.{tsx,jsx,ts,js}
# Flag gesture interactions without corresponding accessibilityActions

grep -n 'Dismissable\|SwipeRow\|SwipeListView\|Swipe.*Action' **/*.{tsx,jsx,ts,js}
# Flag swipeable list items without accessibility actions
```

### Fix Logic

1. Identify all gesture-based interactions (swipe, long-press, drag, pinch)
2. Add `accessibilityActions` array with named actions
3. Add `onAccessibilityAction` handler to perform the action
4. Ensure the action names are descriptive (not "action1", "action2")
5. For swipeable lists, expose delete/archive/etc. as custom actions

### Before/After

**Before:**
```tsx
<Pressable
  onPress={() => openItem(item.id)}
  onLongPress={() => showContextMenu(item)}
  accessibilityLabel={item.title}
  accessibilityRole="button"
>
  <Text>{item.title}</Text>
</Pressable>

<Swipeable
  renderRightActions={() => (
    <Pressable onPress={() => deleteItem(item.id)}>
      <Text>Delete</Text>
    </Pressable>
  )}
>
  <View>
    <Text>{item.title}</Text>
  </View>
</Swipeable>
```

**After:**
```tsx
<Pressable
  onPress={() => openItem(item.id)}
  onLongPress={() => showContextMenu(item)}
  accessibilityLabel={item.title}
  accessibilityRole="button"
  accessibilityActions={[
    { name: 'share', label: 'Share' },
    { name: 'edit', label: 'Edit' },
    { name: 'delete', label: 'Delete' },
  ]}
  onAccessibilityAction={(event) => {
    switch (event.nativeEvent.actionName) {
      case 'share':
        shareItem(item);
        break;
      case 'edit':
        editItem(item);
        break;
      case 'delete':
        deleteItem(item.id);
        break;
    }
  }}
>
  <Text>{item.title}</Text>
</Pressable>

<Swipeable
  renderRightActions={() => (
    <Pressable onPress={() => deleteItem(item.id)}>
      <Text>Delete</Text>
    </Pressable>
  )}
  accessibilityActions={[{ name: 'delete', label: 'Delete' }]}
  onAccessibilityAction={(event) => {
    if (event.nativeEvent.actionName === 'delete') {
      deleteItem(item.id);
    }
  }}
>
  <View accessible={true} accessibilityLabel={item.title}>
    <Text>{item.title}</Text>
  </View>
</Swipeable>
```

### Platform Considerations

- **iOS (VoiceOver):** Custom actions appear when the user swipes up/down on the focused element. VoiceOver announces "Actions available" and the user can cycle through them
- **Android (TalkBack):** Custom actions appear in the TalkBack local context menu (swipe up then right). They are listed as "Custom actions" alongside default actions
- **Both platforms:** The `label` field in `accessibilityActions` is what the screen reader announces. Use clear, descriptive verbs (e.g., "Delete message", "Share photo")
