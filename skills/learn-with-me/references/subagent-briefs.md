# Subagent briefs

Two read-only explorers run in parallel after scoping. They return notes. You write the lesson. Neither may edit files, commit, push, install anything, or call a write API.

Brief them with the repo, the commit SHA (ask them to `git rev-parse HEAD` and confirm it matches), the topic, and the 3–5 intended takeaways. Ask for evidence next to every claim: a path, symbol, commit, or PR. Mark anything without evidence as inference.

## Shared rules for both briefs

- Read only. No edits, no commits, no pushes, no network writes.
- Do not paste secrets, tokens, environment values, customer data, private hostnames, or private IPs into the notes. Describe the shape instead.
- Separate **observed** (seen in code, a commit, a PR, or a doc) from **inferred** (your reading). Label each.
- Quote small snippets only when the exact shape matters; never dump a whole file.
- Stop at the context budget. Prefer 20 strong findings over 100 shallow ones.

## Brief 1: architecture explorer

```text
You are exploring <repo> at <commit> read-only. Topic: <topic>.
Return: (1) entry points and how work enters the system; (2) the components
that matter for <topic>, with the path and symbol that proves each; (3) the
data or control flow between them, in order; (4) where state lives; (5) the
main failure modes and what observes them; (6) anything that contradicts the
repo's own docs. For each item: observed or inferred, plus evidence.
Do not edit, commit, or push. Do not include secrets or internal hostnames.
```

Ask for a short component table and a numbered flow you can redraw. Request the boundary calls (function names) rather than whole functions.

## Brief 2: rationale explorer

```text
You are reading the history of <repo> around <topic>, read-only.
Use git log/show, PR titles and bodies, and docs/ADRs. Return: (1) the
decisions that shaped <topic>; (2) the alternative each decision replaced;
(3) the tradeoff accepted and the symptom that motivated it; (4) dates,
commit SHAs, and PR numbers as evidence; (5) decisions that were later
reversed. Mark observed vs inferred. No edits, commits, or pushes.
```

Useful commands: `git log --oneline -n 50 -- <path>`, `git show <sha> --stat`, `gh pr list --state all --search <term>`, `gh pr view <n>`. Read-only flags only.

## Merge

- Deduplicate. When the two briefs disagree, say so in the lesson and prefer observed evidence.
- Keep the exploration notes in your working context only. The lesson is the deliverable; do not put a research log in it.
- If a claim has no evidence, either drop it or state it as inference in the lesson.
- If the explorers cannot cover the topic at the requested depth, say what is missing before composing. Do not fill the gap with invention about a real system.