# OUL Goblin Lab Projection — GPT-5.6 Sol

**Projection ID:** `OUL-GOBLIN-PROJECTION-GPT56-2026-09-03`  
**Baseline:** `69bac44392047cf9b84d02a0e861775bffa829f6` (`OUL 0.4.0`)  
**Status:** experimental projection; do not merge into `main` before cross-substrate comparison  
**Purpose:** record what GPT-5.6 Sol projects from the completed Goblin Lab handoff/reconciliation experiments when starting from the exact OUL 0.4.0 baseline.

## Source findings compiled

From run 004, compile only the reproducible measurement/handoff pieces: prospective state, explicit next action, separation of routing/investigation/execution, receipt-bearing read-only reconciliation, and fail-closed handling. Do not compile named-goblin orchestration, Bramble-specific trust claims, or a claimed independent juncture-rule benefit.

From run 005, compile the negative lesson that removing the direct reconciliation command did not create investigation-threshold sensitivity. Evidence availability and schema affordances can themselves pressure the workflow. `NEXT ACTION` also requires a temporal anchor because the run produced both pre-execution selected-action and post-execution remaining-action interpretations.

## Projected OUL change

Add a deterministic handoff-transition sidecar that keeps these relations separate:

1. provisional route (`CLEAR`, `HOLD`, `UNKNOWN`);
2. investigation decision (`REQUIRED`, `OPTIONAL`, `NOT_REQUIRED`, `UNKNOWN`);
3. evidence availability;
4. evidence-access authority;
5. evidence access and receipt;
6. final route;
7. next action with explicit `PRE_EXECUTION` or `POST_EXECUTION` timing.

The sidecar does **not** infer that available evidence must be opened. It can preserve a safe unresolved `HOLD` as incomplete without converting it into an incorrect release. Unauthorized evidence access is preserved as an observed event but cannot become authority-valid. A route change without recorded evidence is rejected as an unsupported transition.

## Why a sidecar instead of immediate core rewrite

The comparison target is substrate projection, not version churn. The 0.4.0 core remains unchanged so a later Astra-Rin projection can start from the same commit and the same Goblin Lab evidence without seeing this implementation. Only after comparing the two independent projections should any common mechanism be considered for OUL main.

## Non-claims

This projection does not establish:

- that prior QA confidence changes investigation thresholds;
- that the juncture rule has an independent benefit;
- that named goblin roles generalize;
- that reconciliation should always occur;
- that receipt text independently proves operating-system access;
- that this sidecar is OUL 0.5.0 or ready for promotion.

## Comparison instruction for Astra-Rin

Start from `69bac44392047cf9b84d02a0e861775bffa829f6`, not this branch. Supply the same run-004 and run-005 result artifacts. Ask for the smallest OUL update justified by those experiments. Freeze Astra's design and tests before revealing this branch. Then compare:

- relation types introduced;
- state vocabulary;
- authority semantics;
- treatment of optional evidence;
- treatment of incomplete `HOLD`;
- temporal handling of next action;
- compatibility cost with OUL 0.4.0;
- tests each projection considered load-bearing.
