#!/bin/sh
# Migration test for install.sh in throwaway HOMEs.
#   sh tests/install-migration.sh <repo>
# Needs node/npx and python3; installs skills from the repo and from GitHub.
set -eu

SRC=$(cd "$1" && pwd)
WORK=$(mktemp -d)
FAIL=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; FAIL=1; }

# Current tree, including uncommitted edits, copied to $1.
snapshot() {
  mkdir -p "$1"
  (cd "$SRC" && git ls-files -co --exclude-standard -z | xargs -0 tar -cf - 2>/dev/null) | tar -xf - -C "$1"
}

plugins() { python3 -c 'import json,sys;print(" ".join(json.load(open(sys.argv[1])).get("plugins",[])))' "$1"; }

run_install() { # home repo [args...]
  h=$1; r=$2; shift 2
  HOME=$h XDG_CONFIG_HOME=$h/.config sh "$r/install.sh" --no-rtk "$@" >"$h/out.log" 2>&1
}

# A: plugin removed, other settings and pins kept, ponytail added.
H=$WORK/a; mkdir -p "$H/.config/opencode"; snapshot "$WORK/repo-a"
printf '{"shell":"zsh","plugins":["cc-safety-net@2.5.0","superpowers@git+https://github.com/obra/superpowers.git"]}\n' >"$H/.config/opencode/opencode.json"
run_install "$H" "$WORK/repo-a"
P=$(plugins "$H/.config/opencode/opencode.json")
case "$P" in *superpowers*) fail "A: superpowers still present: $P" ;; *) pass "A: superpowers removed" ;; esac
case "$P" in *cc-safety-net@2.5.0*) pass "A: pinned cc-safety-net kept" ;; *) fail "A: pin lost: $P" ;; esac
case "$P" in *ponytail*) pass "A: ponytail added" ;; *) fail "A: ponytail missing: $P" ;; esac
grep -q '"shell": "zsh"' "$H/.config/opencode/opencode.json" && pass "A: shell kept" || fail "A: shell lost"

# B: a differently pinned superpowers spec is removed and reported.
H=$WORK/b; mkdir -p "$H/.config/opencode"
printf '{"plugins":["superpowers@git+https://github.com/obra/superpowers.git#v5"]}\n' >"$H/.config/opencode/opencode.json"
run_install "$H" "$WORK/repo-a"
grep -q 'removed plugin: superpowers@git+https://github.com/obra/superpowers.git#v5' "$H/out.log" && pass "B: reported" || fail "B: no removed plugin line"
case "$(plugins "$H/.config/opencode/opencode.json")" in *superpowers*) fail "B: still present" ;; *) pass "B: removed" ;; esac

# C: old copies from this repo are listed, removed only with the flag; other sources kept.
H=$WORK/c; R=$WORK/repo-c; mkdir -p "$H/.config/opencode" "$H/.codex" "$R"
(cd "$SRC" && git archive e0f4caa) | tar -x -C "$R"
# Two agents share ~/.agents/skills, as on a real machine.
HOME=$H npx -y skills add "$R" -g -a opencode -a codex --skill brainstorming -y >/dev/null 2>&1
HOME=$H npx -y skills add obra/superpowers -g -a opencode --skill systematic-debugging -y >/dev/null 2>&1
[ -d "$H/.agents/skills/brainstorming" ] && [ -d "$H/.agents/skills/systematic-debugging" ] || fail "C: seeding failed"
rm -rf "$R"; snapshot "$R"
run_install "$H" "$R"
grep -q 'old skill from this repo: brainstorming' "$H/out.log" && pass "C: listed without flag" || fail "C: not listed"
[ -d "$H/.agents/skills/brainstorming" ] && pass "C: kept without flag" || fail "C: removed without flag"
run_install "$H" "$R" --remove-old-skills
grep -q 'removed old skill: brainstorming' "$H/out.log" && [ ! -d "$H/.agents/skills/brainstorming" ] && pass "C: removed with flag" || fail "C: not removed with flag"
grep -q 'kept systematic-debugging: installed from' "$H/out.log" && [ -d "$H/.agents/skills/systematic-debugging" ] && pass "C: other source kept" || fail "C: other source not kept"

# D: rerun removes nothing and exits 0.
if run_install "$H" "$R" --remove-old-skills; then pass "D: rerun exit 0"; else fail "D: rerun failed"; fi
grep -q '^removed' "$H/out.log" && fail "D: rerun removed something" || pass "D: rerun removed nothing"

# E: --target opencode installs the same files as install.sh before --target existed (59482f1),
# and writes nothing for Antigravity.
files() { (cd "$1" && find .config/opencode .agents -type f ! -name .skill-lock.json ! -name '*.pyc' | sort); }
H1=$WORK/e-old; H2=$WORK/e-new; RO=$WORK/repo-old; mkdir -p "$H1" "$H2" "$RO"
(cd "$SRC" && git archive 59482f1) | tar -x -C "$RO"
run_install "$H1" "$RO" || fail "E: old install failed"
run_install "$H2" "$WORK/repo-a" --target opencode || fail "E: new install failed"
files "$H1" >"$WORK/e-old.txt"; files "$H2" >"$WORK/e-new.txt"
if cmp -s "$WORK/e-old.txt" "$WORK/e-new.txt"; then pass "E: same OpenCode files"; else
  fail "E: OpenCode files differ"; diff "$WORK/e-old.txt" "$WORK/e-new.txt" || true; fi
[ -e "$H2/.gemini" ] && fail "E: wrote .gemini" || pass "E: no .gemini"

if [ "$FAIL" = 0 ]; then rm -rf "$WORK"; echo "ALL PASS"; else echo "logs kept in $WORK"; exit 1; fi
