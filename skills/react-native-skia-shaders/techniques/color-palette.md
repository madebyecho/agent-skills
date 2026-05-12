# Color Palettes

How to turn a scalar (noise, distance, time) into a beautiful color.
Cosine palettes are the go-to.

## Iñigo Quilez Cosine Palette

```glsl
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}
```

`a` = bias, `b` = amplitude, `c` = frequency, `d` = phase. All `vec3`.

### Recipe Catalog

```glsl
// Vibrant rainbow
palette(t, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0, 0.33, 0.67))

// Pastel
palette(t, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0, 0.10, 0.20))

// Sunset / warm
palette(t, vec3(0.5, 0.5, 0.5), vec3(0.5, 0.5, 0.5), vec3(1.0, 1.0, 1.0), vec3(0.0, 0.10, 0.20))

// Cool blue-purple
palette(t, vec3(0.5, 0.5, 0.5), vec3(0.5, 0.5, 0.5), vec3(1.0, 1.0, 0.5), vec3(0.80, 0.90, 0.30))

// Bright sunburst
palette(t, vec3(0.8, 0.5, 0.4), vec3(0.2, 0.4, 0.2), vec3(2.0, 1.0, 1.0), vec3(0.0, 0.25, 0.25))

// Earthy / autumn
palette(t, vec3(0.5, 0.5, 0.5), vec3(0.5, 0.5, 0.5), vec3(1.0, 0.7, 0.4), vec3(0.0, 0.15, 0.20))
```

[Tool](https://iquilezles.org/articles/palettes) for live-tweaking the
parameters.

## Two-Color Lerp

```glsl
vec3 col = mix(vec3(0.1, 0.3, 0.7), vec3(0.95, 0.6, 0.2), smoothstep(0.0, 1.0, t));
```

The cheap, reliable workhorse. `smoothstep` gives nicer falloff than linear.

## Three-Stop Palette

```glsl
vec3 palette3(float t, vec3 a, vec3 b, vec3 c) {
    if (t < 0.5) return mix(a, b, t * 2.0);
    return mix(b, c, (t - 0.5) * 2.0);
}
```

## HSL / HSV Conversion

```glsl
vec3 hsl2rgb(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return c.z + c.y * (rgb - 0.5) * (1.0 - abs(2.0 * c.z - 1.0));
}

vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return c.z * mix(vec3(1.0), rgb, c.y);
}
```

Useful for hue-rotation animations.

## Oklab (Perceptually Uniform)

For interpolating colors *without muddy midpoints* (the curse of RGB lerp),
do it in Oklab:

```glsl
vec3 linearToOklab(vec3 c) {
    float l = 0.4122214708 * c.r + 0.5363325363 * c.g + 0.0514459929 * c.b;
    float m = 0.2119034982 * c.r + 0.6806995451 * c.g + 0.1073969566 * c.b;
    float s = 0.0883024619 * c.r + 0.2817188376 * c.g + 0.6299787005 * c.b;
    l = pow(l, 1.0/3.0);
    m = pow(m, 1.0/3.0);
    s = pow(s, 1.0/3.0);
    return vec3(
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    );
}

vec3 oklabToLinear(vec3 c) {
    float l_ = c.x + 0.3963377774 * c.y + 0.2158037573 * c.z;
    float m_ = c.x - 0.1055613458 * c.y - 0.0638541728 * c.z;
    float s_ = c.x - 0.0894841775 * c.y - 1.2914855480 * c.z;
    float l = l_ * l_ * l_;
    float m = m_ * m_ * m_;
    float s = s_ * s_ * s_;
    return vec3(
         4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    );
}

vec3 mixOklab(vec3 a, vec3 b, float t) {
    vec3 al = linearToOklab(a);
    vec3 bl = linearToOklab(b);
    return oklabToLinear(mix(al, bl, t));
}
```

Expensive — 2 `pow` per axis. Use sparingly (precompute uniforms for the
endpoints in Oklab on JS side instead, then `oklabToLinear` once at the end).

## Gradient Stops (CSS-Like)

```glsl
vec3 gradient(float t, vec3 c0, vec3 c1, vec3 c2, vec3 c3, vec3 c4) {
    if (t < 0.25) return mix(c0, c1, t * 4.0);
    if (t < 0.50) return mix(c1, c2, (t - 0.25) * 4.0);
    if (t < 0.75) return mix(c2, c3, (t - 0.50) * 4.0);
    return mix(c3, c4, (t - 0.75) * 4.0);
}
```

## Animated Hue

```glsl
vec3 col = hsv2rgb(vec3(fract(time * 0.1 + uv.x * 0.3), 0.8, 0.9));
```

Cycles hue over time. Pair with a slow `smoothstep` to soften transitions.

## Color Grading (After Tone Mapping)

```glsl
// Lift / gamma / gain
vec3 lift = vec3(0.02, 0.0, -0.02);    // shadows shift
vec3 gain = vec3(1.0, 1.0, 1.1);       // highlights gain
float gamma = 1.0;
col = pow(max((col + lift) * gain, 0.0), vec3(1.0 / gamma));
```

## See Also

- [post-processing](post-processing.md) — Tone mapping, vignette.
- [procedural-noise](procedural-noise.md) — Generates the `t` you feed in.
- [image-effects](image-effects.md) — ColorMatrix-based grading.
