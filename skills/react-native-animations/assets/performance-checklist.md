# Animation Performance Checklist

Pre-ship verification list for React Native motion. Walk through before merging any PR that touches animation or gestures.

## Architecture

- [ ] Every animation uses `useSharedValue` + `useAnimatedStyle` (or layout animations). No `Animated.Value` from the legacy API.
- [ ] Every animated component is an `Animated.*` component (`Animated.View`, `Animated.FlatList`, `Animated.ScrollView`), not the plain version.
- [ ] No shared value is mutated inside `useAnimatedStyle`. Mutations happen in event handlers, effects, or gesture callbacks.
- [ ] No `setState` is called inside `onScroll`, `onGestureEvent`, or any per-frame callback. State updates that cross to JS use `useAnimatedReaction` + `runOnJS` at threshold crossings only.
- [ ] Gesture callbacks use the v2 `Gesture` API (`Gesture.Pan()`, etc.), which is automatically workletized. No manual `'worklet'` directives on inline gesture handlers.
- [ ] Shared values are created at the top of the component, never inside effects or callbacks.

## Properties Animated

- [ ] Movement animations use `transform: [{ translateX }, { translateY }]` — not `top`, `left`, `marginTop`, or `marginLeft`.
- [ ] Size changes use `transform: [{ scale }]` where visually equivalent — reserve `width`/`height` for cases where scale distorts children.
- [ ] Rotation uses `transform: [{ rotate: '...' }]`.
- [ ] Opacity changes use the `opacity` property directly (Reanimated handles this off-thread).
- [ ] Color transitions use `interpolateColor` inside `useAnimatedStyle`.

## Gestures

- [ ] `GestureHandlerRootView` wraps the app root.
- [ ] Pan gestures save the starting value in `onStart` and add `e.translationX/Y` in `onUpdate` — not the cumulative translation.
- [ ] `onEnd` reads `event.velocityX` / `velocityY` and passes it to `withSpring` for momentum-aware snap-back.
- [ ] `runOnJS` is used only for truly non-worklet JS (navigation, haptics, analytics, async) — not for every callback.
- [ ] Haptic feedback fires on threshold crossings or commit points, not inside `onUpdate`.
- [ ] Gestures that can compose (pan + pinch in a photo viewer) are explicitly composed with `Gesture.Simultaneous`.
- [ ] Gestures that disambiguate (single vs double tap) use `Gesture.Exclusive`.

## Timing and Easing

- [ ] No `Easing.linear` on UI transitions (other than infinite loops).
- [ ] No `Easing.in` on mount animations — `Easing.out(Easing.cubic)` is the mount default.
- [ ] No duration exceeds the ceiling for its category (160ms tactile, 300ms inline, 500ms navigational).
- [ ] Spring animations on gesture release include a `velocity` from the gesture event.
- [ ] No `Easing.bounce` or extreme `Easing.elastic` in production code.

## Layout Animations

- [ ] List reordering uses `itemLayoutAnimation={LinearTransition}` on `Animated.FlatList`, not manual translate animations.
- [ ] Mount/unmount uses `entering={FadeIn}` / `exiting={FadeOut}` (or similar) rather than manual effect-driven opacity.
- [ ] Layout animations include `.duration()` or `.springify()` modifiers that match the rest of the app's motion vocabulary.

## Skia (if used)

- [ ] Skia is only used for canvas work (charts, shaders, paths, particles, blur, animated images) — not for regular UI like buttons or lists.
- [ ] Skia components are driven by Reanimated shared values and `useDerivedValue` directly — no legacy `useValue` / `useComputedValue`.
- [ ] Text inside a Skia canvas is only used where native `<Text>` is insufficient — otherwise text is rendered outside the canvas for accessibility.
- [ ] The canvas's React tree is stable — changes come through shared values, not re-renders.

## Accessibility

- [ ] `<ReducedMotionConfig mode={ReduceMotion.System} />` is mounted at the app root.
- [ ] Every movement animation (translate, scale, rotate, parallax) either:
  - Uses the `.reduceMotion(ReduceMotion.System)` modifier, **or**
  - Explicitly checks `useReducedMotion()` and falls back to fade or instant.
- [ ] Infinite animations (loaders, shimmers, pulsing) check `useReducedMotion()` and render a static frame when enabled.
- [ ] Testing with Reduce Motion enabled on the device confirms that:
  - All functionality still works
  - State changes still communicate through opacity/color
  - No vestibular motion (slide, scale, rotate, parallax) is visible

## Profiling

- [ ] The animation has been observed on a mid-tier Android device (Pixel 6a, Samsung A-series, or similar), not only iOS simulator or a flagship device.
- [ ] React Native's Perf Monitor is enabled during testing and shows:
  - JS frame rate stable at 60fps (or 120 on ProMotion)
  - UI thread frame rate stable at 60fps (or 120 on ProMotion)
  - No red frame-drop bars during gesture or transition
- [ ] Flipper / Reanimated DevTools (or Hermes sampling profiler) has been used to confirm that no worklet is accidentally running on JS.
- [ ] Under artificial JS load (e.g., a busy `setInterval` in the background), the animation still runs smoothly — this is the core Reanimated guarantee and should be verified, not assumed.

## Cross-Platform Smoke Test

- [ ] Tested on iOS, at least on the latest iPhone simulator and one real device
- [ ] Tested on Android, at least on a mid-tier real device
- [ ] Tested with Dark Mode if colors are animated
- [ ] Tested with Dynamic Type / Font Scale at 200% — layout doesn't break during animation
- [ ] Tested with VoiceOver / TalkBack running — gestures still work and animations don't interfere with focus

## Red Flags During Review

If you see any of these in a PR, block the merge:

- `setState` inside a scroll handler, animation callback, or gesture callback
- `Animated.Value` or `Animated.timing` from the legacy API
- `LayoutAnimation.configureNext(...)` (use Reanimated layout animations)
- Animation durations > 500ms for standard navigation
- Missing `'worklet'` directive on a non-gesture callback passed to a worklet context
- A shared value mutation inside `useAnimatedStyle`
- `runOnJS` called inside `onUpdate` or `onScroll`
- No `useReducedMotion()` check on a translate/scale/rotate animation
- A Skia canvas rendering regular UI kit components (buttons, lists)

## The Ship-It Test

Ask one question: **"If Reanimated wasn't doing its job, would this animation still feel smooth?"** If the answer is no — the UI thread isolation is doing the work, which is correct. If the answer is yes — you probably don't need the animation at all.
