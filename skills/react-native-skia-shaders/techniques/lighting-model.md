# Lighting Models

Translate "scene with a surface and a light" into "color". For SKSL on
mobile, prefer cheap models: **Lambert + half-Lambert + simple Blinn-Phong
specular** covers 90% of cases. PBR-lite when you need realism.

## Inputs

| Variable | Meaning |
|---|---|
| `p` | World position of surface point |
| `n` | Surface normal (unit) |
| `v` | View direction (camera → point or point → camera, by convention) |
| `l` | Light direction (point → light, unit) |
| `albedo` | Base color, gamma-decoded |
| `roughness` | 0 = mirror, 1 = matte |

Make sure all directions are **normalized** and **consistent** (point→cam
or cam→point — pick one and stick to it).

## Lambert (Diffuse)

```glsl
float diff = max(dot(n, l), 0.0);
vec3 col = albedo * diff;
```

Half-Lambert variant (looks better at grazing angles, used by Valve):
```glsl
float diff = dot(n, l) * 0.5 + 0.5;
diff *= diff;
```

## Blinn-Phong (Diffuse + Specular)

```glsl
vec3 h = normalize(l + v);                 // half-vector
float ndh = max(dot(n, h), 0.0);
float spec = pow(ndh, 32.0);               // 32 = shininess, higher = sharper
vec3 col = albedo * diff + vec3(spec);
```

For **mobile**, replace `pow(x, large)` with repeated squaring:
```glsl
float x = ndh;
x = x * x;     // ^2
x = x * x;     // ^4
x = x * x;     // ^8
x = x * x;     // ^16
x = x * x;     // ^32
float spec = x;
```
5 multiplications vs one `pow`. On older Mali GPUs that's ~3× faster.

## Phong (Original — Reflect-based)

```glsl
vec3 r = reflect(-l, n);
float spec = pow(max(dot(r, v), 0.0), 16.0);
```

Blinn-Phong is generally more physically plausible and slightly cheaper.
Prefer it.

## Toon / Cel

```glsl
float diff = max(dot(n, l), 0.0);
float band = floor(diff * 3.0) / 3.0;       // 3 discrete bands
vec3 col = albedo * (0.4 + 0.6 * band);
// Optional rim:
float rim = 1.0 - max(dot(n, v), 0.0);
rim = smoothstep(0.5, 0.7, rim);
col += rim * vec3(1.0, 0.95, 0.8);
```

## PBR-Lite (Cook-Torrance Ish)

For mobile, a stripped-down Cook-Torrance with GGX is fine:

```glsl
float ggx(float ndh, float a) {
    float a2 = a * a;
    float d = ndh * ndh * (a2 - 1.0) + 1.0;
    return a2 / (3.14159 * d * d);
}

float smithG(float ndv, float ndl, float a) {
    float k = (a + 1.0) * (a + 1.0) / 8.0;
    float gv = ndv / (ndv * (1.0 - k) + k);
    float gl = ndl / (ndl * (1.0 - k) + k);
    return gv * gl;
}

vec3 fresnel(float vdh, vec3 f0) {
    return f0 + (1.0 - f0) * pow(1.0 - vdh, 5.0);
}

vec3 pbr(vec3 n, vec3 v, vec3 l, vec3 albedo, float roughness, float metallic) {
    vec3 h = normalize(l + v);
    float ndl = max(dot(n, l), 0.0);
    float ndv = max(dot(n, v), 0.0);
    float ndh = max(dot(n, h), 0.0);
    float vdh = max(dot(v, h), 0.0);
    float a = roughness * roughness;

    vec3 f0 = mix(vec3(0.04), albedo, metallic);
    vec3 F = fresnel(vdh, f0);
    float D = ggx(ndh, a);
    float G = smithG(ndv, ndl, a);

    vec3 spec = (D * G * F) / max(4.0 * ndv * ndl, 0.001);
    vec3 kd = (1.0 - F) * (1.0 - metallic);
    return (kd * albedo / 3.14159 + spec) * ndl;
}
```

