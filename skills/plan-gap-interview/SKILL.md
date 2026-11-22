---
name: plan-gap-interview
description: Use right after an implementation plan is drafted, or when asked to review a plan for gaps. Finds the plan's gaps, resolves facts from the repo itself, interviews the user one question at a time about the remaining decisions, and waits for approval before the plan is revised or implemented.
---

# Plan gap interview

Turn a drafted plan into requirements the user has confirmed, before anyone implements it.

Load the `grilling` skill with the skill tool now if it is not loaded yet. It is the interview method. This skill adds what to ask about and when to stop.

## Rules for the whole session

- Do not write or modify code, config, tests, or any file. The only exception is the plan file, in step 5, after approval. Use read-only commands.
- Ask one question at a time. This overrides the round format in `grilling`. Use the `question` tool when it exists, with your recommended option first and labelled "(Recommended)". Without it, ask one question in chat with numbered options.
- Facts are yours, decisions are the user's. Never ask the user something the repo, config, docs, or a read-only command can answer.

## 1. Find the gaps

Read the plan and the request or spec it came from. Check each item:

1. **Coverage.** Every requirement maps to a step, and every step traces back to a requirement. Unrequested scope is a gap.
2. **Scope.** Goal, scope, and non-goals are stated.
3. **Acceptance.** Every step has an observable pass check: a command, a scenario, an expected output. "Works", "safe", or "fast" without a predicate is a gap.
4. **Step clarity.** Each step decides one concrete thing. Placeholders like "handle errors" or "add tests" are gaps. Names, types, and paths match across steps.
5. **Failure modes.** Each edge input or failure the spec implies has a step that tests it.
6. **Dependencies and environment.** What must exist first, landing order, target environment, cluster or account, secrets, versions.
7. **Risk and rollback.** Irreversible or outward-facing actions (deploy, migration, deletion, push), how to undo each one, and the blast radius.
8. **Authorization.** Who approves, and which actions need the user's explicit go.
9. **Proportion.** The plan's size fits the change.

## 2. Sort each gap

- **Fact**: the answer exists in the environment. Look it up yourself, delegating large searches to a read-only subagent. Record the answer and its source.
- **Decision**: a preference, priority, scope call, risk tolerance, or business rule. It goes to the interview.

Ask the riskiest decisions first, then the ones other decisions depend on.

## 3. Interview

Run the decision gaps through `grilling`, one question per turn. Each question states the gap, why it matters for the plan, two to four concrete options, and your recommendation.

Challenge an ambiguous answer before moving on:

- A vague word ("aman", "cepat", "seperti biasa", "nanti saja", "safe", "fast") gets a follow-up asking for its measurable meaning or the case it covers.
- An answer that contradicts the code, the plan, or an earlier answer gets both quoted back, with a question about which one wins.

After each answer, update the gap list. An answer can close other gaps or open new ones. Stop when no decision gap is left, or when the user tells you to wrap up; then list what stays open.

## 4. Summary and approval gate

Reply with:

- **Final requirements**: goal, scope, non-goals, and acceptance criteria with pass predicates.
- **Decisions** from the interview, and **facts** you resolved with their sources.
- **Plan changes**: each edit to the plan these imply.
- **ADR candidates**: decisions that are hard to reverse, surprising without context, and a real trade-off. Name them. Do not write ADR files.
- **Open items and assumptions.**

Then stop and ask for approval. Do not revise the plan, implement, or hand off before the user approves. A question or correction is not approval: update the summary and ask again.

## 5. After approval

Apply the plan changes to the plan file only. If you cannot edit files, give the revised plan in chat. Report the plan path and what changed. Implementation still needs its own explicit go.

## Attribution

The gap checklist adapts the Self-Review in `writing-plans` from [obra/superpowers](https://github.com/obra/superpowers) (MIT). The ambiguity challenge and ADR criteria adapt `domain-modeling` from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). The interview method is `grilling` from mattpocock/skills, installed separately.
