"""Contract tests: python3 -m unittest discover -s skills/execution-checkpoint/tests -v"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "checkpoint.py"
PLAN = """# Plan
### Task 1: Authentication
- [ ] Write failing test
- [ ] Implement auth
### Task 2: Integration
- [ ] Verify workflow
"""

class CheckpointTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        (self.repo / "docs/plans").mkdir(parents=True)
        (self.repo / "docs/plans/test.md").write_text(PLAN, encoding="utf8")

    def command(self, *args, expected=0):
        process = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--repo", str(self.repo)],
            capture_output=True, text=True)
        self.assertEqual(process.returncode, expected, process.stdout + process.stderr)
        return process.stdout if expected == 0 else process.stderr

    def initialize(self):
        self.command("init", "--plan", "docs/plans/test.md", "--run", "feature")

    def state(self):
        return json.loads((self.repo / ".pstack/executions/feature/state.json").read_text())

    def test_initialize_and_refuse_overwrite(self):
        self.initialize()
        self.assertEqual(len(self.state()["tasks"]), 2)
        self.assertEqual(len(self.state()["tasks"][0]["steps"]), 2)
        self.assertTrue((self.repo / ".pstack/executions/feature/summary.md").exists())
        self.command("init", "--plan", "docs/plans/test.md", "--run", "feature", expected=2)

    def test_completion_requires_evidence_and_all_steps(self):
        self.initialize()
        self.command("task", "--run", "feature", "--task", "T1", "--status", "complete",
                     "--evidence", "tests passed", expected=2)
        self.command("step", "--run", "feature", "--task", "T1", "--step", "S1",
                     "--status", "complete", expected=2)
        for step in ("S1", "S2"):
            self.command("step", "--run", "feature", "--task", "T1", "--step", step,
                         "--status", "complete", "--evidence", "test command: PASS")
        self.command("task", "--run", "feature", "--task", "T1", "--status", "complete",
                     "--evidence", "integration test: PASS", "--next", "T2")
        self.assertEqual(self.state()["tasks"][0]["status"], "complete")
        self.assertIn("Next: T2", self.command("resume", "--run", "feature"))

    def test_blocker_and_recovery(self):
        self.initialize()
        self.command("block", "--run", "feature", "--task", "T1", "--message", "runner unavailable")
        self.assertIn("runner unavailable", self.command("resume", "--run", "feature"))
        self.command("decision", "--run", "feature", "--text", "use local tests", "--reason", "CI down")
        self.command("note", "--run", "feature", "--summary", "progress recorded", "--next", "resolve runner")
        self.command("unblock", "--run", "feature", "--blocker", "B1", "--resolution", "runner restored")
        self.assertEqual(self.state()["blockers"][0]["status"], "resolved")
        self.assertEqual(self.state()["tasks"][0]["status"], "in_progress")

    def test_drift_and_ambiguous_selection(self):
        self.initialize()
        self.command("init", "--plan", "docs/plans/test.md", "--run", "other")
        self.command("resume", expected=2)
        self.assertEqual(self.command("hook", "--event", "sessionStart"), "{}\n")
        (self.repo / "docs/plans/test.md").write_text(PLAN + "new scope\n")
        self.assertIn("[DRIFT", self.command("resume", "--run", "feature"))

    def test_hook_install_is_additive_and_idempotent(self):
        self.initialize()
        directory = self.repo / ".cursor"
        directory.mkdir()
        (directory / "hooks.json").write_text(json.dumps(
            {"version": 1, "hooks": {"stop": [{"command": "preserved.sh"}]}}))
        self.command("install-cursor-hooks")
        self.command("install-cursor-hooks")
        data = json.loads((directory / "hooks.json").read_text())
        self.assertEqual(data["hooks"]["stop"][0]["command"], "preserved.sh")
        self.assertEqual(len(data["hooks"]["sessionStart"]), 1)
        self.assertEqual(len(data["hooks"]["postToolUse"]), 1)
        self.assertIn("additional_context", self.command("hook", "--event", "sessionStart"))

    def test_containment(self):
        self.command("init", "--plan", "../outside.md", "--run", "feature", expected=2)
        self.command("init", "--plan", "docs/plans/test.md", "--run", "../escape", expected=2)

if __name__ == "__main__":
    unittest.main()
