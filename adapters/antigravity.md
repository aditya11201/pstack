- **Tools.** Ask structured questions with `ask_question`. Spawn native subagents with `invoke_subagent`. Keep the checklist with `update_steps`. Run shell commands with `run_command`. A skill that names the `question` tool means `ask_question`; one that names the `subagent` or `task` tool means `invoke_subagent`.
- **Load a skill.** Antigravity has no skill tool. Read the skill's `SKILL.md` with `read_file`, from `~/.agents/skills/<id>/SKILL.md` or the path listed in your available skills, and follow it. "Load `X`" anywhere in these rules or in a skill means this.
- **Model file.** pstack skills read `~/.agents/pstack-models.antigravity.md`. Wherever a skill names `~/.agents/pstack-models.md` as the settings file for "other harnesses", use the Antigravity file instead. `/setup-pstack` fills it from `agy models`.
- **Orca model file and list.** Orca workers run OpenCode in every harness. Use the `orca workers` line in `~/.agents/pstack-models.md` (the OpenCode file), and take exact slugs from `opencode models`.
- **Permission gates.** The `pstack-gate` hook asks before commit, push, PR, Helm, kubectl, and Terraform commands. Do not route around a gate with another tool.

### Model escalation

The user selects the parent model with `/model` or `agy --model`. Do not switch the session automatically. When a role in the model file names a model, recommend that model for the matching playbook (`bug-fix` for Bug Fix, `hillclimb` for Hillclimb and Swarm, `feature, refactoring` for feature, refactoring, and performance work). When it says `inherit-parent`, stay on the current model. If the first result fails verification after a targeted check, or the task turns out to span multiple components, suggest the highest-effort variant of the same family that `agy models` lists.
