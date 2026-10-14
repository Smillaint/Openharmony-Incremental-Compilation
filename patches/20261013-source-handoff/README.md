# 源码版本与 PR 准备包

完整说明见 [源码与 PR 交接](../../docs/oct13-source-pr-handoff.md)，各仓精确版本见 [versions.json](versions.json)。

- source.bundle：精确恢复快照与准备分支，保留完整验证环境；需对应上游基线对象。
- cumulative-repairs.patch：相对各仓 base_head 的累计修复，排除锁文件与构建适配差异。
- excluded-worktree.patch：保留但不进入修复 PR 的差异。
- 按问题命名的 patch：12 组单提交 format-patch，仅覆盖本轮新增；全部带 Signed-off-by: Smillick <3185479846@qq.com>。

累计补丁与新增补丁采用不同基线，不可重复叠加。准备分支包含迁移快照祖先，不直接作为上游 PR 分支推送。17 仓 bundle 已逐仓校验通过；独立 PR 分支仍需在目标基线执行门禁。
