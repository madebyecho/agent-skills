# Ray Marching Reference

Math and advanced patterns for sphere tracing SDF scenes.

## The Algorithm

For a ray `P(t) = ro + t * rd` (where `rd` is unit) and an SDF `f: R³ → R`:

```
t := 0
loop:
    d := f(P(t))
    if |d| < ε:  HIT  → return t
    if  t > tMax: MISS → return -1
    t := t + d
```

The crucial property: `f(p)` returns the distance to the *nearest* surface.
Stepping by `d` along `rd` is **guaranteed** not to overshoot any surface
(if `f` is a true SDF).

## Convergence Bounds

For an infinitely-thin SDF (perfect distance field), the march converges
in finite steps for any point at distance `D` from the surface, taking
roughly `log(D/ε)` steps along straight grazing rays in the worst case.
For typical scene geometry, ~30–80 steps suffices.

If `f` is a *bounded* distance field (smaller than true distance, e.g.
after a smin), the march under-steps. Convergence is still guaranteed but
slower. Mitigate by:
- Multiplying step by a safety factor: `t += d * 0.7;` (under-march)
- Increasing `MAX_STEPS`

If `f` over-estimates distance (a sin/cos warp without compensation), the
march **overshoots** — visible as missing geometry. Cap the warp amplitude.

## Step-Size Variations

```glsl
// Basic
t += d;

// Over-relaxation (Iñigo Quilez) — faster convergence in low-curvature regions
t += d * 1.3;     // step further than safe in regions away from surface
// Requires backtracking when d turns small — adds complexity but ~2x speedup
```

Mobile: stick with `t += d * 1.0` (or `0.7` for warped fields).

## Adaptive Surface Threshold

Sub-pixel SDF precision is wasted when objects are far from the camera —
their projected size is sub-pixel anyway.

```glsl
float pixelSize = 2.0 * t / resolution.y;   // approx world-units per pixel at distance t
if (d < pixelSize * 0.5) return t;          // surface threshold scales with distance
```

This is the basis of free LOD in SDF rendering — surfaces look correct at
any distance without explicit mipmapping.

## Cone Tracing (Soft Surfaces)

Instead of tracking a ray, track a *cone* with growing radius. The "hit"
condition compares cone radius to SDF distance. Used for cheap AO,
occlusion, glossy reflections.

```glsl
float coneTrace(vec3 ro, vec3 rd, float coneAngle) {
    float t = 0.0;
    for (int i = 0; i < 32; i++) {
        float coneR = t * tan(coneAngle);
        float d = map(ro + t * rd);
        if (d < coneR) return 1.0 - clamp(d / coneR, 0.0, 1.0);
        t += d;
    }
    return 0.0;
}
```

## Bounding Volumes

For complex scenes:

```glsl
float map(vec3 p) {
    float boundsTest = length(p - sceneCenter) - sceneRadius;
    if (boundsTest > 0.5) return boundsTest;
    return detailedSDF(p);
}
```

Saves expensive `detailedSDF` evaluations when the ray is far from the
bounded region.

## SDF Sets ("Material IDs")

Return both distance and an integer/float ID:

```glsl
struct H { float d; int id; };

H mapM(vec3 p) {
    H res = H(p.y, 0);
    float dBall = sdSphere(p - vec3(0, 0.5, 0), 0.4);
    if (dBall < res.d) res = H(dBall, 1);
    return res;
}
```

After hit, use `res.id` to look up material color, roughness, etc.

## Numerical Stability

- `SURF_DIST` too small (< 1e-5) → quantization noise, banding.
- `MAX_DIST` too large (> 1000) → wasted iterations in misses.
- Step backoff (`t += d * 0.5`) → halves performance but doubles
  convergence on bad fields.

## Soft Shadow Math

Quilez's soft shadow tracks the minimum SDF-to-ray-distance ratio:

$$ \mathrm{shadow}(p) = \min_t \frac{k \cdot f(p + t \vec{l})}{t} $$

A `min` along the ray of `(k * d / t)` — when this gets close to 0, the
ray is "almost" hitting something nearby, producing penumbra.

The improved version uses the previous step's height `ph` to interpolate
the actual minimum distance between samples (eliminates banding):

$$ y = \frac{h^2}{2 p_h}, \quad d = \sqrt{h^2 - y^2}, \quad \mathrm{res} = \min(\mathrm{res}, k d / (t - y)) $$

See [`../techniques/shadow-techniques.md`](../techniques/shadow-techniques.md).

## Volume Marching (Constant Step)

For fog, smoke, clouds — `f` is now a *density*, not distance. Step at
fixed `dt` and accumulate transmittance:

```glsl
vec4 marchVolume(vec3 ro, vec3 rd, float tMax) {
    vec3 col = vec3(0.0);
    float trans = 1.0;
    float dt = 0.05;
    float t = 0.0;
    for (int i = 0; i < 64; i++) {
        if (t > tMax) break;
        vec3 p = ro + t * rd;
        float density = densityAt(p) * dt;
        col += trans * density * shadeAt(p);
        trans *= 1.0 - density;
        if (trans < 0.01) break;
        t += dt;
    }
    return vec4(col, 1.0 - trans);
}
```

## Self-Intersection Avoidance

After a hit, when re-marching (for shadows / reflections), start `t` from
a small epsilon to avoid immediately self-shadowing:

```glsl
vec3 ro2 = p + n * 0.01;     // step off the surface along the normal
float shadow = softShadow(ro2, l, 0.02, 5.0, 8.0);
```

## Reflection Rays

```glsl
vec3 rRefl = reflect(rd, n);
float t2 = rayMarch(p + n * 0.01, rRefl);
// Recursive sample of the scene at the reflected hit point.
```

Mobile: limit to 1 bounce. Multi-bounce is desktop-only.

## See Also

- [`../techniques/ray-marching.md`](../techniques/ray-marching.md) — Practical recipe.
- [`../techniques/normal-estimation.md`](../techniques/normal-estimation.md).
- [`../techniques/shadow-techniques.md`](../techniques/shadow-techniques.md).
- [Iñigo Quilez Articles](https://iquilezles.org/articles/) — Canonical SDF/ray-march resources.
