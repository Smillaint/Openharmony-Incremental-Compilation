# OpenHarmony 增量编译项目交接说明（2026-08-19）

本文记录 2026-08-19 的最新验证结果和后续工作。历史迁移、SSH、GitCode 身份、提交与门禁流程继续参考：

```text
docs/incremental-build-handoff-20260817.md
```

本文件中的状态以 2026-08-16 整仓快照及 2026-08-19 最近两轮成功构建为准；如果与旧文档中的 Action 完成数量冲突，以本文件为准。

## 1. 当前验证环境

代码根目录：

```text
/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code
```

最近一次两轮验证日志目录：

```text
/srv/workspace/action_incremental_logs_20260819/ets2bundle_pr7061
```

关键日志：

```text
first_console.log
first_build.log
first_error.log
first_ninja.log
second_console.log
second_build.log
second_error.log
second_ninja.log
```

验证结果：

```text
第一轮 BUILD_STATUS=0
第二轮 BUILD_STATUS=0
```

当前整仓已经可以完成两轮 `rk3568 make_all`。需要注意：构建成功只表示代码和构建图能够正常执行，不表示所有增量 Action 已经收敛。

## 2. 2026-08-19 新增验证结论

### 2.1 ArkUI Action stamp 输出

仓库：

```text
foundation/arkui/ace_engine
```

本地验证分支：

```text
fix-arkui-action-stamp-outputs
```

验证基线：

```text
b068567780699adad607b923cbd0dd29a259af3b
```

处理内容：

- 将相关 Action 的声明输出调整为真实生成的 `*_output.stamp`；
- 删除错误声明的 ui2abc 目录输出；
- 在 `annotate.py` 中将 stamp 路径转换为绝对路径，避免工作目录差异导致输出落到错误位置。

验证结果：

- 第一轮构建成功；
- `runtime_annotate`、`arkoala_annotate` 和 `arkoala_process` 的真实 stamp 均已生成；
- 后续两轮构建中，上述三个 Action 均未重复执行；
- `components_compile_abc` 仍执行，但其上游是 `libarkts`、SDK 打包链，不属于上述 stamp 输出问题。

官方方案参考：

```text
https://gitcode.com/openharmony/arkui_ace_engine/pull/88500
```

官方 PR 同样处理了 `os.path.abspath` 路径问题，并补充输入声明。当前本地方案已经构建成功且解决目标 Action 的重复执行，因此暂不继续扩大 ArkUI 修改范围。

### 2.2 `install_arkguard_tsc_declgen` depfile

仓库：

```text
developtools/ace_ets2bundle
```

本地验证分支：

```text
codex/fix-install-arkguard-tsc-declgen-depfile
```

验证基线：

```text
64da29e2cc1618a8d747bafc562d835c420704d7
```

参考 PR：

```text
https://gitcode.com/openharmony/developtools_ace_ets2bundle/pull/7061
```

按要求只采用以下两个文件中的修改：

```text
BUILD.gn
install_arkguard_tsc_declgen.py
```

明确没有采用：

```text
ets1.2/libarkts/BUILD.gn
ets1.2/libarkts/gn/command/copy_libs.py
```

验证结果：

- 第一轮 `install_arkguard_tsc_declgen` 正常执行；
- 生成了 `out/rk3568/gen/developtools/ace_ets2bundle/install_arkguard_tsc_declgen.d`；
- 第二轮构建中 `install_arkguard_tsc_declgen` 未重复执行；
- 两轮完整构建均成功。

`components_compile_abc` 在第二轮仍执行，其链路为：

```text
libarkts:compile
  -> libarkts_sdk_copy
  -> ohos_ets_libarkts_pack
  -> ohos_ets_libarkts.stamp
  -> SDK bundles
  -> components_compile_abc
```

该问题不属于本次允许采用的两个文件范围，不能通过顺带修改已明确排除的 `ets1.2/libarkts` 文件处理。

## 3. 原始十个 packages Action 最新状态

### 3.1 严格统计

以最近两轮成功构建的实际 Action 调度为验收标准：

```text
完全解决：1/10
部分修复：8/10
尚未解决：1/10
```

旧文档中的 `3/10` 是旧代码快照上的历史结论。迁移到 2026-08-16 新基线后，`sa_profile_src_phone` 和 `sa_profile_binary_phone` 再次受到上游脏输入影响并在第二轮执行，因此不能继续计入“完全解决”。相关 SA 修复提交仍在当前 `build` 分支中，并非 Git 迁移遗漏。

### 3.2 明细

