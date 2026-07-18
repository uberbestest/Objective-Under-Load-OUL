# OUL - Objective Under Load

OUL is a small local CLI for checking whether an objective remains recoverable
when a plan, output, or workflow is exposed to optimization pressure.

It is built as a practical companion to Cass-V, REA, and RPU style review work:
identify the objective, name the load condition, catch proxy substitution, and
recommend the smallest repair. It also evaluates execution authority at each action boundary so a valid plan can proceed through its authorized subset without laundering prepared or blocked work into a completion claim.

No API key, model call, backend, telemetry, or build step is required.

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
Action: Local repair | completed=yes
Action: Platform integration | identity=no | approved=no
```

Each `Action` is evaluated independently. Supported boundary fields are `capable`, `identity`, `approved`, `permitted`, `policy`, `platform`, and `completed`, each set to `yes` or `no`. Omitted authority fields default to `yes`; `completed` defaults to `no`. A blocked action is never included in the authorized scope, even when the rest of the plan remains valid.

## Output

OUL returns deterministic labeled sections:

1. Objective
2. Load / Pressure
3. Preservation Check
4. Proxy Drift Risks
5. Failure Surfaces
6. Classification
7. Objective Status
8. Plan Status
9. Capability Status
10. Execution Authority
11. Authorized Scope
12. Unauthorized Boundary
13. Stop Condition
14. Completion Claim
15. Repair Recommendation
16. Commit Summary

Classification options:

- `PRESERVED`
- `STRESSED`
- `DRIFTING`
- `PROXY_SUBSTITUTED`
- `COLLAPSED`
- `INSUFFICIENT_CONTEXT`

Permission-boundary stops remain separate from constraints and objective preservation: `CAPABILITY_BLOCK`, `IDENTITY_BLOCK`, `APPROVAL_BLOCK`, `PERMISSION_BLOCK`, `POLICY_BLOCK`, and `PLATFORM_BOUNDARY` respectively identify inability, unknown identity, missing approval, missing rights, prohibiting rules, and an unavailable platform mechanism.

## Motivating Forensic Case

Thursday's stopped platform integration is recorded in `examples/oul_permission_boundary_input.txt`. The plan remained valid. Local repair and evidence preparation were authorized and completed. Authenticated platform integration lacked identity-backed approval and execution authority, so it stopped at that boundary and must not be claimed complete. The example preserves the difference between technically understood, prepared, awaiting approval, and completed.

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
