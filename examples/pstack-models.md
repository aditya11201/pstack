# pstack model configuration for OpenCode. One line per role.
# defaults: 3
# budget: medium (high)
feature, refactoring: openai/gpt-6.1-terra#high
bug-fix: alibaba-token-plan/deepseek-v4-pro#high
perf-issue: openai/gpt-6.1-terra#high
hillclimb: alibaba-token-plan/deepseek-v4.1-flash-1017#low
judgment and prose: openai/gpt-6.1-terra#medium
arena runners: openai/gpt-6.1-terra#medium, alibaba-token-plan/deepseek-v4-pro#high
arena cross-judge pool: alibaba-token-plan/qwen4-max-preview#medium, openai/gpt-6.1-terra#medium
swarm workers: alibaba-token-plan/deepseek-v4.1-flash-1017#low
interrogate reviewers: openai/gpt-6.1-terra#medium, alibaba-token-plan/deepseek-v4-pro#high
orca workers: openai/gpt-6-luna, alibaba-token-plan/deepseek-v4.1-flash-1017
