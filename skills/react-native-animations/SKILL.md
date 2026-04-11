---
name: react-native-animations
description: >
  Encodes motion design and animation engineering philosophy for React Native
  apps using Reanimated, Gesture Handler, and Skia. Use when building or
  reviewing mobile animations, gestures, transitions, or interactive UI polish.
  Triggers on animation tasks, micro-interactions, gesture handling, or when
  the user mentions Reanimated, worklets, shared values, Skia, or mobile motion.
license: MIT
metadata:
  author: madebyecho
  version: "1.0.0"
---

# React Native Animations

A philosophy and decision framework for building great motion on React Native. Covers Reanimated (values, worklets, layout animations), Gesture Handler (pan, pinch, composition), and Skia (canvas-driven animation) — the three libraries that make mobile motion feel native in 2026.

This skill is opinionated. It does not cover the legacy `Animated` API, Moti, or Lottie — when those are the right tool, this skill does not apply.

## When to Apply

Reference these guidelines when:
- Building any animation or transition in a React Native or Expo app
- Adding gesture-driven interactions (swipe, drag, pinch, pull-to-refresh)
- Reviewing animation code for performance or polish
- Choosing between Reanimated, Skia, or native views for a motion task
- Deciding easing curves, durations, or spring parameters
- Handling Reduce Motion accessibility settings

## Foundational Philosophy

Three principles underlie every decision in this skill. When in doubt, return to these.

**1. Motion serves the spatial model.** On mobile, animation is not decoration — it is how users understand where content comes from and where it goes. Modals rise from the button that opened them. Drawers slide from the edge they're anchored to. A swipe that dismisses a card moves with the finger until the gesture ends. If motion does not teach the user something about the interface's structure, it should not exist.

**2. The UI thread is sacred.** Every animation that touches the JS thread is a visible stutter waiting to happen. Reanimated worklets, shared values, and native gesture handlers exist for exactly one reason: to run motion at 60–120fps on a thread that never blocks. Any code pattern that forces an animation back to JS is a bug.

**3. Motion should match device physics.** iOS users expect spring-based, slightly overshooting motion with deceleration-dominant curves. Android/Material users expect the "standard curve" — quick acceleration, slow deceleration. Don't ship the same linear tween on both platforms and call it cross-platform.

## Animation Decision Framework

Four questions, in order. Skip any of them and motion becomes noise.

### 1. Should this animate?

| Frequency of interaction | Recommendation |
|--------------------------|----------------|
| 100+ times/day | No animation. Users want instant. |
| Dozens/day | Reduce or remove. Consider scale-only feedback. |
| Occasional | Standard animation. |
| Rare (onboarding, celebration) | Add delight. |

Mobile-specific addition: **Does it serve orientation in the navigation stack?** A push transition teaches "this came from there." A fade teaches nothing spatial. If the answer is "it serves orientation," animate; otherwise default to instant.

### 2. What's the purpose?

Valid reasons to animate on mobile:
- **Spatial continuity** between screens or states
- **Gesture feedback** — the finger is dragging, something should move with it
- **State indication** — loading, success, error, selection
- **Preventing jarring layout shifts** — items appearing in a list, keyboard opening
- **Teaching gesture availability** — bottom sheet preview bounce, swipe affordance

If you cannot name one of these reasons, cut the animation.

### 3. Which easing?

Defaults that work everywhere:

| Use case | Easing | Rationale |
|----------|--------|-----------|
| Entering (mount, appear) | `Easing.out(Easing.cubic)` | Decelerates into place — iOS-feeling |
| Exiting (unmount, dismiss) | `Easing.in(Easing.cubic)` | Accelerates away |
| Moving / morphing | `Easing.inOut(Easing.cubic)` | Material "standard curve" |
| Gesture follow | `withSpring({ damping: 15, stiffness: 150 })` | Physics, not time |
| Infinite loader | `Easing.linear` | The only time linear is acceptable |

Never use `Easing.in` or `Easing.inOut` for mount animations — delayed initial movement feels sluggish.

For custom curves, prefer `cubicBezier(0.23, 1, 0.32, 1)` as an iOS-style entering curve. Material's standard curve is `cubicBezier(0.4, 0, 0.2, 1)`.

See `references/easing-and-timing.md` for the full reference table.

### 4. Which duration?

| Interaction | Duration |
|-------------|----------|
| Button press / scale feedback | 100–160ms |
| Toast, icon toggle, small UI | 150–200ms |
| Navigation push/pop, modal | 250–400ms |
| Drawer, bottom sheet | 300–500ms |
| Onboarding illustration | 500–1000ms |

**Never exceed 500ms for standard navigation.** Beyond that, the user perceives lag, not motion. Spring animations don't have a duration — they have physics, and physics should feel like the device.

