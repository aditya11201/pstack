import { test } from "node:test"
import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"
import { classify } from "./git_gate.mjs"

const here = dirname(fileURLToPath(import.meta.url))
const gated = JSON.parse(readFileSync(join(here, "gated.json"), "utf8"))

// Antigravity treats a PreToolUse output without "decision" (such as {}) as a deny,
// so a command the gate does not cover must produce no output at all.
function raw(stdin) {
  const out = spawnSync(process.execPath, [join(here, "git_gate.mjs")], { input: stdin, encoding: "utf8" })
  assert.equal(out.status, 0, out.stderr)
  return out.stdout
}
const hook = (stdin) => JSON.parse(raw(stdin))

const call = (cmd) => JSON.stringify({ hookEventName: "PreToolUse", toolCall: { name: "run_command", args: { CommandLine: cmd } } })

for (const cmd of [
  "git push origin x",
  "FOO=1 git commit -m y",
  "rtk git push",
  "cd a && terraform apply",
  "gh pr create --draft",
  "git status; git rebase main",
  "echo hi | glab mr merge 3",
]) {
  test(`asks for: ${cmd}`, () => {
    const result = hook(call(cmd))
    assert.equal(result.decision, "ask")
    assert.match(result.reason, /pstack-gate/)
  })
}

for (const cmd of ["ls", "git status", "git log", "helm lint .", "git commitizen", "echo git push"]) {
  test(`stays silent for: ${cmd}`, () => {
    assert.equal(raw(call(cmd)), "")
  })
}

test("malformed stdin asks", () => {
  assert.equal(hook("{not json").decision, "ask")
})

test("missing CommandLine asks", () => {
  assert.equal(hook(JSON.stringify({ toolCall: { name: "run_command", args: {} } })).decision, "ask")
})

test("classify names the matched prefix", () => {
  assert.deepEqual(classify("rtk git push origin main", gated), { rule: "git push" })
  assert.equal(classify("git status", gated), null)
})
