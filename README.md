# OUL - Objective Under Load

OUL is a small local CLI for checking whether an objective remains recoverable
when a plan, output, or workflow is exposed to optimization pressure.

It is built as a practical companion to Cass-V, REA, and RPU style review work:
identify the objective, name the load condition, catch proxy substitution, and
recommend the smallest repair. It also evaluates execution authority at each action boundary so a valid plan can proceed through its authorized subset without laundering prepared or blocked work into a completion claim.

No API key, model call, backend, telemetry, or build step is required.


## Version

Current repository version: **0.3.0** (2026-07-18).

The package version in `pyproject.toml` is the source of truth. This history names
user-visible changes so readers do not have to infer versions by comparing commits.

- **0.3.0** — Changed omitted authority fields from permissive `yes` defaults to
  explicit `unknown`, added the `authority=established` shorthand, preserved the
  supplied drift risk in reports, distinguished unverified from evidence-referenced
  completion declarations, surfaced unauthorized completion without erasing it,
  and removed completion language from authority status.
- **0.2.0** — Added per-action Permission Boundary evaluation, authorized-subset
  execution reporting, explicit completion claims, and distinct capability,
  identity, approval, permission, policy, and platform stop classifications.
- **0.1.0** — Initial deterministic OUL CLI for objective-preservation,
  proxy-drift, failure-surface, and bounded-repair analysis.

## Install

Use directly from the repo:

```powershell
python -m oul.cli --file examples\oul_proxy_substitution_input.txt
```

Or install the local console command:

```powershell
python -m pip install -e .
oul --file examples\oul_proxy_substitution_input.txt
```

## Input

The CLI accepts flags:

```powershell
python -m oul.cli `
  --objective "Improve claim review accuracy." `
  --current-plan "Rank reviewers by throughput score and completion volume." `
  --pressure-source "Management wants higher dashboard scores." `
  --constraints "Preserve evidence verification." `
  --observed-drift-risk "The workflow is only optimizing score and volume."
```

It also accepts a labeled text file:

```text
Objective: Improve claim review accuracy.
Current Plan: Rank reviewers by throughput score and completion volume.
Pressure Source: Management wants higher dashboard scores.
Constraints: Preserve evidence verification.
Observed Drift Risk: The workflow is only optimizing score and volume.
Action: Local repair | authority=established | completed=yes | evidence=local-repair.patch
Action: Platform integration | capable=yes | identity=no | approved=no | permitted=unknown | policy=yes | platform=yes
```

Each `Action` is evaluated independently. Authority fields are `capable`,
`identity`, `approved`, `permitted`, `policy`, and `platform`; they accept `yes`,
`no`, or `unknown`. Omitted authority fields remain `unknown` and stop the action
from entering authorized scope. Use
`authority=established` to explicitly set all six authority fields to `yes`, then
override any field that differs. `completed` accepts `yes` or `no` and defaults
to `no`. An optional `evidence=reference` may accompany `completed=yes`; OUL
reports a completion without evidence as an unverified declaration. An evidence
reference is preserved but not independently validated. A blocked action is never included in the authorized scope,
even when the rest of the plan remains valid.

If a blocked action is supplied with `completed=yes`, OUL preserves that report
as an unauthorized completion declaration. It does not erase possible execution,
and it does not convert the execution into authorized completion.

## Output

OUL returns deterministic labeled sections:

1. Objective
2. Load / Pressure
3. Observed Drift Risk
4. Preservation Check
5. Proxy Drift Risks
6. Failure Surfaces
7. Classification
8. Objective Status
9. Plan Status
10. Capability Status
11. Execution Authority
12. Authorized Scope
13. Unauthorized Boundary
14. Stop Condition
15. Completion Claim
16. Repair Recommendation
17. Commit Summary

Classification options:

- `PRESERVED`
- `STRESSED`
- `DRIFTING`
- `PROXY_SUBSTITUTED`
- `COLLAPSED`
- `INSUFFICIENT_CONTEXT`

Permission-boundary stops remain separate from constraints and objective preservation: `CAPABILITY_BLOCK`, `IDENTITY_BLOCK`, `APPROVAL_BLOCK`, `PERMISSION_BLOCK`, `POLICY_BLOCK`, and `PLATFORM_BOUNDARY` respectively identify inability, unknown identity, missing approval, missing rights, prohibiting rules, and an unavailable platform mechanism.

`AUTHORITY_UNKNOWN(...)` is an evidence state rather than a seventh denial
classification. It records which authority fields were not established and
keeps the action outside authorized scope without pretending that authority was
explicitly denied.

## Motivating Forensic Case

Thursday's stopped platform integration is recorded in `examples/oul_permission_boundary_input.txt`. The plan remained valid. Local repair and evidence preparation were authorized and declared complete, but only local repair carries a completion-evidence reference in the example. Authenticated platform integration lacked identity-backed approval, had unknown permission state, and stopped at that boundary. It must not be claimed complete. The example preserves the difference between technically understood, prepared, awaiting approval, declared complete, and evidence-referenced completion.

## Examples

Example inputs and outputs live in `examples/`:

- `examples/oul_preserved_input.txt`
- `examples/oul_preserved_output.txt`
- `examples/oul_proxy_substitution_input.txt`
- `examples/oul_proxy_substitution_output.txt`
- `examples/oul_constraint_drift_input.txt`
- `examples/oul_constraint_drift_output.txt`
- `examples/oul_permission_boundary_input.txt`
- `examples/oul_permission_boundary_output.txt`

## Tests

```powershell
python -m unittest tests.test_oul
```

To check OUL and the older Cass-V Lite tests together:

```powershell
python -m unittest discover
```

## Scope

This is an MVP, not a philosophy package. It uses deterministic keyword cues and
plain text output so the result can be inspected, copied into a commit note, or
used as a weekend-ready local audit artifact.

Keep the tool small: add examples and tests before adding architecture.

## What OUL Does Not Do

OUL does not decide whether an objective is morally correct, politically valid,
or institutionally acceptable.

OUL does not score models, rank systems, or replace evaluation benchmarks.

OUL does not prove alignment. It checks whether the stated objective remains
recoverable under load.

OUL does not replace Cass-V, REA, or RPU. It sits beside them as a focused check
for objective drift under pressure.

OUL does not redesign the system by default. The preferred output is the smallest
repair that restores the original objective and its constraints.

OUL does not turn proxy signals into enemies. Speed, score, confidence,
throughput, and satisfaction can be useful signals. They become failures when
they replace the task.
