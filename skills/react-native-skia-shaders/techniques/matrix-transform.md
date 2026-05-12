# Matrix Transforms

Camera, rotation, projection. For ray-marched scenes you need a look-at
camera; for 2D shaders, rotation matrices are common.

## 2D Rotation

```glsl
mat2 rot2(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c);
}

// Usage
p = rot2(0.4) * p;
```

## 3D Rotation Matrices

```glsl
mat3 rotX(float a) {
    float c = cos(a), s = sin(a);
    return mat3(1, 0, 0,  0, c, -s,  0, s, c);
}
mat3 rotY(float a) {
    float c = cos(a), s = sin(a);
    return mat3(c, 0, s,  0, 1, 0,  -s, 0, c);
}
mat3 rotZ(float a) {
    float c = cos(a), s = sin(a);
    return mat3(c, -s, 0,  s, c, 0,  0, 0, 1);
}
```

## Look-At Camera (For Ray Marching)

```glsl
mat3 setCamera(vec3 ro, vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);                // forward (camera → target)
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);       // roll
    vec3 cu = normalize(cross(cw, cp));          // right
    vec3 cv = cross(cu, cw);                     // up
    return mat3(cu, cv, cw);
}
```

Usage:
```glsl
vec3 ro = vec3(2.0, 1.5, -3.0);                  // camera position
vec3 ta = vec3(0.0, 0.5,  0.0);                  // target
mat3 ca = setCamera(ro, ta, 0.0);
vec2 uv = (2.0 * pos - resolution) / resolution.y;
vec3 rd = ca * normalize(vec3(uv, focalLength)); // focalLength ~1.5-2.5
```

`focalLength` = 1 → ~90° FOV. 2 → ~53°. 3 → ~37° (telephoto).

## FOV Control

If you want degrees:
```glsl
float focal = 1.0 / tan(radians(fovDegrees) * 0.5);
```

## Orbit Camera (Time/Touch Driven)

```glsl
uniform float yaw;        // 0..2π
uniform float pitch;      // -π/2..π/2
uniform float distance;

vec3 ro = vec3(
    distance * cos(pitch) * sin(yaw),
    distance * sin(pitch),
    distance * cos(pitch) * cos(yaw)
);
vec3 ta = vec3(0.0);
mat3 ca = setCamera(ro, ta, 0.0);
```

Drive `yaw`/`pitch` from a `Gesture.Pan` on the JS side.

## Projection (3D Position → 2D Screen)

Rarely needed in shader-only code (ray-marching skips the projection
matrix), but if you have explicit world positions to project:

```glsl
vec2 projectToScreen(vec3 world, vec3 ro, mat3 ca, float focal, vec2 res) {
    vec3 v = transpose(ca) * (world - ro);     // view space
    return res * 0.5 + vec2(v.x / v.z, v.y / v.z) * focal * res.y * 0.5;
}
```

## Quaternion Rotation (Stable Compositions)

For complex compositions of rotations without gimbal lock:

```glsl
vec3 rotateByQuat(vec3 v, vec4 q) {
    return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}

vec4 quatFromAxisAngle(vec3 axis, float a) {
    float s = sin(a * 0.5);
    return vec4(axis * s, cos(a * 0.5));
}
```

## Performance

- **Compute matrices once per frame, not per pixel.** Pass them as uniforms
  if camera doesn't move per-pixel.
- A `mat3 * vec3` is 9 multiplies + 6 adds — cheap.
- `mat3` rotation chains (`rotY * rotX * rotZ`) collapse mathematically;
  precompute on JS side and pass as a `float3x3` uniform.

## Worked Example: Auto-Orbiting Scene

```glsl
uniform float time;
uniform float2 resolution;

mat3 setCamera(vec3 ro, vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = cross(cu, cw);
    return mat3(cu, cv, cw);
}

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    float yaw = time * 0.3;
    vec3 ro = vec3(3.0 * sin(yaw), 1.5, 3.0 * cos(yaw));
    vec3 ta = vec3(0.0, 0.5, 0.0);
    mat3 ca = setCamera(ro, ta, 0.0);
    vec3 rd = ca * normalize(vec3(uv, 1.8));
    // ... rayMarch(ro, rd) ...
    return vec4(rd * 0.5 + 0.5, 1.0);
}
```

## See Also

- [ray-marching](ray-marching.md) — Main consumer.
- [uniforms-animation](uniforms-animation.md) — Animating yaw/pitch.
- [polar-uv-manipulation](polar-uv-manipulation.md) — 2D coord transforms.
