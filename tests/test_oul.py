import unittest
from pathlib import Path

from oul.cli import parse_labeled_text
from oul.core import SECTION_ORDER, analyze_oul, format_report


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


class OULTests(unittest.TestCase):
    def test_preserved_output_contract(self) -> None:
        result = analyze_oul(
            objective="Keep support answers source-grounded.",
            current_plan="Keep support answers source-grounded while preserving citations.",
            pressure_source="Normal iteration pressure.",
            constraints="Preserve citations.",
            observed_drift_risk="No observed drift.",
        )
        output = format_report(result)

        self.assertIn("Classification:\nPRESERVED", output)
        positions = [output.index(section) for section in SECTION_ORDER]
        self.assertEqual(positions, sorted(positions))

    def test_proxy_substitution_when_objective_disappears(self) -> None:
        result = analyze_oul(
            objective="Improve claim review accuracy.",
            current_plan="Rank reviewers by throughput score and completion volume.",
            pressure_source="Management wants higher dashboard scores.",
            constraints="Preserve evidence verification.",
            observed_drift_risk="The workflow is only optimizing score and volume.",
        )

        self.assertEqual(result.classification, "PROXY_SUBSTITUTED")
        self.assertIn("Score", result.proxy_drift_risks)
        self.assertIn("Metric Capture", result.failure_surfaces)
        self.assertIn("monitoring evidence only", result.repair_recommendation)

    def test_drifting_when_constraints_are_eroded(self) -> None:
        result = analyze_oul(
            objective="Keep assistant answers source-grounded.",
            current_plan="Keep assistant answers source-grounded and reduce handling time by skipping verification.",
            pressure_source="Optimize for speed.",
            constraints="Verify cited sources before final answer.",
            observed_drift_risk="Verification may be bypassed to improve speed.",
        )

        self.assertEqual(result.classification, "DRIFTING")
        self.assertIn("Constraint Erosion", result.failure_surfaces)

    def test_insufficient_context(self) -> None:
        result = analyze_oul(objective="Preserve task intent.")

        self.assertEqual(result.classification, "INSUFFICIENT_CONTEXT")
        self.assertIn("context insufficient", result.commit_summary)

    def test_parse_labeled_example_file(self) -> None:
        fields = parse_labeled_text((EXAMPLES_DIR / "oul_proxy_substitution_input.txt").read_text(encoding="utf-8"))

        result = analyze_oul(**fields)

        self.assertEqual(result.classification, "PROXY_SUBSTITUTED")

    def test_example_snapshot(self) -> None:
        fields = parse_labeled_text((EXAMPLES_DIR / "oul_proxy_substitution_input.txt").read_text(encoding="utf-8"))
        expected = (EXAMPLES_DIR / "oul_proxy_substitution_output.txt").read_text(encoding="utf-8").rstrip()

        self.assertEqual(format_report(analyze_oul(**fields)), expected)


if __name__ == "__main__":
    unittest.main()
