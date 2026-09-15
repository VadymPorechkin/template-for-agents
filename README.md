# Template for Agent-Driven Development

A small, deliberately conservative starter repository for software projects developed with AI agents.

The template keeps the universal layer small: agent instructions, Git/GitHub safety rules, a cost-controlled CI gate, secret-safe defaults, and lightweight project documentation. Project-specific frameworks, dependencies, deployment systems, and domain rules should be added only when a concrete project needs them.

## Core principles

- Give agents the minimum access and automation they need.
- Treat GitHub Actions as a review/release gate, not an iterative debugger.
- Keep pull requests in Draft while implementation is changing.
- Batch related remote writes instead of pushing after every edit.
- Run deterministic checks in an agent-controlled workspace when available.
- Trigger full CI only for a stable review checkpoint.
- Keep secrets and mutable runtime data out of Git.
- Prefer small, targeted changes over broad rewrites.
- Preserve a known Git state before substantial work.

## Included files

```text
AGENTS.md
README.md
.gitignore
.gitattributes
.editorconfig
.env.example
.github/
  pull_request_template.md
  workflows/
    ci.yml
docs/
  GITHUB_ACTIONS_POLICY.md
  architecture.md
  decisions.md
scripts/
  check_actions_policy.py
src/
tests/
output/
```

## Starting a new project

1. Create a new repository from this starter or copy its files into a new repository.
2. Replace the project-name and purpose placeholders in this README.
3. Add the chosen language/framework and project-specific tooling.
4. Extend `.gitignore` and `.env.example` for the actual stack.
5. Update `AGENTS.md` only with project rules that are not obvious from the repository itself.
6. Extend `.github/workflows/ci.yml` with the real project checks while preserving the Actions cost-control policy.
7. Update the workflow allowlist in `scripts/check_actions_policy.py` only when adding an intentional workflow.
8. Make an initial project-stack commit before assigning substantial work to an agent.

## Recommended Git workflow

```text
task branch
  -> Draft PR
  -> agent implementation + agent-workspace checks
  -> one batched push
  -> Ready for review
  -> one exact-head GitHub Actions checkpoint
  -> review
  -> bounded correction round if needed
```

Do not use remote CI as a trial-and-error loop.

## Project-specific additions

This repository intentionally does **not** include Docker, a framework, package manager configuration, database tooling, deployment workflows, MCP servers, or agent skills. Add those only when the project actually requires them.
