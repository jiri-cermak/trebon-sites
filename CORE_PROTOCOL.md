# Tiered Relay Architecture v6 — Core Protocol

This document is the project-agnostic orchestration core. It defines the Architect → Subagent → Verify loop, not this project's stack, domain, tools, or deployment environment.

## Roles

- **Architect:** plans, writes relay context, delegates, independently verifies, records learnings, and controls retries. Does not write feature code.
- **Subagent:** executes only the assigned relay context, changes only named target files, runs declared tests, commits the result, and writes the handover.
- **Verification gate:** accepts only reproducible evidence matching the target boundary.

## Loop

1. **Plan** — classify the requirement and update `.internal_master_plan.md`.
2. **Pre-flight** — verify repository root, working tree, target paths, and adapter readiness.
3. **Relay** — construct a self-contained Markdown context with absolute paths, scope, constraints, tests, stop conditions, and handover contract.
4. **Delegate** — call `delegate_task` with the context directly. Do not use JSON relay payload files.
5. **Execute** — edit only target files, validate, stage explicit files, commit, and write post-commit handover evidence.
6. **Verify** — Architect audits the handover and independently reruns declared tests.
7. **Gate** — pass, retry with a classified correction, or stop/escalate.
8. **Post-mortem** — record evidence and classify each new learning.
9. **Stabilize** — confirm workspace and master plan consistency before unlocking the next step.

## Requirement tiers

- **Minimal:** loose requirement; goal, targets, tests, handover, and stop conditions.
- **Standard:** known feature; adds constraints, shape contract, and surprises checklist.
- **Full:** stable multi-relay work; adds shared-resource contract, dependency map, pre-flight, and explicit stop conditions.

Keep each relay below 30 minutes expected execution. Split larger work. Never unlock a dependent step before its verification gate passes.

## Relay invariants

Every relay context must contain:

- project name and absolute project root;
- task ID and execution profile;
- self-contained task description;
- absolute target file paths with create/modify action;
- files explicitly out of scope;
- adapter-declared tool and dependency boundaries;
- verbatim tests with at least one structural and one negative assertion;
- stop conditions for known environment dead ends;
- exact handover path and contract;
- explicit commit procedure.

The first subagent command must verify location:

```text
cd {PROJECT_ROOT} && pwd && git rev-parse --show-toplevel
```

Do not rely on a `workdir` metadata field unless the runtime has proven that it changes the actual working directory. Absolute paths remain mandatory.

## Verification levels

Choose depth according to the artifact:

1. **Structural:** always required; parse or inspect output with a runtime assertion.
2. **Negative:** always required; prove a forbidden dependency, file, state, or mutation is absent.
3. **Runtime:** required for runnable applications, services, or served assets.
4. **Browser/DOM:** required when UI, HTML rendering, CSS behavior, or client-side JavaScript changes; check console errors and key DOM/state properties.
5. **Visual screenshot:** optional. If unavailable, use browser console/DOM checks; do not loop on a failing vision provider.

The adapter declares exact commands and available tools. The core defines evidence categories, not universal commands.

## Git and workspace safety

- Never use `git add -A` or `git add .` in a relay.
- Stage only explicit target files.
- Never stage internal state, handovers, learnings, or unlisted assets unless the relay names them.
- Before committing, verify `git diff --cached --name-only` against `target_files`.
- Fill the handover from post-commit evidence, not estimates.
- After committing, verify `git status --short` and record intentional untracked files.

## Handover contract

The completion report must contain these exact sections:

1. `## Raw Test Output`
2. `## Git Evidence`
3. `## Files Changed`
4. `## Surprises Checklist`
5. `## Contract Enforcement`

Raw output must be complete, not summarized. Git evidence must include the current commit, diff stat, and working-tree status. The files table must match the commit. All surprises must be disclosed.

## Gate matrix

Apply the first matching rule:

| Gate | Condition | Action |
|---|---|---|
| Fabrication | Evidence contradicts the workspace or cannot be reproduced | Stop and escalate. |
| Stagnation | Same error signature recurs after correction | Stop, record signature, escalate. |
| Environment blocker | Required daemon, package, credential, or permission is unavailable | Stop immediately; do not burn retries. |
| Spec drift | Test/path is wrong because the relay is underspecified | Prune context, correct relay, retry. |
| Execution error | Subagent failed to execute a valid relay | Retry with focused correction; two failures escalate. |
| Contract failure | Code passes but handover/evidence is incomplete | Metadata-only retry. |
| Validation cleared | Independent evidence matches scope and contract | Mark complete and unlock next step. |

Maximum three attempts per task ID. A repeated error signature is a hard stop.

## Learning lifecycle

Classify each observation as:

- **core:** project-agnostic orchestration or evidence rule;
- **adapter:** toolchain, environment, provider, or test-runner rule;
- **project-specific:** domain, design, asset, or product rule;
- **historical:** useful evidence that is not an active rule.

Only `core` learnings may be proposed for propagation into this document. Adapter and project-specific learnings stay in the project. Historical learnings remain archived. One run may justify an adapter rule; core promotion normally requires repetition or a safety/integrity reason.

## Telemetry

Record where available: task ID, model/provider, thinking mode, start/end/duration, retries, tool-call count, verification levels, gate result, and error classification. Metrics are observations, not universal model-selection rules.

## Compatibility

v4 was the JSON relay protocol. v5 introduced direct Markdown delegation context and environment-specific tool rules. v6 keeps direct context, makes the core project-agnostic, and moves local details into adapters.

The core is authoritative for orchestration. The adapter is authoritative for local paths, tools, dependencies, tests, protected files, and domain conventions.
