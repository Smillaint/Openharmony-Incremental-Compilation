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
