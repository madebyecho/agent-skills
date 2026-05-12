# Procedural Noise Reference

Theory behind hash-based noise: aliasing, frequency content, FBM
convergence, Perlin vs Simplex tradeoffs.

## What is "Noise"?

A function `n: Rⁿ → R` that is:
- Deterministic (same input → same output)
- Pseudo-random looking
- Continuous (`C⁰`) or smoother (`C¹`, `C²`)
- Bandlimited (no high-frequency aliasing)

## Hash Quality

The cheapest hash is `fract(sin(dot(p, K)) * M)`. Problems:
- `sin` precision degrades for large arguments on mobile GPUs.
- Output has visible structure when `p` covers a large range.
- Not uniform in the unit interval (slight clumping).

Quality alternatives:
- **PCG / xxHash / Murmur3 integer mixes** — uniform, high entropy. Slightly
  more expensive.
- **Per-octave reseeding** — re-hash the input with a per-octave offset to
  avoid axis-aligned banding.

For react-native-skia on mobile, `fract(sin(dot))` is fine until you see
banding — then upgrade.

## Value Noise

```
value(p) = bilinear interpolation of hash() at integer corners of cell containing p
```

C⁰ continuous if you use linear interpolation. C¹ with smoothstep (`u = f*f*(3-2f)`). C² with quintic (`u = 6f⁵ - 15f⁴ + 10f³`).

Cheap (4 hashes in 2D, 8 in 3D) but the underlying grid is visible at low
frequencies.

## Perlin Noise (Gradient)

Ken Perlin's gradient noise. Instead of hashing the value at each corner,
hash a *gradient vector* and use the dot product with the offset to the
sample point:

$$ p(x) = \sum_{c} w(x - c) \cdot (\vec{g}_c \cdot (x - c)) $$

Where `c` ranges over the 4 (2D) / 8 (3D) corners, `g_c` is the gradient
at corner `c`, and `w` is the quintic falloff.

Perlin removes the value-noise grid signature. The remaining artifact is
**axis-aligned banding** at the cell boundaries, visible at low frequencies.

## Simplex Noise

Ken Perlin's later (2001) noise based on a simplex grid (triangle in 2D,
tetrahedron in 3D). Advantages:
- Fewer interpolation samples (3 in 2D vs 4; 4 in 3D vs 8).
- No axis-aligned banding (the simplex grid is rotated).
- Better directional isotropy.

Disadvantage: more code, slightly more arithmetic per evaluation. On
mobile, simplex 2D is roughly the same cost as Perlin 2D and looks better.

## FBM (Fractal Brownian Motion)

Sum octaves of base noise:

$$ \mathrm{fbm}(x) = \sum_{i=0}^{N-1} a^i \cdot n(b^i \cdot x) $$

Standard: `a = 0.5`, `b = 2`. Frequency doubles each octave, amplitude
halves. Output range converges to `±1` for `n ∈ [-1, 1]` and infinite
octaves.

### Octave Effect

```
1 octave:  smooth blob noise
2 octaves: gentle wrinkles overlaid
3 octaves: visible terrain-like roughness
4 octaves: mountainous detail
5+ octaves: photoreal cloud / terrain
```

Each octave doubles the high-frequency content. Beyond ~6 octaves, detail
is finer than a pixel — pure cost for no visible benefit.

### Mobile Octave Budget

- 3 octaves: low-end Android, ambient FBM
- 4 octaves: mid-tier, default
- 5 octaves: flagship, hero shader
- 6+: desktop only

### Ridged FBM

$$ \mathrm{ridged}(x) = \sum_{i=0}^{N-1} a^i \cdot (1 - |n(b^i \cdot x)|) $$

Produces ridges where the noise crosses zero — used for mountain ridges,
fluid veins, lightning.

### Turbulence

$$ \mathrm{turb}(x) = \sum_{i=0}^{N-1} a^i \cdot |n(b^i \cdot x)| $$

Sharper, "billowy" texture — clouds, smoke.

## Domain Warping

$$ \mathrm{warp}(x) = \mathrm{fbm}(x + \alpha \cdot \mathrm{fbm}(x + \beta)) $$

Iterating this `k` times produces increasingly organic patterns. Iñigo
Quilez's "Warp 2" pattern uses k=2 — gorgeous, expensive (3× the FBM
calls).

## Aliasing Mitigation

When sampling noise at very high frequencies (small features), you alias.
Two mitigations:
- Increase samples per pixel (SSAA — expensive).
- Reduce noise frequency adaptively based on derivative:
  ```glsl
  float lod = log2(fwidth(p) * frequency);
  // For each octave i, fade contribution as i exceeds (MAX - lod)
  ```

In practice on mobile, just cap your max frequency to ~`resolution.y / 4`.

## Why `fract(sin(dot(p, K))) * M` Works

`sin` of an arbitrary large value is effectively chaotic (high-frequency).
Multiplying by `M` and taking `fract` extracts a pseudorandom decimal. The
specific constants `127.1, 311.7, 43758.5453` are empirical — they happen
to spread output uniformly.

Failure mode: as `p` grows large (e.g. `p = (5000, 5000)`), the `sin`
argument is huge and the result of `sin` becomes increasingly imprecise on
16-bit float math (which some mobile GPUs use internally). Banding
appears. Solution: keep coords small (multiply UV by ≤ 100), or move to
integer-mix hashes.

## 3D Noise Cost

Each dimension doubles the corner count:
- 1D: 2 hashes
- 2D: 4 hashes
- 3D: 8 hashes
- 4D: 16 hashes

3D noise costs ~2× 2D. Use 3D only when the third dimension matters
(depth, time-loop continuity). For an animated 2D shader, prefer 2D + scroll.

## Tilable Noise

Repeat the noise period exactly:

```glsl
float tilable(vec2 p, float period) {
    return value(mod(p, period));
}
```

The cell at `mod 0` matches the cell at `mod period`, but the inner
interpolation isn't continuous unless the hashes themselves wrap. For
true tiling, wrap the input to the hash:

```glsl
float h(vec2 i, float period) { return hash21(mod(i, vec2(period))); }
```

## Derivatives (Analytic)

For FBM with analytic derivatives (used in advanced terrain rendering):

$$ \frac{\partial \mathrm{fbm}}{\partial x} = \sum_{i=0}^{N-1} a^i \cdot b^i \cdot n'_x(b^i \cdot x) $$

Where `n'_x` is the partial derivative of the base noise. Useful for: 
correctly-shaded terrain, erosion sim, anisotropic noise.

## See Also

- [`../techniques/procedural-noise.md`](../techniques/procedural-noise.md) — Practical recipes.
- [`../techniques/domain-warping.md`](../techniques/domain-warping.md).
- [`../techniques/voronoi-cellular-noise.md`](../techniques/voronoi-cellular-noise.md).
- [Iñigo Quilez Noise Articles](https://iquilezles.org/articles/) — Canonical references.
