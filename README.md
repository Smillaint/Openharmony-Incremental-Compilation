# OpenHarmony Action 增量编译修复记录

本仓库记录 OpenHarmony `rk3568/phone` 增量构建中重复 Action 的根因、代码修改、PR 与验证证据。

## 最新状态与继续工作入口

[2026-10-15 其他历史 PR 更新准备](docs/oct15-other-pr-refresh.md)：IDL #6982、安装 #7046、JS #853、airscan #22 的更新已保存为带 DCO 的提交并通过本地检查；简短正文已确认。**GitCode 推送认证未完成，4 条远端 PR 暂未更新。** 其他旧 PR 已逐项核对，配套仓及继续发布指令见交接。

[2026-10-15 SA #6965 门禁排查](docs/oct15-sa-gate-repeat-failure.md)：第二轮 dayu600 编译、打包、上传成功，但 EcoTest 任务 `2296023` 超时且没有测试报告；mac-sdk 在编译前工作区清理失败。同期独立 PR 也出现 dayu600 超时，具体设备／调度原因仍需平台日志。源码未改，继续重试门禁。

[2026-10-14 全部修复的离线源码](docs/oct14-all-repairs-offline.md)：**本轮 17 个相关仓已独立恢复到 `D:/workspace/repositories/openharmony-repairs-20261014`，68 个修复文件及 8 个保留差异全部可在本地查看、修改。** 组合验证快照、10 仓发布分支和更新后的 SA #6965 分支均已保留，229 个 LFS 资源已下载并校验。目录内 README 列明逐仓作用、文件和版本；完整产品编译仍需原 OpenHarmony 环境。

[2026-10-14 SA 组旧 PR 更新](docs/oct14-sa-profile-group-update.md)：**三个 SA Action 继续使用 [build #6965](https://gitcode.com/openharmony/build/pull/6965)，已追加带 DCO 的 ZIP 时间戳修复，门禁已启动。** 重复 PR #7130 和临时 Issue #4759 已关闭，保留 Issue #4657。后续沿用历史 PR 分组，优先更新旧 PR。

[2026-10-14 GitCode 发布交接](docs/oct14-gitcode-publish.md)：**10 个个人仓已推送 `fix/incremental-build-20261013`，补齐 7 个 fork，15 条新提交全部带 Smillick DCO，远端 SHA 已逐仓核对。** 分支保留实际通过编译的修复文件；现有 master、旧 PR 分支未改动。该批分支发布阶段未新建 PR，随后首条 Action PR 见上方。仓地址、逐仓提交、上游重叠检查、补丁和 bundle 均已归档。

[2026-10-13 源码、PR 与验证交接](docs/oct13-source-pr-handoff.md) 汇总逐仓修改及提交边界：**本轮新增修复覆盖 10 仓、23 文件，准备 12 组带 Smillick DCO 的补丁；17 仓精确 Git 快照和 bundle 已保存。** 明确区分历史十项 PR、本次新增依赖链修复及 8 个不纳入 PR 的保留差异。最终两轮增量原始十项均为 0，后续人工日志也保持 13 步、十项为 0；尚未新建 GitCode PR。

[2026-10-13 规范性修复实际验证](docs/oct13-phone-norm-validation.md) 是当前入口：JS/CSS 依赖、innerkit、安装规则输入及 ROFS 稳定发布已补齐。**移走源码旧 SDK 生成目录并清空 out 后，全量成功，耗时 2,105.50 秒；随后两轮增量为 154.81 / 87.77 秒，原始十项全部不执行，首轮起没有共享库重链或 phone_install_modules 重跑。** 受控源码与 17 仓 Git 树未变化，旧 SDK 源码生成目录未重建；A/B 的 current 已同步为验证通过的修复版，raw 对照仓保持原样。

[2026-10-13 raw 原始仓对照构建](docs/oct13-raw-baseline-validation.md) 保存原始基线：525 个项目 HEAD 和 93 个修复相关路径通过基线核对后，清理产物的完整构建及随后增量均成功。全量耗时 **9,275.94 秒**，增量耗时 **666.77 秒（约 11 分 7 秒）**，主 Ninja 执行 **5,718 项任务**，原始十项 Action 各执行一次。两轮之间没有改动受控文件，但原始 airscan 构建脚本在运行中重复打补丁，改写 3 个源文件，尚无稳定增量结果。**raw 两轮进程均已结束；修复版验证结果见顶部入口。** 原迁移修复和新增规范性修复分别保存在快照中。

[2026-10-13 GN 兼容修复](docs/oct13-gn-sdk-manifest-repair.md) 保存上一阶段的修复：新增 exec_script 被 OpenHarmony 白名单禁止，随后改为受控文件清单，并补齐 package.json 生产者依赖及 Python action 执行权限。其后实际构建进入 Ninja，但出现 JS 同文件复制失败，随后还有 Taihe RPC 导入错误；原日志已归档。后续修复 JS/CSS 依赖后，attempt5 与最终 attempt6 整仓编译均成功，未再复现 Taihe 导入失败。该文档中的免清理重试说明属于历史状态，不适用于当前对照实验。

[2026-10-13 历史复核与 clean 恢复修复](docs/oct13-phone-audit-clean-recovery.md) 记录规范性修改：核对 15 组准备补丁和 11 个正式 PR diff，未发现已知修复漏迁；新增 9 仓、18 文件的 IDL、JSON、JS/CSS、插件与 wrapper 修改。该版本已保存，当前未应用于 raw 原始仓对照构建。

[2026-10-13 纯迁移验收](docs/oct13-migration-only-validation.md) 记录修改前基线：清理后完整编译及首轮增量均成功，增量完整耗时 **169.92 秒**（GN 29.78 秒、Ninja 69.34 秒），执行 **153 步**；原始十项中九项未执行，`phone_install_modules` 执行一次。这些数据不代表新增规范性修改的效果。

[2026-10-12 clean 恢复探索记录](docs/oct12-migration-clean-recovery.md) 保存分离前的补丁和局部测试证据，不代表当前纯迁移版本已完成整仓验收。

[2026-10-10 接续说明](docs/current-handoff-20261010.md) 保留上一源码版本的 PR 待办、日志及恢复位置。该轮复测成功：**完整耗时 202.21 秒，GN 30.48 秒，Ninja 57.94 秒**；主 Ninja 为 13 步，原始十项、早期三项和两个 ramdisk Action 均未执行。这些是旧仓历史结果，不能作为 10 月 12 日新仓的耗时。

## 9 月 6 日源码复核更新

[2026-09-15 迁移修复与远程构建结果](docs/sep06-migration-build-results-20260915.md)：已补齐 packing_tool、jsframework、airscan 的迁移缺口，并修复 ramdisk 输出、摄像头生成配置、默认 SELinux 输出条件和内核模块重复发布。**9 月 6 日新仓连续两轮完整构建成功，分别耗时 87.44 秒、88.40 秒，主 Ninja 均执行 13 步；原始十项、早期三项和两个 ramdisk Action 均未执行。**剩余为内核检查、模块构建及少量 metadata 任务。补丁、提交与逐轮证据见新交接。

[前序迁移复核与 SA 补充修复](docs/sep06-migration-review-20260915.md) 保留修复前状态和非空 SA ZIP 的七项隔离回归。9 月 9 日归档目录中的双轮日志属于 8 月 16 日源码，与本轮新仓结果分别保存。

## PR 归档与本地目录

[PR 集中归档（2026-09-12）](pr-archive/20260912/README.md) 保存 13 个 GitCode PR 补丁、11 个已准备分支、验证快照和必要日志。源码仓与历史文件的新位置见 [工作区整理说明](docs/workspace-organization-20260912.md)。

## 当前阶段：原始 10 项初步修复完成

最初跟踪的 `//build/ohos/packages` 下 **10 个 Action 增量问题已经初步完成修复**。前 9 项先后收敛，最后的 `phone_install_modules` 在 2026-09-01 组合工作树连续两轮构建中均未执行。

完整说明见 **[原始 10 项修复交接（2026-09-10）](docs/original-ten-actions-completion-20260910.md)**，包含每个 Action 的 PR、修改文件、代码作用、两轮验证来源和未完成的正式提交链。

| 原始 Action | 主要 PR | 修改与作用 |
| --- | --- | --- |
| `sa_profile_src_phone` | [build #6965](https://gitcode.com/openharmony/build/pull/6965) | SA 输入按 label 排序，源 SA JSON 内容相同不重写；配合 parts 稳定化收敛 |
| `sa_profile_binary_phone` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | ZIP 临时生成后比较发布，已测配置下避免重复归档传播 |
| `phone_sa_profile_install_info` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | SA 合并安装 JSON 内容感知写入，截断下游 dirty |
| `check_seccomp_filter_name` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 稳定校验输入，生成成功 result，补齐 cfg/seccomp depfile，校验异常清理旧结果 |
| `process_field_validate` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 补齐 cfg/白名单依赖、成功输出与校验异常处理 |
| `collect_notice_files__phone` | [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009)、[#7048](https://gitcode.com/openharmony/build/merge_requests/7048) | NOTICE 收集与发布拆成两阶段；补充 LICENSE 边界查找与生成物依赖修正 |
| `generate_host_symlink` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | host 元数据规范化，collector 发布稳定中间 JSON，原 Action 消费中间结果 |
| `phone_hisysevent_install_info` | [build #7006](https://gitcode.com/openharmony/build/merge_requests/7006) | 配置和安装 JSON 内容感知写入，实际 YAML 加入 depfile |
| `phone_install_modules` | [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046)、[iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) 及配套修复 | 修正 SA depfile 过滤、稳定安装元数据，沿 SDK/IDL/签名/iptables 等真实输入链消除无效重建 |
| `phone_parts_list` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999)、[#7009](https://gitcode.com/openharmony/build/merge_requests/7009) | 稳定聚合和部件安装 JSON，避免仅 mtime 变化带动 packages 下游 |

上述结果来自组合工作树和分阶段验证。#7046、#7048 等最新独立分支尚未单独整仓复验，SDK split 等调用方仍有待确认的 PR；不能将组合验证效果全部归因于某一个 PR。

旧仓最终两轮主 Ninja 均执行 9 步：3 个 metadata stamp、4 个 metadata Action 和 2 个 ramdisk image Action。它们不属于原始十项。39→9 是旧组合工作树前后对比，不是单个 PR 的收益；新仓结果以顶部更新为准，不跨源码版本直接比较任务数。

## PR 交付与交接入口

2026-09-10 核对的 13 个已知 PR 均为 open；12 个可直接合并，airscan #22 不可直接合并。可合并状态不代表门禁或评审通过。修复效果与社区合入进度分别跟踪。

| 文档 | 用途 |
| --- | --- |
| [原始 10 项修复交接](docs/original-ten-actions-completion-20260910.md) | 当前统一入口：逐 Action 的 PR、代码与作用、完成边界、交付缺口 |
| [GitCode diff 证据索引](docs/evidence/20260910/README.md) | 本次公开 API 核对的 PR 状态、HEAD、文件清单及完整返回 diff |
| [PR 时间线与历史结果](docs/current-open-pr-timeline-and-action-results-20260909.md) | 9 月 9 日 PR 时间线快照，保留历史状态 |
| [iptables 与最终两轮验证](docs/glm52-geninit-fix-handoff-20260901.md) | 最后一项 `phone_install_modules` 收敛的日志、耗时和输出快照 |
| [SDK split 阶段交接](docs/glm52-phone-install-final-handoff-20260828.md) | 上游 SDK/声明生成链的历史排查与验证 |
| [全流程修复记录](docs/incremental-build-repair-process-20260825.md) | 前期根因与迭代过程 |
| [GN/Ninja/restat 方法](docs/current-project-handoff.md) | 历史方法参考；其中旧任务状态以当前交接为准 |
| [SSH 操作说明](SSH远程.md) | 远程连接与日志读取方法；实际源码路径以较新交接为准 |

后续工作优先整理本轮新增补丁的配套 PR、跟进评审及门禁、核对组合补丁与独立分支的一致性。内核检查与 metadata 的剩余执行边界见最新交接。

## 早期三个独立 Action

早期材料中的 `ark_jsf`、`gen_snapshot`、`airscan_action` 不计入上表的 packages 十项，保留其历史成果：

| Action | PR | 材料 |
| --- | --- | --- |
| `ark_jsf`、`gen_snapshot` | [third_party_jsframework #853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853) | [ark_jsf](action相关增量编译/ark_jsf.md)、[gen_snapshot](action相关增量编译/gen_snapshot.md) |
| `airscan_action` | [third_party_sane-airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22) | [airscan_action](action相关增量编译/airscan_action.md) |

当时三项零改动验证中均未执行，详见 [历史修复日志](action相关增量编译/远程日志/修复日志.md)。旧日志中的 `all_ACTION=0` 只适用于当时快照，不能作为当前整仓所有 Action 为 0 的结论。

## 维护方式

- 文本统一使用 UTF-8；修改前保存 Git 版本，保留已有工作树修改。
- 每项修复记录直接根因、变更文件、PR、验证日志及适用配置，区分组合效果和单 PR 效果。
- 完整编译按已确认的源码路径和产品配置串行执行；真实连续两轮日志用于验收，dry-run 用于定位依赖。
- 正式提交保留 DCO；私钥、凭据及临时构建产物不纳入版本。
