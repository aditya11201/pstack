// pstack-checkpoint: Antigravity SessionStart / PreInvocation hook.
// Injects the same read-only checkpoint summary as the OpenCode plugin, once per change.
// Fails open: on any error it prints {} and exits 0.
import { createHash } from "node:crypto"
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath, pathToFileURL } from "node:url"

const here = dirname(fileURLToPath(import.meta.url))
const ID = /^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$/

async function checkpointModule() {
  const installed = join(here, "pstack-execution-checkpoint.js")
  const inRepo = join(here, "..", "..", "examples", "opencode2", "pstack-execution-checkpoint.js")
  return import(pathToFileURL(existsSync(installed) ? installed : inRepo).href)
}

export async function handle(input, { pluginData, env }) {
  const { readCheckpoint, checkpointContext } = await checkpointModule()
  const text = checkpointContext(await readCheckpoint(input?.cwd, env.PSTACK_RUN_ID || undefined))
  if (!text) return {}
  const inject = { injectSteps: [{ systemMessage: { systemMessage: text } }] }
  const conversation = String(input?.conversationId ?? "")
  if (!ID.test(conversation)) return input?.hookEventName === "SessionStart" ? inject : {}
  const hashFile = join(pluginData, "checkpoint-" + conversation + ".sha256")
  const hash = createHash("sha256").update(text).digest("hex")
  if (input.hookEventName !== "SessionStart" && existsSync(hashFile) && readFileSync(hashFile, "utf8") === hash) return {}
  mkdirSync(pluginData, { recursive: true })
  writeFileSync(hashFile, hash)
  return inject
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  let out = {}
  try {
    const input = JSON.parse(readFileSync(0, "utf8"))
    const pluginData = process.env.PLUGIN_DATA || join(here, "..", ".data")
    out = await handle(input, { pluginData, env: process.env })
  } catch (error) {
    process.stderr.write("pstack-checkpoint: " + String(error) + "\n")
    out = {}
  }
  process.stdout.write(JSON.stringify(out) + "\n")
}
