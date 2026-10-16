# 门禁巡检（2026-10-16 04:18 UTC）

IDL 六条 PR 的联合门禁正式通过，全部当前 HEAD 与触发时一致，移出后续巡检。没有新增可操作故障或需要处理的事项。

## IDL 完成记录

[联合门禁 6ad17dba64650f998bd49019](https://dcp.openharmony.cn/workbench/cicd/detail/6ad17dba64650f998bd49019/runlist)在六条 PR 上分别发布“代码门禁通过”回执。以下时间均为 2026-10-16 北京时间：

| PR | HEAD | 通过回执 | 时间 |
| --- | --- | --- | --- |
| build #6982 | `de69337b7f99f2328417e27fe591903862c9bbdc` | 194114104 | 11:53:13 |
| account_os_account #3898 | `b55c624c20ca24d4c64e98304fb5d3f975606a90` | 194114101 | 11:53:12 |
| inputmethod_imf #2774 | `331a15a1cda376687080a3977999de42182ec3ec` | 194114121 | 11:53:16 |
| security_dlp_permission_service #953 | `c5f19c2aad14e30ea3bf00c5ef49e9fbd2a74f28` | 194114115 | 11:53:15 |
| ability_dmsfwk #2123 | `6d99e0fef7fe7b69f63f2445c8852303f055506d` | 194114136 | 11:53:21 |
| multimedia_audio_framework #17444 | `c1aafc5d32b0b1ad6a429149090fda7b187ddf69` | 194114111 | 11:53:14 |

静态检查、编译、冒烟成功标签齐全。最终报告明确将此前零耗时的 `part_compile` 和 `new_part_compile` 列为 `failed(IGNORE)(skip build)`，均不阻断本组；CodeArts 与 master_inner_build 也明确标为忽略。全部六条正式回执保存在 [idl-final-results.json](idl-final-results.json)。不再根据此前零耗时显示推断代码失败。

## 其余范围

| 范围 | 状态 |
| --- | --- |
| HAP | 三项冒烟已通过；dayu200_tdd 仍运行，无最终回执。 |
| loader | x86_64_virt_tdd 新通过（IGNORE）；三项冒烟已通过，dayu200_tdd 仍运行，无最终回执。 |
| SDK split / 安装组 | 同一 HEAD 的原 CodeCheck 失败无变化，沿用[首轮原因与建议](../20261016T014905Z/summary.md)。 |
| SA #6965 | 已确认的 EcoTest HTTP 500 提交失败没有变化，沿用[日志诊断](../20261016T031827Z/summary.md)与[正式回执](../20261016T034833Z/summary.md)。 |
| JS/CSS / 四条已通过历史 PR | 本轮未再查询。 |
| build #7048 / sane-airscan #22 | 当前 HEAD 仍无启动回执，不计为运行或通过。 |

本轮读取 17 条未完成 PR，HEAD 和开放状态均未变化，只有 IDL 六条新增正式通过回执及分配检视提示，没有评论编辑。累计完成并停止检查 12 条 PR，联合门禁完成 2/6 组（IDL、JS/CSS）。下轮检查范围减至 11 条未完成 PR。

HAP 和 loader 当前 DCP 状态见两份 `*-run.txt`。API 快照、状态差异和前后状态保存在同目录。没有修改源码、创建 PR、重复触发门禁或自行合入；全部完成条件尚未满足，继续巡检。
