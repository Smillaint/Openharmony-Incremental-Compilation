# 10 月 13 日 raw 原始仓对照构建

## 当前状态

raw 的清理后完整构建及随后一次增量均成功，退出码均为 0，两个构建进程已结束。两轮使用相同命令，增量前没有再次清理或手动改动受控文件。

| 轮次 | 完整墙钟耗时 | GN | Ninja | 主 Ninja 任务 |
| --- | --- | --- | --- | --- |
| 清理后完整构建 | 9,275.94 秒（2 小时 34 分 36 秒） | 19.34 秒 | 9,112.73 秒 | 125,589 |
| 随后首轮增量 | 666.77 秒（11 分 7 秒） | 30.77 秒 | 566.40 秒 | 5,718 |

完整构建在 2026-10-13 02:15:06—04:49:42 PDT 执行，增量在 04:49:43—05:00:49 PDT 执行。外层完整墙钟耗时与构建器自身的 `Cost Time` 口径不同，后者分别为 2:34:27、0:10:57。构建器默认启用的 ccache 保留，清理 `out` 不代表清空编译缓存。

[结果统计](evidence/20261013-raw-validation/result-summary.json)、[最终状态](evidence/20261013-raw-validation/final-status.json) 和[完整增量控制台](evidence/20261013-raw-validation/increment1-console.log.gz) 已归档。主 Ninja 序号已验证连续，排除了内嵌工具的进度输出。两轮原始控制台的压缩归档同时保存在本地 `D:/workspace/archives/20261012-migration/raw-validation-results/`，原始内容 SHA-256 已与远程核对。

[准备记录](evidence/20261013-raw-validation/prepared.json)、[525 项目版本](evidence/20261013-raw-validation/heads.json)、[Git 快照](evidence/20261013-raw-validation/snapshots.json)、[启动时状态快照](evidence/20261013-raw-validation/launch-status.json) 与[执行脚本](evidence/20261013-raw-validation/raw_two_rounds.py) 保留供追溯。

## 增量结果与源码自修改

5,718 项任务包括 904 个 ACTION、3,306 个 STAMP、412 个 CXX、5 个 CC、545 个 COPY、524 个 SOLINK、7 个 AR、11 个 LINK 和 4 个 RUST。原始十项 Action 各执行一次，早期的 `ark_jsf`、`gen_snapshot`、`airscan_action` 也各执行一次。

完整构建后的 93 个受控文件与增量启动前一致，证明两轮之间没有改动这些文件。两轮构建自身都改变了 `third_party/sane-airscan/airscan-bmp.c`、`airscan-escl.c`、`http_parser.c`，因此状态记录中的 `managed_source_unchanged` 为 false。

原始 `patch_install.py` 每次调用 `patch` 直接处理源码目录，并捕获补丁失败后继续。实际 diff 显示这三个文件重复插入了检查逻辑，见[两轮后的源码差异](evidence/20261013-raw-validation/airscan-source-after-builds.patch)。这是原始仓构建链的行为，本轮没有为消除该现象而应用修复。666.77 秒是一次没有外部改动的重建结果，不能称为已稳定的空增量，也不能直接当作修复版优化收益。

## 仓库与版本

| 用途 | 远程路径 |
| --- | --- |
| raw 原始对照仓 | `/srv/workspace/openharmony_master_default_20261012175945_huawei_1a6915832/code` |
| 原工作仓 | `/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code` |
| raw 日志与状态 | `/srv/workspace/openharmony_master_default_20261012175945_huawei_1a6915832/raw_validation_20261013` |

两仓 manifest 和 project.list 完全一致，525 个项目的 HEAD 逐项相同。raw 的 93 个受控路径（包含原修复、新规范性修改及公共兼容文件）与保存的初始挂载基线一致，没有应用本轮迁移补丁或新规范性修改。

“原始”指挂载所得源码状态；它本身带有 airscan 已打补丁源码、iptables 兼容 include 和生成文件等工作树差异，不等同于每个仓库都没有 Git 修改。准备阶段未重置这些内容。16 个相关仓保存 `backup/before-raw-comparison-20261013` 快照，项目 HEAD、工作树补丁及受控路径哈希保存在实验目录。

## 清理与执行

已验证 raw 的 `code/out` 为真实目录且没有嵌套挂载，没有正在运行的构建进程。清理前保存并校验 14 份日志和构建状态文件，随后删除整个 raw `out`（约 116 GB），耗时 30.88 秒。删除后 93 个受控路径哈希及文件权限保持不变。

实际每轮命令均为：

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_1a6915832/code
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```

构建已由实验目录中的 `raw_two_rounds.py` 串行启动。第一轮写入 `full/console.log`，第二轮写入 `increment1/console.log`。每轮 `status.json` 记录原指令、PID、开始结束时间、退出码与完整墙钟耗时；每轮结束另存构建器日志，避免被下一轮覆盖。SSH 断开不影响该进程。

下面两条指令仅读取状态与最后 30 行，不会重复启动构建：

```bash
cat /srv/workspace/openharmony_master_default_20261012175945_huawei_1a6915832/raw_validation_20261013/status.json
tail -n 30 /srv/workspace/openharmony_master_default_20261012175945_huawei_1a6915832/raw_validation_20261013/full/console.log
```

## 修复版对比的接续状态

原工作仓在前一阶段已恢复到原始基线的受控路径状态，`out` 不存在。纯迁移修复和新增规范性修复均保存在该仓父目录的 `ab_incremental_20261013` 中，未丢失；本轮 raw 构建没有再切换原工作仓。

raw 完成后，修复版对照应选择 `original`（纯迁移修复），清理后完整构建成功再做无改动增量。`current` 是新增规范性修改版本，不应混入这一对照。此前纯迁移版 169.92 秒属于另一次首轮增量，不能直接作为这次实验的修复版结果。

上一阶段 Taihe RPC 失败与全量清理的日志保存在 `/srv/workspace/patch_backups/20261013_full_out_clean_20261013T081306Z`。新增规范性修改的 Git 快照及恢复包仍在原有归档目录；是否与 Taihe 失败有关，需要依据相同基线的实际构建结果判断。
