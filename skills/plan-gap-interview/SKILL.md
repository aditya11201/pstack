---
name: plan-gap-interview
description: Use right after an implementation plan is written, when asked to review a plan for gaps, or when the user adds a requirement or task after the spec was approved. Checks the plan against its approved spec, resolves facts from the repo itself, interviews the user one question at a time about new decisions only, and waits for approval.
---

# Plan gap interview

Keep the spec and the plan aligned with what the user confirmed. The requirements interview happens earlier, in `brainstorming`; this skill only asks about decisions that the spec has not settled.

Load the `grilling` skill with the skill tool now if it is not loaded yet. It is the interview method. This skill decides what to ask and when to stop.

## Modes

- **Plan mode**: a plan was just written (by `writing-plans` or a pstack playbook), or the user asks to review a plan.
- **Change mode**: after the spec was approved, the user adds a requirement, a task, or a scope change. This includes during plan review and during implementation.

## Rules for the whole session

- Do not write or modify code, config, or tests. The only files you may edit are the spec in `docs/specs/` and the plan in `docs/plans/`, and only as these steps say. Use read-only commands for everything else.
- Ask one question at a time. This overrides the round format in `grilling`. Use the `question` tool when it exists, with your recommended option first and labelled "(Recommended)". Without it, ask one question in chat with numbered options.
- Facts are yours, decisions are the user's. Never ask something the repo, config, docs, or a read-only command can answer.
- Do not re-ask a decision the approved spec already records, unless something new conflicts with it. Then quote both and ask which one wins.

## Plan mode

1. Read the plan and the spec it links to. When there is no spec (a small task, or a plan from another source), use the request as the spec and say so.
2. Check the plan against the spec:
   1. **Coverage.** Every spec requirement maps to a task, and every task traces back to a requirement. Unrequested scope is a gap.
   2. **Acceptance.** Every task has an observable pass check: a command, a scenario, an expected output.
   3. **Step clarity.** No placeholders like "handle errors" or "add tests". Names, types, and paths match across tasks.
   4. **Failure modes.** Each edge input or failure the spec implies has a task that tests it.
   5. **Dependencies and environment.** Landing order, target environment, secrets, versions.
   6. **Risk and rollback.** Irreversible or outward-facing actions and how to undo each one.
   7. **Authorization.** Which actions need the user's explicit go.
3. Sort each gap. A **fact** you look up and record with its source. A gap the plan can close without a new decision you mark as a plan edit. A **decision** the spec does not settle goes to the interview.
4. If no decision gap is left, skip the interview and go to the summary.

## Change mode

1. Stop work on the current task at its nearest safe boundary. Do not implement the new item.
2. Restate the new item in one sentence, and name what it touches: spec sections, plan tasks, finished work.
3. Run the plan-mode check on the touched parts only.
4. If the item opens no new decision (for example "also document it in the README"), skip the interview and confirm it in one line in the summary.
5. If the item is a new subsystem, recommend a separate spec and plan instead of growing this one, and ask.

## Interview

Run the decision gaps through `grilling`, one question per turn, riskiest first, then the ones other decisions depend on. Each question states the gap, why it matters, two to four concrete options, and your recommendation.

Challenge an ambiguous answer before moving on:

- A vague word ("aman", "cepat", "seperti biasa", "nanti saja", "safe", "fast") gets a follow-up asking for its measurable meaning or the case it covers.
- An answer that contradicts the code, the spec, or an earlier answer gets both quoted back, with a question about which one wins.

After each answer, update the gap list. Stop when no decision gap is left, or when the user tells you to wrap up; then list what stays open.

## Summary and approval gate

Reply with:

- **Requirements**: in plan mode, the final requirements with pass predicates; in change mode, the new item and the requirements it changes.
- **Decisions** from the interview, and **facts** you resolved with their sources.
- **Spec changes** and **plan changes**: each edit, by section or task.
- **ADR candidates**: decisions that are hard to reverse, surprising without context, and a real trade-off. Name them. Do not write ADR files.
- **Open items and assumptions.**

Then stop and ask for approval of the summary only, for example "Setujui ringkasan ini? Setelah disetujui saya perbarui spec dan plan saja." Do not edit the spec or plan, implement, or hand off before the user approves. A question or correction is not approval: update the summary and ask again.

## After approval

1. In change mode, update the spec first and add a dated entry under its `## Changes` section.
2. Update the plan so every task still traces to the spec.
3. Report both paths and what changed, then end your turn.

Approval of the summary approves the spec and plan edits only. It is never an instruction to implement. Do not load `test-driven-development`, edit code, or run a mutating command in the same turn.

- **Plan mode:** close with exactly this, in the user's language: "Plan siap di `<plan path>`. Ketik perintah implementasi kalau mau mulai." Never write "after approval, implementation starts" or anything like it.
- **Change mode:** if the user had already told you to implement before the new item arrived, resume implementation from the first task the change touches. Otherwise close the same way as plan mode.

## Attribution

The gap checklist adapts the Self-Review in `writing-plans` from [obra/superpowers](https://github.com/obra/superpowers) (MIT). The ambiguity challenge and ADR criteria adapt `domain-modeling` from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). The interview method is `grilling` from mattpocock/skills, installed separately.
