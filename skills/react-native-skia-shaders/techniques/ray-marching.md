# Ray Marching (Sphere Tracing)

Render a 3D scene defined by an SDF (`map(p)` → distance to nearest
surface), without polygons. Cast a ray per fragment from the camera and
step along it by the SDF value each iteration.

Mobile budget: 48–80 steps per pixel depending on device tier (see
[mobile-performance](mobile-performance.md)). This is half the ShaderToy
default of 128.

## Use Cases

- Implicit surfaces (organic blobs, smooth-blended geometry).
- Fractals, procedural alien shapes.
- Volumetric clouds / fog (constant-step march, not sphere trace).
- Distance-field lighting (soft shadows, AO).
- Anything where polygon-modeling would be a pain.

## SKSL Template

```glsl
uniform float2 resolution;
uniform float time;

#define MAX_STEPS 64
#define MAX_DIST  20.0
#define SURF_DIST 0.001

// --- SDF library: see sdf-3d.md ---
float sdSphere(vec3 p, float r) { return length(p) - r; }
float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

float map(vec3 p) {
    float ground = p.y;
    float ball   = sdSphere(p - vec3(0, 0.6, 0), 0.5);
    return min(ground, ball);
}

vec3 calcNormal(vec3 p) {
    const vec2 e = vec2(0.5773, -0.5773) * 0.0005;
    return normalize(
        e.xyy * map(p + e.xyy) +
        e.yyx * map(p + e.yyx) +
        e.yxy * map(p + e.yxy) +
        e.xxx * map(p + e.xxx)
    );
}

float rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + t * rd;
        float d = map(p);
        if (d < SURF_DIST) return t;
        t += d;
        if (t > MAX_DIST) break;
    }
    return -1.0;
}

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    vec3 ro = vec3(0.0, 1.2, -3.0);
    vec3 ta = vec3(0.0, 0.6,  0.0);

    // Camera basis
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(0.0, 1.0, 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = cross(cu, cw);
    vec3 rd = normalize(uv.x * cu + uv.y * cv + 1.5 * cw);

    float t = rayMarch(ro, rd);
    vec3 col = vec3(0.45, 0.55, 0.7) - 0.3 * rd.y;   // sky
    if (t > 0.0) {
        vec3 p = ro + t * rd;
        vec3 n = calcNormal(p);
        vec3 lig = normalize(vec3(0.7, 0.8, -0.4));
        float dif = clamp(dot(n, lig), 0.0, 1.0);
        float amb = 0.4 + 0.6 * n.y;
        col = vec3(0.85, 0.7, 0.6) * (0.3 * amb + dif);
    }
    col = pow(col, vec3(0.4545));    // gamma
    return vec4(col, 1.0);
}
```

## Step-by-Step

### 1. UV and aspect

```glsl
vec2 uv = (2.0 * pos - resolution) / resolution.y;
// x ∈ [-aspect, +aspect], y ∈ [-1, +1]
```

### 2. Camera ray direction

```glsl
// Hard-coded camera
vec3 ro = vec3(0.0, 1.0, -3.0);
vec3 rd = normalize(vec3(uv, 1.5));     // 1.5 ≈ ~60° FOV

// Look-at camera (more flexible)
mat3 setCamera(vec3 ro, vec3 ta, float roll) {
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(sin(roll), cos(roll), 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = cross(cu, cw);
    return mat3(cu, cv, cw);
}
mat3 ca = setCamera(ro, ta, 0.0);
vec3 rd = ca * normalize(vec3(uv, 1.5));
```

### 3. The march loop

```glsl
float rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        float d = map(ro + t * rd);
        if (d < SURF_DIST) return t;
        t += d;
        if (t > MAX_DIST) break;
    }
    return -1.0;
}
```

Step size = `d` (the SDF value) ensures no surface is overshot.

### 4. Normal via tetrahedral trick (4 SDF evals)

```glsl
vec3 calcNormal(vec3 p) {
    const vec2 e = vec2(0.5773, -0.5773) * 0.0005;
    return normalize(
        e.xyy * map(p + e.xyy) +
        e.yyx * map(p + e.yyx) +
        e.yxy * map(p + e.yxy) +
        e.xxx * map(p + e.xxx)
    );
}
```

See [normal-estimation](normal-estimation.md) for the central-differences
variant (6 evals) and quality tradeoffs.

### 5. Shade

```glsl
vec3 lig = normalize(vec3(0.7, 0.9, -0.4));
float dif = clamp(dot(n, lig), 0.0, 1.0);
vec3 col = baseColor * dif;
```

For better looks: add ambient (`0.3 + 0.7 * n.y`), specular (`pow(max(dot(reflect(-lig,n), -rd), 0.0), 32.0)`), soft shadows, AO. See [lighting-model](lighting-model.md), [shadow-techniques](shadow-techniques.md), [ambient-occlusion](ambient-occlusion.md).

