from __future__ import annotations

import html
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from .cli import build_provider
from .orchestrator import MiniDevAgent

app = FastAPI(title="Mini Dev Agent Web UI")


def _escape(value: Optional[str]) -> str:
    return html.escape(value or "")


def _format_list(items: list[str]) -> str:
    if not items:
        return "<p><em>None</em></p>"
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def _render_form(prompt: str = "", provider: str = "auto", model: str = "", reasoning_effort: str = "", workspace: str = "") -> str:
    return f"""
    <h1>Mini Dev Agent</h1>
    <form method="post" action="/run">
      <label>Prompt:<br>
        <textarea name="prompt" rows="4" cols="70">{_escape(prompt)}</textarea>
      </label>
      <br><br>
      <label>Provider:<br>
        <select name="provider">
          <option value="auto"{' selected' if provider == 'auto' else ''}>auto</option>
          <option value="mock"{' selected' if provider == 'mock' else ''}>mock</option>
          <option value="openai"{' selected' if provider == 'openai' else ''}>openai</option>
        </select>
      </label>
      <br><br>
      <label>Model:<br>
        <input type="text" name="model" value="{_escape(model)}" size="40" />
      </label>
      <br><br>
      <label>Reasoning effort:<br>
        <input type="text" name="reasoning_effort" value="{_escape(reasoning_effort)}" size="40" />
      </label>
      <br><br>
      <label>Workspace (optional):<br>
        <input type="text" name="workspace" value="{_escape(workspace)}" size="60" placeholder="Leave blank to use current directory" />
      </label>
      <br><br>
      <button type="submit">Run Agent</button>
    </form>
    """


def _render_report(report: object, workspace: Path) -> str:
    generated_files_html = _format_list([str(path) for path in report.generated_files])
    steps_html = _format_list([step.title for step in report.steps])
    debug_actions_html = _format_list(report.debug_actions)

    return f"""
    <h2>Run Result</h2>
    <p><strong>Prompt:</strong> {html.escape(report.prompt)}</p>
    <p><strong>Provider:</strong> {html.escape(report.provider_name)}</p>
    <p><strong>Success:</strong> {html.escape(str(report.success))}</p>
    <p><strong>Output workspace:</strong> {html.escape(str(workspace))}</p>
    <h3>Planned Steps</h3>
    {steps_html}
    <h3>Generated Files</h3>
    {generated_files_html}
    <h3>Debug Actions</h3>
    {debug_actions_html}
    """


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    html_content = f"""
    <html>
      <head><title>Mini Dev Agent Web UI</title></head>
      <body>
        {_render_form()}
      </body>
    </html>
    """
    return HTMLResponse(html_content)


@app.post("/run", response_class=HTMLResponse)
def run_prompt(
    prompt: str = Form(...),
    provider: str = Form("auto"),
    model: str = Form(""),
    reasoning_effort: str = Form(""),
    workspace: str = Form(""),
) -> HTMLResponse:
    provider_instance = build_provider(
        mode=provider,
        model=model or None,
        reasoning_effort=reasoning_effort or None,
    )
    output_workspace = Path(workspace) if workspace.strip() else Path.cwd()
    agent = MiniDevAgent(provider=provider_instance)
    report = agent.run(prompt=prompt, workspace=output_workspace)

    html_content = f"""
    <html>
      <head><title>Mini Dev Agent Web UI</title></head>
      <body>
        {_render_form(prompt=prompt, provider=provider, model=model, reasoning_effort=reasoning_effort, workspace=str(output_workspace))}
        {_render_report(report, output_workspace)}
      </body>
    </html>
    """
    return HTMLResponse(html_content)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
