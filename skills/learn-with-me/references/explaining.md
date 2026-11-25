# Explaining

The reader is smart and new to this codebase. Write for that person.

## Rules

- **Plain definition first.** Say what the thing is in one sentence before how it works. "A queue is a buffer that holds work until a worker is free." Then the mechanism.
- **One idea per step.** If the title needs "and", split the step. A step may add one component, one state change, or one failure mode.
- **One name per concept.** Pick the name the code uses, or a plain equivalent, and use it in the prose, the diagram, the Details list, and the scenes. Never alternate synonyms for variety.
- **Concrete before abstract.** Start with a single run, request, or event. Generalise after the reader has seen it once.
- **Explain the why.** A component's existence is a tradeoff. Name what would go wrong without it.
- **Keep observed and inferred apart.** For a real repo: "The service retries twice (observed: `retry.ts`). The second try likely covers a replica failover (inference)." Never present inference as fact.
- **Define jargon on first use.** If the term stays, add it to the Details list.
- **Prefer short sentences and active voice.** Present tense. The reader is following a live system, not reading a report.

## Step shape

Aim for 2–5 sentences of prose, then the diagram, then Details. The prose answers:

1. What is true now that was not true in the previous step?
2. Why does this component or step exist?
3. What does the reader now understand that they did not?

Example of the same fact, written twice:

```text
Weak: The gateway is responsible for the routing of requests to the services.
Better: The gateway reads the path and sends the request to one service. The
service never chooses its own traffic.
```

## Avoid

- "Simply", "basically", "just", "obviously".
- A list of every field or file. Keep what the topic needs; name what you cut.
- Metaphors that are never cashed out. If you call it a "mailroom", say which component is the mailroom and where the mail goes.
- Marketing adjectives and claims the evidence does not support.
- A recap that introduces new material. The recap restates the scoped takeaways.

## Details lines

One line per important node. Explain that node's job in this step, not its whole class:

```text
- **gateway**: Chooses the service from the path, then stops reading the body.
- **service**: Owns the order list and shapes the response.
```

Every id in a Details list must exist in that step's diagram. Every actor id should appear as a node somewhere in the lesson.

## Recap

3–5 bullets, one per takeaway from step 1. If a bullet is not visible in the steps, remove it or add the step.