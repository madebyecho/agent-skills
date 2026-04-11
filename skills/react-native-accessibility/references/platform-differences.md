# iOS vs Android Accessibility Differences

Key differences in accessibility behavior between iOS (VoiceOver) and Android (TalkBack) that affect React Native development.

---

## Screen Reader Navigation

| Behavior | iOS (VoiceOver) | Android (TalkBack) |
|----------|-----------------|-------------------|
| **Navigation gesture** | Swipe right/left | Swipe right/left |
| **Activate element** | Double-tap | Double-tap |
| **Scroll** | Three-finger swipe | Two-finger swipe |
| **Heading navigation** | Rotor → Headings | Swipe up/down (heading mode) |
| **Custom actions** | Swipe up/down on element | Local context menu |
| **Escape/back** | Two-finger Z-scrub | Three-finger swipe left |
| **Reading order** | View hierarchy order | View hierarchy order |

## Hiding Elements

| Method | iOS Effect | Android Effect |
|--------|-----------|----------------|
| `accessible={false}` | Removes element (children may still be exposed) | Removes element |
| `accessibilityElementsHidden={true}` | Hides element and ALL children from VoiceOver | **No effect** |
| `importantForAccessibility="no"` | **No effect** | Hides element (children may still appear) |
| `importantForAccessibility="no-hide-descendants"` | **No effect** | Hides element and ALL children |

### Recommended Pattern for Hiding

```tsx
// Cross-platform hiding
<View
  accessible={false}
  accessibilityElementsHidden={true}        // iOS
  importantForAccessibility="no-hide-descendants"  // Android
/>
```

## Modal Focus Trapping

| Feature | iOS | Android |
|---------|-----|---------|
| `accessibilityViewIsModal={true}` | Confines VoiceOver to this view | **No effect** (as of RN 0.73) |
| Background hiding | Automatic with `accessibilityViewIsModal` | Must manually set `importantForAccessibility="no-hide-descendants"` on background |
| Built-in `<Modal>` | Handles focus trapping | Handles focus trapping |
| Focus on open | Auto-focuses first element | Auto-focuses first element |
| Escape gesture | `onAccessibilityEscape` handler | Not supported via RN props |

### Recommended Pattern for Custom Modals

```tsx
// Parent content — hidden when modal is visible
<View
  accessibilityElementsHidden={isModalVisible}        // iOS
  importantForAccessibility={isModalVisible ? 'no-hide-descendants' : 'auto'}  // Android
>
  {/* Main content */}
</View>

// Modal content
<View accessibilityViewIsModal={true}>
  {/* Modal content */}
</View>
```

## Live Regions

| Feature | iOS | Android |
|---------|-----|---------|
| `accessibilityLiveRegion="polite"` | Supported (iOS 17+) | Waits for current speech to finish |
| `accessibilityLiveRegion="assertive"` | Treated same as polite (iOS 17+) | Interrupts current speech |
| `announceForAccessibility()` | Posts `UIAccessibility.Notification.announcement` | Uses `announceForAccessibility` API |
| Pre-iOS 17 live regions | **Not supported** — use `announceForAccessibility()` | Fully supported |

## Touch Targets

| Platform | Minimum Size | Guidelines |
|----------|-------------|------------|
| iOS | 44x44 pt | Apple Human Interface Guidelines |
| Android | 48x48 dp | Material Design Guidelines |
| **React Native recommendation** | **48x48 dp** | Satisfies both platforms |

## Font Scaling

| Feature | iOS | Android |
|---------|-----|---------|
| System font size setting | Settings > Accessibility > Display & Text Size > Larger Text | Settings > Accessibility > Font size |
| Accessibility sizes | Up to ~310% (AX5) | Up to ~200% |
| `allowFontScaling` | Controls Dynamic Type response | Controls font scaling response |
| `maxFontSizeMultiplier` | Caps the maximum scale | Caps the maximum scale |
| Bold Text setting | `AccessibilityInfo.isBoldTextEnabled()` | Not available in RN |

## Roles and Traits

| `accessibilityRole` | iOS Mapping | Android Mapping |
|---------------------|-------------|-----------------|
| `"button"` | UIAccessibilityTraits `.button` | `android.widget.Button` className |
| `"link"` | UIAccessibilityTraits `.link` | Link flag + "link" announcement |
| `"header"` | UIAccessibilityTraits `.header` | Heading flag (heading navigation) |
| `"switch"` | `.switchButton` (iOS 17+) | `android.widget.Switch` className |
| `"checkbox"` | No specific trait (use state) | `android.widget.CheckBox` className |
| `"adjustable"` | UIAccessibilityTraits `.adjustable` | `android.widget.SeekBar` className |
| `"alert"` | Posts announcement notification | "Alert" announcement |

## State Announcements

| `accessibilityState` | iOS Announcement | Android Announcement |
|---------------------|------------------|---------------------|
| `{ disabled: true }` | "dimmed" | "disabled" |
| `{ selected: true }` | "selected" | "selected" |
| `{ checked: true }` | "checked" (with checkbox/switch role) | "checked" |
| `{ checked: false }` | "unchecked" | "not checked" |
| `{ expanded: true }` | "expanded" | "expanded" |
| `{ expanded: false }` | "collapsed" | "collapsed" |
| `{ busy: true }` | "loading" | "busy" |

## Reduce Motion

| Feature | iOS | Android |
|---------|-----|---------|
| Setting location | Settings > Accessibility > Motion > Reduce Motion | Settings > Accessibility > Remove animations |
| RN API | `AccessibilityInfo.isReduceMotionEnabled()` | `AccessibilityInfo.isReduceMotionEnabled()` |
| Change listener | `'reduceMotionChanged'` event | `'reduceMotionChanged'` event |
| Reanimated hook | `useReducedMotion()` | `useReducedMotion()` |
