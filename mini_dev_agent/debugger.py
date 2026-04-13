from __future__ import annotations

from pathlib import Path

from .models import DebugAction, ExecutionResult, GenerationFile
from .providers import LLMProvider
from .structured_output import load_json_object


class DebuggerAgent:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def analyze(self, prompt: str, plan_text: str, failed_result: ExecutionResult, project_dir: Path) -> DebugAction:
        guidance = self.provider.debug(
            prompt=prompt,
            plan=plan_text,
            error_output=(
                f"Command: {' '.join(failed_result.command)}\n\n"
                f"Stdout:\n{failed_result.stdout}\n\n"
                f"Stderr:\n{failed_result.stderr}\n\n"
                f"Project snapshot:\n{_project_snapshot(project_dir)}"
            ),
        )
        suggestion = load_json_object(guidance)
        suggestion_summary = str(suggestion.get("summary") or guidance).strip()
        llm_files = _safe_generation_files(project_dir, suggestion.get("files"))
        if llm_files:
            return DebugAction(summary=suggestion_summary, files=llm_files)

        stderr = failed_result.stderr.lower()
        stdout = failed_result.stdout.lower()

        if "no module named generated_project_runner" in stderr:
            runner_path = project_dir / "generated_project_runner.py"
            return DebugAction(
                summary=f"{suggestion_summary} Added missing runner entrypoint.",
                files=[
                    GenerationFile(
                        path=runner_path,
                        content=_runner_template(project_dir),
                    )
                ],
            )

        if "no module named pytest" in stderr:
            return DebugAction(summary=f"{suggestion_summary} No file change needed because unittest is already in use.")

        if "traceback" in stdout or "traceback" in stderr:
            return DebugAction(summary=f"{suggestion_summary} Automatic repair was not implemented for this failure yet.")

        return DebugAction(summary=f"{suggestion_summary} No deterministic repair matched the failure.")


def _runner_template(project_dir: Path) -> str:
    package_dirs = [entry.name for entry in project_dir.iterdir() if entry.is_dir() and (entry / "app.py").exists()]
    package_name = package_dirs[0] if package_dirs else "generated_app"
    return f"""from {package_name}.app import main


if __name__ == "__main__":
    main()
"""


def _project_snapshot(project_dir: Path, max_chars: int = 6000) -> str:
    sections: list[str] = []
    total = 0
    for path in sorted(project_dir.rglob("*")):
        if "__pycache__" in path.parts or not path.is_file() or path.suffix not in {".py", ".md", ".txt"}:
            continue
        relative_path = path.relative_to(project_dir)
        content = path.read_text(encoding="utf-8")
        section = f"## {relative_path}\n{content}\n"
        if total + len(section) > max_chars:
            remaining = max_chars - total
            if remaining > 0:
                sections.append(section[:remaining])
            break
        sections.append(section)
        total += len(section)
    return "\n".join(sections)


def _safe_generation_files(project_dir: Path, raw_files: object) -> list[GenerationFile]:
    if not isinstance(raw_files, list):
        return []

    resolved_project_dir = project_dir.resolve()
    safe_files: list[GenerationFile] = []
    for item in raw_files:
        if not isinstance(item, dict):
            continue
        relative_path = str(item.get("path", "")).strip()
        content = item.get("content")
        if not relative_path or not isinstance(content, str):
            continue
        target_path = (project_dir / relative_path).resolve()
        try:
            target_path.relative_to(resolved_project_dir)
        except ValueError:
            continue
        safe_files.append(GenerationFile(path=target_path, content=content))
    return safe_files
