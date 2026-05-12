# Domain Repetition

Tile a shape across space without ever instancing it. Modulo the
coordinates before evaluation. Great for infinite worlds, regular grids,
limited-count patterns.

## Infinite Repetition

```glsl
vec3 opRepeat(vec3 p, vec3 c) {
    return mod(p + 0.5 * c, c) - 0.5 * c;
}

float map(vec3 p) {
    vec3 q = opRepeat(p, vec3(2.0));     // 2-unit grid
    return sdSphere(q, 0.5);
}
```

`c` is the period vector. Repeats in any axis you choose:

```glsl
// Only on X — endless row of objects
vec3 q = p; q.x = mod(p.x + 1.0, 2.0) - 1.0;

// On XZ — floor of tiles
vec3 q = p; q.xz = mod(p.xz + 1.0, 2.0) - 1.0;
```

## 2D Repetition

```glsl
vec2 opRepeat2(vec2 p, vec2 c) {
    return mod(p + 0.5 * c, c) - 0.5 * c;
}
```

## Limited Repetition

Repeat only N times in each direction:

```glsl
vec3 opRepLim(vec3 p, vec3 c, vec3 l) {
    return p - c * clamp(round(p / c), -l, l);
}
```

`l = vec3(3, 0, 3)` → 7×1×7 grid (from -3 to +3 in x and z).

## Mirror Repetition

```glsl
vec3 opMirror(vec3 p, vec3 c) {
    vec3 q = mod(p + 0.5 * c, c) - 0.5 * c;
    // Flip every other cell
    vec3 m = floor(p / c);
    q.x *= (mod(m.x, 2.0) < 1.0) ? 1.0 : -1.0;
    q.z *= (mod(m.z, 2.0) < 1.0) ? 1.0 : -1.0;
    return q;
}
```

Avoids the visible seam in regular repetition.

## Per-Cell Randomization

To vary objects across cells while keeping repetition:

```glsl
float map(vec3 p) {
    vec3 cell = floor(p / 2.0);                  // cell index
    vec3 q = mod(p + 1.0, 2.0) - 1.0;            // local coords
    float r = 0.3 + 0.2 * hash31(cell);          // per-cell radius
    return sdSphere(q, r);
}
```

This is the foundation of [voronoi-cellular-noise](voronoi-cellular-noise.md).

## Folding (Symmetry)

Reflect coords into a half-space — fast way to add mirror symmetry:

```glsl
p.x = abs(p.x);                  // 2-way symmetry on X
p.xz = abs(p.xz);                // 4-way symmetry on XZ
```

For polar kaleidoscope, see [polar-uv-manipulation](polar-uv-manipulation.md).

## Pitfall: Distance Field Validity

`opRepeat` produces a **non-true** SDF — adjacent cells appear correctly but
the true distance can exceed the cell radius. The march might over-step
across cell boundaries. Mitigations:

- Cap the ray-march step: `t += d * 0.8;`
- Ensure the object fits well inside the cell (radius < half period).

For accurate repetition, sample the 3×3×3 neighbors and take the min —
quality, but 27× cost. Usually not worth it.

## Worked Example: Infinite Grid Floor

```glsl
float map(vec3 p) {
    vec3 q = vec3(mod(p.x + 1.0, 2.0) - 1.0, p.y, mod(p.z + 1.0, 2.0) - 1.0);
    float floor = p.y + 1.0;
    float ball = sdSphere(q, 0.4);
    return min(floor, ball);
}
```

A floor with an infinite grid of half-buried spheres.

## See Also

- [sdf-3d](sdf-3d.md) — Primitives.
- [domain-warping](domain-warping.md) — Different kind of coord manipulation.
- [voronoi-cellular-noise](voronoi-cellular-noise.md) — Cell-based noise.
- [polar-uv-manipulation](polar-uv-manipulation.md) — Radial repetition.
