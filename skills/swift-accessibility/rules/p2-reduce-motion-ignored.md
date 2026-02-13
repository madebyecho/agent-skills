---
title: Animations Ignore Reduce Motion Setting
priority: P2
impact: MEDIUM
frameworks: SwiftUI, UIKit
tags: reduce-motion, animation, vestibular, wcag
---

## Animations Ignore Reduce Motion Setting

**Priority: P2 (MEDIUM)**

Users with vestibular disorders or motion sensitivity enable Reduce Motion to avoid nausea, dizziness, and headaches. Apps must check this setting and replace complex animations (parallax, spinning, zooming, multi-axis movement) with simple alternatives (fades, opacity changes, instant transitions).

### Detection

**SwiftUI:**
```
# Animations without Reduce Motion check
grep -n '\.animation(\|withAnimation\|\.transition(' *.swift
# Flag if no @Environment(\.accessibilityReduceMotion) or UIAccessibility.isReduceMotionEnabled check nearby

# Parallax effects
grep -n '\.rotation3DEffect\|\.scaleEffect.*animation\|GeometryReader.*offset' *.swift
```

**UIKit:**
```
grep -n 'UIView.animate\|UIViewPropertyAnimator\|CABasicAnimation\|CAKeyframeAnimation' *.swift
# Flag if no UIAccessibility.isReduceMotionEnabled check guards the animation

grep -n '\.parallaxEffect\|UIDynamicAnimator\|UIInterpolatingMotionEffect' *.swift
```

### Fix Logic

1. Identify all animations, transitions, and motion effects
2. **Decorative animations** → disable entirely when Reduce Motion is enabled
3. **Meaningful animations** → replace with simple fades, dissolves, or instant changes
4. SwiftUI: Read `@Environment(\.accessibilityReduceMotion)` and conditionally apply
5. UIKit: Check `UIAccessibility.isReduceMotionEnabled` before animating
6. Never remove functionality — only change the visual transition

### SwiftUI Before/After

**Before:**
```swift
struct CardView: View {
    @State private var isVisible = false

    var body: some View {
        ContentView()
            .scaleEffect(isVisible ? 1 : 0.5)
            .opacity(isVisible ? 1 : 0)
            .animation(.spring(response: 0.6, dampingFraction: 0.7), value: isVisible)
    }
}

struct ParallaxHeader: View {
    var body: some View {
        GeometryReader { geo in
            Image("header")
                .offset(y: geo.frame(in: .global).minY / 2)
        }
    }
}
```

**After:**
```swift
struct CardView: View {
    @State private var isVisible = false
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        ContentView()
            .scaleEffect(isVisible ? 1 : (reduceMotion ? 1 : 0.5))
            .opacity(isVisible ? 1 : 0)
            .animation(reduceMotion ? .none : .spring(response: 0.6, dampingFraction: 0.7), value: isVisible)
    }
}

struct ParallaxHeader: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        GeometryReader { geo in
            Image("header")
                .offset(y: reduceMotion ? 0 : geo.frame(in: .global).minY / 2)
        }
    }
}
```

### UIKit Before/After

**Before:**
```swift
func showCard() {
    cardView.transform = CGAffineTransform(scaleX: 0.5, y: 0.5)
    cardView.alpha = 0
    UIView.animate(withDuration: 0.6, delay: 0, usingSpringWithDamping: 0.7,
                   initialSpringVelocity: 0, options: []) {
        self.cardView.transform = .identity
        self.cardView.alpha = 1
    }
}
```

**After:**
```swift
func showCard() {
    if UIAccessibility.isReduceMotionEnabled {
        cardView.transform = .identity
        cardView.alpha = 1
    } else {
        cardView.transform = CGAffineTransform(scaleX: 0.5, y: 0.5)
        cardView.alpha = 0
        UIView.animate(withDuration: 0.6, delay: 0, usingSpringWithDamping: 0.7,
                       initialSpringVelocity: 0, options: []) {
            self.cardView.transform = .identity
            self.cardView.alpha = 1
        }
    }
}
```
