---
name: plan-from-spec
description: Use when an approved spec needs an implementation plan, or the user asks for a plan file. Turns the spec into a task-by-task plan in docs/plans/ that an engineer without context can execute, then hands it to plan-gap-interview.
---

# Plan from spec

A plan records the decisions an implementer cannot make alone: which files, which names and signatures, which values from the spec, and which check proves each task. It leaves the rest to them. Write for a capable engineer who has not seen this repo or this conversation.

## Before writing

- Read the approved spec. If none exists, use the request as the spec and say so.
- If the spec spans several independent subsystems, propose one plan per subsystem and ask which one comes first.
- List the files to create or change and what each is responsible for. Follow the repo's existing structure. Files that change together belong in the same task.

## File and header

Save to `docs/plans/YYYY-MM-DD-<topic>.md` unless the user names another place. Do not commit it unless the user authorizes that. Start with:

```markdown
# <Topic> Implementation Plan

> **For agentic workers:** Implement task-by-task with `test-first` and `evidence-before-done`. Steps use checkbox (`- [ ]`) syntax for tracking. Commits, pushes, MRs and other outward actions follow the spec's `## Authorizations` section and later grants recorded as `AUTH:` checkpoint decisions.

**Goal:** <one sentence>
**Architecture:** <two or three sentences>
**Tech Stack:** <key tools and libraries>
**Spec:** <path to the spec>

## Global Constraints

<Project-wide rules from the spec, one per line, with exact values. Do not
restate or narrow the spec's Authorizations, and add no "wait for the
user's go" lines; refer to that section.>

## Review Focus

<Up to five inputs or failure modes the spec implies but does not spell
out, most likely first. Each line names the task whose test covers it.>
```

## Tasks

Use `### Task N: <name>` headings; `execution-checkpoint` parses them.

- A task is the smallest change with its own check that a reviewer could accept or reject on its own. Fold setup, config, and docs into the task that needs them.
- Each task lists:
  - **Files**: create, modify (with line ranges when useful), delete.
  - **Interfaces**: what it consumes from earlier tasks, and what later tasks rely on (exact names and signatures).
- Steps are checkboxes, and each one is a single action with a checkable result:
  - **Test step**: the test name and its assertions, with the spec's values.
  - **Run step**: the command and the output that means pass or fail.
  - **Code step**: the signature, the file, and any values the spec pins. Show a body only for an algorithm the test does not determine.
  - **Commit or push step**: only where the spec's Authorizations allow it. Otherwise mark it ask-first.
- No step may say "add error handling", "write tests", or "TBD". No step may use a name that no task defines.

## Reread before handing off

1. **Coverage**: every spec requirement maps to a task, and every task maps to a requirement.
2. **Steps**: each step allows exactly one reasonable implementation, and no step is a transcript of code the test already pins.
3. **Names**: names, types, and paths match across tasks.
4. **Review Focus**: each line has its test in the owning task.
5. **Length**: a plan much longer than its spec is writing the code. Cut the bodies and keep the signatures and tests.

Fix problems in place.

## Hand-off

Load `plan-gap-interview` and run it in plan mode on this plan and its spec. Hand the plan back only after the user approves that summary. Do not start implementing or pick an execution method yourself.
