# Gesture Handler Patterns Reference

Recipes for `react-native-gesture-handler` v2. Gesture callbacks are automatically workletized and integrate directly with Reanimated shared values.

## Setup

Every app using gestures must wrap its root in `GestureHandlerRootView`:

```tsx
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <RootNavigator />
    </GestureHandlerRootView>
  );
}
```

Forgetting this is the most common cause of "my gesture doesn't fire" — gestures register but produce no events.

## Core Gesture Types

```tsx
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

Gesture.Pan()       // Drag along x/y
Gesture.Pinch()     // Two-finger zoom
Gesture.Rotation()  // Two-finger rotate
Gesture.Tap()       // Quick press and release
Gesture.LongPress() // Press and hold
Gesture.Fling()     // Directional fast swipe
```

Every gesture supports `.onBegin()`, `.onStart()`, `.onUpdate()`, `.onEnd()`, `.onFinalize()` — all automatically workletized.

## Applying a Gesture

```tsx
const pan = Gesture.Pan()
  .onUpdate((e) => {
    translateX.value = e.translationX;
  })
  .onEnd(() => {
    translateX.value = withSpring(0);
  });

<GestureDetector gesture={pan}>
  <Animated.View style={[styles.box, animatedStyle]} />
</GestureDetector>
```

## Pan-to-Dismiss Modal

```tsx
const translateY = useSharedValue(0);
const context = useSharedValue({ startY: 0 });

const pan = Gesture.Pan()
  .onStart(() => {
    context.value = { startY: translateY.value };
  })
  .onUpdate((e) => {
    translateY.value = Math.max(0, context.value.startY + e.translationY);
  })
  .onEnd((e) => {
    const shouldDismiss = translateY.value > SCREEN_HEIGHT * 0.25 || e.velocityY > 500;
    if (shouldDismiss) {
      translateY.value = withTiming(SCREEN_HEIGHT, { duration: 250 });
      runOnJS(onDismiss)();
    } else {
      translateY.value = withSpring(0, { damping: 15, stiffness: 150 });
    }
  });
```

**Key points:**
- Save the starting position in `onStart` — otherwise cumulative drags break.
- Read both distance *and* velocity in `onEnd` — flicks should dismiss even at short distance.
- `runOnJS` at the commit point, not inside `onUpdate`.

## Bottom Sheet with Snap Points

```tsx
const SNAP_POINTS = [0, SCREEN_HEIGHT * 0.5, SCREEN_HEIGHT]; // closed, half, full

const translateY = useSharedValue(SNAP_POINTS[2]);
const context = useSharedValue({ startY: 0 });

const pan = Gesture.Pan()
  .onStart(() => {
    context.value = { startY: translateY.value };
  })
  .onUpdate((e) => {
    translateY.value = Math.max(
      SNAP_POINTS[0],
      Math.min(SNAP_POINTS[2], context.value.startY + e.translationY)
    );
  })
  .onEnd((e) => {
    // Pick the nearest snap point, weighted by velocity
    const projected = translateY.value + e.velocityY * 0.2;
    const snap = SNAP_POINTS.reduce((closest, point) =>
      Math.abs(point - projected) < Math.abs(closest - projected) ? point : closest
    );
    translateY.value = withSpring(snap, {
      velocity: e.velocityY,
      damping: 20,
      stiffness: 150,
    });
  });
```

## Pan + Pinch + Rotation (Photo Viewer)

Three gestures active simultaneously for media manipulation.

```tsx
const offset = useSharedValue({ x: 0, y: 0 });
const start = useSharedValue({ x: 0, y: 0 });
const scale = useSharedValue(1);
const savedScale = useSharedValue(1);
const rotation = useSharedValue(0);
const savedRotation = useSharedValue(0);

const animatedStyle = useAnimatedStyle(() => ({
  transform: [
    { translateX: offset.value.x },
    { translateY: offset.value.y },
    { scale: scale.value },
    { rotateZ: `${rotation.value}rad` },
  ],
}));

const dragGesture = Gesture.Pan()
  .averageTouches(true)
  .onUpdate((e) => {
    offset.value = {
      x: e.translationX + start.value.x,
      y: e.translationY + start.value.y,
    };
  })
  .onEnd(() => {
    start.value = { x: offset.value.x, y: offset.value.y };
  });

const zoomGesture = Gesture.Pinch()
  .onUpdate((e) => {
    scale.value = savedScale.value * e.scale;
  })
  .onEnd(() => {
    savedScale.value = scale.value;
  });

const rotateGesture = Gesture.Rotation()
  .onUpdate((e) => {
    rotation.value = savedRotation.value + e.rotation;
  })
  .onEnd(() => {
    savedRotation.value = rotation.value;
  });

const composed = Gesture.Simultaneous(
  dragGesture,
  Gesture.Simultaneous(zoomGesture, rotateGesture)
);

<GestureDetector gesture={composed}>
  <Animated.View style={animatedStyle}>
    <Photo />
  </Animated.View>
</GestureDetector>
```

