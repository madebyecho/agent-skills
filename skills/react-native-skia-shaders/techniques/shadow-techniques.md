# Shadow Techniques

For ray-marched scenes with an SDF, shadows fall out of the same trace —
march from the surface point toward the light and detect occlusion.

## Hard Shadow

```glsl
float hardShadow(vec3 ro, vec3 rd, float maxDist) {
    float t = 0.01;     // small offset to avoid self-shadow
    for (int i = 0; i < 32; i++) {
        float d = map(ro + t * rd);
        if (d < 0.001) return 0.0;       // occluded
        t += d;
        if (t > maxDist) break;
    }
    return 1.0;          // unoccluded
}

// Usage:
vec3 l = normalize(lightPos - p);
float shadow = hardShadow(p + n * 0.01, l, length(lightPos - p));
```

## Soft Shadow (Penumbra Estimate)

Iñigo Quilez's soft shadow — tracks the minimum SDF/t ratio along the ray.
Small `k` = broader penumbra.

```glsl
float softShadow(vec3 ro, vec3 rd, float mint, float maxt, float k) {
    float res = 1.0;
    float t = mint;
    for (int i = 0; i < 32; i++) {
        float d = map(ro + t * rd);
        if (d < 0.001) return 0.0;
        res = min(res, k * d / t);
        t += d;
        if (t > maxt) break;
    }
    return res;
}

// Usage:
float sh = softShadow(p + n * 0.01, l, 0.02, 10.0, 8.0);
```

Tune `k`:
- `k = 2.0` → very soft (point light, large penumbra)
- `k = 8.0` → moderate (typical)
- `k = 32.0` → sharp (directional sun)

## Improved Soft Shadow

Removes banding from the above:

```glsl
float softShadow(vec3 ro, vec3 rd, float mint, float maxt, float k) {
    float res = 1.0;
    float ph = 1e20;
    float t = mint;
    for (int i = 0; i < 32; i++) {
        float h = map(ro + t * rd);
        if (h < 0.001) return 0.0;
        float y = h * h / (2.0 * ph);
        float d = sqrt(h * h - y * y);
        res = min(res, k * d / max(0.0, t - y));
        ph = h;
        t += h;
        if (t > maxt) break;
    }
    return res;
}
```

## Mobile Budget

| Inner-loop steps | Quality | Cost |
|---|---|---|
| 16 | Coarse, banding visible | OK on low-end |
| 24 | Acceptable | Good for mid-tier |
| 32 | Smooth | iOS / flagship |
| 64+ | Diminishing returns | Don't bother on mobile |

Soft shadow is the second-most-expensive thing in a ray-march scene after
the main trace. Halve the steps if you can.

## Applying to Lighting

```glsl
vec3 col = albedo * ndl * shadow + ambient * (0.5 + 0.5 * shadow);
```

Note: include shadow in diffuse, not ambient (or only partial in ambient).
Pure-zero ambient with shadow looks like a void — keep at least 5-10%
ambient even in full shadow.

## Pitfalls

- **Self-shadow acne**: starting `t = 0` makes the SDF immediately register
  as "occluded" because the surface point itself is on the surface. Always
  offset by `p + n * epsilon` or start `t = mint = 0.01`.
- **Light direction wrong way**: `l` should be `surface → light`, not the
  reverse.
- **Shadow over a translucent surface** isn't supported by simple opaque
  shadow trace — see [volumetric](atmospheric-scattering.md) for that.

## See Also

- [lighting-model](lighting-model.md) — How to use the shadow value.
- [ambient-occlusion](ambient-occlusion.md) — Complement to shadows.
- [ray-marching](ray-marching.md) — Main trace.
