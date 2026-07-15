# Release Guardian v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在永久保留并可独立发布 V1 的前提下，构建工程质量与合规并重、由 AI 主动执行的通用 Release Guardian V2。

**Architecture:** 仓库使用 `versions/v1/` 和 `versions/v2/` 保存两个可独立安装和发布的版本。V2 的主 `SKILL.md` 只负责编排，详细规则按需放入 `references/`，确定性扫描放入无第三方依赖的 `scripts/release_scan.py`，行为通过场景样本和脚本单元测试验证。

**Tech Stack:** Markdown Skill、Python 3 标准库、`unittest`、Git、常用只读命令（`rg`、`find`、`git`）。

---

## 文件结构与职责

```text
release-guardian/
├── versions/
│   ├── v1/
│   │   ├── SKILL.md                 # 原版只读快照
│   │   ├── SHA256                   # 原版完整性校验
│   │   └── README.md                # V1 使用和历史说明
│   └── v2/
│       ├── SKILL.md                 # V2 入口、路由、权限与流程
│       ├── README.md                # V2 安装、能力和边界
│       ├── references/
│       │   ├── engineering.md
│       │   ├── release-readiness.md
│       │   ├── security-supply-chain.md
│       │   ├── privacy-china.md
│       │   ├── open-source-ip.md
│       │   ├── operations.md
│       │   ├── project-profiles.md
│       │   └── reporting.md
│       └── scripts/
│           └── release_scan.py
├── tests/
│   ├── test_release_scan.py
│   └── fixtures/                    # 最小化场景样本
├── evals/evals.json                 # Agent 行为测试提示和断言
├── README.md
└── CHANGELOG.md
```

`versions/v1/SKILL.md` 在首次复制并校验后不得编辑。V1 的任何文档改进只能放在相邻 README，不得改变快照哈希。

### Task 1: 固化并保护 V1

**Files:**
- Create: `versions/v1/SKILL.md`
- Create: `versions/v1/SHA256`
- Create: `versions/v1/README.md`
- Modify: `TASKS.md`

- [ ] **Step 1: 复制原版快照**

Run:

```bash
mkdir -p versions/v1
cp /Users/hazel1996/.codex/skills/release-guardian/SKILL.md versions/v1/SKILL.md
```

Expected: `versions/v1/SKILL.md` 存在且内容完整。

- [ ] **Step 2: 写入固定校验值**

Create `versions/v1/SHA256` with exactly:

```text
da54b2a07b0122e01a1ceb47cc1a4050e89ea7543d1e29c1c3f5ef7d1a2aa223  SKILL.md
```

- [ ] **Step 3: 验证快照未改变**

Run:

```bash
(cd versions/v1 && shasum -a 256 -c SHA256)
```

Expected: `SKILL.md: OK`。

- [ ] **Step 4: 编写 V1 说明**

`versions/v1/README.md` 必须说明：这是 2026-07-15 前已安装版本的原样快照；可独立发布；禁止原地升级；校验命令；V2 位于 `../v2/`。

- [ ] **Step 5: 提交 V1 基线**

```bash
git add versions/v1 TASKS.md
git commit -m "chore: preserve release guardian v1"
```

### Task 2: 建立扫描器测试骨架

**Files:**
- Create: `tests/test_release_scan.py`
- Create: `tests/fixtures/placeholder/.env.example`
- Create: `tests/fixtures/exposed-secret/config.js`
- Create: `tests/fixtures/local-path/README.md`

- [ ] **Step 1: 写入失败测试**

`tests/test_release_scan.py` 定义三个测试：占位 Key 不阻断、真实形态 Key 被遮罩且阻断、本机绝对路径被报告。使用 `tempfile`、`unittest` 和 `importlib.util` 加载 `versions/v2/scripts/release_scan.py`。

核心断言：

```python
self.assertEqual(result["summary"]["blockers"], 0)
self.assertNotIn("sk-proj-1234567890abcdefghijklmnop", json.dumps(result))
self.assertEqual(result["findings"][0]["rule_id"], "RG-SEC-001")
self.assertEqual(result["findings"][0]["severity"], "blocker")
self.assertEqual(result["findings"][0]["rule_id"], "RG-PRIV-002")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python3 -m unittest tests/test_release_scan.py -v`

