# Animation Decision Flowchart

A one-page decision tree for motion questions. Walk through top to bottom.

## Step 1 — Should this animate at all?

```
How often does this interaction happen?

 100+ times per day ─────────▶  Do NOT animate. Instant is better.
                                (Send/submit buttons, list rows, toggles)

 Dozens per day ─────────────▶  Reduce to the minimum.
                                (Scale feedback only — no entering/exiting)

 Occasional ─────────────────▶  Standard animation.
                                (Modals, drawers, navigation, tabs)

 Rare (onboarding, launch) ──▶  Add delight.
                                (Celebration, full transitions, illustrations)
```

**Extra mobile check:** Does it serve orientation in the navigation stack? If yes → animate. If no → lean toward instant.

## Step 2 — What's the purpose?

If you can answer one of these, proceed. If you can't, cut the animation.

- [ ] **Spatial continuity** — teaches the user where content came from or went to
- [ ] **Gesture feedback** — the finger is dragging, something must follow
- [ ] **State indication** — loading, success, error, selection
- [ ] **Layout prevention** — items appearing/disappearing in a list without jarring shifts
- [ ] **Gesture affordance** — teaching that something is swipeable or draggable

## Step 3 — Which easing?

```
What kind of motion is this?

 Entering / appearing ────────▶  Easing.out(Easing.cubic)
                                  or cubicBezier(0.23, 1, 0.32, 1)

 Exiting / dismissing ────────▶  Easing.in(Easing.cubic)

 Moving / morphing between ───▶  Easing.inOut(Easing.cubic)
 two static states              or cubicBezier(0.4, 0, 0.2, 1)

 Gesture release ─────────────▶  withSpring({ damping: 15, stiffness: 150 })
                                  + velocity from the gesture end event

 Infinite loop ───────────────▶  Easing.linear (only case it's acceptable)

 Celebration / delight ───────▶  Easing.out(Easing.back(1.5))
```

**Never:**
- `Easing.in` for mount animations (delayed start feels sluggish)
- `Easing.bounce` in production
- Fixed `withTiming` for gesture releases (lose the velocity)

## Step 4 — How long?

```
What is this animation doing?

 Press / tap feedback ────────▶  100–160ms
 Icon toggle / checkbox ──────▶  150–200ms
 Toast / snackbar ────────────▶  200–300ms
 Tooltip / popover ───────────▶  150–250ms
 Tab switch ──────────────────▶  200–300ms
 Modal open ──────────────────▶  250–350ms
 Navigation push/pop ─────────▶  300–400ms
 Drawer / bottom sheet ───────▶  300–500ms
 Onboarding illustration ─────▶  500–1000ms
```

**Hard ceilings:**
- Nothing inline exceeds **300ms**
- Nothing navigational exceeds **500ms**
- Nothing tactile exceeds **160ms**

## Step 5 — Which library primitive?

```
What are you building?

 Mount / unmount / reorder ────▶  Layout animations (entering, exiting,
                                   LinearTransition)

 Gesture-driven movement ──────▶  Gesture Handler v2 + shared values
                                   + withSpring on release

 Scroll-driven interpolation ──▶  useAnimatedScrollHandler
                                   + interpolate / interpolateColor

 Imperative triggered (effect) ▶  useSharedValue + withTiming/Spring
                                   in a useEffect

 Canvas / shader / path ───────▶  @shopify/react-native-skia
                                   driven by Reanimated shared values

 Shared element between routes▶  sharedTransitionTag (Reanimated 3+)
```

## Step 6 — Reduce Motion check

- [ ] If the animation translates, scales, rotates, or parallaxes → wrap it with a `useReducedMotion()` check or a `.reduceMotion(ReduceMotion.System)` modifier
- [ ] If the animation is pure opacity/color → no check needed, it's safe
- [ ] If the animation is infinite → stop it or render a static frame when `useReducedMotion()` is true
- [ ] Mount `<ReducedMotionConfig mode={ReduceMotion.System} />` at the app root as a safety net

## Step 7 — Performance self-check

Before shipping:
- [ ] The animation drives through a shared value, not `setState`
- [ ] The animated style touches only `transform` and `opacity` (or has a very good reason not to)
- [ ] The animated component is `Animated.View`, not `View`
- [ ] Gesture callbacks don't call `setState` or non-worklet JS functions (except via `runOnJS` at commit points)
- [ ] The animation is tested on a real mid-tier Android device, not just the iOS simulator

## The One-Sentence Summary

If you can't answer "why is this animation here, what easing am I using, how long is it, and what does it do under Reduce Motion?" — you're not ready to ship the animation.
