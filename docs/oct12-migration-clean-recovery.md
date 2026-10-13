# 10 月 12 日源码迁移与 clean 恢复验证

## 阶段变更（10 月 13 日）

当前工作入口为 [纯迁移验收](oct13-migration-only-validation.md)。本页记录的是迁移与新增修复混合期间的实验，新增修复已保存并从远程当前工作树分离。以下局部回归结果仅适用于分离前版本，不能作为纯迁移或完整系统编译成功的证据。

混合版本第一次完整编译在 JS snapshot 的两项单测失败后退出；第二次在核对历史命令时主动中断。这两次使用了额外的 `--ccache` 且未保留 `--ninja-args=-dexplain`，不纳入历史命令下的耗时对比。当前纯迁移编译恢复使用 `bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain`。

## 源码与版本边界

- 旧基线：`openharmony_master_default_20260906175718_huawei_10dfe505f/code`。
- 新基线：`openharmony_master_default_20261012175945_huawei_3f7104f86/code`。
- 远程绝对路径前缀为 `/srv/workspace/`。
- 迁移前保存各仓 HEAD、工作树差异、临时索引快照和增量 Git bundle。原有 package-lock 与 iptables C 文件修改不属于本轮补丁。
- 远程备份与日志：`/srv/workspace/patch_backups/20261012_migration_clean/`。
- 本地工作材料：`D:/workspace/archives/20261012-migration/`。

迁移采用旧仓 HEAD、旧仓工作树、新仓工作树三方比较。没有整体覆盖新源码。SELinux 输出条件已被新上游修正，因此保留上游实现；airscan 保留新上游全部八个补丁，包括新增的事件循环互斥修复。

本轮尚未发布新的 GitCode PR。原始十项与历史 PR 的对应关系继续以 [十项修复交接](original-ten-actions-completion-20260910.md) 为准，不能将本轮新增修复写成历史 PR 已包含或已合入。

## 本轮新增修复

| 仓库 / 文件 | 原因与修改 | 作用 |
| --- | --- | --- |
| `build/config/components/idl_tool/idl.gni` | 补齐 client 头文件输出；声明 depfile；支持调用方传入同部件生成依赖，保留定制 GN 的 external_deps 规则 | 输出明确到文件，IDL 工具及共享类型的生成顺序可追踪 |
| `build/config/components/idl_tool/idl.py` | 在 out 内临时目录生成；全部声明输出校验成功后按内容发布；只发布当前目标声明的文件；递归记录 import 与工具文件依赖 | 删除输出后能恢复，失败时保留旧输出，重复生成不改写相同文件，多个目标不争写共享文件 |
| `base/account/os_account/.../osaccount/native/BUILD.gn` | 声明 DomainAccount 回调及公共类型的七个输出 | clean 后账户接口的头文件、Proxy/Stub 和类型文件有明确生成方 |
| `base/inputmethod/imf/.../inputmethod_controller/BUILD.gn` | 声明 `InputMethodClientTypes.idl` 对应的两个输出 | 输入法公共类型缺失时能触发 IDL 目标 |
| `base/security/dlp_permission_service/.../dlp_permission/BUILD.gn` | 声明 `DlpPermissionTypes.idl` 对应的两个输出 | 补齐 DLP 类型文件依赖链 |
| `foundation/ability/dmsfwk/.../common/BUILD.gn` | 声明 `DeviceConnectStatus.idl` 对应的两个输出 | 分布式能力公共类型纳入输出和消费者源文件集合 |
| `foundation/multimedia/audio_framework/services/audio_service/idl/BUILD.gn` | callback 生成目标依赖已有 interface 生成目标，共享 AudioServiceTypes 仅由后者发布 | 消除共享文件的重复生成方，保证删除后先恢复类型文件 |
| `build/hb/services/loader.py` | components JSON 合并不再先删除文件，写入启用 `check_changes=True` | 保留可比较的上轮结果，内容相同时维持 mtime；文件缺失时仍正常重建 |
| `third_party/jsframework/js_framework_build.sh` | 独立编译只清理 out 中的 runtime/src；npm 回退在 out 执行；输出路径绝对化；分别检查构建和单测子进程退出码 | 不再删除源码 runtime，避免 npm 生成物落入源码，防止失败被后台 wait 吞掉 |

IDL 的递归输入使用 depfile 中的具体文件路径。`sources_callback`、`sources_common` 是生成文件命名声明，不应简单与每个 primary IDL 的目录做笛卡尔积；多源目录及相对 import 会因此产生不存在的输入。原始 IDL 文件保留在显式 inputs，导入文件按真实 import 递归解析。

HB 的一次性命令参数缓存仍按原生命周期清理。不能为了保持时间戳而保留已经消费的命令参数，否则下一轮可能继承旧参数。本轮修正的是应持续存在的 components 构建元数据。

## 迁移保留的既有修复

