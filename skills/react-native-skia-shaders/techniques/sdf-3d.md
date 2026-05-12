# 3D Signed Distance Functions

3D SDFs are the foundation of ray-marched scenes. Like 2D SDFs, `d(p)` is
the signed distance to the surface, but in 3D `p` is `vec3`. Sphere tracing
the SDF gives you a renderable surface without polygons.

For the rendering loop, see [ray-marching](ray-marching.md). This file is
the primitive library + composition.

## SKSL Primitive Library

```glsl
// Sphere
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

// Box (b = half-extents)
float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

// Rounded box
float sdRoundedBox(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b + r;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

// Torus (t.x = major radius, t.y = minor)
float sdTorus(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

// Capped cylinder along Y (h half-height, r radius)
float sdCylinder(vec3 p, float h, float r) {
    vec2 d = abs(vec2(length(p.xz), p.y)) - vec2(r, h);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));
}

// Cone (c = (sin, cos) of half-angle, h = height)
float sdCone(vec3 p, vec2 c, float h) {
    vec2 q = h * vec2(c.x / c.y, -1.0);
    vec2 w = vec2(length(p.xz), p.y);
    vec2 a = w - q * clamp(dot(w, q) / dot(q, q), 0.0, 1.0);
    vec2 b = w - q * vec2(clamp(w.x / q.x, 0.0, 1.0), 1.0);
    float k = sign(q.y);
    float d = min(dot(a, a), dot(b, b));
    float s = max(k * (w.x * q.y - w.y * q.x), k * (w.y - q.y));
    return sqrt(d) * sign(s);
}

// Capsule
float sdCapsule(vec3 p, vec3 a, vec3 b, float r) {
    vec3 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

// Octahedron
float sdOctahedron(vec3 p, float s) {
    p = abs(p);
    return (p.x + p.y + p.z - s) * 0.57735027;
}

// Plane (with normal n, offset h)
float sdPlane(vec3 p, vec3 n, float h) {
    return dot(p, n) + h;
}

// Ground plane (y = 0)
float sdGround(vec3 p) {
    return p.y;
}

// Hex prism
float sdHexPrism(vec3 p, vec2 h) {
    const vec3 k = vec3(-0.8660254, 0.5, 0.57735);
    p = abs(p);
    p.xy -= 2.0 * min(dot(k.xy, p.xy), 0.0) * k.xy;
    vec2 d = vec2(length(p.xy - vec2(clamp(p.x, -k.z * h.x, k.z * h.x), h.x)) * sign(p.y - h.x), p.z - h.y);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));
}

// Triangular prism
float sdTriPrism(vec3 p, vec2 h) {
    vec3 q = abs(p);
    return max(q.z - h.y, max(q.x * 0.866025 + p.y * 0.5, -p.y) - h.x * 0.5);
}
```

## Boolean / Composition

```glsl
float opUnion(float a, float b)        { return min(a, b); }
float opSubtraction(float a, float b)  { return max(a, -b); }
float opIntersection(float a, float b) { return max(a, b); }

// Smooth blends (cubic)
float opSmoothUnion(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}
float opSmoothSubtraction(float a, float b, float k) {
    float h = max(k - abs(a + b), 0.0);
    return max(a, -b) + h * h * 0.25 / k;
}
float opSmoothIntersection(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return max(a, b) + h * h * 0.25 / k;
}
```

See [csg-boolean-operations](csg-boolean-operations.md) for material-aware
smooth blends and exponential / power smin variants.

## Domain Operators

```glsl
// Translate
sdBox(p - vec3(0, 1, 0), vec3(0.5));

// Rotate around Y
mat3 rotY(float a) {
    float c = cos(a), s = sin(a);
    return mat3(c, 0, s,  0, 1, 0,  -s, 0, c);
}

// Scale (must divide d to keep it a true SDF)
float dScaled = sdSphere(p / 2.0, 0.5) * 2.0;

// Mirror (XZ plane)
p.y = abs(p.y);

// Twist around Y
vec3 opTwist(vec3 p, float k) {
    float c = cos(k * p.y), s = sin(k * p.y);
    mat2 m = mat2(c, s, -s, c);
    return vec3(m * p.xz, p.y);
}

// Bend along Y
vec3 opBend(vec3 p, float k) {
    float c = cos(k * p.x), s = sin(k * p.x);
    mat2 m = mat2(c, s, -s, c);
    return vec3(m * p.xy, p.z);
}

// Repeat in 3D (period c)
vec3 opRepeat(vec3 p, vec3 c) {
    return mod(p + 0.5 * c, c) - 0.5 * c;
}

// Limited repeat (l = number of repetitions per axis, but signed)
vec3 opRepLim(vec3 p, vec3 c, vec3 l) {
    return p - c * clamp(round(p / c), -l, l);
}
```

