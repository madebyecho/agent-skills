---
name: react-native-skia-shaders
description: >
  Comprehensive SKSL (Skia Shading Language) shader techniques for
  react-native-skia — ray marching, SDF modeling, procedural noise, lighting,
  post-processing, image filters, BackdropFilter, child shaders, gesture- and
  Reanimated-driven uniforms. Triggers on tasks involving Shader, RuntimeEffect,
  SKSL, custom visual effects, animated backgrounds, image distortion, blur,
  glow, glass / liquid effects, or any request to "write a shader" in a React
  Native or Expo app using @shopify/react-native-skia.
license: MIT
metadata:
  author: madebyecho
  version: "1.0.0"
  category: graphics
---

# React Native Skia Shaders

A unified skill covering 25+ SKSL shader techniques adapted for
`@shopify/react-native-skia`. SKSL is Skia's portable shading language — a
GLSL-like dialect that compiles to Metal (iOS), Vulkan/OpenGL (Android), and
WebGPU/WebGL (web). Most ShaderToy / GLSL recipes translate, but the
**type system**, **entry point**, **coordinate system**, **uniform
declaration**, and **child-shader / image sampling** are different. Don't
copy-paste GLSL — port it.

## When to Apply

Reach for this skill when:
- Writing or porting any SKSL shader for `@shopify/react-native-skia`
- Building animated backgrounds, mesh gradients, ink/water/glass effects, particle fields
- Distorting, blurring, or color-grading images with `<Shader>` + `<ImageShader>` or `<RuntimeShader>` filters
- Composing `BackdropFilter` for live-blur / glassmorphism over scrolling content
- Driving shader uniforms from gestures, Reanimated `useSharedValue`, or `useClock`
- Debugging "compilation failed" / black-screen issues in `Skia.RuntimeEffect.Make`
- Picking a performance budget that won't melt mid-tier Android phones
- Translating a ShaderToy / GLSL snippet to SKSL

Skip this skill for: legacy `react-native-svg` masks, animated GIF playback, native iOS Metal / Android Vulkan shaders written outside Skia, Three.js/expo-three (those use raw GLSL with a different runtime).

## Skill Structure

```
react-native-skia-shaders/
├── SKILL.md                          # This file — entry point & routing
├── techniques/                       # Implementation guides (read per routing table)
│   ├── rn-skia-integration.md        # Canvas, Fill, Shader, RuntimeEffect wiring
│   ├── sksl-vs-glsl.md               # Conversion cheatsheet (THE most-used file)
│   ├── uniforms-animation.md         # Reanimated, useClock, gesture-driven uniforms
│   ├── child-shaders.md              # uniform shader, ImageShader, BackdropFilter
│   ├── image-effects.md              # Blur, ColorMatrix, Displacement, RuntimeShader filter
│   ├── mobile-performance.md         # GPU budgets, profiling, fallbacks
│   ├── sksl-pitfalls.md              # Common SKSL compile errors & fixes
│   ├── sdf-2d.md                     # 2D signed distance functions
│   ├── sdf-3d.md                     # 3D signed distance functions
│   ├── ray-marching.md               # Sphere tracing with SDF
│   ├── csg-boolean-operations.md     # Smooth blends, intersections
│   ├── domain-warping.md             # Distort space with noise
│   ├── domain-repetition.md          # Infinite repetition, folding
│   ├── lighting-model.md             # Phong, Blinn-Phong, PBR-lite
│   ├── shadow-techniques.md          # Hard & soft shadows
│   ├── normal-estimation.md          # Tetrahedron technique
│   ├── ambient-occlusion.md          # SDF AO
│   ├── procedural-noise.md           # Value, Perlin, Simplex, FBM
│   ├── voronoi-cellular-noise.md     # Worley, F1/F2 distances
│   ├── color-palette.md              # Cosine palettes, Oklab, HSL
│   ├── procedural-2d-pattern.md      # Bricks, hex, truchet
│   ├── polar-uv-manipulation.md      # Polar, kaleidoscope
│   ├── fractal-rendering.md          # Mandelbrot, Julia
│   ├── sdf-tricks.md                 # Hollowing, outlines, debug viz
│   ├── post-processing.md            # Bloom, tone mapping, vignette
│   ├── anti-aliasing.md              # SDF AA, smoothstep AA
│   ├── matrix-transform.md           # Camera look-at, FOV
│   ├── texture-sampling.md           # ImageShader sampling patterns
│   ├── atmospheric-scattering.md     # Sky, fog, sunset
│   └── particle-system.md            # Stateless particles
└── reference/                        # Deep-dive math, advanced patterns
    ├── sksl-vs-glsl.md               # Full SKSL spec quick-ref
    ├── uniforms-animation.md         # Reanimated worklet patterns
    ├── ray-marching.md               # Sphere tracing math
    ├── lighting-model.md             # PBR derivations
    ├── procedural-noise.md           # Noise function theory
    └── ...
```

