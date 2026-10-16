# 门禁巡检（2026-10-16 02:18 UTC）

本轮没有新增可操作故障、原因变化或需要处理的事项，不重复通知已有失败。

尚未完成的 19 条 PR 均读取了当前 HEAD、标签和全部评论；HEAD 和开放状态均未变化，没有新增机器人评论或新门禁。上一轮完成的 build #6999、#7009、#7006、iptables #62 未再查询。

| 范围 | 本轮变化 / 结论 |
| --- | --- |
| IDL | 多项主构建通过；dayu200 冒烟及 x86_64_virt_tdd、dayu600、dayu200_tdd 仍执行中。两个部件任务仍是零耗时失败、无阶段信息，与上轮相同。 |
| JS/CSS | 两条 PR 新增“编译成功”标签；主构建非忽略项及 new_part_compile 通过。dayu200、dayu600 冒烟仍执行中，整组尚未通过。part_compile 零耗时失败未变化。 |
| HAP | new_part_compile、part_compile 均通过；dayu200 冒烟、dayu600、dayu200_tdd 仍执行中。没有新增阻断失败。 |
| loader | dayu200 与 LiteOS 冒烟通过；dayu600 冒烟、x86_64_virt_tdd 与 dayu200_tdd 编译仍执行中。没有新增阻断失败。 |
| SDK split / 安装组 | 原 CodeCheck 失败不变，无新提交、无新门禁。沿用首轮已记录的规则、行号与处理建议，不重复分析相同告警。 |
| SA #6965 | dayu200 编译通过、冒烟失败不变。再次点击日志入口仍提示“未生成日志文件”；无法新增归因，仍需平台侧记录。两个 TDD 构建仍执行中。 |
| build #7048 / sane-airscan #22 | 当前 HEAD 仍没有门禁启动回执，不计为通过，不自动触发。 |

未将“编译成功”标签或部分目标通过视为整组门禁通过。明确标为“失败(忽略)”的目标保持忽略。没有重发 `start build`、新建 PR、改动产品源码或合入 PR。

证据：`github-gitcode-status.json` 为 19 条 GitCode PR API 快照；`delta.json` 记录与首轮的差异；`*-run.txt` 为 DCP 页面；`sa-test-detail.txt` 包含缺日志提示；`before-state.json`、`after-state.json` 保存前后状态。原故障分析见 [首轮记录](../20261016T014905Z/summary.md)。

尚未达到全部通过或关闭的停止条件，继续每 30 分钟巡检。