See [domain-repetition](domain-repetition.md) for repetition tricks.

## Scene Definition Pattern

```glsl
float map(vec3 p) {
    float ground = sdGround(p);
    float ball   = sdSphere(p - vec3(0.0, 0.5, 0.0), 0.5);
    float box    = sdRoundedBox(p - vec3(1.2, 0.4, 0.0), vec3(0.3), 0.05);
    float scene  = opUnion(ground, opSmoothUnion(ball, box, 0.25));
    return scene;
}
```

For material IDs, return both distance and ID:

```glsl
vec2 map(vec3 p) {       // .x = distance, .y = material id
    float dGround = sdGround(p);
    float dBall   = sdSphere(p - vec3(0, 0.5, 0), 0.5);
    vec2 res = vec2(dGround, 1.0);
    if (dBall < res.x) res = vec2(dBall, 2.0);
    return res;
}
```

## Animating SDFs

Drive parameters via uniforms:

```glsl
uniform float time;
float map(vec3 p) {
    float r = 0.5 + 0.1 * sin(time * 2.0);
    return sdSphere(p, r);
}
```

For wobbly surfaces, add a noise displacement:

```glsl
float map(vec3 p) {
    float base = sdSphere(p, 0.6);
    float n = 0.05 * sin(8.0 * p.x + time) * sin(8.0 * p.y) * sin(8.0 * p.z);
    return base + n;
}
```

(Note: adding noise/displacement makes `d` no longer a true SDF — it
under-estimates surface distance. To compensate, multiply the step size by
a safety factor < 1 in ray-march, or limit displacement amplitude.)

## Common Shapes Recipe Book

```glsl
// A drinking glass (subtract inner cylinder from outer)
float glass(vec3 p) {
    float outer = sdCylinder(p, 0.5, 0.25);
    float inner = sdCylinder(p - vec3(0, 0.05, 0), 0.45, 0.22);
    return opSubtraction(outer, inner);
}

// A coffee mug = cylinder ∪ torus (handle)
float mug(vec3 p) {
    float body = sdCylinder(p, 0.4, 0.25);
    float hole = sdCylinder(p - vec3(0, 0.1, 0), 0.4, 0.22);
    float cup = opSubtraction(body, hole);
    float handle = sdTorus(p - vec3(0.3, 0, 0), vec2(0.12, 0.04));
    return opSmoothUnion(cup, handle, 0.05);
}

// Boolean operation example: tic-tac shape (a cylinder smooth-unioned with two spheres)
float ticTac(vec3 p) {
    float c = sdCylinder(p, 0.3, 0.18);
    float s1 = sdSphere(p - vec3(0,  0.3, 0), 0.18);
    float s2 = sdSphere(p - vec3(0, -0.3, 0), 0.18);
    return opSmoothUnion(opSmoothUnion(c, s1, 0.05), s2, 0.05);
}
```

## SKSL Mobile Considerations

- Each SDF eval is cheap, but the ray-march evaluates `map(p)` 32–80 times
  per pixel. Keep `map` lean.
- Avoid `mat3` rotations inside `map` if the rotation is camera-constant —
  rotate once outside the loop.
- Combine multiple primitives via `min` rather than separately checking IDs
  in a chain — fewer branches, better GPU divergence.

## See Also

- [ray-marching](ray-marching.md) — The rendering loop that uses these.
- [normal-estimation](normal-estimation.md) — Surface normals from SDF.
- [csg-boolean-operations](csg-boolean-operations.md) — Smooth blends.
- [domain-warping](domain-warping.md) / [domain-repetition](domain-repetition.md) — Distortion.
- Reference: [`reference/sdf-3d.md`](../reference/sdf-3d.md).
