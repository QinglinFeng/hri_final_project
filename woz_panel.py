#!/usr/bin/env python3
"""Wizard-of-Oz control panel.

Run this in a second terminal to monitor the experiment state in real time.
It polls the API server's /status endpoint and displays a live dashboard.

Usage:
    source .venv/bin/activate
    python woz_panel.py --server http://localhost:5000
"""

import argparse
import os
import time

import requests


def _clear() -> None:
    os.system("clear")


def _fetch_status(server_url: str) -> dict[str, object] | None:
    try:
        resp = requests.get(server_url + "/status", timeout=3)
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]
    except requests.RequestException:
        return None


def _bar(value: float, width: int = 20) -> str:
    """Render a simple ASCII progress bar for a 0–1 value."""
    filled = int(round(value * width))
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def run(server_url: str, refresh_seconds: float) -> None:
    """Poll the API server and render the dashboard."""
    print(f"Connecting to {server_url} ...")

    while True:
        status = _fetch_status(server_url)
        _clear()

        print("╔══════════════════════════════════════════════════╗")
        print("║         WoZ Control Panel — HRI Experiment       ║")
        print("╚══════════════════════════════════════════════════╝")

        if status is None:
            print("\n  ⚠  Cannot reach API server at", server_url)
            print("     Make sure api_server.py is running.\n")
        else:
            concept = status.get("concept", "—")
            mode = status.get("mode", "—")
            vs_size = int(status.get("vs_size", 0))
            examples = int(status.get("examples", 0))
            active = bool(status.get("active", False))
            f1 = status.get("f1")
            last_response = status.get("last_response", "—")
            last_utterance = status.get("last_utterance", "—")

            # VS convergence: 3600 is max, 1 is converged
            max_vs = 3600
            convergence = 1.0 - (vs_size - 1) / max(max_vs - 1, 1)

            print(f"\n  Concept : {concept}")
            print(f"  Mode    : {mode}")
            print(f"  Active  : {'Yes' if active else 'Session ended'}")
            print()
            print(f"  Examples labeled : {examples}")
            print(f"  Version space    : {vs_size} / {max_vs}")
            print(f"  Convergence      : {_bar(convergence)} {convergence:.0%}")
            if f1 is not None:
                print(f"  F1 score         : {_bar(float(f1))} {float(f1):.3f}")
            print()
            print(f"  Last utterance : {last_utterance}")
            print(f"  Last response  : {last_response}")

        print(f"\n  Refreshing every {refresh_seconds}s — Ctrl+C to quit")
        time.sleep(refresh_seconds)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="WoZ control panel")
    parser.add_argument(
        "--server",
        default="http://localhost:5000",
        help="API server URL (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--refresh",
        type=float,
        default=2.0,
        help="Refresh interval in seconds (default: 2)",
    )
    args = parser.parse_args()
    try:
        run(args.server, args.refresh)
    except KeyboardInterrupt:
        print("\nPanel closed.")


if __name__ == "__main__":
    main()
