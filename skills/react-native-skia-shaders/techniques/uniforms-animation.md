# Uniforms & Animation

How to feed values from React state, gestures, and time into a SKSL shader
without breaking the UI thread. The right answer is almost always **a
Reanimated SharedValue piped through `useDerivedValue` into the `uniforms`
prop**.

## The Two Ways to Pass Uniforms

```tsx
// 1. Plain object — re-evaluated on each React render
<Shader source={s} uniforms={{ resolution: [w, h], time: 0.0 }} />

// 2. Reanimated value — animated on the UI thread, 60–120fps without React renders
const u = useDerivedValue(() => ({ resolution: [w, h], time: clock.value / 1000 }));
<Shader source={s} uniforms={u} />
```

**Use form 2 for anything that moves.** Form 1 is fine for static initial
values or when the only thing changing is a slow React state value (theme,
viewport flip).

## `useClock` — The Time Uniform

```tsx
import { useClock } from "@shopify/react-native-skia";

const clock = useClock();        // SharedValue<number>, ms since Canvas mount

const uniforms = useDerivedValue(() => ({
  resolution: [w, h],
  time: clock.value / 1000,      // seconds is conventional in shaders
}));
```

`useClock` ticks every frame on the UI thread. You can pause it via the
`Canvas` `mode="continuous"|"default"` prop or stop reading it.

### Alternatives for time

- `useTime()` — deprecated alias of `useClock` in some versions.
- A custom loop with `withRepeat(withTiming(...))` if you want
  bouncing/looping time.
- For a fixed-duration cycle (e.g. a 2s breathing animation):
  ```tsx
  const t = useSharedValue(0);
  useEffect(() => {
    t.value = withRepeat(withTiming(1, { duration: 2000, easing: Easing.linear }), -1);
  }, []);
  ```

## Driving Uniforms From Reanimated Values

```tsx
import { useSharedValue, useDerivedValue, withSpring } from "react-native-reanimated";

const intensity = useSharedValue(0.5);

const uniforms = useDerivedValue(() => ({
  resolution: [w, h],
  intensity: intensity.value,
}));

// Trigger animation from any handler:
const onPress = () => { intensity.value = withSpring(1.0); };
```

Inside `useDerivedValue`, all reads of `.value` register dependencies. When
any of them changes on the UI thread, the derived value recomputes and the
shader re-renders — **without** a React re-render.

## Gesture-Driven Uniforms

```tsx
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { useSharedValue, useDerivedValue } from "react-native-reanimated";

const touch = useSharedValue({ x: w / 2, y: h / 2, pressed: 0 });

const pan = Gesture.Pan()
  .onBegin((e) => { touch.value = { x: e.x, y: e.y, pressed: 1 }; })
  .onChange((e) => { touch.value = { x: e.x, y: e.y, pressed: 1 }; })
  .onFinalize(() => { touch.value = { ...touch.value, pressed: 0 }; });

const uniforms = useDerivedValue(() => ({
  resolution: [w, h],
  touch: [touch.value.x, touch.value.y],
  pressed: touch.value.pressed,
}));

return (
  <GestureDetector gesture={pan}>
    <Canvas style={{ width: w, height: h }}>
      <Fill><Shader source={src} uniforms={uniforms} /></Fill>
    </Canvas>
  </GestureDetector>
);
```

For pinch/zoom-driven warps, use `Gesture.Pinch().onChange((e) => { scale.value = e.scale; })` and pass `scale` as a `float` uniform.

## Combining Multiple Animations

`useDerivedValue` can read any number of SharedValues:

```tsx
const time = useClock();
const intensity = useSharedValue(0);
const hue = useSharedValue(0);

const uniforms = useDerivedValue(() => ({
  resolution: [w, h],
  time: time.value / 1000,
  intensity: intensity.value,
  hue: hue.value,
}));
```

When *any* of those values changes, the derived value recomputes. The shader
will paint at the rate of the fastest input — bounded by display refresh.

## Bouncing / Looping a Uniform

```tsx
import { withRepeat, withTiming, Easing } from "react-native-reanimated";

const pulse = useSharedValue(0);
useEffect(() => {
  pulse.value = withRepeat(
    withTiming(1, { duration: 800, easing: Easing.inOut(Easing.cubic) }),
    -1,    // infinite
    true   // reverse (bouncing)
  );
}, []);
```

Then `pulse: pulse.value` inside the derived value goes 0 → 1 → 0 every
1.6s, available as a `uniform float pulse;` in the shader.

## Smoothly Tweening Between Variants

```tsx
const blend = useSharedValue(0);

const uniforms = useDerivedValue(() => ({
  resolution: [w, h],
  // SKSL: vec4 colA = vec4(...); vec4 colB = vec4(...); return mix(colA, colB, blend);
  blend: blend.value,
}));

const swap = () => { blend.value = withTiming(blend.value > 0.5 ? 0 : 1, { duration: 500 }); };
```