| Action | 最近第二轮 | 当前状态 | 说明 |
| --- | --- | --- | --- |
| `sa_profile_src_phone` | 执行 | 部分修复 | 输出稳定化补丁仍在，但新基线的上游输入继续触发 Action |
| `sa_profile_binary_phone` | 执行 | 部分修复 | 输出稳定化可阻断部分下游传播，但 Action 本身仍执行 |
| `phone_sa_profile_install_info` | 未执行 | 完全解决 | Target 仍在 Ninja 图中，最近两轮均保持 clean |
| `check_seccomp_filter_name` | 执行 | 部分修复 | 根因明确且有实验补丁，尚未完成独立正式修复闭环 |
| `process_field_validate` | 执行 | 部分修复 | 需要稳定成功输出并验证失败路径 |
| `collect_notice_files__phone` | 执行 | 部分修复 | NOTICE 输出本身已稳定，仍受 parts 聚合链影响 |
| `generate_host_symlink` | 执行 | 部分修复 | 自身 JSON 可稳定，仍受 host parts 上游影响 |
| `phone_hisysevent_install_info` | 执行 | 部分修复 | 仍受 parts 聚合链影响 |
| `phone_install_modules` | 执行 | 部分修复 | IDL 链已经修复，仍存在其他 `.so`、可执行文件或聚合输入重建 |
| `phone_parts_list` | 执行 | 尚未解决 | 当前关键上游聚合 Action，应优先追踪最早 dirty 节点 |

最近第二轮日志中存在以下实际调度：

```text
ACTION //build/ohos/packages:generate_host_symlink
ACTION //build/ohos/packages:phone_parts_list
ACTION //build/ohos/packages:sa_profile_src_phone
ACTION //build/ohos/packages:sa_profile_binary_phone
ACTION //build/ohos/packages:phone_hisysevent_install_info
ACTION //build/ohos/packages:collect_notice_files__phone
ACTION //build/ohos/packages:phone_install_modules
ACTION //build/ohos/packages:process_field_validate
ACTION //build/ohos/packages:check_seccomp_filter_name
```

`phone_sa_profile_install_info` 没有出现在第一轮和第二轮 console 日志中。其 Ninja Target 和以下产物仍然存在：

```text
packages/phone/sa_profile/sa_install_info.json
packages/phone/sa_profile/merged_sa_profile.zip
obj/build/ohos/packages/phone_sa_profile_install_info.stamp
```

因此它不是被删除或跳过，而是通过稳定输出和 Ninja `restat` 保持 clean。

## 4. 当前 `build` 仓迁移状态

当前组合验证分支仍包含以下提交：

```text
c08d319f83666f1da7affee73a568a437d289cf3  Stabilize SA profile incremental outputs
0008197c18e088abdc43221328c55a99644af1d4  Fix incremental HAP signing outputs
e00d6de2884c1822315f8b44ba8e5b938f0abb70  Fix common IDL output declarations
```

这说明 SA Action 在新基线重复执行不是补丁遗漏，而是尚未解决的上游 dirty 传播。

已经验证的其他修复：

- IDL common 输出声明：两轮构建通过，相关 IDL Action 第二轮不重复执行；
- HAP signing / `compile_app`：稳定声明输出已迁移，仍需与真实上游 HAP 变化区分；
- packing_tool：可重复 ZIP entry 时间方案已迁移；
- ArkUI Action stamp：相关 annotate/process Action 已收敛；
- ace_ets2bundle depfile：`install_arkguard_tsc_declgen` 第二轮已收敛。

## 5. 下一步优先级

### 5.1 第一优先级：`phone_parts_list` 上游

重点追踪链路：

```text
各部件 build_configs
  -> generate_src_installed_info
  -> generate_host_info
  -> gen_binary_installed_info
  -> src_sa_infos_process
  -> merge_all_parts
  -> phone_parts_list
  -> NOTICE / SA / HiSysEvent / packages
```

应从第二轮日志最早的直接 dirty 原因开始，比较输入的 mtime、SHA-256 和 Ninja command hash。不要直接在 `phone_parts_list` 尾端增加跳过逻辑。

### 5.2 第二优先级：SA 两个叶子 Action

在 `phone_parts_list` 上游收敛后重新验证：

```text
sa_profile_src_phone
sa_profile_binary_phone
phone_sa_profile_install_info
```

验收目标是三个 Action 在无源码变化的第二轮均不执行；如果前两个仍执行，再单独查询其 Ninja 直接输入。

### 5.3 可独立整理的小修复

- 从最新上游整理 `check_seccomp_filter_name` 独立 PR；
- 实现并验证 `process_field_validate` 的稳定成功输出和失败路径；
- 分离 `phone_install_modules` 中除 IDL 之外最早重复链接的模块；
- `components_compile_abc` 作为 `libarkts`/SDK 链的独立问题处理，不混入 ace_ets2bundle depfile 补丁。

## 6. 后续验证要求

- 所有文本按 UTF-8 读取和写入；
- 完整构建由操作者手动执行，分析会话只提供命令、读取日志和修改源码；
- 不执行 `git reset --hard`、`git clean` 或递归删除；
- 不覆盖其他子仓和未知工作树修改；
- 不删除真实依赖，不通过空输出或假 stamp 跳过 Action；
- 第一轮成功后必须在不修改源码的情况下执行第二轮；
- 验收同时检查构建状态、Action 行、输出 mtime、SHA-256、depfile 和 `.ninja_log`；
- `BUILD_STATUS=0` 不能单独作为增量修复完成的证据；
- 一个正式 PR 只处理一个根因，不把 ArkUI、ace_ets2bundle、packages 和 validator 修改混在同一提交中。

GitCode 正式提交继续统一使用：

```text
Author: Smillick <3185479846@qq.com>
Committer: Smillick <3185479846@qq.com>
Signed-off-by: Smillick <3185479846@qq.com>
```
