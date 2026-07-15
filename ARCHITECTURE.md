# ARCHITECTURE.md

## Architecture Goal

Release Guardian 采用“轻量入口、按需规则、可选脚本、证据汇总”的结构。单个 AI 必须能够完成完整检查，多 Agent 仅作为可选增强。

## Recommended Structure

```text
release-guardian/
├── SKILL.md
├── references/
│   ├── engineering.md
│   ├── release-readiness.md
│   ├── security-supply-chain.md
│   ├── privacy-china.md
│   ├── open-source-ip.md
│   ├── operations.md
│   ├── project-profiles.md
│   └── reporting.md
├── scripts/
│   └── release_scan.py
├── evals/
│   └── evals.json
└── docs/
    └── superpowers/specs/
```

## Responsibilities

### SKILL.md

负责触发条件、检查对象确认、快速/深度模式选择、规则路由、Agent 权限边界和报告汇总。不要堆放所有详细规则。

### references/

每个文件负责一个独立风险域。规则应解释检查目标、证据来源、严重程度、误报控制、修复建议和人工确认条件。

### scripts/

提供可重复、确定性的本地扫描。基础能力不依赖第三方包；脚本失败时必须能退回 AI 与常用命令检查。

### evals/

保存真实使用场景和客观评价标准，覆盖工程失败、真实风险、假阳性、项目类型组合及制品不一致。

## Data Flow

```text
发布目标确认
  → 项目类型识别
  → 快速体检或深度检查
  → 通用规则与专项规则组合
  → 命令、文件和制品证据
  → 可信度与阻断判断
  → 双层报告
  → 用户确认修复批次
  → AI 修复并重新验证
  → 独立的发布授权
```

## Separation Rules

- 项目识别不得与具体风险规则混杂。
- 扫描结果、风险解释和发布结论分层处理。
- 分数不能覆盖硬阻断规则。
- “未发现”“已验证”和“无法确认”必须是不同状态。
- 法律风险提示与正式法律结论必须明确区分。
- 检查动作与真正发布动作必须分离。

## Future Extensions

结构化报告、CI 集成、更多司法辖区、外部漏洞数据库和多 Agent 编排均属于后续能力，不应阻塞第一版通用检查。

