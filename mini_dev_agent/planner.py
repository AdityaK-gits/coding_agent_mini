from __future__ import annotations

from .models import TaskStep
from .providers import LLMProvider


class TaskPlanner:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def create_plan(self, prompt: str) -> list[TaskStep]:
        raw_plan = self.provider.plan(prompt)
        steps: list[TaskStep] = []
        for line in raw_plan.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            title = cleaned.split(".", 1)[-1].strip()
            steps.append(TaskStep(title=title, description=cleaned))
        return steps
