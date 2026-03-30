"""Command-line interface for the HRI robot active learning experiment."""

from pathlib import Path

from hri_final_project.compound_object import CompoundObject
from hri_final_project.experiment_runner import ExperimentRunner
from hri_final_project.perception_ClaudeAPI import perceive_compound_object


def _get_current_object() -> CompoundObject:
    """Ask for an image path and perceive the compound object from it."""
    image_path_str = input("\nEnter image path: ").strip()
    image_path = Path(image_path_str)
    print("  Perceiving compound object from image...")
    obj = perceive_compound_object(image_path)
    print(
        f"  Perceived: top={obj.color_top} {obj.size_top} {obj.shape_top}"
        f"  |  bottom={obj.color_bottom} {obj.size_bottom} {obj.shape_bottom}"
    )
    return obj


def main() -> None:
    """Run the full experiment."""
    print("=" * 60)
    print("  HRI Robot Active Learning Experiment")
    print("=" * 60)
    subject_id = input("Enter subject ID: ").strip()
    runner = ExperimentRunner(subject_id)

    session = runner.start_next_session()
    while session is not None:
        print(f"\n{'=' * 60}")
        print(f"  Starting session: {session._concept_name} [{session._mode_name}]")  # noqa: SLF001
        print("  Type teacher utterances. Example:")
        print("    'Pepper, this is a HOUSE'")
        print("    'Pepper, is this a HOUSE?'")
        print("    'Pepper, do you have any questions?'")
        print("    'Pepper, we are done'")
        print("=" * 60)

        while session.is_active:
            print(f"\n{session.status_line()}")
            current_obj = _get_current_object()
            utterance = input("Teacher says: ").strip()
            session.process_turn(utterance, current_obj)
            print(f"\nRobot: {session.robot_response}")

        session = runner.start_next_session()

    runner.print_summary()


if __name__ == "__main__":
    main()
