# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

Echo Studio's official collection of agent skills for Claude Code and claude.ai. Skills are packaged instructions and reference material that extend agent capabilities for platform-specific development.

## Creating a New Skill

### Directory Structure

```
skills/
  {skill-name}/           # kebab-case directory name
    SKILL.md              # Required: skill definition
    rules/                # Optional: individual rule/pattern files
      _sections.md        # Section index and ordering
      _template.md        # Template for new rules
      {rule-name}.md      # Individual rules (kebab-case)
    assets/               # Optional: templates, scripts, checklists
    examples/             # Optional: before/after examples
    metadata.json         # Optional: version, author, references
    README.md             # Optional: standalone documentation
  {skill-name}.zip        # Optional: packaged for distribution
```

### Naming Conventions

- **Skill directory**: `kebab-case` (e.g., `swift-accessibility`, `kotlin-testing`)
- **SKILL.md**: Always uppercase, always this exact filename
- **Rules**: `{section-prefix}-{rule-name}.md` (e.g., `p0-images-without-labels.md`)
- **Zip file**: Must match directory name exactly: `{skill-name}.zip`

### SKILL.md Format

```markdown
---
name: {skill-name}
description: >
  {One or two sentences describing when to use this skill.
  Include trigger phrases.}
license: MIT
metadata:
  author: madebyecho
  version: "1.0.0"
---

# {Skill Title}

{Brief description}

## When to Apply

{Bullet list of trigger conditions}

## Rule Categories by Priority

{Table of categories with impact levels}

## Rules

{Reference to rules/ directory with brief descriptions}
```

### Best Practices for Context Efficiency

- **Keep SKILL.md under 500 lines** — put detailed reference material in `rules/` or `assets/`
- **Write specific descriptions** — helps the agent know exactly when to activate the skill
- **Use progressive disclosure** — reference supporting files that get read only when needed
- **Prefer scripts over inline code** — script execution doesn't consume context
- **File references work one level deep** — link directly from SKILL.md to supporting files

### End-User Installation

**Claude Code:**
```bash
npx skills add madebyecho/agent-skills
# or manually:
cp -r skills/{skill-name} ~/.claude/skills/
```

**claude.ai:**
Add the skill to project knowledge or paste SKILL.md contents into the conversation.
