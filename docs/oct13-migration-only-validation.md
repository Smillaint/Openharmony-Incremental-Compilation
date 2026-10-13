# 10 月 13 日纯迁移验收

## 顺序与基线

先将已验证修复迁移到最新源码，完成整仓编译；迁移验收通过后，再处理源码目录中间产物、删除文件后的 `check_changes`、IDL 输出声明与 clean 后依赖断链问题。两个阶段使用独立版本和日志，不能用新增修复的局部测试替代迁移验收。

本阶段验收顺序为完整编译、同命令的一轮无改动增量。若失败，优先检查旧修复与新主干之间的兼容性，只做必要适配并重新验证。新增规范性修复继续保存在独立补丁中，不能混入这轮基线验收。

- 来源交接：[10 月 10 日接续说明](current-handoff-20261010.md)、[9 月迁移结果](sep06-migration-build-results-20260915.md)。
- 远程旧仓：`/srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code`。
- 远程新仓：`/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code`。
- 迁移、源码修改、清理和编译均在远程进行。本地仅保存脚本、补丁、恢复包和交接材料。

迁移采用旧仓 HEAD、旧仓工作树及新仓初始内容三方比较。保留新上游 SELinux 条件和 SDK depfile；airscan 适配新仓完整八项补丁。纯迁移共涉及 9 个修改仓、49 个文件。

## 分离与恢复

混合阶段的全部跟踪修改先保存为 Git 快照，再恢复纯迁移工作树。真实索引和 HEAD 未切换，原有 package-lock 等无关修改保留。

- 快照分支：`backup/before-migration-separation-20261013`。
- 纯迁移分支：`migration/validated-september-to-october-20261013`。
- 远程目录：`/srv/workspace/patch_backups/20261012_migration_clean/migration-only/`。
- `separation.json`：各仓原 HEAD、混合快照、迁移提交及分离文件哈希。
- 各仓 `combined.bundle`、`migration.bundle`：已逐仓通过 `git bundle verify`。
- 各仓 `pending-repairs.patch`：纯迁移至新增修复的差异，待迁移编译通过后复核应用。
- 本地恢复包：`D:/workspace/archives/20261012-migration/migration-only-backup.tar.gz`，下载前后 SHA-256 一致。
- [迁移版本清单](../patches/20261013-migration-only/versions.json)、[分离与文件哈希](../patches/20261013-migration-only/separation.json)；纯迁移补丁位于 `patches/20261013-migration-only/`，待恢复修复位于 `patches/20261013-pending-repairs/`。

分离范围包括 IDL 模板及脚本、五处 IDL 调用方、loader 的新 JSON 调整、JS 路径和错误传播修复，以及 JS 测试环境与 inputs 补充。迁移工作树中的 JS 脚本与 10 月 10 日已验证版本 SHA-256 相同。

## 编译命令与状态

确认没有正在使用该输出目录的构建后，保存混合阶段 args、构建日志及 Ninja 日志，删除新仓 `out`。随后执行历史原指令：

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```

远程 2026-10-13 12:00:51 +0800 启动，清理已完成，纯迁移编译正在执行。尚无成功退出码，不宣称迁移验收通过或提供增量耗时。

- 当前状态：`migration-only/validation/status.json`。
- 原始控制台：`migration-only/validation/console.log`。
- 启动脚本输出：`migration-only/runner.log`。
- 后续增量状态：`migration-only/incremental/status.json`。
- 后续增量控制台与统计：`migration-only/incremental/console.log`、`migration-only/incremental/summary.json`，执行后生成。

增量脚本已启动等待：只有迁移完整编译退出码为 0、相关源码 SHA-256 与保存版本一致且不存在正在运行的 Ninja，才执行一次原指令。增量前不清理产物、不修改源码；保存前后元数据哈希、mtime、实际任务列表和原始十项 Action 计数。完整编译失败时增量不启动。

上述路径相对远程备份目录 `/srv/workspace/patch_backups/20261012_migration_clean/`。本轮为清理后的重建，不计作无改动增量。原始十项的耗时与执行次数需在完整构建成功后单独复测。
