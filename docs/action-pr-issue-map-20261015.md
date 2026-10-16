# Action、PR 与 Issue 对照（2026-10-15）

本批 13 条历史 PR 对应 13 个开放 Issue，重复 Issue build #4759 保持关闭。13 个 Issue 的正文均已补齐 Action、直接修复、跨仓配套及缺少的 PR；公开 API 回读与保存文本一致。现有正式 PR 关联保持原样，本次没有改源码、创建 PR 或触发门禁。

完整安装链入口：[build Issue #4704](https://gitcode.com/openharmony/build/issues/4704)。Issue 正文中的参考链接用于追踪修复，不等于正式加入同一个联合门禁组。

## 原始十项 Action

表中 PR 均为 `openharmony` 组织仓库；同一 PR 可以覆盖多个 Action，同一 Action 也可能需要多个 PR。

| Action | 直接修复 PR | Issue 与补充关系 |
| --- | --- | --- |
| `sa_profile_src_phone` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | [build #4657](https://gitcode.com/openharmony/build/issues/4657)：排序输入，源 JSON 按内容发布；公共 parts 稳定化见下方 |
| `sa_profile_binary_phone` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 同 #4657：稳定 ZIP 内容及 entry 时间戳 |
| `phone_sa_profile_install_info` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 同 #4657：安装 JSON 按内容发布 |
| `check_seccomp_filter_name` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | [build #4678](https://gitcode.com/openharmony/build/issues/4678)：真实输入、成功输出、失败清理 |
| `process_field_validate` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 同 #4678：cfg/白名单依赖及校验输出 |
| `collect_notice_files__phone` | [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009)、[#7048](https://gitcode.com/openharmony/build/merge_requests/7048) | [build #4684](https://gitcode.com/openharmony/build/issues/4684)、[#4705](https://gitcode.com/openharmony/build/issues/4705)：分阶段收集/发布，加许可证边界与生成物依赖补充 |
| `generate_host_symlink` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 同 #4678：host 元数据收集及稳定发布 |
| `phone_hisysevent_install_info` | [build #7006](https://gitcode.com/openharmony/build/merge_requests/7006) | [build #4682](https://gitcode.com/openharmony/build/issues/4682)：配置/安装 JSON 稳定发布，真实 YAML 加入 depfile |
| `phone_install_modules` | [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046) 及下表上游修复 | [build #4704](https://gitcode.com/openharmony/build/issues/4704)：SA 依赖过滤、安装元数据/模块列表稳定、空 arm64e 输出、两份安装规则输入 |
| `phone_parts_list` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999)、[#7009](https://gitcode.com/openharmony/build/merge_requests/7009) | #4678、#4684：parts 聚合与安装元数据稳定；loader 的 `components.json` 补充尚无独立 PR |

## 安装上游与跨仓修复组

下表包含原始十项之外、影响最终安装稳定性的生成链。组合构建的效果不能全部归于 #7046，也不能把保存的源码分支算作已经提交的 PR。

| 修复组 | 已有 PR / 当前 Issue | 配套范围与联合门禁安排 |
| --- | --- | --- |
| HAP 打包与签名 | [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) / [#4663](https://gitcode.com/openharmony/build/issues/4663)；[packing_tool #1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556) / [#1201](https://gitcode.com/openharmony/developtools_packing_tool/issues/1201) | 签名 Action 真实输入/输出与 ZIP entry 固定时间；跨仓两 PR 可以共用 Issue，当前保留原正式关联并互相列明 |
| IDL 模板及五仓调用方 | [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) / [#4668](https://gitcode.com/openharmony/build/issues/4668) | 五仓 PR 待创建，统一关联 #4668，形成六仓组；补齐具体输出、common 类型依赖、递归 import 与 clean 恢复 |
| SDK 接口拆分 | [build #7049](https://gitcode.com/openharmony/build/merge_requests/7049) / [#4706](https://gitcode.com/openharmony/build/issues/4706) | interface_sdk-js 调用方 PR 待创建，关联 #4706，消费 stamp/depfile 并稳定发布 |
| JS/CSS | [jsframework #853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853) / [#323](https://gitcode.com/openharmony/third_party_jsframework/issues/323) | css-what PR 待创建，关联 #323；`gen_snapshot`、`ark_jsf` 在 out 内构建，补齐 CSS 复制输出与 fixture innerkit |
| airscan | [airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22) / [#19](https://gitcode.com/openharmony/third_party_sane-airscan/issues/19) | 八项补丁在 out 生成副本，具体 inputs/outputs，按内容发布；独立组 |
| iptables | [iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) / [#48](https://gitcode.com/openharmony/third_party_iptables/issues/48) | `genInit.py` 不再无条件改写 initext 源，避免 CC/AR/LINK 及安装重跑；独立组 |
| SDK 插件 / wrapper / libarkts | 尚无 PR | developtools_ace_ets2bundle 修复分支已发布；与 SDK split 的 #7049 区分 |
| ROFS | 尚无 PR | graphic_graphic_3d 修复分支已发布；稳定生成对象，避免共享库重链 |
| loader `components.json` | 尚无独立 PR | build 累计修复分支已保存；需按范围提交，不能再向含 build/master PR 的 Issue 增挂另一条 build/master PR |

IDL 五仓：`account_os_account`、`inputmethod_imf`、`security_dlp_permission_service`、`ability_dmsfwk`、`multimedia_audio_framework`。它们补齐 callback/common 输出、InputMethodClientTypes、DlpPermissionTypes、DeviceConnectStatus，以及音频 callback 对共享类型生产者的依赖。逐目标清单已写入 #4668。

按作者 `SmillySmillick` 查询上述五仓、css-what、interface_sdk-js、ace_ets2bundle、graphic_3d 的全部状态 PR，九仓均未返回该作者 PR。查询参数为 `author=SmillySmillick&state=all&per_page=100`，不是 `creator`。因此，除 IDL/CSS 六条外，SDK 调用方、插件/wrapper、ROFS 也仍有提交缺口；loader 是另一个同仓范围。源码范围以 [源码交接](oct13-source-pr-handoff.md) 和 [离线源码目录](oct14-all-repairs-offline.md) 为准，不能仅靠原 13 条 PR 覆盖全部累计修复。

## 联合门禁规则与本次确认

当前 master 的 [OpenHarmony 官方 FAQ](https://gitcode.com/openharmony/docs/blob/master/zh-cn/contribute/FAQ.md) 明确支持：在一个相关仓创建 Issue，将有编译依赖的跨仓 PR 关联到同一 Issue，由构建中心同时下载、构建，审核满足条件后共同合入。FAQ 文件对象为 `4e64b20a0f7a709bd507bffe4eecece750e55211`。

[社区命令清单](https://gitcode.com/openharmony/community/blob/master/zh/infrastructure/build_command.md) 说明，PR 创建人或 Committer 可通过评论 `start build` 触发构建。每组先在其中一条 PR 发起，检查机器人回执是否包含整组 PR 及当前提交，避免重复启动相同组。

同仓同目标分支存在限制。#7130 的机器人评论 `193776440`（2026-10-14）原文：

> 检测到同仓同分支存在2个或以上PR https://gitcode.com/openharmony/build/merge_requests/7130 & https://gitcode.com/openharmony/build/merge_requests/6965 关联相同ISSUE，禁止触发门禁

这两条 PR 的源分支不同，但都合向 `openharmony/build:master`。因此，本批同仓同目标分支的开放 PR 不能靠关联一个 Issue 联合验证；要么整合成一个 PR，要么按依赖顺序合入。NOTICE #7009/#7048 及 parts #6999/#7009 保留各自 Issue，通过正文互相引用完整修复。

关闭历史不等于 Issue 永久不能复用：#4657 的关联接口仍列出已关闭 #7130，但关闭重复项后 #6965 已正常启动门禁，证据见 [SA 组更新记录](oct14-sa-profile-group-update.md)。因此，不采用“曾关联关闭 PR 就必须重开 Issue”的旧说法；以当前开放 PR 组合与机器人回执判断。

后续联合门禁按以下顺序操作：

1. 每组先补齐所有跨仓 PR；新提交带 `Signed-off-by: Smillick <3185479846@qq.com>`。
2. 在 PR 的正式 Issue 关联中选择同一条 Issue；只在正文贴 URL 不会建立正式联合关系。
3. 从 Issue 的关联 PR 列表核对组成员，确认每个仓库/目标分支没有重复开放 PR。IDL 用 build #4668，JS/CSS 用 jsframework #323，SDK split 用 build #4706。
4. 在组内一条 PR 评论 `start build`，核对联合任务的成员与 HEAD。提交发生变化后，旧门禁结果不能代替新提交验证。
5. HAP 两条旧 PR 若需联合验证，可统一正式关联到 build #4663，并保留 packing_tool #1201 的历史记录；本次尚未变更这一关联。

## 保存与核对

- 修改前主仓 HEAD：`fa8549ddf027c2cf37d785bc80f18ff3e674c9bd`；备份标签 `backup/action-issue-grouping-20261015`。
- [修改前快照](evidence/20261015-action-issue-grouping/before.json)、[精确保存文本](evidence/20261015-action-issue-grouping/issue-update-plan.json)、[保存后快照](evidence/20261015-action-issue-grouping/after.json)、[核对结果](evidence/20261015-action-issue-grouping/verification.json)。
- 核对结果：13/13 正文一致，13 个 Issue 均 open，正式 PR 关联均未改变；重复 #4759 为 closed。清单链接不会自动把同仓 PR 合为一个门禁组。
- [九仓配套 PR 查询](evidence/20261015-action-issue-grouping/companion-pr-search.json)、[规则来源](evidence/20261015-action-issue-grouping/gate-rule-sources.json)、[页面截图](evidence/20261015-action-issue-grouping/screenshots/)。
- 本次只整理 Issue 与交接资料，源码提交、PR 正文、现有门禁任务不变。产品构建数据仍引用对应历史验证文档。
