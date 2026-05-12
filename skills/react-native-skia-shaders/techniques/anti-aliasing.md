# Anti-Aliasing

How to render sharp edges without staircase aliasing. For SDF-based shapes,
analytical AA is free and pixel-perfect — that's the right answer 95% of
the time on mobile.

## Analytical AA (SDFs)

```glsl
float aa = 1.5 / resolution.y;                      // half-pixel width in world units
float alpha = 1.0 - smoothstep(-aa, aa, d);
vec3 col = mix(bg, fg, alpha);
```

Smoothstep interpolates the alpha over a 2-pixel band centered on the
shape's edge. Result: pixel-perfect rendering of any SDF at any resolution.

**Why `1.5 / resolution.y`?** It's the world-space width of one pixel (the
factor of 2 comes from the `(2.0 * pos - res)/res.y` aspect math; tweak the
constant to taste — `1.0` for crisp, `2.0` for soft).

## Using `fwidth` (Screen-Space Derivative)

If you have access to `fwidth(d)`, it gives the change in `d` per pixel
automatically:

```glsl
float aa = fwidth(d);
float alpha = 1.0 - smoothstep(-aa, aa, d);
```

Supported on most modern Skia backends (Vulkan, Metal). On older Android
OpenGL ES, `fwidth` may be imprecise — fall back to the constant `aa`.

## Outline / Stroke AA

```glsl
float thickness = 0.005;
float aa = 1.5 / resolution.y;
float stroke = 1.0 - smoothstep(thickness, thickness + aa, abs(d));
col = mix(col, strokeColor, stroke);
```

## Soft Edge (Glow)

```glsl
float glow = exp(-d * 50.0);
col += glowColor * glow;
```

## Supersampling (SSAA)

When the SDF is non-trivial and `smoothstep` doesn't help (e.g.,
high-frequency noise patterns, sharp specular highlights), supersample:

```glsl
// 2x2 SSAA
vec3 col = vec3(0.0);
const float offset = 0.25;
for (int y = 0; y < 2; y++) {
    for (int x = 0; x < 2; x++) {
        vec2 dp = vec2(float(x) * 0.5 - offset, float(y) * 0.5 - offset);
        col += shade(pos + dp);
    }
}
col /= 4.0;
return vec4(col, 1.0);
```

4× cost. Use only when needed and only on the parts that need it.

## Rotated-Grid SSAA (4-tap)

```glsl
const vec2 offsets[4] = vec2[](
    vec2(0.125, 0.375), vec2(0.375, -0.125),
    vec2(-0.125, -0.375), vec2(-0.375, 0.125)
);
```

Distributes samples better than a regular 2×2 grid; same cost.

## Temporal AA

react-native-skia doesn't expose a history buffer, so true TAA isn't really
practical. The closest equivalent is rendering a slightly-jittered shader
and letting the user's eye average it — usually not worth the complexity.

## Cheap AA via `smoothstep` on Coverage

For any binary mask, replace `step(0.5, x)` with `smoothstep(0.4, 0.6, x)`.
Cheap visual smoothing.

## Pitfalls

- **`fwidth(constant)` = 0** → divide-by-zero. Always `max(fwidth(d), 1e-5)`.
- **`smoothstep` with `edge0 > edge1`** silently produces wrong output.
- **AA width too large** → blurry edges; too small → still see stairs.
  `1.5 / resolution.y` is a good default; halve for "crisp", double for "soft".
- **Multiplying AA alpha into RGB without premultiplying** breaks blend
  modes. Skia paints expect premultiplied: `return vec4(rgb * a, a);`.

## See Also

- [sdf-2d](sdf-2d.md) / [sdf-3d](sdf-3d.md) — Source of `d`.
- [post-processing](post-processing.md) — Final-pass touch-ups.
