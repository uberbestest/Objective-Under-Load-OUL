import unittest

from oul.handoff import HandoffBoundary, evaluate_handoff, format_handoff_report


class HandoffProjectionTests(unittest.TestCase):
    def test_clean_clear_does_not_require_recursive_evidence_check(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Alder",
            provisional_route="CLEAR",
            investigation_decision="NOT_REQUIRED",
            final_route="CLEAR",
            next_action="NONE",
            next_action_timing="POST_EXECUTION",
        ))
        self.assertEqual(result.status, "RESOLVED")
        self.assertNotIn("SELECTIVE_OVERCHECK", result.issues)

    def test_soft_hold_can_reconcile_to_clear_with_receipt(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Mica",
            provisional_route="HOLD",
            investigation_decision="REQUIRED",
            evidence_available=True,
            evidence_authorized=True,
            evidence_accessed=True,
            evidence_receipt="mica-reconciliation.txt",
            final_route="CLEAR",
            next_action="NONE",
            next_action_timing="POST_EXECUTION",
        ))
        self.assertEqual(result.status, "RESOLVED")
        self.assertEqual(result.final_route, "CLEAR")
        self.assertIn("receipt: mica-reconciliation.txt", result.evidence_access_state)

    def test_hard_mismatch_can_remain_safe_hold_after_evidence(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Granite",
            provisional_route="HOLD",
            investigation_decision="OPTIONAL",
            evidence_available=True,
            evidence_authorized=True,
            evidence_accessed=True,
            evidence_receipt="granite-reconciliation.txt",
            final_route="HOLD",
            next_action="Stop release",
            next_action_timing="POST_EXECUTION",
        ))
        self.assertEqual(result.status, "RESOLVED")
        self.assertEqual(result.final_route, "HOLD")

    def test_required_investigation_can_stop_safely_without_false_clear(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Mica",
            provisional_route="HOLD",
            investigation_decision="REQUIRED",
            evidence_available=True,
            evidence_authorized=True,
            evidence_accessed=False,
            final_route="HOLD",
            next_action="Read reconciliation record",
            next_action_timing="PRE_EXECUTION",
        ))
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertIn("INCOMPLETE_HANDOFF", result.issues)
        self.assertIn("Safe HOLD preserved", result.completion_claim)

    def test_unauthorized_evidence_access_is_preserved_as_authority_failure(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Mica",
            provisional_route="HOLD",
            investigation_decision="OPTIONAL",
            evidence_available=True,
            evidence_authorized=False,
            evidence_accessed=True,
            evidence_receipt="receipt.txt",
            final_route="HOLD",
        ))
        self.assertEqual(result.status, "AUTHORITY_FAILURE")
        self.assertIn("UNAUTHORIZED_EVIDENCE_ACCESS", result.issues)
        self.assertIn("must not be represented as authority-valid", result.completion_claim)

    def test_route_change_without_evidence_is_not_laundered(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Mica",
            provisional_route="HOLD",
            investigation_decision="OPTIONAL",
            evidence_available=True,
            evidence_authorized=True,
            evidence_accessed=False,
            final_route="CLEAR",
        ))
        self.assertEqual(result.status, "INVALID_TRANSITION")
        self.assertIn("UNSUPPORTED_ROUTE_TRANSITION", result.issues)

    def test_next_action_requires_temporal_anchor_to_avoid_run005_ambiguity(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Mica",
            provisional_route="HOLD",
            investigation_decision="REQUIRED",
            evidence_available=True,
            evidence_authorized=True,
            evidence_accessed=True,
            evidence_receipt="receipt.txt",
            final_route="CLEAR",
            next_action="NONE",
        ))
        self.assertEqual(result.status, "RESOLVED_WITH_WARNING")
        self.assertIn("NEXT_ACTION_TEMPORAL_ANCHOR_MISSING", result.issues)
        self.assertIn("Temporal anchor unknown", result.next_action_state)

    def test_receipt_without_access_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires evidence_accessed=yes"):
            HandoffBoundary(
                item="Mica",
                provisional_route="HOLD",
                investigation_decision="REQUIRED",
                evidence_available=True,
                evidence_authorized=True,
                evidence_accessed=False,
                evidence_receipt="receipt.txt",
                final_route="HOLD",
            )

    def test_report_keeps_decision_access_and_terminal_state_separate(self) -> None:
        result = evaluate_handoff(HandoffBoundary(
            item="Mica",
            provisional_route="HOLD",
            investigation_decision="REQUIRED",
            evidence_available=True,
            evidence_authorized=True,
            evidence_accessed=True,
            evidence_receipt="receipt.txt",
            final_route="CLEAR",
            next_action="NONE",
            next_action_timing="POST_EXECUTION",
        ))
        report = format_handoff_report(result)
        positions = [
            report.index("Provisional Route:"),
            report.index("Investigation State:"),
            report.index("Evidence Access State:"),
            report.index("Final Route:"),
            report.index("Next Action State:"),
        ]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