Expected: FAIL，原因是 `versions/v2/scripts/release_scan.py` 尚不存在。

- [ ] **Step 3: 提交测试骨架**

```bash
git add tests
git commit -m "test: define scanner safety cases"
```

### Task 3: 实现最小确定性扫描器

**Files:**
- Create: `versions/v2/scripts/release_scan.py`
- Test: `tests/test_release_scan.py`

- [ ] **Step 1: 定义稳定输出结构**

扫描函数签名固定为：

```python
def scan(root: Path) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scan_root": str(root.resolve()),
        "findings": [],
        "summary": {"blockers": 0, "warnings": 0, "notes": 0},
        "limitations": [],
    }
```

每项 finding 必须含 `rule_id`、`severity`、`category`、`path`、`line`、`message`、`masked_hint` 和 `confidence`。不得保存完整疑似密钥。

- [ ] **Step 2: 实现三条最小规则**

- `RG-SEC-001`：真实形态密钥；占位词 `example`、`your_`、`placeholder`、`xxxx` 不阻断。
- `RG-PRIV-002`：`/Users/<name>/` 与 `C:\\Users\\<name>\\` 本机路径。
- 默认排除 `.git`、`node_modules`、`dist`、`build`、`coverage`、虚拟环境和二进制文件。

- [ ] **Step 3: 运行测试确认通过**

Run: `python3 -m unittest tests/test_release_scan.py -v`

Expected: 3 tests PASS，输出中不含完整测试密钥。

- [ ] **Step 4: 提交扫描器**

```bash
git add versions/v2/scripts/release_scan.py
git commit -m "feat: add deterministic release scanner"
```

### Task 4: 编写 V2 主编排 Skill

**Files:**
- Create: `versions/v2/SKILL.md`
- Create: `versions/v2/README.md`

- [ ] **Step 1: 编写触发描述**

Frontmatter 的 `name` 使用 `release-guardian-v2`，description 明确覆盖“发布、上线、发 GitHub、deploy、release、公开分享、应用商店、软件包、Skill 发布”，并说明工程质量、安全、合规和知识产权并重。

- [ ] **Step 2: 编写 Agent 主动流程**

主流程固定为：确认检查根目录与实际制品 → 自动识别类型 → 选择快速或深度模式 → 读取适用 references → 执行安全的只读检查 → 汇总证据 → 应用硬阻断 → 输出双层报告 → 提议修复批次 → 用户确认后修复 → 重新验证 → 单独询问是否发布。

- [ ] **Step 3: 写明权限边界**

允许直接执行项目内只读检查和已有验证命令；安装依赖、删除、联网付费、外部平台修改、推送、部署和发布必须确认；任何秘密只显示变量名、路径和遮罩提示。

- [ ] **Step 4: 检查主文件长度和路由**

Run: `wc -l versions/v2/SKILL.md`

Expected: 少于 500 行，且明确指向八个 reference 文件。

- [ ] **Step 5: 提交主 Skill**

```bash
git add versions/v2/SKILL.md versions/v2/README.md
git commit -m "feat: add release guardian v2 orchestrator"
```

### Task 5: 编写工程与发布规则

**Files:**
- Create: `versions/v2/references/engineering.md`
- Create: `versions/v2/references/release-readiness.md`
- Create: `versions/v2/references/operations.md`

- [ ] **Step 1: 编写工程规则**

覆盖技术栈识别、已有构建/测试/lint/typecheck 命令、锁文件、可移植路径、错误处理、核心流程证据。构建失败或核心流程不可用是阻断项；没有测试是警告而非自动阻断。

- [ ] **Step 2: 编写发布完整性规则**

覆盖 README、安装、配置示例、版本、变更记录、制品清单、源码/制品一致性、升级、迁移和回滚。明确实际制品不一致为阻断项。

- [ ] **Step 3: 编写运维规则**

覆盖健康检查、日志脱敏、监控、限流、费用上限、备份、恢复和事故响应；按离线工具、静态站点和在线服务区分适用性。

