# OpenHarmony Action 增量编译修复记录

本仓库记录 OpenHarmony `rk3568/phone` 增量构建中重复 Action 的根因、代码修改、PR 与验证证据。

## PR 归档与本地目录

[PR 集中归档（2026-09-12）](pr-archive/20260912/README.md) 保存 13 个 GitCode PR 补丁、11 个已准备分支、验证快照和必要日志。源码仓与历史文件的新位置见 [工作区整理说明](docs/workspace-organization-20260912.md)。

## 当前阶段：原始 10 项初步修复完成

最初跟踪的 `//build/ohos/packages` 下 **10 个 Action 增量问题已经初步完成修复**。前 9 项先后收敛，最后的 `phone_install_modules` 在 2026-09-01 组合工作树连续两轮构建中均未执行。

完整说明见 **[原始 10 项修复交接（2026-09-10）](docs/original-ten-actions-completion-20260910.md)**，包含每个 Action 的 PR、修改文件、代码作用、两轮验证来源和未完成的正式提交链。

| 原始 Action | 主要 PR | 修改与作用 |
| --- | --- | --- |
| `sa_profile_src_phone` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | SA 输入按 label 排序，源 SA JSON 内容相同不重写；配合 parts 稳定化收敛 |
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

最终两轮主 Ninja 均执行 9 步：3 个 metadata stamp、4 个 metadata Action 和 2 个 ramdisk image Action。它们不属于原始十项，列为**后续扩展优化**，不改变原始任务初步完成的状态。39→9 是组合工作树前后对比，不是单个 PR 的收益。

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

后续工作优先补齐配套 PR、跟进评审及门禁、核对组合补丁与独立分支的一致性。metadata/ramdisk 优化另行跟踪。

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
- 完整编译沿用人工执行流程；真实连续两轮日志用于验收，dry-run 用于定位依赖。
- 正式提交保留 DCO；私钥、凭据及临时构建产物不纳入版本。
