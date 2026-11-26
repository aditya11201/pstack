#!/bin/sh
# Antigravity install test in throwaway HOMEs. Offline: --target antigravity makes no network calls.
#   sh tests/install-antigravity.sh <repo>
set -eu

SRC=$(cd "$1" && pwd)
WORK=$(mktemp -d)
FAIL=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; FAIL=1; }

snapshot() {
  mkdir -p "$1"
  (cd "$SRC" && git ls-files -co --exclude-standard -z | xargs -0 tar -cf - 2>/dev/null) | tar -xf - -C "$1"
}

run_install() { # home repo [args...]
  h=$1; r=$2; shift 2
  HOME=$h XDG_CONFIG_HOME=$h/.config sh "$r/install.sh" --no-rtk "$@" >"$h/out.log" 2>&1
}

entries() { python3 -c 'import json,sys;print(json.dumps([e["path"] for e in json.load(open(sys.argv[1]))["entries"]]))' "$1"; }

R=$WORK/repo; snapshot "$R"

# A: fresh install creates the plugin, merges skills.json, installs the model template.
H=$WORK/a; mkdir -p "$H/.gemini/config"
printf '{"entries":[{"path":"~/other/skills"}]}\n' >"$H/.gemini/config/skills.json"
if run_install "$H" "$R" --target antigravity; then pass "A: exit 0"; else fail "A: exit $? ($(tail -3 "$H/out.log"))"; fi
P=$H/.gemini/config/plugins/pstack
for f in plugin.json hooks.json rules/AGENTS.md hooks/git_gate.mjs hooks/checkpoint_context.mjs hooks/gated.json \
         hooks/package.json hooks/pstack-execution-checkpoint.js skills/plan-review/SKILL.md skills/execution-resume/SKILL.md .pstack-installed; do
  [ -f "$P/$f" ] && pass "A: $f" || fail "A: missing $f"
done
ls "$P/hooks" | grep -q '\.test\.mjs$' && fail "A: test files installed" || pass "A: no test files"
python3 -c 'import json,sys;[json.load(open(f)) for f in sys.argv[1:]]' "$P/plugin.json" "$P/hooks.json" && pass "A: JSON parses" || fail "A: JSON invalid"
[ "$(entries "$H/.gemini/config/skills.json")" = '["~/other/skills", "~/.agents/skills"]' ] && pass "A: skills.json merged" || fail "A: skills.json $(entries "$H/.gemini/config/skills.json")"
cmp -s "$H/.agents/pstack-models.antigravity.md" "$R/examples/pstack-models.antigravity.md" && pass "A: model template" || fail "A: model template differs"
[ -e "$H/.config/opencode" ] && fail "A: wrote OpenCode config" || pass "A: no OpenCode config"

# The installed hooks run from the plugin dir.
OUT=$(cd "$P" && printf '%s' '{"toolCall":{"name":"run_command","args":{"CommandLine":"git push"}}}' | node ./hooks/git_gate.mjs)
case "$OUT" in *'"ask"'*) pass "A: installed gate asks" ;; *) fail "A: installed gate: $OUT" ;; esac
REPO_CK=$WORK/ck; mkdir -p "$REPO_CK/.pstack/executions/r1"
printf '%s' '{"version":1,"run_id":"r1","plan":{"path":"p.md"},"tasks":[{"id":"T1","status":"pending"}],"blockers":[],"next_action":"T1"}' >"$REPO_CK/.pstack/executions/r1/state.json"
OUT=$(cd "$P" && printf '{"hookEventName":"SessionStart","cwd":"%s","conversationId":"c1"}' "$REPO_CK" | PLUGIN_DATA="$WORK/data" node ./hooks/checkpoint_context.mjs)
case "$OUT" in *'Run: r1'*) pass "A: installed checkpoint hook injects" ;; *) fail "A: installed checkpoint hook: $OUT" ;; esac

# B: rerun keeps one skills entry and a user-edited model file.
printf 'feature, refactoring: gemini-4-neon-high\n' >"$H/.agents/pstack-models.antigravity.md"
run_install "$H" "$R" --target antigravity || fail "B: rerun exit"
[ "$(entries "$H/.gemini/config/skills.json")" = '["~/other/skills", "~/.agents/skills"]' ] && pass "B: no duplicate entry" || fail "B: skills.json $(entries "$H/.gemini/config/skills.json")"
grep -q gemini-4-neon-high "$H/.agents/pstack-models.antigravity.md" && pass "B: model file kept" || fail "B: model file overwritten"

# C: a foreign plugins/pstack is kept with a warning.
H=$WORK/c; mkdir -p "$H/.gemini/config/plugins/pstack"; echo mine >"$H/.gemini/config/plugins/pstack/plugin.json"
run_install "$H" "$R" --target antigravity || fail "C: exit"
[ "$(cat "$H/.gemini/config/plugins/pstack/plugin.json")" = mine ] && pass "C: foreign plugin kept" || fail "C: foreign plugin overwritten"
grep -q 'warning: .*plugins/pstack' "$H/out.log" && pass "C: warned" || fail "C: no warning"

# D: stale build output aborts before writing.
H=$WORK/d; mkdir -p "$H"; RD=$WORK/repo-d; snapshot "$RD"
echo stale >>"$RD/agents/core/pstack-workflow.md"
if run_install "$H" "$RD" --target antigravity; then fail "D: stale build installed"; else pass "D: stale build aborts"; fi
[ -e "$H/.gemini/config/plugins/pstack" ] && fail "D: wrote plugin" || pass "D: nothing written"

# E: unknown target is rejected.
H=$WORK/e; mkdir -p "$H"
if run_install "$H" "$R" --target vim; then fail "E: bad target accepted"; else pass "E: bad target rejected"; fi

if [ "$FAIL" = 0 ]; then rm -rf "$WORK"; echo "ALL PASS"; else echo "logs kept in $WORK"; exit 1; fi
