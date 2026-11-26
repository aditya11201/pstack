import { test } from "node:test"
import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const here = dirname(fileURLToPath(import.meta.url))

function repoWith(runs) {
  const root = mkdtempSync(join(tmpdir(), "pstack-ag-"))
  for (const [id, state] of Object.entries(runs)) {
    const dir = join(root, ".pstack", "executions", id)
    mkdirSync(dir, { recursive: true })
    writeFileSync(join(dir, "state.json"), typeof state === "string" ? state : JSON.stringify(state))
  }
  return root
}

function state(id, next = "T1/S1") {
  return {
    version: 1,
    run_id: id,
    plan: { path: "docs/plans/p.md" },
    tasks: [{ id: "T1", status: "in_progress" }, { id: "T2", status: "pending" }],
    blockers: [],
    next_action: next,
  }
}

function hook(event, cwd, { data, env = {}, conversationId = "conv1" } = {}) {
  const out = spawnSync(process.execPath, [join(here, "checkpoint_context.mjs")], {
    input: JSON.stringify({ hookEventName: event, cwd, conversationId }),
    encoding: "utf8",
    env: { ...process.env, PSTACK_RUN_ID: "", PLUGIN_DATA: data ?? mkdtempSync(join(tmpdir(), "pstack-data-")), ...env },
  })
  assert.equal(out.status, 0, out.stderr)
  return JSON.parse(out.stdout)
}

const injected = (result) => result.injectSteps?.[0]?.systemMessage?.systemMessage ?? ""

test("one run: SessionStart injects the run", () => {
  const text = injected(hook("SessionStart", repoWith({ run1: state("run1") })))
  assert.match(text, /Run: run1/)
  assert.match(text, /untrusted repository data/)
})

test("same state on PreInvocation is not injected again", () => {
  const root = repoWith({ run1: state("run1") })
  const data = mkdtempSync(join(tmpdir(), "pstack-data-"))
  assert.match(injected(hook("SessionStart", root, { data })), /run1/)
  assert.deepEqual(hook("PreInvocation", root, { data }), {})
})

test("changed state is injected on PreInvocation", () => {
  const root = repoWith({ run1: state("run1") })
  const data = mkdtempSync(join(tmpdir(), "pstack-data-"))
  hook("SessionStart", root, { data })
  writeFileSync(join(root, ".pstack/executions/run1/state.json"), JSON.stringify(state("run1", "T2/S1")))
  assert.match(injected(hook("PreInvocation", root, { data })), /T2\/S1/)
})

test("zero runs: nothing", () => {
  assert.deepEqual(hook("SessionStart", repoWith({})), {})
})

test("two runs without PSTACK_RUN_ID: nothing", () => {
  assert.deepEqual(hook("SessionStart", repoWith({ a: state("a"), b: state("b") })), {})
})

test("two runs with PSTACK_RUN_ID: the pinned run", () => {
  const text = injected(hook("SessionStart", repoWith({ a: state("a"), b: state("b") }), { env: { PSTACK_RUN_ID: "b" } }))
  assert.match(text, /Run: b/)
})

test("corrupt state.json: nothing, exit 0", () => {
  assert.deepEqual(hook("SessionStart", repoWith({ run1: "{broken" })), {})
})

test("malformed stdin: nothing, exit 0", () => {
  const out = spawnSync(process.execPath, [join(here, "checkpoint_context.mjs")], { input: "nope", encoding: "utf8" })
  assert.equal(out.status, 0)
  assert.deepEqual(JSON.parse(out.stdout), {})
})

test("invalid conversationId: SessionStart only, no hash file", () => {
  const root = repoWith({ run1: state("run1") })
  const data = mkdtempSync(join(tmpdir(), "pstack-data-"))
  assert.match(injected(hook("SessionStart", root, { data, conversationId: "../x" })), /run1/)
  assert.deepEqual(hook("PreInvocation", root, { data, conversationId: "../x" }), {})
})
