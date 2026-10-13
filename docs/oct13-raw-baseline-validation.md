# 10 月 13 日 raw 原始仓对照构建

## 当前状态

2026-10-13 09:15:06 UTC（远程显示 17:15:06 +0800）启动 raw 的清理后完整构建。成功后自动执行一次无改动增量，两轮使用相同命令。任一轮失败即停止；完整构建失败后的续编不能计作增量结果。

本记录创建时第一轮已完成 GN 并进入 Ninja，仍在运行，尚无本轮增量耗时或优化收益结论。构建器默认启用的 ccache 保留，清理 `out` 不代表清空编译缓存。

[准备记录](evidence/20261013-raw-validation/prepared.json)、[525 项目版本](evidence/20261013-raw-validation/heads.json)、[Git 快照](evidence/20261013-raw-validation/snapshots.json)、[启动时状态快照](evidence/20261013-raw-validation/launch-status.json) 与[执行脚本](evidence/20261013-raw-validation/raw_two_rounds.py) 已归档。启动快照不代表构建最终结果；实时状态以远程 `status.json` 为准。

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
