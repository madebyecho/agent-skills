# SDF (3D) Reference

Math behind the primitives, derivation patterns for new shapes, and
correctness invariants.

## SDF Definition

A function `f: Rⁿ → R` is a Signed Distance Function for a surface `S` if:

1. `f(p) = 0` iff `p ∈ S`
2. `f(p) < 0` iff `p` is inside `S`
3. `f(p) > 0` iff `p` is outside `S`
4. `|f(p) - f(q)| ≤ ||p - q||` (Lipschitz with constant 1)

Property 4 is the critical one for sphere tracing: it guarantees stepping
by `f(p)` does not overshoot the surface.

## Constructing New SDFs

### From an implicit equation `g(x, y, z) = 0`

If `g` is smooth, the SDF is approximately:
$$ f(p) \approx \frac{g(p)}{\| \nabla g(p) \|} $$

This is exact for hyperplanes and approximate otherwise (it's the Taylor
linear approximation of distance).

### From a parametric surface

Generally hard — requires numerical root finding. Sphere tracing prefers
implicit / primitive-based SDFs.

### Primitive Library

The canonical primitive set comes from Iñigo Quilez:

```glsl
// Sphere: distance from point to closest point on sphere
float sdSphere(vec3 p, float r) { return length(p) - r; }

// Box: combination of two cases — outside (use closest distance to box's outside) and inside (use signed max).
float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}
```

The `length(max(d, 0))` term handles outside (Euclidean distance from
nearest corner/edge/face). The `min(max(...), 0)` term handles inside
(negative max axis-aligned distance to nearest face).

### Composition Preserves Lipschitz

- `min(f, g)` (union): max Lipschitz constant of the two — still 1.
- `max(f, g)` (intersection): same.
- `max(f, -g)` (subtraction): same — but only if `f` and `g` are properly oriented.
- Smooth blends: introduce a small under-estimate of distance, no longer
  strict SDFs but still useful.

### Translation

```glsl
sdSphere(p - center, r);     // sphere centered at `center`
```

Identical SDF — translation is a rigid motion, preserves distance.

### Rotation

```glsl
sdSphere(rotY(a) * p, r);    // sphere rotated by angle a around Y
```

Rigid motion → preserves SDF property.

### Uniform Scale

```glsl
float dScaled = sdSphere(p / s, r) * s;
```

Must multiply result by `s` to restore Lipschitz constant 1. Without the
multiplication, `t += d` would overshoot when `s > 1`.

### Non-Uniform Scale

Not generally possible — distorts distances. Approximate by under-stepping.

## Smooth Min Derivations

### Quadratic Smin (Polynomial)

$$ \mathrm{smin}_2(a, b, k) = \min(a, b) - \frac{h^2}{4k}, \quad h = \max(k - |a - b|, 0) $$

Continuous, `C¹`. Result no longer a true SDF — undershoots by up to `k/4`.

### Cubic Smin

$$ \mathrm{smin}_3(a, b, k) = \min(a, b) - \frac{h^3 k}{6}, \quad h = \max(k - |a - b|, 0)/k $$

`C²` continuous (smoother gradient). Used in [csg-boolean-operations](../techniques/csg-boolean-operations.md).

### Exponential Smin

$$ \mathrm{smin}_{\exp}(a, b, k) = -\frac{1}{k} \log(e^{-ka} + e^{-kb}) $$

Truly `C^∞`. Slower (two `exp` and one `log`).

## Domain Operators

### Symmetry

```glsl
p.x = abs(p.x);   // 2-way symmetry about YZ plane
```

Operates on input — result is sdShape of half-space mirrored. Preserves
SDF property (the SDF of a symmetric shape).

### Repeat

```glsl
p = mod(p + 0.5*c, c) - 0.5*c;
```

Bounded distance field, not a true SDF — adjacent cells appear correctly,
but far away cells aren't accounted for. Use safety factor on step.

### Twist (Non-Linear)

```glsl
vec3 opTwist(vec3 p, float k) {
    float c = cos(k * p.y), s = sin(k * p.y);
    return vec3(mat2(c, s, -s, c) * p.xz, p.y);
}
```

Distorts space — result is no longer a true SDF. The Lipschitz constant
grows with `k * sceneRadius`. Mitigate with under-step.

## Normal Estimation Theory

The normal at a surface point of `f` is the gradient direction:

$$ \vec{n} = \frac{\nabla f}{\|\nabla f\|} $$

Finite differences:

### Forward (3 evals)

$$ \partial_x f \approx \frac{f(p + (\epsilon, 0, 0)) - f(p)}{\epsilon} $$

Biased — the normal leans toward `+x/+y/+z`.

### Central (6 evals)

$$ \partial_x f \approx \frac{f(p + (\epsilon, 0, 0)) - f(p - (\epsilon, 0, 0))}{2\epsilon} $$

Unbiased, second-order accurate. The 6-eval version of the gradient.

### Tetrahedral (4 evals)

Sample at 4 vertices of a tetrahedron:
$$ \vec{n} = \sum_i \vec{v}_i \cdot f(p + \vec{v}_i \cdot \epsilon) $$

where `v_i` are the tetrahedral directions: `(1,-1,-1)`, `(-1,-1,1)`, `(-1,1,-1)`, `(1,1,1)`. The cross-canceling makes this equivalent to central differences for any twice-differentiable `f`.

Cheaper than central (4 vs 6 evals), same accuracy.

## Material IDs (Extended SDF)

```glsl
struct MapResult { float d; int mat; };

MapResult opUnion(MapResult a, MapResult b) {
    return a.d < b.d ? a : b;
}
```

For smooth-blended materials, interpolate by the smin's `h`:
```glsl
MapResult smin2(MapResult a, MapResult b, float k) {
    float h = max(k - abs(a.d - b.d), 0.0) / k;
    float t = h * h * 0.5;
    return MapResult(
        min(a.d, b.d) - t * k * 0.5,
        a.d < b.d ? a.mat : b.mat    // (or use h to blend a float material id)
    );
}
```

## Performance Patterns

- **Early bounding-volume tests** — wrap detail in a coarse SDF test.
- **Lazy computation** — `if (boundsTest > 0.0) return boundsTest;`
- **Material-deferred shading** — compute distance only in `map`, look up
  material color outside the loop.
- **Avoid `length` when `dot` will do** — `if (length(p) < r)` vs
  `if (dot(p, p) < r*r)`.

## See Also

- [`../techniques/sdf-3d.md`](../techniques/sdf-3d.md) — Primitive code.
- [`../techniques/ray-marching.md`](../techniques/ray-marching.md) — Renders the SDF.
- [`../techniques/csg-boolean-operations.md`](../techniques/csg-boolean-operations.md) — Smooth blends.
- [Iñigo Quilez Distance Functions](https://iquilezles.org/articles/distfunctions/) — Canonical SDF reference.
