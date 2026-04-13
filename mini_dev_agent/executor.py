from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .models import ExecutionResult


class ExecutionAgent:
    def run_checks(self, project_dir: Path) -> list[ExecutionResult]:
        commands = [
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
            [sys.executable, "-m", "generated_project_runner"],
        ]
        results: list[ExecutionResult] = []
        for command in commands:
            completed = subprocess.run(
                command,
                cwd=project_dir,
                text=True,
                capture_output=True,
                check=False,
            )
            results.append(
                ExecutionResult(
                    command=command,
                    returncode=completed.returncode,
                    stdout=completed.stdout,
                    stderr=completed.stderr,
                )
            )
            if completed.returncode != 0:
                break
        return results