Per-pixel cost ~25 ALU ops. Mobile-friendly for a single light.

For environment/ambient with PBR you'd want a prefiltered probe — usually
out of scope on mobile. Approximate with `albedo * (0.3 + 0.7 * n.y)`.

## Three-Light Outdoor Model

A go-to for ray-marched scenes — cheap and looks great:

```glsl
vec3 outdoorLighting(vec3 p, vec3 n, vec3 v, vec3 albedo) {
    vec3 sun = normalize(vec3(0.7, 0.6, -0.3));
    vec3 sky = vec3(0, 1, 0);

    // 1. Sun (warm key)
    float sundot = max(dot(n, sun), 0.0);
    vec3 sunC = vec3(1.0, 0.9, 0.7) * sundot;

    // 2. Sky (cool fill)
    float skydot = max(dot(n, sky), 0.0);
    vec3 skyC = vec3(0.4, 0.6, 0.95) * skydot * 0.4;

    // 3. Bounce (warm reflected from ground)
    vec3 bounce = vec3(0, -1, 0);
    float bdot = max(dot(n, bounce), 0.0);
    vec3 bounceC = vec3(0.6, 0.4, 0.2) * bdot * 0.2;

    return albedo * (sunC + skyC + bounceC);
}
```

Add a [soft shadow](shadow-techniques.md) on `sunC` and [AO](ambient-occlusion.md)
on `skyC + bounceC` for production look.

## Ambient (Cheap)

```glsl
vec3 ambient = albedo * 0.15;                // flat
vec3 ambient = albedo * (0.3 + 0.7 * n.y);   // sky-tinted
```

## Gamma Correction

Always gamma-correct the final color:

```glsl
col = pow(col, vec3(1.0 / 2.2));        // or vec3(0.4545)
```

Without this, dark midtones look crushed. Skia doesn't auto-gamma.

Also, **albedo from JS uniforms is sRGB.** Convert to linear before
lighting math:

```glsl
uniform float3 albedoSrgb;
vec3 albedo = pow(albedoSrgb, vec3(2.2));
// ... lighting ...
col = pow(col, vec3(0.4545));   // back to sRGB for display
```

## Worked Example: Ray-Marched Lit Sphere

```glsl
// Inside main(), after rayMarch finds t > 0:
vec3 p = ro + t * rd;
vec3 n = calcNormal(p);
vec3 v = -rd;
vec3 l = normalize(vec3(0.7, 0.9, -0.4));

float ndl = max(dot(n, l), 0.0);
vec3 h = normalize(l + v);
float ndh = max(dot(n, h), 0.0);
float specP = ndh * ndh; specP *= specP; specP *= specP;     // ^8
float spec = specP * 0.6;

vec3 albedo = vec3(0.85, 0.7, 0.6);
vec3 sky = vec3(0.3, 0.5, 0.7);
vec3 ambient = albedo * (0.3 + 0.7 * n.y) * 0.3;

vec3 col = albedo * ndl + ambient + spec;
col = pow(col, vec3(0.4545));
```

## Performance Notes

- `pow(x, n)` for sharp specular → repeated squaring (5–10× faster on mobile).
- `normalize()` is cheap; `length()` cheaper still — reuse where possible.
- Multiple lights → linear cost, so cap to 1–3.
- Per-pixel matrix inversion is expensive — precompute camera matrices in
  uniforms.
- `pow(x, 0.4545)` (gamma) on final color is fine; doing it per-channel per
  light is wasteful — apply once at end.

## See Also

- [shadow-techniques](shadow-techniques.md) — Soft shadows.
- [ambient-occlusion](ambient-occlusion.md) — Cheap AO.
- [normal-estimation](normal-estimation.md) — Get `n` from SDF.
- [post-processing](post-processing.md) — Tone mapping, bloom.
- Reference: [`reference/lighting-model.md`](../reference/lighting-model.md).