## Performance Tuning (mobile)

| Knob | Effect | Suggested |
|---|---|---|
| `MAX_STEPS` | Trace iterations | 48 (Android mid) – 80 (iOS) |
| `MAX_DIST` | Far plane | 10–30 (no further than scene extent) |
| `SURF_DIST` | Hit threshold | 0.001 – 0.005 (larger = more banding but faster) |
| Step-size factor | `t += d * 0.7;` (under-step) | Use when `map` isn't a strict SDF (displaced/warped) |
| Far LOD | Larger `SURF_DIST` when `t` is large | Adaptive surface |

Adaptive surface threshold (cheap LOD):
```glsl
if (d < SURF_DIST * (1.0 + t * 0.1)) return t;
```

## Worked Example: Floating Blob Scene

```glsl
uniform float2 resolution;
uniform float time;

#define MAX_STEPS 60
#define MAX_DIST  20.0
#define SURF_DIST 0.002

float sdSphere(vec3 p, float r) { return length(p) - r; }

float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}

float map(vec3 p) {
    float t = time * 0.7;
    float s1 = sdSphere(p - vec3( cos(t)*0.5,  0.5+0.2*sin(t),  0.0), 0.35);
    float s2 = sdSphere(p - vec3(-cos(t)*0.5,  0.5+0.2*cos(t),  0.0), 0.30);
    float s3 = sdSphere(p - vec3( sin(t*1.3)*0.2,  0.3, sin(t)*0.4), 0.25);
    float blob = smin(smin(s1, s2, 0.3), s3, 0.3);
    float ground = p.y + 0.4;
    return min(blob, ground);
}

vec3 calcNormal(vec3 p) {
    const vec2 e = vec2(0.5773, -0.5773) * 0.0005;
    return normalize(
        e.xyy * map(p + e.xyy) +
        e.yyx * map(p + e.yyx) +
        e.yxy * map(p + e.yxy) +
        e.xxx * map(p + e.xxx)
    );
}

float rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        float d = map(ro + t * rd);
        if (d < SURF_DIST) return t;
        t += d;
        if (t > MAX_DIST) break;
    }
    return -1.0;
}

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    vec3 ro = vec3(0.0, 1.0, -2.5);
    vec3 ta = vec3(0.0, 0.4,  0.0);
    vec3 cw = normalize(ta - ro);
    vec3 cu = normalize(cross(cw, vec3(0, 1, 0)));
    vec3 cv = cross(cu, cw);
    vec3 rd = normalize(uv.x * cu + uv.y * cv + 1.6 * cw);

    vec3 col = vec3(0.6, 0.8, 1.0) - 0.4 * rd.y;
    float t = rayMarch(ro, rd);
    if (t > 0.0) {
        vec3 p = ro + t * rd;
        vec3 n = calcNormal(p);
        vec3 L = normalize(vec3(0.7, 0.9, -0.5));
        float dif = clamp(dot(n, L), 0.0, 1.0);
        float amb = 0.4 + 0.6 * n.y;
        vec3 base = mix(vec3(0.95, 0.6, 0.4), vec3(0.4, 0.7, 0.95), p.y);
        col = base * (0.2 * amb + dif);
    }
    col = pow(col, vec3(0.4545));
    return vec4(col, 1.0);
}
```

## Debug Visualizations

Drop these into `main` to diagnose:

```glsl
// 1) Step count heatmap
int hits = 0;
float t = 0.0;
for (int i = 0; i < MAX_STEPS; i++) {
    float d = map(ro + t * rd);
    hits = i;
    if (d < SURF_DIST) break;
    t += d;
    if (t > MAX_DIST) break;
}
return vec4(vec3(float(hits) / float(MAX_STEPS)), 1.0);

// 2) Hit distance
return vec4(vec3(t / MAX_DIST), 1.0);

// 3) Normals
return vec4(n * 0.5 + 0.5, 1.0);

// 4) Just sky
return vec4(vec3(0.6, 0.8, 1.0) - 0.4 * rd.y, 1.0);
```

## See Also

- [sdf-3d](sdf-3d.md) — Primitive library and composition.
- [normal-estimation](normal-estimation.md) — Tetrahedral vs central differences.
- [lighting-model](lighting-model.md) — Phong, Blinn-Phong, PBR-lite.
- [shadow-techniques](shadow-techniques.md) — Soft shadows.
- [ambient-occlusion](ambient-occlusion.md) — SDF AO.
- [matrix-transform](matrix-transform.md) — Look-at math.
- Reference: [`reference/ray-marching.md`](../reference/ray-marching.md).
