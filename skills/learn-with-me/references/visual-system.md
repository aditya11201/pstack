# Visual system

The renderer owns the look. The lesson supplies meaning: ids, roles, states, and narration. Never put CSS, HTML, colours, or fonts in `lesson.md`.

## Token owner

`$HUB/src/styles/tokens.css` is the only copy of the design tokens. Read it before designing scenes or choosing labels. Do not restate token values in the skill or in a lesson; if a token is missing, raise it against the hub.

The direction those tokens encode:

- JetBrains Mono, 13 px base.
- Background `#f4ebe0`, foreground `#1d1b18`, primary `#cfe3b2`.
- Flat surfaces with thin offset shadows; radii 3, 6, 9, 12.
- A left sidebar tree and a numbered horizontal step timeline.
- Motion durations of 150 ms and 300 ms.
- Reduced motion shows static frames with the narration.

Use the direction to judge a lesson: quiet surfaces, one accent, type and spacing doing the hierarchy. Do not copy the reference site's logo, copy, or assets.

## What the lesson controls

| Lesson input | Visual result |
|---|---|
| Actor `role` | The generic icon in the actor strip, and the default for matching nodes. |
| Actor `label` | The readable name in the strip and the Details panel. |
| Mermaid node ids | Click targets that open Details; icons attach by id. |
| Scene `state` | `idle`, `busy`, `error`, `queued` on a node, drawn by the renderer. |
| Scene `packet` | A labelled dot on the edge between two nodes. |
| Scene `counter` | A number that accumulates over the run. |
| Scene `narration` | A caption at a timeline position. |
| Gamification blocks | Quiz, ordering, and challenge cards, with XP in later slices. |

## Rules

- Ids are stable and lowercase. Renaming an id breaks Details, icons, and scenes at once.
- One accent per lesson. Do not use scene states for decoration; `busy`, `error`, and `queued` mean what they say.
- Narrate the event, not the pixels. "The gateway checks the cache first", not "the green dot moves right".
- Keep labels short enough to sit in a node. Put the explanation in Details.
- Motion durations belong to the renderer. Do not ask for a specific speed in a scene.
- The Markdown must read well without any of this. The page adds behaviour, never content the Markdown lacks.

## Check

- Open the rendered step beside the Markdown. Every visual state maps to a sentence.
- With reduced motion, the same facts are readable from the frames and narration.
- No lesson text refers to a colour or an animation that only the page has.