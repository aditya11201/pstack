# Rollout

Use when two versions run side by side and traffic moves between them, with a
rollback path.

## Metaphors

- Two lanes on a bridge and a sign that moves cars from one lane to the other.
- A new recipe served at a few tables before the whole room.
- A dimmer switch that moves light from one lamp to another.

## Roles

| Id | Role | Use |
|---|---|---|
| `client` | `client` | The caller |
| `router` | `load-balancer` | The component that splits traffic |
| `old` | `service` | The version serving most traffic |
| `new` | `service` | The version receiving the new share |
| `ci` | `ci` | The builder |
| `registry` | `registry` | Where the built artifact lives |

## Diagram skeleton

```mermaid
flowchart LR
  client([Client]) -->|1 request| router[Router]
  router -->|2 stable| old[Version A]
  router -->|3 canary| new[Version B]
  ci[CI] -->|4 build| registry[Registry]
  registry -->|5 image| new
```

The build path explains what the new version runs. Keep it out of the traffic
diagram only when a previous step already showed it.

## Stage

```yaml
title: Moving traffic to the new version
stage:
  grid: [12, 6]
  place:
    - { actor: ci, at: [2, 1] }
    - { actor: registry, at: [5, 1] }
    - { actor: client, at: [1, 4] }
    - { actor: router, at: [4, 4] }
    - { actor: old, at: [8, 3] }
    - { actor: new, at: [8, 5] }
controls:
  - trigger: Send traffic
  - slider: { id: share, label: New version share, min: 0, max: 100, default: 10 }
timeline:
  - spawn: { token: request, from: client, to: router, every: 8 }
  - when: { share: ">0" }
    then:
      - state: { node: new, to: busy }
      - gauge: { node: new, value: share }
    else:
      - state: { node: new, to: idle }
  - when: { share: "<100" }
    then:
      - state: { node: old, to: busy }
    else:
      - state: { node: old, to: idle }
  - when: { share: ">50" }
    then:
      - bubble: { on: new, text: Most traffic }
narration:
  - at: 1
    text: The slider is the traffic split; the router sends each request to one version.
  - at: 4
    text: Raising the share moves more requests without restarting either version.
```

## What the reader controls

- **Trigger:** starts the traffic stream.
- **Slider:** sets the share of new-version traffic. The new version's gauge
  follows it, and a version turns `idle` when its share reaches zero.
- No toggle: the slider is the split.

## Suggested quiz

```yaml
question: The new version starts failing. What is the fastest safe action?
options:
  - Restart the old version
  - Set the new share back to zero and roll back
  - Wait for the next deploy
answer: Set the new share back to zero and roll back
why: Moving traffic off the failing version restores service without touching the healthy one.
```

Challenge variant: move the share in small steps and keep the old version warm
until the new one has served enough traffic.