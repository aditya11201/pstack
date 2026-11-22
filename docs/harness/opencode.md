# OpenCode integration

This fork adds an integration layer on top of upstream pstack so it cooperates with
Superpowers methods, Ponytail, and Orca inside OpenCode 2. Upstream pstack skills are
not modified; the layer is additive, so `git merge upstream/main` stays clean.

## What this layer adds

| Path | Purpose |
|---|---|
| `agents/pstack-engineer.md` | Primary agent that loads `poteto-mode`, picks one playbook, and applies the routing below. |
| `skills/systematic-debugging/` | Root-cause debugging method (from Superpowers, MIT). |
| `skills/test-driven-development/` | The single TDD procedure (from Superpowers, MIT). |
| `skills/verification-before-completion/` | Fresh evidence on the final diff before claiming success (from Superpowers, MIT). |
| `skills/brainstorming/` | Interview and design first; an architectural change gets a spec in `docs/specs/` that the user approves (from Superpowers, MIT, modified). |
| `skills/writing-plans/` | Writes the plan to `docs/plans/`, linked to its spec (from Superpowers, MIT, modified). |
| `skills/plan-gap-interview/` | Plan mode checks a plan against its approved spec; change mode folds a requirement added later into the spec and plan. Asks one question at a time about new decisions only, then waits for approval. Uses `grilling` from mattpocock/skills. |
| `examples/commands/plan-review.md` | `/plan-review` command to run the same interview manually, e.g. from the built-in `plan` agent. |
| `examples/pstack-models.md` | Example per-role model mapping (OpenAI + Alibaba Token Plan). |
| `examples/opencode.jsonc` | Example workspace config: disable the Superpowers plugin locally and gate risky commands. |

pstack itself stays a prerequisite, installed separately. This repo does not vendor a
second copy of upstream skills beyond the method skills above.

## Install

```sh
# 1. Skills (upstream pstack + the method skills) and the grilling interview method
npx skills add aditya11201/pstack
npx skills add mattpocock/skills --skill grilling -g

# 2. Agent (one-time)
mkdir -p ~/.config/opencode/agents
cp agents/pstack-engineer.md ~/.config/opencode/agents/

# 3. Optional: model mapping and workspace config
cp examples/pstack-models.md ~/.agents/pstack-models.md   # edit to your providers
# Merge examples/opencode.jsonc into your project's opencode.jsonc
mkdir -p ~/.config/opencode/commands
cp examples/commands/plan-review.md ~/.config/opencode/commands/
```

Select the `pstack-engineer` agent in OpenCode, choose a parent model in `/models`,
then give a goal, scope, and pass criteria. Use the built-in `plan` agent for read-only
analysis.

## Routing

One playbook per task, one TDD procedure when relevant, one evidence-based completion
decision. The agent's crosswalk maps pstack steps to this workflow's methods:

- Root-cause / reproduce → `systematic-debugging`, once; carry evidence into the fix.
- Failing-test-first / `tdd` → `test-driven-development` only; skip pstack `tdd`.
- Feature or plan request → `brainstorming` → spec in `docs/specs/` → user approves the spec →
  `writing-plans` → plan in `docs/plans/` → `plan-gap-interview` (plan mode) → user approves.
- Requirement added after the spec was approved → stop at a safe boundary →
  `plan-gap-interview` (change mode) → approval → spec, then plan, updated.
- Verify before done → `verification-before-completion` on the final revision.
- Delegate / swarm / arena → Orca `orchestration` when the user asks; otherwise inline.
- Opening a PR / shipping / commit / rebase → skip unless explicitly authorized.

Ponytail gates coding: read affected code and callers before the first edit, reuse an
existing function before adding one, preserve contracts and validation. Delegation uses
self-contained worker briefs and waits for Orca results; a Codex hook-trust blocker is
surfaced to the user, never auto-approved.

## Models

`examples/pstack-models.md` is a cost-tiered starting point, not a requirement. Edit it to
your providers and budget, or run `@setup-pstack`. The parent model is always chosen in
`/models`; the mapping only guides delegated roles when the subagent tool supports model
selection. Note: `alibaba-token-plan/qwen4-max-preview` is scheduled to retire on
2026-11-25 (UTC+8); re-check `/models` before relying on it.

## Guardrails

`examples/opencode.jsonc` disables the Superpowers plugin for the workspace
(`plugins: ["-superpowers"]`) so the local method skills are the single source, and
sets `ask` permissions for commit, rebase, push, PR/MR CLI, Helm install/upgrade,
`kubectl apply`, and Terraform apply/destroy. These are not a complete mutation list;
cluster access control, branch protection, and CI approvals still apply.

## Sync upstream

```sh
git fetch upstream
git merge upstream/main   # additive layer keeps this conflict-free
```

## Attribution

Upstream pstack is MIT (Lauren Tan and contributors). The method skills are from
[obra/superpowers](https://github.com/obra/superpowers), MIT (Jesse Vincent).
`plan-gap-interview` adapts parts of Superpowers and
[mattpocock/skills](https://github.com/mattpocock/skills), MIT (Matt Pocock). See `NOTICE.md`.