# React Native Skia Integration

How to wire a SKSL shader into a React Native app using
`@shopify/react-native-skia`. Read this **first** — every other technique in
this skill assumes you know this scaffolding.

## Install & Setup

```bash
yarn add @shopify/react-native-skia react-native-reanimated
# Expo:
npx expo install @shopify/react-native-skia react-native-reanimated
```

Reanimated 3+ is the standard driver for shader uniforms. Add the Reanimated
babel plugin to `babel.config.js` if it's not already there:

```js
module.exports = { plugins: ["react-native-reanimated/plugin"] };
```

## Anatomy of a Shader Component

```tsx
import { Canvas, Fill, Shader, Skia } from "@shopify/react-native-skia";

// 1. SKSL source as a JS string
const sksl = `
uniform float2 resolution;
vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    return vec4(uv, 0.5, 1.0);
}`;

// 2. Compile ONCE at module scope (not in render!)
const source = Skia.RuntimeEffect.Make(sksl);
if (!source) throw new Error("SKSL compile failed");

// 3. Use inside <Canvas> with a paintable (<Fill>, <Rect>, <Circle>, etc.)
export const HelloShader = () => (
  <Canvas style={{ flex: 1 }}>
    <Fill>
      <Shader source={source} uniforms={{ resolution: [400, 400] }} />
    </Fill>
  </Canvas>
);
```

The four moving parts:

1. **`Skia.RuntimeEffect.Make(sksl)`** — compiles SKSL → returns a
   `SkRuntimeEffect | null`. **Returns `null` on compile failure, does not
   throw.** Always null-check.
2. **`<Canvas>`** — the GPU-backed surface. Pixel size = `style.width *
   pixelRatio`, etc.
3. **`<Fill>` (or `<Rect>`, `<Circle>`, `<Path>`)** — a paintable. A shader is
   a *paint*; it doesn't render on its own.
4. **`<Shader source={...} uniforms={...} />`** — supplies the paint. Lives
   as a child of the paintable.

## Module-Level vs Render-Level Compilation

```tsx
// ❌ BAD — recompiles SKSL on every render (slow, occasional jank)
export const MyShader = () => {
  const source = Skia.RuntimeEffect.Make(sksl);
  // ...
};

// ✅ GOOD — compiles once at JS module load
const source = Skia.RuntimeEffect.Make(sksl)!;
export const MyShader = () => { /* ... */ };
```

If the SKSL source depends on a prop (e.g. user-selectable variants), memoize
with `useMemo` keyed on the variant:
```tsx
const source = useMemo(
  () => Skia.RuntimeEffect.Make(buildSksl(variant))!,
  [variant]
);
```

## Coordinate System

| Coord | Origin | Range | Source |
|---|---|---|---|
| `pos` (the `main` parameter) | top-left | `0..canvasWidth, 0..canvasHeight` (pixels) | implicit |
| Normalized UV | top-left | `0..1` on both axes | `pos / resolution` |
| Aspect-correct UV | center | `-aspect..aspect` on x, `-1..1` on y | `(2 * pos - resolution) / resolution.y` |
| Centered 0..1 | center | `-0.5..0.5` | `pos / resolution - 0.5` |

`resolution` is **not** a built-in — you must declare and pass it yourself
(see Uniforms below). Skia exposes `<Fill>` size implicitly via the paint
context, but inside the shader you need an explicit `resolution` uniform if
you want aspect-correct math.

## The `<Shader>` Component

```tsx
<Shader
  source={source}                  // SkRuntimeEffect from Make()
  uniforms={{                      // matches uniform names in SKSL
    resolution: [w, h],
    time: 1.0,
    color: [1, 0, 0, 1],
  }}
  transform={[{ rotate: Math.PI / 4 }]}     // optional local transform
  origin={{ x: w / 2, y: h / 2 }}           // optional transform origin
>
  {/* Optional children = child shaders (see child-shaders.md) */}
</Shader>
```

`uniforms` accepts either:
- A plain object — re-evaluated each render
- A Reanimated `SharedValue<object>` or `useDerivedValue` result — animated on the UI thread

### Uniform value formats

| SKSL type | JS value |
|---|---|
| `float`, `int` | `1.5`, `3` |
| `float2`, `int2` | `[x, y]` |
| `float3`, `int3` | `[r, g, b]` |
| `float4`, `int4` | `[r, g, b, a]` |
| `float2x2` | `[a,b, c,d]` row-major (4 floats) |
| `float3x3` | 9 floats row-major |
| `float4x4` | 16 floats row-major |
| `float[N]` | flat array of N floats |
| `uniform shader x` | a **child component**, not a uniforms-prop value |

**Pitfall:** the SKSL compiler will silently drop a uniform if it's never
referenced in the body. Then passing it from JS throws
`Uniform '<name>' not found`. Either reference the uniform somewhere (`= u *
0.0 + ...` as a no-op) or remove the JS-side key.

