import test from "node:test"
import assert from "node:assert/strict"
import { mkdtemp, mkdir, writeFile, rm, symlink } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import plugin, { readCheckpoint, checkpointContext } from "./pstack-execution-checkpoint.js"

async function fixture(t, id = "feature") {
  const root = await mkdtemp(join(tmpdir(), "pstack-oc2-"))
  t.after(() => rm(root, { recursive: true, force: true }))
  const path = join(root, "docs", "executions", id)
  await mkdir(path, { recursive: true })
  const state = {
    version: 1, run_id: id, plan: { path: "docs/plans/auth.md" },
    tasks: [
      { id: "T1", status: "complete" },
      { id: "T2", status: "blocked" },
    ],
    blockers: [{ id: "B1", message: "CI unavailable", status: "open" }],
    next_action: "Retry CI after approval",
  }
  await writeFile(join(path, "state.json"), JSON.stringify(state))
  return { root, path, state }
}

test("loads active run and summarizes current progress", async (t) => {
  const { root } = await fixture(t)
  const state = await readCheckpoint(root, "")
  assert.equal(state.completed, 1)
  assert.equal(state.total, 2)
  assert.deepEqual(state.remaining, ["T2:blocked"])
  assert.match(checkpointContext(state), /CI unavailable/)
})

test("fails closed on ambiguous runs instead of choosing the newest", async (t) => {
  const { root } = await fixture(t)
  await mkdir(join(root, "docs/executions/another"), { recursive: true })
  await writeFile(join(root, ".pstack/executions/another/state.json"), "{}")
  assert.equal(await readCheckpoint(root, ""), null)
  assert.equal((await readCheckpoint(root, "feature")).run, "feature")
})

test("reads legacy state before migration and rejects duplicate run IDs", async (t) => {
  const { root, path } = await fixture(t)
  const oldParent = join(root, ".pstack", "executions")
  await mkdir(oldParent, { recursive: true })
  const oldPath = join(oldParent, "feature")
  const { rename, cp } = await import("node:fs/promises")
  await rename(path, oldPath)
  const legacy = await readCheckpoint(root, "feature")
  assert.equal(legacy.relative, ".pstack/executions/feature")
  await cp(oldPath, path, { recursive: true })
  assert.equal(await readCheckpoint(root, "feature"), null)
})

test("does not follow symlinked state outside the project", async (t) => {
  const { root, path } = await fixture(t)
  const outside = await mkdtemp(join(tmpdir(), "pstack-oc2-outside-"))
  t.after(() => rm(outside, { recursive: true, force: true }))
  await writeFile(join(outside, "state.json"), JSON.stringify({}))
  await rm(join(path, "state.json"))
  await symlink(join(outside, "state.json"), join(path, "state.json"))
  assert.equal(await readCheckpoint(root, "feature"), null)
})

test("registers V2 context and compaction hooks and uses session location", async (t) => {
  const { root } = await fixture(t)
  const hooks = new Map()
  const getCalls = []
  await plugin.setup({
    session: {
      get: async ({ sessionID }) => {
        getCalls.push(sessionID)
        return { location: { directory: root } }
      },
      hook: async (name, callback) => { hooks.set(name, callback) },
    },
  })
  assert.deepEqual([...hooks.keys()], ["context", "compaction"])
  for (const name of hooks.keys()) {
    const event = { sessionID: "ses-test", system: [] }
    await hooks.get(name)(event)
    assert.equal(event.system.length, 1)
    assert.match(event.system[0].text, /Run: feature/)
    assert.match(event.system[0].text, /Completed: 1\/2/)
  }
  assert.deepEqual(getCalls, ["ses-test", "ses-test"])
})

test("does not inject when the session has no checkpoint", async () => {
  const hooks = new Map()
  await plugin.setup({
    session: {
      get: async () => ({ location: { directory: "/unavailable/path" } }),
      hook: async (name, callback) => { hooks.set(name, callback) },
    },
  })
  const event = { sessionID: "ses-test", system: [] }
  await hooks.get("context")(event)
  assert.deepEqual(event.system, [])
})
