# 规范性修复恢复与实际编译验证

## 当前状态

2026-10-13（America/Los_Angeles）在主工作仓恢复此前保存的规范性修复，再修正实际编译暴露的 JS/CSS 依赖问题。远程日志使用 UTC，日期为 2026-10-14。raw 原始对照仓保持原样。

**attempt5 全量成功，随后三轮增量均成功；首轮 phone_install_modules 仍执行一次，后两轮原始十项均未执行。继续修复首轮 ROFS 重链后，attempt6 已从空 out 启动全量，且源码内两个旧 SDK 生成目录也已移走；该最终版本的全量和增量结果仍待取得。** 每次 GN 失败后的主仓 out 均移动到独立归档，再从空 out 执行原产品命令。没有关闭 GN 依赖检查或修改产品参数。

## 本轮补充修改

| 仓库与文件 | 原因与修复 |
| --- | --- |
| jsframework：js_framework_build.sh | 源码 runtime/src 是 CSS 源码链接，GN 的复制结果可能是同源硬链接；原 cp -r -L 会把文件复制到自身并失败。普通构建仅复制 runtime 其余入口，保留 CSS 目标生成的 out/runtime/src；独立构建仍从 innerkit 副本复制。 |
| jsframework：BUILD.gn | 给 CSS 参数明确路径，补齐 9 个具体 CSS 输入；普通构建通过 external_deps 直接依赖两个生产者。 |
| css-what：BUILD.gn、bundle.json | 保留原 css_what_sources innerkit 及目录布局；fixture 目标使用 ohos_copy 并登记为 innerkit，声明两个具体文件输出。原主目标通过私有 deps 保证打包时包含 fixture；跨组件消费者直接引用公开目标，避免不合法 public_deps。 |
| build：ohos/packages/BUILD.gn | 将安装脚本实际读取的 arm64e 白名单与 categorized-libraries.json 补入 sources，确保规则变化会触发重新安装。 |
| graphic_3d：lume/LumeEngine/tools/CompilerAsset.sh | 在构建工作目录中隔离生成 ROFS 对象，校验实际输出后按内容发布；相同内容保留时间戳，避免无变化重链继而触发安装；缺失目录/文件可恢复，失败保留旧对象。 |

以上是在已恢复的 IDL 输出声明、out 内生成、JSON 稳定写入、SDK 文件清单与复制修复之上追加的 4 仓 6 文件修改，未新建 GitCode PR。前序变更见 [规范性修复](oct13-phone-audit-clean-recovery.md) 与 [GN 文件清单兼容](oct13-gn-sdk-manifest-repair.md)。

## 已完成检查

- JS 隔离回归覆盖旧同文件复制失败、普通/独立与 prebuilts/npm fallback 四组合、重复发布的 mtime、输出删除后恢复、缺失源码 CSS 链接、构建及测试失败传播；结果见 [回归记录](evidence/20261013-phone-norm-validation/js-css-regression.json)。
- 使用真实 Node/Babel/测试依赖运行 JS 构建，退出码 0，43 项单元测试通过；CSS 源码内容与 mtime 均未变化。现有 lint 日志仍有报错，不能将此次结果表述为 lint 通过。记录见 [真实 JS 构建](evidence/20261013-phone-norm-validation/js-real-build-status.json)。
- 真实 IDL 隔离 Ninja 回归：从本轮 GN 提取 141 条命令，生成 1,560 个输出；不变构建、部分输出删除后恢复、全部输出删除后恢复均通过，恢复后的不变构建均为 no work。源码未变化。使用 raw 仓已构建的同版 IDL 工具，不替代产品 GN 图和消费者编译验收；见 [逐轮记录](evidence/20261013-phone-norm-validation/idl-real-recovery-status.json) 与 [结果](evidence/20261013-phone-norm-validation/idl-real-recovery-passed.json)。
- attempt1 至 attempt4 的 GN 失败分别暴露生成文件可见性和 innerkit 声明约束；attempt5 改为直接 external_deps 后通过 GN；主 Ninja 的 gen_snapshot、ark_jsf、gen_ui_plugins 和 gen_sdk_ts_wrapper 已执行通过。
- 已保存修改前及每轮构建前的 Git 快照，新增 ROFS 仓后覆盖 17 仓，主仓 HEAD 和真实索引没有切换。恢复包内 Git bundle 校验通过。

## 首轮安装重跑的实际根因

[逐轮汇总](evidence/20261013-phone-norm-validation/build-summary.json) 记录 attempt5：

