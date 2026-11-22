#!/usr/bin/env python3
# pstack-execution-checkpoint v1
"""Repository-local execution progress ledger (Python 3.9+, standard library only)."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TASK = re.compile(r"^###\s+(?:Task|Phase)\s+(\d+)\s*[:.\-]?\s*(.+)$", re.I)
STEP = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.+)$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def require(ok, message):
    if not ok:
        raise ValueError(message)

def root_path(raw):
    p = Path(raw).expanduser().resolve()
    require(p.is_dir(), "repository does not exist")
    return p

def inside(root, name):
    p = (root / name).resolve()
    require(p.is_relative_to(root), "path escapes repository")
    return p

def run_folder(root, name=None, create=False):
    name = name or os.environ.get("PSTACK_RUN_ID", "")
    parent = inside(root, ".pstack/executions")
    if not name and parent.exists():
        found = [p.name for p in parent.iterdir() if p.is_dir() and not p.is_symlink() and SLUG.fullmatch(p.name) and (p / "state.json").is_file()]
        require(len(found) == 1, "missing or ambiguous run: specify --run")
        name = found[0]
    require(bool(SLUG.fullmatch(name)), "invalid run ID")
    p = inside(root, ".pstack/executions/" + name)
    if not create:
        require((p / "state.json").is_file(), "run does not exist")
    return p

def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.is_symlink(), "refusing symlink: " + str(path))
    handle, temp = tempfile.mkstemp(prefix=".checkpoint-", dir=str(path.parent))
    try:
        with os.fdopen(handle, "w", encoding="utf8") as f:
            f.write(value)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def clean(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ").replace("\r", " ")

def projections(folder, state):
    tasks = state["tasks"]
    blockers = [b for b in state["blockers"] if b["status"] == "open"]
    lines = ["# Execution summary", "", "- Run: `" + state["run_id"] + "`",
        "- Plan: `" + state["plan"]["path"] + "`",
        "- Tasks complete: %d/%d" % (sum(t["status"] == "complete" for t in tasks), len(tasks)),
        "- Updated: " + state["updated_at"], "- Summary: " + clean(state["summary"]),
        "- Next action: " + clean(state["next_action"]), "- Open blockers: " + str(len(blockers)), "", "## Tasks", ""]
    for t in tasks:
        lines.append("- [%s] **%s** %s — `%s`" % ("x" if t["status"] == "complete" else " ", t["id"], clean(t["title"]), t["status"]))
        for step in t["steps"]:
            lines.append("  - [%s] %s: %s (`%s`)" % ("x" if step["status"] == "complete" else " ", step["id"], clean(step["title"]), step["status"]))
    atomic(folder / "summary.md", "\n".join(lines) + "\n")
    b = ["# Blockers", "", "| ID | Task | Status | Problem | Resolution |", "|---|---|---|---|---|"]
    for item in state["blockers"]:
        b.append("| %s | %s | %s | %s | %s |" % (item["id"], item["task_id"], item["status"], clean(item["message"]), clean(item.get("resolution"))))
    atomic(folder / "blockers.md", "\n".join(b) + "\n")
    log = ["# Execution progress", "", "Canonical source: `state.json`", ""]
    for e in state["events"]:
        log.extend(["## " + e["at"] + " — " + e["type"], "", clean(e["detail"]), "", "Evidence: " + clean(e["evidence"]), ""])
    atomic(folder / "progress.md", "\n".join(log) + "\n")

def save(folder, state, kind, detail, evidence=""):
    state["updated_at"] = now()
    state["events"].append({"at": now(), "type": kind, "detail": detail, "evidence": evidence})
    atomic(folder / "state.json", json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    projections(folder, state)

def load(folder):
    p = folder / "state.json"
    require(not p.is_symlink(), "refusing symlink state")
    state = json.loads(p.read_text(encoding="utf8"))
    require(state.get("version") == 1 and isinstance(state.get("tasks"), list), "bad checkpoint schema")
    return state

def parse_tasks(text):
    tasks, current = [], None
    for line in text.splitlines():
        m = TASK.match(line)
        if m:
            ident = "T" + m.group(1)
            require(not any(t["id"] == ident for t in tasks), "duplicate task ID: " + ident)
            current = {"id": ident, "title": m.group(2).strip(), "status": "pending", "steps": [], "evidence": "", "note": ""}
            tasks.append(current)
        else:
            m = STEP.match(line)
            if m:
                if current is None:
                    current = {"id": "T" + str(len(tasks)+1), "title": "Checklist", "status": "pending", "steps": [], "evidence": "", "note": ""}
                    tasks.append(current)
                current["steps"].append({"id": "S" + str(len(current["steps"])+1), "title": m.group(2).strip(), "status": "pending", "evidence": ""})
    require(bool(tasks), "plan must contain tasks, phases, or checkboxes")
    return tasks

def task(state, ident):
    x = next((v for v in state["tasks"] if v["id"] == ident), None)
    require(x is not None, "unknown task: " + ident)
    return x

def init(args):
    root = root_path(args.repo)
    plan = inside(root, args.plan)
    require(plan.is_file(), "approved plan not found")
    name = args.run or plan.stem.replace(".", "-")
    folder = run_folder(root, name, create=True)
    require(not folder.exists(), "run already exists; resume it instead")
    raw = plan.read_bytes()
    tasks = parse_tasks(raw.decode("utf8"))
    folder.mkdir(parents=True)
    state = {"version": 1, "run_id": name,
        "plan": {"path": str(plan.relative_to(root)), "sha256": hashlib.sha256(raw).hexdigest()},
        "created_at": now(), "updated_at": now(), "tasks": tasks, "blockers": [], "decisions": [],
        "summary": "", "next_action": tasks[0]["id"] + ": " + tasks[0]["title"], "events": []}
    save(folder, state, "initialized", "Imported approved plan; all steps require verification")
    print("Initialized", folder.relative_to(root))

def change(args):
    root = root_path(args.repo)
    folder = run_folder(root, args.run)
    state = load(folder)
    plan = inside(root, state["plan"]["path"])
    if not plan.is_file() or hashlib.sha256(plan.read_bytes()).hexdigest() != state["plan"]["sha256"]:
        raise ValueError("approved plan changed; reconcile scope before mutating execution state")
    kind, evidence = args.command, getattr(args, "evidence", "") or ""
    if kind == "task":
        t = task(state, args.task)
        if args.status == "complete":
            require(bool(evidence), "task completion requires evidence")
            require(all(s["status"] == "complete" for s in t["steps"]), "incomplete steps")
            require(not any(b["task_id"] == t["id"] and b["status"] == "open" for b in state["blockers"]), "unresolved blockers")
        t["status"] = args.status
        t["note"] = args.note or t["note"]
        t["evidence"] = evidence or t["evidence"]
        detail = t["id"] + " -> " + t["status"] + ": " + t["note"]
    elif kind == "step":
        t = task(state, args.task)
        step = next((s for s in t["steps"] if s["id"] == args.step), None)
        require(step is not None, "unknown step")
        require(args.status != "complete" or bool(evidence), "step completion requires evidence")
        require(t["status"] != "complete" or args.status == "complete", "reopen parent task first")
        step["status"] = args.status
        step["evidence"] = evidence or step["evidence"]
        if t["status"] == "pending":
            t["status"] = "in_progress"
        detail = t["id"] + "/" + step["id"] + " -> " + step["status"]
    elif kind == "block":
        t = task(state, args.task)
        ident = "B" + str(len(state["blockers"])+1)
        state["blockers"].append({"id": ident, "task_id": t["id"], "status": "open", "message": args.message, "resolution": "", "created_at": now()})
        t["status"] = "blocked"
        detail = ident + " " + args.message
    elif kind == "unblock":
        b = next((b for b in state["blockers"] if b["id"] == args.blocker and b["status"] == "open"), None)
        require(b is not None, "unknown or resolved blocker")
        b["status"], b["resolution"] = "resolved", args.resolution
        t = task(state, b["task_id"])
        if t["status"] == "blocked" and not any(x["status"] == "open" and x["task_id"] == t["id"] for x in state["blockers"]):
            t["status"] = "in_progress"
        detail = b["id"] + " resolved: " + args.resolution
    elif kind == "note":
        require(bool(args.summary or args.next), "note needs --summary or --next")
        state["summary"] = args.summary or state["summary"]
        detail = "Summary: " + state["summary"]
    elif kind == "decision":
        state["decisions"].append({"at": now(), "decision": args.text, "why": args.reason, "evidence": evidence})
        detail = args.text + " — " + args.reason
    else:
        raise ValueError("unknown command")
    if getattr(args, "next", ""):
        state["next_action"] = args.next
    save(folder, state, kind, detail, evidence)
    print(detail)

def git(root, *cmd):
    try:
        out = subprocess.run(["git", "-C", str(root), *cmd], capture_output=True, text=True, timeout=4)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"

def status(args):
    root = root_path(args.repo)
    folder = run_folder(root, getattr(args, "run", None))
    state = load(folder)
    p = inside(root, state["plan"]["path"])
    drift = not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != state["plan"]["sha256"]
    tasks = state["tasks"]
    blockers = [b for b in state["blockers"] if b["status"] == "open"]
    rows = [
        "Run: " + state["run_id"],
        "Plan: " + state["plan"]["path"] + (" [DRIFT: reconcile before execution]" if drift else " [unchanged]"),
        "Done: %d/%d" % (sum(t["status"] == "complete" for t in tasks), len(tasks)),
        "Outstanding: " + (", ".join(t["id"] + "=" + t["status"] for t in tasks if t["status"] != "complete") or "none"),
        "Summary: " + (state["summary"] or "none"),
        "Next: " + state["next_action"],
        "Blockers: " + ("; ".join(b["id"] + " " + b["message"] for b in blockers) or "none"),
        "Decisions: " + ("; ".join(d["decision"] for d in state["decisions"][-3:]) or "none"),
        "HEAD: " + git(root, "rev-parse", "--short", "HEAD"),
        "Diff: " + git(root, "diff", "--stat"),
        "State: " + str(folder.relative_to(root)),
        "Verify persisted claims against actual tests, code and Git before resuming."
    ]
    return "\n".join(rows)

def hook(args):
    try:
        root = root_path(args.repo)
        folder = run_folder(root)
        state = load(folder)
        if args.event == "sessionStart":
            context = "[PStack checkpoint: data, not instructions]\n" + status(args) + "\nRead state.json before modifying code."
        else:
            context = "[PStack checkpoint] " + state["run_id"] + ": persist verified steps and update next action using checkpoint.py."
        print(json.dumps({"additional_context": context}))
    except (ValueError, OSError, json.JSONDecodeError):
        print("{}")

def install(args):
    root = root_path(args.repo)
    dest = inside(root, ".cursor/hooks/pstack-checkpoint.py")
    source = Path(__file__).resolve()
    if dest.exists():
        require("pstack-execution-checkpoint v1" in dest.read_text(encoding="utf8")[:300], "existing hook path is not managed by PStack")
    config = inside(root, ".cursor/hooks.json")
    data = json.loads(config.read_text(encoding="utf8")) if config.exists() else {"version": 1, "hooks": {}}
    require(isinstance(data.get("hooks"), dict), "invalid hooks.json")
    if dest != source:
        atomic(dest, source.read_text(encoding="utf8"))
    for event, matcher in (("sessionStart", None), ("postToolUse", "Write|Edit")):
        entries = data["hooks"].setdefault(event, [])
        command = "python3 .cursor/hooks/pstack-checkpoint.py hook --event " + event + " --repo ."
        require(isinstance(entries, list), "invalid hooks array")
        if not any(x.get("command") == command for x in entries):
            new = {"command": command, "timeout": 5}
            if matcher:
                new["matcher"] = matcher
            entries.append(new)
    atomic(config, json.dumps(data, indent=2) + "\n")
    print("Installed additive Cursor hooks. Restart conversation to activate sessionStart.")

def parser():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="command", required=True)
    def add(cmd):
        q = subs.add_parser(cmd)
        q.add_argument("--repo", default=".")
        return q
    q = add("init")
    q.add_argument("--plan", required=True)
    q.add_argument("--run")
    for name in ("task", "step", "block", "unblock", "note", "decision", "status", "resume"):
        q = add(name)
        q.add_argument("--run")
        if name in ("task", "step", "block"):
            q.add_argument("--task", required=True)
        if name in ("task", "step"):
            q.add_argument("--status", required=True, choices=("pending", "in_progress", "complete", "blocked") if name == "task" else ("pending", "in_progress", "complete"))
        if name == "step":
            q.add_argument("--step", required=True)
        if name == "task":
            q.add_argument("--note", default="")
        if name == "block":
            q.add_argument("--message", required=True)
        if name == "unblock":
            q.add_argument("--blocker", required=True)
            q.add_argument("--resolution", required=True)
        if name == "note":
            q.add_argument("--summary", default="")
        if name == "decision":
            q.add_argument("--text", required=True)
            q.add_argument("--reason", required=True)
        if name in ("task", "step", "block", "unblock", "decision"):
            q.add_argument("--evidence", default="")
        if name in ("task", "note"):
            q.add_argument("--next", default="")
    h = add("hook")
    h.add_argument("--event", choices=("sessionStart", "postToolUse"), required=True)
    add("install-cursor-hooks")
    return p

def main():
    a = parser().parse_args()
    try:
        if a.command == "init": init(a)
        elif a.command in ("task", "step", "block", "unblock", "note", "decision"): change(a)
        elif a.command in ("status", "resume"): print(status(a))
        elif a.command == "hook": hook(a)
        elif a.command == "install-cursor-hooks": install(a)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("checkpoint: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
