# Agent instructions

This file contains universal operating rules for AI agents working in this repository. Keep it short. Add project-specific rules only when they are not obvious from the code, configuration, tests, or documentation.

## General working style

- Read the relevant project files before changing anything.
- Prefer small, targeted changes over broad rewrites.
- Do not modify unrelated files.
- Preserve existing conventions unless the task explicitly changes them.
- Do not delete files or data unless the task explicitly requires it.
- Never store passwords, API keys, tokens, private keys, or real credentials in Git.
- Do not modify real `.env` files containing credentials.
- Avoid destructive shell or Git operations unless explicitly required and justified.

## Before changing code

1. Understand the requested result and the affected area.
2. Read relevant tests and documentation.
3. Identify the smallest reasonable change.
4. Check whether a reversible state already exists in Git.

## After changing code

- Run relevant deterministic tests in an agent-controlled execution workspace when available.
- Run lint, type, syntax, or policy checks when the project provides them.
- Verify the requested behavior rather than only checking that files changed.
- Update documentation when the change makes existing docs inaccurate.
- Summarize what changed, validation performed, limitations, and the next action.

## Git and branches

- Do not develop directly on `main` unless the user explicitly requests that workflow.
- Prefer one bounded task per task branch and Draft pull request.
- Intermediate local commits are allowed; they do not require an immediate push.
- Batch related remote writes instead of pushing after every small edit.
- Never use `git reset --hard`, force-push, history rewriting, broad `git clean`, or equivalent destructive operations unless the user explicitly authorizes the exact operation.

## Multi-agent collaboration

For simultaneous multi-agent work, read `docs/AGENT_WORKFLOW.md` before starting.

- One concurrent agent must have one bounded task, one task branch, and one isolated writable workspace.
- Concurrent agents must not share the same writable working tree.
- For local Git work, prefer one Git worktree per concurrent agent; an isolated cloud checkout/sandbox is an acceptable equivalent.
- A control/integration role owns decomposition, shared contracts, ownership boundaries, integration, conflict resolution, and the final review checkpoint.
- Define shared contracts and ownership before parallel implementation starts.
- Worker agents must not silently modify another agent's owned scope; cross-scope changes go through the control/integration role.
- For non-trivial parallel work, prefer an `integration/<feature>` branch. Worker branches integrate there before the final PR to `main`.
- QA/review should validate the assembled integration state, not only isolated worker branches.
- Each worker should leave a durable handoff using `docs/HANDOFF_TEMPLATE.md` or an equivalent project-specific record.
- Heavy CI belongs at meaningful integrated review checkpoints, not on every worker iteration.

## GitHub Actions

GitHub Actions minutes are a controlled project resource.

**CI is a review/release gate, not an iterative debugger.**

During normal development:

- keep the pull request in Draft while implementation is changing;
- validate in the agent-controlled workspace when available;
- batch related changes into one meaningful remote checkpoint;
- do not push merely to trigger CI;
- do not use repeated Draft -> Ready transitions as a CI loop;
- do not dispatch or rerun workflows blindly;
- inspect a failed run before deciding on a correction or rerun;
- trigger heavy CI only for a complete, stable review checkpoint.

Before any workflow edit, dispatch, rerun, or material CI-policy change, read `docs/GITHUB_ACTIONS_POLICY.md`.

Do not add, rename, delete, or materially change GitHub Actions workflows unless the task explicitly includes CI/workflow scope. New workflows must be added deliberately to the allowlist in `scripts/check_actions_policy.py`.

Do not introduce `pull_request_target` for executing pull-request code unless a dedicated security review explicitly requires it.

If there is no agent-controlled executable workspace, record relevant local checks as:

`NOT_RUN — no agent-controlled executable workspace`

Do not delegate routine shell/git/test execution to the user merely because the agent lacks an executable workspace. Final required CI evidence is still required when the project policy requires it.

## Definition of done

A task is complete when:

1. The requested behavior is implemented.
2. Relevant available checks pass, or unavailable checks are recorded accurately.
3. No unrelated behavior is intentionally broken.
4. Documentation is updated when necessary.
5. The final reviewed head is unambiguous and validation is not stale.
6. For multi-agent work, the accepted worker results have been integrated and the assembled state has been validated.
7. The agent gives a concise summary of changes, checks, limitations, and rollback considerations when relevant.
