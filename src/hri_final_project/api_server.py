"""Flask API server — runs on the laptop and handles all AI logic.

Pepper calls two endpoints:
  POST /perceive  — send a camera image, get back a CompoundObject
  POST /turn      — send a teacher utterance, get back the robot response text

Usage:
    source .venv/bin/activate
    python -m hri_final_project.api_server --subject test01
"""

import argparse
import base64
import tempfile
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, request

from hri_final_project.compound_object import CompoundObject
from hri_final_project.experiment_runner import ExperimentRunner
from hri_final_project.perception_ClaudeAPI import perceive_compound_object
from hri_final_project.session_manager import SessionManager

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Server state (initialised when the server starts)
# ---------------------------------------------------------------------------
_runner: ExperimentRunner | None = None
_session: SessionManager | None = None
_current_object: CompoundObject | None = None
_last_utterance: str = ""
_last_response: str = ""


def _get_session() -> SessionManager:
    """Return the active session, or raise if not initialised."""
    if _session is None:
        raise RuntimeError("No active session. Start the server with --subject <id>.")
    return _session


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/perceive")
def perceive() -> Response:
    """Receive a base64-encoded image from Pepper and return a CompoundObject.

    Request JSON:
        {"image": "<base64 string>", "extension": "png"}

    Response JSON:
        {"color_top": ..., "shape_top": ..., "size_top": ...,
         "color_bottom": ..., "shape_bottom": ..., "size_bottom": ...}
    """
    global _current_object  # noqa: PLW0603  # pylint: disable=global-statement
    data: dict[str, Any] = request.get_json(force=True)
    image_b64: str = data["image"]
    extension: str = data.get("extension", "png")

    image_bytes = base64.b64decode(image_b64)
    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = Path(tmp.name)

    obj = perceive_compound_object(tmp_path)
    tmp_path.unlink(missing_ok=True)

    _current_object = obj
    print(
        f"\n[Perception]  top: {obj.color_top}, {obj.shape_top}, {obj.size_top}"
        f"  |  bottom: {obj.color_bottom}, {obj.shape_bottom}, {obj.size_bottom}"
    )
    return jsonify(obj.to_dict())


@app.post("/correct")
def correct() -> Response:
    """Override the current perceived object with a manual correction.

    Request JSON:
        {"color_top": "pink", "shape_top": "triangle", "size_top": "large",
         "color_bottom": "green", "shape_bottom": "square", "size_bottom": "large"}
    """
    global _current_object  # noqa: PLW0603  # pylint: disable=global-statement
    data: dict[str, Any] = request.get_json(force=True)
    _current_object = CompoundObject(
        color_top=data["color_top"],
        shape_top=data["shape_top"],
        size_top=data["size_top"],
        color_bottom=data["color_bottom"],
        shape_bottom=data["shape_bottom"],
        size_bottom=data["size_bottom"],
    )
    print(
        f"\n[Correction]  top: {_current_object.color_top},"
        f" {_current_object.shape_top}, {_current_object.size_top}"
        f"  |  bottom: {_current_object.color_bottom},"
        f" {_current_object.shape_bottom}, {_current_object.size_bottom}"
    )
    return jsonify(_current_object.to_dict())


@app.post("/turn")
def turn() -> Response:
    """Process one teaching turn and return the robot response text.

    Request JSON:
        {"utterance": "Pepper, this is a HOUSE"}

    Response JSON:
        {"response": "Understood, thank you!",
         "session_active": true,
         "vs_size": 42}
    """
    global _session, _last_utterance, _last_response  # noqa: PLW0603  # pylint: disable=global-statement
    session = _get_session()

    if _current_object is None:
        return jsonify({"error": "No object perceived yet. Call /perceive first."})

    data: dict[str, Any] = request.get_json(force=True)
    utterance: str = data["utterance"]
    _last_utterance = utterance

    session.process_turn(utterance, _current_object)
    _last_response = session.robot_response
    print(f"\n[Robot] {session.robot_response}")
    print(session.status_line())

    # Advance to next session if current one ended
    if not session.is_active:
        assert _runner is not None
        next_session = _runner.start_next_session()
        if next_session is not None:
            _session = next_session
            print(
                f"\n[Server] Starting next session: "
                f"{next_session._concept_name} [{next_session._mode_name}]"  # pylint: disable=protected-access
            )  # noqa: SLF001
        else:
            print("\n[Server] Experiment complete.")

    return jsonify(
        {
            "response": session.robot_response,
            "session_active": session.is_active,
            "vs_size": session._learner.version_space_size,  # noqa: SLF001  # pylint: disable=protected-access
        }
    )


@app.get("/status")
def status() -> Response:
    """Return current session status for the WoZ panel."""
    # pylint: disable=protected-access
    if _session is None:
        return jsonify({"status": "no session"})
    f1 = _session._learner.current_accuracy  # noqa: SLF001
    return jsonify(
        {
            "concept": _session._concept_name,  # noqa: SLF001
            "mode": _session._mode_name,  # noqa: SLF001
            "vs_size": _session._learner.version_space_size,  # noqa: SLF001
            "examples": _session._learner.labeled_examples_count,  # noqa: SLF001
            "active": _session.is_active,
            "f1": f1,
            "last_utterance": _last_utterance,
            "last_response": _last_response,
        }
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the API server."""
    global _runner, _session  # noqa: PLW0603  # pylint: disable=global-statement

    parser = argparse.ArgumentParser(description="HRI experiment API server")
    parser.add_argument("--subject", required=True, help="Subject ID")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)"
    )
    parser.add_argument("--port", type=int, default=5000, help="Port (default: 5000)")
    args = parser.parse_args()

    _runner = ExperimentRunner(subject_id=args.subject)
    _session = _runner.start_next_session()

    if _session is not None:
        print(f"[Server] Subject: {args.subject}")
        print(
            f"[Server] First session: {_session._concept_name} "  # noqa: SLF001  # pylint: disable=protected-access
            f"[{_session._mode_name}]"
        )  # noqa: SLF001  # pylint: disable=protected-access
        print(f"[Server] Listening on http://{args.host}:{args.port}")

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
