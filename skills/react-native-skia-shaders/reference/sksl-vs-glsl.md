# SKSL Reference (Deep)

Authoritative reference for SKSL syntax and semantics as it applies to
`@shopify/react-native-skia` `RuntimeEffect`. Canonical source:
[Skia SKSL README](https://github.com/google/skia/tree/main/src/sksl).

## Language Goals

SKSL is "a standardized GLSL variant that avoids all the version and
dialect differences in GLSL in the wild." The Skia compiler emits the
target shader (Metal / Vulkan / OpenGL / WGSL / WebGL) so you write once.

Inside react-native-skia, `RuntimeEffect.Make` accepts **fragment-only**
shaders (no vertex stage). The entry point is `vec4 main(vec2 pos)` or
`half4 main(float2 pos)` (interchangeable).

## Types Table (Comprehensive)

### Scalar
- `bool`
- `int` (32-bit signed)
- `uint` (32-bit unsigned, when supported)
- `short`, `ushort` (16-bit)
- `half` (16-bit float, mediump-equivalent)
- `float` (32-bit float)

### Vector
- `bool2`, `bool3`, `bool4` (or `bvec2/3/4`)
- `int2`, `int3`, `int4` (or `ivec*`)
- `uint2`, `uint3`, `uint4` (or `uvec*`)
- `short2`, `short3`, `short4`
- `half2`, `half3`, `half4`
- `float2`, `float3`, `float4` (or `vec2/3/4`)

### Matrix
- `float2x2`, `float2x3`, `float2x4`,
- `float3x2`, `float3x3`, `float3x4`,
- `float4x2`, `float4x3`, `float4x4`
- `half<R>x<C>` analogues
- `mat2`, `mat3`, `mat4` (square only — `mat3` ≡ `float3x3`)

**Indexing**: `matrix[col]` returns the column vector. `matrix[col][row]`
returns a scalar. Same as GLSL.

### Special
- `shader` (a runtime effect or built-in shader; only valid as a uniform)
- `colorFilter` (rare in RuntimeEffect)
- `blender`

## Storage Qualifiers

- `uniform` — supplied from the host (JS-side `uniforms` prop in
  react-native-skia, or via `<RuntimeShader>`).
- `const` — compile-time constant.
- `in`, `out`, `inout` — function parameters only.
- (No `attribute`, no `varying` — fragment-only.)

## Removed vs GLSL

- `#version` directives → silently dropped if you include one; safer to
  remove.
- `precision` qualifiers (`highp`, `mediump`, `lowp`) → not allowed.
  Express precision via type (`half` vs `float`).
- `gl_*` built-ins → not visible in RuntimeEffect.
- `f` literal suffix → not allowed.
- Vector downcasting (`vec3 v = vec4(...)`) → forbidden; use swizzle.
- Struct ternary → forbidden.

## Built-in Functions (Selected)

All the GLSL math built-ins are available:

```
abs, sign, floor, ceil, round, trunc, fract, mod, modf
min, max, clamp, mix, step, smoothstep
length, distance, dot, cross, normalize, reflect, refract, faceforward
sin, cos, tan, asin, acos, atan, atan2 (alias for atan(y,x))
sinh, cosh, tanh, asinh, acosh, atanh
exp, log, exp2, log2, pow, sqrt, inversesqrt
matrixCompMult, outerProduct, transpose, inverse, determinant
all, any, not, lessThan, greaterThan, lessThanEqual, greaterThanEqual, equal, notEqual
isnan, isinf
bitfield* (where uint is supported)
dFdx, dFdy, fwidth         (partial-derivative builtins; may be slow on some Android GL)
```

SKSL-specific:
- `image.eval(coord)` — sample a child `shader` uniform.
- `sk_FragCoord` — (in raw Skia shaders; not exposed in RuntimeEffect main signature).
- `sk_Caps.*` — compile-time capability bits (`integerSupport`, `framebufferFetchSupport`, etc.).

## Function Modifiers

- `inline` — hint to inline at every call site.
- `noinline` — prevent inlining.
- `$pure` — internal Skia annotation, don't use.

## Preprocessor

Supported:
- `#define` (object-like)
- `#if`, `#ifdef`, `#ifndef`, `#else`, `#elif`, `#endif`
- `#error`
- `#line`

Not supported / unreliable:
- `#define` with arguments that contain function calls (rewrite as `const`)
- `#include` (some embeddings support it; RuntimeEffect does not)
- `#version`, `#extension`

## Swizzles

Standard GLSL swizzles:
- `.xyzw`, `.rgba`, `.stpq`

SKSL extras:
- `.LTRB` for `rect4` types (rare in RuntimeEffect)
- Constant components: `v.x01x` produces `(v.x, 0, 1, v.x)` — `0` and `1`
  insert literal values.

## Numeric Literals

- `1` → `int`
- `1.0`, `1.`, `.5` → `float`
- `1u` → `uint` (where uint is supported)
- `0x1A` → `int` (hex)
- No `f` or `F` suffix.

## Type Constructors

```glsl
float a = float(1);                // explicit conversion
vec3  v = vec3(1.0);               // splat
vec3  v = vec3(1.0, 2.0, 3.0);     // per-component
vec4  q = vec4(v, 1.0);            // append
vec4  q = vec4(v.xy, 0.0, 1.0);
mat3  m = mat3(1.0);               // identity
mat3  m = mat3(v1, v2, v3);        // column-by-column
```

**No downcast**: `vec2 a = vec3(...);` is illegal. Use a swizzle:
`vec2 a = vec3(...).xy;`.

## Statements

- `if`, `else`, `?:`
- `for`, `while`, `do { } while`
- `break`, `continue`, `return`
- `discard` — not available in RuntimeEffect (you can return `vec4(0)`
  premultiplied alpha for transparency).

## Function Declarations

```glsl
float foo(float x);                  // forward declaration
float foo(float x) { return x * 2.0; }  // definition

inline float bar(float x) { return x + 1.0; }

vec3 baz(in vec3 a, out vec3 b, inout vec3 c) {
    // ...
}
```

## Child Shader Sampling

A `uniform shader` represents a Skia shader whose evaluation is supplied by
the runtime — typically an image, gradient, or another effect.

```glsl
uniform shader src;
vec4 c = src.eval(coord);     // returns half4/vec4
```

**Coordinate space:** `coord` is in the destination's pixel space — same
coordinate system as the `main(pos)` parameter.

### Multiple child shaders

```glsl
uniform shader src;
uniform shader mask;
```

In react-native-skia, JSX children of `<Shader>` bind to `uniform shader`
declarations **by declaration order**, not by name:

```tsx
<Shader source={src}>
  <ImageShader image={imgA} ... />     {/* binds to first uniform shader (`src`) */}
  <ImageShader image={imgB} ... />     {/* binds to second (`mask`) */}
</Shader>
```

## RuntimeEffect-Specific Behavior

- `Make()` returns `null` on compile failure (does not throw).
- Unused uniforms are pruned by the compiler — JS-side calls to set them
  throw `Uniform not found`.
- Compile errors include line and column when the callback overload is
  used: `RuntimeEffect.Make(sksl, (err) => ...)`.
- Performance: each compile is non-trivial (~1–10ms). Compile once at
  module scope.

## Useful Internal References

- `sksl/sksl_compute.sksl` — compute-program built-ins (atomics, workgroups).
  Not exposed through react-native-skia's `RuntimeEffect`, but mentioned in
  the official README.
- Skia's `intrinsics.cpp` is the source of truth for which functions exist
  in any given backend.

## Discovery

For an unfamiliar shader, dump uniform info from JS:

```ts
const src = Skia.RuntimeEffect.Make(sksl)!;
console.log("uniform count:", src.getUniformCount());
for (let i = 0; i < src.getUniformCount(); i++) {
  console.log(i, src.getUniformName(i), src.getUniform(i));
}
```

`getUniform(i)` returns size and offset info — useful when porting a SKSL
shader you didn't write.

## See Also

- [`../techniques/sksl-vs-glsl.md`](../techniques/sksl-vs-glsl.md) — Cheatsheet.
- [`../techniques/sksl-pitfalls.md`](../techniques/sksl-pitfalls.md) — Compile-error catalog.
