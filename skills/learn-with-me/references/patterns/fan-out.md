# Fan-out

Use when one event reaches several consumers and each can fail or fall behind on
its own.

## Metaphors

- One announcement on a noticeboard, read by each team when it is free.
- A radio broadcast: every radio receives the same signal on its own schedule.
- A photocopier that makes one copy for each desk.

## Roles

| Id | Role | Use |
|---|---|---|
| `producer` | `service` | The component that publishes the event |
| `topic` | `queue` | The shared channel |
| `orders` | `worker` | The first consumer |
| `notify` | `worker` | The second consumer |
| `store` | `database` | The first consumer's sink |
| `sender` | `external` | The second consumer's outside target |

## Diagram skeleton

```mermaid
flowchart LR
  producer[Producer] -->|1 publish| topic[[Topic]]
  topic -->|2 deliver| orders[Orders worker]
  topic -->|3 deliver| notify[Notification worker]
  orders -->|4 write| store[(Store)]
  notify -->|5 send| sender[External sender]
```

Two consumers are enough to show independence. Add a third only if the lesson
explains a third behaviour.

## Scene

```yaml
title: One event, two consumers
controls:
  - trigger: Publish event
  - toggle: { id: notify-slow, label: Notification consumer is slow, default: false }
timeline:
  - packet: { from: producer, to: topic, label: event }
  - state: { node: topic, to: busy }
  - packet: { from: topic, to: orders, label: deliver }
  - packet: { from: orders, to: store, label: write }
  - when: notify-slow
    then:
      - state: { node: notify, to: queued }
      - bubble: { on: notify, text: Backlog grows }
    else:
      - packet: { from: topic, to: notify, label: deliver }
      - packet: { from: notify, to: sender, label: send }
  - state: { node: orders, to: idle }
narration:
  - at: 1
    text: The producer publishes once; the channel delivers a copy to each consumer.
  - at: 4
    text: A slow consumer builds its own backlog without stopping the other.
```

## What the reader controls

- **Trigger:** publishes one event.
- **Toggle:** makes the notification consumer slow, so it turns `queued` while
  the orders consumer keeps working.
- No slider: the lesson is about independence, not volume.

## Suggested quiz

```yaml
question: The notification consumer stops. What happens to the orders consumer?
options:
  - It stops too
  - It keeps processing
  - It replays the event
answer: It keeps processing
why: Each consumer reads independently, so one backlog does not block the other.
```

Challenge variant: keep the notification consumer out of `queued` while
publishing. The reader leaves the toggle off, or explains why the backlog is
still bounded.