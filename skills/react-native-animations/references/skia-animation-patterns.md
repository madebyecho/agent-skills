# Skia Animation Patterns Reference

Recipes for `@shopify/react-native-skia`. Modern Skia (v1+) uses Reanimated shared values directly — no separate `useValue` hook required.

## When to Use Skia

Pick Skia when RN views cannot do the job:

| Task | Skia? |
|------|-------|
| Charts, line graphs, radial meters | Yes |
| Bézier path morphing / SVG interpolation | Yes |
| Shaders, gradients, blur, color filters | Yes |
| Particle systems, simulations, game loops | Yes |
| Animated GIFs / WebP with frame control | Yes |
| Cards, buttons, lists, modals | **No** — use Reanimated on views |
| Scroll-linked view animations | **No** — use `useAnimatedScrollHandler` |
| Navigation transitions | **No** — use Reanimated layout animations |

Skia renders in its own pipeline. You lose accessibility tree integration, native text, and standard touch handling inside a canvas. Use it for the 5% of your app where pixels matter more than UI-kit conventions.

## Setup

```tsx
import { Canvas, Circle, Group } from '@shopify/react-native-skia';

<Canvas style={{ flex: 1 }}>
  <Circle cx={128} cy={128} r={50} color="cyan" />
</Canvas>
```

All drawing primitives (`Circle`, `Rect`, `Path`, `Image`, `Group`, etc.) live inside a `<Canvas>`.

## Animating with Reanimated Shared Values

Skia components accept shared values directly for their props. This is the canonical pattern.

```tsx
import { Canvas, Circle } from '@shopify/react-native-skia';
import {
  useSharedValue,
  useDerivedValue,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';

export function PulsingCircle() {
  const r = useSharedValue(0);

  useEffect(() => {
    r.value = withRepeat(withTiming(85, { duration: 1000 }), -1, true);
  }, []);

  return (
    <Canvas style={{ flex: 1 }}>
      <Circle cx={128} cy={128} r={r} color="cyan" />
    </Canvas>
  );
}
```

No imperative `.start()`, no callback chains — the shared value drives the render.

## Derived Values for Computed Motion

Use `useDerivedValue` (from Reanimated, not Skia) to compute one shared value from another. Runs on the UI thread.

```tsx
import { Canvas, Circle, Group } from '@shopify/react-native-skia';
import {
  useSharedValue,
  useDerivedValue,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';

export function TricolorPulse() {
  const size = 256;
  const r = useSharedValue(0);
  const c = useDerivedValue(() => size - r.value);

  useEffect(() => {
    r.value = withRepeat(withTiming(size * 0.33, { duration: 1000 }), -1);
  }, [size]);

  return (
    <Canvas style={{ flex: 1 }}>
      <Group blendMode="multiply">
        <Circle cx={r} cy={r} r={r} color="cyan" />
        <Circle cx={c} cy={r} r={r} color="magenta" />
        <Circle cx={size / 2} cy={c} r={r} color="yellow" />
      </Group>
    </Canvas>
  );
}
```

Three circles, one driver. Derived values fan out without additional state.

## Time-Based Animation with useClock

`useClock` from Skia returns a shared value of milliseconds elapsed since the hook mounted. Pipe it through `useDerivedValue` for procedural motion.

```tsx
import { Canvas, Circle, useClock, vec } from '@shopify/react-native-skia';
import { useDerivedValue } from 'react-native-reanimated';

export function Lissajous() {
  const t = useClock();

  const transform = useDerivedValue(() => {
    const scale = (2 / (3 - Math.cos(2 * t.value / 1000))) * 200;
    return [
      { translateX: scale * Math.cos(t.value / 1000) },
      { translateY: scale * Math.sin(2 * t.value / 1000) / 2 },
    ];
  });

  return (
    <Canvas style={{ flex: 1 }}>
      <Circle c={vec(0, 0)} r={50} color="cyan" transform={transform} />
    </Canvas>
  );
}
```

`useClock` is ideal for trigonometric motion, particles, and procedural drawing. For discrete animations (from → to), use shared values with `withTiming` / `withSpring` instead.

## Path Interpolation (SVG Morphing)

Morph between SVG paths using `usePathInterpolation`. Paths must share the same number and types of commands.

