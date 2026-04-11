# Easing and Timing Reference

Consolidated reference for Reanimated easing curves, spring presets, platform motion tokens, and duration ranges. Use this as a lookup table when the SKILL.md decision framework points you here.

## Reanimated Built-In Easing

From `import { Easing } from 'react-native-reanimated'`:

| Curve | Feel | Use For |
|-------|------|---------|
| `Easing.linear` | Constant speed | Infinite loops, spinners |
| `Easing.quad` / `Easing.cubic` / `Easing.quart` / `Easing.quint` | Polynomial acceleration | Base curves for `.in()`, `.out()`, `.inOut()` |
| `Easing.sin` | Gentle sinusoidal | Subtle, non-linear motion |
| `Easing.exp` | Exponential | Very aggressive acceleration/deceleration |
| `Easing.circle` | Circular | Wheel-like motion |
| `Easing.back(s)` | Slight overshoot at end | Playful entrances (s = 1.5–2) |
| `Easing.elastic(n)` | Elastic bounce | Very loud, rarely appropriate |
| `Easing.bounce` | Multi-bounce landing | Cartoon-like, rarely appropriate |
| `Easing.bezier(x1, y1, x2, y2)` | Custom cubic Bézier | Precise curves from design specs |

**Directional modifiers** (wrap any of the above):
- `Easing.in(curve)` — starts slow, ends fast (exit-like)
- `Easing.out(curve)` — starts fast, ends slow (enter-like, iOS-native feel)
- `Easing.inOut(curve)` — slow-fast-slow (Material "standard")

## Recommended Defaults

| Use case | Easing | Duration |
|----------|--------|----------|
| Entering (mount, appear, drawer open) | `Easing.out(Easing.cubic)` | 250–300ms |
| Exiting (unmount, dismiss, drawer close) | `Easing.in(Easing.cubic)` | 200ms |
| Moving / morphing / tween between states | `Easing.inOut(Easing.cubic)` | 250ms |
| Scroll parallax / continuous | `Easing.linear` | N/A |
| Gesture follow | `withSpring` (no easing) | N/A |
| Celebration / delight | `Easing.out(Easing.back(1.5))` | 400–600ms |

## Custom Cubic Bézier Curves

| Curve | Coordinates | Feel |
|-------|-------------|------|
| iOS Standard Ease | `cubicBezier(0.23, 1, 0.32, 1)` | Fast start, long gentle decel — canonical iOS motion |
| Material Standard | `cubicBezier(0.4, 0, 0.2, 1)` | Balanced accel/decel for moving elements |
| Material Decelerate | `cubicBezier(0, 0, 0.2, 1)` | Incoming elements (fades, slides in) |
| Material Accelerate | `cubicBezier(0.4, 0, 1, 1)` | Outgoing elements (fades, slides out) |
| Sharp | `cubicBezier(0.4, 0, 0.6, 1)` | Temporary elements (bottom sheets, chips) |

Use via:
```tsx
import { Easing } from 'react-native-reanimated';

easing: Easing.bezier(0.23, 1, 0.32, 1)
```

Or for CSS-style animations (Reanimated 3.4+):
```tsx
import { cubicBezier } from 'react-native-reanimated';

animationTimingFunction: cubicBezier(0.23, 1, 0.32, 1)
```

## Spring Presets

`withSpring(toValue, { damping, mass, stiffness, velocity })`

| Name | Config | Feel | Use For |
|------|--------|------|---------|
| iOS Native | `{ damping: 15, stiffness: 150 }` | Slight overshoot, natural settle | Default for most interactions |
| Snappy | `{ damping: 20, stiffness: 300 }` | Minimal oscillation, quick | Modals, sheets, snap-to-grid |
| Stiff | `{ damping: 20, stiffness: 400 }` | Tight, immediate | Scale feedback on press |
| Bouncy | `{ damping: 8, stiffness: 150 }` | Pronounced overshoot | Playful celebration |
| Gentle | `{ damping: 18, stiffness: 100 }` | Slow, soft arrival | Drawers, large modals |
| Wobbly | `{ damping: 6, stiffness: 180 }` | Elastic, multiple overshoots | Avoid in serious apps |

**Velocity matters.** Always pass gesture velocity to `withSpring` when releasing a drag:
```tsx
translateY.value = withSpring(snapTarget, {
  velocity: event.velocityY,
  damping: 15,
  stiffness: 150,
});
```

## Duration Tokens by Interaction

| Interaction | Range | Sweet Spot |
|-------------|-------|------------|
| Ripple, press highlight | 80–120ms | 100ms |
| Button scale feedback | 100–160ms | 140ms |
| Icon toggle, checkbox | 150–200ms | 180ms |
| Toast / snackbar in | 200–300ms | 250ms |
| Toast / snackbar out | 150–200ms | 180ms |
| Tooltip / popover | 150–250ms | 200ms |
| Tab switch | 200–300ms | 250ms |
| Modal open | 250–350ms | 300ms |
| Modal close | 200–300ms | 250ms |
| Navigation push/pop | 300–400ms | 350ms |
| Drawer open | 300–500ms | 400ms |
| Bottom sheet | 300–500ms | 400ms |
| Onboarding illustration | 500–1000ms | 700ms |
| Launch screen | 500–2000ms | ~1s |

**Ceilings to respect:**
- Never exceed **500ms** for navigation — users perceive lag.
- Never exceed **300ms** for inline UI (toasts, toggles, hovers).
- Never exceed **160ms** for tactile feedback (press, tap) — it should feel simultaneous with the touch.

## iOS vs Android Motion Expectations

| | iOS | Android / Material |
|---|-----|-----|
| Default easing for movement | Spring-based, slight overshoot | Standard cubic (accel/decel) |
| Default duration | 300–400ms (feels unhurried) | 200–300ms (feels efficient) |
| Navigation style | Push from right with parallax | Slide up with fade |
| Modal style | Slide up from bottom, stays partially visible behind | Full-screen rise or scrim-only |
| Ripple feedback | None (scale + opacity instead) | Touch ripple is the standard |

When using a cross-platform library, prefer spring defaults on iOS and `cubicBezier(0.4, 0, 0.2, 1)` on Android — or just use springs everywhere and accept that Android feels slightly more "iOS" (most users don't mind).

## Easing Decision Shortcut

If you're not sure which curve to use, ask:

1. **Is it entering?** → `Easing.out(Easing.cubic)` or `cubicBezier(0.23, 1, 0.32, 1)`
2. **Is it exiting?** → `Easing.in(Easing.cubic)`
3. **Is it morphing?** → `Easing.inOut(Easing.cubic)` or `cubicBezier(0.4, 0, 0.2, 1)`
4. **Is it gesture-driven?** → `withSpring({ damping: 15, stiffness: 150 })`
5. **Is it infinite?** → `Easing.linear`
6. **None of the above?** → `Easing.out(Easing.cubic)` is a safe default.

## Never

- `Easing.linear` for UI transitions (other than infinite loops)
- `Easing.bounce` for anything shipping to users
- `Easing.in` for mount animations — the delayed start feels broken
- Fixed durations for gesture-released animations — always use `withSpring` with velocity
- Different easing curves across screens for the same interaction — cohesion matters more than novelty
