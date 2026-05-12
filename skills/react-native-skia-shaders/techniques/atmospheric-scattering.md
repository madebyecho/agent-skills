# Atmospheric Scattering / Sky / Fog

Rayleigh + Mie scattering produces a believable sky and atmosphere. On
mobile, prefer a cheap approximation — full multi-sample integrators are
desktop territory.

## Cheap Procedural Sky

```glsl
vec3 sky(vec3 rd) {
    vec3 horizon = vec3(0.95, 0.65, 0.45);
    vec3 zenith  = vec3(0.20, 0.40, 0.85);
    vec3 nadir   = vec3(0.05, 0.05, 0.08);
    float t = clamp(rd.y, -1.0, 1.0);
    if (t > 0.0) return mix(horizon, zenith, pow(t, 0.5));
    return mix(horizon, nadir, pow(-t, 0.5));
}
```

Use as ray-march miss color: `if (t < 0.0) col = sky(rd);`.

## Sun Disc

```glsl
vec3 sunDir = normalize(vec3(0.7, 0.3, -0.4));
float sunDot = max(dot(rd, sunDir), 0.0);
vec3 sunC = vec3(1.0, 0.95, 0.85);
col += sunC * pow(sunDot, 64.0);            // sharp disc
col += sunC * 0.3 * pow(sunDot, 8.0);       // soft halo
```

## Single-Scatter Rayleigh (Approximate)

```glsl
vec3 rayleighSky(vec3 rd, vec3 sunDir) {
    float cosTheta = dot(rd, sunDir);
    float rayleighPhase = 0.75 * (1.0 + cosTheta * cosTheta);
    float miePhase = (1.0 - 0.7 * 0.7) / pow(1.0 + 0.7 * 0.7 - 2.0 * 0.7 * cosTheta, 1.5);

    float height = max(rd.y + 0.05, 0.0);
    vec3 rayleigh = vec3(0.18, 0.50, 1.0) * 0.6 * exp(-height * 4.0);
    vec3 mie      = vec3(1.0) * 0.05 * miePhase * exp(-height * 1.5);

    vec3 col = rayleigh * rayleighPhase + mie;
    col += vec3(1.0, 0.85, 0.5) * pow(max(cosTheta, 0.0), 64.0) * 0.8;
    return col;
}
```

Tunable. Looks great for clear-sky scenes without an actual scattering
integral.

## Height-Based Fog (Exponential)

```glsl
vec3 applyFog(vec3 col, vec3 ro, vec3 rd, float t) {
    float fogDensity = 0.03;
    float fogAmount = 1.0 - exp(-t * fogDensity);
    vec3 fogColor = vec3(0.6, 0.7, 0.85);
    return mix(col, fogColor, fogAmount);
}
```

For sun-tinted fog (god-rays look):
```glsl
vec3 applyFog(vec3 col, vec3 rd, vec3 sunDir, float t) {
    float fogAmount = 1.0 - exp(-t * 0.03);
    float sunAmount = max(dot(rd, sunDir), 0.0);
    vec3 fogColor = mix(vec3(0.5, 0.6, 0.75),
                        vec3(1.0, 0.9, 0.7),
                        pow(sunAmount, 8.0));
    return mix(col, fogColor, fogAmount);
}
```

## Volumetric Fog (Constant-Step March)

```glsl
vec3 marchFog(vec3 ro, vec3 rd, float maxT, vec3 baseCol) {
    vec3 col = vec3(0.0);
    float trans = 1.0;
    float t = 0.0;
    for (int i = 0; i < 24; i++) {
        if (t > maxT) break;
        vec3 p = ro + t * rd;
        float density = exp(-p.y * 0.5) * 0.04;       // height fog
        col += trans * density * vec3(0.8, 0.9, 1.0);
        trans *= 1.0 - density;
        t += 0.3;
    }
    return baseCol * trans + col;
}
```

24 steps × ~5 ALU = ~120 ALU per pixel. Acceptable on flagship.

## Sunset (Time of Day)

```glsl
uniform float timeOfDay;     // 0..1, 0=sunrise, 0.5=noon, 1=sunset

vec3 sunDir = normalize(vec3(cos(timeOfDay * 3.14), sin(timeOfDay * 3.14), -0.3));
vec3 zenith = mix(vec3(0.05, 0.05, 0.15), vec3(0.2, 0.4, 0.85),
                  smoothstep(0.0, 0.2, sin(timeOfDay * 3.14)));
vec3 horizon = mix(vec3(0.3, 0.15, 0.1), vec3(0.95, 0.7, 0.5),
                   smoothstep(-0.1, 0.3, sin(timeOfDay * 3.14)));
```

## God Rays (Screen-Space Approximation)

```glsl
vec3 godRays(vec2 uv, vec2 sunUv, vec3 base) {
    vec2 dir = sunUv - uv;
    vec3 col = base;
    float dist = length(dir);
    float strength = exp(-dist * 4.0);
    for (int i = 0; i < 16; i++) {
        vec2 sp = uv + dir * float(i) / 16.0;
        // sample backdrop at sp (needs <ImageShader> child)
        // col += image.eval(sp).rgb * strength * 0.05;
    }
    return col;
}
```

Approximates radial blur from the sun — works as a post-process.

## Performance

| Effect | Cost per pixel |
|---|---|
| Procedural sky | ~10 ALU |
| Rayleigh approx | ~30 ALU |
| Exp fog | ~5 ALU |
| Volumetric fog (24 steps) | ~120 ALU |
| God rays (16 samples) | ~250 ALU (16 texture fetches) |

## See Also

- [lighting-model](lighting-model.md) — Direct sun.
- [ray-marching](ray-marching.md) — The scene the sky goes around.
- [post-processing](post-processing.md) — Tone mapping after sky.
