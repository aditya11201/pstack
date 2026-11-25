# Gamification

One block that makes the reader commit to an answer is worth more than five decorative ones. At least one gamification block per lesson (lint rule 14 in a later slice).

## Pick the block

| Block | Use it when | Reader does |
|---|---|---|
| `quiz` | The step has a prediction with a clear right answer. | Chooses an option before the scene runs. |
| `order` | The idea is a sequence: handshake, deploy, recovery. | Drags items into order. |
| `challenge` | The scene has a measurable goal and controls. | Tunes the controls until the goal holds. |

Put a `quiz` before its scene. Put an `order` or `challenge` after the scene that supplies the evidence. One block is enough; never put a quiz on every step.

## Quiz

```yaml
question: Which component turns database rows into the response?
options:
  - The browser
  - The API gateway
  - The orders service
answer: The orders service
why: The service reads the rows and shapes the response before the gateway returns it.
```

Rules:

- One correct answer, and `answer` is copied exactly from `options`.
- Three or four options. Two is a coin flip; five invites scanning.
- Distractors come from real misconceptions: the component that looks responsible but only forwards, or the one that stores without shaping.
- No "all of the above", "none of the above", joke options, or options that differ by one word.
- `why` explains the mechanism, not just "that is correct".
- Ask about behaviour the lesson teaches. Do not test trivia the reader cannot infer.
- The question works as plain Markdown; no images or formatting tricks.

## Order

```yaml
items:
  - Build the artifact
  - Run the checks
  - Publish the artifact
  - Deploy to the cluster
why: A deploy consumes what the checks approved, so the artifact is fixed before the last step.
```

Rules:

- List items in the correct order; the renderer shuffles them.
- Four to six items, each one short phrase.
- Each item is a distinct stage, not a sub-step of another.
- `why` names the dependency that fixes the order.

## Challenge

```yaml
goal: { counter: latency, below: 200 }
hint: The cache removes the slow hop for repeated reads.
why: A cache lowers latency only when the hit rate is high enough to skip the store.
```

Rules:

- The `goal` refers to a counter or control in the same scene.
- The goal is reachable with the controls the reader has, and the scene can fail it.
- `hint` points at the mechanism without giving the setting.
- `why` states the principle the reader should keep.
- Do not hide a required step behind a challenge. The lesson text already explains it.

## Progress, XP, badges

- Each passed block adds XP. Finishing every block in a lesson marks it complete.
- A complete lesson gets a badge on the home page.
- Progress lives in `localStorage` only. No account, no server, no leaderboard.
- Retries are allowed and cost nothing. Show the result and `why` after each attempt.
- Never make the page unusable without JavaScript; the Markdown is the reference and the blocks read as plain questions.
- Do not tie progress to time spent, scroll depth, or repeated clicks. Only a passed block counts.

## This slice

Slice 1a renders `quiz`, `order`, and `challenge` as readable cards. They are not interactive yet. Still write them: they are part of the reference, they are reviewed, and later slices switch them on. Do not describe the card state in the lesson text.