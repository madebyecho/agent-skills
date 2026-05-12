# 2D Signed Distance Functions

SDFs describe 2D shapes as a function `d(p) = signed distance from p to the
shape boundary` (negative inside, positive outside). Cheap to render,
trivial to anti-alias, easy to compose.

In SKSL on react-native-skia, SDFs are the right answer for: custom UI
shapes, badges, glyphs, icons-as-math, loading indicators, animated
ornaments. They're rendered into `<Shader>` paints, often inside a
`<Fill>` or a clipped `<RoundedRect>`.

## Use Cases

- Custom shapes (rounded squircles, hex badges, hearts) with perfect AA at any size.
- UI accent elements that breathe / morph / pulse via uniforms.
- Logos and icons defined mathematically (resolution-independent).
- Hit-testing via the same math used for rendering.
- Composing complex shapes from primitives using boolean ops.

## SKSL Template

```glsl
uniform float2 resolution;

float sdCircle(vec2 p, float r) {
    return length(p) - r;
}

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;   // aspect-correct, -1..1 vertical
    float d = sdCircle(uv, 0.5);
    vec3 col = (d > 0.0) ? vec3(0.4, 0.7, 0.85) : vec3(0.9, 0.6, 0.3);
    col *= 1.0 - exp(-6.0 * abs(d));                     // shadow toward boundary
    col *= 0.8 + 0.2 * cos(150.0 * d);                   // banded contour
    col = mix(col, vec3(1.0), 1.0 - smoothstep(0.0, 0.01, abs(d)));   // outline
    return vec4(col, 1.0);
}
```

## SDF Primitive Library

```glsl
// Circle
float sdCircle(vec2 p, float r) {
    return length(p) - r;
}

// Box (b = half-extents)
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

// Rounded box
float sdRoundedBox(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - b + r;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

// Per-corner rounded box (TL, TR, BR, BL)
float sdRoundedBox4(vec2 p, vec2 b, vec4 r) {
    r.xy = (p.x > 0.0) ? r.xy : r.zw;
    r.x  = (p.y > 0.0) ? r.x  : r.y;
    vec2 q = abs(p) - b + r.x;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r.x;
}

// Segment (a -> b, thickness encoded later)
float sdSegment(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}

// Line of thickness w
float sdLine(vec2 p, vec2 a, vec2 b, float w) {
    return sdSegment(p, a, b) - w;
}

// Equilateral triangle (k = side length)
float sdEqTriangle(vec2 p, float k) {
    const float k3 = 1.7320508;     // sqrt(3)
    p.x = abs(p.x) - k;
    p.y = p.y + k / k3;
    if (p.x + k3 * p.y > 0.0) p = vec2(p.x - k3 * p.y, -k3 * p.x - p.y) / 2.0;
    p.x -= clamp(p.x, -2.0 * k, 0.0);
    return -length(p) * sign(p.y);
}

// Regular polygon (n sides, radius r)
float sdPolygon(vec2 p, float n, float r) {
    float a = atan(p.x, p.y) + 3.14159265;
    float seg = 6.28318530 / n;
    float i = floor(a / seg);
    float a0 = i * seg + seg * 0.5 - 3.14159265;
    vec2 e = vec2(sin(a0), cos(a0));
    return dot(p, e) - r * cos(seg * 0.5);
}

// Star (n points, r = outer, ratio = inner/outer)
float sdStar(vec2 p, float r, int n, float ratio) {
    float an = 3.14159265 / float(n);
    float en = 3.14159265 / mix(2.0, float(n), ratio);
    vec2 acs = vec2(cos(an), sin(an));
    vec2 ecs = vec2(cos(en), sin(en));
    float bn = mod(atan(p.x, p.y), 2.0 * an) - an;
    p = length(p) * vec2(cos(bn), abs(sin(bn)));
    p -= r * acs;
    p += ecs * clamp(-dot(p, ecs), 0.0, r * acs.y / ecs.y);
    return length(p) * sign(p.x);
}

// Heart (sized to fit ~[-1,1])
float sdHeart(vec2 p) {
    p.x = abs(p.x);
    if (p.y + p.x > 1.0) return sqrt(dot(p - vec2(0.25, 0.75), p - vec2(0.25, 0.75))) - sqrt(2.0) / 4.0;
    return sqrt(min(dot(p - vec2(0.0, 1.0), p - vec2(0.0, 1.0)), dot(p - 0.5 * max(p.x + p.y, 0.0), p - 0.5 * max(p.x + p.y, 0.0)))) * sign(p.x - p.y);
}

// Ellipse (a, b half-axes) — approximate
float sdEllipse(vec2 p, vec2 ab) {
    p = abs(p);
    if (p.x > p.y) { p = p.yx; ab = ab.yx; }
    float l = ab.y * ab.y - ab.x * ab.x;
    float m = ab.x * p.x / l;
    float n = ab.y * p.y / l;
    float m2 = m * m, n2 = n * n;
    float c = (m2 + n2 - 1.0) / 3.0;
    float c3 = c * c * c;
    float q = c3 + m2 * n2 * 2.0;
    float d = c3 + m2 * n2;
    float g = m + m * n2;
    float co;
    if (d < 0.0) {
        float h = acos(q / c3) / 3.0;
        float s = cos(h);
        float t = sin(h) * sqrt(3.0);
        float rx = sqrt(-c * (s + t + 2.0) + m2);
        float ry = sqrt(-c * (s - t + 2.0) + m2);
        co = (ry + sign(l) * rx + abs(g) / (rx * ry) - m) / 2.0;
    } else {
        float h = 2.0 * m * n * sqrt(d);
        float s = sign(q + h) * pow(abs(q + h), 1.0 / 3.0);
        float u = sign(q - h) * pow(abs(q - h), 1.0 / 3.0);
        float rx = -s - u - c * 4.0 + 2.0 * m2;
        float ry = (s - u) * sqrt(3.0);
        float rm = sqrt(rx * rx + ry * ry);
        co = (ry / sqrt(rm - rx) + 2.0 * g / rm - m) / 2.0;
    }
    vec2 r = ab * vec2(co, sqrt(1.0 - co * co));
    return length(r - p) * sign(p.y - r.y);
}
```

