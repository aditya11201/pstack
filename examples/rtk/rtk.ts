// RTK OpenCode plugin — rewrites shell commands via `rtk rewrite`
// (single source of truth: the rtk binary). Fail-open: any rewrite failure
// passes the original command through unchanged.
//
// Note: `rtk rewrite` prints the rewritten command but exits non-zero
// (observed exit 3 on success), so the exit status is ignored; only stdout
// is used.
//
// V2 status (verified 2026-10-12 on OpenCode 2.0.24): the hook fires and the
// rewrite runs, but the shell-hook event mutation does not reach execution
// (same for tool.execute.before input mutation, nested or whole-object).
// The plugin stays loaded fail-open until the host honors event mutations;
// revisit on an OpenCode upgrade.

import { spawnSync } from "node:child_process"

interface PluginContext {
  shell: {
    hook(
      name: "create.before",
      fn: (event: { command: string }) => Promise<void> | void
    ): Promise<unknown>
  }
}

function resolveRtkBinary(): string {
  const candidates = ["/opt/homebrew/bin/rtk", "/usr/local/bin/rtk", "/usr/bin/rtk"]
  for (const candidate of candidates) {
    const probe = spawnSync(candidate, ["--version"], { encoding: "utf8" })
    if (!probe.error && probe.stdout) return candidate
  }
  return "rtk"
}

function rewrite(rtkBin: string, command: string): string | undefined {
  const result = spawnSync(rtkBin, ["rewrite", command], {
    encoding: "utf8",
    maxBuffer: 1024 * 1024,
  })
  const rewritten = String(result.stdout ?? "").trim()
  return rewritten.length > 0 && rewritten !== command ? rewritten : undefined
}

export default {
  id: "rtk",
  async setup(ctx: PluginContext) {
    const rtkBin = resolveRtkBinary()
    await ctx.shell.hook("create.before", (event) => {
      const rewritten = rewrite(rtkBin, event.command)
      if (rewritten) event.command = rewritten
    })
  },
}
