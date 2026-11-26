"""Contract tests: python3 -m unittest discover -s skills/execution-checkpoint/tests -v"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "orca_worker_start.py"

FAKE_ORCA = r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(json.dumps(args) + "\n")
verb = args[1]
if verb == "worker-start":
    if os.environ.get("FAKE_START_FAIL"):
        print('{"ok": false, "failedStage": "agent_readiness"}')
        sys.exit(1)
    model = args[args.index("--model") + 1] if "--model" in args else None
    with open(os.environ["FAKE_STATE"], "w") as state:
        state.write(json.dumps(model))
    print(json.dumps({"result": {"dispatch": {"id": "ctx_abc123"}}}))
elif verb == "worker-show":
    requested = json.load(open(os.environ["FAKE_STATE"]))
    effective = os.environ.get("FAKE_EFFECTIVE", requested)
    launch = {"requested": {"agent": "opencode", "model": requested},
              "effective": {"agent": "opencode", "model": effective}}
    print(json.dumps({"result": {"worker": {"startOptions": {"launch": launch}}}}))
elif verb == "worker-stop":
    print('{"ok": true}')
'''

FAKE_OPENCODE = r'''#!/usr/bin/env python3
import os, sys
if sys.argv[1:] == ["models"]:
    print(os.environ.get("FAKE_MODELS", "").replace(",", "\n"))
'''

MODELS_FILE = """# pstack model configuration
swarm workers: alibaba-token-plan/deepseek-v4.1-flash-1017#low
orca workers: openai/gpt-6-luna, alibaba-token-plan/deepseek-v4.1-flash-1017#high
"""

START = ["--", "--environment", "local", "--spec", "audit vm", "--worktree", "current", "--agent", "opencode"]


class OrcaWorkerStartTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        for name, body in (("orca", FAKE_ORCA), ("opencode", FAKE_OPENCODE)):
            path = self.dir / name
            path.write_text(body)
            path.chmod(0o755)
        self.models = self.dir / "pstack-models.md"
        self.models.write_text(MODELS_FILE)
        self.log = self.dir / "orca.log"
        self.env = {
            **os.environ,
            "PATH": f"{self.dir}{os.pathsep}{os.environ['PATH']}",
            "FAKE_LOG": str(self.log),
            "FAKE_STATE": str(self.dir / "state.json"),
            "FAKE_MODELS": "openai/gpt-6-luna,alibaba-token-plan/deepseek-v4.1-flash-1017,openai/gpt-6.1-terra",
            "PSTACK_MODELS_FILE": str(self.models),
        }
        self.env.pop("ORCA_CLI_COMMAND", None)

    def run_script(self, *args, expected=0, **env):
        process = subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
            env={**self.env, **env})
        self.assertEqual(process.returncode, expected, process.stdout + process.stderr)
        return process

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def verbs(self):
        return [call[1] for call in self.calls()]

    def test_starts_with_first_orca_workers_model_and_verifies_it(self):
        process = self.run_script(*START)
        start = self.calls()[0]
        self.assertEqual(start[start.index("--model") + 1], "openai/gpt-6-luna")
        self.assertIn("--json", start)
        self.assertEqual(self.verbs(), ["worker-start", "worker-show"])
        show = self.calls()[1]
        self.assertEqual(show[show.index("--environment") + 1], "local")
        self.assertIn("model verified: openai/gpt-6-luna (dispatch ctx_abc123)", process.stdout)

    def test_falls_back_to_next_available_model_without_variant(self):
        self.run_script(*START, FAKE_MODELS="alibaba-token-plan/deepseek-v4.1-flash-1017")
        start = self.calls()[0]
        self.assertEqual(start[start.index("--model") + 1], "alibaba-token-plan/deepseek-v4.1-flash-1017")

    def test_explicit_model_overrides_mapping(self):
        self.run_script("--model", "openai/gpt-6.1-terra", *START)
        start = self.calls()[0]
        self.assertEqual(start[start.index("--model") + 1], "openai/gpt-6.1-terra")

    def test_refuses_to_start_when_no_requested_model_is_available(self):
        process = self.run_script(*START, expected=3, FAKE_MODELS="openai/gpt-6.1-terra")
        self.assertEqual(self.calls(), [])
        self.assertIn("STOP", process.stderr)

    def test_refuses_without_any_worker_model(self):
        self.models.write_text("swarm workers: openai/gpt-6-luna\n")
        process = self.run_script(*START, expected=2)
        self.assertEqual(self.calls(), [])
        self.assertIn("orca workers", process.stderr)

    def test_refuses_model_inside_worker_start_args(self):
        self.run_script(*START, "--model", "openai/gpt-6.1-terra", expected=2)
        self.assertEqual(self.calls(), [])

    def test_stops_worker_when_effective_model_differs(self):
        process = self.run_script(*START, expected=4, FAKE_EFFECTIVE="openai/gpt-6.1-terra")
        self.assertEqual(self.verbs(), ["worker-start", "worker-show", "worker-stop"])
        stop = self.calls()[2]
        self.assertEqual(stop[stop.index("--dispatch") + 1], "ctx_abc123")
        self.assertIn("openai/gpt-6.1-terra", process.stderr)

    def test_stops_worker_when_effective_model_is_missing(self):
        self.run_script(*START, expected=4, FAKE_EFFECTIVE="")
        self.assertEqual(self.verbs()[-1], "worker-stop")

    def test_passes_through_a_failed_start_without_retrying(self):
        self.run_script(*START, expected=1, FAKE_START_FAIL="1")
        self.assertEqual(self.verbs(), ["worker-start"])


if __name__ == "__main__":
    unittest.main()
