# Template for Agent-Driven Development

A small, deliberately conservative starter repository for software projects developed with AI agents.

The template keeps the universal layer small: agent instructions, Git/GitHub safety rules, a cost-controlled CI gate, multi-agent coordination rules, secret-safe defaults, and lightweight project documentation. Project-specific frameworks, dependencies, deployment systems, and domain rules should be added only when a concrete project needs them.

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
- For concurrent work: one agent = one bounded task = one branch = one isolated writable workspace.
- Define ownership and shared contracts before parallel implementation.
- Use a control/integration role to assemble and validate multi-agent work.

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
  AGENT_WORKFLOW.md
  GITHUB_ACTIONS_POLICY.md
  HANDOFF_TEMPLATE.md
  OPERATOR_GUIDE_UA.md
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
2. Replace the project-name and purpose text in this README.
3. Add the chosen language/framework and project-specific tooling.
4. Extend `.gitignore` and `.env.example` for the actual stack.
5. Update `AGENTS.md` only with project rules that are not obvious from the repository itself.
6. Fill `docs/architecture.md` with durable architectural boundaries and flows.
7. Record non-obvious durable decisions in `docs/decisions.md`.
8. Extend `.github/workflows/ci.yml` with the real project checks while preserving the Actions cost-control policy.
9. Update the workflow allowlist in `scripts/check_actions_policy.py` only when adding an intentional workflow.
10. Make an initial project-stack commit before assigning substantial work to an agent.

For the operator-oriented setup checklist in Ukrainian, read `docs/OPERATOR_GUIDE_UA.md`.

## Recommended single-agent Git workflow

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

## Recommended multi-agent workflow

For non-trivial parallel work, read `docs/AGENT_WORKFLOW.md`.

The default model is:

```text
shared specification + contracts
            |
      control agent
            |
   task decomposition
     /      |      \
 isolated isolated isolated
 workspace workspace workspace
 branch    branch    branch
   \        |        /
     durable handoffs
            |
   integration branch
            |
      integrated QA
            |
       final full CI
            |
           main
```

For local Git-based work, Git worktrees are the preferred way to give concurrent agents separate writable checkouts without cloning the repository repeatedly.

Worker agents should stay inside explicit ownership boundaries. The control/integration agent reviews and assembles the results. QA validates the assembled integration state before the final review checkpoint.

## Project-specific additions

This repository intentionally does **not** include Docker, a framework, package manager configuration, database tooling, deployment workflows, MCP servers, or agent skills. Add those only when the project actually requires them.
