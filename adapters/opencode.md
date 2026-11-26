- **Tools.** Ask structured questions with `question`. Load a skill with the `skill` tool. Spawn native subagents with `subagent`. Keep the checklist with the todo tool.
- **Load a skill.** Call the `skill` tool with the skill ID.
- **Model file.** pstack skills read `~/.agents/pstack-models.md`.
- **Orca model file and list.** The `orca workers` line in `~/.agents/pstack-models.md`; exact slugs come from `opencode models`.
- **Permission gates.** The project's `opencode.jsonc` asks before commit, push, PR, Helm, kubectl, and Terraform commands.

### Model escalation

The user selects the parent model in `/models`. Do not switch the session automatically. For Bug Fix, recommend `alibaba-token-plan/qwen4-max-preview#medium` while available. If Qwen is unavailable or still cannot resolve the bug after a targeted investigation, recommend `alibaba-token-plan/deepseek-v4-pro#high`; if Alibaba itself is unavailable or out of quota, recommend `openai/gpt-6.1-terra#high` instead.

For Hillclimb and Swarm, recommend `openai/gpt-6-luna#medium` as parent. Gather missing evidence first; suggest Luna `#high` if the evidence is hard to interpret, or `openai/gpt-6.2-sol#high` for cross-component complexity. If Luna is unavailable, suggest `alibaba-token-plan/deepseek-v4.1-flash-1017#high`. Keep valid results when switching. When delegation and model selection are supported, retry only a failed slice or iteration once: use DeepSeek Flash `#high` for a harder task, or `alibaba-token-plan/qwen3.8-flash#medium` if that DeepSeek model is unavailable.

For feature, refactoring, and performance work, suggest `openai/gpt-6.2-sol#high` if the first result fails verification after a targeted check or the task turns out to span multiple components.
