# Content shape

The hub is the schema owner. Read these before writing, and never copy their contents into a lesson or into this skill:

- `$HUB/src/content.config.ts`: frontmatter fields, types, and allowed values.
- `$HUB/src/lib/icons/roles.mjs`: the role list and generic defaults.
- `$HUB/scripts/lint.mjs`: the rules that must pass.

If this reference and the hub disagree, the hub wins. File a note; do not work around lint.

## Files

```text
content/<repoKey>/<slug>/
  lesson.md
  skeletons/<file>        optional, each referenced from lesson.md
```

`repoKey` is the repo folder name, user-approved when the source is private. `slug` names the topic. Both match `^[a-z0-9-]+$` and the pair is unique in `content/`, case-insensitively. Keep both stable across updates so URLs do not change.

## Frontmatter

| Field | Rule |
|---|---|
| `schemaVersion` | Integer, starts at 1. |
| `title`, `summary` | Required, plain language, no marketing. |
| `repoKey` | Lowercase folder name, `^[a-z0-9-]+$`, approved for private sources. |
| `slug` | Lowercase, `^[a-z0-9-]+$`. |
| `visibility` | `public` or `internal`. Private source defaults to `internal`. |
| `sourceVisibility` | `public` or `private`. Detect it; do not assume. |
| `source` | `{ url, commit }`. Only when `sourceVisibility: public`. |
| `publicApproval` | `{ by, date }`. Required for `visibility: public` from a private source. |
| `actors` | `{ id, role, label, icon? }[]`. The only place icon names appear. |
| `updated` | ISO date. |

Actor rules:

- `id` matches a mermaid node id in at least one step.
- `role` comes from the hub role list. See `icons.md`.
- `label` is what the reader sees, such as "Orders service", not a class name.
- `icon` is optional and only for a real technology the lesson is about. Omit it for generic patterns and templates.

## Body anatomy

1. **Intro.** What this is and what the reader will understand. Two to four sentences.
2. **`## Step N: <title>`.** N starts at 1, no gaps, 3–12 steps. Each step has:
   - one idea, in prose that stands alone;
   - exactly one `mermaid` block;
   - a **Details** list with one `- **<id>**: <explanation>` line per important node;
   - optional one `scene` block;
   - optional `[skeletons/<file>](skeletons/<file>)` links;
   - optional `path:line` refs, public sources only.
3. **`## Recap`.** 3–5 bullets that match the scoped takeaways.

## Lint rules active now

1. Frontmatter matches the schema.
2. 3–12 steps, numbered from 1 without gaps.
3. Exactly one mermaid block per step, at most 15 nodes.
4. Each skeleton is at most 40 lines, uses `…` not `...`, and is referenced both ways.
5. A private source has no `source` and no `path:line` refs.
6. Public visibility from a private source requires `publicApproval`.
7. No raw HTML, remote images or scripts, or MDX outside code fences.
8. `repoKey`/`slug` are unique across `content/`.
9. Every step has at least one Details entry; every Details id is in that step's diagram.
12. Icon names only in `actors`; every role is in the list; every icon exists; no mermaid icon syntax.
13. No mermaid `click`.

Rules 10, 11, 14, and 15 switch on in later slices: at least one scene, scene references that match the diagram, at least one gamification block, and valid stage placement. Write to them anyway. Other authoring rules live in `explaining.md`, `diagrams.md`, and the patterns; lint cannot judge clarity.

## Block order

Put a `quiz` before the `scene` it predicts. Put an `order` or `challenge` after the scene. One scene per step at most. The Markdown must read as a complete lesson without the renderer.

## Defaults by source

| Source | `sourceVisibility` | `visibility` | `source` | `path:line` |
|---|---|---|---|---|
| Public repo | `public` | `public` | `{ url, commit }` | Allowed |
| Private repo | `private` | `internal` | Omit | No |
| Private repo, user asks for public | `private` | `public` | Omit | No |

A public lesson from a private source also needs `publicApproval`; see `publishing.md`.