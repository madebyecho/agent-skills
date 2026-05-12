# Post-Processing

Effects applied after rendering: tone mapping, bloom, vignette, chromatic
aberration, grain, glitch. In react-native-skia, post-process either:
- Inside the shader's final `return` line (cheap effects).
- Via a `<RuntimeShader>` filter over a rendered layer (heavier effects).

For Skia-built-in post (Blur, ColorMatrix, DropShadow), see
[image-effects](image-effects.md).

## Tone Mapping (HDR → SDR)

Without tone mapping, bright pixels clip and look "wrong". Map HDR linear
values to display.

### Reinhard

```glsl
vec3 reinhard(vec3 c) {
    return c / (1.0 + c);
}
```

Soft, low-contrast. Good for ambient.

### ACES Filmic (Cheap Approximation)

```glsl
vec3 aces(vec3 x) {
    const float a = 2.51, b = 0.03, c = 2.43, d = 0.59, e = 0.14;
    return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}
```

The default for production. Use after lighting, before gamma.

### Uncharted 2 / Hable

```glsl
vec3 uncharted2Tonemap(vec3 x) {
    const float A = 0.15, B = 0.50, C = 0.10, D = 0.20, E = 0.02, F = 0.30;
    return ((x * (A * x + C * B) + D * E) / (x * (A * x + B) + D * F)) - E / F;
}
vec3 uncharted2(vec3 c) {
    vec3 v = uncharted2Tonemap(c * 2.0);
    vec3 w = uncharted2Tonemap(vec3(11.2));
    return v / w;
}
```

## Gamma Correction

Always do this **last**:

```glsl
col = pow(col, vec3(1.0 / 2.2));     // ≈ vec3(0.4545)
```

For most lighting setups: ACES → gamma. For ambient/UI shaders: just gamma
(or skip if your colors are already perceptual).

## Vignette

Darken edges:

```glsl
vec2 uv = pos / resolution;
float v = 1.0 - smoothstep(0.4, 1.0, distance(uv, vec2(0.5)));
col *= v;
```

Adjust the `0.4..1.0` range for intensity. Multiply by ~0.7 for very mild,
go as dark as `pow(v, 4.0)` for cinematic.

## Chromatic Aberration

Channel-shift the image sample:

```glsl
uniform shader image;
vec4 main(vec2 pos) {
    vec2 center = resolution * 0.5;
    vec2 dir = (pos - center) / resolution.y;
    float strength = 0.005;
    float r = image.eval(pos + dir * strength * resolution).r;
    float g = image.eval(pos).g;
    float b = image.eval(pos - dir * strength * resolution).b;
    return vec4(r, g, b, 1.0);
}
```

3 image samples — moderately expensive.

## Film Grain

```glsl
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec4 main(vec2 pos) {
    // ... compute col ...
    float grain = (hash(pos + time * 1000.0) - 0.5) * 0.06;
    col += grain;
    return vec4(col, 1.0);
}
```

## Bloom (Approximation, Single-Pass)

Real bloom needs a downsampled blur pass — use the built-in `<Blur>` layered
on a copy of the rendered image. Single-pass cheap "bloom" via radial blur:

```glsl
uniform shader image;
vec4 main(vec2 pos) {
    vec3 base = image.eval(pos).rgb;
    vec3 bloom = vec3(0.0);
    for (int i = 1; i <= 6; i++) {
        float r = float(i) * 3.0;
        bloom += image.eval(pos + vec2( r, 0)).rgb;
        bloom += image.eval(pos + vec2(-r, 0)).rgb;
        bloom += image.eval(pos + vec2(0,  r)).rgb;
        bloom += image.eval(pos + vec2(0, -r)).rgb;
    }
    bloom /= 24.0;
    bloom = max(bloom - 0.7, 0.0);    // threshold
    return vec4(base + bloom * 1.5, 1.0);
}
```

24 samples — slow. For real bloom on mobile use:
```tsx
<Group>
  <Image image={img} ... />
  <Image image={img} ...>
    <Blur blur={20} />
  </Image>   {/* blended on top with screen blend mode */}
</Group>
```

## Glitch / Datamosh

```glsl
vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    float h = hash(vec2(floor(pos.y / 4.0), floor(time * 8.0)));
    if (h > 0.95) {
        uv.x += (hash(vec2(floor(time * 20.0))) - 0.5) * 0.3;
    }
    return image.eval(uv * resolution);
}
```

## Sharpen

```glsl
vec4 main(vec2 pos) {
    vec3 c = image.eval(pos).rgb;
    vec3 n = image.eval(pos + vec2(0, -1)).rgb;
    vec3 s = image.eval(pos + vec2(0,  1)).rgb;
    vec3 e = image.eval(pos + vec2( 1, 0)).rgb;
    vec3 w = image.eval(pos + vec2(-1, 0)).rgb;
    vec3 high = c * 5.0 - n - s - e - w;
    return vec4(mix(c, high, 0.5), 1.0);
}
```

## CRT / Retro Scanlines

```glsl
float scan = 0.5 + 0.5 * sin(pos.y * 1.5);
col *= mix(1.0, scan, 0.15);
```

## Order Matters

In the final shader, apply effects in this order:
1. Compute base color.
2. Lighting + shadows.
3. **Tone map** (ACES) to bring HDR into 0..1.
4. Color grading (lift/gamma/gain).
5. Vignette.
6. Chromatic aberration (optional).
7. Grain.
8. **Gamma** (last).

## See Also

- [image-effects](image-effects.md) — Built-in filters (Blur, ColorMatrix).
- [color-palette](color-palette.md) — Color grading.
- [lighting-model](lighting-model.md) — Generates the HDR input.
