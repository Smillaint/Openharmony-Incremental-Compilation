# OpenHarmony 增量构建最后一项修复交接（2026-08-25）

## 1. 任务目标

原始跟踪的 10 个增量构建 Action 当前按目标口径为 **9/10**。唯一尚未闭环的原始目标是：

```text
//build/ohos/packages:phone_install_modules
```

本次只处理当前最早、边界清晰的直接原因：

```text
//developtools/ace_ets2bundle/ets1.2/libarkts:panda_sdk__notice
```

对应 Ninja dry-run 报告：

```text
depfile 'clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk__notice.d' is missing
depfile 'clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk_info.d' is missing
```

目标是找出这两个 depfile 在无源码变化的第二轮仍被判缺失的真实原因，做一个符合上游规范的最小修复，使相关 Action 第二轮不再重复执行，同时不破坏其他 toolchain、产品和部件构建。

不要同时处理本文列出的其他缺失输出或 HAP 时间戳问题。一个根因完成定位、修改和验证后停止，由主会话复核。

## 2. 远程环境

Windows 侧工作区：

```text
D:\workspace\Openharmony-Incremental-Compilation
```

SSH：

```powershell
ssh -p 42247 -i C:\Users\31854\.ssh\id_ed25519 -o IdentitiesOnly=yes root@119.3.182.128
```

远程源码根目录：

```text
/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code
```

产品和完整构建入口：

```text
rk3568
./build.sh -p rk3568 --build-target make_all
```

接手者不得自行执行 `build.sh` 或实际 Ninja 构建。完成代码和静态检查后，只提供第一轮编译指令；构建由操作者执行，主会话负责读取日志验收。

允许的只读 Ninja 操作包括：

```text
ninja -t query
ninja -t commands
ninja -t targets
ninja -n -d explain
```

直接执行 Ninja 时必须带 `-n`，工具查询使用 `-t`。禁止把构建命令和 grep 检查命令放在同一段交给操作者复制。

## 3. 当前 Git 状态与保护要求

### 3.1 build 子仓

```text
目录：code/build
分支：incremental-build-all-validation-20260825
HEAD：3dc68b61dd6156d5a5bbe60381b0961e557f3396
```

当前已有两处未提交修改，均已完成对应功能验证，不得覆盖、回退或顺手重构：

```text
M config/components/idl_tool/idl.gni
M ohos/notice/collect_module_notice_file.py
```

`build` 官方上游已在 2026-08-25 刷新到：

```text
gitcode/master
d7e7b9e8954a87233bebc222d66c53364e4c5c18
```

### 3.2 developtools_ace_ets2bundle 子仓

```text
目录：code/developtools/ace_ets2bundle
分支：codex/fix-install-arkguard-tsc-declgen-depfile
HEAD：64da29e2cc1618a8d747bafc562d835c420704d7
```

该子仓也不是干净工作树，已有其他任务修改：

```text
M BUILD.gn
M install_arkguard_tsc_declgen.py
```

这两处修改不属于当前任务，不得覆盖、暂存或提交。当前 panda SDK 定义位于：

```text
developtools/ace_ets2bundle/ets1.2/libarkts/BUILD.gn
```

开始修改前必须：

1. UTF-8 严格读取目标文件；
2. `git status --short --branch` 核对已有修改；
3. fetch `gitcode/master` 并检查最新上游是否已有等价修复；
4. 不切换分支，不 reset，不 clean，不 checkout 覆盖现有工作树；
5. 暂不 commit、不 push，只落最小补丁供主会话复核。

如果修复最终落在 `build` 子仓，也必须避开上述两处未提交文件之外的无关修改；如果必须修改同一文件，先停止并说明冲突，不得自行覆盖。

## 4. 已完成进度

原始 10 个目标中，以下 9 个已有收敛方案或双轮验证证据：

```text
sa_profile_src_phone
sa_profile_binary_phone
phone_sa_profile_install_info
check_seccomp_filter_name
process_field_validate
collect_notice_files__phone
generate_host_symlink
phone_hisysevent_install_info
phone_parts_list
```

尚未收敛：

```text
phone_install_modules
```

最近又消除了 `phone_install_modules` 的两个上游放大源：

1. 连续大写缩写 IDL 接口头文件的 GN 输出名与生成器实际文件名不一致；
2. NOTICE 递归搜索在 `.gn` 边界目录中未检查该目录自身的 `LICENSE`。

NOTICE 边界修复双轮结果：

```text
第一轮：rk3568 build success
第二轮：rk3568 build success
总 ACTION：8450 -> 780
NOTICE ACTION：7527 -> 4
```

原有大量以下错误已经消失：

```text
output NOTICE_FILES/static/... doesn't exist
```

第二轮只剩 4 个 NOTICE 相关 Action：

