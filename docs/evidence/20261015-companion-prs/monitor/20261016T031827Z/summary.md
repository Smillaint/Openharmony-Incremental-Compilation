# 门禁巡检（2026-10-16 03:18 UTC）

SA #6965 的 dayu200 冒烟失败已定位到 EcoTest 任务提交：服务连续返回 HTTP 500，没有创建有效测试任务。全部非忽略项编译已通过；尚未收到本轮最终门禁汇总回执，不能记为门禁通过。

## SA：EcoTest 触发接口返回 500

- PR：[build #6965](https://gitcode.com/openharmony/build/merge_requests/6965)，HEAD `f15f9bded74ae12a75b8a9ef729c1397a7202ec2`。
- [当前第三轮门禁](https://dcp.openharmony.cn/workbench/cicd/detail/6ad165ef64650f998bcd430a/runlist)，CI `6ad165ef64650f998bcd430a`，开始回执 `194060838`。
- dayu200 产物：`Artifacts-dayu200-20261016-1-00010-version-dayu200.tar.gz`；[产物弹窗](sa-build-artifacts.txt)同时显示当前 HEAD 补丁。
- [构建日志入口](https://cidownload.openharmony.cn/Artifacts/dayu200/20261016-1-00010/log/build.log)指向 [build.log.zip](https://cidownload.openharmony.cn/Artifacts/dayu200/20261016-1-00010/log/build.log.zip)。文件实际为 TAR，成员 `ditribute_job_client`。

首个与该失败相关的报错位于第 **260228** 行，之后连续两次重试仍为相同错误。时间采用 GMT+08:00：

| 日志行 | 时间（2026-10-16） | 内容 |
| --- | --- | --- |
| 260228 | 08:18:25.921 | `trigger_ecotest result 500`，`Internal Server Error` |
| 260229 | 08:18:31.201 | 第二次 HTTP 500 |
| 260230 | 08:18:36.482 | 第三次 HTTP 500 |
| 260232 | 08:18:41.762 | `trigger ecoTest failed` |
| 260236 | 08:18:41.763 | `testTaskId=error`、`testDuration=0`、`buildFailReason=trigger_ecotest_failed`、`buildFailType=E06` |
| 260244–260249 | 08:19:20–08:19:26 | 后续 `upload version failed`、脚本退出 1、`Finished: FAILURE` |

分类为**测试平台服务／任务提交失败**，尚未进入测试用例执行。末尾上传失败和流水线退出是后续错误，不能替代前面的 HTTP 500 作为首个原因。这些证据不指向 SA 编译错误；服务内部为何返回 500 仍需平台日志。

建议向 EcoTest 平台维护人员提供上述 CI、产物编号 `20261016-1-00010` 和北京时间 **08:18:25–08:18:41**，检查任务提交接口异常。本轮没有有效测试任务号，不能使用第二轮 dayu600 的任务号 `2296023` 查询本次问题。

[日志摘录](sa-build-excerpt.json)保存报错及必要流水线字段。完整原始日志仅保存在本地 `D:/workspace/archives/20261015-companion-prs/monitor-20261016T031827Z/`，不加入 GitHub 归档。测试详情页仍显示“未生成日志文件”，本次原因来自构建日志中的 EcoTest 提交记录。

## 其余范围

| 范围 | 状态 |
| --- | --- |
| IDL | 三项冒烟通过；x86_64_virt_tdd、dayu200_tdd 仍运行，无最终回执。部件任务零耗时失败没有新日志，不套用其他组的忽略结论。 |
| HAP | 三项冒烟通过；dayu200_tdd 仍运行，无最终回执。 |
| loader | 三项冒烟通过；x86_64_virt_tdd、dayu200_tdd 仍运行，无最终回执。 |
| SDK split / 安装组 | 原 CodeCheck 失败与提交未变化，沿用[首轮分析](../20261016T014905Z/summary.md)。 |
| JS/CSS / 四条已通过历史 PR | 已完成，本轮未再查询。 |
| build #7048 / sane-airscan #22 | 当前 HEAD 仍无启动回执，不计为运行或通过。 |

本轮查询 17 条未完成 PR：HEAD 和开放状态均未变化，没有新增或编辑评论；仅 SA #6965 新增“编译成功”标签。SA 的 dayu200_tdd 已通过，dayu600 和 LiteOS 冒烟通过。详细页面分别保存在 `*-run.txt`，API 快照见 `github-gitcode-status.json`，状态差异见 `delta.json`。

没有重发 `start build`、创建 PR、修改产品源码或合入 PR。未达到全部完成的停止条件，继续巡检；后续相同 HTTP 500 失败保持安静。
