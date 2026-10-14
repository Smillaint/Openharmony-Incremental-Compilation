# 10 月 13 日纯迁移验收与首轮增量结果

> 最新逐仓源码、DCO 补丁、恢复版本与 PR 更新判断见 [2026-10-13 源码交接](oct13-source-pr-handoff.md)。本文保留对应阶段记录；最终空 out 全量及连续两轮增量已经通过，不能将历史“尚未编译”状态当作当前结论。

> 本文记录纯迁移基线。后续远程工作树已应用 [历史复核与 clean 恢复修复](oct13-phone-audit-clean-recovery.md)，该阶段仅完成静态和模拟检查，尚未编译；下列结果不能归到后续代码。

## 验收结论

远程 10 月 12 日新源码的纯迁移版本完成清理后整仓编译，随后一轮无改动增量也成功，退出码均为 0。两轮均使用交接文档原指令，没有加入新增规范性修复。未出现需要额外修改源码才能通过的编译兼容错误。

| 轮次 | 退出码 | 完整耗时 | GN | Ninja | 主 Ninja 实际任务 |
| --- | --- | --- | --- | --- | --- |
| 清理后完整编译 | 0 | 7,968.07 秒（约 2 小时 12 分 48 秒） | 24.43 秒 | 7,833.22 秒 | 125,605 |
| 首轮无改动增量 | 0 | 169.92 秒（约 2 分 50 秒） | 29.78 秒 | 69.34 秒 | 153 |

增量的 153 步为 51 个 Action、96 个 stamp、5 个共享库链接和 1 个 COPY，没有主 Ninja CC/CXX 任务。原始十项中九项未执行，`phone_install_modules` 执行一次；`gen_snapshot`、`ark_jsf` 各一次，`airscan_action` 为零；两个 ramdisk Action 各一次，此外还有其他镜像任务。不能据此宣称十项全部收敛。

这是清理后的第一次增量，没有第二轮实际增量的稳定性证据。后续只执行了一次 `ninja -n -dexplain` 分析，不计作编译或性能测试。它仍报告 `arkui-plugins` 和 `koala-wrapper` 相关目录时间戳触发；不能把首轮 153 步认定为以后每轮固定任务数，也不能直接与旧仓已经稳定的 13 步比较收益。

完整统计、原始控制台和依赖解释见 [验证证据](evidence/20261013-migration-validation/README.md)。主 Ninja 计数已验证连续序号，并排除内嵌工具的进度输出。构建器自身报告的 `Cost Time` 为 2:12:40 和 0:02:41，与外层完整命令耗时采用不同口径。

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

远程完整构建在 2026-10-13 12:00:51 +0800 启动清理与验证，14:13:52 +0800 结束。增量在 14:14:03 +0800 启动，14:16:53 +0800 结束。两轮均已结束。

- 当前状态：`migration-only/validation/status.json`。
- 原始控制台：`migration-only/validation/console.log`。
- 启动脚本输出：`migration-only/runner.log`。
- 增量状态：`migration-only/incremental/status.json`。
- 增量控制台与统计：`migration-only/incremental/console.log`、`migration-only/incremental/summary.json`。

增量启动前已确认完整编译退出码为 0，58 个相关文件的 SHA-256 与保存版本一致，且不存在正在运行的 Ninja。增量前没有清理产物或修改源码；前后元数据哈希、mtime、实际任务列表及原始十项 Action 计数均已保存。

上述路径相对远程备份目录 `/srv/workspace/patch_backups/20261012_migration_clean/`。完整编译为清理后的重建，不能当作增量耗时；169.92 秒来自其后单独执行的无改动增量。

## 增量触发与下一阶段

首轮实际日志中的触发根因以目录 mtime 为主：SDK API 声明、JS runtime、HDC 哈希生成、五个 3D shader 生成目录、SELinux 检查、ETS/JS loader 目录。元数据聚合还有两个文件时间戳触发。完整列表见 [root-explanations.txt](evidence/20261013-migration-validation/incremental/root-explanations.txt)。

首轮结束后立即执行的 dry-run 只剩四条本类根因，均围绕 `arkui-plugins` 和 `koala-wrapper` 的生成目录以及 SDK 复制目录。这说明不能将首轮所有目录触发都称为持续问题。dry-run 不运行 Action，也无法替代下一次实际构建的 `restat` 结果。

本阶段没有编译失败需要修补，先保留已通过的纯迁移版本。后续规范性处理应优先核对上述插件生成链的文件级 outputs 和消费者，再单独恢复并复核已归档的 IDL clean 依赖、JSON 生命周期及 JS 生成目录修复。每项保持独立版本，修改后清理对应产物并验证恢复，随后验证无改动增量。

本轮没有执行设备端服务或完整单元测试套件；成功结论限于两个 `make_all` 命令。迁移版 JS 脚本仍保留旧有后台 `wait` 行为，因此整仓退出码不能作为所有内嵌 JS 单测均通过的证据；先前的退出码传播及测试环境补丁仍保存在待修复组。

完整原始日志归档位于本地 `D:/workspace/archives/20261012-migration/migration-validation-results.tar.gz`，SHA-256 为 `f6227fbc12aff7183fdfc6a5aeba252ffd1554d354a4918d0af48219b39c0ca9`，与远程一致。
