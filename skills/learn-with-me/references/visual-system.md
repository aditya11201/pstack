# Visual system

The renderer and the active theme own the look. The lesson supplies meaning:
ids, roles, states, narration, and the metaphor. Never put CSS, HTML, colours,
or fonts in `lesson.md`.

## Theme modules

The hub has two swappable modules:

- **Content profile** (`.config.profile`): how the lesson explains. See
  `references/profiles/`.
- **Theme** (`.config.theme`): how the page and stage look.

A theme is `$HUB/src/themes/<name>/` with three files:

| File | Holds |
|---|---|
| `tokens.css` | Custom properties scoped to `[data-theme="<name>"]`, including `--lwm-role-<role>` for every role. |
| `stage.mjs` | `preset = { shapes, material, outline, light, camera }`. `shapes` picks a builder per role; `material` is `toon`, `lambert`, or `basic`. |
| `theme.json` | `{ layout: "three-column" }`. |

Read the default from `$HUB/learn-with-me.config.json`. A lesson's frontmatter
`theme` overrides it. The resolved name goes on `<body data-theme>`. The two
shipped themes are `paper` (default: warm paper, ink outlines) and `ink` (dark,
high contrast, `basic` material, different `service` and `database` builders).

Do not copy token values into the skill or the lesson. Point at the theme.

## Fixed within a theme

These are settled by the theme and the renderer. A lesson does not override them:

- tokens, type scale, spacing, radii, shadows, and contrast;
- motion durations (150 ms and 300 ms) and the reduced-motion frames;
- the three-column layout: lesson tree, stage with metrics and timeline, step
  panel;
- the camera rules: isometric default, ±45° azimuth, limited tilt and zoom,
  "Reset view", and a reset on step change;
- labels stay readable and are HTML buttons that open Details.

A different theme may change all of them except the interaction rules below.

## Free

These are chosen per topic, not by the theme:

- the shapes and the visual metaphor: a queue as people at a counter, a
  pipeline as a conveyor, a cache as a shelf beside a desk;
- which actors and nodes carry the story;
- the scene and its controls;
- the automatic stage, `stage.place`, or a rare `stage.mjs`.

## Interaction rules

- Every motion maps to an event in the text. If the prose does not mention it,
  the scene does not animate it.
- The reader controls the scene: a trigger, a toggle, or a slider. No
  autoplay-only scene.
- A scene state means what it says. `busy`, `error`, and `queued` are not
  decoration.
- Narrate the event, not the pixels: "The gateway checks the cache first", not
  "the green dot moves right".
- Reduced motion leaves the same facts readable in the frames and narration.
- The Markdown reads well without any of this. The page adds behaviour, never
  content the Markdown lacks.

## The reference is a quality bar

The design reference uses a warm background, JetBrains Mono, flat surfaces with
thin offset shadows, a left sidebar tree, and a numbered horizontal timeline.
That is an example of the quality bar, not a template.

Copy no logo, no copy, and no assets from the reference site. Keep the craft:
quiet surfaces, one accent, type and spacing doing the hierarchy, no decoration
for its own sake.

## What the lesson controls

| Lesson input | Visual result |
|---|---|
| Actor `role` | The 3D builder for that role and the 2D icon in the actor strip. |
| Actor `id` | The link between diagrams, Details, scenes, and stage roots. |
| Mermaid node ids | Click targets and the stage layout. |
| `stage.place` | Grid positions that override the automatic layout. |
| Scene `state` | `idle`, `busy`, `error`, or `queued` on a node. |
| Scene `packet` / `spawn` | Tokens on an edge. |
| Scene `gauge` | A load bar on a node. |
| Scene `counter` | A number in the metrics bar. |
| Scene `narration` | A caption at a timeline position. |
| `outcomes` | The "You'll learn" list in the step panel. |

## Rules

- Ids are stable and lowercase. Renaming an id breaks Details, scenes, and the
  stage at once.
- One accent per lesson. State colours are meaning, not style.
- Keep labels short enough to sit on a shape. Put the explanation in Details.
- Read theme colours from the tokens in `stage.mjs`; no colour literals there.
- Do not ask for a specific animation speed in a scene. Timing belongs to the
  renderer.

## Check

- Open the rendered step beside the Markdown. Every visual state maps to a
  sentence.
- With reduced motion, the same facts are readable from the frames and
  narration.
- Switch `theme` from `paper` to `ink` in the config. The page colours and the
  stage preset change, and no lesson file changes.
- No lesson text refers to a colour or an animation that only the page has.