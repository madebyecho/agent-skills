# Image Effects, Filters, and BackdropFilter

react-native-skia ships a set of built-in image filters (`Blur`,
`ColorMatrix`, `DisplacementMap`, `Offset`, `Morphology`, etc.) plus the
`RuntimeShader` filter which wraps your own SKSL. This file shows how to
combine them and when to reach for each.

## The Three Layers

1. **Shader paint** (`<Shader>`) — colors *fragments* of a shape.
2. **Image filter** (`<Blur>`, `<ColorMatrix>`, etc.) — runs *after* a shape
   is rasterized, processes the resulting pixel grid.
3. **`<BackdropFilter>`** — filters the *backdrop* (everything underneath)
   and paints it as the layer's background.

Pick by question:
- "Color is a function of position / time / data" → shader paint.
- "Blur / re-color / displace the rendered output" → image filter.
- "I want a frosted-glass strip over scrolling content" → BackdropFilter.

## Built-in Image Filters

### Blur

```tsx
import { Canvas, Image, Blur, useImage } from "@shopify/react-native-skia";

<Canvas style={{ width, height }}>
  <Image image={img} fit="cover" x={0} y={0} width={width} height={height}>
    <Blur blur={20} mode="clamp" />
  </Image>
</Canvas>
```

Cheaper and more correct than a manual SKSL blur for radii > 4 — Skia uses
multi-pass tile blur. Below ~3px you can do it in shader.

### ColorMatrix

A 4×5 matrix that multiplies RGBA and adds an offset. Used for color
grading: saturation, hue rotation, sepia, contrast.

```tsx
import { ColorMatrix } from "@shopify/react-native-skia";

// Grayscale
const gray = [
  0.21, 0.72, 0.07, 0, 0,
  0.21, 0.72, 0.07, 0, 0,
  0.21, 0.72, 0.07, 0, 0,
  0,    0,    0,    1, 0,
];
<Image image={img} ...>
  <ColorMatrix matrix={gray} />
</Image>
```

| Effect | Pattern |
|---|---|
| Grayscale | luminance row repeated 3 times |
| Sepia | RGB→sepia conversion matrix |
| Invert | `-1` on diagonal, `+1` offset |
| Saturate | matrix interp between identity and grayscale by `s` |
| Hue rotate | rotation in YIQ space |
| Brightness | identity diagonal scaled |
| Contrast | identity diagonal scaled with offset to recenter |

### Displacement Map

Displaces each pixel of a source by RG channels of a *displacement* image (a
shader, usually). Built-in `DisplacementMap` is faster than re-implementing
it in SKSL when you already have a normal-map-ish input.

```tsx
<Image image={img} ...>
  <DisplacementMap channelX="r" channelY="g" scale={20}>
    <Shader source={noiseShader} uniforms={u} />
  </DisplacementMap>
</Image>
```

For arbitrary distortion patterns (sin waves, gesture-driven warps), reach
for the SKSL `image.eval(pos + offset)` approach in [child-shaders](child-shaders.md) — that's more flexible.

### Offset / Shadow / DropShadow

```tsx
<Group>
  <DropShadow dx={0} dy={4} blur={8} color="rgba(0,0,0,0.4)" />
  <RoundedRect x={0} y={0} width={200} height={120} r={16} color="white" />
</Group>
```

Shadows are image filters. They run on the layer's alpha. Stack them with
other filters by nesting.

### Morphology (Dilate / Erode)

```tsx
<Image image={img} ...>
  <Morphology operator="dilate" radius={2} />
</Image>
```

`dilate` grows opaque regions, `erode` shrinks them. Useful for hand-drawn
outline thickening, "bloom-lite", or glyph hinting.

## `<RuntimeShader>` — Your SKSL as an Image Filter

Apply a SKSL pass on top of a rendered layer:

```tsx
import { RuntimeShader, Skia } from "@shopify/react-native-skia";

const filter = Skia.RuntimeEffect.Make(`
uniform shader image;
vec4 main(vec2 pos) {
    vec4 c = image.eval(pos);
    return vec4(1.0 - c.rgb, c.a);   // invert
}`)!;

<Group>
  <RuntimeShader source={filter} uniforms={{}} />
  <Image image={img} ... />
</Group>
```

**Order matters:** `<RuntimeShader>` is a *declaration* that attaches to
the current Group's paint — it must appear **before** the content it
filters in the JSX, not after. Inside the Group, everything rendered after
the declaration is filtered through the shader. The wrapped content
becomes the (first) `uniform shader image` input. Pass additional uniforms
via `uniforms`. Pass extra child shaders by nesting them inside
`<RuntimeShader>`.

When to use `<RuntimeShader>` vs a `<Shader>` paint:
- Painting a shape with a procedural color → `<Shader>` inside the shape.
- Post-process an already-rendered layer → `<RuntimeShader>`.

## `<BackdropFilter>` — Glassmorphism

