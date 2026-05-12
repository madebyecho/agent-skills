# Stateless Particle Systems

True particle systems need state across frames. react-native-skia shaders
are pure functions of pixel position — no easy frame-to-frame state. So we
implement **stateless** particles: each particle is a deterministic
function of `(particleId, time)`. Looks similar, no buffers needed.

## Pattern

For each fragment, loop over all particles, compute current position by
formula, accumulate contribution.

```glsl
float hash(float n) { return fract(sin(n) * 43758.5453); }

vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    vec3 col = vec3(0.0);
    const int N = 60;
    for (int i = 0; i < N; i++) {
        float id = float(i);
        float seed = hash(id);
        // Particle orbit
        float lifeSeed = hash(id + 1.0);
        float life = fract(time * 0.3 + lifeSeed);
        vec2 origin = vec2(hash(id + 2.0), hash(id + 3.0));
        vec2 vel = (vec2(hash(id + 4.0), hash(id + 5.0)) - 0.5) * 0.3;
        vec2 p = origin + vel * life;
        float r = 0.005 * (1.0 - life);
        float d = distance(uv, p);
        col += vec3(1.0, 0.7, 0.4) * smoothstep(r, 0.0, d) * (1.0 - life);
    }
    return vec4(col, 1.0);
}
```

`N = 60` particles per pixel × full screen = 60 × ~2M = 120M particle evals
per frame. Each is a few ALU ops, so on mobile this is roughly ~600M ALU =
heavy. Cap `N` to 32 on Android, 60 on iOS.

## Examples

### Stars / Sparkles

```glsl
float stars(vec2 p) {
    vec3 col = vec3(0.0);
    for (int i = 0; i < 30; i++) {
        float seed = float(i);
        vec2 sp = vec2(hash(seed), hash(seed + 0.1));
        float twinkle = 0.5 + 0.5 * sin(time * 3.0 + seed * 6.28);
        col += vec3(1.0) * twinkle * smoothstep(0.002, 0.0, distance(p, sp));
    }
    return col;
}
```

### Falling Rain

```glsl
for (int i = 0; i < 50; i++) {
    float id = float(i);
    float x = fract(hash(id) + time * 0.02 * hash(id + 1.0));
    float y = fract(-time * (0.5 + 0.5 * hash(id + 2.0)) + hash(id + 3.0));
    vec2 p = vec2(x, y);
    col += vec3(0.7, 0.85, 1.0) * smoothstep(0.0, 0.001, 0.005 - abs(uv.x - p.x)) * step(y, uv.y) * step(uv.y, y + 0.04);
}
```

### Fire Sparks

```glsl
for (int i = 0; i < 40; i++) {
    float id = float(i);
    float life = fract(time * 0.6 + hash(id));
    vec2 origin = vec2(0.5 + 0.1 * (hash(id + 1.0) - 0.5), 0.2);
    vec2 vel = vec2((hash(id + 2.0) - 0.5) * 0.4, 1.5);
    vec2 p = origin + vel * life;
    p.x += 0.05 * sin(life * 12.0 + id);     // wobble
    float fade = (1.0 - life);
    float r = 0.008 * fade;
    col += vec3(1.0, 0.6, 0.2) * smoothstep(r, 0.0, distance(uv, p)) * fade;
}
```

### Galaxy Spiral

```glsl
for (int i = 0; i < 200; i++) {
    float id = float(i);
    float r = hash(id);                    // radius 0..1
    float a = hash(id + 1.0) * 6.28 + r * 6.0 + time * 0.05;  // spiral
    vec2 p = vec2(0.5) + r * 0.4 * vec2(cos(a), sin(a));
    vec3 c = mix(vec3(1.0, 0.7, 0.4), vec3(0.4, 0.6, 1.0), r);
    col += c * smoothstep(0.003, 0.0, distance(uv, p)) * (1.0 - r);
}
```

## Mobile Budget

Particles are O(N) per pixel. Tier guidance:
- iOS flagship: 60-120 particles
- Mid-tier Android: 32-50
- Low-end: 16-24

Pre-pass: render to a smaller `<Canvas>` (0.5× scale) and let the display upscale.

## Bouncing / Containment

```glsl
vec2 p = origin + vel * life;
p = abs(fract(p * 0.5) - 0.5) * 2.0;   // ping-pong within 0..1
```

## See Also

- [procedural-noise](procedural-noise.md) — Driving particle velocities.
- [color-palette](color-palette.md) — Color over life.
- [uniforms-animation](uniforms-animation.md) — Driving the time uniform.