```tsx
import { Canvas, Path, usePathInterpolation, Skia } from '@shopify/react-native-skia';
import { useSharedValue, withTiming } from 'react-native-reanimated';

const angry = Skia.Path.MakeFromSVGString('M 16 25 C 32 27 ... Z')!;
const normal = Skia.Path.MakeFromSVGString('M 21 31 C 31 32 ... Z')!;
const happy = Skia.Path.MakeFromSVGString('M 21 45 C 21 37 ... Z')!;

export function MoodMorph() {
  const progress = useSharedValue(0);

  useEffect(() => {
    progress.value = withTiming(1, { duration: 1000 });
  }, []);

  const path = usePathInterpolation(
    progress,
    [0, 0.5, 1],
    [angry, normal, happy]
  );

  return (
    <Canvas style={{ flex: 1 }}>
      <Path
        path={path}
        style="stroke"
        strokeWidth={5}
        strokeCap="round"
        strokeJoin="round"
      />
    </Canvas>
  );
}
```

## Animated GIFs with Pause Control

`useAnimatedImageValue` returns a shared value for animated images (GIF, WebP). Accepts an optional `isPaused` shared value.

```tsx
import { Canvas, Image, useAnimatedImageValue } from '@shopify/react-native-skia';
import { useSharedValue } from 'react-native-reanimated';
import { Pressable } from 'react-native';

export function PlayableBird() {
  const isPaused = useSharedValue(false);
  const bird = useAnimatedImageValue(require('./bird.gif'), isPaused);

  return (
    <Pressable onPress={() => { isPaused.value = !isPaused.value; }}>
      <Canvas style={{ width: 320, height: 180 }}>
        <Image image={bird} x={0} y={0} width={320} height={180} fit="contain" />
      </Canvas>
    </Pressable>
  );
}
```

## Shimmer / Gradient Overlay

A classic skeleton pattern using Skia's gradient primitives.

```tsx
import { Canvas, LinearGradient, Rect, vec } from '@shopify/react-native-skia';
import { useSharedValue, useDerivedValue, withRepeat, withTiming } from 'react-native-reanimated';

export function Shimmer({ width, height }) {
  const progress = useSharedValue(0);

  useEffect(() => {
    progress.value = withRepeat(withTiming(1, { duration: 1200 }), -1);
  }, []);

  const start = useDerivedValue(() => vec(-width + progress.value * width * 2, 0));
  const end = useDerivedValue(() => vec(progress.value * width * 2, 0));

  return (
    <Canvas style={{ width, height }}>
      <Rect x={0} y={0} width={width} height={height}>
        <LinearGradient
          start={start}
          end={end}
          colors={['#e0e0e0', '#f5f5f5', '#e0e0e0']}
        />
      </Rect>
    </Canvas>
  );
}
```

## Reanimated ↔ Skia Mental Model

```
┌──────────────────────┐     ┌──────────────────────┐
│  useSharedValue      │────▶│  Skia component prop │
│  (UI-thread state)   │     │  (cx, r, color, ...) │
└──────────────────────┘     └──────────────────────┘
         │                             ▲
         │                             │
         ▼                             │
┌──────────────────────┐               │
│  useDerivedValue     │───────────────┘
│  (computed worklet)  │
└──────────────────────┘
         ▲
         │
┌──────────────────────┐
│  withTiming/Spring/  │
│  Repeat/Sequence     │
└──────────────────────┘
```

Shared values are the contract. Reanimated drives them; Skia consumes them. No bridge crossing, no JS thread.

## Performance Rules for Skia

1. **Keep canvases small.** One full-screen `<Canvas>` is cheap; fifty small ones are not. Group related drawing inside one canvas.
2. **Avoid re-rendering canvases from React state.** Drive changes through shared values — the canvas's React tree should be stable.
3. **Use `<Group>` for shared transforms.** A single `transform` on a group beats per-primitive transforms.
4. **Don't animate `strokeWidth` or other properties that trigger path rasterization** on every frame if you can avoid it. Transforms are cheap; rasterization is not.
5. **For heavy text, prefer RN `Text` + Reanimated.** Skia text rendering is powerful but loses OS features (font scaling, selection, accessibility).

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using outdated `useValue` / `useComputedValue` | Modern Skia uses Reanimated shared values directly |
| Canvas renders once and never updates | Ensure the prop is a shared value, not a plain number |
| Text inside canvas loses accessibility | Render text outside the canvas with `<Text>` |
| Canvas ignores gestures | Skia canvases don't participate in the touch tree — wrap with `GestureDetector` + `Pressable` for interactivity |
| Path morphing looks wrong | Paths must share identical command structure — normalize with `Skia.Path.MakeFromSVGString` and matching curve counts |
