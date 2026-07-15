---
name: release-guardian
description: Run a pre-release guardian review before publishing any code, webpage, app, GitHub repository, release tag, demo package, or public share. Use this skill whenever the user says "执行发布检查", "帮我发布前Review", "发布前检查", "上线前检查", "准备发布", "准备上线", "发 GitHub", "打包发布", "release", "deploy", or when the current work is about to be shared publicly. It scans for secrets, privacy leaks, gitignore gaps, demo-data risks, license/readme/changelog gaps, version/release-note readiness, and practical key/API safety controls, then returns a compact scorecard.
---

# Release Guardian

Use this skill before anything leaves the private workspace: code repositories, static sites, H5 pages, mobile apps, packaged demos, GitHub releases, public ZIP files, or deployment folders.

The goal is a fast, conservative release-readiness screen. Prefer clear warnings over silence. Do not claim the release is safe if files were not scanned.

## Operating Rules

1. Work from the project or release package root. If the user did not specify a path, use the current workspace root and say which path was checked.
2. Prefer `rg`, `git status`, `git ls-files`, `find`, package metadata, and repository files over manual inspection.
3. Exclude dependency/build/cache folders unless the release artifact itself is one of those folders: `node_modules`, `.git`, `.next`, `.nuxt`, `dist`, `build`, `coverage`, `.venv`, `venv`, `target`, `Pods`, `DerivedData`.
4. Never print full secret values, tokens, passwords, cookies, private addresses, ID numbers, or bank numbers. Show only the variable name, file path, and a short masked hint when needed.
5. If a high-risk finding appears, mark the relevant section `❌` even if most checks passed.
6. Keep the final answer short and scorecard-first. Put detailed evidence only when there are warnings or failures.

## Workflow

### Step 1: Secret Scan

Scan for committed secrets and secret-like names/values.

Check at least:

- API keys and generic key names: `API_KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `PRIVATE_KEY`, `CLIENT_SECRET`, `WEBHOOK_SECRET`
- OpenAI: `OPENAI_API_KEY`, `sk-...`, `sk-proj-...`
- Anthropic: `ANTHROPIC_API_KEY`, `sk-ant-...`
- Gemini / Google: `GEMINI_API_KEY`, `GOOGLE_API_KEY`, service account JSON, `AIza...`
- Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- Firebase: `FIREBASE`, `firebaseConfig`, service account credentials
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AKIA...`
- Azure: `AZURE_CLIENT_SECRET`, `AZURE_STORAGE_CONNECTION_STRING`
- Tencent Cloud: `TENCENT_SECRET_ID`, `TENCENT_SECRET_KEY`
- Alibaba Cloud: `ALIYUN_ACCESS_KEY_ID`, `ALIYUN_ACCESS_KEY_SECRET`, `LTAI...`
- Stripe: `STRIPE_SECRET_KEY`, `sk_live_...`, `rk_live_...`, webhook signing secret
- GitHub: `GITHUB_TOKEN`, `ghp_...`, `github_pat_...`
- JWT: `JWT_SECRET`, hardcoded JWT tokens
- Environment files: committed `.env`, `.env.local`, `.env.production`, `.env.*`

Classify:

- `✅` no suspicious secret indicators found.
- `⚠️` secret-like names exist but appear to be examples/placeholders.
- `❌` real-looking secret values, env files committed, private keys, live tokens, or passwords are present.

Recommended fixes:

- Move real values into `.env` or the platform secret manager.
- Rotate any key that may already have been committed.
- Use `.env.example` with placeholder values only.

### Step 2: Privacy Check

Scan for personal or environment-identifying information.

Check at least:

- Real names, especially common demo names mixed with realistic contact data.
- Email addresses.
- Mainland China phone numbers and common international phone formats.
- Computer usernames, Mac usernames, and absolute paths: `/Users/...`, `C:\Users\...`, `Documents/`, `Desktop/`, `Downloads/`.
- The current user's likely names/usernames when visible in paths, for example `Hazel`, `hazel1996`.
- Home addresses, ID card numbers, bank card numbers.
- Cookies, session values, access tokens, refresh tokens.
- Test accounts and test passwords.

Classify:

- `✅` no personal/private identifiers found.
- `⚠️` only local paths, generic emails, or clearly fake demo accounts found.
- `❌` real-looking personal data, account credentials, cookies, tokens, ID numbers, bank numbers, or home addresses found.

Recommended fixes:

- Replace with neutral demo values.
- Remove local absolute paths from docs, logs, configs, screenshots, and generated files.
- Redact credentials and rotate exposed tokens.

