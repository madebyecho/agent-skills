# Reanimated Patterns Reference

Recipes for `react-native-reanimated` v3+. Every example targets the UI thread — no JS-thread animation drivers.

## Shared Values

A shared value is a container whose `.value` lives on the UI thread. Mutations don't trigger re-renders.

```tsx
import { useSharedValue } from 'react-native-reanimated';

// Primitive
const offset = useSharedValue(0);

// Object
const position = useSharedValue({ x: 0, y: 0 });

// Array
const points = useSharedValue<number[]>([0, 0, 0]);
```

**Reading:** `offset.value` — anywhere (JS or UI thread).
**Writing:** `offset.value = 100` — anywhere. No re-render, UI thread sees the new value immediately.
**Never:** mutate shared values inside `useAnimatedStyle`. Use event handlers, effects, or gesture callbacks.

## useAnimatedStyle

A worklet that reads shared values and returns a style object. Runs on the UI thread whenever its dependencies change.

```tsx
import Animated, { useAnimatedStyle, useSharedValue } from 'react-native-reanimated';

function Box() {
  const translateX = useSharedValue(0);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return <Animated.View style={[styles.box, animatedStyle]} />;
}
```

**Rules:**
- Must return a style object (not an array)
- Applied only to `Animated.*` components — never plain `View`
- Animated styles take precedence over static `StyleSheet` styles
- The callback runs on both JS and UI threads; use `global._WORKLET` to differentiate if needed

## withTiming

Time-based animation with custom easing.

```tsx
import { withTiming, Easing } from 'react-native-reanimated';

offset.value = withTiming(100, {
  duration: 300,
  easing: Easing.out(Easing.cubic),
});

// With completion callback (automatically workletized)
offset.value = withTiming(100, { duration: 300 }, (finished) => {
  if (finished) {
    runOnJS(onComplete)();
  }
});
```

**Defaults:** `duration: 300`, `easing: Easing.inOut(Easing.quad)`.

## withSpring

Physics-based animation. No duration — driven by damping, mass, stiffness, and velocity.

```tsx
import { withSpring } from 'react-native-reanimated';

offset.value = withSpring(100, {
  damping: 15,      // How quickly the spring stops. Higher = less oscillation.
  mass: 1,          // Mass of the object. Higher = more inertia.
  stiffness: 150,   // Spring strength. Higher = faster movement.
  velocity: 500,    // Initial velocity (pass gesture velocity here).
});
```

**Presets to memorize:**
- iOS-native feel: `{ damping: 15, stiffness: 150 }`
- Snappier, less bounce: `{ damping: 20, stiffness: 300 }`
- Bouncy / playful: `{ damping: 8, stiffness: 150 }`
- Scale feedback (button press): `{ damping: 20, stiffness: 400 }`

## withSequence

Run animations one after another without callback chains.

```tsx
import { withSequence, withTiming } from 'react-native-reanimated';

offset.value = withSequence(
  withTiming(100, { duration: 200 }),
  withTiming(50, { duration: 200 }),
  withTiming(0, { duration: 200 }),
);
```

## withDelay

Delay an animation by a fixed time.

```tsx
import { withDelay, withSpring } from 'react-native-reanimated';

opacity.value = withDelay(100, withSpring(1));
```

## withRepeat

Repeat an animation a fixed number of times or forever.

```tsx
import { withRepeat, withTiming } from 'react-native-reanimated';

// Infinite
rotation.value = withRepeat(withTiming(360, { duration: 1000 }), -1);

// Finite, reversing direction on each iteration
scale.value = withRepeat(withTiming(1.1, { duration: 500 }), 4, true);
```

## useAnimatedReaction

Reactively run a worklet when a shared value changes. Useful for imperative side effects that can't be expressed in a style.

```tsx
import { useAnimatedReaction, runOnJS } from 'react-native-reanimated';

useAnimatedReaction(
  () => translateY.value,
  (current, previous) => {
    if (current > 100 && (previous ?? 0) <= 100) {
      runOnJS(triggerHaptic)();
    }
  },
);
```

## interpolate

Map one range to another on the UI thread. Core primitive for scroll-driven animation.

```tsx
import { interpolate, Extrapolation } from 'react-native-reanimated';

const animatedStyle = useAnimatedStyle(() => {
  const opacity = interpolate(
    scrollY.value,
    [0, 100, 200],
    [0, 0.5, 1],
    Extrapolation.CLAMP,
  );
  return { opacity };
});
```

**Extrapolation options:**
- `CLAMP` — stop at the boundary values
- `EXTEND` — keep going linearly (default)
- `IDENTITY` — return the input unchanged outside the range

## interpolateColor

Same idea, for colors.

```tsx
import { interpolateColor } from 'react-native-reanimated';

const backgroundColor = interpolateColor(
  progress.value,
  [0, 1],
  ['#ff0000', '#00ff00'],
);
```

