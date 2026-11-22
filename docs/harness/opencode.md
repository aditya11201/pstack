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
| `skills/execution-checkpoint/` | Persistent execution status, evidence, decisions, blockers, summary, and resume points in the **working repo** under `.pstack/executions/<run-id>/`. |\n| `skills/plan-gap-interview/` | Plan mode checks a plan against its approved spec; change mode folds a requirement added later into the spec and plan. Asks one question at a time about new decisions only, then waits for approval. Uses `grilling` from mattpocock/skills. |
| `examples/commands/plan-review.md` | `/plan-review` command to run the same interview manually, e.g. from the built-in `plan` agent. |
| `examples/pstack-models.md` | Example per-role model mapping (OpenAI + Alibaba Token Plan). |
| `examples/opencode.jsonc` | Example workspace config: disable the Superpowers plugin locally and gate risky commands. |
| `examples/opencode.global.json` | Plugins the workflow expects globally; `install.sh` merges them. |
| `examples/rtk/` | RTK OpenCode plugin and rules. |
| `install.sh` | One-command install of everything above. |

pstack itself stays a prerequisite, installed separately. This repo does not vendor a
second copy of upstream skills beyond the method skills above.

## Prerequisites

- OpenCode 2, Node.js with `npx`, and `python3`.
- Optional: the [`rtk`](https://github.com/rtk-ai/rtk) binary for terminal output
  compression, and the Orca app for `orchestration` / `orca-cli` delegation (Orca ships
  those skills itself).
- Provider accounts and MCP servers are personal; configure them separately.

## Install

```sh
git clone https://github.com/aditya11201/pstack && cd pstack
./install.sh            # or ./install.sh --no-rtk
```

The script is safe to rerun. It installs, for the current user:

| What | Where |
|---|---|
| pstack, method, spec/plan, and `plan-gap-interview` skills from this repo | `~/.agents/skills/` |
| `grilling` from mattpocock/skills | `~/.agents/skills/` |
| `pstack-engineer` agent, `/plan-review` command | `~/.config/opencode/agents/`, `commands/` |
| Model mapping (only when none exists) | `~/.agents/pstack-models.md` |
| Plugins `superpowers`, `cc-safety-net`, `ponytail`, merged without touching other settings or replacing a version you already pin | `~/.config/opencode/opencode.json` |
| RTK plugin and rules, with `@RTK.md` added to `~/.claude/CLAUDE.md` | `~/.config/opencode/plugins/rtk.ts`, `~/.claude/RTK.md` |

Per project, merge `examples/opencode.jsonc` into the project's `opencode.jsonc`. It
disables the global Superpowers plugin there, so this repo's method skills are the only
copy, and makes commit, push, PR, and deploy commands ask first.

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

## Resume an approved implementation after compaction

Use `execution-checkpoint` for multi-step plans once implementation is explicitly authorized. Initialize it from the working codebase with `python3 <installed-skill>/scripts/checkpoint.py init --repo . --plan docs/plans/<file>.md --run <id>`. On each verifiable milestone, record a `step` or `task` completion with evidence and update the summary and next action. Use `block` / `unblock` for blockers, and `decision` for design choices.

After a context reset, run `python3 <installed-skill>/scripts/checkpoint.py resume --repo . --run <id>` **before** implementing. The CLI reports plan hash drift, tasks still open, blockers, decisions, HEAD, and working diff. Verify results using actual tests/Git before trusting completion claims. The checkpoint is not a substitute for approvals or the `verification-before-completion` skill.

OpenCode uses the agent instructions, not Cursor hooks. Cursor's optional hook setup is documented in [execution-checkpoint.md](execution-checkpoint.md), with the limitation that `sessionStart` fires for a newly created conversation, not guaranteed at in-place compaction.

## OpenCode 2 native checkpoint recovery

OpenCode 2 is a supported host, with a **native V2 plugin** (not the legacy V1 `experimental.session.compacting` hook). The repository installer places `examples/opencode2/pstack-execution-checkpoint.js` into `~/.config/opencode/plugins/pstack-execution-checkpoint.js`, merging with existing plugins without replacing unrelated files. OpenCode 2 discovers this directory automatically. Restart OpenCode if the plugin is not detected.

- `ctx.session.hook("context", ...)`: loads the selected run from the **actual session directory** before every agent model request, including the first request following compaction.
- `ctx.session.hook("compaction", ...)`: supplies the same short state reference to the compaction summary model.
- `ctx.session.get({sessionID})`: determines the workspace for each invocation; a missing, ambiguous, or symlink-escaped run fails closed.
- `/execution-resume <run-id>`: explicit manual inspection of the canonical state, Git diff, completed steps, blockers and next action (does **not** auto-implement).
- Only a single pinned run is selected when multiple runs exist; set `PSTACK_RUN_ID` when invoking OpenCode 2, or pass `--run` to the CLI. The global pin still resolves relative to the session's own repository.
- The plugin reads state; agents must explicitly write checkpoints using the `execution-checkpoint` skill and its CLI. It does not approve commits, apply Terraform, or execute jobs.

Verify actual V2 plugin registration on the running host:

```bash
opencode2 api get /api/plugin
# Expect plugin id: pstack.execution-checkpoint
```

Run its local contract tests:

```bash
node --test examples/opencode2/pstack-execution-checkpoint.test.mjs
```

**Compatibility note:** OpenCode 2's plugin API remains beta; verify against the installed OpenCode 2 version before production use. [Official V2 plugin API](https://opencode.ai/v2/docs/build/plugins/). The test suite mocks the documented plugin hooks but does not prove a live OpenCode 2 process loaded them.

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