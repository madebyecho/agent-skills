# Accessibility Manual Verification Checklist

Run through this checklist after automated fixes have been applied. Each section maps to an Apple Accessibility Nutrition Label category. Testing on a real device is strongly recommended.

---

## 1. VoiceOver

**Setup**: Settings > Accessibility > VoiceOver > On (or triple-click Side button)

### Navigation
- [ ] **Full navigation**: Swipe through every screen — all meaningful content is announced
- [ ] **No silent elements**: No interactive elements are skipped by VoiceOver
- [ ] **Logical order**: Swiping forward follows a natural reading order
- [ ] **Can navigate backward**: Swipe left returns through all elements without looping
- [ ] **Headings work**: Rotor set to "Headings" navigates between section titles
- [ ] **No offscreen access**: VoiceOver cannot reach invisible or background content

### Labels and Descriptions
- [ ] **Labels are accurate**: Each element's announcement correctly describes its purpose
- [ ] **Labels are concise**: No unnecessarily verbose descriptions
- [ ] **Labels make sense out of context**: Avoid "Click here" or "Learn more" without context
- [ ] **Labels don't include control type**: Don't say "button" in the label (VoiceOver adds traits automatically)
- [ ] **No redundant announcements**: Related elements are grouped (not announced separately)

### Interactions
- [ ] **Actions work**: All buttons, toggles, and controls activate with VoiceOver double-tap
- [ ] **Custom actions available**: Swipe-up/down reveals custom actions where needed (delete, archive, share)
- [ ] **Long press alternatives**: Long-press actions are available as custom actions
- [ ] **Drag-and-drop alternatives**: Drag operations have accessible alternatives
- [ ] **Adjustable controls**: Custom sliders/steppers respond to VoiceOver swipe up/down

### Dynamic Content
- [ ] **Content changes announced**: Loading states, errors, and updates are spoken
- [ ] **Focus moves to modals**: VoiceOver focus moves to sheets, alerts, and dialogs when they appear
- [ ] **Modals are dismissible**: Escape gesture (two-finger Z-scrub) dismisses modals and popovers
- [ ] **Background hidden behind modals**: Cannot reach content behind active modal
- [ ] **Forms**: All text fields have labels; errors are announced

### Charts and Data
- [ ] **Charts are accessible**: Charts use accessibility APIs or have text alternatives
- [ ] **Data visualizations have descriptions**: Complex visualizations include summary labels

---

## 2. Voice Control

**Setup**: Settings > Accessibility > Voice Control > On

- [ ] **"Show Names"**: All interactive elements display their names/labels
- [ ] **"Show Numbers"**: All interactive elements display numbered overlays
- [ ] **"Tap [name]"**: Saying the visible label activates the correct element
- [ ] **Names match visible text**: Voice Control labels match what's visually displayed
- [ ] **Custom actions**: "Show actions for [number]" reveals context menu / custom actions
- [ ] **Text entry**: Dictation works in all text fields ("type hello world")
- [ ] **Scrolling**: "Scroll down" / "Scroll up" commands work on scrollable content
- [ ] **Complete tasks**: All common tasks can be completed without touching the screen

---

## 3. Larger Text (Dynamic Type)

**Setup**: Settings > Accessibility > Display & Text Size > Larger Text

Test at these sizes:
- [ ] **Default** (baseline)
- [ ] **Largest standard** (max of the non-accessibility range)
- [ ] **AX1** (first accessibility size)
- [ ] **AX5** (maximum accessibility size)

At each size:
- [ ] All text is visible (not clipped or truncated)
- [ ] Layouts adapt (e.g., HStack reflows to VStack at large sizes)
- [ ] Scrolling works for content that exceeds the screen
- [ ] No overlapping elements
- [ ] Images and icons remain proportional
- [ ] Text scales to at least 200% of default size

---

## 4. Sufficient Contrast

