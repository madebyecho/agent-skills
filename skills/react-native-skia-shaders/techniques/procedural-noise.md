# Procedural Noise

Hash-based pseudo-random functions and their smoothed variants. The
building blocks of everything procedural — terrain, clouds, fluids,
displacement, mesh gradients, particle distributions.

Mobile budget: 3–5 FBM octaves max ([mobile-performance](mobile-performance.md)).

## Hashes

```glsl
// 1D → 1D
float hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

// 2D → 1D
float hash21(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// 3D → 1D
float hash31(vec3 p) {
    return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

// 2D → 2D
vec2 hash22(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453);
}

// 3D → 3D
vec3 hash33(vec3 p) {
    p = vec3(dot(p, vec3(127.1, 311.7, 74.7)),
             dot(p, vec3(269.5, 183.3, 246.1)),
             dot(p, vec3(113.5, 271.9, 124.6)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453);
}
```

**Tradeoff:** `sin(dot(...))` hashes are cheap but produce visible patterns
on large scales (esp. on mobile GPUs with lower-precision `sin`). For
seamless tiling and quality, prefer integer-bit-mix hashes:

```glsl
// PCG-style int hash — higher quality, slightly more expensive
uint pcg(uint v) {
    uint state = v * 747796405u + 2891336453u;
    uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}
```

(SKSL accepts `uint` since Skia 0.9.x; check your version.)

## Value Noise

Bilinear interpolation between grid corner hashes. Cheap but blocky.

```glsl
float valueNoise2D(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);     // smoothstep
    return mix(
        mix(hash21(i + vec2(0,0)), hash21(i + vec2(1,0)), u.x),
        mix(hash21(i + vec2(0,1)), hash21(i + vec2(1,1)), u.x),
        u.y);
}
```

## Perlin Noise (Gradient)

Gradient noise — smoother than value noise. Slightly more expensive.

```glsl
float perlin2D(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(dot(hash22(i + vec2(0,0)), f - vec2(0,0)),
            dot(hash22(i + vec2(1,0)), f - vec2(1,0)), u.x),
        mix(dot(hash22(i + vec2(0,1)), f - vec2(0,1)),
            dot(hash22(i + vec2(1,1)), f - vec2(1,1)), u.x),
        u.y);
}
```

3D Perlin (used for volumetric noise, displacement):

```glsl
float perlin3D(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    vec3 u = f * f * (3.0 - 2.0 * f);

    return mix(mix(mix(dot(hash33(i + vec3(0,0,0)), f - vec3(0,0,0)),
                       dot(hash33(i + vec3(1,0,0)), f - vec3(1,0,0)), u.x),
                   mix(dot(hash33(i + vec3(0,1,0)), f - vec3(0,1,0)),
                       dot(hash33(i + vec3(1,1,0)), f - vec3(1,1,0)), u.x), u.y),
               mix(mix(dot(hash33(i + vec3(0,0,1)), f - vec3(0,0,1)),
                       dot(hash33(i + vec3(1,0,1)), f - vec3(1,0,1)), u.x),
                   mix(dot(hash33(i + vec3(0,1,1)), f - vec3(0,1,1)),
                       dot(hash33(i + vec3(1,1,1)), f - vec3(1,1,1)), u.x), u.y),
               u.z);
}
```

## Simplex Noise

Higher quality, fewer artifacts than Perlin at the cost of more math.
On mobile, prefer simplex for terrain (avoids grid alignment), Perlin for
quick displacement.

```glsl
// 2D simplex by Ashima — public domain
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 permute(vec3 x) { return mod289(((x * 34.0) + 1.0) * x); }

float simplex2D(vec2 v) {
    const vec4 C = vec4(0.211324865, 0.366025404, -0.577350269, 0.024390244);
    vec2 i  = floor(v + dot(v, C.yy));
    vec2 x0 = v - i + dot(i, C.xx);
    vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod289(i);
    vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
    vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
    m = m * m; m = m * m;
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291 - 0.85373472 * (a0 * a0 + h * h);
    vec3 g;
    g.x  = a0.x * x0.x   + h.x  * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
}
```

## Fractal Brownian Motion (FBM)

