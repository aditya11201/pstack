---
name: spec-first
description: Use when asked for a plan, spec, or design, or before building a feature or changing behavior. Agrees on intent, sizes the work, and produces an approved design (in chat for small changes, a spec file in docs/specs/ for larger ones) before any plan or code.
---

# Spec first

Nothing gets built until the user has approved a design, and the size of the design matches the size of the work. This skill ends at an approved design. Plans come from `plan-from-spec`, code comes later.

## 1. Pin down intent

- Read what already exists before asking anything: the files involved, docs, recent commits, earlier answers in this session.
- Write back, in a few lines:
  - the outcome the user wants;
  - who it is for;
  - what done looks like;
  - the known constraints.

  Mark what they said and what you assumed. Let them correct it.
- Ask only what the repo cannot answer, and ask one question per turn. Use the `question` tool when it exists, with your recommended option first.

## 2. Size the work and say it

Pick one size and tell the user, so they can overrule it:

| Size | When | Artifact |
|---|---|---|
| **Probe** | "Can we…?", "is it possible…?". The answer matters, not the code. | 2–3 sentences: the question and how you will test it. Code you write is throwaway. |
| **Small** | A contained change to a flow that already exists in this repo. | A short design in chat: the approach, the files touched, how it will be checked. |
| **Large** | A new project or subsystem, changed interfaces, or work across components or teams. | A spec file, then a plan. |

If unsure, pick the larger size. If the work turns out bigger mid-task, stop and move up a size. Never move down.

## 3. Design

- **Probe and small:** present the design, then stop. Continue only after the user says yes.
- **Large:**
  1. Offer two or three approaches with their trade-offs, and recommend one.
  2. Present the chosen design in short sections, and check each with the user before the next. Cover:
     - units with one purpose each;
     - the interfaces between them;
     - data flow;
     - failure handling;
     - how it will be verified.
  3. Follow existing patterns in the repo. Include a refactor only when the work needs it.

## 4. Write the spec (large only)

Save it to `docs/specs/YYYY-MM-DD-<topic>-design.md` unless the user names another place. Do not commit it unless the user authorizes that.

The spec contains:

- **Goal**, **Scope** (with what is out of scope), **Approach**.
- **Acceptance**: observable checks, each one a command, a scenario, or an expected output.
- **`## Authorizations`** with three lists. Fill them from what the user said. When the work has outward actions and the user has not said, ask one question about it:
  - **Allowed without asking**: the executor does the action, then reports. Examples: commit and push a work branch, open or update a draft MR, update tickets, read-only cloud checks.
  - **Ask first**: each item needs its own go. Examples: merge, apply, deploy, starting or stopping shared resources.
  - **Forbidden**: the executor never does these. Example: editing pipeline scripts.
- **Open items**: what is still undecided.
- **`## Changes`**: starts empty. Every requirement added after approval gets a dated entry here.

Before showing the spec, reread it and fix these in place:

1. No placeholders such as "TBD", "TODO", or "handle errors".
2. No two sections contradict each other.
3. The scope fits one plan. If it does not, propose splitting it into separate specs.
4. Each requirement has only one reading.
5. Every outward action the work needs appears in exactly one Authorizations list.

## 5. Gate

End the turn with the spec path and ask for review. Even if the user asked for "spec and plan", stop here.

- **Corrections:** apply them, rerun the reread, and ask again.
- **Approval:** load `plan-from-spec`. Approval of a spec approves writing the plan only. It never authorizes implementation, so never phrase the gate as "approve and I'll implement".
- **Small path:** after approval of the chat design, implement it with `test-first` and `evidence-before-done`. Probe path: report findings as a recommendation.

Each new request gets its own sizing and its own approval. Approval of one request does not carry over to a follow-up.
