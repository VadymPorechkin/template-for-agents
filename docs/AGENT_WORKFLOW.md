# Multi-agent development workflow

This document defines the default collaboration model when more than one AI agent works on the same project at the same time.

The core formula is:

> **one concurrent agent = one bounded task = one task branch = one isolated writable workspace**

For local Git-based work, the preferred isolated workspace is a **Git worktree**. A separate cloud sandbox or other isolated checkout is equivalent if agents cannot write into each other's working directories.

## 1. Why isolation is required

Concurrent agents must not share the same writable working tree. If several agents edit the same checkout at the same time, one agent can observe or overwrite another agent's uncommitted changes, tests can run against a moving filesystem, and the resulting Git state becomes ambiguous.

A Git worktree solves the filesystem-isolation problem while keeping all branches attached to the same repository.

Example:

```text
project-control/      -> integration/feature-x
project-design/       -> task/feature-x-design
project-frontend/     -> task/feature-x-frontend
project-backend/      -> task/feature-x-backend
project-qa/           -> task/feature-x-qa
```

A worktree does not solve architectural conflicts by itself. Parallel work also needs explicit scope, ownership, and shared contracts.

## 2. Roles

### Control / integration agent

The control agent owns coordination and integration. Its default responsibilities are:

- understand the requested outcome;
- decompose the work into bounded parallel tasks;
- identify dependencies between tasks;
- define or confirm shared contracts before parallel implementation starts;
- assign file/domain ownership;
- create or coordinate the integration branch and task branches;
- review worker diffs and handoffs;
- integrate accepted work;
- resolve cross-task conflicts deliberately;
- run or coordinate integrated validation;
- prepare the final review checkpoint to `main`.

The control agent should not casually redo worker tasks. It should primarily coordinate, review, integrate, and resolve boundaries.

### Implementation agent

An implementation agent owns one bounded part of the task, such as frontend, backend, database, infrastructure, or a narrowly scoped feature.

It must stay inside its assigned scope and report cross-scope blockers instead of silently modifying another agent's owned area.

### Specialist agent

A specialist may own design, security, data, performance, infrastructure, research, or another cross-cutting area. Its scope and write permissions must still be explicit.

### QA / review agent

A QA agent may work in two phases:

1. **parallel preparation** — derive tests and acceptance checks from the shared specification/contracts while implementation is still in progress;
2. **integrated validation** — test the assembled integration branch independently before the final review checkpoint.

QA should validate the integrated behavior, not only isolated worker branches.

## 3. Branch topology

For a non-trivial multi-agent feature, prefer:

```text
main
  |
  +-- integration/feature-x
        |
        +-- task/feature-x-design
        +-- task/feature-x-frontend
        +-- task/feature-x-backend
        +-- task/feature-x-qa
```

Rules:

- `main` remains the stable integration target.
- `integration/<feature>` is the assembly branch for the multi-agent task.
- each worker branch starts from the agreed integration base;
- worker branches do not merge directly to `main` by default;
- the final integration branch is reviewed and validated as one coherent change before merge to `main`.

For very small tasks, the integration branch may be unnecessary. Do not add process where it provides no isolation or coordination benefit.

## 4. Shared contracts come before parallel code

Parallel work is safe only when agents agree on the boundaries they share.

Examples of shared contracts:

- API routes, methods, request/response schemas, and error semantics;
- database schema or migration boundaries;
- component props and UI state contracts;
- event names and payloads;
- file formats;
- environment-variable names;
- acceptance criteria;
- ownership boundaries.

Example:

```text
POST /api/login

request:
{
  "email": string,
  "password": string
}

response:
{
  "token": string,
  "user": {...}
}
```

Frontend and backend can now work independently against the same contract.

If the contract must change during implementation, the agent discovering the problem reports it to the control agent. The control agent coordinates the change before parallel workers diverge.

## 5. Ownership

