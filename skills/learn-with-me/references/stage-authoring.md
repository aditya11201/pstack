# Stage authoring

Every step gets a three.js stage built by the hub from the step's mermaid
diagram, the actor roles, the active theme's preset, and the scene's `stage:`
block. Most lessons never write three.js code. This reference says what the
stage gives you, when the automatic stage is enough, and how to add a
`stage.mjs` safely.

## What the hub builds

The hub calls:

```js
createStage(host, { actors, nodeIds, edges, place, grid, preset, onSelect })
```

- `actors`, `nodeIds`, `edges`: from the step's frontmatter and diagram.
- `place`, `grid`: from the scene's optional `stage:` block.
- `preset`: the theme's `stage.mjs` export: `{ shapes, material, outline, light,
  camera }`.
- `onSelect`: opens the Details panel when the reader clicks a shape or label.

`createStage` returns the `StageApi` below. A lesson's `stage.mjs` receives that
same object after the automatic stage is built. Do not call `createStage` from a
lesson.

## `@lwm/stage` exports

| Export | Use |
|---|---|
| `createStage` | Hub only. Builds the renderer, scene, camera, controls, and shapes. |
| `THREE` | The bundled three.js namespace. |
| `SHAPES` | Named role builders: `crowd`, `device`, `hexPrism`, `cylinderStack`, `shelf`, `boxRow`, `keyBlock`, `steps`, `tower`, `cluster`, `mesh`, `portal`, `slab`. |
| `ROLE_BUILDERS` | The default builder name per role. |
| `builderFor` | `builderFor(role, preset)` returns the builder name for a role. |
| `layoutStage` | The layer layout used by the hub: `{ positions, grid }`. |
| `TOKEN_STYLES` | The five token styles: `request`, `response`, `message`, `error`, `user`. |

## StageApi

| Member | Signature | Does |
|---|---|---|
| `addPacket` | `addPacket(from, to, { label?, kind? }) -> Promise<void>` | Sends one dot along the edge `from -> to`. `kind` is `request`, `response`, or `ghost`. Resolves on arrival. |
| `spawn` | `spawn(token, from, to, { every }) -> handle` | Starts a stream of tokens. `token` is a `TOKEN_STYLES` key; `every` is a rate or slider id. Handle: `{ setRate, stop, stats, onChange }`. |
| `move` | `move(id, [x, y])` or `move(id, otherId)` | Moves an actor or node to a grid cell, or onto another root. |
| `appear` | `appear(id, { instant? })` | Fades a root in. |
| `vanish` | `vanish(id, { instant? })` | Fades a root out. |
| `shake` | `shake(id)` | Shakes a root once. |
| `glow` | `glow(id)` | A short halo pulse. |
| `setState` | `setState(id, 'idle'\|'busy'\|'error'\|'queued')` | Sets the state ring. |
| `setGauge` | `setGauge(id, pct)` | Sets a load bar on the root, `0`–`100`. |
| `bubble` | `bubble(id, text \| null)` | Shows or clears a label above the root. |
| `pulse` | `pulse(id)` | One scale pulse. |
| `project` | `project(id) -> { x, y }` | Client coordinates of a root. Used by tests. |
| `resetCamera` | `resetCamera()` | Restores the default isometric view. |
| `cameraAzimuthDeg` | `cameraAzimuthDeg() -> number` | Rotation from the default, in degrees. |
| `builderFor` | `builderFor(id) -> THREE.Object3D \| null` | The built root for an actor or node. |
| `dispose` | `dispose()` | Hub only. Disposes the stage. |
| `THREE`, `SHAPES`, `renderer`, `scene`, `camera` | | The live objects, for advanced use. |

The stage owns one renderer, one render loop, one `ResizeObserver`, the camera
limits, and step-change disposal. Never create a second renderer or animation
loop in `stage.mjs`.

## When the automatic stage is enough

Use the scene format and `stage.place` when:

- the actors' roles already look like the parts (a database is a cylinder
  stack, a queue is a row of boxes, a cache is a shelf);
- the diagram has at most 15 nodes and the default layout reads left to right;
- the behaviour is packets, states, gauges, counters, spawn, bubble, or the
  other scene primitives;
- `stage.place` on a `[12, 6]` grid gives the picture you want.

This covers almost every lesson. Prefer it: the lesson stays in Markdown, the
theme can restyle it, and reduced motion works already.

## When to write `stage.mjs`

Write one only when the idea needs something the scene format cannot express:

- a custom object or arrangement that is the point of the step;
- a visual that must react per frame;
- a builder override for one actor, beyond the theme preset.

The Markdown must still carry every fact. The extra visual is a bonus, not the
only explanation. With reduced motion, the per-hop frames and narration must
still make sense without the custom scene.

## The file

Path: `content/<repoKey>/<slug>/stage.mjs`, next to `lesson.md`.

```js
import { THREE } from '@lwm/stage';