## The Reanimated Mental Model

Before writing any animation code, internalize these concepts.

**`useSharedValue`** — a value that lives on the UI thread. Mutations don't trigger React re-renders. It is the atom of Reanimated.

```tsx
const offset = useSharedValue(0);
offset.value = 100; // No re-render. The UI thread sees the new value immediately.
```

**`useAnimatedStyle`** — a worklet that reads shared values and returns a style object. Runs on the UI thread whenever its shared values change.

```tsx
const animatedStyle = useAnimatedStyle(() => ({
  transform: [{ translateX: offset.value }],
}));
```

**`withTiming` / `withSpring`** — animation drivers that return values over time. Assign the return value to a shared value to animate it.

```tsx
offset.value = withSpring(100, { damping: 15, stiffness: 150 });
```

**Worklets** — functions marked with `'worklet'` that run on the UI thread. Gesture callbacks are automatically workletized. To call a JS function from a worklet, wrap it in `runOnJS`.

```tsx
const tap = Gesture.Tap().onEnd(() => {
  'worklet';
  runOnJS(logAnalytics)('tap');
});
```

**Layout animations** — declarative mount/unmount and reorder animations. The easiest path to polish.

```tsx
<Animated.View entering={FadeIn.duration(300)} exiting={FadeOut} />
```

**`Animated.View` is not `View`.** Regular `View` doesn't participate in the worklet render pipeline. Every component that consumes an animated style must be an `Animated.*` component.

**Critical bug to avoid:** mutating a shared value inside `useAnimatedStyle` causes undefined behavior — potentially an infinite loop. Shared values are written from event handlers, effects, or gesture callbacks — never from inside the style worklet.

See `references/reanimated-patterns.md` for API recipes.

## Gesture-Driven Animation

Gesture Handler v2 is a declarative API composed with Reanimated. This is where mobile motion becomes mobile.

**Core gestures:** `Gesture.Pan()`, `Gesture.Pinch()`, `Gesture.Tap()`, `Gesture.LongPress()`, `Gesture.Rotation()`, `Gesture.Fling()`.

**Composition:**
- `Gesture.Simultaneous(a, b)` — both active at once (pinch + pan in a photo viewer)
- `Gesture.Race(a, b)` — first to activate wins
- `Gesture.Exclusive(a, b)` — one blocks the others

**Canonical pan-to-dismiss pattern:**

```tsx
const translateY = useSharedValue(0);

const pan = Gesture.Pan()
  .onUpdate((e) => {
    translateY.value = Math.max(0, e.translationY);
  })
  .onEnd((e) => {
    const shouldDismiss = translateY.value > 100 || e.velocityY > 500;
    if (shouldDismiss) {
      translateY.value = withTiming(SCREEN_HEIGHT, { duration: 250 });
      runOnJS(onDismiss)();
    } else {
      translateY.value = withSpring(0, { damping: 15, stiffness: 150 });
    }
  });
```

Three things to notice:
1. **Velocity matters.** A fast flick should dismiss even before the threshold distance. Always read `event.velocityX` / `velocityY` in `onEnd`.
2. **Springs for snap-back.** Rubber-band-feeling returns use `withSpring`, not `withTiming`.
3. **`runOnJS` for commit.** Navigation, haptics, and analytics all cross the thread boundary via `runOnJS`.

**Haptic coordination:** fire `Haptics.impactAsync` via `runOnJS` at gesture commit points (activation, snap, dismiss). Never inside `onUpdate` — you'll haptic every frame.

**Interruption:** spring animations must be interruptible. If a new pan starts mid-snap-back, the shared value is simply reassigned and `withSpring` takes over from the current velocity. Never queue animations with callbacks when you could use `withSequence`.

See `references/gesture-handler-patterns.md` for composition recipes and the full pinch+pan+rotate photo viewer example.

## Layout Animations & List Transitions

The declarative path — use these first, before reaching for custom worklets.

**Mount/unmount animations:**
```tsx
<Animated.View entering={FadeIn.duration(300)} exiting={FadeOut.duration(200)} />
<Animated.View entering={SlideInRight.springify().damping(15)} exiting={SlideOutLeft} />
```

**List reordering:**
```tsx
<Animated.FlatList
  data={data}
  renderItem={renderItem}
  itemLayoutAnimation={LinearTransition.springify()}
/>
```

**Modifiers:** `.duration(ms)`, `.easing(Easing.out(Easing.cubic))`, `.springify()`, `.damping(15)`, `.delay(100)`, `.withCallback(cb)`, `.reduceMotion(ReduceMotion.System)`.

