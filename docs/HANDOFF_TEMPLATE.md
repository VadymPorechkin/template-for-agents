# Agent handoff template

Use this template for durable handoff between a worker agent and the control/integration role, or between agent sessions.

Copy it into the task's documentation area and fill only what is relevant.

## Identity

```text
Task ID:
Role:
Owner/agent:
Base branch:
Base SHA:
Final branch:
Final SHA:
Integration target:
```

## Goal

What result was assigned?

## Scope / ownership

```text
Owned paths or domain:
Allowed shared paths:
Explicit do-not-touch paths:
```

## Shared contracts

List the contracts this task depended on, for example API schemas, component props, DB boundaries, events, environment-variable names, file formats, or acceptance criteria.

## What changed

Summarize the implementation or deliverables. Point to the important files/areas rather than reproducing the diff.

## Decisions and assumptions

Record non-obvious decisions, assumptions, and rejected approaches that matter to integration or future work.

## Validation

Record exact checks that were actually run and their outcomes.

```text
Command/check:
Result:
Evidence/notes:
```

If the agent had no executable workspace, record unavailable local checks exactly as:

`NOT_RUN — no agent-controlled executable workspace`

Do not claim CI PASS or local verification that did not occur.

## Known limitations / blockers

List anything incomplete, uncertain, externally blocked, or intentionally out of scope.

## Contract changes

Did any shared contract change from the task's starting assumptions? If yes, describe the accepted change and who/what else must adapt.

## Integration notes

Tell the control/integration agent what matters when assembling this work:

- dependencies on other worker branches;
- expected conflict areas;
- shared files touched;
- ordering constraints;
- generated artifacts or migrations;
- follow-up checks required on the assembled state.

## Rollback

Describe how to revert or disable the change if it causes a problem. For trivial reversible changes, a normal Git revert may be sufficient; for data/runtime changes, document the real boundary explicitly.

## Next action

State the next concrete action for the control/integration role or next agent.