## How to Use

1. **Identify the technique(s)** from the Routing Table below.
2. **Always read `techniques/rn-skia-integration.md`** before generating any shader code — it shows the exact React component wiring (`<Canvas>` → `<Fill>` → `<Shader>` → `RuntimeEffect.Make`) and how to feed uniforms.
3. **Always read `techniques/sksl-vs-glsl.md`** before porting a GLSL/ShaderToy snippet — the translation is not free.
4. **Read the matched `techniques/*.md`** — each contains core principles, SKSL-correct code templates, and a worked example.
5. **Follow the reference link** at the bottom of each technique file if you need math derivations.
6. Apply the **Performance Budget** (below) — react-native-skia runs on phones, not desktop GPUs.

## Technique Routing Table

| User wants to create... | Primary technique | Combine with |
|---|---|---|
| **First-time SKSL shader, "just show me how"** | [rn-skia-integration](techniques/rn-skia-integration.md) | sksl-vs-glsl |
| **Port a ShaderToy / GLSL effect** | [sksl-vs-glsl](techniques/sksl-vs-glsl.md) | rn-skia-integration |
| Animated background driven by time | [uniforms-animation](techniques/uniforms-animation.md) | procedural-noise, color-palette |
| Gesture-controlled distortion | [uniforms-animation](techniques/uniforms-animation.md) | domain-warping, child-shaders |
| Distorted / wavy image | [child-shaders](techniques/child-shaders.md) | domain-warping, image-effects |
| Glass / frosted / glassmorphism | [child-shaders](techniques/child-shaders.md) + [image-effects](techniques/image-effects.md) | post-processing |
| Live blur over scrolling content (`BackdropFilter`) | [image-effects](techniques/image-effects.md) | child-shaders |
| Color grading an image | [image-effects](techniques/image-effects.md) | color-palette |
| Displacement map / liquid effect | [image-effects](techniques/image-effects.md) + [domain-warping](techniques/domain-warping.md) | procedural-noise |
| Mesh gradient / fluid color blob | [procedural-noise](techniques/procedural-noise.md) | color-palette, domain-warping |
| 3D objects / scenes from math | [ray-marching](techniques/ray-marching.md) + [sdf-3d](techniques/sdf-3d.md) | lighting-model, shadow-techniques |
| Smooth-blended 3D shapes | [csg-boolean-operations](techniques/csg-boolean-operations.md) | sdf-3d, ray-marching |
| Infinite repeating patterns | [domain-repetition](techniques/domain-repetition.md) | sdf-3d, ray-marching |
| Organic / warped shapes | [domain-warping](techniques/domain-warping.md) | procedural-noise |
| Realistic lighting (Phong, PBR-lite) | [lighting-model](techniques/lighting-model.md) | shadow-techniques, ambient-occlusion |
| Soft shadows | [shadow-techniques](techniques/shadow-techniques.md) | lighting-model |
| Surface normals from SDF | [normal-estimation](techniques/normal-estimation.md) | sdf-3d |
| Ambient occlusion | [ambient-occlusion](techniques/ambient-occlusion.md) | lighting-model, normal-estimation |
| Noise / FBM textures | [procedural-noise](techniques/procedural-noise.md) | domain-warping |
| Tiled 2D patterns | [procedural-2d-pattern](techniques/procedural-2d-pattern.md) | polar-uv-manipulation |
| Voronoi / cell patterns | [voronoi-cellular-noise](techniques/voronoi-cellular-noise.md) | color-palette |
| Fractals (Mandelbrot, Julia) | [fractal-rendering](techniques/fractal-rendering.md) | color-palette, polar-uv-manipulation |
| Color grading / palettes | [color-palette](techniques/color-palette.md) | — |
| Bloom / tone mapping / glitch | [post-processing](techniques/post-processing.md) | child-shaders |
| 2D shapes / UI from SDF | [sdf-2d](techniques/sdf-2d.md) | color-palette, anti-aliasing |
| Sky / fog / atmospheric | [atmospheric-scattering](techniques/atmospheric-scattering.md) | — |
| Stateless particles (sparks, stars) | [particle-system](techniques/particle-system.md) | procedural-noise |
| Polar / kaleidoscope | [polar-uv-manipulation](techniques/polar-uv-manipulation.md) | procedural-2d-pattern |
| Anti-aliased SDF rendering | [anti-aliasing](techniques/anti-aliasing.md) | sdf-2d |
| Camera transforms / look-at | [matrix-transform](techniques/matrix-transform.md) | ray-marching |
| Image sampling tricks | [texture-sampling](techniques/texture-sampling.md) | child-shaders |
| SDF tricks / optimization | [sdf-tricks](techniques/sdf-tricks.md) | sdf-3d, ray-marching |
| "It compiles but is black" / crashes | [sksl-pitfalls](techniques/sksl-pitfalls.md) + [mobile-performance](techniques/mobile-performance.md) | — |

