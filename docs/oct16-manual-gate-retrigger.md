# 2026-10-16 静态检查通过组的门禁重跑

北京时间约 16:22—16:26，当前静态检查成功且完整门禁未通过的 SA、HAP 两组各提交一次 `start build`。两组均收到新的启动回执；HAP 配套 PR 收到相同 CI 编号。当前为运行中，尚无本轮最终结果。

| 分组 | PR | 新门禁 | 回执 |
| --- | --- | --- | --- |
| SA | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | [6ad1df3c64650f998bfe576e](http://dcp.openharmony.cn/workbench/cicd/detail/6ad1df3c64650f998bfe576e/runlist) | 命令 194176632，启动 194176796 |
| HAP | [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) + [packing_tool #1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556) | [6ad1df6864650f998bfe6baf](http://dcp.openharmony.cn/workbench/cicd/detail/6ad1df6864650f998bfe6baf/runlist) | 命令 194176816，启动 194177048 / 194177042 |

机器人选择“部分构建失败，仅触发失败构建”：SA 重跑 dayu200 编译和测试、master_inner_build、ohos-sdk-codearts-new；HAP 重跑 dayu200_tdd、master_inner_build、x86_64_virt_tdd、ohos-sdk-codearts-new。通过的静态检查由平台沿用。

SDK、安装组新提交仅有 DCO 成功，代码更新后静态状态已重置，未触发本轮门禁。build #7048、airscan #22 也没有当前提交的静态成功结果。此前确认通过的 13 条 PR 保留原结果。

自动巡检仍为 PAUSED。未修改源码或 PR 正文，未合入 PR。旧失败记录保留于 monitor-state.json 的 previous_gate；新任务状态为 running，不将启动视为通过。

启动回执、页面快照及截图见 [证据目录](evidence/20261016-manual-gate-retrigger/)。
