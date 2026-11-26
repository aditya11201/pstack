---
name: learn-with-me
description: Teach a codebase visually. Use when the user says "teach me", "learn-with-me", "explain this repo's architecture", "how does this request flow work", or asks for a visual, interactive, or step-by-step lesson about a repo or system. Writes a lint-clean lesson.md into the local Astro hub, checks it, renders it on localhost, and ends the reply with the URL.
---

# learn-with-me

Turn one codebase topic into a `lesson.md`: a complete Markdown reference that also renders as a local visual page. The hub owns the schema, tokens, lint, and scan. This skill owns the guidance and the content. Nothing leaves the machine unless the user asks for that lesson to be uploaded or published.

A request to use this skill is the user's request for this outcome: a lesson committed on `lesson/<repoKey>/<slug>` in the local hub and served on localhost. That outcome includes creating or switching to that branch and making the local commit. The hub has no remote, so the commit never leaves the machine. Do not skip the commit or ask about it. It does not authorize push, upload, or publish.

## Resolve the hub

```sh
HUB=$(sed -n 's/^hub=//p' "$HOME/.config/learn-with-me/config")
HUB=${HUB:-$HOME/projects/learn-with-me}
[ -f "$HUB/package.json" ] || echo "hub missing at $HUB"
```

If the hub is missing, stop and point the user to the Phase 1 bootstrap in `references/publishing.md`. Do not write a lesson without a hub to lint and render it.

## Flow

### 1. Scope

- Fix the repo, the topic, the commit SHA, and 3–5 things the reader should leave with.
- Detect source visibility: `gh repo view <repo> --json visibility`. When unknown, treat the source as private.
- For a private source, propose a `repoKey` and get the user's OK before writing.
- Read `references/content-shape.md` for the fields and defaults, and `references/safety.md` for what never goes into a lesson.

### 2. Gather

Run the two read-only subagents in parallel, briefed from `references/subagent-briefs.md`: the architecture explorer and the rationale explorer. Keep observed facts separate from inference.

### 3. Compose

Start from `templates/lesson.md`. Read `references/content-shape.md`, `references/explaining.md`, `references/diagrams.md`, `references/visual-system.md`, `references/icons.md`, `references/gamification.md`, `references/interactive.md`, and `references/stage-authoring.md`. Pick the closest pattern in `references/patterns/`, then map its roles to this lesson's actors. Icon names go in `actors` only; mermaid nodes stay plain.

**Content profile (mandatory).** Read the `profile` in `$HUB/learn-with-me.config.json`, unless the user names one or the lesson frontmatter sets one. Then follow `references/profiles/<profile>.md`. The default, `plain-and-technical`, opens every step with an everyday analogy, then the precise terms tied back to it. Do not write a lesson from the technical layer alone.

**Visual design (mandatory).** Load `threejs-web` with the skill tool, then the specialist skills its routing table names for this lesson's stage. Choose the visual metaphor from `references/visual-system.md` and `references/stage-authoring.md`. Decide whether the automatic stage with `stage.place` is enough or the lesson needs a `stage.mjs`. The theme owns colours and type; the lesson supplies ids, roles, scenes, and labels.

### 4. Skeletons

Follow `references/code-skeleton.md`. Keep each skeleton at most 40 lines, elide with `…`, and reference every file from `lesson.md`. For a private source, write invented shapes with generic names, never trimmed source.

### 5. Write to the hub

Work on branch `lesson/<repoKey>/<slug>` and commit locally. Never push.

```sh
git -C "$HUB" switch "lesson/$repoKey/$slug" 2>/dev/null ||
  git -C "$HUB" switch -c "lesson/$repoKey/$slug"
mkdir -p "$HUB/content/$repoKey/$slug"
```

Write `content/<repoKey>/<slug>/lesson.md`, plus `skeletons/` when used. The local commit is required, not optional. Commit only that folder:

```sh
git -C "$HUB" add "content/$repoKey/$slug"
git -C "$HUB" commit -m "lesson: add $repoKey/$slug"
```

### 6. Check

In the hub, run both, with no exceptions:

```sh
npm run lint -- "content/$repoKey/$slug"
npm run scan -- "content/$repoKey/$slug"
```

Any finding blocks rendering. Fix the lesson and rerun; if a finding remains, stop and report the rule, file, and line. Claim no URL. For a scan hit, follow the incident steps in `references/safety.md`.

### 7. Render locally

Follow the local-only rules in `references/safety.md`. Check the port:

```sh
curl -s -o /dev/null -w '%{http_code}' http://localhost:4321/
```

- `000` or empty: start `npm run dev` in the background in `$HUB`, then wait until the port answers.
- Any answer: reuse the server only if it serves this hub. Its home HTML contains `data-lesson-target`, and `http://localhost:4321/<repoKey>/<slug>/` returns 200. Otherwise report the port conflict and do not claim a URL.

Start the dev server from `$HUB` and leave it running; Astro may detach it itself, so check readiness with curl, not the process.

Before reporting the URL, require the lesson commit to be visible:

```sh
git -C "$HUB" log -1 --format=%s
git -C "$HUB" status --porcelain -- "content/$repoKey/$slug"
```

The first must print `lesson: add <repoKey>/<slug>`; the second must print nothing. If either check fails, do not report success.

Confirm the lesson URL returns 200 and its HTML contains `Step 1 of`. Report the `threejs-*` skills you used, then end the reply with that URL. Do not offer or ask about uploading.

## Levels

| Level | Trigger | What happens | Leaves the machine? |
|---|---|---|---|
| Local | Default | Steps 1–7. | No. |
| Upload | The user asks to upload or back up this lesson. | Push the lesson branch and open a PR in the private hub repo. Checks run; nothing deploys. | Yes, private repo and Access-locked previews only. |
| Publish | The user asks to publish this lesson. | Upload if needed, merge by the visibility rules, deploy. | Yes, live sites. |

Read `references/publishing.md` before any upload or publish. A request to upload is not a request to publish, and the default reply must not mention either.

## This slice

Slice 1b renders each step on a three.js stage, laid out in three columns. Scenes run on the stage; the Diagram tab stays static; without WebGL the diagram and narration show; with reduced motion each hop shows as a static frame with its narration. Every step follows the active content profile.

## Never

- Push, upload, or publish without an explicit request for that lesson.
- Put icon names outside `actors`, or use mermaid `@{ icon: }`, `click`, raw HTML, MDX, or remote assets.
- Use `path:line` refs or a real `source` for a private source.
- Use company code in a sample or test lesson. Invent content.