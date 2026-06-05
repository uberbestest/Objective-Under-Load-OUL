from __future__ import annotations

import re
from dataclasses import dataclass


CLASSIFICATIONS = (
    "PRESERVED",
    "STRESSED",
    "DRIFTING",
    "PROXY_SUBSTITUTED",
    "COLLAPSED",
    "INSUFFICIENT_CONTEXT",
)

SECTION_ORDER = (
    "Objective:",
    "Load / Pressure:",
    "Preservation Check:",
    "Proxy Drift Risks:",
    "Failure Surfaces:",
    "Classification:",
    "Repair Recommendation:",
    "Commit Summary:",
)

PROXY_TERMS = (
    "accuracy metric",
    "automation level",
    "completion rate",
    "confidence",
    "convenience",
    "engagement",
    "handling time",
    "latency",
    "ranking",
    "satisfaction",
    "score",
    "speed",
    "throughput",
    "volume",
)

PRESSURE_TERMS = (
    "automate",
    "automation",
    "bonus",
    "deadline",
    "delegate",
    "handoff",
    "increase",
    "iterate",
    "maximize",
    "metric",
    "minimize",
    "optimize",
    "pressure",
    "rank",
    "reduce",
    "scale",
    "score",
    "speed",
)

FAILURE_SURFACE_CUES = (
    ("Goodharting", ("goodhart", "metric", "kpi", "score", "ranking")),
    ("Reward Hacking", ("reward", "bonus", "incentive", "game")),
    ("Scope Expansion", ("expand", "broaden", "additional scope", "scope creep")),
    ("Constraint Erosion", ("drop", "remove", "ignore", "bypass", "without review", "skip verification")),
    ("Semantic Flattening", ("flatten", "generic", "rename", "simplify the meaning")),
    ("Automation Drift", ("automate", "automation", "autonomous")),
    ("Delegation Drift", ("delegate", "handoff", "handover")),
    ("Specification Gaming", ("spec gaming", "loophole", "checklist", "pass the test")),
    ("Narrative Replacement", ("story", "narrative", "positioning", "spin")),
    ("Metric Capture", ("metric", "dashboard", "score", "kpi")),
)


@dataclass(frozen=True)
class OULResult:
    objective: str
    load_condition: str
    preservation_check: str
    proxy_drift_risks: list[str]
    failure_surfaces: list[str]
    classification: str
    repair_recommendation: str
    commit_summary: str


def analyze_oul(
    objective: str = "",
    current_plan: str = "",
    pressure_source: str = "",
    constraints: str = "",
    observed_drift_risk: str = "",
) -> OULResult:
    objective = _clean(objective)
    current_plan = _clean(current_plan)
    pressure_source = _clean(pressure_source)
    constraints = _clean(constraints)
    observed_drift_risk = _clean(observed_drift_risk)

    combined = " ".join(
        part for part in (current_plan, pressure_source, constraints, observed_drift_risk) if part
    )
    lower_combined = combined.lower()

    if not objective or not combined:
        return OULResult(
            objective=objective or "Objective not stated.",
            load_condition=pressure_source or "Load condition not stated.",
            preservation_check="Cannot determine whether the objective survives because required context is missing.",
            proxy_drift_risks=["Insufficient context to identify proxy drift risks."],
            failure_surfaces=["Insufficient context"],
            classification="INSUFFICIENT_CONTEXT",
            repair_recommendation="State the objective, current plan or output, pressure source, constraints, and observed drift risk.",
            commit_summary="OUL: context insufficient for objective-under-load classification.",
        )

    proxies = _detect_proxy_risks(combined)
    failures = _detect_failure_surfaces(lower_combined, proxies, constraints)
    objective_visible = _objective_visible(objective, current_plan)
    constraint_visible = _constraint_visible(constraints, current_plan)
    pressure_present = _contains_any(lower_combined, PRESSURE_TERMS)
    constraint_eroded = "Constraint Erosion" in failures

    classification = _classify(
        objective_visible=objective_visible,
        constraint_visible=constraint_visible,
        pressure_present=pressure_present,
        proxies=proxies,
        failures=failures,
        observed_drift_risk=observed_drift_risk,
        constraint_eroded=constraint_eroded,
    )
    preservation_check = _preservation_check(
        objective_visible=objective_visible,
        constraint_visible=constraint_visible,
        proxies=proxies,
        classification=classification,
    )
    repair = _repair_recommendation(classification, objective, constraints, proxies, failures)
    summary = _commit_summary(classification, objective, proxies, failures)

    return OULResult(
        objective=objective,
        load_condition=pressure_source or "No explicit pressure source stated.",
        preservation_check=preservation_check,
        proxy_drift_risks=proxies or ["No likely proxy substitution detected."],
        failure_surfaces=failures or ["No explicit failure surface detected."],
        classification=classification,
        repair_recommendation=repair,
        commit_summary=summary,
    )


def format_report(result: OULResult) -> str:
    return "\n\n".join(
        (
            f"Objective:\n{result.objective}",
            f"Load / Pressure:\n{result.load_condition}",
            f"Preservation Check:\n{result.preservation_check}",
            "Proxy Drift Risks:\n" + _format_list(result.proxy_drift_risks),
            "Failure Surfaces:\n" + _format_list(result.failure_surfaces),
            f"Classification:\n{result.classification}",
            f"Repair Recommendation:\n{result.repair_recommendation}",
            f"Commit Summary:\n{result.commit_summary}",
        )
    )


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _contains_any(text: str, cues: tuple[str, ...]) -> bool:
    return any(cue in text for cue in cues)