```text
//developtools/ace_ets2bundle/ets1.2/libarkts:panda_sdk__notice
//build/ohos/packages:stage_notice_files__phone
//build/ohos/packages:collect_notice_files__phone
//build/ohos/packages:merge_system_notice_file_phone
```

后三个是第一个 Action 向 packages 聚合链的传播结果，因此当前先处理 `panda_sdk__notice`，不要直接修改 packages 聚合器。

## 5. 日志与证据位置

IDL 输出名称修复日志：

```text
/srv/workspace/action_incremental_logs_20260825/phone_install_idl_name_fix
```

NOTICE 边界修复日志：

```text
/srv/workspace/action_incremental_logs_20260825/phone_install_notice_boundary_fix
```

NOTICE 目录已保存：

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

当前第二轮直接 dirty 原因来自在构建完成后执行的只读命令：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 \
  -w dupbuild=warn \
  -n -d explain \
  packages/phone/system_install_modules.json
```

其中与本任务直接相关的两行是：

```text
ninja explain: depfile 'clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk__notice.d' is missing
ninja explain: depfile 'clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk_info.d' is missing
```

## 6. 当前规则事实

`developtools/ace_ets2bundle/ets1.2/libarkts/BUILD.gn` 中的主要关系：

```text
action("panda_sdk_run")
  -> 生成 panda_sdk.tgz、sdk 目录和 panda-sdk 目录

ohos_prebuilt_etc("panda_sdk")
  -> source 使用 panda_sdk_run 的第一个输出
  -> install_enable = false
  -> 自动派生 panda_sdk__notice 和 panda_sdk_info
```

生成后的关键 Ninja 输出：

```text
out/rk3568/clang_x64/obj/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk.notice.txt
out/rk3568/clang_x64/obj/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk_module_info.json
```

两者在第二轮后真实存在：

```text
panda_sdk.notice.txt          size=10175
panda_sdk_module_info.json    size=577
```

但对应 depfile 在第二轮后均不存在：

```text
out/rk3568/clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk__notice.d
out/rk3568/clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk_info.d
```

Ninja 中 `panda_sdk__notice` 的实际命令为：

```text
/usr/bin/env ../../build/ohos/notice/collect_module_notice_file.py
  --module-source-dir ../../developtools/ace_ets2bundle/ets1.2/libarkts
  --depfile clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk__notice.d
  --output clang_x64/obj/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk.notice.txt
```

`panda_sdk_info` 的实际生成脚本为：

```text
../../build/templates/metadata/gen_module_info.py
```

它接收：

```text
--output-file clang_x64/obj/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk_module_info.json
--depfile clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk_info.d
```

生成的 Ninja edge 对两个 Action 都明确声明了 `depfile = ...` 和 `restat = 1`。

## 7. 排查顺序

必须从事实验证开始，不要先猜测补丁：

1. 对 `panda_sdk__notice` 和 `panda_sdk_info` 分别执行 `ninja -t query`、`ninja -t commands`，确认输出、命令和 depfile 路径；
2. 阅读 `collect_module_notice_file.py`、`gen_module_info.py` 和 `build_utils.write_depfile`，确认成功路径是否必然写 depfile；
3. 使用 `/tmp` 中的输出和 depfile 参数单独执行脚本功能测试，确认脚本自身能否生成 depfile；这不是构建，不得修改源码产物；
4. 检查 host toolchain 的 `root_build_dir`、`root_out_dir`、`target_gen_dir` 和 rebase 结果，确认是否存在路径基准不一致；
5. 与一个第二轮稳定的 `ohos_prebuilt_etc` host target 对比生成的 Ninja edge；
6. 确认 depfile 是从未生成、生成到错误位置、生成后被工具删除，还是声明方式不符合当前 Ninja 的 depfile 使用规则；
7. 确认 `panda_sdk__notice` 和 `panda_sdk_info` 是同一个模板根因，还是两个独立问题；若不是同根因，本轮只修最早的 `panda_sdk__notice`；
8. 检查最新官方上游是否已经修改 `ohos_prebuilt_etc`、notice 模板、metadata 模板或 panda SDK 定义；优先遵循上游已有模式；
9. 选择责任层最准确的最小修复，不删除真实依赖，不伪造 clean。

建议重点回答：

- 为什么普通 target 的相同模板没有重复，而 host-toolchain 下的 panda SDK 会重复？
- `install_enable = false` 是否与自动派生 notice/info target 的语义冲突？
- `panda_sdk_run` 同时把文件和目录声明为 outputs 是否会影响派生 metadata；此问题若与 depfile 无直接关系，不要顺手修改；
- depfile 是否应该物理保留，还是应由 Ninja deps log 接管；以本仓现有稳定规则为准，不凭经验假设。

## 8. 可使用的只读命令

查看目标：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 -w dupbuild=warn -t query \
  clang_x64/obj/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk.notice.txt
```

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 -w dupbuild=warn -t query \
  clang_x64/obj/developtools/ace_ets2bundle/ets1.2/libarkts/panda_sdk_module_info.json
