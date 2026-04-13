from __future__ import annotations

import unittest

from build_a_login_system_with_mvp_app.app import build_app_summary


class BuildAppSummaryTests(unittest.TestCase):
    def test_summary_contains_core_fields(self) -> None:
        summary = build_app_summary()
        self.assertEqual(summary["status"], "scaffolded")
        self.assertEqual(summary["project_name"], 'Build A Login System With MVP')
        self.assertIn("features", summary)
        self.assertGreaterEqual(len(summary["features"]), 3)
        self.assertIn("verification", summary)


if __name__ == "__main__":
    unittest.main()
