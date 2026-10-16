# 门禁巡检（2026-10-16 02:48 UTC）

JS/CSS 联合门禁已正式通过，移出后续检查。没有新增可操作故障或需要处理的事项。

## 已完成组

[JS/CSS 门禁报告](https://dcp.openharmony.cn/workbench/cicd/detail/6ad17dce64650f998bd497ca/runlist)：

| PR | 当前 HEAD | 通过回执 | 北京时间 |
| --- | --- | --- | --- |
| third_party_jsframework #853 | 4172098b9b45baf9b37fa3be021bf1ff6bea6359 | 194083585 | 2026-10-16 10:21:47 |
| third_party_css-what #29 | 0ad16b63ecbad73335b62474499f205b8848382c | 194083555 | 2026-10-16 10:21:43 |

两条 PR 的回执均为“代码门禁通过”，对应既定 CI，HEAD 与触发时一致。静态检查、编译、冒烟成功标签齐全。最终报告明确将之前的 part_compile 零耗时失败列为 `failed(IGNORE)(skip build)`，new_part_compile 为 `success(IGNORE)`，CodeArts 异常也标为忽略，均不阻断本组。以后不再轮询该组。

## 其余结果

| 范围 | 当前状态 |
| --- | --- |
| IDL | dayu200、dayu600、LiteOS 冒烟通过；x86_64_virt_tdd 与 dayu200_tdd 仍执行中，无最终回执。部件任务零耗时状态未变化，不能套用 JS/CSS 的最终分类。 |
| HAP | dayu200、dayu600、LiteOS 冒烟通过；dayu200_tdd 仍执行中，无最终回执。 |
| loader | dayu200、dayu600、LiteOS 冒烟通过；x86_64_virt_tdd 与 dayu200_tdd 仍执行中，无最终回执。 |
| SA #6965 | x86_64_virt_tdd 已通过（忽略项），dayu200_tdd 仍运行。既有 dayu200 冒烟失败再次打开仍提示“未生成日志文件”，原因没有新证据。 |
| SDK split / 安装组 | 同一提交的原 CodeCheck 失败无变化，未出现新门禁；沿用首轮分析。 |
| build #7048 / sane-airscan #22 | 当前提交仍无启动回执，不计为通过或运行。 |

本轮查询 19 条未完成 PR；全部 HEAD、开放状态未变化。只有 JS/CSS 的两条 PR 新增结果及检视分配提示。四条先前已通过的历史 PR 未再查询。累计完成并停止检查的 PR 为 6 条，其中本轮联合组完成 1/6。

没有重发 `start build`、创建 PR、修改产品源码或合入 PR。未根据运行时长自动重试。尚未达到全部通过或合入/关闭的停止条件，巡检继续。

`github-gitcode-status.json` 保存 API 快照；`delta.json` 保存差异和通过回执 ID；`*-run.txt` 为 IDL、HAP、loader、SA 的 DCP 页面；`sa-test-detail.txt` 含再次打开失败日志时的提示；`before-state.json`、`after-state.json` 保存前后状态。[原故障分析](../20261016T014905Z/summary.md)继续有效。
