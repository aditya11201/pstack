# Publishing

Local is the default. Upload and publish are separate, explicit requests for one lesson. Rendering locally never implies either.

## Levels

| Level | Trigger | What happens | Leaves the machine? |
|---|---|---|---|
| Local | Default | Write, lint, scan, render on `localhost:4321`. | No. |
| Upload | The user asks to upload or back up this lesson. | Push the lesson branch to the private hub repo and open a PR. `check.yml` runs lint, scans, both builds, and Access-locked previews. Nothing deploys. | Private repo and Access-locked previews only. |
| Publish | The user asks to publish this lesson. | Upload if needed, merge by the rules below, deploy. | The live sites. |

A request to upload is not a request to publish. The default reply ends with the local URL and does not offer or ask about either.

## Visibility rules

| Lesson | Default `visibility` | Merge |
|---|---|---|
| From a public source | `public` | After `check.yml` is green. |
| From a private source, kept internal | `internal` | After `check.yml` is green; deploys to the internal site only. |
| From a private source, made public | `public`, only on the user's request | Show the Access-locked preview. After the user's explicit go, add `publicApproval`, then merge. |

- A public lesson from a private source keeps `sourceVisibility: private`, has no `source`, and renews `publicApproval` whenever its content changes.
- Never copy private source into a lesson to make it publishable. Rewrite it as an invented shape.
- An internal lesson never appears in the public build, index, or sitemap. `LESSON_TARGET=public` filters it out; verify the built artifact before any deploy.

## Approval gate

1. Build the lesson with `visibility: internal` first.
2. Show the user the Access-locked preview of the PR.
3. Ask for an explicit yes for that lesson.
4. Add `publicApproval: { by: <user>, date: <ISO date> }`, push a new commit, wait for `check.yml`.
5. Merge only after green.

The approval is for that lesson at that content. Do not reuse it for another lesson or after a content change.

## Phase 1: hub bootstrap

Only when the hub is missing. It needs no GitHub repo, no Cloudflare account, and no network beyond npm.

1. Confirm Node 24 and `gitleaks` are installed.
2. Create `~/projects/learn-with-me` with the hub: Astro static site, the lesson schema and parser, the role list, `src/styles/tokens.css`, `scripts/lint.mjs`, `scripts/scan.sh`, `.gitleaks.toml`, and the pinned dependencies from the spec.
3. Run `git init` inside it. Add no remote.
4. Write `~/.config/learn-with-me/config` with one line: `hub=<absolute path>`.
5. Render the sample lesson locally and confirm `http://localhost:4321/<repoKey>/<slug>/` returns 200.
6. Run `npm test`, `npm run lint`, and `npm run scan` to prove the hub is healthy.

Do not write API tokens or secrets into the config, the repo, or any lesson. The config holds only the hub path.

## Phase 2: bootstrap, only when the user first wants to upload or publish

Ask first; this is a new outward step. Then:

1. The user creates a Cloudflare account, enables Zero Trust Free, and creates an API token with Pages: Edit only. The token and account id go into GitHub Actions secrets, never into a file.
2. Create the private GitHub repo `aditya11201/learn-with-me` and add it as the hub's remote.
3. Add the workflows: `check.yml` (PR), `publish.yml` (push to main), `security.yml` (CodeQL, zizmor), and Dependabot.
4. Create both Pages projects with wrangler: `learn-with-me` public and `learn-with-me-internal` behind Access.
5. Put Access in front of all of `learn-with-me-internal` and its previews, and in front of `learn-with-me` previews.
6. Confirm push protection and secret scanning are on.

Never create or upgrade accounts, enter payment details, or write tokens to files.

## Upload

1. Confirm the user asked to upload this lesson.
2. Ensure the lesson branch is committed and lint and scan pass locally.
3. `git push -u origin lesson/<repoKey>/<slug>`.
4. `gh pr create` with the lesson summary and the local check output.
5. Wait for `check.yml`. A red check is fixed with a new commit on the same branch. Never force-push. Never merge on red.
6. Report the PR URL and the Access-locked preview. Do not deploy.

If a PR for the branch already exists, resume it: `gh pr list --head lesson/<repoKey>/<slug>`. The PR is the only stored state.

## Publish

1. Confirm the user asked to publish this lesson, not only to upload.
2. Upload first if there is no PR.
3. Apply the visibility rule and the approval gate above.
4. Merge with `gh pr merge` using the user's own credentials. No workflow auto-merges.
5. `publish.yml` runs the same scans and builds, rescans both `dist/` outputs, and deploys exactly those artifacts.
6. Verify the public URL and, for an internal lesson, that an unauthenticated request gets the Access login page.
7. If a deploy fails, report the last good deployment and roll back from the Pages dashboard.

## Update and remove

- **Update:** rerun the skill at the newer commit, keep `repoKey`/`slug` stable, and use the same branch name. Renew `publicApproval` if a public lesson from a private source changed.
- **Remove locally:** delete `content/<repoKey>/<slug>/`.
- **Remove when published:** open a PR that deletes the folder, merge after green, and redeploy. For a public lesson, also delete the old deployments (`wrangler pages deployment delete`).
- **Rotate first:** if a credential ever reached a page, rotate it before cleaning up. See `safety.md`.