## Gesture Composition

Three composition modes, chosen by interaction semantics.

### Simultaneous — all gestures can be active at once
```tsx
const composed = Gesture.Simultaneous(pan, pinch);
```
Use for: photo viewers, canvases, map-like interactions.

### Race — first to activate wins, others cancel
```tsx
const composed = Gesture.Race(tap, longPress);
```
Use for: mutually exclusive interactions where the first recognized gesture should own the touch.

### Exclusive — higher-priority gesture blocks lower-priority ones
```tsx
const composed = Gesture.Exclusive(doubleTap, singleTap);
```
Use for: tap disambiguation — a double-tap should prevent the single-tap handler from also firing.

## Tap and Long Press

```tsx
const tap = Gesture.Tap()
  .maxDuration(250)
  .onEnd((_e, success) => {
    if (success) {
      runOnJS(onTap)();
    }
  });

const longPress = Gesture.LongPress()
  .minDuration(500)
  .onStart(() => {
    runOnJS(Haptics.impactAsync)(Haptics.ImpactFeedbackStyle.Medium);
    runOnJS(onLongPress)();
  });
```

## Double Tap via Exclusive

```tsx
const singleTap = Gesture.Tap()
  .numberOfTaps(1)
  .onEnd(() => runOnJS(onSingleTap)());

const doubleTap = Gesture.Tap()
  .numberOfTaps(2)
  .onEnd(() => runOnJS(onDoubleTap)());

const composed = Gesture.Exclusive(doubleTap, singleTap);
```

## runOnJS — When to Cross Thread

By default, gesture callbacks run on the UI thread (they're workletized). `runOnJS` is needed when calling code that *can't* run in a worklet:

| Needs `runOnJS` | Can stay on UI thread |
|-----------------|----------------------|
| `navigation.navigate(...)` | Shared value mutations |
| `Haptics.impactAsync(...)` | `withTiming` / `withSpring` |
| `setState(...)` | `interpolate` / `interpolateColor` |
| Analytics / logging | Other shared values via `useDerivedValue` |
| `fetch` / async APIs | Conditional branching on shared values |

**Rule of thumb:** if the function comes from a regular JS import and doesn't say "worklet" in its definition, it needs `runOnJS`.

## Velocity-Aware Snap-Back

Always read velocity in `onEnd` and pass it to `withSpring` — users expect momentum.

```tsx
.onEnd((e) => {
  offset.value = withSpring(0, {
    velocity: e.velocityX,
    damping: 15,
    stiffness: 150,
  });
})
```

## Haptic Coordination

Fire haptics at commit points, never inside `onUpdate`:

```tsx
const pan = Gesture.Pan()
  .onStart(() => {
    runOnJS(Haptics.selectionAsync)();
  })
  .onEnd(() => {
    if (crossedThreshold) {
      runOnJS(Haptics.impactAsync)(Haptics.ImpactFeedbackStyle.Medium);
    }
  });
```

Or trigger via `useAnimatedReaction` when a shared value crosses a threshold:

```tsx
useAnimatedReaction(
  () => translateX.value > 100,
  (isPastThreshold, wasPastThreshold) => {
    if (isPastThreshold && !wasPastThreshold) {
      runOnJS(Haptics.impactAsync)();
    }
  }
);
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Missing `GestureHandlerRootView` | Wrap the app root |
| Gesture fires but animation doesn't move | Confirm the style is applied to `Animated.View`, not `View` |
| Drag jumps on second touch | Save the starting value in `onStart` and add delta in `onUpdate` |
| Haptics fire every frame | Move `runOnJS(Haptics.*)` to `onEnd` or threshold branches |
| Double-tap and single-tap both fire | Use `Gesture.Exclusive(doubleTap, singleTap)` |
| Pan competes with parent `ScrollView` | Use `Gesture.Simultaneous` or `.activeOffsetX`/`Y` to disambiguate |