export default function addMarker(api) {
  const style = getComputedStyle(api.renderer.domElement);
  const accent = style.getPropertyValue('--lwm-primary-500').trim();
  const geometry = new THREE.TorusGeometry(0.5, 0.06, 8, 24);
  const material = new THREE.MeshBasicMaterial({ color: accent });
  const ring = new THREE.Mesh(geometry, material);
  ring.position.set(0, 0.2, 0);
  ring.name = 'marker-ring';
  api.scene.add(ring);

  return () => {
    api.scene.remove(ring);
    geometry.dispose();
    material.dispose();
  };
}
```

- One default export function. It receives the `StageApi`.
- The function may return a cleanup function. The hub calls it on step change
  and page leave, before it disposes the stage.
- Read theme colours from `getComputedStyle(api.renderer.domElement)`. Do not
  hard-code a palette; a different theme must still work.
- Dispose what you create that is not in `api.scene`. The stage disposes scene
  geometries and materials on teardown.
- Keep it at most 300 lines. Small is a feature.

## Lint rule 16

`stage.mjs` may import only:

- `three`;
- `three/addons/*`;
- `@lwm/stage`.

It must not contain `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`,
`eval`, `Function(`, dynamic `import(`, `document`, `window.location`, `cookie`,
`localStorage`, `sessionStorage`, `indexedDB`, or a remote URL. It has exactly
one default export, that export is a function, and the file is at most 300
lines. The scan runs on it like any other lesson file.

These are static checks, not a sandbox. Review the diff before publishing.

## Which specialist skill to load

Always start with `threejs-web` and follow its routing. Then load the rows that
match the stage work:

| Stage task | Skill |
|---|---|
| Camera, framing, resize, scene graph, transforms | `threejs-scene` |
| Custom geometry, repeated props, instancing | `threejs-geometry` |
| Materials, colour, texture, transparency | `threejs-materials` |
| Lights, shadows, environment | `threejs-lighting` |
| Motion, transitions, timing, scroll | `threejs-animation` |
| Picking, dragging, orbit controls | `threejs-interaction` |
| HTML labels, overlays, page integration | `threejs-html` |
| Keyboard, screen readers, reduced motion | `threejs-accessibility` |
| Frame time, memory, resource disposal | `threejs-performance` |
| Blank canvas, wrong colour, flicker | `threejs-debugging` |
| Browser checks and visual evidence | `threejs-testing` |

Report the skills you used in the final reply.

## Check

- The automatic stage or `stage.place` already tells the story, or the
  `stage.mjs` adds only what the scene cannot.
- Every actor in `place` exists; every token is known; every cell is inside the
  grid.
- `stage.mjs` imports only the allowlist, has one default function, and is at most
  300 lines.
- Colors come from the theme, not a literal.
- The cleanup restores anything the module changed.
- Reduced motion still leaves the facts readable.