# GitHub Actions cost-control policy

Status: **BASE TEMPLATE POLICY**

This policy exists to prevent AI-agent iteration from consuming GitHub Actions minutes through repeated remote commit -> push -> full CI loops.

## 1. Governing principle

> CI is a review/release gate, not an iterative debugger.

Routine implementation and debugging should happen in an agent-controlled execution workspace when one is available. GitHub-hosted CI is reserved for a complete review checkpoint, an explicitly justified manual checkpoint, and post-merge verification of `main`.

A changed pull-request head invalidates earlier CI evidence for exact-head review.

## 2. Default development flow

```text
agent edits + agent-workspace tests
-> Draft PR remains Draft
-> one meaningful batch push
-> verify remote head
-> Draft -> Ready for review
-> one exact-head CI checkpoint
```

Intermediate local commits are fine. They do not imply an immediate push.

If the agent has no executable workspace, it records local checks exactly as:

`NOT_RUN — no agent-controlled executable workspace`

The agent should still prepare one complete bounded remote checkpoint instead of emitting one commit per file or asking the user to run routine commands on the agent's behalf.

## 3. Trigger policy

The base heavy CI workflow uses:

- `pull_request` with `types: [ready_for_review]` only;
- `push` to `main` for post-merge verification;
- `workflow_dispatch` for intentional manual checkpoints.

For heavy workflows:

- automatic `pull_request` activity type `synchronize` is forbidden;
- bare `pull_request:` without an explicit final-review activity type is forbidden;
- `opened` and `reopened` are not full-CI events by default;
- `concurrency` is required;
- `cancel-in-progress: true` is required for review CI;
- every job must have a bounded `timeout-minutes`;
- expensive specialized workflows should use narrow `paths` filters when practical;
- `pull_request_target` must not be introduced for executing untrusted PR code without a dedicated security review.

## 4. Remote-write budget

Default per implementation or review-fix round:

```text
complete bounded edits
+ available agent-workspace checks
+ documentation updates
-> one batch push
```

Rules:

1. Do not push after every small edit.
2. Do not push only to obtain a SHA, run ID, artifact ID, receipt, or comment update.
3. Opening or updating a Draft PR is not a reason to run full CI.
4. Do not dispatch CI after each failing local test.
5. Do not repeatedly change Draft -> Ready solely to obtain more CI runs.
6. If a genuine code/test defect is found in final CI, move back to Draft, collect the fixes into one bounded correction round, then produce one new review checkpoint.

## 5. Failures and reruns

A failed workflow is evidence to inspect, not a button to press repeatedly.

- Code/test failure: diagnose, fix as one bounded correction round, and create a new exact-head checkpoint.
- Confirmed transient GitHub runner/service failure: one bounded rerun is reasonable after the cause is identified.
- Ambiguous failure: inspect logs before rerunning.
- `cancel-in-progress` is defense in depth; it does not justify frequent pushes.

## 6. Permissions and checkout

Default workflow permissions should be least-privilege:

```yaml
permissions:
  contents: read
```

Grant write permissions only to a workflow that genuinely needs a narrowly scoped write action.

Checkout steps should normally use:

```yaml
with:
  persist-credentials: false
```

Actions used by security-sensitive workflows should be pinned deliberately. The base template pins `actions/checkout` to an exact commit.

## 7. Workflow governance

The base workflow allowlist is:

```text
ci.yml
```

Adding, renaming, deleting, or materially changing workflows is a deliberate governance change, not a routine feature-edit side effect. When a project intentionally adds workflows such as `deploy.yml`, `e2e.yml`, or `release.yml`, update the allowlist and policy checker in the same reviewed change.

`scripts/check_actions_policy.py` is an offline guard. It rejects unregistered workflows and common policy regressions such as automatic `synchronize` CI, missing final-review/manual gates, missing concurrency, missing timeouts, weakened read-only permissions, or credential persistence.

## 8. Specialized expensive workflows

When a project adds deployment bundles, browser suites, integration environments, or other expensive jobs:

- keep the final-review gate;
- add narrow `paths` filters where possible;
- use explicit timeouts;
- use concurrency groups;
- avoid broad write permissions;
- avoid automatic execution for docs-only or unrelated changes.

## 9. Stop conditions

Stop and return the task for review rather than weakening the policy when:

- a required final check cannot run;
- the exact reviewed head is ambiguous;
- a proposed shortcut restores per-push full CI;
- an unplanned workflow appears outside the allowlist;
- a task attempts to describe a real code/test failure as an infrastructure outage without evidence;
- a workflow needs materially broader permissions or a new trust boundary.
