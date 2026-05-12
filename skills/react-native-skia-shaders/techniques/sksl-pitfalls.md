# SKSL Pitfalls

The full catalog of "my shader doesn't work" failure modes for SKSL inside
`@shopify/react-native-skia`, with their fixes.

## `Skia.RuntimeEffect.Make` returns `null`

The SKSL failed to compile. `Make` returns `null` (does **not** throw).

```tsx
const source = Skia.RuntimeEffect.Make(sksl);
if (!source) throw new Error("SKSL compile failed");
```

The current public signature is single-arg: `Skia.RuntimeEffect.Make(sksl: string)` — there's no error callback overload exposed. When compilation fails, Skia itself logs the error to `console.log` (visible in Metro / Flipper). If you're not seeing the log:
- Copy the SKSL into a CanvasKit / SKSL playground in a browser — its console will show the line number.
- Bisect: render a minimal shader (`vec4 main(vec2 pos) { return vec4(1); }`) and re-add code until it breaks.

## "Uniform '<x>' not found"

The compiler **pruned the uniform** because it's never used in the shader
body. The JS side tries to set it anyway → error.

Fix: either use the uniform inside the shader, or stop passing it:
```glsl
uniform float unused;   // ❌ will be pruned
vec4 main(vec2 pos) { return vec4(1.0); }
```
```glsl
uniform float unused;
vec4 main(vec2 pos) {
    return vec4(1.0) + unused * 0.0;   // ✅ referenced (as a no-op)
}
```

## Wrong uniform arity → silent wrong output

Declaring `uniform float3 color;` and passing `color: [1, 0]` (2 elements)
silently produces wrong colors. There's no runtime size check.

| SKSL | JS arity |
|---|---|
| `float` / `int` | 1 |
| `float2` / `int2` | 2 |
| `float3` / `int3` | 3 |
| `float4` / `int4` | 4 |
| `float2x2` | 4 |
| `float3x3` | 9 |
| `float4x4` | 16 |
| `float[N]` | N |

## Black screen / nothing renders

Checklist in order:

1. Did `Skia.RuntimeEffect.Make` return non-null? (most common)
2. Is `<Shader>` inside a paintable (`<Fill>`, `<Rect>`, etc.)?
3. Is the Canvas inside a sized container? `<Canvas style={{ flex: 1 }}>` needs a parent with non-zero size.
4. Is alpha being returned? `return vec4(col, 0.0);` is fully transparent.
5. Are uniforms supplied with correct arity?
6. Is `resolution` actually being passed and non-zero? Divide-by-zero in `pos / resolution` produces `NaN` and shows black.
7. Try replacing the body with `return vec4(1.0, 0.0, 0.0, 1.0);`. If that's red, your wiring is fine and the bug is in shader logic. If still black, your wiring is broken.

## Reserved-word collisions

SKSL forbids these as identifiers:

```
sample, filter, input, output, texture, common, partition, active, patch,
cast, layout
```

Most common: naming a local `sample` (used for tap positions, sampling
points). Rename to `samplePos`, `coord`, `tap`.

```glsl
// ❌
vec2 sample = pos / resolution;
// ✅
vec2 samplePos = pos / resolution;
```

## `gl_FragCoord` / `texture()` / `iTime` errors

SKSL doesn't have these. See [sksl-vs-glsl](sksl-vs-glsl.md) for the full
translation table. Quick fixes:

- `gl_FragCoord.xy` → `pos` (the `main` parameter).
- `texture(s, uv)` → `s.eval(pixelCoord)` where `s` is `uniform shader`.
- `iTime` → declare `uniform float time;` and pass it from JS.
- `iResolution.xy` → declare `uniform float2 resolution;`.

## Vector downcasting

SKSL does **not** allow `vec3 v = vec4(...)`. Use a swizzle:

```glsl
// ❌
vec3 col = vec4(1.0, 0.5, 0.2, 1.0);
// ✅
vec3 col = vec4(1.0, 0.5, 0.2, 1.0).xyz;
```

## Numeric literal suffix `f`

Allowed in GLSL ES, **not** in SKSL:

```glsl
// ❌
float x = 1.5f;
// ✅
float x = 1.5;
```

## Vector ↔ float ambiguity

```glsl
// ❌ — vec3 from a single float
vec3 col = 0.5;
// ✅
vec3 col = vec3(0.5);
```

## Function used before declared

Same rule as GLSL — forward-declare or reorder:

```glsl
// ❌ — sceneSDF used before defined
float map(vec3 p) { return sceneSDF(p); }
float sceneSDF(vec3 p) { return length(p) - 1.0; }

// ✅ — reorder
float sceneSDF(vec3 p) { return length(p) - 1.0; }
float map(vec3 p) { return sceneSDF(p); }

// ✅ — or forward-declare
float sceneSDF(vec3 p);
float map(vec3 p) { return sceneSDF(p); }
float sceneSDF(vec3 p) { return length(p) - 1.0; }
```

## `#define` with function calls

