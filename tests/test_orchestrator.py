from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mini_dev_agent import MiniDevAgent


class MiniDevAgentTests(unittest.TestCase):
    def test_run_builds_project_and_repairs_missing_runner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            report = MiniDevAgent(max_debug_loops=2).run(
                prompt="Build a login system with JWT auth",
                workspace=workspace,
            )

            self.assertTrue(report.success)
            self.assertTrue((workspace / "generated_project" / "generated_project_runner.py").exists())
            self.assertGreaterEqual(len(report.steps), 3)
            self.assertGreaterEqual(len(report.attempts), 2)


if __name__ == "__main__":
    unittest.main()
