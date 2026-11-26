# pstack model configuration for Antigravity. One line per role.
# Run /setup-pstack in Antigravity to fill this from `agy models`.
# inherit-parent: the role runs on the current chat model.
# orca workers: Orca workers run OpenCode, so this line keeps OpenCode slugs.
# defaults: 3
feature, refactoring: inherit-parent
bug-fix: inherit-parent
perf-issue: inherit-parent
hillclimb: inherit-parent
judgment and prose: inherit-parent
arena runners: inherit-parent
arena cross-judge pool: inherit-parent
swarm workers: inherit-parent
interrogate reviewers: inherit-parent
orca workers: openai/gpt-6-luna, alibaba-token-plan/deepseek-v4.1-flash-1017
