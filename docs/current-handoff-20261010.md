# OpenHarmony 接续说明（2026-10-10）

## 当前结论

原始十项 packages Action 的重复执行已经在组合工作树中收敛。9 月 6 日源码完成修复迁移及扩展优化；10 月 10 日重新连接构建机，在不修改源码的情况下执行一轮 `rk3568 / make_all`，退出码为 0。

| 口径 | 9 月 15 日最终两轮 | 10 月 10 日本轮 |
| --- | --- | --- |
| 完整命令耗时 | 87.44 秒、88.40 秒 | 202.21 秒 |
| GN | 21.79 秒、22.66 秒 | 30.48 秒 |
| Ninja | 25.99 秒、25.82 秒 | 57.94 秒 |
| 主 Ninja 实际任务 | 每轮 13 步 | 13 步 |
| 原始十项、早期三项、两个 ramdisk Action | 均未执行 | 均未执行 |

本轮构建工具自己的 `Cost Time` 为 3 分 12 秒，与外层记录的完整耗时 3 分 22 秒是不同统计口径。给出阶段耗时时必须注明 GN、Ninja 或完整流程。任务数量一致不代表运行时间固定；当前没有证据将时间波动归因于某一种机器或缓存因素。

剩余 13 步为 7 个 Action、6 个 stamp：内核检查、内核模块构建、rockchip_products 元数据和四个 metadata Action。内核模块 Action 内部仍调用 make，不能把主 Ninja 无 CC/CXX 理解为完全没有内部编译活动。

## 优先读取的资料

| 内容 | 入口 |
| --- | --- |
| 最新复测结果 | [summary.json](evidence/20261010/summary.json) |
| 最新原始控制台 | [console.log.gz](evidence/20261010/console.log.gz) |
| 运行前修复文件校验 | [fix-verification.json](evidence/20261010/fix-verification.json) |
| 运行前仓库状态 | [source-state-before.json](evidence/20261010/source-state-before.json) |
| 9 月迁移、新增修复及验收 | [迁移修复与构建结果](sep06-migration-build-results-20260915.md) |
| 原始十项逐项对应 PR | [十项修复交接](original-ten-actions-completion-20260910.md) |
| 历史 13 个 PR 与补丁 | [PR 集中归档](../pr-archive/20260912/README.md) |
| 新增提交及分支基线 | [fix-commits.json](evidence/20260915-build/fix-commits.json) |

## PR 维护待办

历史归档包含 11 个与原始十项相关的 PR，另有 jsframework、airscan 两个早期 PR。10 月 9 日对公开接口的查询返回均为 open，不能据此断言网页上不存在状态差异；继续操作前应重新核对当前页面、评论和提交。

- build #7048、#7049 的 9 月 28 日机器人评论提示长期未响应、可能自动关闭，优先确认反馈及门禁状态。
- airscan #22 当时接口返回不可直接合并，需核对当前基线和冲突，并纳入后来验证过的 staging/补丁方向修复。
- 多数历史 PR 有门禁通过和请求分配评审的记录，需要推进评审。
- 9 月 15 日新增修复保存了独立提交与补丁，但没有在该轮创建新的 GitCode PR；组合树通过不等于所有修复都已进入历史 PR。
- SDK 调用方等部分已准备分支尚未确认 PR 编号，见十项交接的正式提交覆盖表。不要编造编号或将未发布修改写成已合入。

下一步适合先核对实际 PR diff 与已验证补丁的差异，再处理基线、门禁和评审。若继续分析耗时，应在相同配置下分别记录完整流程及各阶段数据，不清理构建输出后将重建当作无改动增量。

## 本地位置

| 路径（相对 D:/workspace） | 内容 |
| --- | --- |
| `Openharmony-Incremental-Compilation/` | 主资料仓、交接文档、小体积证据及补丁 |
| `repositories/` | 本地源码仓和关联 worktree，路径保持不变 |
| `repositories/pr-publishing/` | 发布清单、脚本和已准备分支 |
| `archives/logs/20261010-incremental-recheck/` | 最新完整原始日志、统计、源码状态及 ZIP |
| `archives/logs/20260915-migration-build/` | 9 月最终两轮完整日志 ZIP |
| `archives/bundles/20260915-migration-build/` | 17 个已校验的增量恢复 bundle |
| `archives/bundles/20260915-sa-binary-review/` | SA 补充修复恢复包 |
| `archives/20261010-local-organization/` | 本次整理前 Git bundle、README 副本及移动清单 |
| `archives/fixtures/package-validation-20261010/` | 从主资料仓移出的空验证目录结构 |
| `reports/生产实习报告/` | Word 报告、正文、生成脚本和 QA 图片 |

本次整理前，主资料仓版本为 `9d69aa1`，根仓与主资料仓均建立 `backup/local-organization-20261010` 引用。主资料仓完整历史 bundle 已验证可恢复。本轮未推送 GitHub 或修改 GitCode PR。

根仓原有两份报告删除状态及实习报告文件的未跟踪状态保留；整理提交仅新增报告导航，没有纳入这些既有变化。私钥与凭据继续使用已有忽略和权限设置，未读取内容或纳入归档。

## 远程现场

- 当前源码：`/srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code`。
- 最新日志：`/srv/workspace/action_incremental_logs_20261010/recheck_20261010T071908Z/`。
- 迁移与修复备份：`/srv/workspace/patch_backups/20260915_migration_build/`。
- SSH 连接方式见仓库现有 [SSH 说明](../SSH远程.md)，旧材料中的源码路径应替换为上述新仓路径。

已执行的构建命令：

```bash
cd /srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```

再次启动前确认同一输出目录没有其他构建进程。当前已记录轮次均已结束，无需恢复后台构建。