## useAnimatedScrollHandler

Worklet-based scroll handler that doesn't cross to JS.

```tsx
import Animated, { useAnimatedScrollHandler, useSharedValue } from 'react-native-reanimated';

const scrollY = useSharedValue(0);

const scrollHandler = useAnimatedScrollHandler({
  onScroll: (event) => {
    scrollY.value = event.contentOffset.y;
  },
});

<Animated.ScrollView onScroll={scrollHandler} scrollEventThrottle={16}>
  {/* ... */}
</Animated.ScrollView>
```

## useDerivedValue

A shared value computed from other shared values. Runs on the UI thread.

```tsx
import { useDerivedValue } from 'react-native-reanimated';

const scale = useSharedValue(1);
const translateX = useSharedValue(0);

const invertedTranslate = useDerivedValue(() => -translateX.value / scale.value);
```

## Layout Animations

The declarative path for mount, unmount, and reorder. Prefer these over hand-rolled effects.

```tsx
import Animated, {
  FadeIn, FadeOut,
  SlideInRight, SlideOutLeft,
  LinearTransition,
} from 'react-native-reanimated';

<Animated.View
  entering={FadeIn.duration(300).easing(Easing.out(Easing.cubic))}
  exiting={FadeOut.duration(200)}
/>

<Animated.View
  entering={SlideInRight.springify().damping(15)}
  exiting={SlideOutLeft}
/>

<Animated.FlatList
  data={items}
  itemLayoutAnimation={LinearTransition.springify()}
  renderItem={renderItem}
/>
```

**Built-in entering/exiting:** `FadeIn`, `FadeInUp`, `FadeInDown`, `FadeInLeft`, `FadeInRight`, `SlideInUp`, `SlideInDown`, `SlideInLeft`, `SlideInRight`, `ZoomIn`, `BounceIn`, `RotateIn` — and `FadeOut`, etc. for exits.

**Modifiers (chainable):**
- `.duration(ms)` — override default duration
- `.easing(fn)` — provide a custom easing
- `.springify()` — switch from time-based to spring physics
- `.damping(n)` — spring damping (default 10)
- `.mass(n)` — spring mass (default 1)
- `.stiffness(n)` — spring stiffness
- `.delay(ms)` — delay the start
- `.withCallback(cb)` — run a callback on completion (wrap in `runOnJS` if needed)
- `.reduceMotion(ReduceMotion.System)` — per-animation reduce-motion setting

## Custom Layout Transition Worklet

When built-in layout animations aren't enough:

```tsx
const customLayoutTransition = (values) => {
  'worklet';
  return {
    animations: {
      originX: withTiming(values.targetOriginX, { duration: 1000 }),
      originY: withDelay(
        1000,
        withTiming(values.targetOriginY, { duration: 1000 })
      ),
      width: withSpring(values.targetWidth),
      height: withSpring(values.targetHeight),
    },
    initialValues: {
      originX: values.currentOriginX,
      originY: values.currentOriginY,
      width: values.currentWidth,
      height: values.currentHeight,
    },
  };
};

<Animated.View layout={customLayoutTransition} />
```

## runOnJS

Cross from the UI thread back to JS for things that can't run in a worklet (navigation, analytics, haptics, async APIs).

```tsx
import { runOnJS } from 'react-native-reanimated';

const pan = Gesture.Pan().onEnd(() => {
  'worklet';
  runOnJS(navigate)('DetailScreen');
  runOnJS(Haptics.impactAsync)(Haptics.ImpactFeedbackStyle.Medium);
});
```

**Rules:**
- `runOnJS` is only needed when calling *non-worklet* JS code
- Don't wrap every callback — gesture callbacks are already workletized
- Never `runOnJS` inside `onUpdate` of a gesture unless you're comfortable with JS-thread calls every frame

## Shared Element Transitions

Reanimated 3+ with the React Navigation native stack.

```tsx
import Animated from 'react-native-reanimated';

// Source screen
<Animated.Image
  source={photo.source}
  sharedTransitionTag={`photo-${photo.id}`}
/>

// Destination screen
<Animated.Image
  source={photo.source}
  sharedTransitionTag={`photo-${photo.id}`}
  style={styles.fullSize}
/>
```

The tag matches elements between screens and animates their geometry automatically.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using plain `View` with animated styles | Use `Animated.View` |
| Mutating shared values inside `useAnimatedStyle` | Mutate from event handlers or effects |
| Forgetting `'worklet'` on gesture callbacks in the legacy API | Use the v2 `Gesture` API — auto-workletized |
| Creating shared values inside render logic | Always call `useSharedValue` at the top of the component |
| Animating `marginTop` for positioning | Animate `transform: [{ translateY }]` instead |
| Chaining `withTiming(...).then(...)` | Use `withSequence` |