- packages 十项：SA 元数据/二进制、NOTICE、HiSysEvent、seccomp/字段校验、host symlink、parts 安装信息与 modules 安装依赖。
- 构建输入稳定化：loader、部件元数据、host 信息、JSON 比较写入。
- 生成与打包：SDK/声明文件、静态 ABC、HAP 签名与打包、packing_tool ZIP 时间戳、iptables genInit。
- 空跑与 clean：airscan 在 out 应用八个补丁、34 个明确输出；摄像头配置 C/H 放到 out；ramdisk 输出与内核模块发布稳定化。
- 新增 Python Action `generate_host_info.py`、`stabilize_json_file.py` 保留可执行位。

新上游 SDK/npm 链仍有目录输出和源码内生成的既有设计，尤其是 libarkts。当前验证不能证明这些模板已经全部符合文件级输出约束；本轮 IDL、airscan 和摄像头生成链的验证不能外推为整个 OpenHarmony 的所有生成器均已治理。

## 验证记录

1. 完整删除新仓旧 `out` 前，保存原 args、构建日志和 Ninja 日志。旧输出中还引用预热机路径，不能作为新源码验收依据。
2. `bash ./build.sh -p rk3568 --build-target make_all --build-only-gn` 成功。
3. 真实 IDL 工具逐条检查本配置的 141 个 C++ IDL Action，修正前五处存在未声明文件；修正后声明文件均生成成功，发布文件中没有未声明输出。
4. IDL、airscan、JSON 共 12 项隔离回归通过，包括内容/mtime 保持、缺失文件恢复、完整生成目录 clean、错误输入保留旧结果。已使用新仓本轮编译出的 IDL 工具复跑通过。
5. JS 路径回归使用模拟 node/npm，覆盖普通/独立编译 × 预置依赖/npm 回退四种组合，每组检查重复运行和输出删除恢复；另检查构建、单测两类失败能传递至父进程。不能把该路径测试表述成真实 JS 单测已通过。
6. 专用 `out/idl_clean_validation` 的真实 GN/Ninja 恢复验证通过：141 个目标、1,560 个明确输出；首次生成成功，无改动重跑无任务；每个目标删除一个输出后自动补回且其余文件 mtime 不变；全部输出连同 IDL 工具删除后自动重建成功。两类恢复后的无改动重跑均为 `no work to do`。该目录独立于主编译。
7. 混合版本整仓编译未通过验收：第一轮失败，第二轮主动中断。对应状态为 `build/full-status.json` 和 `build/full2-status.json`。当前不能沿用 9 月或 10 月 10 日数据作为新仓结果。

混合阶段实际执行过的命令（已停止使用）：

```sh
bash ./build.sh --product-name rk3568 --ccache --build-target make_all
```

原仓 template 测试入口会删除整个 out，并替换构建测试配置，因此没有在主构建并行运行期间直接执行。替代验证使用上述真实 GN、141 个实际 IDL 目标和隔离 clean 回归。设备端服务、IPC 行为与模糊测试不在本轮已执行证据中。

既有七项 SA ZIP 回归也已在新仓通过，覆盖非空/空归档、时钟变化、删除重建、内容变化、元数据映射、权限/顺序/依赖以及失败保留旧结果。

## 补丁与恢复

- [各仓修复提交及文件 SHA-256](../patches/20261012-migration/fix-commits.json)：14 个修改仓、55 个文件；SELinux 沿用上游，未另造修改。
- [真实 Ninja 恢复结果](evidence/20261012-migration/build/idl-ninja/status.json)。其中耗时是与主构建并行时的局部验证时间，不是系统增量耗时。
- [新仓 IDL 工具与回归退出码](evidence/20261012-migration/regression-tool.json)。
- [SA 七项回归](evidence/20261012-migration/sa-binary-regression.log)。
- 修复分支：各远程源码仓的 `fix/incremental-clean-20261012`，基于各自新仓 HEAD。原工作树 HEAD 与真实索引未切换。
- 增量恢复 bundle：本地 `D:/workspace/archives/20261012-migration/delivery/<仓名>/fix.bundle`。每份 bundle 已在其对应远程仓验证；恢复时需要清单记录的基线 HEAD。
- 提交前已运行各仓 `git diff --check`、修改 Python 的语法编译及 Shell 的 `bash -n`。

## 接续入口

- 主构建状态：远程备份目录下 `build/full-status.json`。
- 主构建日志：`build/full-console.log`。
- IDL 恢复状态：`build/idl-ninja/status.json`。
- 源码生成对照：`idl-graph-final.json`。
- 隔离回归：`regression-results.json`、`regression-tool.json`、`js-path-regression.json`。

以上路径保留混合阶段证据。当前编译状态改读 `migration-only/validation/status.json`；先确认纯迁移整仓编译成功，再恢复新增修复。`out/rk3568/error.log` 可能残留早先失败记录，不能仅凭其存在判定最新构建失败。