## SKSL Quick Reference (most-used translations)

When the user shows you GLSL / ShaderToy code, apply these mechanical rewrites **before** anything else (full table in [`techniques/sksl-vs-glsl.md`](techniques/sksl-vs-glsl.md)):

| GLSL / ShaderToy | SKSL (react-native-skia) |
|---|---|
| `void mainImage(out vec4 c, in vec2 fc)` | `vec4 main(vec2 pos)` (or `half4 main(float2 pos)`) |
| Implicit `fragColor` write | `return vec4(...);` |
| `fragCoord` / `gl_FragCoord.xy` | `pos` (the parameter — already pixel-space, top-left origin) |
| `iResolution.xy` | A `uniform float2 resolution;` you must pass yourself |
| `iTime` | A `uniform float time;` driven by `useClock()` or Reanimated |
| `iMouse` | A `uniform float2 touch;` driven by `Gesture.Pan()` |
| `texture(iChannel0, uv)` | `image.eval(uv * resolution)` with `uniform shader image;` |
| `#version 300 es` / `precision highp float;` | **Remove** — SKSL has no `#version` |
| `vec2`, `vec3`, `vec4` | Same — or `float2/3/4` (interchangeable); prefer `half2/3/4` for color math |
| `mat2`, `mat3` | `float2x2`, `float3x3` (or keep `mat2`/`mat3` — both work) |
| `out vec4 fragColor;` | **Delete** — `main` returns a `vec4` instead |
| `gl_FragCoord.xy / iResolution.xy` | `pos / resolution` |

### Critical entry point

Every SKSL shader for react-native-skia returns a color:

```glsl
uniform float2 resolution;
uniform float time;

vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;     // 0..1
    vec3 col = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));
    return vec4(col, 1.0);
}
```

`pos` is **pixel-space, top-left origin** — same as `gl_FragCoord.xy`. Aspect-correct UVs:
```glsl
vec2 uv = (2.0 * pos - resolution) / resolution.y;   // -aspect..aspect on x, -1..1 on y
```

### Wiring it into a React component

