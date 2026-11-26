# Queue under load

Use when the lesson is about buffering, backpressure, and what happens when
arrivals outpace workers.

## Metaphors

- A line at a ticket counter with one clerk.
- A conveyor belt feeding one packer.
- Rain into a bucket with a small drain: the water level is the backlog.

## Roles

| Id | Role | Use |
|---|---|---|
| `users` | `user` | The source of work |
| `lb` | `load-balancer` | The front door that admits traffic |
| `queue` | `queue` | The buffer |
| `worker` | `worker` | The consumer that drains the buffer |
| `database` | `database` | The durable sink |

## Diagram skeleton

```mermaid
flowchart LR
  users([Users]) -->|1 request| lb[Load balancer]
  lb -->|2 enqueue| queue[[Work queue]]
  queue -->|3 pull| worker[Worker]
  worker -->|4 write| database[(Database)]
```

Show the queue depth as a bubble on the queue, not as extra nodes. One worker
node stands for the fleet.

## Stage

```yaml
title: Why the queue grows
stage:
  grid: [14, 6]
  place:
    - { actor: users, at: [1, 3] }
    - { actor: lb, at: [4, 3] }
    - { actor: queue, at: [7, 3] }
    - { actor: worker, at: [10, 3] }
    - { actor: database, at: [13, 3] }
controls:
  - trigger: Send requests
  - slider: { id: rps, label: Requests per second, min: 1, max: 100, default: 10 }
timeline:
  - spawn: { token: request, from: users, to: lb, every: rps }
  - bubble: { on: queue, text: "Depth: {queue}" }
  - when: { rps: ">60" }
    then:
      - state: { node: worker, to: queued }
      - glow: { on: queue }
    else:
      - state: { node: worker, to: busy }
narration:
  - at: 1
    text: Each tick adds one request at the rate the slider sets.
  - at: 3
    text: Above the worker's capacity, the buffer grows instead of the throughput.
```

## What the reader controls

- **Trigger:** starts the stream of requests.
- **Slider:** sets the arrival rate. At or below 60 the worker keeps up; above
  60 it turns queued and the queue bubble grows.
- No toggle: the point is volume, not a branch.

## Suggested challenge

Keep the worker out of the queued state while the stream runs, then raise the
slider until it flips. Ask the reader what a growing depth says about the
worker, not the users.

## Suggested quiz

```yaml
question: The queue depth keeps rising. What does that tell you?
options:
  - The users are sending too few requests
  - Arrivals are outrunning the worker
  - The database is empty
answer: Arrivals are outrunning the worker
why: A steady queue depth means the service rate is lower than the arrival rate.
```