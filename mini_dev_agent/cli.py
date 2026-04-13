from __future__ import annotations

import argparse
from pathlib import Path

from .orchestrator import MiniDevAgent
from .providers import ProviderConfigurationError, build_provider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Mini Dev Agent MVP.")
    parser.add_argument("prompt", help="The project request for the agent.")
    parser.add_argument(
        "--provider",
        choices=["auto", "mock", "openai"],
        default="auto",
        help="Provider backend to use. 'auto' uses OpenAI when OPENAI_API_KEY is set, otherwise MockProvider.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI model name to use when the OpenAI provider is active.",
    )
    parser.add_argument(
        "--reasoning-effort",
        default=None,
        help="Optional OpenAI reasoning effort, such as minimal, low, medium, or high.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace where the generated project should be written.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        provider = build_provider(
            mode=args.provider,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
        )
    except ProviderConfigurationError as exc:
        raise SystemExit(str(exc)) from exc

    agent = MiniDevAgent(provider=provider)
    report = agent.run(prompt=args.prompt, workspace=args.workspace)

    print(f"Prompt: {report.prompt}")
    print(f"Provider: {report.provider_name}")
    print(f"Success: {report.success}")
    print("Planned steps:")
    for step in report.steps:
        print(f"- {step.title}")
    print("Generated files:")
    for path in report.generated_files:
        print(f"- {path}")
    if report.debug_actions:
        print("Debug actions:")
        for action in report.debug_actions:
            print(f"- {action}")
