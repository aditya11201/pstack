#!/bin/sh
# Install the pstack workflow for OpenCode, Antigravity, or both.
# Safe to rerun: files are overwritten with the repo version, config is merged.
#
#   ./install.sh            # everything, for OpenCode and Antigravity
#   ./install.sh --target opencode|antigravity|all
#   ./install.sh --no-rtk   # skip the RTK plugin and rules
#   ./install.sh --remove-old-skills
#                           # also remove skill copies this repo installed under
#                           # their old names (they are listed on every run)
#
# Prerequisites: node/npx, python3, opencode. Optional: agy (Antigravity), rtk binary,
# Orca app. --target antigravity makes no network calls.
set -eu

REPO=$(cd "$(dirname "$0")" && pwd)
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
GEMINI_CONFIG="${GEMINI_CONFIG:-$HOME/.gemini/config}"
WITH_RTK=1
REMOVE_OLD=0
TARGET=all
while [ $# -gt 0 ]; do
  case "$1" in
    --no-rtk) WITH_RTK=0 ;;
    --remove-old-skills) REMOVE_OLD=1 ;;
    --target) shift; TARGET=${1:-} ;;
    --target=*) TARGET=${1#--target=} ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done
case "$TARGET" in
  opencode|antigravity|all) ;;
  *) echo "unknown target: $TARGET (use opencode, antigravity, or all)" >&2; exit 2 ;;
esac

step() { printf '\n==> %s\n' "$1"; }

step "Generated agent files are current"
python3 "$REPO/scripts/build_agents.py" --check

install_opencode() {

step "Skills: pstack, method skills, plan-gap-interview (from this repo)"
npx -y skills add "$REPO" -g -a opencode --skill '*' -y

step "Skill: grilling (mattpocock/skills)"
npx -y skills add mattpocock/skills --skill grilling -g -a opencode -y

step "Agent and command"
mkdir -p "$CONFIG/agents" "$CONFIG/commands"
cp "$REPO/agents/pstack-engineer.md" "$CONFIG/agents/"
cp "$REPO/examples/commands/plan-review.md" "$CONFIG/commands/"
cp "$REPO/examples/commands/execution-resume.md" "$CONFIG/commands/"

step "OpenCode 2 persistent checkpoint plugin"
mkdir -p "$CONFIG/plugins"
CHECKPOINT_PLUGIN="$CONFIG/plugins/pstack-execution-checkpoint.js"
if [ -e "$CHECKPOINT_PLUGIN" ] && ! grep -q '^// pstack-execution-checkpoint-v2' "$CHECKPOINT_PLUGIN"; then
  echo "warning: custom checkpoint plugin exists at $CHECKPOINT_PLUGIN; kept unchanged"
else
  cp "$REPO/examples/opencode2/pstack-execution-checkpoint.js" "$CHECKPOINT_PLUGIN"
  echo "installed native OpenCode 2 plugin: $CHECKPOINT_PLUGIN"
fi

step "Model mapping (kept if it already exists)"
if [ -e "$HOME/.agents/pstack-models.md" ]; then
  echo "kept existing ~/.agents/pstack-models.md"
else
  cp "$REPO/examples/pstack-models.md" "$HOME/.agents/pstack-models.md"
  echo "installed ~/.agents/pstack-models.md; edit it to your providers"
fi

step "Plugins merged into $CONFIG/opencode.json"
python3 - "$CONFIG" "$REPO/examples/opencode.global.json" <<'PY'
import json, sys
from pathlib import Path
config, example = Path(sys.argv[1]), Path(sys.argv[2])
if (config / "opencode.jsonc").exists() and not (config / "opencode.json").exists():
    sys.exit("opencode.jsonc found: merge the plugins from examples/opencode.global.json by hand")
target = config / "opencode.json"
data = json.loads(target.read_text()) if target.exists() else {"$schema": "https://opencode.ai/config.json"}
wanted = json.loads(example.read_text())["plugins"]
plugins = data.get("plugins", [])
name = lambda spec: spec.split("@git+")[0] if "@git+" in spec else spec.rsplit("@", 1)[0] if spec.rfind("@") > 0 else spec
have = {name(p) for p in plugins if isinstance(p, str)}
added = [p for p in wanted if name(p) not in have]
dropped = [p for p in plugins if isinstance(p, str) and name(p) == "superpowers"]
for p in dropped:
    print("removed plugin:", p)
data["plugins"] = [p for p in plugins if p not in dropped] + added
target.write_text(json.dumps(data, indent=2) + "\n")
print("added:", added or "nothing, all present")
PY

step "Old method skill names"
OLD_SKILLS=$(python3 - "$HOME/.agents/.skill-lock.json" "$REPO" <<'PY'
import json, sys
from pathlib import Path
lock, repo = Path(sys.argv[1]), sys.argv[2]
skills = json.loads(lock.read_text()).get("skills", {}) if lock.exists() else {}
for old in ["brainstorming", "writing-plans", "systematic-debugging",
            "test-driven-development", "verification-before-completion"]:
    entry = skills.get(old)
    if not entry:
        continue
    if entry.get("source") == repo:
        print(old)
    else:
        print("kept %s: installed from %s" % (old, entry.get("source")), file=sys.stderr)
PY
)
if [ -z "$OLD_SKILLS" ]; then
  echo "none from this repo"
else
  for s in $OLD_SKILLS; do echo "old skill from this repo: $s"; done
  if [ "$REMOVE_OLD" = 1 ]; then
    for s in $OLD_SKILLS; do
      # No -a: ~/.agents/skills is shared by several agents, and removing only the
      # opencode link leaves the folder in place.
      npx -y skills remove "$s" -g -y >/dev/null
      if [ -e "$HOME/.agents/skills/$s" ]; then
        echo "warning: $s still present in ~/.agents/skills; remove it by hand"
      else
        echo "removed old skill: $s"
      fi
    done
  else
    echo "kept; rerun with --remove-old-skills to remove them"
  fi
fi

if [ "$WITH_RTK" = 1 ]; then
  step "RTK plugin and rules"
  mkdir -p "$CONFIG/plugins" "$HOME/.claude"
  cp "$REPO/examples/rtk/rtk.ts" "$CONFIG/plugins/rtk.ts"
  cp "$REPO/examples/rtk/RTK.md" "$HOME/.claude/RTK.md"
  touch "$HOME/.claude/CLAUDE.md"
  grep -qx '@RTK.md' "$HOME/.claude/CLAUDE.md" || printf '@RTK.md\n' >> "$HOME/.claude/CLAUDE.md"
  command -v rtk >/dev/null 2>&1 || echo "warning: rtk binary not found; install it from https://github.com/rtk-ai/rtk"
fi
}

