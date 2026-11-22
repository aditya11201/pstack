---
name: test-first
description: Use when implementing a feature or fixing a bug that has a practical executable check, before writing the production change. Write the check, watch it fail for the right reason, make the smallest change, watch it pass.
---

# Test first

A check only proves something if you saw it fail before the change. This skill covers when to write that check and in what order.

## When it applies

- **A behavior with a cheap, local, executable check:** a unit test, a script assertion, or a CLI call with expected output. Apply the full cycle below.
- **Config, Helm, Terraform, or infrastructure changes with no behavior test:** skip the cycle. Run the closest targeted validation instead, such as `helm template` plus a diff, `terraform fmt -check`, a schema check, or a dry-run that is allowed. Then state what that validation does not prove.
- **A check that would need heavy harness work, brittle mocks, or production-only state:** use the reproduction command and say that no regression test was added, and why.

## Cycle

1. **Write one check for one behavior.**
   - Its name says what should happen.
   - It uses real code paths. Mock only what you cannot run.
   - It asserts the outcome the user cares about, not how the code is built inside.
2. **Run it and watch it fail.**
   - It must fail because the behavior is missing or wrong, not because of a typo, an import error, or a broken fixture.
   - If it passes already, the check is wrong or the behavior exists. Fix the check before touching the code.
3. **Make the smallest change that passes it.** Keep caller contracts, validation, and error handling. Add no extra options or abstractions.
4. **Run it and watch it pass.** Then run the surrounding tests to catch regressions.
5. **Clean up while the check stays green.** Then take the next behavior.

## Rules

- Production code written before its check gets the check added now. Then confirm the check fails if you undo the change: revert it temporarily or use a mutation, and see red.
- A bug fix starts with a check that reproduces the bug.
- Keep the failing output and the passing output. `evidence-before-done` quotes them.
- Do not change a check just to make it pass. If the check was wrong, say so and fix it before the code.

## Report

- **Cycle used:** name the check, the command, the failure output before the change, and the pass output after it.
- **Validation used instead:** name the validation and what it leaves unproven.
