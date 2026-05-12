# Polar / UV Manipulation

Convert between Cartesian and polar coordinates, then operate in polar to
get rotational symmetry, kaleidoscopes, spirals, ripples.

## Cartesian ↔ Polar

```glsl
// Cartesian → polar: (x, y) → (radius, angle)
vec2 toPolar(vec2 p) {
    return vec2(length(p), atan(p.y, p.x));
}

// Polar → cartesian
vec2 toCart(vec2 p) {     // p.x = r, p.y = theta
    return p.x * vec2(cos(p.y), sin(p.y));
}
```

`atan(y, x)` returns `-PI..PI`. Use `atan(p.x, p.y) + PI` for `0..2*PI`.

## N-Way Kaleidoscope

Fold the angle into a small wedge, then mirror:

```glsl
vec2 kaleidoscope(vec2 p, float segments) {
    float a = atan(p.x, p.y);
    float r = length(p);
    a = mod(a, 6.28318 / segments);
    a = abs(a - 3.14159 / segments);     // mirror around the wedge center
    return vec2(sin(a), cos(a)) * r;
}
```

Then evaluate any pattern at the folded coord — result has `n`-way
symmetry.

## Spiral

```glsl
vec2 spiral(vec2 p, float tightness) {
    float r = length(p);
    float a = atan(p.y, p.x);
    a += tightness * r;
    return r * vec2(cos(a), sin(a));
}
```

Or just use polar coords with a phase shift:
```glsl
float a = atan(p.y, p.x);
float r = length(p);
float pattern = sin(10.0 * r + 5.0 * a);
```

## Log-Polar (Self-Similar Zoom)

```glsl
vec2 logPolar(vec2 p) {
    return vec2(log(length(p)), atan(p.y, p.x));
}
```

In log-polar, a scale becomes a translation — perfect for infinite-zoom
fractal renders.

## Radial Repeat (Ring of Objects)

```glsl
vec2 radialRepeat(vec2 p, float count) {
    float a = atan(p.x, p.y);
    float r = length(p);
    float segment = 6.28318 / count;
    a = mod(a + segment * 0.5, segment) - segment * 0.5;
    return vec2(sin(a), cos(a)) * r;
}
```

Then `sdCircle(radialRepeat(p, 8.0) - vec2(0, 0.4), 0.1)` puts 8 circles in
a ring at radius 0.4.

## Angular Stripes (Pie Slices)

```glsl
float angle = atan(p.y, p.x);
float stripe = step(0.0, sin(angle * 8.0));   // 8 slices
```

## Concentric Rings

```glsl
float r = length(p);
float ring = smoothstep(0.01, 0.0, abs(fract(r * 5.0) - 0.5));
```

## Distort by Angle

```glsl
float a = atan(p.y, p.x);
vec2 q = p + 0.05 * vec2(sin(a * 6.0), cos(a * 6.0));   // flower outline
```

## Worked Example: Animated Kaleidoscope

```glsl
uniform float2 resolution;
uniform float time;

float fbm(vec2 p);   // see procedural-noise.md

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    uv *= 1.5;

    float a = atan(uv.x, uv.y);
    float r = length(uv);
    float seg = 6.28318 / 8.0;
    a = mod(a, seg);
    a = abs(a - seg * 0.5);
    vec2 q = r * vec2(sin(a), cos(a));

    float n = fbm(q * 3.0 + time * 0.1);
    vec3 col = 0.5 + 0.5 * cos(6.28 * (vec3(1.0) * (n + time * 0.05) + vec3(0.0, 0.33, 0.67)));
    return vec4(col, 1.0);
}
```

## Pitfalls

- **`atan(y, x)` has a discontinuity along the negative-x axis** — the
  output jumps from `+π` to `-π`. Patterns that wrap that boundary will
  show a seam. Use `mod` or `abs` to fold it out before evaluating.
- **`atan(p.y, p.x)` vs `atan(p.x, p.y)`** — different conventions, swap
  axes. Test by rotating the input; if pattern rotates the wrong way, swap.
- **`length(zero)` = 0 → divide-by-zero** when normalizing at the origin.
  Use `max(length(p), 0.0001)`.

## See Also

- [procedural-2d-pattern](procedural-2d-pattern.md) — Patterns to apply.
- [fractal-rendering](fractal-rendering.md) — Log-polar zoom.
- [domain-repetition](domain-repetition.md) — Linear analogue.
