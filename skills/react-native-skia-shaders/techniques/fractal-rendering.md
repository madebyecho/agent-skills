# Fractal Rendering

Iterative escape-time visualizations of Mandelbrot, Julia, and 3D
analogues. Mathematically gorgeous, but expensive — on mobile, keep
iteration counts low and zoom levels modest.

## Mandelbrot Set (2D)

```glsl
float mandelbrot(vec2 c) {
    vec2 z = vec2(0.0);
    for (int i = 0; i < 64; i++) {
        z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + c;
        if (dot(z, z) > 4.0) return float(i) / 64.0;
    }
    return 0.0;
}
```

```glsl
vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    vec2 c = uv * 1.5 - vec2(0.5, 0.0);
    float m = mandelbrot(c);
    vec3 col = (m < 1.0) ? 0.5 + 0.5 * cos(6.28 * (vec3(1.0) * m + vec3(0.0, 0.33, 0.67))) : vec3(0.0);
    return vec4(col, 1.0);
}
```

## Smooth Coloring (Continuous Escape)

The bands above are coarse. For smooth color gradients:

```glsl
float mandelbrotSmooth(vec2 c) {
    vec2 z = vec2(0.0);
    for (int i = 0; i < 64; i++) {
        z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + c;
        float d = dot(z, z);
        if (d > 256.0) {
            return float(i) - log2(log2(d)) + 4.0;
        }
    }
    return 0.0;
}
```

Then `col = palette(escape * 0.05);`.

## Julia Set

Same iteration, but the additive constant `k` is fixed (instead of using
`c = uv`):

```glsl
float julia(vec2 z, vec2 k) {
    for (int i = 0; i < 64; i++) {
        z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + k;
        if (dot(z, z) > 4.0) return float(i) / 64.0;
    }
    return 0.0;
}
```

Animate `k` over time for a morphing Julia:
```glsl
vec2 k = 0.7885 * vec2(cos(time * 0.3), sin(time * 0.3));
float j = julia(uv * 1.5, k);
```

## Burning Ship

```glsl
for (int i = 0; i < 64; i++) {
    z = vec2(z.x * z.x - z.y * z.y, abs(2.0 * z.x * z.y)) + c;
    if (dot(z, z) > 4.0) break;
}
```

`abs` on the imaginary part. Produces a ship-like silhouette.

## 3D Fractals: Mandelbulb

```glsl
float mandelbulb(vec3 p) {
    vec3 z = p;
    float dr = 1.0;
    float r = 0.0;
    const float power = 8.0;
    for (int i = 0; i < 8; i++) {
        r = length(z);
        if (r > 2.0) break;
        float theta = acos(z.z / r);
        float phi = atan(z.y, z.x);
        dr = pow(r, power - 1.0) * power * dr + 1.0;
        float zr = pow(r, power);
        theta = theta * power;
        phi = phi * power;
        z = zr * vec3(sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta));
        z += p;
    }
    return 0.5 * log(r) * r / dr;
}
```

Returns a distance estimate — use it as `map(p)` in [ray-marching](ray-marching.md). 8 iterations is mobile-friendly.

## Mandelbox

```glsl
float mandelbox(vec3 p) {
    vec3 z = p;
    float dr = 1.0;
    float scale = 2.5;
    const float fixedRadius2 = 1.0;
    const float minRadius2 = 0.25;
    for (int i = 0; i < 12; i++) {
        z = clamp(z, -1.0, 1.0) * 2.0 - z;
        float r2 = dot(z, z);
        if (r2 < minRadius2) {
            float f = fixedRadius2 / minRadius2;
            z *= f; dr *= f;
        } else if (r2 < fixedRadius2) {
            float f = fixedRadius2 / r2;
            z *= f; dr *= f;
        }
        z = scale * z + p;
        dr = dr * abs(scale) + 1.0;
    }
    return length(z) / abs(dr);
}
```

## Performance

| Fractal | Iterations | Mobile cost |
|---|---|---|
| 2D Mandelbrot (64 iter) | 64 multiplies + branches | Manageable on mid-tier |
| Julia animated | 64 iter | Same |
| Mandelbulb (8 iter) | 8 × (acos, pow, sin, cos, atan) | Heavy — flagship only |
| Mandelbox (12 iter) | 12 × clamp/scale | OK on mid-tier |

For mobile fractals:
- Cap iterations at 32 (2D) or 6 (3D).
- Avoid zoom > 100× — float precision breaks down anyway.
- Use 2D — 3D is desktop territory.

## Coloring Strategies

```glsl
// Bands
vec3 col = palette(fract(escape * 0.1));

// Smooth + glow
vec3 col = palette(escape * 0.05);
col += vec3(1.0) * pow(escape * 0.02, 4.0);    // hot core glow

// Distance estimate (for distance-estimated fractals)
vec3 col = vec3(1.0 - exp(-d * 50.0));
```

## See Also

- [polar-uv-manipulation](polar-uv-manipulation.md) — Log-polar for infinite zoom.
- [color-palette](color-palette.md) — Coloring the escape values.
- [ray-marching](ray-marching.md) — For 3D fractals.
