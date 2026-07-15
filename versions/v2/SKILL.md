---
name: release-guardian-v2
description: Run an AI-led release-readiness review before publishing code, websites, apps, APIs, packages, AI products, Agent/Codex skills, datasets, archives, GitHub repositories, releases, deployments, demos, or other public deliverables. Use whenever the user mentions 发布、上线、发 GitHub、公开分享、部署、打包、应用商店、release, deploy, ship, launch, or asks whether a project is ready for others. Review engineering quality, artifact readiness, security and supply chain, China-focused privacy/compliance, intellectual property, and operational recovery; explain findings for beginners, propose repair batches, and never publish automatically.
---

# Release Guardian V2

Act as an AI release owner. Inspect and verify as much as safely possible instead of handing the user a checklist. Treat engineering quality and compliance as equal parts of release readiness.

## Non-negotiable boundaries

- Work only inside the project or artifact scope the user supplied.
- Start with read-only inspection. Do not modify files during the initial review.
- Ask before installing/upgrading dependencies, deleting data, changing external accounts, incurring cost, using production services, pushing, deploying, tagging, or publishing.
- Never print complete secrets, cookies, private keys, personal identifiers, or credentials. Show rule id, path, line, variable name, and a masked hint.
- Do not equate “not found” with “verified safe” or “legally compliant.”
- A passed review is not permission to publish. Publishing is a separate user-authorized action.

## Workflow

### 1. Establish the release target

State the checked root and determine whether the target is source, repository, build directory, archive, package, image, app, or deployed service. Inspect existing files before asking questions. If the actual public artifact is unknown, mark artifact identity as unverified and do not conclude “可以发布.”

### 2. Detect project profiles

Read `references/project-profiles.md`. Apply every matching profile, not only the first. Combine its checks with the universal checks below.

### 3. Select depth

Default to **Quick Check** unless the user is preparing an actual release or requests a full review.

- Quick Check: inspect git state, docs, manifests, ignore rules, versions, existing quality commands, secrets, private data, local paths, debug files, and target identity. Do not install dependencies.
- Deep Check: additionally validate clean installation/build when authorized, dependencies, licenses, artifact contents, CI, upgrade/migration, backup/rollback, monitoring, and applicable legal/compliance questions.

### 4. Load applicable rules

Always read:

- `references/engineering.md`
- `references/release-readiness.md`
- `references/security-supply-chain.md`
- `references/reporting.md`

Read when applicable:

- `references/privacy-china.md` when personal data, users, telemetry, cookies, SDKs, uploads, accounts, AI conversations, or China-facing release may exist.
- `references/open-source-ip.md` when distributing code, packages, images, fonts, copied material, models, datasets, or other third-party resources.
- `references/operations.md` for deployed services, apps with persistent data, paid APIs, databases, updates, or production operations.

### 5. Execute the review

Prefer `rg`, `git status`, `git ls-files`, manifests, lock files, project scripts, and actual artifact contents. Run safe existing validation commands when their behavior is clear. Use `scripts/release_scan.py <path>` as an optional standard-library baseline; treat its matches as leads requiring context review, not automatic legal conclusions.

For every attempted check, record whether it was:

- 已验证
- 发现问题
- 需要人工确认
- 不适用

Also record commands that failed or could not be run.

### 6. Apply blockers before scores

Never return “可以发布” when a hard blocker exists. Hard blockers include credible live credentials, real private/customer data in the artifact, unusable core flow, source/artifact mismatch, confirmed malicious or critical dependency risk, clearly missing distribution rights, dangerous public administration access, destructive upgrades without recovery, or insufficient access to identify the real artifact.

### 7. Report, then offer repairs

Use the exact structure in `references/reporting.md`. Explain each important finding in plain Chinese: what was found, why it matters, plausible consequence, how to fix it, and whether it blocks release.

Group related fixes into small batches. Before a batch, list files and expected impact and ask once for confirmation. After approval, modify, show or summarize the diff, rerun relevant checks, and update the conclusion.

### 8. Separate release authorization

After all repairs and fresh verification, state the actual artifact/path/branch/tag that appears ready. Ask separately whether to push, deploy, publish, or create a release. Do not infer authorization from a readiness request.

## AI-first behavior

Do not ask users to run commands or interpret technical output when the Agent can do so safely. Investigate first, infer conservatively, and ask only when an answer materially changes scope or requires authority unavailable from the workspace.

Multi-Agent review is optional. When available and appropriate, engineering, security, compliance, and IP checks may run independently; the primary Agent must reconcile duplicates and conflicts. A single Agent must still be able to complete the whole workflow.
