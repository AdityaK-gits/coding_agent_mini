from __future__ import annotations

import importlib.util
import json
import os
from abc import ABC, abstractmethod
from typing import Any


DEFAULT_OPENAI_MODEL = "gpt-5"


class ProviderConfigurationError(RuntimeError):
    """Raised when a provider cannot be configured safely."""


class LLMProvider(ABC):
    name = "base"

    @abstractmethod
    def plan(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate(self, prompt: str, plan: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def debug(self, prompt: str, plan: str, error_output: str) -> str:
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Deterministic fallback provider so the MVP runs without API keys."""

    name = "mock"

    def plan(self, prompt: str) -> str:
        return "\n".join(
            [
                "1. Analyze the requested product scope.",
                "2. Scaffold a small Python project for the feature.",
                "3. Add basic tests or smoke checks.",
                "4. Run the project and capture failures.",
                "5. Apply focused fixes until the checks pass.",
            ]
        )

    def generate(self, prompt: str, plan: str) -> str:
        project_name = _prompt_to_project_name(prompt)
        payload = {
            "project_name": project_name,
            "summary": f"Generate a backend-oriented starter project for: {prompt}.",
            "features": [
                f"requirements plan for {prompt.lower()}",
                "modular Python scaffold",
                "closed-loop execution",
                "automatic repair hooks",
            ],
            "components": [
                "application summary module",
                "README with implementation notes",
                "unit test coverage",
                "debug repair entrypoint",
            ],
            "verification": [
                "run unit tests",
                "verify generated summary keys",
                "exercise the debug loop",
            ],
        }
        return json.dumps(payload)

    def debug(self, prompt: str, plan: str, error_output: str) -> str:
        lowered = error_output.lower()
        if "no module named pytest" in lowered:
            return '{"summary": "Pytest is unavailable. Switch to unittest-based verification.", "files": []}'
        if "syntaxerror" in lowered:
            return '{"summary": "Inspect the generated Python file and repair the syntax issue.", "files": []}'
        return '{"summary": "Review the failing command output and apply the smallest safe fix.", "files": []}'


class OpenAIProvider(LLMProvider):
    """LLM provider backed by the OpenAI Responses API."""

    name = "openai"

    def __init__(
        self,
        model: str | None = None,
        reasoning_effort: str | None = None,
        api_key_env: str = "OPENAI_API_KEY",
        client: Any | None = None,
    ) -> None:
        self.model = model or os.getenv("MINI_DEV_AGENT_OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self.reasoning_effort = reasoning_effort or os.getenv("MINI_DEV_AGENT_REASONING_EFFORT")
        self.api_key_env = api_key_env
        self.client = client or self._build_client()

    def plan(self, prompt: str) -> str:
        return self._complete(
            instructions=(
                "You are the task planner for an autonomous coding assistant. "
                "Return 4 to 7 numbered steps, one per line, each beginning with '<number>. '. "
                "Focus on implementation, execution, debugging, and verification for the user's request. "
                "Do not use markdown headings or commentary."
            ),
            prompt=f"User request:\n{prompt}",
        )

    def generate(self, prompt: str, plan: str) -> str:
        return self._complete(
            instructions=(
                "You are the code generation planner for an autonomous coding assistant. "
                "Return strict JSON with keys project_name, summary, features, components, and verification. "
                "features, components, and verification must be arrays of 3 to 6 short strings. "
                "Keep the project tailored to the user request. Do not wrap the JSON in markdown."
            ),
            prompt=f"User request:\n{prompt}\n\nExecution plan:\n{plan}",
        )

    def debug(self, prompt: str, plan: str, error_output: str) -> str:
        return self._complete(
            instructions=(
                "You are the debugger for an autonomous coding assistant. "
                "Return strict JSON with keys summary and files. "
                "summary must be a single short sentence. "
                "files must be an array of objects with keys path and content. "
                "Only include files when you are confident that replacing or adding a whole file is the safest repair. "
                "All paths must be relative to the project root. Do not use markdown."
            ),
            prompt=(
                f"User request:\n{prompt}\n\n"
                f"Execution plan:\n{plan}\n\n"
                f"Failure context:\n{error_output}"
            ),
        )

    def _build_client(self) -> Any:
        if not os.getenv(self.api_key_env):
            raise ProviderConfigurationError(
                f"Set {self.api_key_env} to use the OpenAI provider, or run with --provider mock."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderConfigurationError(
                "Install the `openai` package to use the OpenAI provider."
            ) from exc
        return OpenAI()

    def _complete(self, instructions: str, prompt: str) -> str:
        request: dict[str, Any] = {
            "model": self.model,
            "instructions": instructions,
            "input": prompt,
        }
        if self.reasoning_effort and self.reasoning_effort.lower() != "none":
            request["reasoning"] = {"effort": self.reasoning_effort}

        response = self.client.responses.create(**request)
        output_text = getattr(response, "output_text", "")
        if output_text:
            return output_text.strip()
        return str(response).strip()


def build_provider(
    mode: str = "auto",
    model: str | None = None,
    reasoning_effort: str | None = None,
    api_key_env: str = "OPENAI_API_KEY",
) -> LLMProvider:
    normalized_mode = mode.strip().lower()
    if normalized_mode == "mock":
        return MockProvider()
    if normalized_mode == "openai":
        return OpenAIProvider(model=model, reasoning_effort=reasoning_effort, api_key_env=api_key_env)
    if normalized_mode == "auto":
        if _has_openai_sdk() and os.getenv(api_key_env):
            return OpenAIProvider(model=model, reasoning_effort=reasoning_effort, api_key_env=api_key_env)
        return MockProvider()
    raise ProviderConfigurationError(f"Unsupported provider mode: {mode}")


def _has_openai_sdk() -> bool:
    return importlib.util.find_spec("openai") is not None


def _prompt_to_project_name(prompt: str) -> str:
    parts = [word.strip(".,:;!?-_") for word in prompt.split()]
    cleaned = [part for part in parts if part]
    if not cleaned:
        return "Generated Project MVP"
    title = " ".join(word.capitalize() for word in cleaned[:5])
    return f"{title} MVP"
