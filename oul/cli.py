from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import ActionBoundary, analyze_oul, format_report


FIELD_ALIASES = {
    "objective": "objective",
    "current plan": "current_plan",
    "current output": "current_plan",
    "plan": "current_plan",
    "output": "current_plan",
    "pressure": "pressure_source",
    "pressure source": "pressure_source",
    "load": "pressure_source",
    "constraints": "constraints",
    "constraint": "constraints",
    "observed drift risk": "observed_drift_risk",
    "drift risk": "observed_drift_risk",
    "drift": "observed_drift_risk",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a deterministic Objective Under Load audit.")
    parser.add_argument("--objective", default="", help="Stated objective.")
    parser.add_argument("--current-plan", default="", help="Current plan or output under review.")
    parser.add_argument("--pressure-source", default="", help="Optimization pressure or load condition.")
    parser.add_argument("--constraints", default="", help="Constraints that must remain intact.")
    parser.add_argument("--observed-drift-risk", default="", help="Observed risk or suspected drift.")
    parser.add_argument("--file", type=Path, help="Optional labeled text input file.")
    parser.add_argument("--action", action="append", default=[], help="Action boundary: name | authority=established | completed=no | evidence=reference")
    args = parser.parse_args(argv)

    fields = {
        "objective": args.objective,
        "current_plan": args.current_plan,
        "pressure_source": args.pressure_source,
        "constraints": args.constraints,
        "observed_drift_risk": args.observed_drift_risk,
        "action_boundaries": [parse_action_boundary(value) for value in args.action],
    }

    if args.file:
        fields.update({key: value for key, value in parse_labeled_text(args.file.read_text(encoding="utf-8")).items() if value})
    elif not any(fields.values()) and not sys.stdin.isatty():
        fields.update({key: value for key, value in parse_labeled_text(sys.stdin.read()).items() if value})

    result = analyze_oul(**fields)
    print(format_report(result))
    return 0


def parse_labeled_text(text: str) -> dict[str, object]:
    fields = {
        "objective": "",
        "current_plan": "",
        "pressure_source": "",
        "constraints": "",
        "observed_drift_risk": "",
        "action_boundaries": [],
    }
    active_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        label, sep, value = line.partition(":")
        key = FIELD_ALIASES.get(label.strip().lower()) if sep else None
        if sep and label.strip().lower() == "action":
            active_key = None
            fields["action_boundaries"].append(parse_action_boundary(value.strip()))
            continue
        if key:
            active_key = key
            fields[key] = _append(fields[key], value.strip())
        elif active_key:
            fields[active_key] = _append(fields[active_key], line)

    return fields


def parse_action_boundary(text: str) -> ActionBoundary:
    parts = [part.strip() for part in text.split("|") if part.strip()]
    if not parts: raise ValueError("Action boundary requires an action name.")
    authority_fields = ("capable", "identity_established", "approved", "permitted", "policy_allows", "platform_exposes")
    values: dict[str, object] = {field: None for field in authority_fields}
    values.update({"completed": False, "completion_evidence": ""})
    aliases = {
        "identity": "identity_established",
        "policy": "policy_allows",
        "platform": "platform_exposes",
        "evidence": "completion_evidence",
    }
    for part in parts[1:]:
        key, sep, raw = part.partition("=")
        key = aliases.get(key.strip().lower(), key.strip().lower())
        raw = raw.strip()
        normalized = raw.lower()
        if not sep:
            raise ValueError(f"Invalid action boundary field: {part}")
        if key == "authority":
            if normalized not in {"established", "unknown"}:
                raise ValueError(f"Invalid action boundary field: {part}")
            state = True if normalized == "established" else None
            values.update({field: state for field in authority_fields})
        elif key == "completion_evidence":
            if not raw:
                raise ValueError("Completion evidence requires a non-empty reference.")
            values[key] = raw
        elif key == "completed":
            if normalized not in {"yes", "no"}:
                raise ValueError(f"Invalid action boundary field: {part}")
            values[key] = normalized == "yes"
        elif key in authority_fields:
            if normalized not in {"yes", "no", "unknown"}:
                raise ValueError(f"Invalid action boundary field: {part}")
            values[key] = None if normalized == "unknown" else normalized == "yes"
        else:
            raise ValueError(f"Invalid action boundary field: {part}")
    return ActionBoundary(action=parts[0], **values)


def _append(existing: str, value: str) -> str:
    if not value:
        return existing
    if not existing:
        return value
    return f"{existing} {value}"


if __name__ == "__main__":
    raise SystemExit(main())
