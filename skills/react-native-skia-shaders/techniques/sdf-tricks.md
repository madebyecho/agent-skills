# SDF Tricks

Single-line transformations of an SDF value that produce useful visuals:
hollow shells, onion layers, concentric edges, outlines, bumps.

## Onion / Hollow Shell

Replace the solid interior with a thin shell:

```glsl
d = abs(d) - thickness;
```

A sphere becomes a thin spherical shell. A box becomes an empty box.

For multiple concentric shells:
```glsl
d = abs(abs(d) - r1) - r2;       // two layers
```

## Layered / Banded Outlines

Visualize SDF contours:

```glsl
float bands = abs(fract(d * 10.0) - 0.5);    // tight rings every 0.1 units
```

For glowing rings:
```glsl
float glow = exp(-50.0 * abs(fract(d * 10.0) - 0.5));
col += vec3(0.5, 0.7, 1.0) * glow;
```

## Hollow Out (Engrave)

Carve a thin groove from a shape:

```glsl
float d = sdSphere(p, 0.5);
float groove = abs(d - 0.0) - 0.02;   // narrow band at the surface
```

## Round Off Sharp Edges

Subtract from inside, add to outside ≡ Minkowski sum with a sphere:

```glsl
float dRound = d - radius;            // rounds edges by `radius`
```

This works in 2D (`vec2`) and 3D (`vec3`).

## Bevels / Chamfers

```glsl
// Polygon: combine with a circular bevel
float bevel = max(d, length(p) - r);
```

## Bounding-Volume Acceleration

Skip detailed SDF when far from a shape:

```glsl
float map(vec3 p) {
    float bound = length(p) - 2.0;     // bounding sphere
    if (bound > 0.5) return bound;      // outside bound → no detail needed
    return detailedSDF(p);
}
```

In ray-march loops, this skips evaluating expensive `map` until close to
geometry. Big speedup for complex scenes.

## Debug Visualization

Show SDF as concentric bands plus zero-crossing:

```glsl
vec3 dbg = (d > 0.0 ? vec3(0.9, 0.6, 0.3) : vec3(0.4, 0.7, 0.85));
dbg *= 0.8 + 0.2 * cos(150.0 * d);            // tight rings
dbg = mix(dbg, vec3(1.0), 1.0 - smoothstep(0.0, 0.01, abs(d)));
return vec4(dbg, 1.0);
```

Perfect for verifying your SDF is correct — every shape should be inside
the saturated region, every band concentric, the zero-crossing crisp.

## Smooth-Step Edges

For SDF-to-color anti-aliasing:

```glsl
float aa = 1.5 / resolution.y;
float alpha = 1.0 - smoothstep(-aa, aa, d);
```

See [anti-aliasing](anti-aliasing.md) for more on `aa` width.

## Displacement (Bumpy Surface)

Add a small noise on top of an SDF:

```glsl
float d = sdSphere(p, 0.5) + 0.03 * sin(15.0 * p.x) * sin(15.0 * p.y) * sin(15.0 * p.z);
```

Note: the result is no longer a true SDF. In ray-march loops, undershoot
steps: `t += d * 0.7;`. Or limit displacement amplitude.

## Inflate / Deflate

Uniform scale of the iso-value:

```glsl
d -= inflation;     // grow outward by `inflation`
```

Useful for "morphing into a bigger version" animations.

## Two-Color SDF Render

```glsl
vec3 inColor  = vec3(0.95, 0.5, 0.3);
vec3 outColor = vec3(0.1, 0.2, 0.5);
vec3 col = mix(inColor, outColor, smoothstep(-aa, aa, d));
```

## See Also

- [sdf-2d](sdf-2d.md) / [sdf-3d](sdf-3d.md) — Base primitives.
- [csg-boolean-operations](csg-boolean-operations.md) — Combining shapes.
- [anti-aliasing](anti-aliasing.md) — Smooth edges.