(Most of these primitives are Inigo Quilez's distance-function library,
ported to SKSL — `vec2` works, math identical.)

## Boolean Operations

```glsl
float opUnion(float a, float b)         { return min(a, b); }
float opSubtraction(float a, float b)   { return max(a, -b); }
float opIntersection(float a, float b)  { return max(a, b); }

float opSmoothUnion(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}

float opSmoothSubtraction(float a, float b, float k) {
    float h = max(k - abs(a + b), 0.0);
    return max(a, -b) + h * h * 0.25 / k;
}
```

## Coloring & Filling

```glsl
// Solid fill (no AA)
vec3 fill = (d < 0.0) ? vec3(0.95, 0.4, 0.2) : vec3(0.0);

// AA fill — `aa` is a small constant in world units (e.g. 1.5 pixels)
float aa = 1.5 / resolution.y;
float alpha = 1.0 - smoothstep(-aa, aa, d);
vec3 fill = mix(vec3(0.0), vec3(0.95, 0.4, 0.2), alpha);

// Outlined
float thickness = 0.005;
float outline = 1.0 - smoothstep(thickness, thickness + aa, abs(d));
vec3 col = mix(fill, vec3(1.0), outline);
```

See [anti-aliasing](anti-aliasing.md) for SDF AA details.

## Domain Transforms

```glsl
// Translate
float dCircle = sdCircle(p - vec2(0.3, 0.0), 0.2);

// Rotate
vec2 rot(vec2 p, float a) { float c = cos(a), s = sin(a); return mat2(c, s, -s, c) * p; }
float dBox = sdBox(rot(p, 0.5), vec2(0.2));

// Scale (must divide d by scale to keep it a true SDF)
float dScaled = sdSphere(p / 2.0, 0.5) * 2.0;

// Mirror / kaleidoscope — see polar-uv-manipulation.md
```

## Worked Example: Animated Heart Button

```tsx
const sksl = `
uniform float2 resolution;
uniform float pulse;
uniform float aspect;

float sdHeart(vec2 p) {
    p.x = abs(p.x);
    if (p.y + p.x > 1.0) return distance(p, vec2(0.25, 0.75)) - sqrt(2.0) / 4.0;
    return sqrt(min(
        dot(p - vec2(0.0, 1.0), p - vec2(0.0, 1.0)),
        dot(p - 0.5 * max(p.x + p.y, 0.0), p - 0.5 * max(p.x + p.y, 0.0))
    )) * sign(p.x - p.y);
}

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    uv.y = -uv.y * 0.9 + 0.4;
    uv *= 1.0 / (0.9 + 0.1 * pulse);
    float d = sdHeart(uv);
    float aa = 2.0 / resolution.y;
    float fill = 1.0 - smoothstep(-aa, aa, d);
    vec3 col = mix(vec3(0.05, 0.05, 0.08), vec3(1.0, 0.25, 0.4 + 0.2 * pulse), fill);
    return vec4(col, 1.0);
}`;
```

```tsx
const source = Skia.RuntimeEffect.Make(sksl)!;
const HeartButton = () => {
  const pulse = useSharedValue(0);
  useEffect(() => {
    pulse.value = withRepeat(withTiming(1, { duration: 700 }), -1, true);
  }, []);
  const u = useDerivedValue(() => ({ resolution: [120, 120], pulse: pulse.value, aspect: 1 }));
  return (
    <Canvas style={{ width: 120, height: 120 }}>
      <Fill>
        <Shader source={source} uniforms={u} />
      </Fill>
    </Canvas>
  );
};
```

## Tricks (Brief)

See [sdf-tricks](sdf-tricks.md) for these in depth:

```glsl
// Hollow shell of thickness t
d = abs(d) - t;

// Concentric rings every step `s`
d = abs(mod(d, s) - s * 0.5) - lineWidth;

// Onion layers
d = abs(d) - r;   // ring of half-width r
```

## See Also

- [anti-aliasing](anti-aliasing.md) — SDF analytical AA, more on `smoothstep` widths.
- [sdf-tricks](sdf-tricks.md) — Hollowing, outlines, debug viz.
- [csg-boolean-operations](csg-boolean-operations.md) — Smooth blends.
- [polar-uv-manipulation](polar-uv-manipulation.md) — Kaleidoscopes, polar warps.
- Reference: [`reference/sdf-3d.md`](../reference/sdf-3d.md) (covers the 2D math too).
