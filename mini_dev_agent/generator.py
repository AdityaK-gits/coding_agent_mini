from __future__ import annotations

from typing import Any
from pathlib import Path

from .models import GenerationFile, TaskStep
from .providers import LLMProvider
from .structured_output import load_json_object, to_string_list


class CodeGenerator:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def build_scaffold(self, prompt: str, steps: list[TaskStep], output_dir: Path) -> list[GenerationFile]:
        plan_text = "\n".join(f"- {step.title}" for step in steps)
        raw_blueprint = self.provider.generate(prompt, plan_text)
        blueprint = _parse_blueprint(raw_blueprint, prompt)
        slug = _slugify(str(blueprint["project_name"]))
        package_name = f"{slug}_app"

        files = [
            GenerationFile(
                path=output_dir / "README.md",
                content=_readme_template(prompt, package_name, blueprint),
            ),
            GenerationFile(
                path=output_dir / package_name / "__init__.py",
                content='"""Generated application package."""\n',
            ),
            GenerationFile(
                path=output_dir / package_name / "app.py",
                content=_app_template(prompt, blueprint),
            ),
            GenerationFile(
                path=output_dir / "tests" / "test_app.py",
                content=_test_template(package_name, blueprint),
            ),
        ]
        return files


def _slugify(prompt: str) -> str:
    chars = [ch.lower() if ch.isalnum() else "_" for ch in prompt]
    slug = "".join(chars).strip("_")
    compact = "_".join(part for part in slug.split("_") if part)
    return compact[:40] or "generated"


def _parse_blueprint(raw_blueprint: str, prompt: str) -> dict[str, Any]:
    payload = load_json_object(raw_blueprint)
    return {
        "project_name": str(payload.get("project_name") or prompt),
        "summary": str(
            payload.get("summary")
            or "Generate a compact project scaffold for the requested product idea."
        ),
        "features": to_string_list(
            payload.get("features"),
            [
                "task planning",
                "code generation",
                "execution loop",
                "debug retries",
            ],
        ),
        "components": to_string_list(
            payload.get("components"),
            [
                "application summary module",
                "README with implementation notes",
                "unit test coverage",
            ],
        ),
        "verification": to_string_list(
            payload.get("verification"),
            [
                "run unit tests",
                "check the generated summary",
                "exercise the repair loop",
            ],
        ),
    }


def _readme_template(prompt: str, package_name: str, blueprint: dict[str, Any]) -> str:
    feature_lines = "\n".join(f"- {item}" for item in blueprint["features"])
    component_lines = "\n".join(f"- {item}" for item in blueprint["components"])
    verification_lines = "\n".join(f"- {item}" for item in blueprint["verification"])
    return f"""# Generated Project

Prompt: {prompt}

## Summary

{blueprint["summary"]}

## Planned Features

{feature_lines}

## Components

{component_lines}

## Package

The generated code lives in `{package_name}/app.py`.

## Verification

{verification_lines}

## Run

```bash
python -m unittest discover -s tests -p "test_*.py"
```
"""


def _app_template(prompt: str, blueprint: dict[str, Any]) -> str:
    return f'''from __future__ import annotations


def build_app_summary() -> dict[str, object]:
    """Return a compact summary for the requested project."""
    return {{
        "project_name": {blueprint["project_name"]!r},
        "requested_prompt": {prompt!r},
        "summary": {blueprint["summary"]!r},
        "status": "scaffolded",
        "features": {blueprint["features"]!r},
        "components": {blueprint["components"]!r},
        "verification": {blueprint["verification"]!r},
    }}


def main() -> None:
    summary = build_app_summary()
    print("Generated app summary:")
    for key, value in summary.items():
        print(f"{{key}}: {{value}}")


if __name__ == "__main__":
    main()
'''


def _test_template(package_name: str, blueprint: dict[str, Any]) -> str:
    return f'''from __future__ import annotations

import unittest

from {package_name}.app import build_app_summary


class BuildAppSummaryTests(unittest.TestCase):
    def test_summary_contains_core_fields(self) -> None:
        summary = build_app_summary()
        self.assertEqual(summary["status"], "scaffolded")
        self.assertEqual(summary["project_name"], {blueprint["project_name"]!r})
        self.assertIn("features", summary)
        self.assertGreaterEqual(len(summary["features"]), 3)
        self.assertIn("verification", summary)


if __name__ == "__main__":
    unittest.main()
'''
