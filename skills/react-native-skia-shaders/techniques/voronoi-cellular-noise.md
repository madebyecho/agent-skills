# Voronoi / Cellular Noise

Partition space into cells around random seed points; per pixel, find the
distance to the nearest (F1), second-nearest (F2), etc. Foundation of
cracked-earth, organic cell, scales, crystal, and worley textures.

## 2D Voronoi (F1)

```glsl
vec2 hash22(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return fract(sin(p) * 43758.5453);
}

// Returns: x = F1 distance, yz = nearest cell center
vec3 voronoi(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 minPt;
    float minDist = 8.0;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 g = vec2(float(x), float(y));
            vec2 o = hash22(i + g);
            vec2 r = g + o - f;
            float d = dot(r, r);
            if (d < minDist) {
                minDist = d;
                minPt = i + g + o;
            }
        }
    }
    return vec3(sqrt(minDist), minPt);
}
```

9 hashes per pixel. Mobile cost: ~30 ALU ops.

## F1, F2 (Cracked Earth / Edge Detection)

```glsl
vec2 voronoiF1F2(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float f1 = 8.0, f2 = 8.0;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 g = vec2(float(x), float(y));
            vec2 o = hash22(i + g);
            vec2 r = g + o - f;
            float d = dot(r, r);
            if (d < f1) { f2 = f1; f1 = d; }
            else if (d < f2) { f2 = d; }
        }
    }
    return vec2(sqrt(f1), sqrt(f2));
}
```

`F2 - F1` gives edge intensity (crack patterns):
```glsl
vec2 f = voronoiF1F2(uv * 8.0);
vec3 col = vec3(smoothstep(0.0, 0.05, f.y - f.x));   // cracks white
```

## Worley Noise (Cell Distance)

Voronoi F1 is exactly Worley:
```glsl
float worley(vec2 p) { return voronoi(p).x; }
```

Layer multiple frequencies for organic textures:
```glsl
float w = 0.5 * worley(p) + 0.25 * worley(p * 2.0) + 0.125 * worley(p * 4.0);
```

## Animated Voronoi

Move the seed points over time:

```glsl
vec2 hashSeed(vec2 i, float t) {
    vec2 o = hash22(i);
    return 0.5 + 0.5 * sin(t + 6.28 * o);     // each cell orbits its center
}

vec3 voronoiAnim(vec2 p, float t) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float minDist = 8.0;
    vec2 minPt;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 g = vec2(float(x), float(y));
            vec2 o = hashSeed(i + g, t);
            vec2 r = g + o - f;
            float d = dot(r, r);
            if (d < minDist) { minDist = d; minPt = i + g + o; }
        }
    }
    return vec3(sqrt(minDist), minPt);
}
```

Used for organic moving cells, "Spore"-like microbe shaders.

## 3D Voronoi

Same idea, 27 hashes (3³ neighbors). Expensive — use 2D when you can.

```glsl
vec3 hash33(vec3 p) {
    p = vec3(dot(p, vec3(127.1, 311.7, 74.7)),
             dot(p, vec3(269.5, 183.3, 246.1)),
             dot(p, vec3(113.5, 271.9, 124.6)));
    return fract(sin(p) * 43758.5453);
}

float voronoi3D(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    float minDist = 8.0;
    for (int z = -1; z <= 1; z++)
    for (int y = -1; y <= 1; y++)
    for (int x = -1; x <= 1; x++) {
        vec3 g = vec3(float(x), float(y), float(z));
        vec3 o = hash33(i + g);
        vec3 r = g + o - f;
        minDist = min(minDist, dot(r, r));
    }
    return sqrt(minDist);
}
```

## Coloring

Color per cell via cell index:

```glsl
vec3 v = voronoi(uv * 10.0);
vec3 col = 0.5 + 0.5 * cos(6.28 * (v.yz.x * 0.1 + vec3(0.0, 0.33, 0.67)));
```

Each cell gets a stable color derived from its seed.

## Mobile Notes

- 2D Voronoi: 9 hashes per pixel = OK on all tiers.
- 3D Voronoi: 27 hashes = flagship only.
- Layered Worley: triple the cost per layer.

## See Also

- [procedural-noise](procedural-noise.md) — Companion noise types.
- [color-palette](color-palette.md) — Mapping cell IDs to colors.
- [domain-warping](domain-warping.md) — Distorting Voronoi cells.
- [procedural-2d-pattern](procedural-2d-pattern.md) — Crystallized patterns.
