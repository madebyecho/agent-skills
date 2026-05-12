# Uniforms & Animation Reference

Deep dive on driving shader uniforms from React state, Reanimated, and
gestures, including the mental model of UI-thread vs JS-thread.

## The Thread Model

```
JS thread                UI (worklet) thread          Skia (GPU/native)
─────────                ──────────────────           ─────────────────
React renders            Reanimated shared values     Canvas draw
useState                 useDerivedValue, useClock    Shader uniforms applied
                                                      Frame painted
```

Anything in `useDerivedValue` runs on the UI thread. Anything reading
`.value` from outside a worklet runs on JS. The two communicate via
SharedValues.

**Why this matters for shaders:** if you update a uniform via React state
(`setState`), every change costs a React re-render + an IPC hop. That
caps you at ~JS-thread speed (50–60fps best case, often less under load).
SharedValue + `useDerivedValue` runs entirely on the UI thread —
shader-locked refresh rate (60–120fps), no JS involvement after setup.

## React-Native-Skia ↔ Reanimated Bridge

When you pass a SharedValue (or `useDerivedValue` result) as a prop:

```tsx
const u = useDerivedValue(() => ({ time: clock.value / 1000 }));
<Shader source={src} uniforms={u} />
```

react-native-skia subscribes to the SharedValue. On each UI-thread tick
where the value changes, the Canvas marks itself dirty and re-paints
within the same frame — no React tree update.

If you pass a plain object:
```tsx
<Shader source={src} uniforms={{ time: someState }} />
```
That object is computed during React render and only changes when
`someState` changes. The Canvas paints once per render, not per UI-thread
tick.

## useClock Internals

```tsx
const clock = useClock();
// clock: SharedValue<number>, milliseconds since first read
```

`useClock` starts a UI-thread `requestAnimationFrame` loop that ticks the
SharedValue each frame. It pauses when the Canvas is unmounted.

For pausing mid-animation:
```tsx
const clock = useClock();
const paused = useSharedValue(false);
const offset = useSharedValue(0);
const lastClock = useSharedValue(0);

// Toggle pause:
const toggle = () => {
  if (paused.value) {
    offset.value -= (clock.value - lastClock.value);
  } else {
    lastClock.value = clock.value;
  }
  paused.value = !paused.value;
};

const time = useDerivedValue(() => {
  return paused.value
    ? lastClock.value + offset.value
    : clock.value + offset.value;
});
```

## Driving Uniforms from Multiple SharedValues

`useDerivedValue` reads multiple `.value` accesses; the result recomputes
whenever any of them changes:

```tsx
const t = useClock();
const x = useSharedValue(0);
const y = useSharedValue(0);
const scale = useSharedValue(1);

const u = useDerivedValue(() => ({
  resolution: [w, h],
  time: t.value / 1000,
  touch: [x.value, y.value],
  scale: scale.value,
}));
```

Any change to `t`, `x`, `y`, or `scale` triggers a Canvas repaint.

## Allocation Considerations

Each call to `useDerivedValue` produces a new object every frame. For one
uniform set + steady allocation pattern, this is fine. For a complex
uniform block computed many times per frame across many shaders, you can
see GC pressure on low-end Android. Mitigations:
- Combine uniforms into a single SharedValue
- Use Reanimated's `useAnimatedReaction` if you need fine-grained control

In practice: don't worry about it until profiling shows a problem.

## Gesture Handler Integration

```tsx
import { Gesture, GestureDetector } from "react-native-gesture-handler";

const touch = useSharedValue([0, 0]);
const pressing = useSharedValue(0);

const pan = Gesture.Pan()
  .onBegin((e) => { touch.value = [e.x, e.y]; pressing.value = 1; })
  .onChange((e) => { touch.value = [e.x, e.y]; })
  .onFinalize(() => { pressing.value = 0; });

const u = useDerivedValue(() => ({
  resolution: [w, h],
  touch: touch.value,
  pressed: pressing.value,
}));
```

Each event runs on the UI thread inside a worklet — no JS involvement. The
shader receives the latest touch position with at most 1 frame latency.

## Tween, Spring, Repeat

Reanimated's `withTiming`, `withSpring`, `withRepeat` produce
SharedValue animations on the UI thread:

```tsx
import { withTiming, withSpring, withRepeat, Easing } from "react-native-reanimated";

const intensity = useSharedValue(0);

// Animate when something happens:
intensity.value = withTiming(1.0, { duration: 600, easing: Easing.out(Easing.cubic) });

// Spring:
intensity.value = withSpring(1.0, { damping: 12, mass: 0.6 });

// Looping:
intensity.value = withRepeat(
  withTiming(1, { duration: 800 }),
  -1,    // infinite
  true   // bounce
);
```

In the shader, `intensity` is a single `uniform float`.

## Color Animation

Reanimated's `interpolateColor` operates on ARGB integers; react-native-skia's
`interpolateColors` does the same. To pass to a shader, unpack:

```tsx
import { interpolateColors } from "@shopify/react-native-skia";

const u = useDerivedValue(() => {
  const c = interpolateColors(t.value, [0, 1], ["#ff007a", "#00d4ff"]);
  return {
    color: [
      ((c >> 16) & 0xff) / 255,
      ((c >>  8) & 0xff) / 255,
      ( c        & 0xff) / 255,
      ((c >> 24) & 0xff) / 255,
    ],
  };
});
```

## Reading Component Layout

If shader size depends on a measured layout:

```tsx
const size = useSharedValue({ w: 0, h: 0 });
const onLayout = useCallback((e: LayoutChangeEvent) => {
  size.value = { w: e.nativeEvent.layout.width, h: e.nativeEvent.layout.height };
}, []);

const u = useDerivedValue(() => ({ resolution: [size.value.w, size.value.h] }));

<View onLayout={onLayout}>
  <Canvas><Fill><Shader source={src} uniforms={u} /></Fill></Canvas>
</View>
```

## Patterns

### Idle ramp-down

When the user stops interacting, ease the intensity back to 0:

```tsx
const intensity = useSharedValue(0);
const pan = Gesture.Pan()
  .onChange(() => { intensity.value = 1.0; })
  .onFinalize(() => { intensity.value = withTiming(0, { duration: 400 }); });
```

### Per-element parallax

Each instance can have its own animation parameters:

```tsx
{items.map((item, i) => (
  <ShaderItem key={i} offset={useSharedValue(i * 0.1)} />
))}
```

## See Also

- [`../techniques/uniforms-animation.md`](../techniques/uniforms-animation.md) — Practical recipes.
- [`../techniques/rn-skia-integration.md`](../techniques/rn-skia-integration.md) — Wiring.
