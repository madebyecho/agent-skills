# Normal Estimation

Get a unit surface normal at a point on an SDF surface. Used for lighting
and reflections in ray-marched scenes.

The SDF gradient = surface normal:
$$ \vec{n} = \nabla \, d(p) $$

We approximate it with finite differences.

## Tetrahedral Trick (4 evals — preferred)

```glsl
vec3 calcNormal(vec3 p) {
    const vec2 e = vec2(0.5773, -0.5773) * 0.0005;     // epsilon = 0.0005
    return normalize(
        e.xyy * map(p + e.xyy) +
        e.yyx * map(p + e.yyx) +
        e.yxy * map(p + e.yxy) +
        e.xxx * map(p + e.xxx)
    );
}
```

4 SDF evaluations. Equivalent quality to central differences (6 evals).

## Central Differences (6 evals — most accurate)

```glsl
vec3 calcNormal(vec3 p) {
    const vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}
```

50% more expensive than tetrahedral. Almost never worth it on mobile.

## Forward Differences (3 evals — fastest, lower quality)

```glsl
vec3 calcNormal(vec3 p) {
    float d = map(p);
    const float h = 0.001;
    return normalize(vec3(
        map(p + vec3(h, 0, 0)) - d,
        map(p + vec3(0, h, 0)) - d,
        map(p + vec3(0, 0, h)) - d
    ));
}
```

Cheap, slightly biased (the "normal" leans toward +x/+y/+z). Acceptable
for fast-moving scenes where flicker matters less.

## Choosing Epsilon

Too small → numerical noise (banding, sparkle).
Too large → smoothed normals, faceting on sharp edges.

| Scene scale | Epsilon |
|---|---|
| Closeup (1m objects) | 0.001 |
| Mid (10m room) | 0.005 |
| Far (terrain, 100m+) | 0.01 |

Adaptive: scale by hit distance to handle wide-range scenes.

```glsl
vec3 calcNormal(vec3 p, float t) {
    float eps = max(0.0005, 0.0005 * t / 8.0);   // grows with distance
    const vec2 d = vec2(1.0, -1.0);
    return normalize(
        d.xyy * map(p + d.xyy * eps) +
        d.yyx * map(p + d.yyx * eps) +
        d.yxy * map(p + d.yxy * eps) +
        d.xxx * map(p + d.xxx * eps)
    );
}
```

## Performance

Normal estimation is the second-largest constant cost per pixel after the
ray-march itself (4–6 SDF evaluations). Only compute it on hit, never on
miss.

```glsl
float t = rayMarch(ro, rd);
if (t > 0.0) {
    vec3 p = ro + t * rd;
    vec3 n = calcNormal(p);     // <-- only here
    // ...
}
```

## Bumped / Displaced Normals

If you've added displacement noise to `map`:
```glsl
float map(vec3 p) {
    return sdSphere(p, 0.5) + 0.05 * sin(p.x * 8.0) * sin(p.y * 8.0) * sin(p.z * 8.0);
}
```
The normal will automatically pick up the bumps via finite differences. No
extra work needed.

## Debug: Visualize Normals

```glsl
return vec4(n * 0.5 + 0.5, 1.0);
```

Smooth gradients = correct. Banding/sparkle = epsilon too small. Faceted
look = epsilon too large or SDF discontinuous (often a `max`/`min` cusp
under-resolved).

## See Also

- [ray-marching](ray-marching.md) — Where this is used.
- [sdf-3d](sdf-3d.md) — SDF definitions.
- [lighting-model](lighting-model.md) — Consumes the normal.
