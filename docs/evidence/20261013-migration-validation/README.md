# 纯迁移构建与首轮增量证据

两轮均在远程 10 月 12 日源码执行，命令为 `bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain`。新增规范性修复未应用。完整说明见 [交接文档](../../oct13-migration-only-validation.md)。

| 文件 | 内容 |
| --- | --- |
| [validation/summary.json](validation/summary.json) | 清理后完整编译：退出码 0、7,968.07 秒、125,605 个主 Ninja 任务 |
| [validation/console.log.gz](validation/console.log.gz) | 完整构建原始控制台 |
| [validation/source-verification.json](validation/source-verification.json) | 58 个相关源码文件与保存版本的哈希核对 |
| [validation/args.gn.gz](validation/args.gn.gz) | 完整编译实际 GN 参数 |
| [incremental/summary.json](incremental/summary.json) | 单轮无改动增量：退出码 0、169.92 秒、153 步及逐 Action 计数 |
| [incremental/console.log.gz](incremental/console.log.gz) | 增量原始控制台 |
| [incremental/build.log.gz](incremental/build.log.gz) | 包含 Ninja explain 的增量构建日志 |
| [incremental/root-explanations.txt](incremental/root-explanations.txt) | 首轮依赖触发根因摘录 |
| [incremental/artifacts-before.json](incremental/artifacts-before.json)、[after](incremental/artifacts-after.json) | 部分构建元数据和 JS snapshot 的哈希、大小与 mtime |
| [incremental/next-dry-run-summary.json](incremental/next-dry-run-summary.json) | 后续 dry-run 的命令、退出码与四条目录时间戳根因；不属于第二轮实际增量 |
| [incremental/next-dry-run.log.gz](incremental/next-dry-run.log.gz) | dry-run 完整输出 |

全部原始日志（含较大的完整 build/Ninja 日志）保存于本地 `D:/workspace/archives/20261012-migration/migration-validation-results.tar.gz` 和远程 `/srv/workspace/patch_backups/20261012_migration_clean/migration-only/`。仓内只保存必要证据。