```tsx
import { Canvas, Fill, Shader, Skia, useClock } from "@shopify/react-native-skia";
import { useDerivedValue, useWindowDimensions } from "react-native";

const source = Skia.RuntimeEffect.Make(`
uniform float2 resolution;
uniform float time;
vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    return vec4(0.5 + 0.5 * cos(time + uv.xyx + vec3(0,2,4)), 1.0);
}
`)!;

export const Cosmic = () => {
  const { width, height } = useWindowDimensions();
  const clock = useClock();                                    // ms shared value
  const uniforms = useDerivedValue(() => ({
    resolution: [width, height],
    time: clock.value / 1000,                                  // seconds
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

`uniforms` accepts a plain object or a Reanimated derived value. The object keys must exactly match the `uniform` names in the SKSL source. The values must be numbers or arrays of numbers — vectors are arrays (`float2` → `[x, y]`), matrices are flat row-major arrays.

## Performance Budget (mobile)

Skia on a phone is **not** WebGL on a desktop. Be aggressive about cost:

| Limit | iOS (Metal) | Android (mid-tier) | Notes |
|---|---|---|---|
| Ray-march steps (per pixel) | ≤ 80 | ≤ 48 | Far below the 128 ShaderToy budget |
| Volume / shadow inner loops | ≤ 16 | ≤ 8 | Each costs ~1 SDF evaluation |
| FBM octaves | ≤ 5 | ≤ 4 | Mid-tier Snapdragons stutter past 4 |
| Total inner-loop iterations / pixel | ≤ 500 | ≤ 300 | Beyond this the GPU thread budget breaks 60fps |
| Canvas size | Match `pixelRatio` carefully | Downscale to ~0.75x | A retina-sized full-screen shader is 3x more work than it looks |
| `pow()`, `exp()`, `log()`, `sin()`, `cos()` | Cheap — use freely | Cheap | Avoid `pow(x, 100.0)` for sharp specular — use repeated `*` |

**Always test on the lowest-end target device.** A shader that hits 60fps on iPhone 15 Pro will often drop to 20fps on a 2022 Pixel 6a. See [`techniques/mobile-performance.md`](techniques/mobile-performance.md) for profiling.

## Common SKSL Pitfalls

(Full list in [`techniques/sksl-pitfalls.md`](techniques/sksl-pitfalls.md).)

### `Skia.RuntimeEffect.Make()` returns `null`

The compile failed. `Make` returns `null` on error and **does not throw**. Always:
```ts
const source = Skia.RuntimeEffect.Make(sksl);
if (!source) throw new Error("SKSL compile failed");
```
The current public signature is `Skia.RuntimeEffect.Make(sksl: string)` — no error callback. If `Make` returns `null`, errors are logged to `console.log` by Skia itself. To diagnose, run the same SKSL in a CanvasKit playground or temporarily wrap with a smaller test shader and bisect the body.

### Wrong uniform sizes → silent black

If you declare `uniform float3 color;` but pass `color: [1, 0]`, the shader silently produces wrong output (sometimes black). Vector arity must match exactly: `float2`=2, `float3`=3, `float4`=4, `float3x3`=9 floats row-major.

### Unused uniforms get pruned

If a uniform is never referenced in the shader body, the compiler removes it. Passing it later throws `Uniform not found`. Either reference the uniform (`= uniform * 0.0 + …`) or drop it from the JS side.

### `texture()` doesn't exist in SKSL

Use `image.eval(pixelCoords)` on a `uniform shader image;` parameter. **Coordinates are in pixels, not UVs** — multiply your normalized UV by the image's natural size or by `resolution` before passing.

### Reserved words

SKSL inherits GLSL's reserved-word list and adds a few. Don't name a variable `sample`, `filter`, `input`, `output`, `texture`, `partition`, `active`, `common`, `cast`, `patch`. Especially `sample` — it collides with a built-in.

### Reanimated values from JS thread

Passing a Reanimated `SharedValue` directly to `uniforms` works (Skia integrates with Reanimated). Passing `sharedValue.value` from JS does **not** animate — it's captured once. Either use `useDerivedValue(() => ({...}))` or pass the SharedValue itself (when supported by your version).

## Quick Recipes

End-to-end shader recipes assembled from technique modules.

### Animated mesh gradient background
1. **Color**: [color-palette](techniques/color-palette.md) cosine palette
2. **Movement**: [domain-warping](techniques/domain-warping.md) low-freq FBM
3. **Time**: [uniforms-animation](techniques/uniforms-animation.md) `useClock`
4. **Output**: [rn-skia-integration](techniques/rn-skia-integration.md) `<Canvas>/<Fill>/<Shader>`

### Glassmorphism card
1. **Backdrop**: `BackdropFilter` wrapping a `Blur(20)` ([image-effects](techniques/image-effects.md))
2. **Refraction**: light displacement via a [child-shader](techniques/child-shaders.md) with a normal-map sample
3. **Edge highlight**: [sdf-2d](techniques/sdf-2d.md) rounded rect AA outline
4. **Composite**: stacked `<RoundedRect>` + glass shader + content

### Liquid / ripple distortion over an image
1. **Source**: [`<ImageShader>`](techniques/child-shaders.md) as a `uniform shader`
2. **Distortion**: [domain-warping](techniques/domain-warping.md) sin/FBM displacement
3. **Driver**: [uniforms-animation](techniques/uniforms-animation.md) `useClock` + tap position
4. **Polish**: [anti-aliasing](techniques/anti-aliasing.md) bilinear sample

### Stylized 2D scene
1. **Shapes**: [sdf-2d](techniques/sdf-2d.md) + [sdf-tricks](techniques/sdf-tricks.md) (layered edges)
2. **Color**: [color-palette](techniques/color-palette.md) + [polar-uv-manipulation](techniques/polar-uv-manipulation.md)
3. **Polish**: [anti-aliasing](techniques/anti-aliasing.md) analytic AA + [post-processing](techniques/post-processing.md) vignette

### Photoreal ray-marched scene (use sparingly on mobile)
1. **Geometry**: [sdf-3d](techniques/sdf-3d.md) + [csg-boolean-operations](techniques/csg-boolean-operations.md)
2. **Rendering**: [ray-marching](techniques/ray-marching.md) + [normal-estimation](techniques/normal-estimation.md)
3. **Lighting**: [lighting-model](techniques/lighting-model.md) + [shadow-techniques](techniques/shadow-techniques.md) (soft)
4. **Atmosphere**: [atmospheric-scattering](techniques/atmospheric-scattering.md) height fog
5. **Post**: [post-processing](techniques/post-processing.md) ACES tone-map + vignette

## Shader Debugging Cookbook

Replace your `return` line with one of these to diagnose:

| What to check | Code | What to look for |
|---|---|---|
| UV mapping | `return vec4(uv, 0.0, 1.0);` | Smooth red→yellow gradient = correct |
| Distance field | `return vec4(d > 0.0 ? vec3(0.9,0.6,0.3) : vec3(0.4,0.7,0.85), 1.0) * (0.8 + 0.2*cos(150.0*d));` | Concentric bands = SDF working |
| Normal direction | `return vec4(n * 0.5 + 0.5, 1.0);` | Smooth color gradients = correct |
| Ray-march step count | `return vec4(vec3(float(steps) / 64.0), 1.0);` | Red hotspots = bottleneck |
| Hit distance | `return vec4(vec3(t / 10.0), 1.0);` | Depth ramp |
| Time pulse | `return vec4(vec3(0.5 + 0.5 * sin(time)), 1.0);` | Confirms `time` uniform is wired |
| Image sample | `return image.eval(pos);` | Confirms `<ImageShader>` child is reaching the shader |
| Resolution check | `return vec4(pos / resolution, 0.0, 1.0);` | Should be a clean 0..1 gradient |

If you see a **solid black canvas**:
1. Did `Skia.RuntimeEffect.Make` return non-null? (check immediately)
2. Are all uniforms supplied with correct arity?
3. Did you forget `return vec4(..., 1.0)` (alpha must be > 0)?
4. Is `<Fill>` or another shape wrapping the `<Shader>`? `<Shader>` is a paint, not a layer — it needs something to paint.

## Anti-Pattern Catalog

- ❌ Calling `Skia.RuntimeEffect.Make` inside a component body — recompiles every render. **Hoist to module scope.**
- ❌ Passing `Date.now()` as the time uniform from JS — locks the frame rate to JS scheduling. Use `useClock()` (worklet-driven).
- ❌ Building uniforms as a fresh object every render without `useDerivedValue` — breaks Reanimated optimization.
- ❌ A 1024×1024 ray-march on `<Fill>` of a full-screen Canvas on a Pixel 4a — that's ~1M pixels × 64 steps = 64M SDF evaluations per frame.
- ❌ Mixing `half` and `float` carelessly in PBR-style math — half overflows in `pow(x, 64.0)` highlights.
- ❌ Using `gl_FragCoord` anywhere — it doesn't exist in SKSL. Use the `pos` parameter.
- ❌ Trying to read pixel neighbours in a single pass — Skia shaders are pure functions of position; multi-pass = re-render the Canvas.
