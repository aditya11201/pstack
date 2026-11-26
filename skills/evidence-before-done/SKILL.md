---
name: evidence-before-done
description: Use before saying work is done, fixed, passing, deployed, or ready for review, and before committing, pushing, or opening an MR/PR. Every success claim needs a fresh check on the current revision, quoted in the reply.
---

# Evidence before done

A claim of success is a claim about output you have seen. If you have not run the check on the current state, you do not know the result, and the reply has to say so.

## Before any success claim

1. **Name the check that proves the claim.**

   | Claim | Check that proves it |
   |---|---|
   | Tests pass | The test command, with zero failures in its output. |
   | Bug fixed | The original reproduction, now passing. |
   | Build or lint clean | The build or lint command, exit code 0. |
   | Config or IaC valid | The validation the project allows, such as `fmt -check`, `helm template`, or a CI plan job. |
   | Deployed or applied | The live state, read back. Example: `gcloud … describe`, `kubectl get`, the job status. |
   | Requirements met | Each requirement in the spec or plan, checked one by one. |
   | Worker finished | The diff or artifact the worker produced, inspected. The worker's own report does not count. |
   | Worker ran on the required model | The launched model read back from Orca (`worker-show`), equal to the model required. |
2. **Run it now,** on the current revision or diff. Evidence from before your last edit is stale.
3. **Read the whole output.** Check the exit code, the failure count, and any warnings.
4. **Report what the output shows.** If it shows success, state it plainly and quote the key line. If it does not, report the actual status.
5. **A missed requirement is a failure.** Evidence that an explicit requirement from the user, spec, or plan was not met, such as "requested X, got Y", fails the claim even when everything else succeeded. Report it as failed or blocked, never as done.

## Reuse and limits

- You may reuse evidence that is fresh for the same artifact. Rerun only when it is stale or incomplete, or when the user asks for an independent check.
- Say what the check does not cover. Examples: "verified locally; the CI plan job has not run", "unit tests pass; not tested against the real API".
- These do not count as evidence: "should work", "looks right", a previous run, a different command, a proxy (the file exists, it compiled), or a worker saying it succeeded.

## In the reply

- **Every success claim** gets its command and the key output line or link.
- **Anything not verified** is named as unverified. It is not dressed up as done.
- **Done after an outward action** (push, MR, ticket update) includes the link or ID you read back after the action.