**Setup**: Enable all three simultaneously:
- Settings > Accessibility > Display & Text Size > **Bold Text**
- Settings > Accessibility > Display & Text Size > **Increase Contrast**
- Settings > Accessibility > Display & Text Size > **Reduce Transparency**

- [ ] **Normal text**: Meets 4.5:1 contrast ratio against background
- [ ] **Large text** (18pt+ / 14pt bold+): Meets 3:1 contrast ratio
- [ ] **UI components**: Icons, borders, and focus indicators meet 3:1 contrast
- [ ] **Light Mode**: Contrast is sufficient
- [ ] **Dark Mode**: Contrast is sufficient (common to forget this)
- [ ] **Increase Contrast**: Contrast improves when enabled
- [ ] **Custom colors verified**: Use Xcode Accessibility Inspector color contrast calculator
- [ ] **No invisible elements**: No element blends into its background in any mode

---

## 5. Dark Interface

- [ ] All text is readable in Dark Mode
- [ ] No invisible elements (same color as background)
- [ ] Images and icons adapt or remain visible
- [ ] Custom colors look correct in both modes
- [ ] No hardcoded white/black colors that break in the opposite mode

---

## 6. Differentiate Without Color Alone

**Setup**: Settings > Accessibility > Display & Text Size > Color Filters > Grayscale

- [ ] **Grayscale test**: App is fully usable in grayscale
- [ ] **Status indicators**: Use icons/shapes/text alongside color (not just red/green dots)
- [ ] **Error states**: Errors shown with icon + text, not just red color
- [ ] **Selection states**: Selected vs unselected items distinguishable without color
- [ ] **Charts/graphs**: Use patterns, labels, or icons in addition to color coding

---

## 7. Reduced Motion

**Setup**: Settings > Accessibility > Motion > Reduce Motion

- [ ] **Parallax disabled**: No depth simulation or parallax effects
- [ ] **Complex animations simplified**: Spinning, zooming, and multi-axis motion replaced with fades
- [ ] **Auto-advancing content stopped**: Carousels and auto-play content stop or provide controls
- [ ] **Transitions simplified**: Use dissolve/fade instead of slide/zoom transitions
- [ ] **No functionality lost**: All features work the same, just with simpler visuals
- [ ] **3D effects disabled**: No simulated depth or 3D rotations

---

## 8. Touch Targets

- [ ] All buttons and interactive elements have a tap area of at least **44x44 points**
- [ ] Adjacent interactive elements have enough spacing to avoid accidental taps
- [ ] Small visual elements (e.g., close buttons, info icons) have expanded hit areas
- [ ] Toolbar items and navigation bar buttons meet minimum size

---

## 9. Xcode Accessibility Inspector

**Setup**: Xcode > Open Developer Tool > Accessibility Inspector

- [ ] **Audit**: Run the inspector's audit on each screen — resolve all warnings
- [ ] **Inspect elements**: Tap each element to verify:
  - Label is present and descriptive
  - Traits are correct (button, header, link, etc.)
  - Value is present for stateful elements
  - Hint is present for interactive elements
  - Frame is at least 44x44 for interactive elements
- [ ] **Color Contrast Calculator**: Verify custom colors meet minimum ratios

---

## 10. Automated Tests

- [ ] Generated `AccessibilityAuditTests.swift` compiles without errors
- [ ] All audit tests pass (`.contrast`, `.dynamicType`, `.elementDetection`, `.hitRegion`, `.sufficientElementDescription`)
- [ ] Review any audit warnings that were intentionally filtered

---

## 11. Final Verification

- [ ] All `[VERIFY]` markers in code have been reviewed and labels confirmed or updated
- [ ] No remaining accessibility warnings in Xcode's Issue Navigator
- [ ] Test on at least one physical device (Simulator misses some VoiceOver behaviors)
- [ ] All common user tasks completable with VoiceOver only
- [ ] All common user tasks completable with Voice Control only
