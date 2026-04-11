---
title: Missing Focus Management for Custom Modals
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: focus, modals, voiceover, talkback, navigation
---

## Missing Focus Management for Custom Modals

**Priority: P2 (MEDIUM)**

When custom modals, bottom sheets, or overlay dialogs appear, screen reader focus must move to the new content and be trapped within it. When dismissed, focus must return to the trigger element. Background content behind modals must not be reachable. React Native's built-in `<Modal>` handles this automatically, but custom implementations often fail.

### Detection

```
grep -n '<Modal\b' **/*.{tsx,jsx,ts,js}
# Check if using RN's built-in Modal (handles focus automatically) or a custom implementation

grep -n 'position.*absolute.*zIndex\|position.*absolute.*elevation' **/*.{tsx,jsx,ts,js}
# Flag custom overlay/modal patterns using absolute positioning

grep -n 'BottomSheet\|ActionSheet\|Overlay\|Drawer\|Popup\|Dialog' **/*.{tsx,jsx,ts,js}
# Flag third-party modal components — verify they handle focus trapping

grep -n 'accessibilityViewIsModal' **/*.{tsx,jsx,ts,js}
# Find existing focus management
```

### Fix Logic

1. **Built-in `<Modal>`**: Handles focus trapping automatically — no fix needed
2. **Custom overlays**: Add `accessibilityViewIsModal={true}` on the modal container
3. **Focus on open**: Use `AccessibilityInfo.announceForAccessibility()` or set `autoFocus` on the first focusable element
4. **Background hiding**: Add `importantForAccessibility="no-hide-descendants"` on the background content (Android) and `accessibilityElementsHidden={true}` (iOS)
5. **Focus on dismiss**: Return focus to the trigger element using a ref

### Before/After

**Before:**
```tsx
function CustomBottomSheet({ visible, onClose, children }) {
  if (!visible) return null;

  return (
    <View style={StyleSheet.absoluteFill}>
      <Pressable style={styles.backdrop} onPress={onClose} />
      <View style={styles.sheet}>
        {children}
        <Pressable onPress={onClose}>
          <Text>Close</Text>
        </Pressable>
      </View>
    </View>
  );
}

function ParentScreen() {
  const [showSheet, setShowSheet] = useState(false);

  return (
    <View>
      <MainContent />
      <Pressable onPress={() => setShowSheet(true)}>
        <Text>Open Sheet</Text>
      </Pressable>
      <CustomBottomSheet visible={showSheet} onClose={() => setShowSheet(false)}>
        <Text>Sheet Content</Text>
      </CustomBottomSheet>
    </View>
  );
}
```

**After:**
```tsx
function CustomBottomSheet({ visible, onClose, children }) {
  if (!visible) return null;

  return (
    <View style={StyleSheet.absoluteFill}>
      <Pressable
        style={styles.backdrop}
        onPress={onClose}
        accessible={false}
        importantForAccessibility="no"
      />
      <View
        style={styles.sheet}
        accessibilityViewIsModal={true}
        accessibilityRole="none"
      >
        {children}
        <Pressable
          onPress={onClose}
          accessibilityLabel="Close"
          accessibilityRole="button"
        >
          <Text>Close</Text>
        </Pressable>
      </View>
    </View>
  );
}

function ParentScreen() {
  const [showSheet, setShowSheet] = useState(false);
  const triggerRef = useRef(null);

  return (
    <View
      importantForAccessibility={showSheet ? 'no-hide-descendants' : 'auto'}
      accessibilityElementsHidden={showSheet}
    >
      <MainContent />
      <Pressable
        ref={triggerRef}
        onPress={() => setShowSheet(true)}
        accessibilityRole="button"
      >
        <Text>Open Sheet</Text>
      </Pressable>
    </View>

    <CustomBottomSheet
      visible={showSheet}
      onClose={() => {
        setShowSheet(false);
        // Return focus to trigger
        triggerRef.current?.focus();
      }}
    >
      <Text>Sheet Content</Text>
    </CustomBottomSheet>
  );
}
```

### Platform Considerations

- **iOS (VoiceOver):** `accessibilityViewIsModal={true}` tells VoiceOver to confine navigation within this view, ignoring sibling elements. This is the primary mechanism for focus trapping on iOS
- **Android (TalkBack):** `importantForAccessibility="no-hide-descendants"` on the background content hides it from TalkBack. Android doesn't have a direct equivalent of `accessibilityViewIsModal`, so background hiding is essential
- **Both platforms:** React Native's built-in `<Modal>` component handles focus management on both platforms. Prefer using it over custom overlay implementations when possible
