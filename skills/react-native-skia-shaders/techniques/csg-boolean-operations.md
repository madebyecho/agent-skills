# CSG Boolean Operations

Combining SDFs to make complex shapes. The core operations are `min` /
`max` / negation; the interesting variants smoothly blend the seams.

## Hard Operations

```glsl
float opUnion(float a, float b)        { return min(a, b); }
float opSubtraction(float a, float b)  { return max(a, -b); }    // a minus b
float opIntersection(float a, float b) { return max(a, b); }
```

Hard ops produce a sharp seam at the boundary — correct SDFs, but visually
"glued together". Smooth variants make organic blends.

## Smooth Operations (Cubic Polynomial)

```glsl
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0) / k;
    return min(a, b) - h * h * h * k * (1.0 / 6.0);
}

// Backwards-compatible quadratic version (often used in literature):
float sminQ(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}

float ssub(float a, float b, float k) {
    float h = max(k - abs(a + b), 0.0);
    return max(a, -b) + h * h * 0.25 / k;
}

float sintersect(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return max(a, b) + h * h * 0.25 / k;
}
```

`k` is the **blend radius** — larger = wider blend. Typical: 0.05 – 0.3 in
world units.

## Power smin (Sharp Control)

```glsl
float sminPow(float a, float b, float k) {
    a = pow(a, k); b = pow(b, k);
    return pow((a * b) / (a + b), 1.0 / k);
}
```

Requires positive distances — only works *outside* the surface. Use the
polynomial smin for interior.

## Exponential smin

```glsl
float sminExp(float a, float b, float k) {
    float r = exp(-k * a) + exp(-k * b);
    return -log(r) / k;
}
```

Computationally heavier but produces a particularly nice gradient. Good for
material blends.

## Material-Aware smin

To know which input "won" (for material assignment):

```glsl
vec2 smin2(vec2 a, vec2 b, float k) {     // .x = distance, .y = material id
    float h = max(k - abs(a.x - b.x), 0.0) / k;
    float t = h * h * h * 0.5;
    return vec2(
        min(a.x, b.x) - t * k * (1.0 / 3.0),
        (a.x < b.x) ? mix(a.y, b.y, t) : mix(b.y, a.y, t)
    );
}
```

## Combining 3+ Shapes

`smin` is associative-ish — left-fold:

```glsl
float d = smin(smin(smin(a, b, 0.2), c, 0.2), d, 0.2);
```

For very organic blobs, all-pairs smin in a loop:

```glsl
float blob(vec3 p, vec3 centers[N], float r, float k) {
    float d = sdSphere(p - centers[0], r);
    for (int i = 1; i < N; i++) {
        d = smin(d, sdSphere(p - centers[i], r), k);
    }
    return d;
}
```

(SKSL doesn't support arrays as parameters in all versions; if so, unroll
manually or use uniform arrays.)

## Visual Reference

| Operation | Visual effect |
|---|---|
| `min(a, b)` | Hard union with a crease |
| `smin(a, b, k)` | Smooth blob, k controls gulp |
| `max(a, -b)` | Hard hole in a |
| `ssub(a, b, k)` | Smooth indentation |
| `max(a, b)` | Hard intersection (lens) |
| `sintersect(a, b, k)` | Smooth lens |

## Picking k

| k (world units) | Effect |
|---|---|
| 0.02 | Subtle softness on seams |
| 0.1 | Visible blob "neck" |
| 0.3 | Heavy blending, blob-like |
| 0.5+ | Surfaces lose definition |

Animate `k` over time for a "morphing creature":
```glsl
float k = 0.1 + 0.15 * (0.5 + 0.5 * sin(time));
```

## Pitfall: Blends ≠ True SDFs

Smooth blends slightly under-estimate distance — the result is a *bounded*
distance field, not a true SDF. For most ray-marching this is fine, but
near very thin features the march can overstep. Mitigations:

- Reduce ray-march step size: `t += d * 0.7;`
- Or cap `k` to ≤ 0.3.

## See Also

- [sdf-3d](sdf-3d.md) — Primitives.
- [sdf-2d](sdf-2d.md) — Same ops in 2D.
- [sdf-tricks](sdf-tricks.md) — More compositions.
- [ray-marching](ray-marching.md) — Renders the result.
