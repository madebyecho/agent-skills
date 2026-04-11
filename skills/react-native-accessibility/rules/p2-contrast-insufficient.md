---
title: Insufficient Color Contrast
priority: P2
impact: MEDIUM
platforms: iOS, Android
tags: contrast, wcag, vision, color
---

## Insufficient Color Contrast

**Priority: P2 (MEDIUM)**

Text and interactive elements must meet minimum contrast ratios against their backgrounds. Low contrast makes content unreadable for users with low vision, and difficult for everyone in bright environments. WCAG AA requires 4.5:1 for normal text and 3:1 for large text (18pt+ or 14pt bold+) and UI components.

### Detection

```
grep -n 'color:\s*["\x27]#\|color:\s*["\x27]rgb\|color:\s*["\x27]hsl' **/*.{tsx,jsx,ts,js}
# Flag hardcoded color values for manual contrast review

grep -n "color:\s*['\"]gray['\"]\\|color:\s*['\"]lightgray['\"]\\|color:\s*['\"]silver['\"]" **/*.{tsx,jsx,ts,js}
# Flag commonly low-contrast named colors

grep -n 'opacity:\s*0\.[0-4]' **/*.{tsx,jsx,ts,js}
# Flag low-opacity text that may fail contrast requirements
```

### Fix Logic

1. Flag hardcoded color pairs for manual contrast review — automated contrast checking requires rendering context
2. Recommend using a contrast checker tool (WebAIM, Colour Contrast Analyser)
3. Common fixes:
   - Replace light gray text with a darker shade (at least `#767676` on white)
   - Increase opacity of semi-transparent text
   - Use semantic color tokens that adapt to light/dark mode
4. Add `[VERIFY]` marker for manual review

### Before/After

**Before:**
```tsx
<Text style={{ color: '#999', fontSize: 14 }}>
  Last updated 2 hours ago
</Text>

<Text style={{ color: 'lightgray' }}>
  No results found
</Text>

<Pressable style={{ backgroundColor: '#eee' }}>
  <Text style={{ color: '#bbb' }}>Submit</Text>
</Pressable>
```

**After:**
```tsx
<Text style={{ color: '#767676', fontSize: 14 }}>
  {/* [VERIFY] contrast ratio against background meets 4.5:1 */}
  Last updated 2 hours ago
</Text>

<Text style={{ color: '#767676' }}>
  {/* [VERIFY] contrast ratio against background meets 4.5:1 */}
  No results found
</Text>

<Pressable style={{ backgroundColor: '#eee' }}>
  <Text style={{ color: '#595959' }}>
    {/* [VERIFY] contrast ratio of #595959 on #eee is ~4.6:1 — passes AA */}
    Submit
  </Text>
</Pressable>
```

### Platform Considerations

- **iOS (VoiceOver):** iOS supports "Increase Contrast" in accessibility settings. Apps should respond by using higher-contrast color variants. React Native can detect this via `AccessibilityInfo.isInvertColorsEnabled` or native modules
- **Android (TalkBack):** Android 14+ supports contrast themes. Ensure custom colors don't override system contrast preferences
- **Both platforms:** Use a contrast checking tool during development. Consider creating a theme with semantic color tokens (e.g., `colors.textPrimary`, `colors.textSecondary`) that meet minimum ratios by default
