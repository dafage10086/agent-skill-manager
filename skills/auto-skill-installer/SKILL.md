---
name: auto-skill-installer
description: Detect missing capabilities during an AI agent task, search local skill folders plus configured GitHub skill registries, then install and validate the best matching skill before continuing. Use when an agent has loaded this skill and realizes another skill would make the current job safer, faster, or more accurate. Compatible with Codex by default and adaptable to other agent runtimes.
---

# Auto Skill Installer

Use this skill when the current task exposes a capability gap and another skill is likely the right fix.

## Workflow

1. Summarize the missing capability in one short phrase.
2. Search local and remote sources with `scripts/auto_install.py search --need "<capability>"`.
3. Prefer an already-installed or system skill when it is a strong match.
4. Install the best remote match with `scripts/auto_install.py ensure --need "<capability>"`.
5. Validate the installed skill, then continue the user task and mention what was installed.

## Search Strategy

- Start with concrete task language, not generic words. Prefer `github review comments` over `github`.
- If the first search is noisy, run a second search with two or three sharper keywords.
- Prefer skills whose `description` explicitly matches the task and trigger context.
- If several candidates are close, read the strongest candidates' `SKILL.md` files before choosing.

Read [references/source-format.md](references/source-format.md) when you need to add or debug a registry source.

## Commands

```powershell
python scripts/auto_install.py search --need "github pull request review comments"
python scripts/auto_install.py ensure --need "figma design generation"
python scripts/auto_install.py add-source --repo your-org/skills --path skills --name your-org
python scripts/auto_install.py list-sources
```

## Decision Rules

- Install automatically when one candidate is clearly better than the rest.
- Pause and tell the user when multiple candidates have different tradeoffs and no clear winner.
- Do not overwrite an existing destination skill directory.
- Treat user-configured sources as higher priority than broad fallback registries.
- After installation, tell the user that restarting or reloading the target agent may be required for automatic discovery.

## Safety

- Use `$CODEX_HOME/skills` as the default Codex destination; use `--dest` when another agent runtime needs a different skills directory.
- Only install directories that contain `SKILL.md`.
- Reject archive paths that escape the temporary extraction root.
- If a network source fails, explain the failure briefly and continue with remaining sources.
