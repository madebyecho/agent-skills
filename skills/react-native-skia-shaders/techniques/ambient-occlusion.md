# Ambient Occlusion (SDF-Based)

AO darkens crevices where geometry occludes ambient light. With an SDF you
get it almost free — sample the field at increasing distances along the
normal; if it stays small, the area is enclosed.

## 5-Tap AO (Iñigo Quilez)

```glsl
float calcAO(vec3 p, vec3 n) {
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < 5; i++) {
        float h = 0.01 + 0.12 * float(i) / 4.0;
        float d = map(p + n * h);
        occ += (h - d) * sca;
        sca *= 0.95;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}
```

5 SDF evals per pixel. Smooth, mobile-friendly.

## Cone-Trace AO (Cheaper, More Coarse)

```glsl
float calcAO(vec3 p, vec3 n) {
    float a = 0.0;
    float w = 1.0;
    for (int i = 1; i <= 5; i++) {
        float d = 0.08 * float(i);
        a += w * (d - map(p + n * d));
        w *= 0.5;
    }
    return clamp(1.0 - 8.0 * a, 0.0, 1.0);
}
```

3-Tap (lowest tier):
```glsl
float ao3(vec3 p, vec3 n) {
    float a = (0.04 - map(p + n * 0.04))
            + (0.08 - map(p + n * 0.08)) * 0.5
            + (0.16 - map(p + n * 0.16)) * 0.25;
    return clamp(1.0 - 6.0 * a, 0.0, 1.0);
}
```

## Application

AO multiplies ambient/indirect light, **not** direct sun:

```glsl
vec3 col = albedo * (ndl * shadow + ambient * ao);
```

Mistake to avoid: multiplying direct diffuse by AO darkens lit surfaces
unnaturally. Direct sun should respect *shadow*; AO is for ambient.

## Mobile Budget

| Variant | SDF evals | Use case |
|---|---|---|
| 3-tap | 3 | Low-end Android |
| 5-tap (cone) | 5 | Default |
| 5-tap (IQ) | 5 | Best look |
| 8+ | excessive | Skip |

AO + shadow + normal eval = ~13 SDF evaluations per hit. Combined with a
60-step march, that's ~73 SDF evaluations per hit pixel. Keep `map` lean.

## See Also

- [lighting-model](lighting-model.md) — Consumes AO.
- [shadow-techniques](shadow-techniques.md) — Complement.
- [ray-marching](ray-marching.md) — Surrounding loop.