- [ ] **Step 4: 规则一致性检查**

Run: `rg -n "已验证|发现问题|需要人工确认|不适用|阻断" versions/v2/references/{engineering,release-readiness,operations}.md`

Expected: 三个模块均使用统一状态和阻断术语。

- [ ] **Step 5: 提交工程规则**

```bash
git add versions/v2/references/engineering.md versions/v2/references/release-readiness.md versions/v2/references/operations.md
git commit -m "feat: add engineering release and operations rules"
```

### Task 6: 编写安全、隐私与知识产权规则

**Files:**
- Create: `versions/v2/references/security-supply-chain.md`
- Create: `versions/v2/references/privacy-china.md`
- Create: `versions/v2/references/open-source-ip.md`

- [ ] **Step 1: 编写安全与供应链规则**

保留 V1 的密钥类型并深化权限、认证、依赖来源、危险安装脚本、已知漏洞、最小权限和密钥撤销。任何示例不得包含可用凭证。

- [ ] **Step 2: 编写中国隐私合规规则**

覆盖个人信息最小化、告知同意、敏感个人信息、日志脱敏、Cookie/SDK、第三方共享、数据出境、未成年人和备案/许可提示。所有法律判断使用初步风险措辞并列出人工确认条件。

- [ ] **Step 3: 编写知识产权规则**

覆盖项目许可证、依赖许可证、复制代码、图片、字体、模型、数据集、署名和再分发条件。不得仅凭许可证名称直接宣布违法。

- [ ] **Step 4: 扫描规则文件自身**

Run: `python3 versions/v2/scripts/release_scan.py versions/v2`

Expected: 不包含完整凭证；示例占位内容不产生阻断项。

- [ ] **Step 5: 提交风险规则**

```bash
git add versions/v2/references/security-supply-chain.md versions/v2/references/privacy-china.md versions/v2/references/open-source-ip.md
git commit -m "feat: add security compliance and IP rules"
```

### Task 7: 编写项目画像与报告规范

**Files:**
- Create: `versions/v2/references/project-profiles.md`
- Create: `versions/v2/references/reporting.md`

- [ ] **Step 1: 定义项目画像**

为 GitHub 仓库、Web、API、App、CLI/软件包、AI 应用、Agent Skill、文档/数据集、ZIP/镜像列出识别证据、额外检查和不适用规则。允许多画像叠加。

- [ ] **Step 2: 定义评分与硬阻断**

固化六维权重 `25/20/20/15/10/10`。结论仅允许“可以发布 / 有条件发布 / 暂不建议发布 / 禁止自动发布”；硬阻断优先于总分。

- [ ] **Step 3: 定义双层报告字段**

每项发现包含：`rule_id`、状态、严重程度、证据、可信度、后果、修复、AI 可执行范围、用户动作、复核方式。报告末尾列出扫描范围、排除项、命令、失败检查和免责声明。

- [ ] **Step 4: 提交画像与报告规范**

```bash
git add versions/v2/references/project-profiles.md versions/v2/references/reporting.md
git commit -m "feat: add project profiles and reporting rules"
```

### Task 8: 建立 Agent 行为评测

**Files:**
- Create: `evals/evals.json`
- Create: `tests/fixtures/node-incomplete/package.json`
- Create: `tests/fixtures/ai-chat/README.md`
- Create: `tests/fixtures/skill-risk/SKILL.md`
- Create: `tests/fixtures/artifact-mismatch/source/README.md`
- Create: `tests/fixtures/artifact-mismatch/release/.env`

- [ ] **Step 1: 写入六个真实提示**

每个 eval 包含 `id`、`prompt`、`expected_output`、`files` 和客观 assertions，分别覆盖静态站点、工程不完整 Node 项目、AI 聊天应用、Skill、假阳性、制品不一致。

- [ ] **Step 2: 固化关键断言**

至少验证：项目画像正确；真实密钥/制品泄露被阻断；占位 Key 不阻断；测试失败被发现；报告包含证据和检查边界；不擅自修改或发布；用小白语言解释。

