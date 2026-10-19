# #7006 SDK 门禁失败排查（2026-10-18）

[build #7006](https://gitcode.com/openharmony/build/merge_requests/7006) 本轮阻塞在 SDK 的 Koala TypeScript 依赖解析：`@koalaui/build-common/tsconfig.json` 不可解析，报 `TS6053`。没有发现 HiSysEvent 修复引起的报错；先按门禁依赖准备问题保留，不修改 #7006，不重新触发门禁。具体是预置依赖包不完整、安装未完成还是 node_modules 链接异常，公开日志不足以进一步区分。

本地记录日期为 America/Los_Angeles 的 2026-10-18，以下执行时间均为北京时间 2026-10-19。

## 当前提交及门禁

- HEAD：`3dc5695a126e2c9b3de9336ad8a290d2b66c8d29`，本轮没有更新源码。
- 构建基线：`6b6d6533967db07e8e7d40d140fc63d0faabacbd`。
- [门禁任务](https://dcp.openharmony.cn/workbench/cicd/detail/6ad576e764650f998bfeab08/runlist)，关联 Issue #4682，只有 #7006 一个 PR。
- 机器人在 09:47:56 提示旧验证超过 12 小时并自动触发，任务于 09:48:12 调度，10:58:24 结束，最终结果为失败。本轮排查没有发送 `start build`。
- CodeCheck、BundleCheck、部件依赖检查通过；dayu200、hispark_taurus_LiteOS、dayu600_7885 三项冒烟通过。
- 唯一未忽略的编译失败为 `ohos-sdk`。`master_inner_build` 和 `ohos-sdk-codearts-new` 页面标为忽略项，不作为本次修复依据。

通过现有 Edge 门禁页核对任务与 SDK 产物，页面显示失败目标为 `ohos-sdk`，产物为 `Artifacts/ohos-sdk/20261019-1-00249`，补丁文件名对应上述 HEAD。之后读取页面实际请求的公开任务接口，确认了提交、基线和各阶段状态。

## 首个真实报错

[原始构建日志](https://cidownload.openharmony.cn/Artifacts/ohos-sdk/20261019-1-00249/log/build.log.zip)内的 `ditribute_job_client_failed`，第 9457–9481 行：

```text
FAILED: [code=1] clang_x64/obj/developtools/ace_ets2bundle/ets1.2/interop/interop_compile.stamp
> root@ compile:interop .../developtools/ace_ets2bundle/ets1.2
> npm run compile --prefix interop
> tsc -b .
../compat/tsconfig.json(2,16): error TS6053: File '@koalaui/build-common/tsconfig.json' not found.
../common/tsconfig.json(2,16): error TS6053: File '@koalaui/build-common/tsconfig.json' not found.
```

日志包装时间为 10:04:48，内部构建输出时间为 10:04:46。后续 `ELIFECYCLE`、`npm failed`、Ninja 返回 1 和 TBuild 失败均为该错误的传播结果，不是独立根因。日志前面的 Python venv 提示已被脚本忽略，构建继续进入 Ninja，也不是本次退出的直接原因。

普通 `build.log` 只有 87 字节，内容是压缩日志的地址。名为 `build.log.zip` 的产物实际采用 tar 格式，需按文件头识别后读取，不能把解压失败当作门禁根因。

## 与 PR 修改的关系及判断边界

#7006 只有两个文件的差异：

| 文件 | 修改 |
| --- | --- |
| `hb/util/loader/load_ohos_build.py` | 仅为 hisysevent_config 启用 JSON 内容比较，其他部件仍沿用原写入行为。 |
| `ohos/hisysevent/hisysevent_process.py` | 将实际读取的 YAML 加入 depfile；安装信息 JSON 内容不变时保留时间戳。 |

未改 ace、Koala、npm 安装、tsconfig 或 SDK 的依赖准备逻辑。现场错误是 ace 的 interop 编译无法解析已有本地依赖，与上述变更无直接调用关系。

只读核对当时 ace 上游 master：`ets1.2/build-common/tsconfig.json` 存在；interop 的 dependencies、common/compat 的 devDependencies 均声明 `@koalaui/build-common: ../build-common`。这说明上游声明中有该依赖；该检查不是对 CI 工作区 node_modules 实物的检查，也不能替代门禁当次 ace 提交的完整源码快照。

同期对照未取得可用于 A/B 的 SDK 任务：已打开的安装组门禁没有进入 SDK 编译，SA 最近一次任务没有 SDK 构建项。因此没有声称在独立 PR 中复现相同错误。当前判断依据为首个报错、#7006 的精确差异、单 PR 门禁成员和现有上游依赖声明。

进一步处理应由门禁维护者在失败工作区检查 common/compat/interop 所使用的 node_modules 中，`@koalaui/build-common` 是否存在、链接目标是否有效，以及依赖预置包是否与该次 ace 源码匹配。没有在 #7006 中添加绕过 TypeScript 配置或自动安装依赖的改动。

## 保存记录

- [任务、PR、diff、上游核对和日志节选](evidence/20261018-pr7006-sdk-gate/)。完整原始归档保存在 `D:/workspace/archives/20261018-7006-gate/`，未将日志中的整段环境变量转存到 GitHub。
- 交接修改前标签：`backup/pr-7006-gate-audit-20261018`，对应 `6814348`。
- 自动巡检仍暂停；检视回复草稿没有修改或发送，未标记讨论已解决。

本轮只进行只读故障定位，没有产品源码修订，也没有运行新的产品编译。源码保留已有 DCO 提交，#7006 当前完整门禁状态应记录为 SDK 依赖失败，不能继续沿用 8 月旧任务的通过状态。
