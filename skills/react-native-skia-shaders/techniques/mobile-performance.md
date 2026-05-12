# Mobile Performance

react-native-skia runs on phones with thermal limits, modest GPUs, and a
60–120Hz display budget. Shaders that fly on desktop will tank a Pixel 6a.
This file is the budget and the debug toolkit.

## The Budget

Per-pixel cost, broken down for a 1080×1920 ≈ 2M fragments/frame at 60fps:

| Operation | Approx GPU cost | Mobile budget per fragment |
|---|---|---|
| `+`, `-`, `*`, `min`, `max`, `dot`, `length(vec2)` | 1 cycle | basically free |
| `sin`, `cos`, `exp`, `log`, `pow` | 4–8 cycles | dozens are fine |
| `length(vec3)`, `normalize(vec3)` | 4–6 cycles | dozens are fine |
| Hash (`fract(sin(dot(...)))`) | ~10 cycles | use sparingly |
| 1× FBM octave (4 hashes + 4 mixes) | ~50 cycles | 4–5 octaves max |
| 1× SDF sphere/box evaluation | ~10 cycles | dozens per ray OK |
| Full 3-axis SDF normal (6 evals) | ~60 cycles | 1× per pixel only |
| 1× ray-march step | 1× SDF + ~5 cycles | 48 (Android) / 80 (iOS) max |
| `image.eval` (texture fetch) | ~50 cycles bandwidth-bound | unlimited locally, expensive globally |

**Rule of thumb:** keep the *worst-case fragment* under ~1000 cycles of
work for 60fps on a mid-tier Android. Halve that for 120Hz iOS.

## Per-Phone Tier Estimates

| Tier | Examples | Ray-march steps | FBM octaves | Inner-loop budget |
|---|---|---|---|---|
| **Flagship iOS** | iPhone 14 Pro+ | 96 | 6 | ~1000 |
| **Flagship Android** | Pixel 8, S24 | 80 | 5 | ~700 |
| **Mid-tier Android** | Pixel 6a, A54 | 48 | 4 | ~400 |
| **Low-end Android** | most 2021 budget phones | 32 | 3 | ~200 |
| **Web (Skia CanvasKit)** | desktop browser | 128 | 6 | ~1500 |

If your target audience includes low-end Android, dial down accordingly or
ship a fallback (a `<LinearGradient>` instead of a procedural shader).

## Profiling

### Flipper + perf monitor

`yarn react-native run-android --variant=release` then open Flipper → Performance.
Watch the JS/UI thread and dropped frames.

### React Native Performance Monitor

In Expo: shake device → "Show Perf Monitor". Look at the UI line — that's
shader time. If it dips below your target FPS, the shader is too expensive
for the device.

### `Canvas` `onSize` + Time per frame

```tsx
import { useEffect, useRef } from "react";

const lastFrame = useRef(performance.now());
const fpsClock = useDerivedValue(() => {
  const now = performance.now();
  const dt = now - lastFrame.current;
  lastFrame.current = now;
  return dt;
});
```

(Hacky — Reanimated and the Canvas don't expose an official frame callback
yet in all versions. Use Flipper for reliable numbers.)

### Step-count visualization

The fastest way to diagnose a slow shader is to visualize what's inside:

```glsl
// Inside your ray-march:
int steps = 0;
for (int i = 0; i < MAX_STEPS; i++) {
    steps = i;
    // ...
    if (d < SURF_DIST) break;
    if (t > MAX_DIST) break;
}
// Then return:
return vec4(vec3(float(steps) / float(MAX_STEPS)), 1.0);
```

Red zones → bottleneck. Often it's a grazing ray that never converges; cap
`MAX_STEPS` lower or add a sky bail-out.

## Optimization Checklist

### Reduce iterations

- Cap `MAX_STEPS` to per-tier budget.
- Use a near/far split: trace at low quality far out, refine near surfaces.
- For FBM, replace 6 octaves with 3 + dynamic detail (LOD by `length(rd)`).
- Replace `sin(t)` running animations with `cos`-of-position to remove the temporal frequency from the inner loop.

