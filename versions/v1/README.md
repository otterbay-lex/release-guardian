# Release Guardian V1

这是 2026-07-15 前本机已安装的 Release Guardian 原样快照，也是可以独立发布的经典基础版。

## 版本保护

- `SKILL.md` 不得原地修改或被 V2 覆盖。
- V1 的说明性更新只能写入本 README。
- V2 位于 `../v2/`，两个版本可以分别安装和发布。

## 完整性校验

在本目录运行：

```bash
shasum -a 256 -c SHA256
```

预期输出：`SKILL.md: OK`。

## 适用场景

V1 提供快速、紧凑的发布前检查，覆盖 Secrets、Privacy、Git Ignore、Demo Data、License、Version 和 Security。需要更全面的工程质量、供应链、中国合规、知识产权和运维检查时，可另行选择 V2。
