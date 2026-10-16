# 门禁巡检（2026-10-16 05:48 UTC）

HAP 联合门禁新增失败，阻断项是 dayu200_tdd 的 `pipeline running timeout`。构建日志确认源码编译已经成功，超时发生在编译完成后的归档／产物发布窗口；结果回写随后因状态异常被拒绝。

## PR 和回执

| PR | 当前 HEAD | 失败回执 | 北京时间 |
| --- | --- | --- | --- |
| [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) | `34aa8cba0c5fcb3344e2dd652c18027d69a71396` | 194126102 | 2026-10-16 13:30:08 |
| [packing_tool #1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556) | `dcbbc78ada8c90cb31542ecc385bb7d5b5faddbc` | 194126103 | 2026-10-16 13:30:09 |

两条 PR 的 HEAD 未变化，回执对应原 [CI 6ad17e0a64650f998bd4b234](https://dcp.openharmony.cn/workbench/cicd/detail/6ad17e0a64650f998bd4b234/runlist)。静态检查和 dayu200、dayu600、LiteOS 三项冒烟通过；hap_build 通过。x86_64_virt_tdd、master_inner_build、CodeArts 的失败明确标为 IGNORE，不是本轮阻断项。[正式结果](hap-final-results.json)已保存。

## 首个错误与时间线

DCP 的“日志解析”没有给出错误，但“日志详情”有当前两条 HEAD 的补丁以及 dayu200_tdd 产物 `20261016-1-00094`。因此继续读取[构建日志入口](https://cidownload.openharmony.cn/Artifacts/dayu200_tdd/20261016-1-00094/log/build.log)指向的 [build.log.zip](https://cidownload.openharmony.cn/Artifacts/dayu200_tdd/20261016-1-00094/log/build.log.zip)，实际为 TAR，成员 `ditribute_job_client`，共 755486 行。

以下时间均为 2026-10-16 GMT+08:00，采用日志消息内时间；外层采集时间可能稍晚。

| 时间 | 证据 | 含义 |
| --- | --- | --- |
| 09:29:33 | DCP 调度时间 | 本轮任务已调度。 |
| 13:14:33 | 第 755120 行：`rk3568 build success` | dayu200_tdd 源码编译成功。 |
| 13:15:47–13:19:13 | 第 755256、755258 行 | 收集并复制测试产物。 |
| 13:19:14 | 第 755270 行：`tar -I 'gzip --fast'` | 开始压缩归档。 |
| 13:30:08 | build #6974 最终回执 | 门禁已判定 `pipeline running timeout`。 |
| 13:30:40 | 第 755271 行：`tar image result: 0` | 归档成功，压缩阶段约 11 分 26 秒。 |
| 13:30:56 | 第 755472 行：`Upload successfully`，15.84GB，状态 200 | 产物实际上传成功。 |
| 13:31:02 | 第 755480 行：`currentStatus error, can not upload result to mongo` | 首个明确 ERROR，结果回写被拒绝。 |
| 13:31:03–13:31:09 | 第 755481、755482、755486 行 | 后续报上传失败、脚本退出 1、流水线 FAILURE。 |

失败分类为**流水线总时限及结果状态回写问题**。时间线支持“归档还没结束时门禁先判定超时，晚到结果无法回写”的判断；具体配置时限和服务端状态变更仍需平台确认。不能将最后的 `upload version failed` 理解为产物没有上传，因为前面已有 HTTP 200 和完整产物。没有发现本目标失败指向 HAP 源码编译的证据，门禁本身仍是失败状态。

可执行建议：向 CI 平台维护人员提供本 CI、产物 `20261016-1-00094` 和北京时间 **13:14–13:31**，检查总超时是否包含排队及归档时间，以及超时后结果回写的处理方式。调度至失败回执约 4 小时，但未读取平台配置，不断言配置值恰为 4 小时。维护人员可据完整成功产物评估补录结果或调整时间预算；本次不自动重触门禁，不据此改 HAP 源码。

[脱敏日志摘录](hap-build-excerpt.json)只保留编译、归档、上传与结果回写记录。完整原始日志仅保存在本地 `D:/workspace/archives/20261015-companion-prs/monitor-20261016T054826Z/`，不加入 GitHub 归档。

## 其余状态

SDK split、安装组仍为原 CodeCheck 失败；SA 仍为原 EcoTest HTTP 500 提交失败，没有变化。IDL、JS/CSS、loader 和四条历史 PR 共 13 条已完成，本轮未查询。build #7048 与 sane-airscan #22 当前 HEAD 仍无启动回执。

本轮查询 10 条 PR，HEAD 和开放状态均未变化，只有 HAP 两条新增失败结果及标签变化。六个联合组现为三组通过、三组失败，无组仍在运行；原 SA 另为失败。全部通过或合入/关闭的停止条件未满足，继续观察后续回执与处理，不重复触发门禁。
