# SKSL vs GLSL: Conversion Cheatsheet

SKSL (Skia Shading Language) is GLSL-like but has its own conventions. This
file is the **lookup table** for translating GLSL / ShaderToy code to SKSL
for use in react-native-skia.

For the canonical Skia reference, see the
[SKSL README](https://github.com/google/skia/tree/main/src/sksl).

## The Entry Point

| GLSL / ShaderToy | SKSL |
|---|---|
| `void mainImage(out vec4 fragColor, in vec2 fragCoord) { fragColor = ...; }` | `vec4 main(vec2 pos) { return ...; }` |
| `void main() { gl_FragColor = ...; }` (WebGL1) | `vec4 main(vec2 pos) { return ...; }` |
| `void main() { fragColor = ...; }` (WebGL2 with `out`) | `vec4 main(vec2 pos) { return ...; }` |

SKSL also accepts `half4 main(float2 pos)` — half precision is fine for
color, often faster on mobile.

## Coordinates

| ShaderToy / GLSL | SKSL |
|---|---|
| `fragCoord` | `pos` (the `main` parameter) |
| `gl_FragCoord.xy` | `pos` |
| `iResolution.xy` | A `uniform float2 resolution;` you pass yourself |
| `(2.0 * fragCoord - iResolution.xy) / iResolution.y` | `(2.0 * pos - resolution) / resolution.y` |
| `fragCoord / iResolution.xy` (UV 0..1) | `pos / resolution` |

**Y-axis:** SKSL `pos` is **top-left origin** (same as `gl_FragCoord`). If
you're porting a ShaderToy shader and it appears upside down compared to the
preview on shadertoy.com, flip Y: `vec2 uv = vec2(pos.x, resolution.y -
pos.y) / resolution;`. Most ShaderToy code doesn't care.

## Built-in Uniforms (ShaderToy)

ShaderToy provides `iTime`, `iResolution`, `iMouse`, etc. **SKSL has none of
these built-in.** You declare and pass them yourself:

```glsl
uniform float2 resolution;   // was iResolution.xy
uniform float  time;         // was iTime
uniform float2 touch;        // was iMouse.xy (0,0 if untouched)
uniform float  frame;        // was iFrame (rarely needed)
```

## Types

| GLSL | SKSL | Notes |
|---|---|---|
| `vec2` | `vec2` or `float2` | Interchangeable |
| `vec3` | `vec3` or `float3` | Interchangeable |
| `vec4` | `vec4` or `float4` | Interchangeable |
| `ivec2`, `ivec3`, `ivec4` | `int2`, `int3`, `int4` | Or `ivec*` works |
| `bvec2/3/4` | `bool2`, `bool3`, `bool4` | `bvec*` also works |
| `mat2`, `mat3`, `mat4` | `float2x2`, `float3x3`, `float4x4` | Or `mat2/3/4` |
| `mat2x3` etc. | `float2x3` etc. | Skia uses `RxC` consistent ordering |
| n/a | `half`, `half2`, `half3`, `half4` | Medium precision, faster on mobile |
| n/a | `short`, `ushort` | Medium-precision integer |

**Precision modifiers** like `highp`, `mediump`, `lowp` are **not allowed**
in SKSL — use `half` for medium and `float` for high. `precision highp
float;` and similar headers must be removed.

## Numeric Literals

```glsl
// GLSL                  // SKSL
float x = 1.0;           float x = 1.0;     // OK
float x = 1.;            float x = 1.;      // OK
float x = 1;             float x = 1;       // OK (SKSL relaxes this)
float y = 1.0f;          float y = 1.0;     // 'f' suffix NOT allowed
```

## Built-in Variables

| GLSL | SKSL | Notes |
|---|---|---|
| `gl_FragColor` | `return value` of `main()` | Don't declare; just `return vec4(...)`. |
| `gl_FragCoord.xy` | `pos` (parameter) | |
| `gl_FragCoord.z` | n/a | No depth in fragment-only SKSL shaders |
| `gl_PointCoord` | n/a | No points |
| Output `vec4 fragColor` declaration | **Remove it** | SKSL returns from `main` |
| `#version 300 es` | **Remove it** | No version directives |
| `precision highp float;` | **Remove it** | No precision modifiers |
| `texture(s, uv)` / `texture2D` | `s.eval(pixelCoord)` where `s` is `uniform shader` | **Coords are pixels, not UV.** |
| `dFdx` / `dFdy` / `fwidth` | Same names — **but limited support**; check device | |

## Sampling Images / Textures

```glsl
// GLSL (ShaderToy)
uniform sampler2D iChannel0;
vec4 c = texture(iChannel0, uv);

// SKSL (react-native-skia)
uniform shader image;
vec4 c = image.eval(pos);          // pos is pixel coordinates of THIS shader's canvas
// To sample at a custom location in image pixels:
vec4 c = image.eval(uv * imageSize);   // imageSize you must pass as a uniform
```

In react-native-skia, the child shader is supplied as a JSX child:
```tsx
<Shader source={source} uniforms={...}>
  <ImageShader image={img} fit="cover" rect={rect} />
</Shader>
```
The SKSL identifier (`image` in the example above) matches by **declaration
order**, not name — first `uniform shader` = first JSX child.

## Functions, Operators, Math

These work in both (no change needed):

```
abs, sign, floor, ceil, round, fract, mod, min, max, clamp, mix, step,
smoothstep, length, distance, dot, cross, normalize, reflect, refract,
faceforward, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, log,
pow, sqrt, inversesqrt, exp2, log2, matrixCompMult, transpose, inverse,
determinant
```

**Swizzles** work normally (`.xyz`, `.rgba`, `.xxyy`, etc.). SKSL adds two
extras you can usually ignore: `.LTRB` for left/top/right/bottom on bounds
types, and constant swizzles `.0` / `.1` to insert literal 0 or 1 components.

**Downcasting vector size**: SKSL **forbids** `vec3 v = vec4(...)`. Use a
swizzle: `vec3 v = vec4(...).xyz;`.

## Loops and Branching

- `for`, `while`, `do-while`, `if`/`else`, `?:` all work.
- `break`, `continue`, `return` work.
- Compile-time constant loop bounds are still preferred for older drivers but
  SKSL handles non-const bounds fine on modern Skia.
- Recursion is **not allowed** (same as GLSL).

## Macros / Preprocessor

```glsl
// Allowed
#define MAX_STEPS 64
#define PI 3.14159265
#define ITER(i) for (int i = 0; i < N; i++)

// NOT allowed: macro body containing function calls
#define SUN normalize(vec3(0.7, 0.5, -0.6))   // ❌
const vec3 SUN = vec3(0.71, 0.51, -0.61);     // ✅ pre-compute or use const
```

## Structs

```glsl
struct Hit { float t; vec3 n; int mat; };
Hit h;
h.t = 1.0;
```
Works. **Cannot ternary-select structs** (`a ? structA : structB` is illegal).
Use `if/else`.

## Reserved Words to Avoid

Beyond GLSL keywords, SKSL also reserves these as identifiers — don't name a
variable, function, or uniform any of them:

```
sample, filter, input, output, texture, common, partition, active, patch,
cast, half, half2, half3, half4, short, ushort, layout, uniform_buffer
```

The most common mistake: naming a parameter `sample` — SKSL's child-shader
sampling intrinsic conflicts. Use `samplePos`, `coord`, etc.

## Function-Definition Order

Like GLSL, SKSL needs functions declared before use. Either reorder, or
forward-declare:

```glsl
float fbm(vec2 p);                  // forward decl
float noise(vec2 p) { return fbm(p); }     // legal now
float fbm(vec2 p) { /* … */ }       // body later
```

## `inline` Hint

SKSL supports `inline` as a hint to the compiler (GLSL does not). Use it for
small hot helpers:
```glsl
inline float sdSphere(vec3 p, float r) { return length(p) - r; }
```

## ShaderToy `mainImage` → SKSL Wrapper

When porting a ShaderToy snippet, the mechanical translation is:

```glsl
// ShaderToy original
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    fragColor = vec4(uv, 0.5 + 0.5 * sin(iTime), 1.0);
}
```

becomes:

```glsl
// SKSL port
uniform float2 resolution;
uniform float time;

vec4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    return vec4(uv, 0.5 + 0.5 * sin(time), 1.0);
}
```

Mechanical rules:
1. Strip the `out vec4 fragColor, in vec2 fragCoord` signature → `vec4 main(vec2 pos)`.
2. Rename `fragCoord` → `pos` (or whatever you called the param).
3. Replace every `iResolution.xy` with `resolution`, declare it as a uniform.
4. Replace every `iTime` with `time`, declare uniform.
5. Replace every `iMouse.xy` with `touch`, declare uniform; in ShaderToy
   `iMouse` has `.z`/`.w` for click state — SKSL has none, you handle that JS-side.
6. Replace the last `fragColor = vec4(...);` with `return vec4(...);`. Remove
   any other writes to `fragColor` and re-flow with locals.
7. Replace `texture(iChannelN, uv)` → `imageN.eval(uv * imageSize)` and
   declare `uniform shader imageN;`. **Remember UV→pixel conversion.**

## Complete Port Example

### Before (ShaderToy GLSL)

```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
    float d = length(uv) - 0.5;
    vec3 col = vec3(smoothstep(0.01, 0.0, d));
    col *= 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0, 2, 4));
    fragColor = vec4(col, 1.0);
}
```

### After (SKSL for react-native-skia)

```glsl
uniform float2 resolution;
uniform float time;

vec4 main(vec2 pos) {
    vec2 uv = (2.0 * pos - resolution) / resolution.y;
    float d = length(uv) - 0.5;
    vec3 col = vec3(smoothstep(0.01, 0.0, d));
    col *= 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));
    return vec4(col, 1.0);
}
```

Diff:
- Signature line rewritten.
- `fragCoord` → `pos`; `iResolution.xy` → `resolution`; `iTime` → `time`.
- Final write swapped for `return`.

## Features SKSL Adds (Not in GLSL)

- `half`, `half2/3/4`, `short`, `ushort` types.
- `inline` function modifier.
- `sk_Caps.*` compile-time capability bits.
- `sk_Position`, `sk_FragCoord`, `sk_Clockwise` — only relevant when writing
  raw shaders for Skia's GPU backend (not exposed via react-native-skia's
  `RuntimeEffect`, which is fragment-only).

## Features SKSL Removes / Restricts vs GLSL

- No `#version`, no precision modifiers, no `f` literal suffix.
- No vector downcasts (`vec3 v = vec4(...)` illegal — use swizzle).
- No struct ternary.
- No recursion.
- No `gl_*` built-ins inside RuntimeEffect.
- No multi-out attachments (RuntimeEffect returns a single color).

## See Also

- [rn-skia-integration](rn-skia-integration.md) — How to actually run the shader.
- [sksl-pitfalls](sksl-pitfalls.md) — Compile-error catalog.
- Reference: [`reference/sksl-vs-glsl.md`](../reference/sksl-vs-glsl.md).
