from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mini_dev_agent.debugger import DebuggerAgent
from mini_dev_agent.models import ExecutionResult
from mini_dev_agent.providers import MockProvider, OpenAIProvider, build_provider


class _FakeResponsesAPI:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class _FakeOpenAIClient:
    def __init__(self, output_text: str) -> None:
        self.responses = _FakeResponsesAPI(output_text)


class _DebugPatchProvider(MockProvider):
    def debug(self, prompt: str, plan: str, error_output: str) -> str:
        return (
            '{"summary": "Patch the failing file.", '
            '"files": [{"path": "repairs/fix.py", "content": "print(\\"patched\\")\\n"}]}'
        )


class ProviderTests(unittest.TestCase):
    def test_build_provider_auto_falls_back_to_mock_without_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            provider = build_provider(mode="auto")
        self.assertIsInstance(provider, MockProvider)

    def test_openai_provider_uses_responses_api_shape(self) -> None:
        fake_client = _FakeOpenAIClient("1. Inspect\n2. Build\n3. Test")
        provider = OpenAIProvider(
            client=fake_client,
            model="gpt-5",
            reasoning_effort="low",
        )

        plan = provider.plan("Build a login system with JWT auth")

        self.assertEqual(plan, "1. Inspect\n2. Build\n3. Test")
        self.assertEqual(len(fake_client.responses.calls), 1)
        request = fake_client.responses.calls[0]
        self.assertEqual(request["model"], "gpt-5")
        self.assertEqual(request["reasoning"], {"effort": "low"})
        self.assertIn("task planner", str(request["instructions"]).lower())

    def test_debugger_accepts_safe_llm_file_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            result = ExecutionResult(
                command=["python", "-m", "unittest"],
                returncode=1,
                stdout="",
                stderr="Traceback: simulated failure",
            )

            action = DebuggerAgent(_DebugPatchProvider()).analyze(
                prompt="Build a login system with JWT auth",
                plan_text="1. Plan\n2. Build\n3. Test",
                failed_result=result,
                project_dir=project_dir,
            )

            self.assertEqual(action.summary, "Patch the failing file.")
            self.assertEqual(len(action.files), 1)
            self.assertTrue(action.files[0].path.is_relative_to(project_dir.resolve()))


if __name__ == "__main__":
    unittest.main()