Sum octaves of noise at doubling frequency, halving amplitude. The standard
recipe for "natural-looking" textures.

```glsl
float fbm(vec2 p) {
    float v = 0.0;
    float amp = 0.5;
    float freq = 1.0;
    for (int i = 0; i < 5; i++) {   // 5 octaves
        v += amp * perlin2D(p * freq);
        freq *= 2.0;
        amp  *= 0.5;
    }
    return v;
}
```

### Octave count budget

| Octaves | Use case | Cost ratio |
|---|---|---|
| 2 | Quick mesh-gradient warp | 1× |
| 3 | Mid-tier mobile FBM | 1.5× |
| 4 | Decent terrain / clouds | 2× |
| 5 | iOS flagship terrain | 2.5× |
| 6 | Desktop only | 3× |

Each extra octave doubles the inner-loop hash cost; mobile cliffs hard
around octave 5.

### Ridged Noise

```glsl
float ridged(vec2 p) {
    return 1.0 - abs(perlin2D(p));
}

float ridgedFbm(vec2 p) {
    float v = 0.0, amp = 0.5;
    for (int i = 0; i < 5; i++) {
        v += amp * (1.0 - abs(perlin2D(p)));
        p *= 2.0; amp *= 0.5;
    }
    return v;
}
```

Used for mountains, lightning, fluid-vein patterns.

### Turbulence

```glsl
float turbulence(vec2 p) {
    float v = 0.0, amp = 1.0;
    for (int i = 0; i < 5; i++) {
        v += amp * abs(perlin2D(p));
        p *= 2.0; amp *= 0.5;
    }
    return v;
}
```

Sharper, "billowy" — clouds, smoke.

## Animating Noise

```glsl
// 3D noise sampled along time axis — smooth, no looping
float n = perlin3D(vec3(p * 2.0, time * 0.3));

// 2D noise + scrolling — cheaper but obvious direction
float n = fbm(p + vec2(time * 0.1, 0.0));

// Looping 4D noise via cos/sin trick (perlin4D needed, expensive on mobile)
// Use sparingly.
```

## Worked Example: Mesh-Gradient Background

```glsl
uniform float2 resolution;
uniform float time;

float hash21(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec2  hash22(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453);
}
float perlin2D(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(dot(hash22(i + vec2(0,0)), f - vec2(0,0)),
            dot(hash22(i + vec2(1,0)), f - vec2(1,0)), u.x),
        mix(dot(hash22(i + vec2(0,1)), f - vec2(0,1)),
            dot(hash22(i + vec2(1,1)), f - vec2(1,1)), u.x),
        u.y);
}
float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) { v += a * perlin2D(p); p *= 2.0; a *= 0.5; }
    return v;
}

vec3 palette(float t) {
    return 0.5 + 0.5 * cos(6.2831 * (vec3(1.0) * t + vec3(0.0, 0.33, 0.67)));
}

vec4 main(vec2 pos) {
    vec2 uv = pos / resolution.y * 1.5;
    float n = fbm(uv + vec2(time * 0.07, time * 0.04));
    float m = fbm(uv * 1.7 + vec2(-time * 0.05, time * 0.03) + n);   // domain-warped
    vec3 col = palette(m * 0.7 + 0.3);
    return vec4(col, 1.0);
}
```

## Pitfalls on Mobile

- **`fract(sin(...))` hashes alias** at high coords (large `time` * many
  multiplications). If you see plaid patterns at scale, switch to
  PCG or hash13/hash22 variants.
- **5+ octaves stutter on Android.** Cap to 3–4 and add domain warping for
  richer look at half the cost.
- **3D noise** is 2× the cost of 2D — only use when the third axis (time
  or depth) needs continuity.
- **`mod289` / Ashima simplex**: works fine in SKSL but the macro-free
  rewrite is verbose. Inline once, reuse.

## See Also

- [domain-warping](domain-warping.md) — Use noise to distort other math.
- [color-palette](color-palette.md) — Mapping noise to colors.
- [voronoi-cellular-noise](voronoi-cellular-noise.md) — Cellular noise variant.
- [terrain-rendering](atmospheric-scattering.md) — FBM for height fields.
- Reference: [`reference/procedural-noise.md`](../reference/procedural-noise.md).
