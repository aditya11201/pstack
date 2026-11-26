// pstack-gate: Antigravity PreToolUse hook for run_command.
// Asks before the commands examples/opencode.jsonc gates in OpenCode (list in gated.json).
// Fails closed: anything it cannot read gets "ask".
import { readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const ASSIGNMENT = /^[A-Za-z_][A-Za-z0-9_]*=\S*$/

export function classify(commandLine, gated) {
  for (const segment of commandLine.split(/&&|\|\||;|\||\n/)) {
    const words = segment.trim().split(/\s+/).filter(Boolean)
    while (words.length && ASSIGNMENT.test(words[0])) words.shift()
    if (words[0] === "rtk") words.shift()
    const command = words.join(" ")
    for (const prefix of gated) {
      if (command === prefix || command.startsWith(prefix + " ")) return { rule: prefix }
    }
  }
  return null
}

const ask = (reason) => ({ decision: "ask", reason: "pstack-gate: " + reason })

export function decide(stdin, gated) {
  let input
  try {
    input = JSON.parse(stdin)
  } catch {
    return ask("could not read the tool call; approve manually")
  }
  const commandLine = input?.toolCall?.args?.CommandLine
  if (typeof commandLine !== "string") return ask("no command line found; approve manually")
  const match = classify(commandLine, gated)
  return match ? ask(match.rule + " needs approval") : {}
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  let out
  try {
    const gated = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), "gated.json"), "utf8"))
    out = decide(readFileSync(0, "utf8"), gated)
  } catch (error) {
    process.stderr.write(String(error) + "\n")
    out = ask("hook error; approve manually")
  }
  process.stdout.write(JSON.stringify(out) + "\n")
}
