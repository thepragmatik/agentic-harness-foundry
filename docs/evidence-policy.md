# Evidence Handling Policy

Status: `specified`

The repository is public. Runtime evidence is therefore **local/private by default**, even when the evidence itself is required to complete a task.

## Default rule

Paths under `evidence/` are intentionally gitignored.

A task may write host/config/benchmark/security evidence there, but an agent MUST NOT commit or paste that evidence into a public issue/PR/chat unless it has been explicitly reduced to a safe summary.

## Never publish by default

- API keys, OAuth tokens, cookies or credential-store output;
- full `.env` files;
- private keys/certificates;
- unredacted Hermes/Pi/provider configs;
- absolute paths that disclose sensitive usernames/customer/project names when avoidable;
- raw prompts/conversations containing private data;
- Mnemosyne/LCM databases or dumps;
- raw repository/customer source used as an evaluation fixture;
- malicious/security-test payload captures that include real secrets;
- provider request/response bodies from sensitive tasks;
- model files.

Use sentinel/fake secrets for security tests.

## What may be committed after review

Prefer compact, manually reviewed summaries containing only what is needed to support a decision:

- pinned public package/model/version/commit identifiers;
- aggregate tokens, latency, memory and throughput measurements;
- pass/fail outcomes;
- normalized failure reason;
- sanitized command line with secret values removed;
- content/model artifact hashes that do not reveal private content;
- diagrams/spec changes;
- synthetic/non-sensitive fixtures.

If a durable validation summary is useful, add it under `docs/validation/` only after a human or explicit sanitization task confirms that it contains no sensitive material.

## Evidence references in `TASKS.md`

`TASKS.md` paths such as `evidence/m1/granite-q1.json` describe the **local evidence contract**, not an instruction to commit the file.

A checkbox may be marked complete based on local evidence. The commit should normally contain only the implementation/spec change and, when useful, a sanitized validation summary.

## Redaction is not enough for secrets

Known secrets should be excluded from evidence generation where possible rather than collected and later redacted. For example:

- record the name of an environment variable, never its value;
- record that a provider credential was present, not the token;
- hash synthetic fixture content if identity is needed;
- use a sentinel secret for egress tests.

## Public issue / PR discipline

Do not attach raw logs reflexively. Extract the smallest safe excerpt needed to explain a failure.

Before creating a public issue upstream, verify that the excerpt does not include:

- host/home paths with sensitive naming;
- private repository names/URLs;
- prompts or memory content;
- headers/auth data;
- environment dumps;
- customer/source code.

## Incident rule

If real secret material is accidentally committed, do not rely on deleting the file/commit alone. Treat the secret as exposed and rotate/revoke it through the provider/credential owner, then clean repository history as a separate remediation.

## Agent rule

Agents MUST treat all local runtime evidence as `sensitive` until a task explicitly authorizes a sanitized publication. When uncertain, keep it untracked and report only the evidence path plus pass/fail result.
