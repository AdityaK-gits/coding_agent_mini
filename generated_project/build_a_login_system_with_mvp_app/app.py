from __future__ import annotations


def build_app_summary() -> dict[str, object]:
    """Return a compact summary for the requested project."""
    return {
        "project_name": 'Build A Login System With MVP',
        "requested_prompt": 'Build a login system with JWT auth',
        "summary": 'Generate a backend-oriented starter project for: Build a login system with JWT auth.',
        "status": "scaffolded",
        "features": ['requirements plan for build a login system with jwt auth', 'modular Python scaffold', 'closed-loop execution', 'automatic repair hooks'],
        "components": ['application summary module', 'README with implementation notes', 'unit test coverage', 'debug repair entrypoint'],
        "verification": ['run unit tests', 'verify generated summary keys', 'exercise the debug loop'],
    }


def main() -> None:
    summary = build_app_summary()
    print("Generated app summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
