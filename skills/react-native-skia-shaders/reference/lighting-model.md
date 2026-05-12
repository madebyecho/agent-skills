# Lighting Models Reference

Derivations for the lighting equations.

## The Rendering Equation (Local)

For a point on a surface with normal `n`, viewed from `v`, lit by lights `lᵢ`:

$$ L_o = L_e + \int (f_r \cdot L_i \cdot \cos\theta) \, d\omega $$

We approximate the integral with direct lights and a constant ambient
term.

## Lambert (Diffuse BRDF)

For an ideal diffuse surface:
$$ f_r = \frac{\rho}{\pi} $$

Where `ρ` is the albedo (reflectance). The diffuse contribution:
$$ L_o^{diff} = \frac{\rho}{\pi} \cdot L_i \cdot \cos\theta = \frac{\rho}{\pi} \cdot L_i \cdot (\vec{n} \cdot \vec{l}) $$

In code:
```glsl
vec3 diffuse = albedo * max(dot(n, l), 0.0);   // ignoring the 1/π factor (folded into light intensity)
```

The 1/π normalization matters for energy conservation in PBR. For
non-physical lighting (Phong, toon), drop it.

## Half-Lambert (Valve)

```glsl
float h = dot(n, l) * 0.5 + 0.5;
float diff = h * h;
```

Wraps light around the back side, then squares to keep the bright peak. No
physical basis, but matches eye expectation for skin / soft materials.

## Blinn-Phong (Specular)

Half-vector:
$$ \vec{h} = \mathrm{normalize}(\vec{l} + \vec{v}) $$

Specular intensity:
$$ I_{spec} = (\vec{n} \cdot \vec{h})^s $$

`s` (shininess) controls highlight sharpness. Energy-conserving variant
includes a normalization factor:
$$ I_{spec} = \frac{s + 8}{8\pi} (\vec{n} \cdot \vec{h})^s $$

In practice (non-PBR), drop the factor.

## Phong (Original — Reflect-Based)

$$ \vec{r} = \mathrm{reflect}(-\vec{l}, \vec{n}) = 2(\vec{n} \cdot \vec{l})\vec{n} - \vec{l} $$
$$ I_{spec} = (\vec{r} \cdot \vec{v})^s $$

Slightly more expensive than Blinn-Phong (compute `r`) and physically less
plausible at grazing angles. Use Blinn-Phong.

## Cook-Torrance (PBR Microfacet)

$$ f_r = \frac{D(\vec{h}) \cdot G(\vec{l}, \vec{v}, \vec{h}) \cdot F(\vec{v}, \vec{h})}{4 (\vec{n} \cdot \vec{l}) (\vec{n} \cdot \vec{v})} $$

Three terms:

### Normal Distribution (D) — GGX / Trowbridge-Reitz

$$ D_{GGX}(h) = \frac{\alpha^2}{\pi ((\vec{n} \cdot \vec{h})^2 (\alpha^2 - 1) + 1)^2} $$

Where `α = roughness²` (Disney convention).

### Geometry (G) — Smith with GGX

$$ G_2(l, v) = G_1(l) \cdot G_1(v) $$

Schlick-GGX approximation:
$$ G_1(v) = \frac{\vec{n} \cdot \vec{v}}{(\vec{n} \cdot \vec{v})(1 - k) + k} $$
$$ k = \frac{(\alpha + 1)^2}{8} $$ (for direct lighting)

### Fresnel (F) — Schlick

$$ F(v, h) = F_0 + (1 - F_0)(1 - \vec{v} \cdot \vec{h})^5 $$

Where `F₀` is the reflectance at normal incidence:
- 0.04 (vec3) for non-metals
- `albedo` for metals

The `metallic` parameter interpolates: `F₀ = mix(vec3(0.04), albedo, metallic)`.

### Combining

```glsl
vec3 spec  = D * G * F / max(4.0 * NdotL * NdotV, 0.001);
vec3 kd    = (1.0 - F) * (1.0 - metallic);    // diffuse weight
vec3 diff  = kd * albedo / 3.14159;
vec3 Lo    = (diff + spec) * NdotL * Li;
```

## Energy Conservation

The diffuse term is downweighted by `(1 - F)` because energy reflected
specularly cannot also contribute to diffuse. Metals have no diffuse
(`kd = 0` when `metallic = 1`).

## Ambient & Indirect

PBR ambient should ideally be a prefiltered environment lookup. On mobile
without an env map, approximate:

```glsl
vec3 ambient = albedo * (0.3 + 0.7 * (n.y * 0.5 + 0.5)) * 0.2;
```

Sky-tinted ambient: bright at top, darker at bottom.

## Subsurface Scattering (Approximation)

For wax / skin / leaves, light wraps around:

```glsl
float wrap = 0.5;
float sss = max(0.0, (dot(n, l) + wrap) / (1.0 + wrap));
```

## Toon Shading

```glsl
float diff = max(dot(n, l), 0.0);
float band = floor(diff * 3.0 + 0.5) / 3.0;
```

Quantize the diffuse into N bands.

## Rim Light

```glsl
float rim = 1.0 - max(dot(n, v), 0.0);
rim = smoothstep(0.5, 0.8, rim);
col += rim * vec3(1.0);
```

Bright halo at silhouette edges — cheap "fresnel-ish" effect.

## Why Gamma Correction Matters

Most albedo / diffuse colors entering shaders are sRGB-encoded (perceptual
space). Lighting math is **linear**:

```glsl
vec3 albedo = pow(albedoSrgb, vec3(2.2));     // sRGB → linear
// ... linear lighting math ...
col = pow(col, vec3(1.0 / 2.2));              // linear → sRGB
```

Without this, dark colors look crushed and bright surfaces wash out.

## See Also

- [`../techniques/lighting-model.md`](../techniques/lighting-model.md) — Practical code.
- [`../techniques/shadow-techniques.md`](../techniques/shadow-techniques.md).
- [`../techniques/ambient-occlusion.md`](../techniques/ambient-occlusion.md).
- [`../techniques/post-processing.md`](../techniques/post-processing.md) — Tone mapping → gamma chain.
