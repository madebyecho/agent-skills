---
title: Animations Ignore Reduce Motion Setting
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: reduce-motion, animation, vestibular, wcag
---

## Animations Ignore Reduce Motion Setting

**Priority: P2 (MEDIUM)**

Users with vestibular disorders or motion sensitivity enable Reduce Motion to avoid nausea, dizziness, and headaches. Apps must check this setting and replace complex animations (parallax, spinning, zooming, multi-axis movement) with simple alternatives (fades, opacity changes, instant transitions).

### Detection

```
grep -n 'Animated\.\|useAnimatedStyle\|useSharedValue\|withSpring\|withTiming\|withSequence' **/*.{tsx,jsx,ts,js}
# Flag animations (React Native Animated API or Reanimated) without reduce-motion check

grep -n 'LayoutAnimation\|layoutAnimation' **/*.{tsx,jsx,ts,js}
# Flag LayoutAnimation usage without reduce-motion check

grep -n 'useReducedMotion\|isReduceMotionEnabled\|prefersReducedMotion' **/*.{tsx,jsx,ts,js}
# Find existing reduce-motion checks to gauge coverage
```

### Fix Logic

1. Identify all animations, transitions, and motion effects
2. **Decorative animations** → disable entirely when Reduce Motion is enabled
3. **Meaningful animations** → replace with simple fades or instant changes
4. Use `useReducedMotion()` from `react-native-reanimated` (preferred) or `AccessibilityInfo.isReduceMotionEnabled()` (built-in)
5. Never remove functionality — only change the visual transition

### Before/After

**Before:**
```tsx
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';

function CardReveal({ visible }: { visible: boolean }) {
  const scale = useSharedValue(0.5);
  const opacity = useSharedValue(0);

  useEffect(() => {
    scale.value = withSpring(visible ? 1 : 0.5);
    opacity.value = withTiming(visible ? 1 : 0, { duration: 300 });
  }, [visible]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return <Animated.View style={animatedStyle}><Card /></Animated.View>;
}
```

**After:**
```tsx
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  useReducedMotion,
} from 'react-native-reanimated';

function CardReveal({ visible }: { visible: boolean }) {
  const reduceMotion = useReducedMotion();
  const scale = useSharedValue(0.5);
  const opacity = useSharedValue(0);

  useEffect(() => {
    if (reduceMotion) {
      scale.value = visible ? 1 : 0.5;
      opacity.value = visible ? 1 : 0;
    } else {
      scale.value = withSpring(visible ? 1 : 0.5);
      opacity.value = withTiming(visible ? 1 : 0, { duration: 300 });
    }
  }, [visible, reduceMotion]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return <Animated.View style={animatedStyle}><Card /></Animated.View>;
}
```

**Alternative using built-in API (no Reanimated):**
```tsx
import { AccessibilityInfo } from 'react-native';

const [reduceMotion, setReduceMotion] = useState(false);

useEffect(() => {
  AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotion);
  const subscription = AccessibilityInfo.addEventListener(
    'reduceMotionChanged',
    setReduceMotion,
  );
  return () => subscription.remove();
}, []);
```

### Platform Considerations

- **iOS (VoiceOver):** Reduce Motion is set in Settings > Accessibility > Motion > Reduce Motion. React Native's `AccessibilityInfo.isReduceMotionEnabled()` reads this setting
- **Android (TalkBack):** Android has "Remove animations" in Settings > Accessibility. `AccessibilityInfo.isReduceMotionEnabled()` reads this on Android as well
- **Both platforms:** `useReducedMotion()` from `react-native-reanimated` v3+ is the recommended hook — it reactively updates when the setting changes and works on the UI thread
