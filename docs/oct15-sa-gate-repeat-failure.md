# SA #6965 重复冒烟超时排查（2026-10-15）

[build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) 的第二轮门禁仍未通过。源码保持 `f15f9bded74ae12a75b8a9ef729c1397a7202ec2`，本次只排查门禁、保存证据和重新触发，没有追加代码修改。

## 第二轮结果

[门禁任务 6acfa28164650f998b3e5d24](https://dcp.openharmony.cn/workbench/cicd/detail/6acfa28164650f998b3e5d24/runlist)，结果评论 ID `193844642`。

- 静态检查通过；`dayu200`、`hispark_taurus_LiteOS` 编译及冒烟通过。
- `dayu600_7885` 编译通过，测试为 `failed(ecotest timeout)`，报告链接为空；DCP 提示“未生成日志文件”。
- `mac-sdk` 新增 `failed(流水构建失败)`，失败发生于工作区清理和源码准备阶段。
- `master_inner_build`、`x86_64_virt_tdd`、`ohos-sdk-codearts-new` 的失败标为 IGNORE，与上述两项分开记录。

## dayu600：编译成功，EcoTest 已接收但没有测试报告

[构建日志入口](https://cidownload.openharmony.cn/Artifacts/dayu600_7885/20261014-1-01060/log/build.log) 指向 [build.log.zip](https://cidownload.openharmony.cn/Artifacts/dayu600_7885/20261014-1-01060/log/build.log.zip)。实际文件为 TAR，成员 `ditribute_job_client`。编译、打包和上传均成功，结尾为 `Finished: SUCCESS`。

关键记录（日志时区 GMT+08:00）：

```text
[2026/10/15 00:27:44.186 GMT+08:00] trigger_ecotest result 200 {"statusCode":1,"status":"Success","result":"Success","failReason":"调度系统执行成功,未出现异常","taskId":2296023,"blockId":""}
[2026/10/15 00:27:51.102 GMT+08:00] Finished: SUCCESS
```

EcoTest 模板为 `L2_P7885_DOOR`，任务号为 **2296023**。初始接收响应不能证明后续设备调度或执行成功；目前公开记录只能确认任务已接收，随后门禁超时且没有提供测试报告。需要平台侧检查该任务的设备分配、执行及结果回传。

## mac-sdk：编译前工作区清理失败

[mac 构建日志](https://cidownload.openharmony.cn/Artifacts/mac/3d01fbfe0d5b4bdbbf05de5c67df5135/log/build.log) 停留在 `step2 : download code`。日志反复尝试 `timeout 1200s repo forall -c git clean -dfx`，第 3223 行报错：

```text
[ERROR]: mac_ci_build.sh,Line:232: failed to exec repo forall -c reset --hard
```

执行记录与最终错误标签的命令文字不同，因此仅定位为 CI 工作区清理／源码准备失败，不推断具体脚本实现错误。尚未进入产品编译或本 PR 的 SA 处理脚本。

## 同期对照与结论边界

- 独立 [build #7117](https://gitcode.com/openharmony/build/pull/7117) 的 [门禁](https://dcp.openharmony.cn/workbench/cicd/detail/6ad0959164650f998b8a5812/runlist) 同样出现 `dayu600_7885 success / failed(ecotest timeout)`，随后 `ohci1` 设为测试人并通过测试。这支持平台侧共性问题的判断，但不能替代本 PR 的设备测试。
- [build #7131](https://gitcode.com/openharmony/build/pull/7131) 的 [门禁](https://dcp.openharmony.cn/workbench/cicd/detail/6ad0adcf64650f998b946a72/runlist) 中 dayu600 和 mac-sdk 均成功，不能据此认定整个测试平台持续不可用。
- 暂未发现本次失败指向 SA 修改的证据。Mac 失败已定位到编译前；dayu600 的具体底层原因仍需测试平台日志确认。此前本地 rk3568 验证不等于 dayu600 设备验证。

## 证据与重试

[PR 第二轮结果](evidence/20261015-sa-smoke-recheck/pr6965-second-result.txt)、[DCP 详情](evidence/20261015-sa-smoke-recheck/second-gate.txt)、[#7117 对照](evidence/20261015-sa-smoke-recheck/comparison-pr7117.txt)、[#7131 对照](evidence/20261015-sa-smoke-recheck/comparison-pr7131.txt)。

完整原始日志保存在本地 `D:/workspace/archives/20261015-sa-smoke-recheck/`，未加入 GitHub 文档仓；其中含构建环境输出，归档仓仅保留上述相关摘录。

第三轮 `start build` 已发送，机器人已确认“门禁构建开始”。新任务为 [6ad165ef64650f998bcd430a](https://dcp.openharmony.cn/workbench/cicd/detail/6ad165ef64650f998bcd430a/runlist)。平台因上轮超过 12 小时而重新全量验证并重置旧验证状态；当前只确认启动，尚无最终结果。

[第三轮启动回执](evidence/20261015-sa-smoke-recheck/third-gate-started.txt)、[启动截图](evidence/20261015-sa-smoke-recheck/third-gate-started.png)。本轮不修改源码和 PR 描述；若再次失败，凭上述任务号和日志联系维护人员排查。

## 第三轮更新（2026-10-16 03:18 UTC）

当前 HEAD 未变化，全部非忽略项编译已通过，包括 dayu200_tdd；dayu600 和 LiteOS 冒烟通过。dayu200 冒烟失败，尚无最终门禁汇总回执。

本次失败与第二轮 dayu600 接收后超时不同：[dayu200 构建日志](https://cidownload.openharmony.cn/Artifacts/dayu200/20261016-1-00010/log/build.log.zip)第 260228–260230 行显示，EcoTest 触发接口于北京时间 2026-10-16 08:18:25、08:18:31、08:18:36 连续返回 HTTP 500。第 260236 行记录 `trigger_ecotest_failed`、`E06`、`testTaskId=error`、`testDuration=0`，没有创建有效测试任务。后续上传失败和流水线退出 1 属于后续错误。

失败位于测试平台任务提交阶段，没有测试用例失败或 SA 编译错误证据。应向平台维护人员提供 CI `6ad165ef64650f998bcd430a`、dayu200 产物 `20261016-1-00010`、北京时间 08:18:25–08:18:41，检查服务内部异常。第二轮任务号 `2296023` 不适用于本次失败。

[本轮巡检与日志摘录](evidence/20261015-companion-prs/monitor/20261016T031827Z/summary.md)保存完整证据索引。此次没有修改源码、PR 描述或重新触发门禁。

## 第三轮最终回执（2026-10-16 03:48 UTC 巡检）

机器人于北京时间 11:19:55 发布结果评论 `194102298`，对应同一 CI 和 HEAD，确认“代码门禁未通过”。dayu200 测试失败明确标注 `trigger_ecotest_failed`；静态检查和全部非忽略项编译通过。最终报告与上述 HTTP 500 诊断一致，没有新增失败原因。详情见[本轮巡检](evidence/20261015-companion-prs/monitor/20261016T034833Z/summary.md)，没有重新触发门禁。
