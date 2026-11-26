# Antigravity integration

This fork installs the same workflow it runs in OpenCode 2 into Antigravity: the `agy` CLI, the Antigravity 2.0 app, and the IDE. All three read `~/.gemini/config/`. Spec: `docs/specs/2026-11-26-antigravity-support-design.md`.

## Facts this integration relies on

Checked on 2026-11-26 against `agy` 1.5.17. The sources are the built-in `agy-customizations` skill (`~/.gemini/antigravity-cli/builtin/skills/agy-customizations/`) and an `agy -p` session that listed its own tools.

| Fact | Value | Source |
|---|---|---|
| Global customization root | `~/.gemini/config/` | agy-customizations `SKILL.md` |
| Plugin location | `~/.gemini/config/plugins/<dir>/plugin.json`. Unknown top-level manifest fields are dropped. | `docs/plugins.md`, builtin `plugin` skill |
| Plugin rules | `rules/AGENTS.md`, no frontmatter, always on while the plugin is enabled | builtin `plugin` skill |
| Rule size cap | 24,000 bytes per file; the overflow is truncated | `docs/rules.md` |
| Extra skill roots | `~/.gemini/config/skills.json` `entries[].path`, scanned one level deep. This machine already lists `~/.agents/skills`. | `docs/json_configs.md` |
| Hooks | `<plugin>/hooks.json` at the plugin root. Handlers get JSON on stdin and write JSON on stdout. They run in the plugin dir with `PLUGIN_ROOT` and `PLUGIN_DATA` set. | `docs/hooks.md` |
| Hook events | `SessionStart`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`. There is **no compaction hook**. | `docs/hooks.md` |
| Context injection | `{"injectSteps":[{"systemMessage":{"systemMessage":"…"}}]}`. It persists in the conversation, so it is injected only when it changes. | `docs/hooks.md` |
| Tool gate | `PreToolUse` returns `{"decision":"ask"}` | `docs/hooks.md` |
| Slash commands | Every skill is also `/<name>` | builtin `migrate-workflows` skill |
| Plugin toggle | `agy plugin enable|disable <dir>`, or the plugin page | builtin `plugin` skill |
| Model list | `agy models` | `agy --help` |

## Tool names

| Role | OpenCode | Antigravity |
|---|---|---|
| Structured question | `question` | `ask_question` |
| Load a skill | `skill` | none: read the skill's `SKILL.md` with `read_file` |
| Spawn a subagent | `subagent` (`task`) | `invoke_subagent` |
| Todo checklist | `todowrite` | `update_steps` |
| Shell | `shell` | `run_command` |
| Read, edit, write files | `read`, `edit`, `write` | `read_file`, `edit_file`, `write_file` |
| Background tasks | — | `manage_task` |

Source: `agy -p --mode plan` in a scratch repo, 2026-11-26. The CLI listed `read_file`, `write_file`, `edit_file`, `run_command`, `manage_task`, `update_steps`, `send_message`, `schedule`, `invoke_subagent`, `define_subagent`, `manage_subagents`, `search_web`, `run_workflow`, `swarm`, `ask_question`, `call_mcp_tool`, `list_resources`, and `read_resource`. It also said that skills are loaded by reading their `SKILL.md`.
