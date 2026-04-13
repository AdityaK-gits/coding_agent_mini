from __future__ import annotations

from pathlib import Path

from .debugger import DebuggerAgent
from .executor import ExecutionAgent
from .generator import CodeGenerator
from .models import GenerationFile, RunReport
from .planner import TaskPlanner
from .providers import LLMProvider, build_provider


class MiniDevAgent:
    def __init__(self, provider: LLMProvider | None = None, max_debug_loops: int = 2) -> None:
        self.provider = provider or build_provider(mode="auto")
        self.max_debug_loops = max_debug_loops
        self.planner = TaskPlanner(self.provider)
        self.generator = CodeGenerator(self.provider)
        self.executor = ExecutionAgent()
        self.debugger = DebuggerAgent(self.provider)

    def run(self, prompt: str, workspace: Path) -> RunReport:
        output_dir = workspace / "generated_project"
        output_dir.mkdir(parents=True, exist_ok=True)

        steps = self.planner.create_plan(prompt)
        generated_files = self.generator.build_scaffold(prompt, steps, output_dir)
        self._write_files(generated_files)

        attempts = []
        debug_actions: list[str] = []
        plan_text = "\n".join(step.description for step in steps)

        for _ in range(self.max_debug_loops + 1):
            results = self.executor.run_checks(output_dir)
            attempts.extend(results)
            failed = next((result for result in results if not result.ok), None)
            if failed is None:
                break
            action = self.debugger.analyze(prompt, plan_text, failed, output_dir)
            debug_actions.append(action.summary)
            if not action.files and not action.extra_commands:
                break
            self._write_files(action.files)

        return RunReport(
            provider_name=getattr(self.provider, "name", self.provider.__class__.__name__),
            prompt=prompt,
            steps=steps,
            generated_files=[item.path for item in generated_files],
            attempts=attempts,
            debug_actions=debug_actions,
        )

    @staticmethod
    def _write_files(files: list[GenerationFile]) -> None:
        for file in files:
            file.path.parent.mkdir(parents=True, exist_ok=True)
            file.path.write_text(file.content, encoding="utf-8")