install_antigravity() {
step "Antigravity plugin"
PLUGIN="$GEMINI_CONFIG/plugins/pstack"
if [ -e "$PLUGIN" ] && [ ! -e "$PLUGIN/.pstack-installed" ]; then
  echo "warning: $PLUGIN was not installed by this repo; kept unchanged"
else
  mkdir -p "$PLUGIN"
  cp -R "$REPO/antigravity/." "$PLUGIN/"
  rm -f "$PLUGIN"/hooks/*.test.mjs
  cp "$REPO/examples/opencode2/pstack-execution-checkpoint.js" "$PLUGIN/hooks/"
  touch "$PLUGIN/.pstack-installed"
  echo "installed $PLUGIN"
fi

step "Skill root in $GEMINI_CONFIG/skills.json"
python3 - "$GEMINI_CONFIG/skills.json" <<'PY'
import json, sys
from pathlib import Path
target = Path(sys.argv[1])
data = json.loads(target.read_text()) if target.exists() else {}
entries = data.setdefault("entries", [])
if any(e.get("path") == "~/.agents/skills" for e in entries):
    print("~/.agents/skills already listed")
else:
    entries.append({"path": "~/.agents/skills"})
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n")
    print("added ~/.agents/skills")
PY
[ -e "$HOME/.agents/skills/spec-first/SKILL.md" ] || echo "warning: pstack skills not found in ~/.agents/skills; run ./install.sh --target opencode first"

step "Antigravity model mapping (kept if it already exists)"
mkdir -p "$HOME/.agents"
if [ -e "$HOME/.agents/pstack-models.antigravity.md" ]; then
  echo "kept existing ~/.agents/pstack-models.antigravity.md"
else
  cp "$REPO/examples/pstack-models.antigravity.md" "$HOME/.agents/pstack-models.antigravity.md"
  echo "installed ~/.agents/pstack-models.antigravity.md; run /setup-pstack in Antigravity to fill it"
fi
command -v agy >/dev/null 2>&1 || echo "warning: agy not found on PATH; files are installed for when Antigravity is"
}

case "$TARGET" in
  opencode) install_opencode ;;
  antigravity) install_antigravity ;;
  all) install_opencode; install_antigravity ;;
esac

step "Done"
if [ "$TARGET" != antigravity ]; then
cat <<'EOF'
OpenCode, per project: merge examples/opencode.jsonc into the project's opencode.jsonc
(disables the Superpowers plugin there in case it is still installed, and gates
commit/push/deploy commands).
Then pick the pstack-engineer agent in OpenCode and a parent model in /models.
EOF
fi
if [ "$TARGET" != opencode ]; then
cat <<'EOF'
Antigravity: the pstack plugin is on in every workspace from the next turn.
Turn it off with `agy plugin disable pstack` or on its plugin page.
Run /setup-pstack in Antigravity to choose models.
EOF
fi
