---
name: execution-checkpoint
description: Keep persistent progress, verification evidence, blockers, decisions and a resumable execution summary in the working repository when implementing an approved plan or resuming after context compaction.
---

# Execution checkpoint

Record execution state for an approved plan in the working repository, so work can resume after compaction or a new session without trusting memory. The helper is `scripts/checkpoint.py` in this skill's folder; for OpenCode that is normally:

```bash
CHECKPOINT="$HOME/.agents/skills/execution-checkpoint/scripts/checkpoint.py"
```

Run it from the **repository being modified** with `--repo .`, never from the pstack checkout. It writes `.pstack/executions/<run-id>/`. `state.json` is canonical; `summary.md`, `progress.md`, and `blockers.md` are regenerated views. Do not edit any of them by hand.

## Authorization and ownership

- Only start when the user has explicitly told you to *implement*. Approval of a spec, a plan, or a `plan-gap-interview` summary does not authorize coding.
- The approved plan in `docs/plans/` stays read-only. Its SHA-256 is recorded at `init`; any later edit shows as drift.
- One coordinator writes to a run. Delegated workers report evidence; the coordinator records it.
- With more than one run, always pass `--run` (or set `PSTACK_RUN_ID`). Never pick a recent run by guessing.

## Starting

1. Check for an existing run: `python3 "$CHECKPOINT" status --repo .` (add `--run <id>` if you know it). `checkpoint: invalid run ID` without `--run` means no single run exists (none, or several). Reuse a run; `init` refuses to overwrite one.
2. If none exists: `python3 "$CHECKPOINT" init --repo . --plan docs/plans/<plan>.md --run <id>`. It parses `### Task N:` / `### Phase N:` headings into `T1, T2, …` and their checkboxes into `S1, S2, …`. Boxes already checked in the plan do not count as done.

## Checkpoint at every boundary

Right after a verified step, a task transition, a failed check, a blocker, a decision, or a handoff:

```bash
python3 "$CHECKPOINT" task     --repo . --run <id> --task T1 --status in_progress --next "T1/S1"
python3 "$CHECKPOINT" step     --repo . --run <id> --task T1 --step S1 --status complete --evidence "<command>: <observed output>"
python3 "$CHECKPOINT" task     --repo . --run <id> --task T1 --status complete --evidence "<command>: <observed output>" --next "T2"
python3 "$CHECKPOINT" note     --repo . --run <id> --summary "<current state>" --next "<single next action>"
python3 "$CHECKPOINT" block    --repo . --run <id> --task T1 --message "<why blocked>" --evidence "<what you saw>"
python3 "$CHECKPOINT" unblock  --repo . --run <id> --blocker B1 --resolution "<what fixed it>"
python3 "$CHECKPOINT" decision --repo . --run <id> --text "<decision>" --reason "<why>" --evidence "<pointer>"
```

- Evidence is the command you actually ran and the output you saw. The helper requires it to complete a step or task but does not run or check it; you do. A failed check is recorded as a failure or a blocker, never as complete.
- A task completes only when all its steps are complete and it has no open blocker; the helper enforces both.
- If the plan changed, the helper refuses updates. Reconcile scope with `plan-gap-interview` (change mode) and get approval before continuing.
- Redact secrets, credentials, customer data and sensitive log bodies from evidence.

## Resuming after compaction or a new session

1. `python3 "$CHECKPOINT" resume --repo . [--run <id>]`. It prints progress, next action, blockers, decisions, HEAD, diff stat, and plan drift.
2. Treat that output as claims. Compare it with the approved plan, `git status`, `git diff`, and the recorded evidence; rerun a check when the evidence is stale or missing.
3. If the plan drifted, stop and report it. Otherwise continue from the first unverified step.
4. Resuming does not grant permission to implement. Continue only if implementation was already authorized for this run; otherwise report state and wait.

## Host integration

- **OpenCode 2:** the plugin `pstack-execution-checkpoint.js` (installed by `install.sh`) injects a read-only summary of the single run, or the pinned run, into the session context. It never writes state. Still call `resume` yourself after compaction.
- **Cursor:** `python3 "$CHECKPOINT" install-cursor-hooks --repo .` merges session-start and post-edit reminders into `.cursor/hooks.json`. Review the diff before committing it.
- Nothing here commits, pushes, merges, deploys or deletes. Those keep their own explicit approval.

## Handoff

Report the run ID, the plan path, completed and pending tasks, the last verified step with its evidence, open blockers, decisions, any drift, and the next safe action. Missing evidence is reported as `unverified`, not `complete`.

See [architecture and setup](../../docs/harness/execution-checkpoint.md).
