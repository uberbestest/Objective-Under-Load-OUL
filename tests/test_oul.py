import unittest
from pathlib import Path

from oul.cli import parse_action_boundary, parse_labeled_text
from oul.core import BLOCK_TYPES, SECTION_ORDER, ActionBoundary, analyze_oul, format_report


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

    def test_thursday_authorized_subset_and_completion_claim(self) -> None:
        result = analyze_oul(objective="Complete the platform integration without overstating execution.", current_plan="Complete local repair and evidence preparation, then perform the platform integration.", pressure_source="Pressure to treat technically understood work as effectively done.", constraints="Require authenticated identity-backed approval for platform integration.", observed_drift_risk="Prepared or awaiting approval may be compressed into completed.", action_boundaries=[ActionBoundary("Local repair", completed=True), ActionBoundary("Evidence preparation", completed=True), ActionBoundary("Authenticated platform integration", identity_established=False, approved=False)])
        self.assertEqual(result.plan_status, "Structurally valid.")
        self.assertEqual(result.execution_authority, "Incomplete; only the authorized subset may execute.")
        self.assertEqual(result.authorized_scope, ["Local repair", "Evidence preparation"])
        self.assertEqual(result.unauthorized_boundary, ["Authenticated platform integration [IDENTITY_BLOCK, APPROVAL_BLOCK]"])
        self.assertIn("Completed: Local repair; Evidence preparation.", result.completion_claim)
        self.assertIn("must not be claimed complete", result.completion_claim)

    def test_each_permission_boundary_classification_is_preserved(self) -> None:
        fields = {"CAPABILITY_BLOCK": "capable", "IDENTITY_BLOCK": "identity_established", "APPROVAL_BLOCK": "approved", "PERMISSION_BLOCK": "permitted", "POLICY_BLOCK": "policy_allows", "PLATFORM_BOUNDARY": "platform_exposes"}
        self.assertEqual(tuple(fields), BLOCK_TYPES)
        for block, field in fields.items():
            result = analyze_oul(objective="Preserve authorized execution.", current_plan="Preserve authorized execution per action.", pressure_source="Execution pressure.", action_boundaries=[ActionBoundary("Boundary action", **{field: False})])
            self.assertEqual(result.unauthorized_boundary, [f"Boundary action [{block}]"])

    def test_action_parser_and_labeled_file_actions(self) -> None:
        parsed = parse_labeled_text("Objective: Preserve authority.\nPlan: Preserve authority per action.\nPressure: Deadline pressure.\nAction: Local repair | completed=yes\nAction: Platform integration | approved=no\n")
        self.assertEqual(parsed["action_boundaries"][0], parse_action_boundary("Local repair | completed=yes"))
        self.assertFalse(parsed["action_boundaries"][1].approved)

    def test_permission_boundary_example_snapshot(self) -> None:
        fields = parse_labeled_text((EXAMPLES_DIR / "oul_permission_boundary_input.txt").read_text(encoding="utf-8"))
        expected = (EXAMPLES_DIR / "oul_permission_boundary_output.txt").read_text(encoding="utf-8").rstrip()
        self.assertEqual(format_report(analyze_oul(**fields)), expected)


if __name__ == "__main__":
    unittest.main()
