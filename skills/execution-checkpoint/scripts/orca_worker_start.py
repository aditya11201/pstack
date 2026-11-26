#!/usr/bin/env python3
"""Start an Orca worker on a required model and prove Orca launched it on that model.

    orca_worker_start.py [--model <provider/id>] -- <orca orchestration worker-start args>

The model is --model when the user or spec named one, else the first available
entry of the `orca workers:` line in ~/.agents/pstack-models.md
(PSTACK_MODELS_FILE overrides the path). Exit codes: 0 started and verified,
1 worker-start failed (not retried), 2 usage, 3 no requested model available,
4 Orca launched another model or none, so the worker was stopped.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def fail(code, message):
    print(f"orca_worker_start: {message}", file=sys.stderr)
    sys.exit(code)


def mapped_models(path):
    if not path.exists():
        return []
    for line in path.read_text(encoding="utf8").splitlines():
        role, sep, value = line.partition(":")
        if sep and role.strip() == "orca workers":
            # Orca cannot pass an OpenCode variant, so `#high` style suffixes are dropped.
            return [entry.strip().split("#")[0] for entry in value.split(",") if entry.strip()]
    return []


def option(args, name):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else None


def find_dispatch_id(node):
    if isinstance(node, dict):
        for key in ("dispatchId", "dispatch_id"):
            if isinstance(node.get(key), str):
                return node[key]
        dispatch = node.get("dispatch")
        if isinstance(dispatch, dict) and isinstance(dispatch.get("id"), str):
            return dispatch["id"]
        children = node.values()
    elif isinstance(node, list):
        children = node
    else:
        return node if isinstance(node, str) and re.fullmatch(r"ctx_[0-9a-f]+", node) else None
    for child in children:
        found = find_dispatch_id(child)
        if found:
            return found
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", help="model the user or spec named; overrides the mapping")
    parser.add_argument("start_args", nargs=argparse.REMAINDER)
    ns = parser.parse_args()
    start_args = ns.start_args[1:] if ns.start_args[:1] == ["--"] else ns.start_args
    if not start_args:
        fail(2, "pass the worker-start arguments after --")
    if "--model" in start_args or "--terminal" in start_args:
        fail(2, "do not pass --model or --terminal to worker-start; this script sets the model")

    models_file = Path(os.environ.get("PSTACK_MODELS_FILE", Path.home() / ".agents/pstack-models.md"))
    candidates = [ns.model] if ns.model else mapped_models(models_file)
    if not candidates:
        fail(2, f"no worker model: pass --model or add an `orca workers:` line to {models_file}")

    agent = option(start_args, "--agent")
    if agent in ("opencode", "opencode2"):
        listed = subprocess.run(["opencode", "models"], capture_output=True, text=True)
        available = set(listed.stdout.split())
        missing = [model for model in candidates if model not in available]
        candidates = [model for model in candidates if model in available]
        if not candidates:
            fail(3, f"STOP and ask the user: none of {missing} is in `opencode models`")
    model = candidates[0]

    orca = os.environ.get("ORCA_CLI_COMMAND", "orca")
    env_args = ["--environment", option(start_args, "--environment")] if "--environment" in start_args else []
    json_flag = [] if "--json" in start_args else ["--json"]
    start = subprocess.run([orca, "orchestration", "worker-start", *start_args, "--model", model, *json_flag],
                           capture_output=True, text=True)
    sys.stdout.write(start.stdout)
    sys.stderr.write(start.stderr)
    if start.returncode != 0:
        fail(1, "worker-start failed; follow Orca's recovery guide, do not rerun this blindly")

    try:
        dispatch = find_dispatch_id(json.loads(start.stdout))
    except json.JSONDecodeError:
        dispatch = None
    if not dispatch:
        fail(4, "worker-start returned no dispatch id; check `orca orchestration worker-list` and stop the worker by hand")

    show = subprocess.run([orca, "orchestration", "worker-show", "--dispatch", dispatch, *env_args, "--json", "--full"],
                          capture_output=True, text=True)
    try:
        launch = json.loads(show.stdout)["result"]["worker"]["startOptions"]["launch"]
        effective = (launch.get("effective") or {}).get("model")
    except (json.JSONDecodeError, KeyError, TypeError):
        effective = None
    if effective != model:
        subprocess.run([orca, "orchestration", "worker-stop", "--dispatch", dispatch, *env_args, "--json"],
                       capture_output=True, text=True)
        fail(4, f"requested {model} but Orca launched {effective or 'no explicit model'}; "
                f"stopped dispatch {dispatch}. Record a blocker; do not accept this worker.")
    print(f"model verified: {model} (dispatch {dispatch})")


if __name__ == "__main__":
    main()