**Shared element transitions** (Reanimated 3+):
```tsx
<Animated.Image sharedTransitionTag="profile-photo" />
```

Shared tags on a source and destination screen automatically animate geometry between them. Requires the navigator to use the native stack.

## Skia for Advanced Motion

Reach for `@shopify/react-native-skia` when RN views can't do the job:

- Charts, graphs, paths, Bézier morphing
- Shaders, blur, color filters, blend modes
- Particle systems, game loops
- Custom gradients and masks
- Animated GIFs with frame control (`useAnimatedImageValue`)

**Interop is seamless in modern Skia + Reanimated.** Skia components accept shared values and derived values directly — no separate `useValue` hook needed:

```tsx
import { Canvas, Circle } from "@shopify/react-native-skia";
import { useDerivedValue, useSharedValue, withRepeat, withTiming } from "react-native-reanimated";

const r = useSharedValue(0);
useEffect(() => {
  r.value = withRepeat(withTiming(85, { duration: 1000 }), -1);
}, []);

return (
  <Canvas style={{ flex: 1 }}>
    <Circle cx={128} cy={128} r={r} color="cyan" />
  </Canvas>
);
```

**Time-based animation:** `useClock()` returns a shared value of elapsed milliseconds. Pipe it through `useDerivedValue` for trigonometric or procedural motion.

**Path interpolation:** `usePathInterpolation(progress, [0, 0.5, 1], [pathA, pathB, pathC])` morphs SVG paths as a shared-value progress moves from 0 to 1.

**When not to use Skia:** box-model UI (cards, lists, buttons). Skia runs in its own renderer — you lose accessibility tree integration, native text rendering, and standard touch handling. Use it for the 5% of your app where Reanimated-on-views isn't enough.

See `references/skia-animation-patterns.md` for canvas recipes.

## Performance Rules

Non-negotiables. Violating any of these means a dropped frame somewhere.

1. **Drive animations through shared values, not state.** Never `setState` in an animation loop.
2. **Prefer `transform` and `opacity`.** Reanimated *can* animate `width`, `height`, and `top` off-thread (unlike the legacy Animated API), but transforms are still cheaper and never trigger layout reflow of siblings.
3. **Never mutate a shared value inside `useAnimatedStyle`.** Infinite loop / undefined behavior.
4. **Don't `setState` in `onScroll` or `onGestureEvent`.** Use `useAnimatedScrollHandler` and gesture worklets. When you need JS state, use `useAnimatedReaction` with `runOnJS`.
5. **Gate hover/press state by platform.** `hover` doesn't exist on touch. Use `Pressable` states, gesture handlers, or `scale` feedback.
6. **Fire haptics at commit points, not per frame.** Wrap `Haptics.impactAsync` in `runOnJS` and call it in `onEnd` or threshold-crossing branches.
7. **Profile on mid-tier Android, not the iOS simulator.** The simulator lies. A real Pixel 6a or Samsung A-series tells the truth.
8. **Watch the UI thread frame rate, not just JS.** Perf Monitor shows both. If the UI thread is dropping frames, Reanimated isn't saving you — there's layout or paint work hiding somewhere.

See `assets/performance-checklist.md` for the pre-ship verification list.

## Accessibility: Reduce Motion

This is not a footnote. Users with vestibular disorders enable Reduce Motion to avoid nausea — animations that ignore this setting are a physical accessibility failure.

**`useReducedMotion()`** (from `react-native-reanimated`) — synchronous boolean. Preferred over `AccessibilityInfo.isReduceMotionEnabled()` because it works in worklets and doesn't require async.

**`ReducedMotionConfig`** — app-wide component. Place it at the root of the app to globally disable animations when the OS setting is on.

```tsx
import { ReducedMotionConfig, ReduceMotion } from 'react-native-reanimated';

<ReducedMotionConfig mode={ReduceMotion.System} />
```

**`.reduceMotion()` modifier** — per-animation override. Available on all `withTiming`, `withSpring`, and layout animation builders.

```tsx
<Animated.View
  entering={SlideInRight.duration(300).reduceMotion(ReduceMotion.System)}
/>
```

**The decision rule when Reduce Motion is on:**
- **Keep** opacity, color, and fade animations — they convey state without vestibular impact.
- **Remove** translate, scale, rotate, and parallax — collapse to instant or fade.

Example: a slide-up modal becomes a fade-in when Reduce Motion is on. The user still sees the modal appear; they just don't see it travel.

See `references/accessibility.md` for the full matrix. For audit-mode detection of missing reduce-motion checks, cross-reference the `react-native-accessibility` skill's `p2-reduce-motion-ignored` rule.

## Component Patterns

The mobile equivalent of Emil Kowalski's "button responsiveness" section. Lift these directly.