```

只读检查当前 dirty 原因：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 -w dupbuild=warn -n -d explain \
  packages/phone/system_install_modules.json 2>&1 \
  | grep 'ninja explain:' \
  | grep -v ' is dirty$'
```

检查两轮 Action：

```bash
grep -n -E \
  'ACTION //developtools/ace_ets2bundle/ets1.2/libarkts:panda_sdk__notice|ACTION //build/ohos/packages:(stage_notice_files__phone|collect_notice_files__phone|merge_system_notice_file_phone|phone_install_modules)' \
  /srv/workspace/action_incremental_logs_20260825/phone_install_notice_boundary_fix/second_console.log
```

## 9. 修复约束

- 所有文本按 UTF-8 读取和写入；
- 修复必须具备清晰的变量、函数和文件命名，保持原项目风格；
- 不在 README 或注释中写自动生成、模型生成或按要求修改等描述；
- 不执行 `git reset --hard`、`git clean`、未确认目标的删除或覆盖；
- 不修改已有无关工作树内容；
- 不删除 `deps`、`inputs`、`outputs` 或 depfile 来绕过 Ninja；
- 不使用空安装列表、假 stamp、无条件 touch 或更新时间戳伪造 clean；
- 不把 host-only 特例粗暴扩大到所有产品；
- 不把 panda SDK、其他缺失输出、HAP 时间戳和 camera/kernel 问题混进同一个补丁；
- 不自行执行完整编译，不 commit，不 push。

如果修复需要改变通用 `build` 模板，必须证明：

1. 该模板对所有调用者的语义仍正确；
2. 输出和 depfile 路径在 host/target toolchain 下都正确；
3. 不会使其他部件丢失增量依赖；
4. 有至少一个稳定 target 作为对照；
5. 上游没有更窄、更规范的实现方式。

## 10. 静态验证要求

落补丁后至少完成：

```text
git diff --check
目标 Python 文件 UTF-8 解码
目标 Python 文件 AST/语法检查
GN formatter 只读预览或目标 BUILD.gn 格式检查
脚本级 /tmp 功能测试
与最新 gitcode/master 的差异检查
```

不得为了格式化而改写无关历史代码。不得把功能测试产物写入源码目录。

## 11. 两轮构建验收标准

代码由主会话复核后，操作者执行两轮：

```text
./build.sh -p rk3568 --build-target make_all
```

两轮之间不得修改源码、构建配置和输出目录。每轮必须独立保存：

```text
console.log
build.log
error.log
.ninja_log
```

本根因通过必须同时满足：

1. 两轮均为 `rk3568 build success`；
2. 第二轮不再执行 `panda_sdk__notice`；
3. dry-run 不再报告 `panda_sdk__notice.d` 缺失；
4. 如果同一根因覆盖 `panda_sdk_info.d`，该行也必须消失；否则必须明确拆分为下一问题；
5. 第二轮不新增 GN、Ninja、Python、NOTICE 或 metadata 错误；
6. 已验证的 IDL 和 static NOTICE 修复不得回退；
7. `phone_install_modules` 若仍执行，必须继续报告新的最早直接原因，不能把本子问题通过表述为全部 10/10。

## 12. 接手者交付内容

完成排查和补丁后，只需向主会话提供：

1. 一段准确根因说明；
2. 最新上游比较结果；
3. 修改仓库、文件和精确 diff；
4. 为什么修复位于该责任层；
5. 静态检查和脚本级测试结果；
6. 潜在跨 toolchain、跨产品影响；
7. 一条第一轮完整构建命令及日志目录建议；
8. 明确声明未执行编译、未提交、未推送。

主会话会复核差异、上游一致性、代码规范和两轮日志，再决定是否保留、拆分分支和提交。

## 13. 后续但不属于本轮的问题

当前 dry-run 还暴露以下独立问题，全部暂不处理：

```text
clang_x64/gen/arkcompiler/ets_frontend/ets2panda/consistency_check.stamp 不存在
obj/interface/sdk-js/ohos_base_split.timestamp 不存在
camera vdi tmp.c 不存在
system.cil.sha256 不存在
generate_pcid_build_ext_components.txt 不存在
kernel/checkpoint/compile_check 不存在
部分 HAP js_assets.zip 早于共享 releaseAssets map
systemres_hap__js_assets.d 和 telephonyres_hap__js_assets.d 缺失
```

这些问题只有在 `panda_sdk__notice` 单项完成验证后，才能按新的最早依赖顺序逐个接手。
