# React Native Accessibility API Reference

Comprehensive reference for all React Native accessibility props and APIs, with platform mapping.

---

## View Props

| Prop | Type | Description | iOS | Android |
|------|------|-------------|-----|---------|
| `accessible` | `boolean` | Marks element as accessible. Groups children when `true` on a container | `isAccessibilityElement` | `importantForAccessibility` |
| `accessibilityLabel` | `string` | Text read by screen reader | `accessibilityLabel` | `contentDescription` |
| `accessibilityHint` | `string` | Additional context about action result | `accessibilityHint` | Appended to content description |
| `accessibilityRole` | `string` | Element type (button, link, header, etc.) | Maps to `UIAccessibilityTraits` | Maps to `className` |
| `accessibilityState` | `object` | Current state: `{ disabled, selected, checked, busy, expanded }` | `UIAccessibilityTraits` | `AccessibilityNodeInfo` state |
| `accessibilityValue` | `object` | Current value: `{ min, max, now, text }` | `accessibilityValue` | `RangeInfo` or `contentDescription` |
| `accessibilityActions` | `array` | Custom actions: `[{ name, label }]` | `accessibilityCustomActions` | `AccessibilityNodeInfo.addAction` |
| `onAccessibilityAction` | `function` | Handler for custom actions | Callback | Callback |
| `accessibilityLiveRegion` | `'none' \| 'polite' \| 'assertive'` | Announces dynamic content changes | Supported iOS 17+ | Maps to `liveRegion` |
| `accessibilityViewIsModal` | `boolean` | Confines screen reader focus to this view | `accessibilityViewIsModal` | No direct equivalent (use background hiding) |
| `accessibilityElementsHidden` | `boolean` | Hides element and children from VoiceOver | `accessibilityElementsHidden` | No effect (use `importantForAccessibility`) |
| `importantForAccessibility` | `string` | Controls Android accessibility tree inclusion | No effect | `importantForAccessibility` |
| `onAccessibilityEscape` | `function` | iOS two-finger Z-scrub gesture handler | `accessibilityPerformEscape` | Not supported |
| `onAccessibilityTap` | `function` | Custom tap handler for screen readers | `accessibilityActivate` | Not supported |

## `importantForAccessibility` Values (Android)

| Value | Description |
|-------|-------------|
| `"auto"` | Default — system determines importance |
| `"yes"` | Element is important for accessibility |
| `"no"` | Element is not important (but children may be) |
| `"no-hide-descendants"` | Element and all children are hidden from accessibility |

## `accessibilityRole` Values

| Role | Description | iOS Trait | Android Class |
|------|-------------|-----------|---------------|
| `"none"` | No specific role | None | None |
| `"button"` | Pressable element | `.button` | `android.widget.Button` |
| `"link"` | Hyperlink | `.link` | Announces "link" |
| `"search"` | Search field | `.searchField` | `android.widget.EditText` |
| `"image"` | Image element | `.image` | `android.widget.ImageView` |
| `"header"` | Section header | `.header` | Heading flag |
| `"summary"` | Summary of content | `.summaryElement` | None |
| `"alert"` | Important notification | Announcement | Announces "alert" |
| `"checkbox"` | Checkable control | None (use state) | `android.widget.CheckBox` |
| `"radio"` | Radio button | None (use state) | `android.widget.RadioButton` |
| `"switch"` | Toggle switch | `.switchButton` (iOS 17+) | `android.widget.Switch` |
| `"adjustable"` | Adjustable control (slider) | `.adjustable` | `android.widget.SeekBar` |
| `"tab"` | Tab element | `.tab` (iOS 17+) | Tab flag |
| `"tabbar"` | Tab bar container | `.tabBar` | Tab bar |
| `"tablist"` | Container for tabs | `.tabBar` | Tab container |
| `"timer"` | Timer element | `.updatesFrequently` | Timer flag |
| `"progressbar"` | Progress indicator | `.updatesFrequently` | `android.widget.ProgressBar` |
| `"spinbutton"` | Spin button | `.adjustable` | Number picker |
| `"menu"` | Menu container | None | Menu |
| `"menubar"` | Menu bar | None | Menu bar |
| `"menuitem"` | Menu item | None | Menu item |

## `accessibilityState` Properties

| Property | Type | Description |
|----------|------|-------------|
| `disabled` | `boolean` | Element is disabled |
| `selected` | `boolean` | Element is selected |
| `checked` | `boolean \| 'mixed'` | Checkbox/switch is checked |
| `busy` | `boolean` | Element is loading/updating |
| `expanded` | `boolean` | Expandable element is expanded |

## `accessibilityValue` Properties

| Property | Type | Description |
|----------|------|-------------|
| `min` | `number` | Minimum value for adjustable elements |
| `max` | `number` | Maximum value for adjustable elements |
| `now` | `number` | Current value for adjustable elements |
| `text` | `string` | Text description of the value |

## AccessibilityInfo API

```tsx
import { AccessibilityInfo } from 'react-native';

// Query current settings
const isScreenReaderEnabled = await AccessibilityInfo.isScreenReaderEnabled();
const isReduceMotionEnabled = await AccessibilityInfo.isReduceMotionEnabled();
const isBoldTextEnabled = await AccessibilityInfo.isBoldTextEnabled();         // iOS only
const isGrayscaleEnabled = await AccessibilityInfo.isGrayscaleEnabled();       // iOS only
const isInvertColorsEnabled = await AccessibilityInfo.isInvertColorsEnabled(); // iOS only
const isReduceTransparencyEnabled = await AccessibilityInfo.isReduceTransparencyEnabled(); // iOS only

// Listen for changes
const subscription = AccessibilityInfo.addEventListener(
  'screenReaderChanged',  // or 'reduceMotionChanged', 'boldTextChanged', etc.
  (isEnabled) => { /* handle change */ }
);
subscription.remove(); // cleanup

// Announce to screen reader
AccessibilityInfo.announceForAccessibility('Item added to cart');

// Set focus (iOS)
AccessibilityInfo.setAccessibilityFocus(reactTag);
```

## Platform-Specific Props

### iOS Only

| Prop | Description |
|------|-------------|
| `accessibilityElementsHidden` | Hides element and children from VoiceOver |
| `onAccessibilityEscape` | Handles two-finger Z-scrub dismiss gesture |
| `onAccessibilityTap` | Custom tap handler for VoiceOver |
| `accessibilityLanguage` | Language for screen reader pronunciation |

### Android Only

| Prop | Description |
|------|-------------|
| `importantForAccessibility` | Controls presence in Android accessibility tree |
| `accessibilityLabelledBy` | References another element's nativeID as label (Android API 22+) |

## Expo-Specific Notes

- Expo managed workflow supports all React Native accessibility props
- `expo-image` `<Image>` supports `accessibilityLabel` like standard `<Image>`
- `expo-router` screens can set `screenOptions` with accessibility labels on navigation elements
- `expo-haptics` should be paired with visual/audio feedback for accessibility
