from __future__ import annotations


def build_app_summary() -> dict[str, object]:
    """Return a compact summary for the requested project."""
    return {
        "requested_prompt": 'Build a login system with JWT auth',
        "status": "scaffolded",
        "features": [
            "task planning",
            "code generation",
            "execution loop",
            "debug retries",
        ],
    }


def main() -> None:
    summary = build_app_summary()
    print("Generated app summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