## What Can Paint a Shader

Any `<Shape>` can carry a shader paint as its child. Common patterns:

```tsx
// Full-screen
<Fill><Shader source={src} uniforms={u} /></Fill>

// Rectangle with shader
<Rect x={0} y={0} width={w} height={h}>
  <Shader source={src} uniforms={u} />
</Rect>

// Rounded rect / button-shaped shader
<RoundedRect x={0} y={0} width={200} height={60} r={12}>
  <Shader source={src} uniforms={u} />
</RoundedRect>

// Circle
<Circle cx={100} cy={100} r={50}>
  <Shader source={src} uniforms={u} />
</Circle>

// Path / SVG-shaped
<Path path={mySkPath} color="white">
  <Shader source={src} uniforms={u} />
</Path>
```

## Complete Working Examples

### Static gradient

```tsx
import { Canvas, Fill, Shader, Skia } from "@shopify/react-native-skia";
import { useWindowDimensions } from "react-native";

const source = Skia.RuntimeEffect.Make(`
uniform float2 resolution;
vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    vec3 col = mix(vec3(0.1, 0.2, 0.5), vec3(0.9, 0.3, 0.5), uv.y);
    return vec4(col, 1.0);
}`)!;

export const Gradient = () => {
  const { width, height } = useWindowDimensions();
  return (
    <Canvas style={{ flex: 1 }}>
      <Fill>
        <Shader source={source} uniforms={{ resolution: [width, height] }} />
      </Fill>
    </Canvas>
  );
};
```

### Time-driven animation

```tsx
import { Canvas, Fill, Shader, Skia, useClock } from "@shopify/react-native-skia";
import { useDerivedValue } from "react-native-reanimated";
import { useWindowDimensions } from "react-native";

const source = Skia.RuntimeEffect.Make(`
uniform float2 resolution;
uniform float time;
vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    vec3 col = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));
    return vec4(col, 1.0);
}`)!;

export const Cosmic = () => {
  const { width, height } = useWindowDimensions();
  const clock = useClock();
  const uniforms = useDerivedValue(() => ({
    resolution: [width, height],
    time: clock.value / 1000,
  }));
  return (
    <Canvas style={{ flex: 1 }}>
      <Fill>
        <Shader source={source} uniforms={uniforms} />
      </Fill>
    </Canvas>
  );
};
```

### Gesture-driven uniform

```tsx
import { Canvas, Fill, Shader, Skia } from "@shopify/react-native-skia";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { useSharedValue, useDerivedValue } from "react-native-reanimated";

const source = Skia.RuntimeEffect.Make(`
uniform float2 resolution;
uniform float2 touch;
vec4 main(vec2 pos) {
    float d = distance(pos, touch);
    float r = 0.5 + 0.5 * cos(d * 0.05);
    return vec4(r, r * 0.7, 1.0 - r, 1.0);
}`)!;

export const Ripple = ({ width, height }) => {
  const touch = useSharedValue([width / 2, height / 2]);
  const gesture = Gesture.Pan()
    .onChange((e) => { touch.value = [e.x, e.y]; });
  const uniforms = useDerivedValue(() => ({
    resolution: [width, height],
    touch: touch.value,
  }));
  return (
    <GestureDetector gesture={gesture}>
      <Canvas style={{ width, height }}>
        <Fill>
          <Shader source={source} uniforms={uniforms} />
        </Fill>
      </Canvas>
    </GestureDetector>
  );
};
```

## Shader as an Image Filter (Distortion)

To distort an image, declare a `uniform shader image;` and pass an
`<ImageShader>` child. See [`child-shaders.md`](child-shaders.md) for details.

```tsx
<Shader source={source} uniforms={u}>
  <ImageShader image={img} fit="cover" rect={{ x:0, y:0, width:w, height:h }} />
</Shader>
```

## Component Tree Mental Model

```
<Canvas>                       ← surface (GPU framebuffer)
  <Group transform=...>        ← optional grouping
    <Fill | Rect | Path>       ← paintable (shape)
      <Shader source=...>      ← paint (color provider)
        <ImageShader />        ← optional child shader (uniform shader)
        <LinearGradient />     ← another child shader
      </Shader>
    </Fill>
  </Group>
</Canvas>
```

A `<Shader>` is **a paint**. It needs **something to paint** (a `<Shape>`).
Children of a `<Shader>` become its `uniform shader` parameters, in
declaration order.

## See Also

- [sksl-vs-glsl](sksl-vs-glsl.md) — Syntax cheatsheet for porting GLSL.
- [uniforms-animation](uniforms-animation.md) — Reanimated patterns in depth.
- [child-shaders](child-shaders.md) — `uniform shader`, `ImageShader`.
- [image-effects](image-effects.md) — `BackdropFilter`, `Blur`, `ColorMatrix`.
- Reference: [`reference/uniforms-animation.md`](../reference/uniforms-animation.md).
