# Icons

Icons are optional and live in one place: the `actors` frontmatter. Mermaid
nodes stay plain. Scenes, stages, and `stage.mjs` refer to actor ids, never to
icons.

## The sixteen roles

| Role | Use for |
|---|---|
| `user` | A person using the system |
| `client` | A browser, mobile app, CLI, or SDK |
| `gateway` | An entry point that routes or admits traffic |
| `load-balancer` | A component that spreads traffic across instances |
| `service` | A process that owns behaviour or data |
| `worker` | A process that consumes work asynchronously |
| `database` | A durable relational or document store |
| `cache` | A fast store in front of a slower one |
| `queue` | A buffer between producers and consumers |
| `storage` | Object or file storage |
| `identity-provider` | A component that authenticates and issues tokens |
| `ci` | A build or test runner |
| `registry` | An artifact or image registry |
| `cluster` | A compute cluster or scheduler |
| `network` | DNS, routing, or a network boundary |
| `external` | A third party or an unknown boundary |

The hub owns the generic default for each role
(`$HUB/src/lib/icons/roles.mjs`). Never write a default icon name in a lesson;
the renderer looks it up from the role.

## Actor fields

```yaml
actors:
  - id: gateway
    role: gateway
    label: Edge gateway
  - id: db
    role: database
    label: Orders store
```

- `id`: lowercase, matches a mermaid node id in at least one step.
- `role`: from the table above.
- `label`: the reader-facing name.
- `icon`: optional brand icon. Omit it and the role's generic icon is used.

Keep the actor list to the components the lesson actually visits. Three to
eight is usually enough; the actor strip shows all of them.

## Generic versus brand

Use the generic role icon by default. A brand icon adds meaning only when the
lesson is about that specific product's behaviour, such as how a particular
broker delivers a message. If the same role could be any product, leave `icon`
out.

Do not use a brand to make a diagram look authoritative. Do not add a logo for
a product the lesson never names.

## Finding a brand icon

Use the `better-icons` CLI, then copy the id it returns:

```sh
better-icons search "<product or concept>"
better-icons get "<pack:id>"
```

Only an id from a bundled pack works: `logos`, `simple-icons`, `fluent-emoji`,
or `noto`. The hub's lint rule 12 checks that the icon exists. Put the found id
in `icon` on the matching actor, and nowhere else:

```yaml
  - id: broker
    role: queue
    label: Event broker
    icon: <pack:id>
```

If the lookup returns nothing, keep the generic role icon. Do not invent a name.

## The actor strip and the stage

The 2D actor strip is the only place an icon appears. It shows each actor's role
icon, or the brand icon when the lesson names a real product.

- The strip stays 2D. It shows without WebGL and with reduced motion, and logs
  no error.
- The 3D stage builds a generic shape per role and puts a text label on it.
  Brand logos are not extruded, attached, or built in 3D.
- `stage.mjs` does not load or draw icons. It may add a custom shape, not a
  logo.
- Extruded 3D logos are an open item and are not built. Do not add one.

The stage carries identity through the role shape, the label, and the actor id.
That is enough for the reader to connect a shape to the strip.

## Check

- Every actor id is a node in some step.
- Every `role` is in the table.
- Every `icon` was returned by the lookup and exists in a bundled pack.
- The body, diagrams, scenes, and skeletons contain no icon names.
- The stage and `stage.mjs` contain no brand icon or extruded logo.
- The strip reads as a system, not a logo wall: generic where the role is
  generic, branded only where the product is the point.