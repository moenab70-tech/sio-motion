# Local changes (SIO install, 2026-11-15)

Source: github.com/nextlevelbuilder/ui-ux-pro-max-skill (main, MIT), only `.claude/skills/ui-ux-pro-max/`. Sub-skills (brand, banner-design, design, design-system, slides, ui-styling) NOT installed.

Patched SKILL.md: 11 invocations `python "${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py"` → `python3 .claude/skills/ui-ux-pro-max/scripts/search.py` (plugin variable is unset for project skills; only python3 exists). Added an SIO scope note. Audit: stdlib-only, no network/exec calls, no hooks, no symlinks.