## Sharing a SharedValue Across Components

Pass it through props:

```tsx
function Parent() {
  const t = useSharedValue(0);
  return (
    <>
      <Slider value={t} />
      <ShaderView t={t} />
    </>
  );
}
function ShaderView({ t }: { t: SharedValue<number> }) {
  const u = useDerivedValue(() => ({ resolution: [w, h], t: t.value }));
  return <Canvas><Fill><Shader source={src} uniforms={u} /></Fill></Canvas>;
}
```

## Color Uniforms

```glsl
uniform float4 color;          // RGBA in 0..1
```

```tsx
import { interpolateColors } from "@shopify/react-native-skia";

const t = useSharedValue(0);
const uniforms = useDerivedValue(() => {
  const c = interpolateColors(t.value, [0, 1], ["red", "blue"]);
  // interpolateColors returns an ARGB number; unpack to a float4
  return {
    resolution: [w, h],
    color: [
      ((c >> 16) & 0xff) / 255,   // R
      ((c >>  8) & 0xff) / 255,   // G
      ( c        & 0xff) / 255,   // B
      ((c >> 24) & 0xff) / 255,   // A
    ],
  };
});
```

Or use Reanimated's `interpolateColor` and parse the hex string yourself.
There's no built-in "color" uniform type — colors are just `float4`.

## Common Mistake: Closing Over Stale Values

```tsx
// ❌ Captures w,h ONCE — won't react to dimension changes
const uniforms = useDerivedValue(() => ({ resolution: [w, h], time: clock.value }));
```

If `w`/`h` come from `useWindowDimensions`, React re-renders and recreates
the `useDerivedValue` — so this actually does work. But if they come from a
SharedValue (e.g. an animated layout), you must read `.value` inside:

```tsx
const size = useSharedValue({ w, h });
const uniforms = useDerivedValue(() => ({
  resolution: [size.value.w, size.value.h],   // ✅ reads .value, reactive
  time: clock.value / 1000,
}));
```

## Throttling Updates (Save Battery)

For non-critical animations, downsample:

```tsx
const time = useClock();
const uniforms = useDerivedValue(() => ({
  resolution: [w, h],
  time: Math.floor(time.value / 33.33) * 33.33 / 1000,   // ~30fps cap
}));
```

Better: gate the Canvas itself with `mode="default"` (which only renders on
prop change) and pulse a SharedValue at a slower interval. For shaders that
animate continuously and don't need 120fps, this can halve battery cost.

## Pausing / Stopping Animation

`useClock` keeps ticking as long as the component is mounted. To pause:

```tsx
const clock = useClock();
const paused = useSharedValue(false);
const pausedTime = useSharedValue(0);

const time = useDerivedValue(() => {
  return paused.value ? pausedTime.value : clock.value / 1000;
});

const uniforms = useDerivedValue(() => ({ resolution: [w, h], time: time.value }));
```

## Pattern: Touch Ripple That Decays

```tsx
const touch = useSharedValue([0, 0, 0]);   // x, y, startTime

const tap = Gesture.Tap().onStart((e) => {
  touch.value = [e.x, e.y, clock.value];
});

const uniforms = useDerivedValue(() => {
  const elapsed = Math.max(0, (clock.value - touch.value[2]) / 1000);
  return {
    resolution: [w, h],
    touch: [touch.value[0], touch.value[1]],
    rippleAge: elapsed,    // shader fades when this > 1.0
  };
});
```

```glsl
uniform float2 resolution;
uniform float2 touch;
uniform float rippleAge;
vec4 main(vec2 pos) {
    float d = distance(pos, touch);
    float ring = exp(-pow(d - rippleAge * 200.0, 2.0) / 800.0);
    float fade = exp(-rippleAge * 1.5);
    return vec4(vec3(ring * fade), 1.0);
}
```

## Anti-Patterns

- ❌ `time: Date.now() / 1000` — locks to JS thread, drops frames.
- ❌ `useEffect(() => setInterval(() => setX(x+1)))` — JS-thread tick, costs a React render per frame.
- ❌ `new Date()` inside `useDerivedValue` — `Date` may not be available in
  worklets on all platforms. Use `clock.value` and arithmetic.
- ❌ Allocating fresh objects every frame when only one number changed and the
  rest are constants — fine for correctness, not great for GC pressure on
  Android. If profiling shows GC churn, hoist constants.
- ❌ Reading `someRef.current` inside `useDerivedValue` — refs aren't shared
  with the UI thread. Use SharedValues.

## See Also

- [rn-skia-integration](rn-skia-integration.md) — basic wiring.
- [child-shaders](child-shaders.md) — passing an image into a shader.
- Reference: [`reference/uniforms-animation.md`](../reference/uniforms-animation.md).
