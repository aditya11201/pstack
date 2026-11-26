# Interactive animation

A scene is YAML inside a fenced `scene` block. On the page it runs on the
three.js stage; in Markdown it reads as a plain description of the sequence.
The Diagram tab stays static: node clicks open Details, and nothing animates
there.

## Rules

- **Every motion maps to an event in the prose.** If the text does not mention
  it, the scene does not animate it.
- **The reader controls it.** Every scene has at least one trigger, toggle, or
  slider. There is no autoplay-only scene.
- **One scene per step, at most.** Use it on the step where the dynamic
  behaviour is the point.
- **References must exist.** Every packet endpoint, state node, gauge node,
  spawn endpoint, and bubble target is a node or actor in this step's diagram.
  Lint rule 11 checks it.
- **Actor ids, not icons.** Mermaid nodes stay plain. The stage builds a shape
  per actor role; scenes use the same ids.
- **Stay inside the stage.** `grid` and every `place` cell must be in range,
  and `spawn` uses a known token. Lint rule 15 checks it.
- **Reduced motion** shows one static frame per hop with its narration; no
  packet is added. The facts must still read.

## Scene fields

| Field | Meaning |
|---|---|
| `title` | Short scene name. |
| `controls` | At least one `trigger` (button label), `toggle` (`id`, `label`, `default`), or `slider` (`id`, `label`, `min`, `max`, `default`). |
| `timeline` | Ordered actions. |
| `narration` | `{ at, text }` captions at a timeline position. |
| `stage` | Optional `{ grid: [w, h], place: [{ actor, at }] }` override. |

## Timeline primitives

| Primitive | Shape | Does |
|---|---|---|
| `packet` | `{ from, to, label?, ms? }` | One labelled dot along an existing edge. |
| `state` | `{ node, to }` | `idle`, `busy`, `error`, or `queued` on a node. |
| `when` | `when: <toggle id>` or `{ <slider>: ">60" }`, with `then` and optional `else` | Branch on a control. |
| `counter` | `{ id, label, sum }` | Accumulates packet `ms`; shows in the metrics bar. |
| `spawn` | `{ token, from, to, every }` | A stream of tokens; `every` is a rate or slider id. |
| `move` | `{ actor?, node?, to: [x, y] }` | Moves an actor or node to a grid cell. It does not move spawned tokens. |
| `appear`, `vanish` | `{ on }` | Fades a node or actor in or out. |
| `shake`, `glow` | `{ on }` | One shake or halo pulse. |
| `bubble` | `{ on, text }` | A short label above a node or actor. |
| `gauge` | `{ node, value }` | A load bar; `value` is `0`–`100` or a slider id. |

Tokens come from `TOKEN_STYLES`: `request`, `response`, `message`, `error`,
`user`. In `bubble` text, `{queue}` is the number of tokens still in flight;
`{<counter-id>}` reads a counter. Other braces stay literal.

## Automatic stage

Without `stage:`, the hub lays the step's diagram out left to right, one shape
per actor role. This is the default and covers most steps.

```yaml
title: Cache hit versus miss
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
      - packet: { from: cache, to: api, label: hit, ms: 20 }
    else:
      - packet: { from: api, to: db, label: query, ms: 300 }
      - state: { node: db, to: busy }
      - packet: { from: db, to: api, label: rows }
  - packet: { from: api, to: client, label: 200 OK }
  - gauge: { node: db, value: rps }
  - when: { rps: ">60" }
    then:
      - state: { node: db, to: queued }
  - counter: { id: latency, label: Latency, sum: ms }
narration:
  - at: 1
    text: The gateway checks the cache before it asks the database.
```

## Stage placement

Use `stage:` when the idea is a quantity, a crowd, or an illustration rather
than a topology: a queue growing, traffic piling up, a shelf in front of a
store. `place` puts actors at grid cells, and the same timeline runs.

```yaml
title: Why the queue grows
stage:
  grid: [12, 6]
  place:
    - { actor: users, at: [1, 3] }
    - { actor: lb, at: [5, 3] }
    - { actor: worker, at: [9, 3] }
controls:
  - trigger: Send requests
  - slider: { id: rps, label: Requests per second, min: 1, max: 100, default: 10 }
timeline:
  - spawn: { token: request, from: users, to: lb, every: rps }
  - bubble: { on: worker, text: "Queue: {queue}" }
  - when: { rps: ">60" }
    then:
      - state: { node: worker, to: queued }
      - glow: { on: worker }
narration:
  - at: 1
    text: Every token is one request still in flight toward the worker.
```

For a picture the scene format cannot express, a lesson may add `stage.mjs`.
Read `stage-authoring.md`; it is rare.

## The page around the scene

The lesson page has three columns:

- left: the lesson tree;
- centre: the metrics bar, the stage with 3D and Diagram tabs, "Reset view",
  and the step timeline;
- right: the step panel with "Step n / N", the type tag, each profile layer as
  its own labelled block, the prose, the Key idea, Details, Back/Next, and
  "You'll learn" from `outcomes`.

The scene controls sit under the stage. Without WebGL, the Diagram tab is
selected and the 3D tab is disabled with a note. With reduced motion, the stage
shows the frame list and no packet moves.

## Pick a mode

| The idea is | Use | Pattern |
|---|---|---|
| A path through components | Automatic stage, packets | `request-journey`, `auth-flow` |
| A branch with different outcomes | Automatic stage, toggle | `cache-hit-miss`, `failover` |
| Volume, pressure, or a backlog | `stage.place`, slider and spawn | `queue-under-load` |
| One event reaching many consumers | Automatic stage, or a stage crowd | `fan-out` |
| Traffic moving between versions | `stage.place`, slider | `rollout` |
| An ordered set of stages | Automatic stage, spawn | `pipeline` |

## Adapting a pattern

1. List the pattern's roles and pick the lesson actors that fill them.
2. Rename ids only if the lesson needs it; then rename them in the diagram,
   Details, and scene together.
3. Delete actions the lesson does not explain. Add a narration line for every
   state change you keep.
4. Check that the toggle or slider changes something the reader can see, and
   that the prose names that change.
5. Run lint. Rules 10, 11, 15, 16, and 17 cover scenes, stage placement, and the
   profile; they do not judge whether the scene is clear.

## Check

- Each scene has a control, and the prose names what it changes.
- Every reference is in this step's diagram.
- Reduced motion leaves the same facts readable.
- The Diagram tab shows the mermaid view with no animation.