### Step 3: Git Ignore

Check whether `.gitignore` exists and includes:

- `.env`
- `node_modules`
- `dist`
- `coverage`
- `*.log`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `.DS_Store`

Classify:

- `✅` `.gitignore` exists and covers the core items.
- `⚠️` `.gitignore` exists but misses one or more recommended items.
- `❌` no `.gitignore`, or high-risk generated/private files are tracked.

### Step 4: Demo Data

Scan for realistic-looking test data that could be mistaken for real customer or case material.

Examples:

- `客户A`, `客户B`, `张三`, `李四`, `王五`, `合同1`, `身份证`, `银行卡`
- Realistic emails, phones, addresses, companies, legal case names, contract names, account/password pairs.

Classify:

- `✅` demo data is neutral or absent.
- `⚠️` generic demo names exist but no sensitive details are attached.
- `❌` realistic customer/case/identity/payment data appears in files intended for release.

Recommended fix: replace with clearly fictional demo data, for example `Demo User`, `demo@example.com`, `Example Co., Ltd.`, `000000`.

### Step 5: License And Project Docs

Check for:

- `LICENSE`
- `README.md`
- `CHANGELOG.md` or `CHANGELOG`

Classify:

- `✅` all present.
- `⚠️` one or two are missing.
- `❌` README is missing, or a public/open-source release has no license.

### Step 6: Release Readiness

Check whether version and release notes appear updated.

Look for:

- Version fields in `package.json`, `pyproject.toml`, `Cargo.toml`, app manifests, or visible app metadata.
- Git tags when available.
- Release notes in `CHANGELOG`, GitHub release notes, `RELEASE.md`, or docs.
- Obvious stale placeholders: `0.0.0`, `0.1.0` forever, `TODO`, `TBD`, `未更新`, `待补充`.

Classify:

- `✅` version and release notes are present and plausibly current.
- `⚠️` version exists but release notes/tag are unclear.
- `❌` no version, no release notes, or obvious stale placeholders.

When suggesting a next version, infer conservatively:

- Patch version for fixes/checklist/doc updates.
- Minor version for new user-facing features.
- Major version only for breaking changes explicitly described.

### Step 7: Security Suggestions

Review practical operational safety. This is often advisory because code alone may not prove the setting.

Check or ask whether:

- API usage has quota/rate limits.
- Browser keys are restricted by domain/origin.
- Server keys are restricted by IP or service account permissions where possible.
- Logs avoid secrets and personal data.
- Keys can be revoked quickly.
- Production and test keys are separated.
- Error pages do not expose stack traces or internal paths.

Classify:

- `✅` controls are documented or visible.
- `⚠️` controls are unknown or not documented.
- `❌` code/config visibly exposes dangerous defaults.

## Scoring

Start from 100 and subtract:

- `❌ Secrets`: -35
- `❌ Privacy`: -25
- `❌ Git Ignore`: -12
- `❌ Demo Data`: -15
- `❌ License`: -8
- `❌ Version`: -10
- `❌ Security Suggestions`: -10
- Each `⚠️`: -3 to -7 depending on severity

Cap the score:

- If Secrets is `❌`, maximum score is 60.
- If Privacy is `❌`, maximum score is 70.
- If both Secrets and Privacy are clean but Version is `❌`, maximum score is 90.

Release judgment:

- `90-100`: 可以发布
- `75-89`: 建议修复警告后发布
- `60-74`: 暂不建议发布
- `<60`: 不可以发布

## Final Output Format

Always use this compact format. Keep details under `建议` short and action-oriented.

```text
========================
Release Guardian
========================

检查路径：
[path]

Secrets
[✅/⚠️/❌]

Privacy
[✅/⚠️/❌]

Git Ignore
[✅/⚠️/❌]

Demo Data
[✅/⚠️/❌]

License
[✅/⚠️/❌]

Version
[✅/⚠️/❌]

Security
[✅/⚠️/❌]

建议：
- [只列最重要的 1-6 条；没有就写：无]

========================

综合评分
[score]/100

[可以发布 / 建议修复警告后发布 / 暂不建议发布 / 不可以发布]

========================
```

## Evidence Style

When findings exist, use concise evidence lines:

```text
- Secrets ❌：发现 OPENAI_API_KEY in src/config.ts，建议移入 .env 并轮换 Key。
- Privacy ⚠️：发现本机路径 /Users/Hazel/...，建议改为相对路径或示例路径。
- Git Ignore ⚠️：缺少 .env、*.sqlite3。
```

Do not include raw secret values. Mask sensitive fragments like `sk-proj-...abcd`.
