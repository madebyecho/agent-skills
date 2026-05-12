# Child Shaders (`uniform shader`)

How to nest shaders. The most powerful feature of SKSL for react-native-skia:
you can declare another shader as a uniform and `.eval()` it at any
coordinate. This is how you sample images, gradients, and other shaders
inside your own SKSL.

## Concept

```glsl
uniform shader image;       // a child shader, supplied by the parent

half4 main(float2 pos) {
    return image.eval(pos);  // sample the child at this fragment's position
}
```

In react-native-skia, "the child shader" is a JSX child of `<Shader>`:

```tsx
<Shader source={src} uniforms={u}>
  <ImageShader image={img} fit="cover" rect={rect} />
</Shader>
```

**Children bind to `uniform shader` declarations in source-order.** Names in
SKSL do not matter — the first JSX child is the first `uniform shader`, the
second JSX child is the second, etc.

## `image.eval(coords)` Semantics

- `coords` is in **pixel space** of the *parent* shader's destination.
- The child shader is sampled at those coordinates and returns a color.
- For an `<ImageShader>`, the returned color is the image pixel at those
  coordinates (after applying `fit`, `rect`, `tx`/`ty`).
- For a `<LinearGradient>` child, the returned color is the gradient lookup
  at those coordinates.

`image.eval(pos)` returns a `half4` (or `vec4`, interchangeable).

## Sampling an Image (Distortion / Wave / Blur)

```tsx
import { Canvas, Fill, Shader, ImageShader, Skia, useImage } from "@shopify/react-native-skia";

const sksl = `
uniform shader image;
uniform float2 resolution;
uniform float time;

vec4 main(vec2 pos) {
    vec2 offset = vec2(sin(pos.y * 0.05 + time) * 6.0, 0.0);
    return image.eval(pos + offset);
}`;

const source = Skia.RuntimeEffect.Make(sksl)!;

export const Wavy = ({ uri, width, height }) => {
  const img = useImage(uri);
  const clock = useClock();
  const uniforms = useDerivedValue(() => ({
    resolution: [width, height],
    time: clock.value / 1000,
  }));
  if (!img) return null;
  return (
    <Canvas style={{ width, height }}>
      <Fill>
        <Shader source={source} uniforms={uniforms}>
          <ImageShader image={img} fit="cover" rect={{ x: 0, y: 0, width, height }} />
        </Shader>
      </Fill>
    </Canvas>
  );
};
```

## Image Coordinate Conventions

`ImageShader` accepts:

| Prop | Meaning |
|---|---|
| `image` | The loaded `SkImage` (use `useImage(uri)`). |
| `fit` | `"contain" \| "cover" \| "fill" \| "fitWidth" \| "fitHeight" \| "none" \| "scaleDown"` |
| `rect` | Destination rect in the parent's pixel space. |
| `tx`, `ty` | Tiling mode per axis: `"clamp" \| "decal" \| "mirror" \| "repeat"` |

When sampling near edges, set `tx="decal"` to get transparent outside the
rect, or `"clamp"` to extend edge pixels, or `"mirror"` for seamless wraps.

```tsx
<ImageShader
  image={img}
  fit="cover"
  rect={{ x: 0, y: 0, width, height }}
  tx="clamp"
  ty="clamp"
/>
```

## Sampling at Custom Coordinates

`image.eval(coords)` doesn't care about UVs — it's *destination pixel
coordinates* in the rect. To sample image pixel (50, 50):

```glsl
// Assuming the <ImageShader rect> covers (0,0,w,h):
return image.eval(vec2(50.0, 50.0));
```

If you have normalized UVs:
```glsl
vec2 uv = pos / resolution;   // 0..1
return image.eval(uv * resolution);   // back to pixel coords, same as just `pos`
```

## Multiple Child Shaders

```glsl
uniform shader src;
uniform shader mask;
uniform float2 resolution;

vec4 main(vec2 pos) {
    float m = mask.eval(pos).r;     // grayscale mask
    return src.eval(pos) * m;
}
```

```tsx
<Shader source={blendSrc} uniforms={u}>
  <ImageShader image={photo} fit="cover" rect={r} />    {/* binds to `src`  */}
  <ImageShader image={maskImg} fit="cover" rect={r} />  {/* binds to `mask` */}
</Shader>
```

Three children would bind to three `uniform shader` declarations in
source-order.

## Using a Gradient as a Child Shader

`LinearGradient`, `RadialGradient`, `SweepGradient` are all shaders — they
work as children:

```tsx
<Shader source={src} uniforms={u}>
  <LinearGradient
    start={vec(0, 0)}
    end={vec(width, height)}
    colors={["#ff007a", "#00d4ff"]}
  />
</Shader>
```

```glsl
uniform shader gradient;
vec4 main(vec2 pos) {
    vec4 c = gradient.eval(pos);
    return vec4(c.rgb * 1.5, c.a);   // brighten the gradient
}
```

## Combining an Image and a Procedural Effect

Common recipe: sample an image AND modulate by a noise/SDF:

```glsl
uniform shader image;
uniform float2 resolution;
uniform float time;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    float n = hash(floor(pos / 4.0) + floor(time * 12.0));   // film grain
    vec4 c = image.eval(pos);
    return vec4(c.rgb + (n - 0.5) * 0.08, c.a);
}
```

## Edge Cases & Pitfalls

### Sampling outside the rect

If `pos` falls outside the child shader's `rect`, the result depends on `tx`/`ty`:
- `clamp` → edge color extended (default-ish).
- `decal` → transparent.
- `mirror` → reflects.
- `repeat` → tiles.

For shaders that displace coordinates (distortion), set `tx="clamp"` or `"mirror"` to avoid black borders.

### The `<ImageShader>` `rect` must match where you want pixels

The most common mistake is setting `rect={{ x:0, y:0, width:imageWidth, height:imageHeight }}` (image's natural size) when the Canvas is a different size. Then `image.eval(pos)` returns transparent for any `pos >= imageWidth`. Either:
- Set `rect` to match the Canvas size and `fit="cover"`, OR
- Set `rect` to the image's natural size and scale your coords in SKSL.

### `image.eval` on every pixel = full image sample per fragment

Very fast in raw cost (it's just a texture fetch), but if you call
`image.eval` 8× per fragment for a blur, you're doing 8× the bandwidth. Use
the built-in `<Blur>` filter for big blurs (see [image-effects](image-effects.md)) — it's tile-optimized.

## Worked Example: Image + Mesh Gradient Overlay

```tsx
const src = Skia.RuntimeEffect.Make(`
uniform shader image;
uniform shader gradient;
uniform float blend;
vec4 main(vec2 pos) {
    vec4 a = image.eval(pos);
    vec4 b = gradient.eval(pos);
    return mix(a, vec4(a.rgb * b.rgb * 2.0, a.a), blend);
}`)!;

<Shader source={src} uniforms={{ blend: 0.6 }}>
  <ImageShader image={photo} fit="cover" rect={r} />
  <LinearGradient
    start={vec(0, 0)} end={vec(0, height)}
    colors={["#ffd86b", "#8a2be2"]}
  />
</Shader>
```

## See Also

- [image-effects](image-effects.md) — Built-in Blur, ColorMatrix, Displacement, BackdropFilter.
- [texture-sampling](texture-sampling.md) — Sampling patterns: bilinear, box, dithered.
- [domain-warping](domain-warping.md) — Distorting sampling coords with noise.
- [rn-skia-integration](rn-skia-integration.md) — Basic wiring.
