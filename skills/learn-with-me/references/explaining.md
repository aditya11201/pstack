# Explaining

The reader is smart and new to this codebase. Write for that person.

## The active profile comes first

How a step explains is a content profile. Read the profile before writing:

1. the lesson frontmatter `profile`, if set;
2. otherwise the default in `$HUB/learn-with-me.config.json`;
3. otherwise the profile the user names.

Then follow `references/profiles/<profile>.md`. That guide owns the layer
markers, their order, and the step limit. This file holds the rules that apply
to every profile.

Two profiles ship with the hub:

- `plain-and-technical` (default): an everyday analogy first, then the precise
  terms tied back to it.
- `engineer`: technical and dense; an analogy only where it saves words.

## Rules

- **One idea per step.** If the title needs "and", split the step. A step may
  add one component, one state change, or one failure mode.
- **One name per concept.** Pick the name the code uses, or a plain equivalent,
  and use it in the prose, the diagram, the Details list, and the scenes. Never
  alternate synonyms for variety.
- **Concrete before abstract.** Start with a single run, request, or event.
  Generalise after the reader has seen it once.
- **Define jargon on first use.** If the term stays, add it to the Details list.
- **Explain the why.** A component's existence is a tradeoff. Name what would go
  wrong without it.
- **Keep observed and inferred apart.** For a real repo: "The service retries
  twice (observed: `retry.ts`). The second try likely covers a replica failover
  (inference)." Never present inference as fact.
- **Prefer short sentences and active voice.** Present tense. The reader is
  following a live system, not reading a report.
- **Mind the step budget.** Lint rejects a lesson outside its profile's range.
  If the topic needs more, split the lesson or ask the user about switching to
  `engineer`.

## Step shape

Adapted from the hub's valid fixture:

- heading `## Step N: <title>`;
- `> **Type:** problem|technique|tradeoff|recap`;
- the layers the profile requires;
- `> **Key idea:** <one sentence>`;
- a short prose paragraph that answers: what is true now, why it exists, and
  what the reader understands now;
- the mermaid diagram;
- the Details list;
- at most one scene, where the dynamic behaviour is the point.

Example of the same fact, written twice:

```text
Weak: The gateway is responsible for the routing of requests to the services.
Better: The gateway reads the path and sends the request to one service. The
service never chooses its own traffic.
```

## Avoid

- "Simply", "basically", "just", "obviously".
- A list of every field or file. Keep what the topic needs; name what you cut.
- Metaphors that are never cashed out. If you call it a "mailroom", say which
  component is the mailroom and where the mail goes.
- Marketing adjectives and claims the evidence does not support.
- A recap that introduces new material. The recap restates the scoped takeaways.

## Details lines

One line per important node. Explain that node's job in this step, not its whole
class:

```text
- **gateway**: Chooses the service from the path, then stops reading the body.
- **service**: Owns the order list and shapes the response.
```

Every id in a Details list must exist in that step's diagram. Every actor id
should appear as a node somewhere in the lesson.

## Recap

3–5 bullets, one per takeaway from step 1. If a bullet is not visible in the
steps, remove it or add the step.