def _detect_proxy_risks(text: str) -> list[str]:
    lower = text.lower()
    risks = []
    for term in PROXY_TERMS:
        if term in lower:
            risks.append(term)
    if not risks and _contains_any(lower, ("metric", "kpi", "dashboard")):
        risks.append("metric target")
    return [risk.title() for risk in risks[:5]]


def _detect_failure_surfaces(lower_text: str, proxies: list[str], constraints: str) -> list[str]:
    surfaces = []
    for label, cues in FAILURE_SURFACE_CUES:
        if any(cue in lower_text for cue in cues):
            surfaces.append(label)

    if proxies and "Metric Capture" not in surfaces:
        surfaces.append("Metric Capture")
    if constraints and any(cue in lower_text for cue in ("drop", "remove", "ignore", "bypass", "skip")):
        if "Constraint Erosion" not in surfaces:
            surfaces.append("Constraint Erosion")

    return surfaces[:5]


def _objective_visible(objective: str, current_plan: str) -> bool:
    if not current_plan:
        return False
    objective_terms = _meaningful_terms(objective)
    plan_terms = set(_meaningful_terms(current_plan))
    return bool(objective_terms) and any(term in plan_terms for term in objective_terms)


def _constraint_visible(constraints: str, current_plan: str) -> bool:
    if not constraints:
        return True
    constraint_terms = _meaningful_terms(constraints)
    plan_terms = set(_meaningful_terms(current_plan))
    return bool(constraint_terms) and any(term in plan_terms for term in constraint_terms)


def _meaningful_terms(text: str) -> list[str]:
    stop = {
        "and",
        "for",
        "from",
        "keep",
        "must",
        "not",
        "the",
        "this",
        "that",
        "with",
    }
    words = re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", text.lower())
    return [word for word in words if word not in stop][:8]


def _classify(
    *,
    objective_visible: bool,
    constraint_visible: bool,
    pressure_present: bool,
    proxies: list[str],
    failures: list[str],
    observed_drift_risk: str,
    constraint_eroded: bool,
) -> str:
    drift_lower = observed_drift_risk.lower()
    severe_drift = _contains_any(
        drift_lower,
        ("cannot recover", "lost", "collapsed", "objective absent"),
    )

    if severe_drift and not objective_visible:
        return "COLLAPSED"
    if proxies and not objective_visible:
        return "PROXY_SUBSTITUTED"
    if proxies and (constraint_eroded or not constraint_visible):
        return "DRIFTING"
    if proxies or failures:
        return "STRESSED"
    return "PRESERVED"


def _preservation_check(
    *,
    objective_visible: bool,
    constraint_visible: bool,
    proxies: list[str],
    classification: str,
) -> str:
    if classification == "PRESERVED":
        return "The objective remains visible and no proxy substitution is apparent."
    if classification == "STRESSED":
        return "The objective remains recoverable, but load is introducing proxy pressure."
    if classification == "DRIFTING":
        return "The objective is still recoverable, but constraints or attention are shifting toward proxy targets."
    if classification == "PROXY_SUBSTITUTED":
        return "The current plan appears to target a proxy more clearly than the stated objective."
    if classification == "COLLAPSED":
        return "The original objective is not recoverable from the current plan or drift signal."
    if not objective_visible or not constraint_visible or proxies:
        return "The objective cannot be classified confidently from the supplied context."
    return "The preservation state is unclear."


def _repair_recommendation(
    classification: str,
    objective: str,
    constraints: str,
    proxies: list[str],
    failures: list[str],
) -> str:
    if classification == "PRESERVED":
        return "No repair required. Keep monitoring proxies as signals, not targets."
    if classification == "INSUFFICIENT_CONTEXT":
        return "Add the missing objective-under-load fields before making a repair call."

    proxy_text = ", ".join(proxies) if proxies else "the proxy target"
    constraint_text = f" Preserve constraints: {constraints}" if constraints else ""

    if classification == "COLLAPSED":
        return f"Stop optimization work and restate the original objective before proceeding: {objective.rstrip('.')}.{constraint_text}"
    if classification == "PROXY_SUBSTITUTED":
        return f"Bind the plan back to the original objective and demote {proxy_text} to monitoring evidence only.{constraint_text}"
    if classification == "DRIFTING":
        return f"Add an explicit check that {proxy_text} cannot pass unless it also preserves the objective.{constraint_text}"
    return f"Keep the plan, but add a guardrail that treats {proxy_text} as a signal rather than the task."


def _commit_summary(
    classification: str,
    objective: str,
    proxies: list[str],
    failures: list[str],
) -> str:
    objective_fragment = objective[:72].rstrip(".")
    if classification == "PRESERVED":
        return f"OUL: objective preserved for '{objective_fragment}'."
    if classification == "INSUFFICIENT_CONTEXT":
        return "OUL: insufficient context for objective preservation check."

    proxy_fragment = ", ".join(proxies[:2]) if proxies else "proxy pressure"
    failure_fragment = ", ".join(failures[:2]) if failures else "load pressure"
    return f"OUL: {classification.lower()} risk on '{objective_fragment}' via {proxy_fragment}; surfaces: {failure_fragment}."


def _format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
