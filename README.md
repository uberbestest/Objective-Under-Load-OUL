# OUL - Objective Under Load

OUL is a small local CLI for checking whether an objective remains recoverable
when a plan, output, or workflow is exposed to optimization pressure.

It is built as a practical companion to Cass-V, REA, and RPU style review work:
identify the objective, name the load condition, catch proxy substitution, and
recommend the smallest repair.

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
```

## Output

OUL returns deterministic labeled sections:

1. Objective
2. Load / Pressure
3. Preservation Check
4. Proxy Drift Risks
5. Failure Surfaces
6. Classification
7. Repair Recommendation
8. Commit Summary

Classification options:

- `PRESERVED`
- `STRESSED`
- `DRIFTING`
- `PROXY_SUBSTITUTED`
- `COLLAPSED`
- `INSUFFICIENT_CONTEXT`

## Examples

Example inputs and outputs live in `examples/`:

- `examples/oul_preserved_input.txt`
- `examples/oul_preserved_output.txt`
- `examples/oul_proxy_substitution_input.txt`
- `examples/oul_proxy_substitution_output.txt`
- `examples/oul_constraint_drift_input.txt`
- `examples/oul_constraint_drift_output.txt`

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