Filters everything *behind* the BackdropFilter region. The classic use case:
frosted-glass card over a scrolling feed.

```tsx
import { Canvas, BackdropFilter, Blur, Fill, RoundedRect } from "@shopify/react-native-skia";

<Canvas style={{ flex: 1 }}>
  {/* … your scrollable / background content rendered into the canvas … */}

  {/* Glass strip from y=200 to y=320 */}
  <BackdropFilter
    filter={<Blur blur={20} />}
    clip={{ x: 16, y: 200, width: width - 32, height: 120, r: 24 }}
  >
    {/* A semi-transparent tint over the blur */}
    <Fill color="rgba(255,255,255,0.25)" />
  </BackdropFilter>
</Canvas>
```

The `clip` prop bounds the filter region (rounded rect supported). Children
of `<BackdropFilter>` paint *on top of* the filtered backdrop.

### Custom SKSL as a BackdropFilter

```tsx
<BackdropFilter
  filter={<RuntimeShader source={myFilter} uniforms={u} />}
  clip={{ x: 0, y: 0, width, height }}
/>
```

Use cases:
- Refractive glass (sample backdrop at offset coords).
- Chromatic aberration on hover.
- Subtle ripple / heat-haze.

```glsl
// Refraction-ish glass: sample backdrop with slight wave
uniform shader image;
uniform float time;
vec4 main(vec2 pos) {
    vec2 d = vec2(
        sin(pos.y * 0.04 + time * 0.6) * 4.0,
        cos(pos.x * 0.04 + time * 0.6) * 4.0
    );
    return image.eval(pos + d);
}
```

## Composing Filters

Filters nest. Inside one, the inner filter's output becomes the outer's
input:

```tsx
<Image image={img} ...>
  <ColorMatrix matrix={contrast}>
    <Blur blur={4} />
  </ColorMatrix>
</Image>
```

Reading top-down in JSX: outer filter applies *after* inner. So here: blur
first, then bump contrast.

## Performance Notes

- **`<Blur>` is the right call for any blur > ~3px.** It uses tile-aware
  multi-pass internally. A naive SKSL blur sampling N×N taps in a loop is
  always slower.
- **Filters allocate offscreen layers.** Stacking many filters costs memory
  bandwidth, not just ALU.
- **BackdropFilter is expensive on Android.** Each frame, the backdrop must
  be re-read. Keep the `clip` region small.
- **DropShadow on a complex Path is slow.** Render the path once into an
  offscreen via `<Group layer>` and shadow the group instead.
- **Live blur (≥20px) over scrolling content** stalls on low-end Android.
  Cap blur radius, lower the Canvas pixel ratio for the glass region, or
  skip the blur on Android via `Platform.select`.

## Recipes

### Frosted glass with a hint of color

```tsx
<BackdropFilter
  filter={
    <Blur blur={24}>
      <ColorMatrix matrix={[
        1.05, 0, 0, 0, 0,
        0, 1.05, 0, 0, 0,
        0, 0, 1.15, 0, 0,
        0, 0, 0,    1, 0,
      ]}/>
    </Blur>
  }
  clip={glassClip}
>
  <Fill color="rgba(255,255,255,0.15)" />
</BackdropFilter>
```

### Image with vignette + grain

```tsx
const grain = Skia.RuntimeEffect.Make(`
uniform shader image;
uniform float2 resolution;
uniform float time;
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec4 main(vec2 pos) {
    vec4 c = image.eval(pos);
    vec2 uv = pos / resolution;
    float v = 1.0 - smoothstep(0.5, 1.0, distance(uv, vec2(0.5)));
    float g = (hash(floor(pos / 2.0) + time) - 0.5) * 0.06;
    return vec4(c.rgb * v + g, c.a);
}`)!;

<Group>
  <RuntimeShader source={grain} uniforms={uniforms} />
  <Image image={img} ... />
</Group>
```

### Sepia toned photo

```tsx
const sepia = [
  0.393, 0.769, 0.189, 0, 0,
  0.349, 0.686, 0.168, 0, 0,
  0.272, 0.534, 0.131, 0, 0,
  0,     0,     0,     1, 0,
];
<Image image={img} ...>
  <ColorMatrix matrix={sepia} />
</Image>
```

### Soft duotone

```tsx
const duotone = Skia.RuntimeEffect.Make(`
uniform shader image;
uniform float4 dark;
uniform float4 light;
vec4 main(vec2 pos) {
    vec4 c = image.eval(pos);
    float l = dot(c.rgb, vec3(0.299, 0.587, 0.114));
    return vec4(mix(dark.rgb, light.rgb, l), c.a);
}`)!;
```

## See Also

- [child-shaders](child-shaders.md) — Deep dive on `uniform shader`.
- [color-palette](color-palette.md) — Cosine palettes, Oklab, HSL.
- [post-processing](post-processing.md) — Bloom, tone mapping, glitch.
- [mobile-performance](mobile-performance.md) — When filters become too expensive.