| 阶段 | 完整耗时 | 主 Ninja 任务 | phone_install_modules | 原始十项其余九项 |
| --- | ---: | ---: | ---: | --- |
| 空 out 全量 | 2,107.41 秒 | 125,626 | 1 | 各 1 |
| 增量 1 | 175.60 秒 | 108 | 1 | 均 0 |
| 增量 2 | 84.37 秒 | 13 | 0 | 均 0 |
| 增量 3 | 89.04 秒 | 13 | 0 | 均 0 |

四轮均退出 0，任务序列有效，受控源码未变化。增量 1 没有 C/C++ 编译，但重新链接 libPluginCamPreview、libPluginAGPRender、libPluginAGP3D、libPluginMRT、libPluginDotfield 五个共享库。

Ninja explain 显示 Shader 目标的目录产物被后续生成动作更新时间戳，导致 ROFS 动作执行。旧 CompilerAsset.sh 随后无条件覆盖对象文件，导致五个库重链及 phone_install_modules 重新执行。隔离使用真实 LumeAssetCompiler 重复处理 6 个产品 ROFS，确认对象内容与原产物一致，但旧脚本每次改变 mtime。

新的发布逻辑保留相同对象的 mtime；实际资产内容变化仍会更新对象。6 个真实对象重复、删除文件/目录恢复，以及变更资产、生成失败和未生成声明输出的测试均通过，见 [ROFS 回归](evidence/20261013-phone-norm-validation/rofs-after.json)。只调整构建发布，不修改 Shader、ROFS 格式、插件 UID、API/ABI、安装路径或 GLES/Vulkan 运行时代码。

已读 graphic_3d 的仓级、lume、LumeEngine 指引及渲染资源与插件链路、构建验证地图、提交规则。没有执行设备画面、XTS 或运行时 fuzz；本次以对象字节一致性和完整产品编译验证构建行为。

attempt6 先保存 17 仓 Git 快照，移走未跟踪的 arkui-plugins/lib（266 文件）与 koala-wrapper/build（869 文件），再将完整 out 归档后重新构建，见 [清理记录](evidence/20261013-phone-norm-validation/clean-record.json)。raw 仓未修改。Shader 等既有目录产物声明仍可能导致少量上游动作运行，本次修复确保相同内容不继续触发库重链与安装；不将此表述为全仓所有 Action 都不执行。

## 安装动作验收边界

必须在全量成功后保持源码及参数不变，取得连续两轮 phone_install_modules 不执行的实际增量日志，不能沿用纯迁移版 169.92 秒或旧仓结果。

安装 depfile 仍有历史 HAP/资源目录依赖。不能仅删除目录项或改为一次性枚举后丢失新增/删除文件的触发条件。后续应从真实 Ninja explain 追踪根因，并在必要时联动生产者清单与安装消费关系。

## 构建与状态位置

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```

本轮运行器已启动时不要重复启动上述命令。运行目录由下列文件记录：

```text
/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/phone_norm_validation_20261013/latest-run.txt
```

对应目录的 status.json、runner.log、各阶段 console.log 和 summary.json 保存状态与计数。全量失败即停止；成功后依次执行最多三轮增量，保存原始十项及相关生成动作的次数。确认最终结论还需核对源码未变化和有效任务序列，不能仅依赖运行器结束状态。

## Git 与恢复

[本轮提交及文件清单](../patches/20261013-phone-norm-validation/versions.json) 中 before 是恢复后的规范版（graphic_3d 为未修改的上游 HEAD），after 是 attempt6 构建前快照。各仓 repair.patch 是两者之间的追加差异；cumulative.patch 是当前上游 HEAD 到该快照的完整差异，不能重复叠加使用。

- 远程归档目录：主工作目录旁 phone_norm_validation_20261013/source-delivery-attempt6。
- 本地恢复包：D:\workspace\archives\20261012-migration\source-delivery-attempt6.tar.gz。
- SHA-256：1d7fc7271482b0a2874a75225b4044b33246c76b791789110e3f45e40c03aa8a。
- [完整 17 仓版本](evidence/20261013-phone-norm-validation/all-repository-versions.json)。

A/B 控制器已补齐 17 仓、95 路径，包含新增 CSS bundle.json 与 ROFS 脚本；current 仍是此前缓存的规范版，不包含本轮追加差异；需要恢复本轮版本时使用上述 after 快照与补丁。切换前须停止构建并另存当前状态。