### Use `half` where possible

```glsl
half4 main(float2 pos) {   // half output is fine
    half3 col = half3(0.5);
    // ... half math is faster on mobile GPUs
    return half4(col, 1.0);
}
```

Position math should stay `float`/`float2` (`half2` precision is ~10 bits,
insufficient for pixel-accurate coords). Color math is the right place for
`half`.

### Avoid expensive functions in the hot path

- `pow(x, 64.0)` for sharp specular → unroll to `x*x; x = x*x; x = x*x;` (6
  squarings = ^64). Same result, 5–10× faster on integrated GPUs.
- `pow(x, y)` with constant `y` < 4 → manual multiplies are always faster.
- `exp(-x)` ramps → `1.0 / (1.0 + x)` is a perceptually-close cheap approx.
- `length(p)` then `length(p)*length(p)` → use `dot(p, p)` once.

### Sample image at lower rate

If you're sampling a background image and applying noise, sample once and
multiply by noise — don't sample inside the noise loop.

### Pre-compute in a uniform

Anything that's constant per frame should be a uniform, not a per-pixel
computation. Camera matrices, sun direction, palette params, etc.

### Lower the Canvas resolution

For full-screen procedural backgrounds, render at 0.5× or 0.75× and let the
display upscale:

```tsx
const ratio = 0.75;
<Canvas style={{
  width, height,
  transform: [{ scale: 1 / ratio }],     // upscale the visual
}}>
  {/* render at small pixel size */}
</Canvas>
```

(Or use `Canvas` `pixelRatio` if your version exposes it.) Visually for
soft procedural noise/gradients, the user can't tell.

### Use the right tool

- 20px blur → built-in `<Blur>`, not SKSL.
- Color grading → `<ColorMatrix>`, not SKSL.
- Mesh gradient → SKSL is the right tool.
- Displacement of an image → SKSL with `<ImageShader>` child + small offset.

## Platform Differences

### iOS (Metal backend)

- `half` is consistently fast.
- `pow`, `exp`, `log` are fast.
- Branching is usually fine — no need to lerp instead of `if`.
- Older devices (iPhone X and below) have lower fillrate; full-screen
  procedural shaders cost.

### Android (Vulkan / OpenGL)

- `half` benefit varies by GPU vendor — Adreno (Qualcomm) and Mali (ARM)
  both benefit; PowerVR less so.
- Aggressive branching can stall older Mali GPUs; prefer `mix`/`step` for
  short branches.
- Thermal throttling drops GPU clock to ~50% after sustained load. A shader
  that runs 60fps cold may drop to 30fps after 2 minutes.
- `dFdx`/`dFdy` are reliable on Vulkan but slow on older OpenGL ES.

### Web (Skia CanvasKit)

- Way more headroom — typically a desktop GPU.
- But: `RuntimeEffect.Make` compile errors are clearer in browser DevTools;
  use that for porting.

## Battery Considerations

A full-screen 60Hz shader can pull 1–2W on a phone. After 5 minutes the
device is warm. Mitigations:

- Drop to 30fps for ambient backgrounds (gate `useClock` value).
- Pause `useClock` when the view is out of focus (`useIsFocused()` from
  React Navigation).
- Use `mode="default"` on the Canvas so it only renders on prop change
  (great for static / occasional-update shaders).

```tsx
import { useIsFocused } from "@react-navigation/native";
const focused = useIsFocused();
const t = useDerivedValue(() => focused ? clock.value / 1000 : 0);
```

## When Not to Use a Shader

- Simple linear gradient → `<LinearGradient>` (built-in, GPU-optimal).
- Solid-color fade → React Native's `Animated.View` opacity.
- A button glow → `<DropShadow>` is way cheaper than a SKSL bloom.
- "Just one image with rounded corners" → `<Image>` with `borderRadius`.

## See Also

- [sksl-pitfalls](sksl-pitfalls.md) — Compile-time failure modes.
- [ray-marching](ray-marching.md) — Includes a per-tier `MAX_STEPS` table.
- [procedural-noise](procedural-noise.md) — Octave / detail LOD patterns.
