# Engineer

Use this profile when the reader already works in the codebase, or when the user
asks for a dense, technical lesson. The default profile is
`plain-and-technical`; this one trades the everyday layer for speed.

The machine rules are in `$HUB/profiles/engineer.json`: no required layers, and
3–12 steps.

## Rules

- Lead with the precise term and the mechanism: "The gateway validates the JWT,
  then routes by path prefix." No warm-up paragraph.
- Keep one idea per step, even when the step is dense. A title with "and" still
  means two steps.
- Denser steps are fine: three to six sentences, the failure mode, the tradeoff,
  and the number that makes the tradeoff real.
- An analogy is optional. Use one only where it saves words, and cash it out in
  the same paragraph. Never add a plain layer to every step out of habit.
- If you use an analogy, say where it stops holding.
- Use exact names, versions, paths, and ownership. Separate observed facts from
  inference as `explaining.md` requires.
- Details lines stay one line per node, with the precise job of that node in
  this step.
- Scene narration names the event, not the pixels: "The probe fails and the
  router switches to the replica."

## Layers

No marker pair is required. Write normal prose. A single inline picture is
enough: "The gateway is a doorman: it checks the path and sends each request to
one service." Then continue with the exact terms.

If the same lesson may later switch to `plain-and-technical`, write both layers
now; see that guide. A lesson-level `profile` in frontmatter overrides the hub
default.

## Check

- An engineer new to this repo can name the components and the failure mode
  after each step.
- Every precise claim has a source in the lesson or in the gathered facts.
- The lesson has 3–12 steps.
- Any analogy is short, cashed out, and honest about where it stops.