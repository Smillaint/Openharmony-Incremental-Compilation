# 门禁结果复核（2026-10-18）

安装组的新任务已在静态检查阶段结束，SDK 编译没有启动。ace #7210 仍为十条既有文件名术语告警；build #7046 和 graphic_3d #676 的静态检查通过。没有发现需要追加修改的代码告警，本轮保留源码版本。

另外，SDK split 两条 PR 已通过完整门禁，HiSysEvent #7006 经维护者重跑失败项后也已通过。23 条相关 PR 的当前 HEAD 与保存版本相同，回读时均为 open；门禁通过与正式合入分开记录。

## 当前任务结果

| PR / 分组 | 当前提交 | 结果 |
| --- | --- | --- |
| ace #7210 | `92f3fe9598c24f6118774101968176b20fc7b342` | CodeCheck 未通过，10 条 WordsTool.110 Intent |
| build #7046 | `a82a8a03bd3a43c23c186d4ed32cd2602c010c93` | CodeCheck 通过，联合组在静态阶段被拦 |
| graphic_graphic_3d #676 | `57e960e087a2f0aefbcc5f21b0f88b6cefc354f0` | CodeCheck 通过，联合组在静态阶段被拦 |
| build #7049 / interface_sdk-js #36540 | `72115384` / `7b42242e` | 完整 SDK split 联合门禁通过 |
| build #7006 | `3dc5695a126e2c9b3de9336ad8a290d2b66c8d29` | 维护者重跑失败项，门禁通过 |

安装组[任务 6ad596ab64650f998b0d95f2](https://dcp.openharmony.cn/workbench/cicd/detail/6ad596ab64650f998b0d95f2/runlist)的结束时间为北京时间 2026-10-19 12:13:07。最终机器人回执为 ace `194466096`、build `194466097`、graphic_3d `194466093`。报告中的编译项显示 pending，但任务已经关闭，不能将这些项解释为仍在排队或运行。

## 十条告警的实际内容

[本轮 CodeCheck](https://dcp.openharmony.cn/workbench/cicd/detail/6ad596ab64650f998b0d95f2/runlist?pop=codecheck&taskId=MR_7d0848d5a7824d4ca6b4a87d0f4eda94)只有十条一般级别的 `WordsTool.110 Intent`。均位于 `arkui-plugins/sdk_files.json`，没有新增 G.FIO.05 或 package.json 告警。

| 清单位置 | 声明内容 |
| --- | --- |
| 23、40、759、760、761 | 五个现有 insight-intent TypeScript 源文件 |
| 1099、1116、1522、1523、1524 | 对应的五个 JavaScript 输出 |

已将五个源文件逐一与本轮门禁实际 ace 基线 `268bd17d50ae5f646fa44db1ed86981b4ed49191` 比较，Git blob 全部相同。PR 只是把真实路径纳入明确的 GN 输入输出，没有修改这些文件或引入其命名。清单中的十项依赖应保留，后续需要仓库维护者审核这十条文件名术语告警。

本轮没有更改清单编码、重命名业务源码、删减依赖或处置告警状态。既有检视回复草稿保留且未发送。

## 新确认的通过项

SDK split [任务 6ad56fa064650f998bfb70a8](https://dcp.openharmony.cn/workbench/cicd/detail/6ad56fa064650f998bfb70a8/runlist)已结束且 result 为 success，结束时间为北京时间 2026-10-19 11:11:49。任务中的两条 HEAD 与当前 PR 完全一致。

HiSysEvent #7006 的旧失败任务仍保留为历史记录。维护者 `ohci1` 于北京时间 11:11:23 发送 `start update build`，失败项重跑进入[任务 6ad58a7364650f998b07fb47](https://dcp.openharmony.cn/workbench/cicd/detail/6ad58a7364650f998b07fb47/runlist)，机器人于 11:31:58 以评论 `194455074` 确认门禁通过。该次只重跑失败构建，沿用此前已经通过的检查和测试。

通过任务的公开 SDK 日志中，ets1.2 的 npm 安装和 interop_compile 都实际执行。成功 manifest 与之前失败 manifest 的 build 基线、ace 提交完全相同，分别为 `6b6d6533`、`9e0f9e58`；#7006 补丁仍为 `3dc5695a`，没有带入尚未合入的 ace #7210。

这说明当次缺依赖并非在同一受控源码上必现。失败节点锁文件和链接未取得，具体工作区状态差异仍未确认。[旧锁文件兼容修复](oct18-build-common-dependency.md)有独立复现与验证，但不能将其写成 #7006 此次重跑通过的原因。

## 保存与继续处理

- 修改交接前保存标签 `backup/install-gate-followup-20261018`，对应交接仓 `0caccd1`。
- [任务、PR 快照、十条告警实物、基线 blob 比较和成功构建节选](evidence/20261018-install-gate-followup/)均已归档。完整 SDK 原始日志只保存在 `D:/workspace/archives/20261018-install-gate-followup/`，交接仓保留必要节选。
- 产品源码仍为既有带 DCO 的提交，本轮没有源码修改，也没有重新触发任务。没有新增编译或测试运行。
- 安装组标为静态失败并停止待查状态；SDK split 与 #7006 标为通过。自动巡检保持 PAUSED。

安装组继续推进的前提是维护者审核十条现有文件名告警。其余更新后尚无当前提交门禁回执的分支保持待验证，没有沿用旧版本结果。
