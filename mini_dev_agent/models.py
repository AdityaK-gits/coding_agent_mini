from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class TaskStep:
    title: str
    description: str


@dataclass(slots=True)
class GenerationFile:
    path: Path
    content: str


@dataclass(slots=True)
class ExecutionResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(slots=True)
class DebugAction:
    summary: str
    files: list[GenerationFile] = field(default_factory=list)
    extra_commands: list[list[str]] = field(default_factory=list)


@dataclass(slots=True)
class RunReport:
    provider_name: str
    prompt: str
    steps: list[TaskStep]
    generated_files: list[Path]
    attempts: list[ExecutionResult]
    debug_actions: list[str]

    @property
    def success(self) -> bool:
        return bool(self.attempts) and self.attempts[-1].ok