- [ ] **Step 3: 校验 JSON**

Run: `python3 -m json.tool evals/evals.json >/dev/null`

Expected: exit code 0。

- [ ] **Step 4: 提交评测样本**

```bash
git add evals tests/fixtures
git commit -m "test: add release guardian behavior evals"
```

### Task 9: 运行 V1 与 V2 对比评测

**Files:**
- Create: `docs/evaluation/iteration-1-summary.md`
- Modify: `versions/v2/SKILL.md`（仅在评测发现明确缺口时）
- Modify: relevant `versions/v2/references/*.md`（仅修改对应规则）

- [ ] **Step 1: 保存 V1 校验结果**

Run: `(cd versions/v1 && shasum -a 256 -c SHA256)`

Expected: `SKILL.md: OK`。若失败，停止所有工作，不尝试自动“修复”V1。

- [ ] **Step 2: 使用 skill-creator 运行同批 V1/V2 场景**

V1 指向 `versions/v1/SKILL.md`，V2 指向 `versions/v2/SKILL.md`；每个场景使用相同输入。记录阻断项召回、假阳性、工程覆盖、解释清晰度、修改边界、耗时和 token。

- [ ] **Step 3: 形成对比摘要**

`docs/evaluation/iteration-1-summary.md` 必须逐项列出 V2 相对 V1 的改进、退步、误报和未覆盖项，不允许只给总分。

- [ ] **Step 4: 修正明确问题并复测**

只修改有失败证据的模块；重新运行受影响场景和 `python3 -m unittest discover -s tests -v`。

- [ ] **Step 5: 提交评测结果**

```bash
git add versions/v2 docs/evaluation
git commit -m "test: validate release guardian v2 against v1"
```

### Task 10: 双版本发布准备与自检

**Files:**
- Modify: `README.md`
- Modify: `TASKS.md`
- Create: `CHANGELOG.md`
- Create: `LICENSE`（必须先由用户确认许可证后再创建）

- [ ] **Step 1: 编写双版本入口**

根 README 清晰展示 V1（经典基础版）和 V2（通用 Agent 版）的能力、目录、安装方式、适用场景和独立下载路径，不把 V1 标为废弃。

- [ ] **Step 2: 编写变更记录**

CHANGELOG 分别记录 V1 快照来源和 V2 新增能力；不把 V2 的能力错误归入 V1。

- [ ] **Step 3: 确认许可证**

在创建 LICENSE 前向用户确认 MIT 或其他许可证，并核查项目内第三方材料是否允许相同方式发布。

- [ ] **Step 4: 运行完整验证**

```bash
(cd versions/v1 && shasum -a 256 -c SHA256)
python3 -m unittest discover -s tests -v
python3 versions/v2/scripts/release_scan.py versions/v2
git diff --check
git status --short
```

Expected: V1 `OK`；全部测试 PASS；V2 无真实敏感信息阻断；无空白错误；仅有预期变更。

- [ ] **Step 5: 用 V2 检查整个仓库**

执行快速体检和深度检查，保存检查边界、证据、未完成事项和最终建议。发现阻断项时不得进入 GitHub 发布流程。

- [ ] **Step 6: 提交发布准备**

```bash
git add README.md TASKS.md CHANGELOG.md LICENSE
git commit -m "docs: prepare dual-version release"
```

## 全局验收门槛

- `versions/v1/SKILL.md` 的 SHA-256 始终为 `da54b2a07b0122e01a1ceb47cc1a4050e89ea7543d1e29c1c3f5ef7d1a2aa223`。
- V1 和 V2 均有独立入口、说明和可发布目录。
- V2 保留 V1 七类检查，并补齐六大支柱。
- V2 基础检查不依赖第三方 Python 包或付费服务。
- 所有真实形态秘密在输出中被遮罩。
- 硬阻断不能被高分覆盖。
- AI 主动完成安全的检查，修改和发布遵守授权边界。
- 六个评测场景通过，且 V2 不得在工程覆盖和假阳性控制上弱于 V1。
- 真正创建 GitHub 仓库、推送和 Release 是计划完成后的独立授权任务。
