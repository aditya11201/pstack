# Code skeletons

A skeleton is an illustrative shape, not a file dump. It shows the order, the boundaries, and the branch that the prose describes.

## Keep

- The function or handler signature, with types when the type is the point.
- The order of calls at the boundary the step is about.
- The one branch, loop, or retry that explains the behaviour.
- A small data shape when the response or event is the subject.
- A comment only for a reason the code cannot show, one line, starting with `why:`.

## Elide

- Bodies that do not change the idea: replace them with a line containing `…`.
- Imports, logging, metrics, dependency wiring, error translation that the step does not discuss.
- Licence headers, generated code, and framework boilerplate.
- Anything that would need a second screen to understand.

Lint rule 4: at most 40 lines per file, `…` not `...`, and every file referenced from `lesson.md`.

## Naming and location

```text
content/<repoKey>/<slug>/skeletons/<topic>.ts
```

Name the file for what it shows: `retry-on-timeout.ts`, `order-handler.ts`. One idea per file. Reference it from the step it belongs to:

```markdown
[skeletons/order-handler.ts](skeletons/order-handler.ts)
```

Every reference must exist and every file must be referenced. Lint checks both directions.

## Public versus private sources

- **Public:** you may keep real names and add small `path:line` refs. Still trim to the idea.
- **Private:** write an invented shape with generic names. Never copy a real private function, never include real hostnames, payloads, or field names. The skeleton must teach the same shape without exposing the source.

## Example

```ts
// why: the retry wraps the call, not the handler, so one request gets one budget.
export async function fetchWithRetry(path: string, attempts = 3) {
  for (let i = 1; i <= attempts; i++) {
    try {
      return await call(path)
    } catch (error) {
      if (i === attempts) throw error
      …
    }
  }
}
```

## Check

- Read it alone. Does it teach the step without the lesson text?
- Indentation and names are consistent with the prose.
- No secret, hostname, token, customer value, or company name.
- The line count is at most 40, and the elisions are `…`.