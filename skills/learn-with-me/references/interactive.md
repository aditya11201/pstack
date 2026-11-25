# Interactive animation

A scene is YAML inside a fenced `scene` block. It animates the step's diagram, or an illustrated stage, under the reader's control. In Markdown it reads as a plain description of the sequence.

## Rules

- **Every motion maps to an event in the prose.** If the text does not mention it, the scene does not animate it.
- **The reader controls it.** A scene has a trigger, a toggle, or a slider. There is no autoplay-only scene.
- **One scene per step, at most.** Use it on the step where the dynamic behaviour is the point.
- **References must exist.** Every `packet` endpoint and every `state` node is a node in this step's diagram. Every toggle id and slider id is stable and lowercase.
- **Actor ids, not icons.** Mermaid nodes stay plain. A node whose id matches an actor id gets that actor's icon from the frontmatter. Scenes use the same ids.
- **Quiz before the scene** when the scene reveals the answer. The scene unlocks after the answer in later slices.
- **Reduced motion** must leave the facts readable: static frames plus the narration.

## Diagram mode

Use it when the step is about a path, a branch, or a hop between components.

```yaml
title: Cache miss versus hit
controls:
  - trigger: Send request
  - toggle: { id: cache, label: Cache warm, default: false }
  - slider: { id: rps, label: Requests per second, min: 1, max: 50, default: 5 }
timeline:
  - packet: { from: client, to: api, label: GET /orders }
  - state: { node: api, to: busy }
  - when: cache
    then:
      - packet: { from: api, to: cache, label: lookup }
      - packet: { from: cache, to: api, label: hit, ms: 150 }
    else:
      - packet: { from: api, to: db, label: query, ms: 300 }
      - state: { node: db, to: busy }
      - packet: { from: db, to: api, label: rows }
  - packet: { from: api, to: client, label: 200 OK }
  - counter: { id: latency, label: Latency, sum: ms }
narration:
  - at: 1
    text: The gateway checks the cache before it asks the database.
```

Fields:

| Field | Meaning |
|---|---|
| `title` | Short scene name. |
| `controls` | At least one `trigger` (button), `toggle` (`id`, `label`, `default`), or `slider` (`id`, `label`, `min`, `max`, `default`). |
| `timeline` | Ordered actions: `packet`, `state`, `when`/`then`/`else`, `counter`. |
| `narration` | `{ at, text }` captions at a timeline position. |

- `packet`: `{ from, to, label, ms }`. `ms` is an optional duration for that hop.
- `state`: `{ node, to }`, where `to` is `idle`, `busy`, `error`, or `queued`.
- `when`: names a toggle id, or compares a slider (`{ rps: ">60" }`). `then` and `else` hold action lists.
- `counter`: `{ id, label, sum }`, where `sum` names the field to add, such as `ms` or a queue length.

## Stage mode

Use it when the idea is a quantity, a crowd, or an illustration rather than a topology: a queue growing, traffic shifting, requests piling up. A scene with `stage:` animates sprites on a grid instead of the diagram.

```yaml
title: Why the queue grows
stage:
  grid: [12, 6]
  place:
    - { actor: users, at: [1, 3] }
    - { actor: lb, at: [5, 3] }
    - { actor: worker, at: [9, 3] }
controls:
  - slider: { id: rps, label: Requests per second, min: 1, max: 100, default: 10 }
timeline:
  - spawn: { token: request, from: users, to: lb, every: rps }
  - when: { rps: ">60" }
    then:
      - state: { node: worker, to: queued }
      - bubble: { on: worker, text: "Queue: {queue}" }
```

- `grid`: `[columns, rows]`. Every `at` is `[column, row]` inside it.
- `place`: `{ actor, at }`, and the actor id must exist in the frontmatter.
- Tokens: `request`, `response`, `message`, `error`, `user`.
- Extra actions: `spawn` (repeated sprites, `every` a slider id), `move`, `appear`, `vanish`, `shake`, `glow`, `bubble` (`on`, `text`).
- Conditions may compare slider values, as in `{ rps: ">60" }`.

## Pick a mode

| The idea is | Use | Pattern |
|---|---|---|
| A path through components | Diagram | `request-journey`, `auth-flow` |
| A branch with different outcomes | Diagram + toggle | `cache-hit-miss`, `failover` |
| Volume, pressure, or a growing backlog | Stage + slider | `queue-under-load` |
| One event reaching many consumers | Diagram, or stage for the crowd | `fan-out` |
| Traffic moving between versions | Stage + slider | `rollout` |
| An ordered set of stages | Stage or diagram | `pipeline` |

## Adapting a pattern

1. List the pattern's roles and pick the lesson actors that fill them.
2. Rename ids only if the lesson needs it; then rename them in the diagram, Details, and scene together.
3. Delete actions the lesson does not explain. Add a narration line for every state change you keep.
4. Check that the toggle or slider changes something the reader can see, and that the prose names that change.

## This slice

Slice 1a renders `scene` as a readable card labelled "interactive in a later release". The lesson still includes the scene, the controls, the narration, and the gamification blocks. They are part of the Markdown reference and are validated in later slices. Do not skip them, and do not describe the card in the lesson text.