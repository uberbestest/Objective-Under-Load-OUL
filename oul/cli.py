from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import analyze_oul, format_report


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
    args = parser.parse_args(argv)

    fields = {
        "objective": args.objective,
        "current_plan": args.current_plan,
        "pressure_source": args.pressure_source,
        "constraints": args.constraints,
        "observed_drift_risk": args.observed_drift_risk,
    }

    if args.file:
        fields.update({key: value for key, value in parse_labeled_text(args.file.read_text(encoding="utf-8")).items() if value})
    elif not any(fields.values()) and not sys.stdin.isatty():
        fields.update({key: value for key, value in parse_labeled_text(sys.stdin.read()).items() if value})

    result = analyze_oul(**fields)
    print(format_report(result))
    return 0


def parse_labeled_text(text: str) -> dict[str, str]:
    fields = {
        "objective": "",
        "current_plan": "",
        "pressure_source": "",
        "constraints": "",
        "observed_drift_risk": "",
    }
    active_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        label, sep, value = line.partition(":")
        key = FIELD_ALIASES.get(label.strip().lower()) if sep else None
        if key:
            active_key = key
            fields[key] = _append(fields[key], value.strip())
        elif active_key:
            fields[active_key] = _append(fields[active_key], line)

    return fields


def _append(existing: str, value: str) -> str:
    if not value:
        return existing
    if not existing:
        return value
    return f"{existing} {value}"


if __name__ == "__main__":
    raise SystemExit(main())
