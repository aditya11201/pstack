---
name: root-cause
description: Use when something is broken (a bug, a failing test or pipeline job, an error, unexpected behavior) before proposing or making any fix. Finds the cause with evidence, then fixes the cause instead of the symptom.
---

# Root cause

No fix before a cause backed by evidence. A guess that happens to work hides the real problem and costs more later.

## 1. Reproduce

- Read the whole error: message, stack trace, exit code, job log. Note the file, line, and the values involved.
- Find the smallest way to trigger the failure: a command, a test, an input. Run it and record the output.
- If you cannot reproduce it, collect more data (logs, config, environment, versions) instead of guessing. Report that the failure is not reproduced yet.
- Check what changed: `git log` and `git diff` for the area, plus recent dependency, config, and environment changes.

## 2. Trace

- Follow the bad value back to where it first goes wrong. The place that throws is often not the place that is wrong.
- In a system with several layers (CI → script → tool → cloud API, or client → service → database), find which layer is broken before changing any of them. Check what goes in and what comes out at each boundary, with one targeted log line or read-only command per boundary.
- Find a similar case that works (another environment, an older commit, a sibling resource). List every difference between the working case and the broken one, including the ones that look irrelevant.

## 3. Test one hypothesis at a time

- State it plainly: "X fails because Y, which shows up as Z."
- Choose the smallest experiment that would prove it wrong, and change one variable only.
- If it is disproved, drop it and form a new hypothesis from the evidence. Do not stack a second change on top of a failed one.
- If you do not know something, say so and look it up. Do not paper over the gap.

## 4. Fix

- Make the failure executable first: a failing test via `test-first`, or, when no practical test exists, the reproduction command from step 1.
- Make one change that addresses the cause. No unrelated cleanup in the same change.
- Run the reproduction again, then the nearby tests. Report with `evidence-before-done`.

## When fixes keep failing

After three fixes that each failed, or that each moved the failure somewhere else, stop. That pattern usually means the design or an assumption is wrong, not the last line you touched. Report to the user:

- what you tried;
- what each attempt showed;
- which assumption you now doubt.

Ask before trying a fourth fix.

## Report

The reply covers:

- the cause, in one sentence;
- the evidence: the command and its output;
- the fix;
- what it does not prove. Example: "verified locally; the CI job still has to run".
