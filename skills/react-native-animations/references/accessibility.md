# Accessibility Reference — Reduce Motion

Motion that ignores system accessibility settings is a physical failure, not a stylistic one. Users with vestibular disorders (inner-ear conditions, motion sensitivity) enable Reduce Motion specifically to avoid nausea, dizziness, and headaches. An animation that disregards this setting can physically harm a user.

This reference covers the three Reanimated integration points for Reduce Motion, plus a decision matrix for *what to change* when the setting is on.

For detection-and-fix audit coverage, cross-reference the `react-native-accessibility` skill's `p2-reduce-motion-ignored` rule.

## The Three Integration Points

Reanimated provides three ways to respect Reduce Motion. Use all three — they compose.

### 1. `useReducedMotion()` hook

A synchronous hook that returns a boolean. Prefer this over React Native's `AccessibilityInfo.isReduceMotionEnabled()` because:
- It's synchronous (no promise)
- It works inside worklets
- It updates reactively when the user changes the setting

```tsx
import { useReducedMotion } from 'react-native-reanimated';

function CardReveal({ visible }: { visible: boolean }) {
  const reduceMotion = useReducedMotion();
  const scale = useSharedValue(0.5);
  const opacity = useSharedValue(0);

  useEffect(() => {
    if (reduceMotion) {
      // Instant — skip spatial animation
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

### 2. `<ReducedMotionConfig>` component

App-wide configuration. Place it at the root of the app to globally set a default for all Reanimated animations when the OS setting is on.

```tsx
import { ReducedMotionConfig, ReduceMotion } from 'react-native-reanimated';

export default function App() {
  return (
    <>
      <ReducedMotionConfig mode={ReduceMotion.System} />
      <RootNavigator />
    </>
  );
}
```

**Modes:**
- `ReduceMotion.System` — follow the OS setting (recommended default)
- `ReduceMotion.Always` — always disable animation (for testing)
- `ReduceMotion.Never` — always run animation, regardless of OS (for non-spatial animations that should always play)

With `ReducedMotionConfig` mounted, `withTiming`, `withSpring`, and layout animations automatically go instant when the user has Reduce Motion enabled — no per-component code needed.

### 3. `.reduceMotion()` modifier (per animation)

Override the global config on a single animation. Available on layout animation builders and animation functions.

```tsx
import { FadeIn, ReduceMotion } from 'react-native-reanimated';

<Animated.View
  entering={SlideInRight.duration(300).reduceMotion(ReduceMotion.System)}
/>

// Or: always play (a fade that's safe even with reduce motion)
<Animated.View
  entering={FadeIn.duration(300).reduceMotion(ReduceMotion.Never)}
/>
```

On `withTiming` / `withSpring`:
```tsx
offset.value = withTiming(100, {
  duration: 300,
  reduceMotion: ReduceMotion.System,
});
```

## The Decision Matrix — What to Change

When Reduce Motion is on, not every animation should be disabled. Semantic motion (indicating state) should stay; vestibular motion (indicating space) should go.

| Animation type | When Reduce Motion is on |
|----------------|-------------------------|
| **Opacity / fade** | **Keep.** Not vestibular. |
| **Color / background transition** | **Keep.** Not vestibular. |
| **Slide / translate** | **Remove.** Replace with fade or instant. |
| **Scale (zoom in/out)** | **Remove.** Replace with fade. |
| **Rotate** | **Remove.** Highly vestibular. |
| **Parallax scrolling** | **Remove.** Disable entirely. |
| **Shake / wobble** | **Remove.** Replace with color change. |
| **Auto-playing background video** | **Pause.** Especially ones with motion. |
| **Blur transitions** | **Keep** (visual, not spatial) but simplify if performance suffers. |
| **Bounce / elastic** | **Remove.** Replace with instant. |
| **Skeleton shimmer** | **Simplify.** Replace shimmer with static placeholder or low-amplitude pulse. |

**The rule:** if an animation conveys meaning through *movement*, remove the movement but keep the meaning. A slide-up modal becomes a fade-in; the user still sees the modal appear — they just don't see it travel.

## Common Patterns

### Collapsing a slide animation to a fade

```tsx
const reduceMotion = useReducedMotion();

<Animated.View
  entering={
    reduceMotion
      ? FadeIn.duration(200)
      : SlideInUp.springify().damping(15)
  }
  exiting={
    reduceMotion
      ? FadeOut.duration(150)
      : SlideOutDown.duration(200)
  }
/>
```

### Skipping a scale animation for a button press

```tsx
const reduceMotion = useReducedMotion();
const scale = useSharedValue(1);

const onPressIn = () => {
  if (reduceMotion) return; // Skip entirely
  scale.value = withSpring(0.97, { damping: 20, stiffness: 400 });
};
```

### Pausing an infinite animation

```tsx
const reduceMotion = useReducedMotion();
const rotation = useSharedValue(0);

useEffect(() => {
  if (reduceMotion) {
    rotation.value = 0; // Static
  } else {
    rotation.value = withRepeat(withTiming(360, { duration: 2000 }), -1);
  }
}, [reduceMotion]);
```

## Platform Settings Reference

- **iOS:** Settings → Accessibility → Motion → Reduce Motion. Also exposes separate toggles for "Auto-play Message Effects" and "Prefer Cross-Fade Transitions."
- **Android:** Settings → Accessibility → Remove Animations (some variants call it "Reduce Animations"). Also respects the Developer Options "Animation Scale" settings.

Both platforms are exposed through a single React Native API: `AccessibilityInfo.isReduceMotionEnabled()` and `AccessibilityInfo.addEventListener('reduceMotionChanged', ...)`. Reanimated's `useReducedMotion` reads from the same source but gives you a synchronous, reactive value.

## Testing

- **Enable Reduce Motion in simulator/device settings** before shipping.
- **Force-enable in development** via `<ReducedMotionConfig mode={ReduceMotion.Always} />` at the app root to walk through every screen.
- **Watch for leftover movement** — if any screen still translates/scales/rotates when Reduce Motion is on, something bypassed the system. Usually a direct `Animated` API call or a CSS-like inline style.
- **Verify fades still play** — confirm that state changes still communicate through opacity/color, so functionality isn't lost.

## Anti-Patterns

| Anti-pattern | Fix |
|--------------|-----|
| Using the legacy `Animated` API for motion | Reanimated respects Reduce Motion; legacy does not without manual checks |
| Ignoring `useReducedMotion` in infinite animations | Stop the animation or render a static frame when reduce motion is on |
| Disabling *all* animations (including fades) | Keep non-spatial animations — users still want to see state changes |
| Relying only on `<ReducedMotionConfig>` without per-component checks for imperative animations | Combine the app-wide config with explicit checks in imperative code |
| Using `AccessibilityInfo.isReduceMotionEnabled()` inside useEffect without re-subscribing | Use `useReducedMotion` — it's reactive |

## Cross-Link

For **audit mode** — scanning a codebase for animations that ignore Reduce Motion — use the `react-native-accessibility` skill's `p2-reduce-motion-ignored` rule. That rule contains detection grep patterns and automated fix logic that complements the design guidance here.
