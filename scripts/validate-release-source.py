#!/usr/bin/env python3
"""Release only a successful main push from this repository at the checked-out main commit."""
import json
import os
from pathlib import Path
import subprocess


def main():
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    event_name = os.environ["GITHUB_EVENT_NAME"]
    if event_name == "workflow_run":
        run = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())["workflow_run"]
        if not (run.get("event") == "push" and run.get("conclusion") == "success"
                and run.get("head_branch") == "main"
                and run.get("head_repository", {}).get("full_name") == os.environ["GITHUB_REPOSITORY"]
                and run.get("head_sha") == sha):
            raise SystemExit("release source is not the successful current main push from this repository")
    elif event_name == "workflow_dispatch":
        if os.environ.get("GITHUB_REF") != "refs/heads/main":
            raise SystemExit("manual release must be dispatched from main")
    else:
        raise SystemExit("unsupported release trigger")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        print(f"sha={sha}", file=output)


if __name__ == "__main__":
    main()
