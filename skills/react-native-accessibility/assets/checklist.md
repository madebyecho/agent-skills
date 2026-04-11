# Accessibility Manual Verification Checklist

Run through this checklist after automated fixes have been applied. Test on both iOS and Android physical devices — simulators miss some screen reader behaviors.

---

## 1. VoiceOver (iOS)

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
- [ ] **Labels don't include control type**: Don't say "button" in the label (VoiceOver adds roles automatically)
- [ ] **No redundant announcements**: Related elements are grouped (not announced separately)

### Interactions
- [ ] **Actions work**: All buttons and controls activate with VoiceOver double-tap
- [ ] **Custom actions available**: Swipe up/down reveals custom actions where needed (delete, archive, share)
- [ ] **Escape gesture**: Two-finger Z-scrub dismisses modals and goes back

### Dynamic Content
- [ ] **Content changes announced**: Loading states, errors, and updates are spoken
- [ ] **Focus moves to modals**: VoiceOver focus moves to sheets, alerts, and dialogs when they appear
- [ ] **Modals are dismissible**: Escape gesture dismisses modals and popovers
- [ ] **Background hidden behind modals**: Cannot reach content behind active modal
- [ ] **Forms**: All text fields have labels; errors are announced

---

## 2. TalkBack (Android)

**Setup**: Settings > Accessibility > TalkBack > On (or long-press both volume buttons)

### Navigation
- [ ] **Full navigation**: Swipe through every screen — all meaningful content is announced
- [ ] **No silent elements**: No interactive elements are skipped by TalkBack
- [ ] **Logical order**: Swiping forward follows a natural reading order
- [ ] **Headings work**: Set navigation mode to "Headings" and swipe up/down to jump between headers
- [ ] **No offscreen access**: TalkBack cannot reach invisible or background content

### Labels and Descriptions
- [ ] **Labels are accurate**: Each element's announcement correctly describes its purpose
- [ ] **Labels are concise**: No unnecessarily verbose descriptions
- [ ] **Roles announced**: Buttons say "Double tap to activate", checkboxes say "checked/unchecked"
- [ ] **No redundant announcements**: Related elements are grouped (not announced separately)

### Interactions
- [ ] **Actions work**: All buttons and controls activate with TalkBack double-tap
- [ ] **Custom actions available**: Local context menu shows custom actions
- [ ] **Forms**: All text fields have labels; keyboard appears when double-tapping a text field

### Dynamic Content
- [ ] **Content changes announced**: Loading states, errors, and updates are spoken
- [ ] **Focus moves to modals**: TalkBack focus moves to new dialogs
- [ ] **Background hidden behind modals**: Cannot reach content behind active modal with TalkBack navigation

---

## 3. Font Scaling

### iOS
**Setup**: Settings > Accessibility > Display & Text Size > Larger Text

Test at these sizes:
- [ ] **Default** (baseline)
- [ ] **Largest standard** (max of the non-accessibility range)
- [ ] **AX1** (first accessibility size)
- [ ] **AX5** (maximum accessibility size)

### Android
**Setup**: Settings > Accessibility > Font size (or Display size)

Test at:
- [ ] **Default** (baseline)
- [ ] **Maximum** font size setting

### At each size (both platforms):
- [ ] All text is visible (not clipped or truncated)
- [ ] Layouts adapt (content scrolls if needed)
- [ ] No overlapping elements
- [ ] `allowFontScaling` is not set to `false` anywhere

---

## 4. Color and Contrast

- [ ] **Normal text**: Meets 4.5:1 contrast ratio against background
- [ ] **Large text** (18pt+ / 14pt bold+): Meets 3:1 contrast ratio
- [ ] **UI components**: Icons, borders, and focus indicators meet 3:1 contrast
- [ ] **Not color-only**: Status indicators use icons/text alongside color
- [ ] **Light theme**: Contrast is sufficient
- [ ] **Dark theme**: Contrast is sufficient (if supported)
- [ ] **Grayscale test**: App is usable with color filters set to grayscale

---

## 5. Touch Targets

- [ ] All buttons and interactive elements have a tap area of at least **48x48 dp**
- [ ] Adjacent interactive elements have enough spacing to avoid accidental taps
- [ ] Small visual elements (e.g., close buttons, info icons) have expanded hit areas via `hitSlop`

---

## 6. Reduce Motion

### iOS
**Setup**: Settings > Accessibility > Motion > Reduce Motion

### Android
**Setup**: Settings > Accessibility > Remove animations

- [ ] Complex animations are simplified or replaced with fades
- [ ] Auto-advancing content (carousels) stops or provides controls
- [ ] No functionality is lost — only visual transitions change
- [ ] Parallax and 3D effects are disabled

---

## 7. Automated Tests

- [ ] Generated `accessibility.test.tsx` runs without errors
- [ ] All accessibility queries find the expected elements
- [ ] All images have labels or are hidden from the accessibility tree
- [ ] All pressable elements have labels and roles

---

## 8. Final Verification

- [ ] All `[VERIFY]` markers in code have been reviewed and labels confirmed or updated
- [ ] Test on at least one physical iOS device (Simulator misses some VoiceOver behaviors)
- [ ] Test on at least one physical Android device (Emulator misses some TalkBack behaviors)
- [ ] All common user tasks completable with VoiceOver only
- [ ] All common user tasks completable with TalkBack only
