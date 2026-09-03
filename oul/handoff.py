from __future__ import annotations

from dataclasses import dataclass


ROUTES = ("CLEAR", "HOLD", "UNKNOWN")
INVESTIGATION_DECISIONS = ("REQUIRED", "OPTIONAL", "NOT_REQUIRED", "UNKNOWN")
NEXT_ACTION_TIMINGS = ("PRE_EXECUTION", "POST_EXECUTION")


@dataclass(frozen=True)
class HandoffBoundary:
    item: str
    provisional_route: str = "UNKNOWN"
    investigation_decision: str = "UNKNOWN"
    evidence_available: bool = False
    evidence_authorized: bool | None = None
    evidence_accessed: bool = False
    evidence_receipt: str = ""
    final_route: str = "UNKNOWN"
    next_action: str = ""
    next_action_timing: str | None = None

    def __post_init__(self) -> None:
        if not self.item.strip():
            raise ValueError("Handoff boundary requires an item name.")
        if self.provisional_route not in ROUTES:
            raise ValueError(f"Invalid provisional route: {self.provisional_route}")
        if self.final_route not in ROUTES:
            raise ValueError(f"Invalid final route: {self.final_route}")
        if self.investigation_decision not in INVESTIGATION_DECISIONS:
            raise ValueError(f"Invalid investigation decision: {self.investigation_decision}")
        if self.next_action_timing not in (None, *NEXT_ACTION_TIMINGS):
            raise ValueError(f"Invalid next action timing: {self.next_action_timing}")
        if self.evidence_receipt and not self.evidence_accessed:
            raise ValueError("Evidence receipt requires evidence_accessed=yes.")


@dataclass(frozen=True)
class HandoffResult:
    item: str
    provisional_route: str
    investigation_state: str
    evidence_access_state: str
    final_route: str
    next_action_state: str
    issues: list[str]
    status: str
    completion_claim: str


def evaluate_handoff(boundary: HandoffBoundary) -> HandoffResult:
    issues: list[str] = []

    if boundary.evidence_accessed and not boundary.evidence_available:
        issues.append("EVIDENCE_ACCESSED_WITHOUT_DECLARED_AVAILABILITY")

    if boundary.evidence_accessed:
        if boundary.evidence_authorized is False:
            issues.append("UNAUTHORIZED_EVIDENCE_ACCESS")
        elif boundary.evidence_authorized is None:
            issues.append("EVIDENCE_AUTHORITY_UNKNOWN")

    if boundary.evidence_accessed and not boundary.evidence_receipt:
        issues.append("EVIDENCE_ACCESS_WITHOUT_RECEIPT")

    if (
        boundary.provisional_route == "CLEAR"
        and boundary.investigation_decision == "NOT_REQUIRED"
        and boundary.evidence_accessed
    ):
        issues.append("SELECTIVE_OVERCHECK")

    if (
        boundary.provisional_route == "HOLD"
        and boundary.investigation_decision == "REQUIRED"
        and not boundary.evidence_accessed
    ):
        issues.append("INCOMPLETE_HANDOFF")

    if (
        boundary.final_route != boundary.provisional_route
        and not boundary.evidence_accessed
    ):
        issues.append("UNSUPPORTED_ROUTE_TRANSITION")

    if (
        boundary.provisional_route == "HOLD"
        and boundary.final_route == "CLEAR"
        and boundary.investigation_decision == "REQUIRED"
        and not boundary.evidence_accessed
    ):
        issues.append("PREMATURE_CLEAR")

    if boundary.next_action and boundary.next_action_timing is None:
        issues.append("NEXT_ACTION_TEMPORAL_ANCHOR_MISSING")

    investigation_state = _investigation_state(boundary)
    evidence_access_state = _evidence_access_state(boundary)
    next_action_state = _next_action_state(boundary)
    status = _status(boundary, issues)
    completion_claim = _completion_claim(boundary, status, issues)

    return HandoffResult(
        item=boundary.item,
        provisional_route=boundary.provisional_route,
        investigation_state=investigation_state,
        evidence_access_state=evidence_access_state,
        final_route=boundary.final_route,
        next_action_state=next_action_state,
        issues=issues,
        status=status,
        completion_claim=completion_claim,
    )


