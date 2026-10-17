"""Exercise release trust checks with real temporary Git checkouts and event fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate-release-source.py"


class ReleaseSourceTests(unittest.TestCase):
    def test_only_current_main_push_or_main_dispatch_can_release(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q", temp], check=True)
            subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com",
                            "commit", "-q", "--allow-empty", "-m", "fixture"], cwd=temp, check=True)
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=temp, text=True).strip()
            good = {"event": "push", "conclusion": "success", "head_branch": "main",
                    "head_repository": {"full_name": "owner/image-use"}, "head_sha": sha}
            cases = [("workflow_run", "refs/heads/main", {}, True),
                     ("workflow_run", "refs/heads/main", {"event": "pull_request"}, False),
                     ("workflow_run", "refs/heads/main", {"conclusion": "failure"}, False),
                     ("workflow_run", "refs/heads/main", {"head_branch": "feature"}, False),
                     ("workflow_run", "refs/heads/main", {"head_repository": {"full_name": "fork/image-use"}}, False),
                     ("workflow_run", "refs/heads/main", {"head_sha": "0" * 40}, False),
                     ("workflow_dispatch", "refs/heads/main", {}, True),
                     ("workflow_dispatch", "refs/heads/feature", {}, False),
                     ("pull_request", "refs/heads/main", {}, False)]
            for event_name, ref, change, allowed in cases:
                with self.subTest(event=event_name, change=change, ref=ref):
                    event = root / "event.json"
                    event.write_text(json.dumps({"workflow_run": dict(good, **change)}))
                    output = root / "output"
                    output.write_text("")
                    env = dict(os.environ, GITHUB_EVENT_NAME=event_name, GITHUB_REF=ref,
                               GITHUB_REPOSITORY="owner/image-use", GITHUB_EVENT_PATH=str(event),
                               GITHUB_OUTPUT=str(output))
                    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=temp, env=env,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode == 0, allowed, result.stderr)
                    self.assertEqual(output.read_text(), f"sha={sha}\n" if allowed else "")
