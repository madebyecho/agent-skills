---
title: Dynamic Content Updates Not Announced
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: voiceover, talkback, live-region, announcements, dynamic
---

## Dynamic Content Updates Not Announced

**Priority: P2 (MEDIUM)**

When content changes dynamically (loading states, toast notifications, error messages, counters, real-time updates), screen reader users are not informed unless the update is explicitly announced. Without live regions or manual announcements, users don't know that new content has appeared.

### Detection

```
grep -n 'useState\|useReducer' **/*.{tsx,jsx,ts,js}
# Identify state variables that drive UI updates — cross-reference with rendered text

grep -n 'Toast\|Snackbar\|Alert\|notification\|loading\|error\|isLoading\|isError' **/*.{tsx,jsx,ts,js}
# Flag dynamic status indicators without accessibilityLiveRegion or announcements

grep -n 'accessibilityLiveRegion\|announceForAccessibility' **/*.{tsx,jsx,ts,js}
# Find existing live region usage to gauge coverage
```

### Fix Logic

1. Identify content that changes dynamically after the initial render
2. For persistent updates (counters, status text) → add `accessibilityLiveRegion` to the container
   - `"polite"` — announces after the screen reader finishes current speech
   - `"assertive"` — interrupts current speech (use for urgent updates like errors)
3. For transient updates (toasts, snackbars) → use `AccessibilityInfo.announceForAccessibility()`
4. Don't make frequently updating content (timers, progress bars) live regions — it creates excessive announcements

### Before/After

**Before:**
```tsx
{/* Counter with no announcement */}
<Text>{cartItems.length} items in cart</Text>

{/* Error state with no announcement */}
{error && <Text style={styles.error}>{error.message}</Text>}

{/* Toast notification with no announcement */}
{showToast && (
  <View style={styles.toast}>
    <Text>Item added to cart</Text>
  </View>
)}
```

**After:**
```tsx
{/* Counter announced politely when changed */}
<Text accessibilityLiveRegion="polite">
  {cartItems.length} items in cart
</Text>

{/* Error announced assertively */}
{error && (
  <Text
    style={styles.error}
    accessibilityLiveRegion="assertive"
    accessibilityRole="alert"
  >
    {error.message}
  </Text>
)}

{/* Toast announced programmatically */}
{showToast && (
  <View style={styles.toast}>
    <Text>Item added to cart</Text>
  </View>
)}
// In the effect that triggers the toast:
useEffect(() => {
  if (showToast) {
    AccessibilityInfo.announceForAccessibility('Item added to cart');
  }
}, [showToast]);
```

### Platform Considerations

- **iOS (VoiceOver):** `accessibilityLiveRegion` is supported on iOS 17+. For older iOS versions, use `AccessibilityInfo.announceForAccessibility()`. On iOS, `"assertive"` and `"polite"` are both treated as polite by VoiceOver
- **Android (TalkBack):** `accessibilityLiveRegion` maps directly to Android's `liveRegion` attribute. TalkBack respects both `"polite"` and `"assertive"` levels
- **Both platforms:** `AccessibilityInfo.announceForAccessibility(message)` works cross-platform and is the most reliable way to announce transient changes
