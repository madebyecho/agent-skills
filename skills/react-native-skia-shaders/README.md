# react-native-skia-shaders

A skill for Claude Code / claude.ai that adds 25+ SKSL shader techniques
adapted for `@shopify/react-native-skia`.

Companion to [`react-native-animations`](../react-native-animations) — use that
skill for motion/gesture decisions, this one for everything that runs inside
a `<Shader>`.

## Install (Claude Code)

```bash
cp -r react-native-skia-shaders ~/.claude/skills/
# or
npx skills add madebyecho/agent-skills
```

## Use

Read `SKILL.md` for the routing table. Or just ask Claude things like:

- "Write a SKSL shader that animates a mesh gradient background."
- "Port this ShaderToy to react-native-skia: …"
- "How do I do a live blur over a scroll view?"
- "My RuntimeEffect.Make returns null — debug it."
- "Build a liquid distortion over this Image."

## Layout

- `SKILL.md` — Entry point, routing table, quick reference, performance budget.
- `techniques/` — Implementation guides (one per technique).
- `reference/` — Math / deep-dive companions.

## Acknowledgements

The structure and many of the technique recipes are ported from
[minimax-ai/shader-dev](https://skills.sh/minimax-ai/skills/shader-dev), which
is a GLSL/ShaderToy-focused skill. The SKSL syntax, the react-native-skia
integration patterns, the mobile performance budget, and all of the
RN-specific files are new.
