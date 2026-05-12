# Procedural 2D Patterns

Tiled, mathematically-defined 2D motifs. Useful for backgrounds, fabric,
ornamental UI, abstract art.

## Checker

```glsl
float checker(vec2 p, float s) {
    vec2 c = floor(p * s);
    return mod(c.x + c.y, 2.0);
}
```

## Stripes

```glsl
float stripes(vec2 p, float freq, float angle) {
    float c = cos(angle), s = sin(angle);
    float u = c * p.x - s * p.y;
    return step(0.5, fract(u * freq));
}
```

## Diamond / Cross

```glsl
float diamond(vec2 p) {
    return step(abs(p.x) + abs(p.y), 1.0);
}
```

## Brick (Offset Rows)

```glsl
float brick(vec2 p, vec2 size, float mortar) {
    p.x += (mod(floor(p.y / size.y), 2.0) > 0.0) ? size.x * 0.5 : 0.0;
    vec2 cell = mod(p, size) / size;
    vec2 edge = step(mortar, cell) * step(mortar, 1.0 - cell);
    return edge.x * edge.y;
}
```

## Hex Grid

```glsl
// Get hex cell coordinates
vec4 hexCell(vec2 p, float s) {
    // s = hex radius
    vec2 q = vec2(p.x * 2.0 / 3.0, (p.y - p.x / sqrt(3.0)) / sqrt(3.0)) / s;
    vec2 r = round(q);
    vec2 f = q - r;
    if (3.0 * f.x * f.x + f.y * f.y > 1.0) r += sign(f) * step(0.5, abs(f));
    return vec4(p - s * vec2(r.x * 1.5, r.y * sqrt(3.0) + r.x * sqrt(3.0) * 0.5), r);
}

// Or: simpler IQ technique
vec2 hexCenter(vec2 p) {
    vec2 r = vec2(1.0, sqrt(3.0));
    vec2 h = r * 0.5;
    vec2 a = mod(p, r) - h;
    vec2 b = mod(p - h, r) - h;
    return dot(a, a) < dot(b, b) ? a : b;
}

// Distance to nearest hex edge:
float hexDist(vec2 p) {
    p = abs(p);
    return max(dot(p, vec2(sqrt(3.0) * 0.5, 0.5)), p.y);
}
```

## Truchet Tiles

```glsl
float truchet(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p) - 0.5;
    float r = hash21(i);
    if (r < 0.5) f.x = -f.x;
    // Quarter arcs from corners
    float a = abs(length(f - 0.5) - 0.5);
    float b = abs(length(f + 0.5) - 0.5);
    return min(a, b);
}
```

Renders as flowing curves; smoothstep for AA.

## Islamic-Style Star Pattern

```glsl
float starGrid(vec2 p, int n) {
    // Polar within each cell
    vec2 q = fract(p) - 0.5;
    float a = atan(q.x, q.y);
    float r = length(q);
    float m = cos(floor(0.5 + a / (6.28 / float(n))) * (6.28 / float(n)) - a) * r;
    return m;
}
```

Inspired by Iñigo Quilez's polar-fold patterns. Tune `n` (5, 6, 8, 12).

## Concentric Rings

```glsl
float rings(vec2 p, float spacing) {
    float d = length(p);
    return abs(fract(d / spacing) - 0.5);
}
```

## Animated Tile (Beating Cells)

```glsl
vec3 col = vec3(0.0);
vec2 i = floor(p);
vec2 f = fract(p) - 0.5;
float h = hash21(i);
float pulse = 0.5 + 0.5 * sin(time * 2.0 + h * 6.28);
float d = length(f) - 0.3 * pulse;
col = mix(vec3(1.0), vec3(0.1), smoothstep(-0.01, 0.01, d));
```

## Worked Example: Animated Hex Mesh

```glsl
uniform float2 resolution;
uniform float time;

float hash21(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

vec3 palette(float t) {
    return 0.5 + 0.5 * cos(6.28 * (vec3(1.0) * t + vec3(0.0, 0.33, 0.67)));
}

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    uv *= 4.0;
    vec2 r = vec2(1.0, sqrt(3.0));
    vec2 h = r * 0.5;
    vec2 a = mod(uv, r) - h;
    vec2 b = mod(uv - h, r) - h;
    vec2 local = dot(a, a) < dot(b, b) ? a : b;
    vec2 cell  = uv - local;
    float k = hash21(cell);
    float d = max(abs(local.x), max(abs(local.y), abs(local.x) * 0.5 + abs(local.y) * 0.866));
    float aa = 4.0 / resolution.y;
    float edge = smoothstep(0.49, 0.49 + aa, d);
    vec3 col = palette(k + time * 0.1);
    col = mix(col, vec3(0.05), edge);
    return vec4(col, 1.0);
}
```

## See Also

- [polar-uv-manipulation](polar-uv-manipulation.md) — Radial patterns.
- [voronoi-cellular-noise](voronoi-cellular-noise.md) — Organic cells.
- [sdf-2d](sdf-2d.md) — Shape-based patterns.
