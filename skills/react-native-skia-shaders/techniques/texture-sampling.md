# Texture Sampling

Reading pixels from a child `<ImageShader>` or another shader inside SKSL.
The `image.eval(coord)` intrinsic always interpolates (bilinear by default,
depending on Skia's filter mode); higher-quality filtering you implement
yourself.

## Basic Sample

```glsl
uniform shader image;
vec4 main(vec2 pos) {
    return image.eval(pos);     // bilinear filtered, in pixel coords
}
```

## Pixel-Perfect (Nearest)

```glsl
return image.eval(floor(pos) + 0.5);     // snap to pixel center
```

Force nearest-neighbor by snapping coords. Or set the `filter` prop on
`<ImageShader>` if your version supports it.

## Bilinear (Manual, Filtered Sample)

```glsl
vec4 bilinear(vec2 p) {
    vec2 q = floor(p) + 0.5;
    vec2 f = p - q;
    vec4 a = image.eval(q + vec2(0, 0));
    vec4 b = image.eval(q + vec2(1, 0));
    vec4 c = image.eval(q + vec2(0, 1));
    vec4 d = image.eval(q + vec2(1, 1));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
```

Useful if Skia's default sampling is already nearest (depending on
`<ImageShader>` filter prop).

## Bicubic (Higher Quality)

```glsl
// Catmull-Rom-ish — 4×4 kernel
float w0(float a) { return (1.0/6.0) * (a * (a * (-a + 3.0) - 3.0) + 1.0); }
float w1(float a) { return (1.0/6.0) * (a * a * (3.0 * a - 6.0) + 4.0); }
float w2(float a) { return (1.0/6.0) * (a * (a * (-3.0 * a + 3.0) + 3.0) + 1.0); }
float w3(float a) { return (1.0/6.0) * (a * a * a); }

vec4 bicubic(vec2 p) {
    vec2 i = floor(p);
    vec2 f = p - i;
    // ... 16 image.eval calls weighted ...
}
```

16 samples — usually overkill on mobile. Use bilinear unless explicitly
upsampling.

## Box Blur (Cheap)

```glsl
vec4 boxBlur(vec2 p, float r) {
    vec4 sum = vec4(0.0);
    const int N = 3;
    float n = 0.0;
    for (int y = -N; y <= N; y++)
    for (int x = -N; x <= N; x++) {
        sum += image.eval(p + vec2(float(x), float(y)) * r);
        n += 1.0;
    }
    return sum / n;
}
```

49 samples — slow. For any radius > 3, use the built-in `<Blur>` filter.

## Tile Modes (`tx`, `ty` Props)

`<ImageShader>` controls what happens outside its `rect`:

| `tx`/`ty` | Behavior outside rect |
|---|---|
| `"clamp"` | Edge pixels extend |
| `"decal"` | Transparent black |
| `"mirror"` | Reflective tiling |
| `"repeat"` | Wraps to other side |

For distortion shaders, **`"clamp"` is the safest default** — avoids black
borders when displacement exceeds the rect.

## Sampling at Sub-Pixel Offsets

`image.eval` accepts fractional coordinates. Each sample is bilinearly
filtered by Skia. So:

```glsl
return image.eval(pos + vec2(0.25, 0.0));     // shifts by 1/4 pixel, filtered
```

## Sampling Outside The Image's Natural Pixels

If the `<ImageShader rect>` covers the full Canvas but the image's natural
size is smaller, `image.eval` returns interpolated pixels at the rect-scale
mapped to image-pixel-space. Skia handles the mapping; your coords are
**Canvas pixels**.

## No-Tile Texture Trick (Procedural Variation)

For tiled textures that look obviously tiled, dither by sub-tile offsets:

```glsl
vec4 noTile(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 r1 = hash22(i + vec2(0, 0));
    vec2 r2 = hash22(i + vec2(1, 0));
    vec2 r3 = hash22(i + vec2(0, 1));
    vec2 r4 = hash22(i + vec2(1, 1));
    vec4 c1 = image.eval((p + r1) * scale);
    vec4 c2 = image.eval((p + r2) * scale);
    vec4 c3 = image.eval((p + r3) * scale);
    vec4 c4 = image.eval((p + r4) * scale);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(c1, c2, u.x), mix(c3, c4, u.x), u.y);
}
```

4 texture fetches; breaks visible repetition.

## See Also

- [child-shaders](child-shaders.md) — How `<ImageShader>` works.
- [image-effects](image-effects.md) — When to use built-in Blur instead.
- [domain-warping](domain-warping.md) — Distorting the sample coord.
