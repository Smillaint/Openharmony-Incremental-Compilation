# 静态检查修订与巡检停止（2026-10-16）

自动任务 `openharmony-30` 已设为 `PAUSED`，停止每 30 分钟巡检。最后一次自动读取为 07:48 UTC，10 条未完成 PR 的 HEAD、回执和状态没有变化；13 条通过项未重复查询。随后的一次性检视者核对与源码修订见下。

## 源码修改与发布

修改前，两个源码仓及主归档仓均创建 `backup/codecheck-fixes-20261016` 标签。

| PR | 文件及修改 | 作用 | 新提交 |
| --- | --- | --- | --- |
| [interface_sdk-js #36540](https://gitcode.com/openharmony/interface_sdk-js/merge_requests/36540) | `process_internal.py`、`remove_internal.py`：在 `finally` 中直接调用 `shutil.rmtree(staging_path)`。 | 原代码已经通过辅助函数清理临时目录；将清理放到创建目录的同一函数中，便于静态检查识别。保持未变化输出、发布失败回滚及备份清理逻辑。 | `7b42242e2fec2fba4fd33b469d8bbf0bf49ab209` |
| [developtools_ace_ets2bundle #7210](https://gitcode.com/openharmony/developtools_ace_ets2bundle/merge_requests/7210) | `sdk_files.py`：使用 `PurePosixPath` 构造 GN 输入路径，替代字符串相加。 | 对应 `G.FIO.05` 告警，保留 GN 的 `//` 前缀和正斜杠语义；清单内容与原实现一致。 | `e76639ebbd94be09cd2038c9ae377dfca1724333` |

两个提交均包含 `Signed-off-by: Smillick <3185479846@qq.com>`，通过已有独立远程发布仓正常推送到原分支。推送前核对远端旧提交和祖先关系，推送后通过 `ls-remote` 及公开 PR API 回读提交。没有强推、创建新 PR 或修改已确认的 PR 正文。

SDK 分支为 `fix/sdk-interface-incremental-20261015`；ace 远端分支为 `fix/incremental-build-20261013`，本地整理分支为 `fix/sdk-helpers-companion-20261015`。

## 验证及剩余问题

执行 `python -B D:/workspace/archives/20261016-codecheck-fixes/verify_fixes.py`，11 项检查通过：两个 SDK 脚本分别覆盖无变化时间戳、输入增删、缺失输出恢复、depfile、生成失败清理、发布失败回滚；插件与 wrapper 清单覆盖双斜杠、空格、中文路径、新旧实现字节一致及文件时间戳稳定；三个修改文件通过 UTF-8 解析和 `git diff --check`。

本轮没有运行远程产品构建或重新触发社区门禁，不能将本地检查当作 CodeCheck 已通过。原两组门禁的失败回执对应旧提交，不适用于此次新提交。

- 安装组剩余 10 条 `WordsTool.110 Intent` 均命中已有 `insight-intent` 源文件及输出路径。清单条目保留，需仓库维护者确认误报或按既有规则处理；没有重命名源码或删除必需输入输出。
- SA #6965 维持原 EcoTest HTTP 500 提交失败，见[原诊断](evidence/20261015-companion-prs/monitor/20261016T031827Z/summary.md)。
- HAP #6974 / packing_tool #1556 维持原归档超时及迟到结果回写失败，编译和三项冒烟已成功，见[时间线](evidence/20261015-companion-prs/monitor/20261016T054826Z/summary.md)。
- build #7048 和 airscan #22 仍没有当前提交的启动回执。

## 已通过且检视者包含 ringking0 的 PR

公开 PR API 的 `assignees` 字段包含 ringking0，五条均保持编译、静态检查和冒烟成功标签，当前为 `waiting_for_review`。其 `accept=false`，不能将名单中的出现视为已经批准合入。

| 修复 | PR |
| --- | --- |
| IDL 输出声明 | https://gitcode.com/openharmony/build/merge_requests/6982 |
| loader / components.json | https://gitcode.com/openharmony/build/merge_requests/7134 |
| 包校验输入 | https://gitcode.com/openharmony/build/merge_requests/6999 |
| NOTICE 收集 | https://gitcode.com/openharmony/build/merge_requests/7009 |
| HiSysEvent 输入 | https://gitcode.com/openharmony/build/merge_requests/7006 |

## 保存位置

- [验证脚本与结果、检视者快照、PR 提交回读](evidence/20261016-codecheck-fixes/)。
- [两个仓库的补丁、增量 bundle 和版本清单](../patches/20261016-codecheck-fixes/)。bundle 依赖清单中 `before` 提交的历史，并非完整克隆。
- 本地源码：`D:/workspace/repositories/companion-prs-20261015/interface_sdk-js` 和 `D:/workspace/repositories/companion-prs-20261015/developtools_ace_ets2bundle`。
- 本地操作归档：`D:/workspace/archives/20261016-codecheck-fixes/`。
- 远程发布备份：`/srv/workspace/patch_backups/20261016_codecheck_fixes/`。

## 10 月 18 日复核

本地日期为 America/Los_Angeles 的 2026-10-18，API 时间为 2026-10-19 UTC，北京门禁回执为 10 月 19 日。23 条 PR 全部回读当前 HEAD 和标签，16 条门禁通过、均未合入；另外五条属于重新启动的 SDK/安装联合组，NOTICE #7048 与 airscan #22 当前版本尚无门禁结果。

- SA #6965 已通过上次重跑，最终回执 `194192597`，北京时间 10 月 16 日 17:08:36。
- HAP #6974 / packing_tool #1556 已通过同一次联合重跑，最终回执 `194225803` / `194225794`，北京时间 10 月 16 日 19:40。
- SDK 与 ace 的原代码告警已在 10 月 16 日提交 `7b42242e` / `e76639eb` 修订。本轮再次核对本地与远端提交，11 项本地回归通过，没有追加源码变更。
- 安装组旧报告的 10 条 `WordsTool.110 Intent` 命中五个既有源文件和对应 JS 输出。源文件与合并适配的主干 `5444f03da530ddee9e2441084a577180e2d7bc50` 的 blob 完全相同，见路径及对象证据。清单保留完整的具体文件声明，需按既有功能术语确认误报。
- 两条 `static-check` 最终分别返回：SDK `194414436` 为 pass，ace `194414463` 为 noPass。独立检查不代替完整门禁。
- SDK、安装组随后各发起一次完整联合门禁：SDK `6ad56fa064650f998bfb70a8`；安装 `6ad56fc464650f998bfb7be7`。均收到机器人启动回执；SDK 两仓 CodeCheck 通过，接口检查、编译与冒烟仍需最终回执。安装组三仓中 build 和 graphic_3d 的 CodeCheck 通过，ace 只剩 10 条 `WordsTool.110`，`G.FIO.05` 已消除。不能把这五条计为完整门禁通过。

回读、命令与启动回执、本地回归、路径证据见 [10 月 18 日证据](evidence/20261018-gate-fixes/)。自动巡检保持 PAUSED。

### ace #7210 追加排查

安装组本轮已经结束。[最终门禁报告](https://dcp.openharmony.cn/workbench/cicd/detail/6ad56fc464650f998bfb7be7/runlist)由机器人在北京时间 2026-10-19 09:22:42 回写，评论 `194414993` 明确为“代码门禁未通过”。当前 ace HEAD 仍为 `e76639ebbd94be09cd2038c9ae377dfca1724333`。build #7046 和 graphic_graphic_3d #676 的 CodeCheck 通过，但联合组因 ace 被拦，不能计为完整门禁通过；报告中的编译项为 pending，并非仍在编译。

[当前 CodeCheck 详情](https://dcp.openharmony.cn/workbench/cicd/detail/6ad56fc464650f998bfb7be7/runlist?pop=codecheck&taskId=MR_1c8b3a201d4a4cca8e4d87a7503297b9)只有 10 条一般级别的 `WordsTool.110 Intent`，没有致命或严重问题，也没有之前的 `G.FIO.05`。十条均位于 `arkui-plugins/sdk_files.json`：输入行 23、40、759、760、761，输出行 1099、1116、1522、1523、1524。

这些行声明现有五个 TypeScript 文件和对应的五个 JavaScript 输出。清单将真实文件名显式列入 GN 依赖，词检查因其中的 `insight-intent` 报告术语告警。五个源文件与合并适配的主干 `5444f03da530ddee9e2441084a577180e2d7bc50` 的 Git blob 相同，PR 没有引入这项功能或修改其命名。应对这十条申请既有术语的误报审核；源码改名、删减输入输出、转义字符串或关闭扫描都不适合作为本次增量修复。

DCP 当前处于未登录状态，报告未显示可用的告警处置入口。没有提交忽略操作或新的门禁命令，源码和 PR 描述均未修改。下文是可交给维护者的说明草稿，尚未发送：

> `sdk_files.json` 中这 10 条 `WordsTool.110 Intent` 告警来自现有 `insight-intent` 文件名，分别是 5 个 TS 输入和对应的 5 个 JS 输出。源码文件和主干版本一致，这次只是把它们列为明确的 GN 输入输出。请审核这 10 条既有文件名告警，确认后按误报处理，清单中的真实依赖需要保留。

证据：[最新 PR 与评论快照](evidence/20261018-gate-fixes/ace-followup-latest.json)、[最终结果与十条位置](evidence/20261018-gate-fixes/ace-followup-summary.json)、[主干对象对照](evidence/20261018-gate-fixes/intent-filename-evidence.json)、[CodeCheck 页面截图](evidence/20261018-gate-fixes/ace-followup-codecheck.png)。归档前版本保存在 `backup/ace-static-followup-20261018`。