Allowed in GLSL, **not safe** in SKSL — macros are textual, but some SKSL
preprocessors are stricter:

```glsl
// ❌ — fragile
#define SUN normalize(vec3(0.7, 0.5, -0.6))

// ✅ — precompute
const vec3 SUN = vec3(0.7637, 0.5455, -0.6546);
```

## Ternary on structs

```glsl
struct H { float t; vec3 n; };
H a, b;
// ❌
H c = cond ? a : b;
// ✅
H c;
if (cond) c = a; else c = b;
```

## `inout` with structs vs primitives

SKSL supports `inout` for primitives and small structs, but some old
backends choke on `inout` for arrays. If you see weird "cannot be used as
inout" errors, pass by value and return.

## Child shader binding by order, not name

```glsl
uniform shader image;
uniform shader mask;
```

```tsx
// ❌ — mask binds to `image` (first JSX child)
<Shader source={src}>
  <ImageShader image={mask} ... />   // becomes `image`
  <ImageShader image={img}  ... />   // becomes `mask`
</Shader>
```

JSX child order = uniform declaration order. Watch the order.

## `image.eval` returns transparent

If the destination rect of the child `<ImageShader>` is smaller than the
Canvas (or doesn't overlap the sample coord), `image.eval(pos)` returns
transparent. Set `rect` to the Canvas size (or wherever you'll sample) and
use `fit="cover"` so the image fills it.

```tsx
<ImageShader image={img} fit="cover" rect={{ x: 0, y: 0, width, height }} />
```

Also set `tx="clamp"` / `ty="clamp"` to avoid black/transparent edges when
your shader displaces sampling coords beyond the rect.

## Reanimated value not updating uniform

```tsx
// ❌ — captures sharedValue.value once, JS-side
<Shader uniforms={{ time: shared.value }} />

// ✅ — pass a derived value
const u = useDerivedValue(() => ({ time: shared.value }));
<Shader uniforms={u} />
```

## Recompiles on every render

```tsx
// ❌
function MyShader() {
  const source = Skia.RuntimeEffect.Make(sksl);   // recompiles every render
  // ...
}

// ✅
const source = Skia.RuntimeEffect.Make(sksl)!;    // module scope
function MyShader() { /* ... */ }
```

If the SKSL depends on a prop, memoize:
```tsx
const source = useMemo(() => Skia.RuntimeEffect.Make(buildSksl(variant))!, [variant]);
```

## Loop bound issues

Older driver versions (Adreno, PowerVR) want compile-time-constant loop
bounds. SKSL handles dynamic bounds in most current versions, but if you
see "Loop bound must be constant" or similar:

```glsl
// ✅ — use a #define constant
#define MAX_STEPS 64
for (int i = 0; i < MAX_STEPS; i++) { ... }
```

## Backslash escapes inside JS template literals

```tsx
const sksl = `
uniform float x;
vec4 main(vec2 pos) {
    // ❌ The backslash here may be interpreted by JS first
    float n = some\\nthing(x);
    return vec4(1.0);
}`;
```

If you need a literal `\` in SKSL (rare), double it in the JS string.
Mostly: keep SKSL ASCII, no escapes.

## NaN / Inf creeping in

```glsl
// ❌ — division by zero possible
vec3 dir = vec3(uv, 0.0);
vec3 nd = normalize(dir);    // NaN if dir is zero vector

// ✅
vec3 nd = length(dir) > 0.0001 ? normalize(dir) : vec3(0, 0, 1);
```

NaN propagates; one bad pixel sometimes becomes black for that whole
fragment. Common sources:
- `normalize(zeroVec)`
- `pow(negativeBase, fract)` — undefined
- `acos(x)` for `|x| > 1`
- `sqrt(negative)`
- `log(0)`

Clamp inputs defensively.

## Mixing `half` and `float`

```glsl
half3 col = half3(...);
float x = ...;
col *= x;                  // implicit promotion may be slow or fail
col *= half(x);            // explicit cast
```

Some drivers are strict; explicit casts are safer.

## Premultiplied alpha confusion

Skia paints expect **premultiplied** alpha. If your shader returns
`vec4(rgb, alpha)` with non-pre RGB, you'll get over-bright halos on
semi-transparent regions.

```glsl
// If your color is "straight" (not premultiplied):
return vec4(rgb * alpha, alpha);
```

For opaque (`alpha = 1.0`), this doesn't matter.

## "It works on iOS, breaks on Android"

Usually one of:
- Used `pow(x, large)` — overflows in `half`. Force `float` or unroll.
- Used `dFdx`/`dFdy` — slower / less precise on older Adreno.
- Used a long loop that compiles but stalls due to thermal throttling.
- Used `image.eval` on coordinates outside the rect with default `tx`/`ty`.

Test on the lowest-end target you support, early and often.

## See Also

- [sksl-vs-glsl](sksl-vs-glsl.md) — Conversion cheatsheet.
- [mobile-performance](mobile-performance.md) — Cost budgets and profiling.
- [rn-skia-integration](rn-skia-integration.md) — Wiring fundamentals.