def format_handoff_report(result: HandoffResult) -> str:
    issue_lines = "\n".join(f"- {issue}" for issue in result.issues) if result.issues else "- None detected."
    return "\n\n".join(
        (
            f"Item:\n{result.item}",
            f"Provisional Route:\n{result.provisional_route}",
            f"Investigation State:\n{result.investigation_state}",
            f"Evidence Access State:\n{result.evidence_access_state}",
            f"Final Route:\n{result.final_route}",
            f"Next Action State:\n{result.next_action_state}",
            f"Issues:\n{issue_lines}",
            f"Handoff Status:\n{result.status}",
            f"Handoff Completion Claim:\n{result.completion_claim}",
        )
    )


def _investigation_state(boundary: HandoffBoundary) -> str:
    if boundary.investigation_decision == "REQUIRED":
        return "Investigation explicitly required by the recorded decision."
    if boundary.investigation_decision == "OPTIONAL":
        return "Investigation permitted as an optional decision; availability does not make it required."
    if boundary.investigation_decision == "NOT_REQUIRED":
        return "Investigation explicitly not required by the recorded decision."
    return "Investigation requirement unresolved; do not infer a requirement from evidence availability."


def _evidence_access_state(boundary: HandoffBoundary) -> str:
    if not boundary.evidence_accessed:
        if boundary.evidence_available:
            authority = _authority_word(boundary.evidence_authorized)
            return f"Evidence available but not accessed; access authority is {authority}."
        return "No evidence access recorded."

    authority = _authority_word(boundary.evidence_authorized)
    receipt = boundary.evidence_receipt or "no receipt"
    return f"Evidence accessed; access authority is {authority}; receipt: {receipt}."


def _authority_word(value: bool | None) -> str:
    if value is True:
        return "established"
    if value is False:
        return "denied"
    return "unknown"


def _next_action_state(boundary: HandoffBoundary) -> str:
    action = boundary.next_action.strip()
    if not action:
        return "No next action supplied."
    if boundary.next_action_timing == "PRE_EXECUTION":
        return f"Selected before execution: {action}"
    if boundary.next_action_timing == "POST_EXECUTION":
        return f"Remaining after execution: {action}"
    return f"Temporal anchor unknown: {action}"


def _status(boundary: HandoffBoundary, issues: list[str]) -> str:
    if any(issue in issues for issue in ("UNAUTHORIZED_EVIDENCE_ACCESS", "EVIDENCE_AUTHORITY_UNKNOWN")):
        return "AUTHORITY_FAILURE"
    if any(issue in issues for issue in ("PREMATURE_CLEAR", "UNSUPPORTED_ROUTE_TRANSITION")):
        return "INVALID_TRANSITION"
    if "INCOMPLETE_HANDOFF" in issues or boundary.final_route == "UNKNOWN":
        return "INCOMPLETE"
    if issues:
        return "RESOLVED_WITH_WARNING"
    return "RESOLVED"


def _completion_claim(boundary: HandoffBoundary, status: str, issues: list[str]) -> str:
    if status == "AUTHORITY_FAILURE":
        return "Observed evidence access is preserved, but the handoff must not be represented as authority-valid."
    if status == "INVALID_TRANSITION":
        return "The terminal route is not justified by the recorded transition evidence."
    if status == "INCOMPLETE":
        if boundary.final_route == "HOLD":
            return "Safe HOLD preserved; investigation or resolution remains incomplete."
        return "Handoff remains incomplete; no resolved terminal claim is justified."
    if status == "RESOLVED_WITH_WARNING":
        return "Terminal route is recorded, but one or more measurement or temporal warnings remain explicit."
    return "Terminal route is resolved under the recorded investigation, evidence-access, and authority state."