**Pressable scale feedback** (the 160ms "alive" feel):
```tsx
const scale = useSharedValue(1);
const animatedStyle = useAnimatedStyle(() => ({
  transform: [{ scale: scale.value }],
}));

<Pressable
  onPressIn={() => { scale.value = withSpring(0.97, { damping: 20, stiffness: 400 }); }}
  onPressOut={() => { scale.value = withSpring(1, { damping: 20, stiffness: 400 }); }}
>
  <Animated.View style={[styles.button, animatedStyle]} />
</Pressable>
```

**Toast / snackbar:** `entering={SlideInDown.springify().damping(18)}` + `exiting={SlideOutDown.duration(200)}`. Never exceed 300ms on either side.

**Bottom sheet snap:** pan gesture + `withSpring` with velocity: `translateY.value = withSpring(snapPoint, { velocity: event.velocityY, damping: 20, stiffness: 150 })`. Snap points at 0, 0.5, 1 of screen height.

**Pull-to-refresh:** `useAnimatedScrollHandler` reads `event.contentOffset.y`, drives a `useSharedValue` for rubber-band overscroll, fires a refresh via `runOnJS` at threshold.

**Skeleton shimmer:** `withRepeat(withTiming(1, { duration: 1200 }), -1)` drives a `translateX` on a gradient overlay. Skia gives the nicest gradient; Reanimated-on-view works for simpler skeletons.

**Hero / shared element:** `sharedTransitionTag="id"` on source and destination screens. Requires a native stack navigator.

## Anti-Patterns

Short, punchy, often-seen, always wrong.

- **Using the legacy `Animated` API for interactive elements.** It's JS-thread-driven. Use Reanimated.
- **`setState` inside `onScroll` or `onGestureEvent`.** Use worklets + `useAnimatedReaction`.
- **Animating `marginTop` or `top` instead of `translateY`.** Triggers layout reflow.
- **Forgetting the `'worklet'` directive on callbacks passed to gestures.** They run on JS and stutter.
- **Chaining animations with `withTiming(...).then(...)`-style callbacks** when `withSequence` exists.
- **Mutating shared values inside `useAnimatedStyle`.** Undefined behavior.
- **Ignoring `useReducedMotion`.** Physical accessibility failure.
- **Using `LayoutAnimation` from core React Native.** It's JS-thread-driven and uneven across platforms. Use Reanimated layout animations instead.
- **Reaching for Skia for a button press.** Skia is for canvas work, not UI kit polish.
- **Driving a Reanimated animation from a React `useEffect` that depends on a changing prop** without reading from a shared value. You're re-creating the animation every render.

## Review Format

When reviewing existing animation code, output a **markdown table with Before | After | Why columns.** Never use separate "Before:" and "After:" lines — the table makes the tradeoff visible at a glance.

Example:

| Before | After | Why |
|--------|-------|-----|
| `top: withTiming(100)` | `transform: [{ translateY: withTiming(100) }]` | `top` triggers layout; `translateY` is compositor-only |
| `setState({ x })` in `onUpdate` | `sharedValue.value = e.translationX` | `setState` crosses to JS thread every frame |
| `Animated.timing(...)` (legacy) | `withTiming(...)` (Reanimated) | Legacy API runs on JS thread |

## External Resources

- [Reanimated docs](https://docs.swmansion.com/react-native-reanimated) — canonical API reference
- [Gesture Handler docs](https://docs.swmansion.com/react-native-gesture-handler) — gesture composition and v2 API
- [React Native Skia docs](https://shopify.github.io/react-native-skia) — canvas, shaders, animated images
- [Apple HIG: Motion](https://developer.apple.com/design/human-interface-guidelines/motion) — iOS motion principles
- [Material Design Motion](https://m3.material.io/styles/motion/overview) — Android motion specs and tokens
- [Emil Kowalski's animations.dev](https://animations.dev) — web motion theory that translates to mobile
- [React Native Reanimated Accessibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility/) — Reduce Motion integration

## Supporting Files

Loaded on-demand during execution:

- `references/reanimated-patterns.md` — Full Reanimated API recipes (shared values, hooks, animation drivers, interpolation)
- `references/gesture-handler-patterns.md` — Gesture composition recipes including pan+pinch+rotate viewer
- `references/skia-animation-patterns.md` — Skia canvas animation patterns with Reanimated interop
- `references/easing-and-timing.md` — Consolidated easing curves, spring presets, duration tokens
- `references/accessibility.md` — Reduce Motion integration patterns and decision matrix
- `assets/decision-flowchart.md` — Quick-reference decision flowchart
- `assets/performance-checklist.md` — Pre-ship performance verification checklist