Each parallel task should declare primary ownership.

Example:

```text
Frontend agent
  owns:
    src/frontend/**
    src/components/**
    tests/frontend/**

Backend agent
  owns:
    src/backend/**
    database/**
    tests/backend/**

QA agent
  owns:
    tests/integration/**
    test plans / validation evidence
```

Shared files such as package manifests, schemas, generated clients, root configuration, or shared types require coordination when more than one task may touch them.

An agent that discovers a required change outside its scope should report a blocker or integration requirement rather than silently expanding scope.

## 6. Task packet

Before a worker starts, it should have enough information to act without inventing missing architecture.

A useful task packet contains:

```text
Task ID:
Role:
Goal:
Base branch / base SHA:
Owned paths / domain:
Allowed shared paths:
Do-not-touch paths:
Shared contracts:
Acceptance criteria:
Required checks:
Known dependencies:
Handoff location:
```

The task packet may live in an issue, task document, PR description, or another durable project artifact.

## 7. Worker execution

Each worker follows this sequence:

```text
read task + contracts
-> inspect relevant project context
-> implement only owned scope
-> run available deterministic checks in its isolated workspace
-> update handoff
-> batch related changes
-> one meaningful remote checkpoint
-> stop implementation when the assigned result is complete
```

Workers must not use repeated GitHub Actions runs as an iterative debugger.

## 8. Handoff

Every parallel worker should leave a durable handoff. Use `docs/HANDOFF_TEMPLATE.md` as a starting point.

The handoff records at least:

- role and task;
- base and final head;
- files/areas changed;
- important decisions and assumptions;
- validation performed;
- checks not run and why;
- known limitations or blockers;
- shared-contract changes;
- integration notes;
- rollback considerations.

The handoff prevents the control agent from having to reconstruct important state from chat history.

## 9. Integration

The control agent reviews each worker result before integration.

Recommended sequence:

```text
worker branches complete
-> review diffs + handoffs
-> integrate into integration/<feature>
-> resolve conflicts against shared contracts
-> run integrated deterministic checks
-> QA/review agent validates assembled behavior
-> bounded correction round if needed
-> final integration PR to main
-> Ready for review
-> exact-head GitHub Actions checkpoint
-> merge to main
```

A merge conflict is not merely a text-editing problem. The control agent must decide which behavior and contract are correct before resolving the conflict.

## 10. GitHub Actions in multi-agent work

The cost-control rule still applies:

> **CI is a review/release gate, not an iterative debugger.**

By default, worker branches and worker PRs should not each trigger expensive full CI. For larger multi-agent work, worker PRs can target the integration branch and remain outside the heavy `main` review gate. The assembled `integration/<feature>` branch becomes the main full-CI checkpoint when its PR is made Ready for review against `main`.

Agents should validate their own scope in their isolated workspaces when possible. The final integrated state still requires exact-head validation.

## 11. Conflict and blocker rules

Return control to the integration agent when:

- two agents need to modify the same owned files;
- a shared contract must change;
- a worker needs to cross an explicit ownership boundary;
- a dependency assumption is no longer true;
- the integration base changed materially;
- tests reveal incompatible worker assumptions;
- resolution would require destructive Git operations or broader permissions.

Do not let multiple agents independently "fix" the same cross-cutting problem.

## 12. When not to parallelize

Parallel agents are not automatically better. Keep work sequential when:

- the task is small;
- most edits touch the same files;
- the architecture or contract is still unknown;
- one task depends heavily on the exact result of another;
- coordination cost is larger than implementation cost.

The goal is independent parallelism, not the maximum number of agents.

## 13. Summary formula

```text
shared specification + contracts
            |
      control agent
            |
   task decomposition
     /      |      \
 worktree worktree worktree
 branch   branch   branch
 scope    scope    scope
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

The quality of multi-agent development depends more on isolation, clear contracts, and disciplined integration than on the number of agents running at once.
