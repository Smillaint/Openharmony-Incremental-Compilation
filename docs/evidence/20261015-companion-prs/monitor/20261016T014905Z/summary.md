# 联合门禁巡检（2026-10-16 01:49 UTC 起）

检查范围为六组 16 条联合门禁 PR，以及原十项 Action 的其他 7 条历史 PR。23 条 PR 的实际 HEAD、评论、状态标签均已读取。仅核对已触发的当前提交，未发送 `start build`，未修改产品源码或合入 PR。

## 本轮结论

| 范围 | 当前结果 | 后续处理 |
| --- | --- | --- |
| SDK split，build #7049 + interface_sdk-js #36540 | CodeCheck 不通过，编译均 pending | 两条临时目录清理告警，原因及建议见下 |
| 安装组，build #7046 + ace #7210 + graphic_3d #676 | ace 的 CodeCheck 不通过，编译均 pending | 十条既有文件名告警、一条 GN 路径告警 |
| IDL、JS/CSS、HAP、loader | 主门禁仍执行中；各自 CodeCheck 均通过 | 保留待查，不把部分构建通过算成整组通过 |
| SA，build #6965 第三轮 | dayu200 编译通过、冒烟失败；整轮尚未结束 | 日志入口提示“未生成日志文件”，需要平台侧日志 |
| build #6999、#7009、#7006、iptables #62 | 当前 HEAD 已有通过记录 | 标记完成，停止后续检查 |
| build #7048、sane-airscan #22 | 未发现当前 HEAD 的启动回执 | 不计入通过或运行，不自动触发 |

所有联合组的实际 HEAD 与提交清单一致。四条历史通过 PR 的提交时间早于最后成功门禁，当前成功标签仍有效且评论中没有后续代码重置或新启动；原始提交信息见 `passed-head-commits.json`。sane-airscan #22 在 2026-10-16 08:10 北京时间发生更新，其八月通过记录不适用于当前提交。

## SDK split：临时目录清理规则

[报告](https://dcp.openharmony.cn/workbench/cicd/detail/6ad17ded64650f998bd4a4d2/runlist?pop=codecheck&taskId=MR_91bd80f2605940f7b49da2cd2637ba71)，机器人失败评论 `194071706` / `194071708`，北京时间 09:38:16。

CodeCheck 返回两条严重级别的 `G.FIO.04 临时文件使用完毕应及时删除`：`process_internal.py:158` 与 `remove_internal.py:82` 的 `tempfile.mkdtemp`。

对应提交 `9e2c44a2cca432c7686c396ab9465ea51c1119da` 中，两处都有 `finally`，分别在 177–179、99–101 行调用 `remove_path(staging_path)`，辅助函数最终执行 `shutil.rmtree`。发布成功时目录被移动为正式输出，变量设为 None。因此现有证据更符合静态分析未跟踪跨函数清理，尚未证明运行时存在目录泄漏。

建议将清理动作在同一函数中显式表达，或使用 `TemporaryDirectory` 管理容器目录、在其内部准备发布子目录；保留内容不变时不改写、发布失败回滚的语义。修订后再申请新一轮门禁。两仓编译尚未执行，本轮不能据此评价编译兼容性。

## 安装组：GN 路径与既有文件名

[报告](https://dcp.openharmony.cn/workbench/cicd/detail/6ad17dfc64650f998bd4ac9f/runlist?pop=codecheck&taskId=MR_9fca7110469543e391477e0ba7e5eb7f)，机器人失败评论 `194071745` / `194071743` / `194071744`，北京时间 09:38:25。

ace 提交 `a9bc178d4d9bcc0f1179f24ef1b620d51537f4d6` 共 11 条一般级别问题：

- `sdk_files.py:168`：`G.FIO.05` 命中 `'//' + p.relative_to(root).as_posix()`。这里生成的是 GN 源码根相对路径，`//` 有明确语义，不能直接替换成随宿主变化的路径分隔符。建议使用明确的 POSIX 路径构造方式并保持双斜杠前缀。
- `arkui-plugins/sdk_files.json`：`WordsTool.110 Intent` 共 10 条，行号为 23、40、759、760、761、1099、1116、1522、1523、1524。全部是 `insight-intent` 的源文件路径及对应 JS 输出路径；父提交已经存在这些源码文件，不是新增业务命名。建议由仓库维护者确认误报或按项目已有规则豁免，不应删除必需输入输出项或重命名现有源码以躲过扫描。

build、graphic_3d 的静态检查通过。三仓联合编译均未开始，失败发生在静态检查阶段。

## SA 第三轮：dayu200 冒烟缺少日志

[当前报告](https://dcp.openharmony.cn/workbench/cicd/detail/6ad165ef64650f998bcd430a/runlist)，启动回执 `194060838`，对应 `f15f9bded74ae12a75b8a9ef729c1397a7202ec2`。

dayu200 的编译和 InnerApi 检查通过，但冒烟为失败；点击失败项，页面提示“未生成日志文件”。dayu600 与 LiteOS 冒烟通过，mac-sdk 编译通过；x86_64_virt_tdd 与 dayu200_tdd 尚在执行。不能沿用上轮 dayu600 EcoTest 超时或 mac 清理错误解释这一轮的新失败。

当前没有首个测试错误可供定位，原因暂不能归为源码或环境。建议向平台维护者提供上面的 CI 编号，请其补查 dayu200 的测试任务、设备执行及日志/结果回传记录。未自动重试。

## 未形成可操作结论的子任务

IDL 的 new_part_compile / part_compile、JS/CSS 的 part_compile 显示耗时 0、失败、阶段均为空；IDL 失败项点击后未返回日志。保留为待查子状态，不根据零耗时断言环境问题。主门禁仍在运行。平台明确标注“失败(忽略)”的 master_inner_build、CodeArts 等分支不按阻断失败报告。

## 证据与后续巡检

- `github-gitcode-status.json`：23 条 GitCode PR 的只读 API 快照（文件名沿用读取脚本命名，内容来自 GitCode）。
- `primary-comments-final.json`：收尾时 7 个主入口的最新机器人评论。
- `sdk-codecheck-problems.txt`、`ace-codecheck-problems.txt`、对应 PNG：静态规则、文件、行号与页面证据。
- `codecheck-source-evidence.txt`：清理逻辑、GN 路径构造与父提交既有文件名的源码证据。
- `*-run.txt` / `idl-run-later.txt`：各组 DCP 页面状态；`sa-dayu200-log-unavailable.txt` 保存日志入口返回信息。
- `before-state.json`、`after-state.json`：巡检前后状态；全局状态在 `../../monitor-state.json`。

本轮新增失败指纹已记录。相同提交、相同规则或相同缺日志状态后续不重复通知；等待新日志、结果变化或修订提交对应的新门禁。没有重新触发门禁，没有合入 PR。四条已通过项停止检查；尚未达到全部完成条件，30 分钟巡检继续。
