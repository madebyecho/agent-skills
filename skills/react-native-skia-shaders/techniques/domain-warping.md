# Domain Warping

Distort the coordinate space *before* evaluating a function. The cheapest
way to make stiff math look organic — turn straight lines into flowing
forms, smooth circles into amoebae, FBM into clouds with structure.

## Basic Pattern

```glsl
// Before: evaluate f at p
vec3 col = vec3(f(p));

// After: warp p first
vec2 q = p + warp(p);
vec3 col = vec3(f(q));
```

The "warp" function is typically itself a low-frequency noise or sin/cos
combination.

## Sin/Cos Warp (Cheapest)

```glsl
vec2 warp(vec2 p, float time) {
    return vec2(
        sin(p.y * 2.0 + time),
        cos(p.x * 2.0 + time * 0.7)
    ) * 0.3;
}
```

Used for: water ripples, plasma-like patterns.

## FBM Warp (Iñigo Quilez)

The classic "warp the noise with another noise" — produces beautiful
cloud/marble effects.

```glsl
float fbm(vec2 p);   // see procedural-noise.md

float pattern(vec2 p, float time) {
    vec2 q = vec2(
        fbm(p + vec2(0.0, 0.0)),
        fbm(p + vec2(5.2, 1.3))
    );
    vec2 r = vec2(
        fbm(p + 4.0 * q + vec2(1.7, 9.2) + time * 0.1),
        fbm(p + 4.0 * q + vec2(8.3, 2.8) + time * 0.13)
    );
    return fbm(p + 4.0 * r);
}
```

Three layers of FBM. Each costs ~5 octaves; total ~15 noise evals per
pixel. **On mobile, drop to 2-layer:**

```glsl
float pattern(vec2 p, float time) {
    vec2 q = vec2(fbm(p + time * 0.1), fbm(p + vec2(5.2, 1.3) + time * 0.13));
    return fbm(p + 3.0 * q);
}
```

That's ~10 evals — still expensive but manageable. Pair with low octave
counts (3) inside each `fbm`.

## Animated Warp (Mesh Gradient)

```glsl
uniform float2 resolution;
uniform float time;

// ... fbm() ...

vec3 palette(float t) {
    return 0.5 + 0.5 * cos(6.28318 * (vec3(1.0) * t + vec3(0.0, 0.33, 0.67)));
}

vec4 main(vec2 pos) {
    vec2 uv = pos / resolution.y;
    vec2 q = vec2(fbm(uv + time * 0.07), fbm(uv + vec2(5.2, 1.3) - time * 0.05));
    float m = fbm(uv + 2.5 * q);
    vec3 col = palette(m * 0.7 + 0.3);
    return vec4(col, 1.0);
}
```

This is the canonical "animated mesh gradient" recipe.

## Warping an SDF

```glsl
float map(vec3 p) {
    p += 0.1 * vec3(sin(p.y * 3.0), sin(p.z * 3.0), sin(p.x * 3.0));
    return sdSphere(p, 0.5);
}
```

Turns a sphere into a wobbly potato. Note: warping an SDF makes it no
longer a *true* distance field. Compensate with a smaller ray-march step
(`t += d * 0.7;`).

## Warping Image Sampling

For distorting an image with `<ImageShader>`:

```glsl
uniform shader image;
uniform float2 resolution;
uniform float time;

vec4 main(vec2 pos) {
    vec2 d = vec2(
        sin(pos.y * 0.04 + time) * 6.0,
        cos(pos.x * 0.04 + time * 0.7) * 6.0
    );
    return image.eval(pos + d);
}
```

Liquid / heat-haze / underwater effects.

## Gesture-Driven Warp

Push the warp toward the touch point:

```glsl
uniform float2 touch;
vec4 main(vec2 pos) {
    vec2 dir = pos - touch;
    float r = length(dir);
    float falloff = exp(-r * 0.01);
    vec2 offset = normalize(dir) * 20.0 * falloff;
    return image.eval(pos + offset);
}
```

Combine with [uniforms-animation](uniforms-animation.md) to drive `touch`
from a `Gesture.Pan`.

## Cost

Each FBM warp layer = O(octaves) noise evaluations. Budget:
- 1 layer FBM warp + 1 base FBM = ~8 evals — fine on mid-tier
- 2 layer FBM warp + 1 base FBM = ~15 evals — flagship only
- 3 layer (IQ classic) = ~20 evals — desktop

Sin/cos warps are 100× cheaper. Use them when "noise quality" doesn't matter.

## See Also

- [procedural-noise](procedural-noise.md) — The FBM you'll warp.
- [color-palette](color-palette.md) — Mapping output to colors.
- [domain-repetition](domain-repetition.md) — A different style of domain manipulation.
- [child-shaders](child-shaders.md) — When warping `<ImageShader>` input.
