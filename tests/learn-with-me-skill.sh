#!/bin/sh
# Checks the learn-with-me skill files and that the template is lint- and scan-clean.
set -eu

ROOT=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
SKILL="$ROOT/skills/learn-with-me"
TEMPLATE="$SKILL/templates/lesson.md"
FAIL=0

pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; FAIL=1; }

# (a) SKILL.md exists and is under 120 lines.
if [ -f "$SKILL/SKILL.md" ]; then
  pass "SKILL.md exists"
  lines=$(wc -l <"$SKILL/SKILL.md" | tr -d ' ')
  if [ "$lines" -lt 120 ]; then
    pass "SKILL.md under 120 lines ($lines)"
  else
    fail "SKILL.md under 120 lines ($lines)"
  fi
else
  fail "SKILL.md exists"
fi

# (b) Eleven references, eight patterns, one template.
missing=""
for name in subagent-briefs content-shape explaining diagrams code-skeleton visual-system \
  interactive icons gamification safety publishing; do
  [ -f "$SKILL/references/$name.md" ] || missing="$missing $name.md"
done
if [ -z "$missing" ]; then
  pass "11 references exist"
else
  fail "11 references exist (missing:$missing)"
fi

missing=""
for name in request-journey cache-hit-miss queue-under-load failover fan-out rollout \
  pipeline auth-flow; do
  [ -f "$SKILL/references/patterns/$name.md" ] || missing="$missing $name.md"
done
if [ -z "$missing" ]; then
  pass "8 patterns exist"
else
  fail "8 patterns exist (missing:$missing)"
fi

if [ -f "$TEMPLATE" ]; then
  pass "templates/lesson.md exists"
else
  fail "templates/lesson.md exists"
fi

# (c) Patterns and templates stay generic: no brand icon names.
if [ -d "$SKILL/references/patterns" ] && [ -d "$SKILL/templates" ] &&
  ! grep -rEq '(logos|simple-icons):' "$SKILL/references/patterns" "$SKILL/templates"; then
  pass "patterns and templates name no brand icons"
else
  fail "patterns and templates name no brand icons"
fi

# (d) Copy the template into a temp content root and run the hub's lint and scan.
CONFIG="$HOME/.config/learn-with-me/config"
HUB=""
if [ -f "$CONFIG" ]; then
  HUB=$(sed -n 's/^hub=//p' "$CONFIG" | head -n 1)
fi
if [ -z "$HUB" ]; then
  HUB="$HOME/projects/learn-with-me"
fi

hub_ok=0
if [ -f "$HUB/scripts/lint.mjs" ] && [ -f "$HUB/scripts/scan.sh" ]; then
  hub_ok=1
  pass "hub with lint and scan found at $HUB"
else
  fail "hub with scripts/lint.mjs and scripts/scan.sh at $HUB"
fi

if [ "$hub_ok" -eq 1 ] && [ -f "$TEMPLATE" ]; then
  repo_key=$(sed -n 's/^repoKey:[[:space:]]*//p' "$TEMPLATE" | head -n 1 | tr -d '[:space:]')
  slug=$(sed -n 's/^slug:[[:space:]]*//p' "$TEMPLATE" | head -n 1 | tr -d '[:space:]')

  if [ -z "$repo_key" ] || [ -z "$slug" ]; then
    fail "template frontmatter has repoKey and slug"
  else
    tmp_root=$(mktemp -d)
    trap 'rm -rf "$tmp_root"' EXIT HUP INT TERM
    mkdir -p "$tmp_root/$repo_key/$slug"
    cp "$TEMPLATE" "$tmp_root/$repo_key/$slug/lesson.md"

    if out=$(node "$HUB/scripts/lint.mjs" "$tmp_root" 2>&1); then
      pass "template passes hub lint"
    else
      fail "template passes hub lint"
      printf '%s\n' "$out" | sed 's/^/  /'
    fi

    if out=$(sh "$HUB/scripts/scan.sh" "$tmp_root" 2>&1); then
      pass "template passes hub scan"
    else
      fail "template passes hub scan"
      printf '%s\n' "$out" | sed 's/^/  /'
    fi
  fi
elif [ "$hub_ok" -eq 1 ]; then
  fail "template available for lint and scan"
fi

if [ "$FAIL" -eq 0 ]; then
  echo "ALL PASS"
else
  echo "FAILURES"
  exit 1
fi