# Safety

The lesson may describe architecture. It must not carry the system's secrets. Lint checks shape; the scan checks content. Neither replaces judgement.

## Never in a lesson or skeleton

- API keys, tokens, passwords, private keys, cookies, session ids, connection strings.
- Values of environment variables, even ones that look harmless.
- Customer or personal data: names, emails, order ids, payload samples from production.
- Internal hostnames, private IPs, service-account emails, cluster names, project ids.
- Company or customer names in a sample lesson, or code copied from a private repository.
- A private repo's real source, even trimmed. Use an invented shape with generic names.
- Screenshots or terminal output with credentials, internal URLs, or account ids.
- Security weaknesses spelled out as an exploit recipe, or incident details that identify someone.

The scan's generic patterns cover RFC 1918 addresses, hosts ending in `.internal`, `.corp`, `.local`, `.lan`, or `svc.cluster.local`, and `*.iam.gserviceaccount.com` emails. It cannot cover a project name or a cleverly described secret. Do not rely on it for that.

## Defaults

- A private source gets `sourceVisibility: private` and `visibility: internal`. No `source`, no `path:line` refs.
- `repoKey` for a private source is proposed and approved by the user.
- The dev server binds `127.0.0.1` only. Do not expose it on a LAN address or through a tunnel.
- Use invented systems in samples, tests, and patterns.

## Scan workflow

Run after the lesson is written and before rendering:

```sh
npm run lint -- "content/$repoKey/$slug"
npm run scan -- "content/$repoKey/$slug"
```

The scan runs gitleaks with the hub's `.gitleaks.toml` and redacts matches. It exits non-zero on a finding.

On a finding:

1. Do not render the lesson. Do not paste the matched value into the reply; the tool already redacted it.
2. Open the file and remove or replace the value. If the lesson needs the shape, use a generic placeholder.
3. Rerun both commands. A finding blocks the URL until both pass.
4. If the value looks like a real credential, tell the user and rotate it. Do not decide that it is fake on your own.
5. Do not edit `.gitleaks.toml`, add an allowlist entry, or skip the scan to make it pass. If it is a false positive, report the rule and ask the user.

## Incident steps

If a secret reached a lesson file, a rendered page, a commit, or a remote:

1. Stop. Report what leaked, where, and which lesson, without repeating the value.
2. Tell the user to revoke and rotate the credential now. Rotation is the fix; deleting the file is not.
3. Remove it from the lesson, rerun lint and scan, and do not render until both pass.
4. If it was committed, add a commit that removes it and tell the user the value is still in history. The user decides on history rewriting. Never force-push.
5. If it was pushed to the private repo, treat the PR as compromised: close it or fix it with a new commit, and rotate.
6. If it was published, remove the lesson through a PR and redeploy, and delete the old public deployments. A live URL can outlive the page, so rotation still comes first.

## Local render

- Confirm the URL is `http://localhost:4321/...` and the server binds `127.0.0.1`.
- Do not claim a URL when the port belongs to another app; report the conflict instead.
- Nothing is uploaded by rendering. The default reply does not mention upload or publish.