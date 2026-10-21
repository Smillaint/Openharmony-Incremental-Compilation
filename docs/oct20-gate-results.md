# 修订版门禁结果复核（2026-10-20）

查询时间：2026-10-20 20:49 PDT（`2026-10-21T03:49:56.258571+00:00`）。八组最新修订门禁全部结束，三组通过、五组失败。十四条组内 PR 的当前 HEAD 与事件实测 HEAD 一致，十四条 DCO 和静态检查均通过；没有新的静态告警。

本轮只查询门禁、评论和公开构建日志，未修改源码、回复检视、合入或重触发任务。自动巡检继续暂停。

## 八组实际结果

| 分组 | PR 入口 | 静态 | 最终结果 / 阻断项 | 门禁 |
| --- | --- | --- | --- | --- |
| IDL 六仓 | [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) | 通过 | dayu600 冒烟超时 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad733af64650f998ba21c45/runlist) |
| 校验、host、parts | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 通过 | dayu600 冒烟超时；dayu200_tdd 流水线超时 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad733b164650f998ba21ed3/runlist) |
| loader | [build #7134](https://gitcode.com/openharmony/build/merge_requests/7134) | 通过 | 通过 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad7337e64650f998ba20458/runlist) |
| SA 三项 | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 通过 | dayu600 冒烟超时 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad733e364650f998ba2405e/runlist) |
| HAP 两仓 | [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) | 通过 | dayu600 冒烟超时 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad733f664650f998ba24803/runlist) |
| NOTICE 收集 | [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009) | 通过 | 通过 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad7340464650f998ba24fe4/runlist) |
| NOTICE 配套 | [build #7048](https://gitcode.com/openharmony/build/merge_requests/7048) | 通过 | 通过 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad7341764650f998ba25b13/runlist) |
| airscan | [third_party_sane-airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22) | 通过 | dayu600 冒烟超时 | [任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad7342c64650f998ba2669d/runlist) |

通过组的 `master_inner_build`、`ohos-sdk-codearts-new` 等失败行均由最终回执明确标注 `IGNORE`，没有把这些行误计成阻断故障。五个失败组则都有未忽略的 `dayu600_7885` 测试超时。

## dayu600 的五次超时

五组编译、打包、上传均成功，公开日志末尾为 `Finished: SUCCESS`。EcoTest 接口均返回 HTTP 200、`status=Success`，取得了真实任务 ID；随后门禁以 `ecotest timeout` 结束，没有测试报告、用例断言或失败堆栈。

| 触发 PR | EcoTest 任务 | blockId | 构建阶段 | 日志 |
| --- | --- | --- | --- | --- |
| #6982 | `2307291` | 空 | 成功 | [构建日志](https://cidownload.openharmony.cn/Artifacts/dayu600_7885/20261020-1-00921/log/build.log.zip) |
| #6999 | `2307324` | 空 | 成功 | [构建日志](https://cidownload.openharmony.cn/Artifacts/dayu600_7885/20261020-1-00913/log/build.log.zip) |
| #6965 | `2307321` | 空 | 成功 | [构建日志](https://cidownload.openharmony.cn/Artifacts/dayu600_7885/20261020-1-00926/log/build.log.zip) |
| #6974 | `2307318` | 空 | 成功 | [构建日志](https://cidownload.openharmony.cn/Artifacts/dayu600_7885/20261020-1-00924/log/build.log.zip) |
| #22 | `2307232` | 空 | 成功 | [构建日志](https://cidownload.openharmony.cn/Artifacts/dayu600_7885/20261020-1-00916/log/build.log.zip) |

现有证据定位到测试服务执行/回报超时，不能进一步认定是设备分配、刷机、用例执行还是回报链路，也不能仅凭超时认定源码绝对无关。下一步应由 EcoTest 平台根据上述任务 ID 查询 `L2_P7885_DOOR` 的设备、刷机和执行记录；没有据此修改增量构建脚本或自动重试。

## #6999 的额外失败

`dayu200_tdd` 在日志中完成 `357163/357163` 个 Ninja 任务，随后于北京时间 `2026-10-20 21:20:14` 显示 `rk3568 build success`，主构建耗时 `13242.84 s`。DCP 于 `21:27:09` 将流水线判为 `pipeline running timeout`。产物约 15.97 GB，后续 `21:38:13` 上传成功，但 `21:38:19` 回写结果报 `currentStatus error, can not upload result to mongo`，最终退出失败。

因此本次不是编译器报错导致该项失败：编译完成后还需要打包、上传，整个任务超过平台时限；回写错误发生在其后。运行缓慢的进一步资源原因没有从日志确认。[日志尾部精确证据](evidence/20261020-gate-result-check/6999-dayu200_tdd-final-signals.json)。

此外 `x86_64_virt_tdd` 的首个真实错误是：

```text
ninja: error: 'clang_x64/obj/arkcompiler/toolchain/inspector/test/unittest.stamp', needed by 'precise', missing and no known rule to make it
```

该项在最终回执被明确标为 `failed(IGNORE)(compile failed)`，不是本组阻断项。#6999 的实际二十个修改文件没有 precise 或 inspector 规则改动，当前按精确构建目标图兼容问题记录；没有凭缺目标错误扩大增量修复范围。[首错片段](evidence/20261020-gate-result-check/6999-x86-first-error.json)、[实际 PR diff](evidence/20261020-gate-result-check/build-6999-files.json)。

## 其余 PR 和检视

本次回读全部二十三条相关 PR：八条开放 PR 有当前提交的完整门禁通过记录；十四条开放 PR 被本轮超时或既有安装组静态告警阻断；build #7006 已合入。没有运行中的组，也没有 HEAD 变化。

- SDK split（build #7049、interface_sdk-js #36540）、JS/CSS（jsframework #853、css-what #29）、iptables #62 继续通过。
- 安装组（build #7046、ace #7210、graphic_3d #676）状态未变化，ace 仍为十条术语告警，未重新触发。
- 本轮新通过且审查人列表包含 ringking0 的 PR：[loader #7134](https://gitcode.com/openharmony/build/merge_requests/7134)、[NOTICE #7009](https://gitcode.com/openharmony/build/merge_requests/7009)、[NOTICE 配套 #7048](https://gitcode.com/openharmony/build/merge_requests/7048)。当前三条的 ringking0 `accept=false`，门禁通过不代表检视批准。#7134 先前批准在源码修订后已重置。

## 证据与保存

[逐组诊断与最终回执 ID](evidence/20261020-gate-result-check/diagnosis.json)、[公开 API 原始快照](evidence/20261020-gate-result-check/summary.json)以及同目录 `gate-*.json`、逐 PR JSON、过滤后的日志片段保留查询时状态。所有十四条 PR 的最终回执均已逐条核对，不仅依据标签判断。

原始日志和分段尾部仅保存在 `D:/workspace/archives/20261020-gate-check-034956Z/`，没有把完整环境输出放入归档仓。检查前 Git 标签为 `backup/gate-result-check-20261020`，指向 `d9a2e484af204003708c51cec1cae40309c61605`。归档提交保留 Smillick DCO，并同步既有 GitHub 分支。
