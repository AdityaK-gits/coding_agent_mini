# Mini Dev Agent

`mini-dev-agent` is a Python MVP for the autonomous coding assistant you described: planner, generator, execution loop, debugger, and a runnable CLI.

## What It Does

- Accepts a natural-language project request such as `Build a login system with JWT auth`
- Produces a structured task plan
- Generates a task-specific project scaffold in `generated_project/`
- Runs verification commands automatically
- Detects a known failure and repairs it in a debug loop
- Can use the OpenAI Responses API for planning, blueprint generation, and safe file-level repair suggestions

## Why This MVP Is Useful

It gives you a real closed-loop skeleton you can extend with:

- OpenAI or Claude-backed planning/generation
- Richer code patching
- Dependency installation
- Docker sandboxing
- GitHub automation

## Quick Start

```bash
python -m pip install -e .
mini-dev-agent "Build a login system with JWT auth"
```

Or run directly:

```bash
python -m mini_dev_agent.cli "Build a login system with JWT auth"
```

## OpenAI Provider

The CLI now supports three provider modes:

- `auto`: use OpenAI when `OPENAI_API_KEY` is set, otherwise fall back to the deterministic mock provider
- `mock`: always use the local deterministic provider
- `openai`: require a valid OpenAI API key and use the Responses API

Example:

```bash
$env:OPENAI_API_KEY="your_api_key_here"
python -m mini_dev_agent.cli "Build a login system with JWT auth" --provider openai --model gpt-5
```

Optional environment variables:

- `OPENAI_API_KEY`: API key used by the OpenAI SDK
- `MINI_DEV_AGENT_OPENAI_MODEL`: default model override for `auto` or `openai`
- `MINI_DEV_AGENT_REASONING_EFFORT`: optional Responses API reasoning effort

## Project Layout

- `mini_dev_agent/planner.py`: prompt to task steps
- `mini_dev_agent/generator.py`: writes the initial scaffold
- `mini_dev_agent/executor.py`: runs checks
- `mini_dev_agent/debugger.py`: inspects failures and applies repairs
- `mini_dev_agent/providers.py`: mock and OpenAI-backed provider implementations
- `mini_dev_agent/orchestrator.py`: drives the closed loop
- `mini_dev_agent/web.py`: simple FastAPI web UI for the agent
- `tests/test_orchestrator.py`: end-to-end MVP test

## Web UI

A lightweight FastAPI web front end is now available alongside the CLI.

Run it with:

```powershell
& ".\.venv\Scripts\python.exe" -m mini_dev_agent.web
```

Then open:

```text
http://127.0.0.1:8000
```

The web UI lets you enter a prompt, choose provider settings, and view the generated plan and output files.

## Next Extensions

1. Upgrade the debugger from whole-file patches to diff-based patch generation.
2. Run generated projects inside Docker.
3. Add dependency installation and richer execution logs.
4. Add Git and GitHub publishing steps.
