# OpenHarmony 增量构建最后一项修复交接（2026-08-28）

## 1. 任务目标

原始跟踪的 10 个增量构建 Action 当前严格口径仍为 **9/10**。唯一尚未闭环的原始目标是：

```text
//build/ohos/packages:phone_install_modules
```

截至 2026-08-28，已经沿该目标的真实输入链消除了多层上游无效重建。最近完成双轮验证的子根因是：

```text
//interface/sdk-js:ohos_base_split
```

该 Action 原来声明：

```text
out/rk3568/obj/interface/sdk-js/ohos_base_split.timestamp
```

但 `parse_interface_sdk.py` 不创建这个输出，同时 Action 没有足够的文件级输入描述。缺失输出使 Ninja 每轮执行 `ohos_base_split`，并经 SDK 声明、ArkUI 代码生成、CXX 和 SOLINK 链最终带动 `phone_install_modules`。

本轮已经为 `ohos_base_split` 补齐稳定 stamp 和运行时 depfile。两轮真实构建证明该 Action 第二轮不再执行，stamp 和 depfile 均保持稳定。但 `phone_install_modules` 仍由下一层重复 Action 带动：

```text
//interface/sdk-js:ohos_declaration_ets2
  -> //foundation/arkui/ace_engine/.../arkoala_generator:patch_sdk
  -> //foundation/arkui/ace_engine/.../arkoala_generator:runner_gen_code
  -> CXX / SOLINK
  -> //build/ohos/packages:phone_install_modules
```

因此：

- `ohos_base_split` 子根因已经闭环；
- `phone_install_modules` 尚未闭环；
- 当前不能写成 10/10；
- 下一步只处理 `ohos_declaration_ets2` 的最早直接原因，不直接修改 packages 尾端 Action。

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

接手者不得自行执行 `build.sh`、真实 Ninja 构建或后台构建。完成代码修改和静态检查后，只提供第一轮编译指令；真实构建由操作者执行，主会话负责读取日志并决定是否进入第二轮。

允许的只读 Ninja 操作：

```text
ninja -t query
ninja -t commands
ninja -t targets
ninja -n -d explain
```

直接调用 Ninja 时必须使用 `-t` 工具模式或带 `-n`。禁止执行没有 `-n` 的目标构建。禁止把真实构建命令、grep、dry-run 和清理命令放在同一段交给操作者复制。

## 3. 当前 Git 状态与保护要求

### 3.1 build 子仓

```text
目录：code/build
分支：incremental-build-all-validation-20260825
HEAD：3dc68b61dd6156d5a5bbe60381b0961e557f3396
本地 gitcode/master 引用：b8854b92ab32b0509372543228026b61554c728a
```

当前工作树：

```text
M config/components/idl_tool/idl.gni
M ohos/common/binary_install_info.py
M ohos/notice/collect_module_notice_file.py
M ohos/notice/collect_system_notice_files.py
M ohos/packages/modules_install.py
M ohos/sdk/parse_interface_sdk.py
```

这些修改分别属于已经定位或已经验证的增量构建子问题，不得覆盖、回退、混合格式化或顺手重构。

当前各文件作用：

| 文件 | 修复目的 | 当前状态 |
|---|---|---|
| `config/components/idl_tool/idl.gni` | 使连续大写缩写 IDL 的 GN 输出名与生成器真实头文件名一致 | 已有双轮验证证据，保护 |
| `ohos/common/binary_install_info.py` | 使用 `check_changes=True`，内容不变时不重写安装信息 JSON | 已验证输出稳定，保护 |
| `ohos/notice/collect_module_notice_file.py` | 在 `.gn` 边界目录返回前先检查目录自身 LICENSE | 已有双轮验证证据，保护 |
| `ohos/notice/collect_system_notice_files.py` | 不把已复制 NOTICE 文件全部扩入聚合 depfile | 已验证 NOTICE 聚合链收敛，保护 |
| `ohos/packages/modules_install.py` | 正确过滤 SA 文件，避免 `extend` 将原列表再次追加 | 已验证 depfile 中对应 SA 条目消失，保护 |
| `ohos/sdk/parse_interface_sdk.py` | 为 `ohos_base_split` 写运行时 depfile 和稳定 stamp | 2026-08-28 双轮验证通过，保护 |

### 3.2 interface_sdk-js 子仓

```text
目录：code/interface/sdk-js
状态：detached HEAD
HEAD：0d4497963c7800c067ae4d420c7738db147a0e25
本地 gitcode/master 引用：5205a3c09d9f83bbfc6f32ba54d66c8f991a7cd5
```

当前工作树：

```text
M BUILD.gn
```

该修改为 `ohos_base_split` 增加：

```text
--stamp
--depfile
depfile = "${target_out_dir}/${target_name}.d"
```

该子仓目前是 detached HEAD。后续需要提交时，必须先按操作者指定的名称创建不含 `codex` 的新分支；未经指示不要自行建分支、commit 或 push。

### 3.3 developtools_ace_ets2bundle 子仓

```text
目录：code/developtools/ace_ets2bundle
分支：codex/fix-install-arkguard-tsc-declgen-depfile
HEAD：64da29e2cc1618a8d747bafc562d835c420704d7
本地 gitcode/master 引用：cf6a916d83232b975b88d21e389c29b299dece20
```

当前工作树：

```text
M BUILD.gn
M ets1.2/BUILD.gn
M ets1.2/libarkts/BUILD.gn
M install_arkguard_tsc_declgen.py
```

这些修改涵盖 ArkGuard/TypeScript/Declgen depfile、libarkts SDK 输出目录隔离和更精确的输入声明。它们属于前序已验证子问题，不得覆盖、暂存到其他仓的提交或为了当前 SDK 声明问题而重构。

### 3.4 通用保护要求

开始任何修改前必须：

1. 使用 UTF-8 严格读取目标文本；
2. 执行 `git status --short --branch` 核对已有修改；
3. 检查最新上游是否已有等价修复；
4. 不执行 `git reset --hard`、`git clean` 或覆盖已有工作树的 checkout；
5. 不提交、不推送，直到主会话完成双轮复核且操作者明确要求；
6. 最终提交必须按仓库拆分，使用 `git commit -s` 保留 DCO `Signed-off-by`，不得把多个子仓混成一个提交。

## 4. 已完成进度

### 4.1 原始 10 个目标

以下 9 个原始目标已有收敛方案或双轮验证证据：

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

严格进度仍为：

```text
9/10
```

### 4.2 `phone_install_modules` 已消除的上游放大源

目前已经处理或验证过的子问题包括：

1. 连续大写缩写 IDL 输出名与真实生成文件名不一致；
2. NOTICE `.gn` 边界目录没有检查目录自身 LICENSE；
3. panda SDK NOTICE/metadata 的 host-toolchain depfile 问题；
4. ArkGuard/TypeScript/Declgen 安装结果被后续 npm 操作删除；
5. libarkts SDK Action 把过大的源码目录或输出目录作为依赖边界；
6. `modules_install.py` SA depfile 过滤使用 `extend`，导致应删除条目仍保留；
7. binary install info 内容不变仍重写；
8. system NOTICE 聚合 depfile 吸收全部 NOTICE 文件，形成高扇出传播；
9. `ohos_base_split.timestamp` 声明存在但脚本从不创建。

这些修复只代表各子根因已经被消除，不能替代 `phone_install_modules` 的最终双轮闭环。

### 4.3 `ohos_base_split` 修复方法

排查中确认以下因果链：

```text
ohos_base_split.timestamp 缺失
  -> ohos_base_split 每轮 dirty
  -> SDK declaration / patch_sdk / runner_gen_code
  -> converter_generated.h / arkoala_api_generated.h 更新时间
  -> 相关 CXX 对象重新编译
  -> 大量共享库重新 SOLINK
  -> phone_install_modules 的真实二进制输入更新时间
  -> phone_install_modules 执行
```

曾评估并拒绝以下不安全方案：

1. 直接从 `outputs` 删除 timestamp：Action 没有完整文件输入，删除后可能使接口源码变化不再触发；
2. 只创建稳定 timestamp：同样会把原来“每轮执行”变成“永远 clean”，暴露输入缺失并造成陈旧 SDK；
3. 只把目录路径声明为 input：已有文件内容变化通常不会改变父目录 mtime；
4. 无条件 `touch`：每轮更新时间，仍会向下游传播 dirty。

最终方案：

- `BUILD.gn` 保留 timestamp 输出，同时声明 depfile；
- `parse_interface_sdk.py` 成功完成真实处理后才写 depfile 和 stamp；
- depfile 记录 `interface/sdk-js` 的文件和每级目录；
- 文件依赖覆盖内容修改，目录依赖覆盖新增和删除；
- 包含 Node.js 工具及实际 `node_modules` 依赖；
- 包含权限定义、Python import 依赖和公开 SDK 模式下的 `build_sdk_path`；
- 排除 `.git`、`.gitee` 版本控制元数据；
- depfile 左侧严格使用 GN 第一个输出 `sdk-interface`；
- stamp 使用 `build_utils.atomic_output` 写空内容，内容不变时不更新时间。

该实现涉及：

```text
build/ohos/sdk/parse_interface_sdk.py
interface/sdk-js/BUILD.gn
```

运行时 depfile 当前约包含：

```text
17000 余个文件和目录条目
大小约 1.57 MB
```

最小 `/tmp` Ninja 实验已验证：

```text
初轮执行
无变化第二轮 clean
修改普通文件后重新执行
新增文件后重新执行
删除文件后重新执行
修改 node_modules 实际模块后重新执行
再次无变化后 clean
```

## 5. 日志与证据位置

### 5.1 前序关键日志

```text
IDL 输出名称修复：
/srv/workspace/action_incremental_logs_20260825/phone_install_idl_name_fix

NOTICE 边界修复：
/srv/workspace/action_incremental_logs_20260825/phone_install_notice_boundary_fix

大规模真实重链接诊断：
/srv/workspace/action_incremental_logs_20260827/phone_install_modules_dirty_probe
```

`phone_install_modules_dirty_probe` 证明当时不是尾端 Action 自身无条件执行：探针中新增 7281 条 Ninja 记录，包括约 1902 个 `.so`、603 个 `.o` 和 3202 个 stamp，真实重链接输入足以使 `phone_install_modules` dirty。因此不得在 packages 尾端跳过 Action 或删除真实二进制依赖。

### 5.2 `ohos_base_split` 双轮日志

```text
/srv/workspace/action_incremental_logs_20260828/ohos_base_split_depfile_fix
```

保存文件：

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

第一轮：

```text
rk3568 build success
构建时间：0:04:44（外层 real 4m52s）
ACTION // 计数：661
SOLINK 计数：6
ohos_base_split：执行
phone_install_modules：执行
```

第一轮生成：

```text
out/rk3568/obj/interface/sdk-js/ohos_base_split.timestamp
  size=0
  mtime=1787888262

out/rk3568/obj/interface/sdk-js/ohos_base_split.d
  size=1573342
  mtime=1787888262
```

depfile 开头：

```text
sdk-interface: ../../base/security/access_token/services/accesstokenmanager/permission_definitions.json ../../build/gn_helpers.py ../../build/ohos/sdk/convert_permissions.py ../../build/ohos/sdk/parse_interface_sdk.py ...
```

第二轮：

```text
rk3568 build success
构建时间：0:10:01（外层 real 10m08s）
ACTION // 计数：750
SOLINK 计数：941
ohos_base_split：未执行
ohos_base_split.timestamp：mtime/size 不变
ohos_base_split.d：mtime/size 不变
```

第二轮仍执行：

```text
665:  ACTION //interface/sdk-js:ohos_declaration_ets2
684:  ACTION //foundation/arkui/ace_engine/frameworks/bridge/arkts_frontend/arkoala_generator:patch_sdk
3826: ACTION //foundation/arkui/ace_engine/frameworks/bridge/arkts_frontend/arkoala_generator:runner_gen_code
7043: ACTION //build/ohos/packages:phone_install_modules
```

两轮没有新增以下错误：

```text
FAILED:
ninja: error
GN Failed
Traceback
```

控制台尾部存在 startup_guard 既有告警，但两轮最终均为 `rk3568 build success`，不属于本补丁失败。

### 5.3 当前结论

本轮通过的是：

```text
ohos_base_split 子根因
```

本轮未通过的是：

```text
phone_install_modules 最终目标
```

不能用“第二轮 `ohos_base_split` 消失”替代“第二轮 `phone_install_modules` 消失”。

## 6. 当前规则事实

### 6.1 `ohos_base_split`

`interface/sdk-js/BUILD.gn` 中的 Action 当前关系：

```text
action("ohos_base_split")
  script = //build/ohos/sdk/parse_interface_sdk.py
  outputs[0] = sdk-interface
  outputs[1] = bundleStatusCallback.d.ts
  outputs[2] = ohos_base_split.timestamp
  depfile = ohos_base_split.d
```

关键规则：

- Ninja depfile 左侧必须与第一个 GN output 一致，即 `sdk-interface`；
- stamp 只在主处理成功后创建；
- depfile 使用相对 `out/rk3568` 的路径；
- `--root-build-dir ../../` 解析后是源码根；
- `--build-sdk-path ohos_ets` 按 Ninja cwd 解析为 `out/rk3568/ohos_ets`；
- `node_modules` 是 `handleApiFiles.js` 的真实运行时依赖，不能排除。

### 6.2 下一层 `ohos_declaration_ets2`

`interface/sdk-js/BUILD.gn` 的 `ohos_declaration_template` 当前声明目录输出和：

```text
${target_out_dir}/${target_name}.timestamp
```

对应脚本为：

```text
//interface/sdk-js/remove_internal.py
```

前序静态检查发现 `remove_internal.py` 没有明显的 timestamp 创建逻辑；最新第二轮又确认 `ohos_declaration_ets2` 实际执行。它很可能是 `ohos_base_split` 收敛后暴露出的下一项缺失输出，但仍需通过最新产物 `stat`、`ninja -t query` 和 `ninja -n -d explain` 完成证据闭环，不能只根据相似模式直接修改。

同一文件中的 `ohos_copy_internal` 等模板也声明 `.timestamp` 输出，前序检查时这些 timestamp 普遍不存在。当前必须按 Ninja 最早 dirty 链逐个处理，不要一次性批量修改所有模板。

## 7. 下一步排查顺序

只处理当前最早的 `ohos_declaration_ets2`：

1. 检查 `out/rk3568/obj/interface/sdk-js/ohos_declaration_ets2.timestamp` 是否存在；
2. 用 `ninja -t query` 确认真实 outputs、显式输入、隐式输入和依赖；
3. 用 `ninja -t commands` 保存 `remove_internal.py` 的完整参数；
4. 用 `ninja -n -d explain` 确认是 timestamp 缺失、目录 mtime、上游输出更新还是其他输入 dirty；
5. 阅读 `remove_internal.py` 及其 import/子进程，枚举实际读取的源树、remove list、metadata 和工具文件；
6. 检查最新 `interface/sdk-js` 上游是否已有 stamp、depfile 或稳定输出模式；
7. 判断修复应落在单个调用、`ohos_declaration_template` 还是脚本公共层；
8. 如果需要 stamp，必须同时补齐真实输入或 depfile，不能只创建空文件；
9. 使用 `/tmp` 脚本测试验证内容修改、新增、删除和稳定第二轮；
10. 静态检查通过后停止，只给操作者第一轮完整构建命令。

建议重点回答：

- `remove_internal.py` 是否删除并重建整个输出目录；
- Action 的真实第一个 GN output 是什么，depfile 左侧是否匹配；
- `deps = [ ":ohos_base_split", ":..._info" ]` 是 order-only 还是能表达脚本读取的生成物；
- `input_project_dir`、`remove_list.json`、`module_info` 和 Node/Python 工具是否全部被依赖图覆盖；
- 模板修复是否会同时影响动态、静态、public SDK、ArkUI-X 和不同 host toolchain；
- 目录输出的 mtime 是否足以向真实变更传播，同时在无变化时保持稳定。

## 8. 可使用的只读命令

以下命令只用于定位，不会执行真实构建。

检查疑似缺失输出：

```bash
cd /srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code

stat \
  out/rk3568/obj/interface/sdk-js/ohos_declaration_ets2.timestamp \
  out/rk3568/ohos_declaration/ohos_declaration_ets2
```

查看目标：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 -w dupbuild=warn -t query \
  obj/interface/sdk-js/ohos_declaration_ets2.timestamp
```

查看真实命令：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 -w dupbuild=warn -t commands \
  obj/interface/sdk-js/ohos_declaration_ets2.timestamp
```

只读检查当前 dirty 原因：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 -w dupbuild=warn \
  -n -d explain \
  packages/phone/system_install_modules.json 2>&1 \
  | grep -E \
    'ohos_declaration_ets2|patch_sdk|runner_gen_code|phone_install_modules|missing|doesn.t exist'
```

检查 2026-08-28 第二轮 Action：

```bash
grep -n -E \
  'ACTION //interface/sdk-js:(ohos_base_split|ohos_declaration_ets2)|ACTION .*:(patch_sdk|runner_gen_code)|ACTION //build/ohos/packages:phone_install_modules' \
  /srv/workspace/action_incremental_logs_20260828/ohos_base_split_depfile_fix/second_console.log
```

注意：不要把以上 grep/dry-run 与真实 `build.sh` 放在同一个代码块交给操作者。

## 9. 修复约束

- 所有文本按 UTF-8 读取和写入；
- 变量、函数、文件和 GN target 命名必须保持项目现有风格；
- 代码应可扩展、可读，并覆盖不同产品和 toolchain 的有效路径；
- README、代码注释和提交信息只描述工程事实、设计原因与验证结果；
- 不执行 `git reset --hard`、`git clean`、未确认目标的删除或覆盖；
- 不覆盖任何已验证的未提交修改；
- 不删除真实 `deps`、`inputs`、`outputs` 或 depfile 来绕过 Ninja；
- 不使用空安装列表、假 stamp、无条件 touch 或强制更新时间伪造 clean；
- 不只依赖目录 input 表达已有文件内容变化；
- 不排除 Node/Python 实际加载的工具依赖；
- 不把 `.git`、`.gitee` 等高频 VCS 元数据写入业务 depfile；
- 不把 `phone_install_modules` 尾端改成条件跳过；
- 不一次性修复所有相似 timestamp；必须按当前最早 dirty 根因逐个验证；
- 不自行执行完整编译，不启动后台编译，不 commit，不 push。

如果修改通用模板，必须证明：

1. 每个调用者声明的 output 都由脚本真实生成；
2. 修改、新增、删除输入都能触发；
3. 无变化第二轮保持 clean；
4. depfile 左侧与第一个 GN output 严格一致；
5. host/target toolchain 和 public/static/dynamic 分支路径正确；
6. 不会使其他部件漏掉增量依赖；
7. 上游没有更窄、更规范的等价实现。

## 10. 静态验证要求

每个补丁至少完成：

```text
git diff --check
目标文本 UTF-8 严格解码
Python AST 或 py_compile
GN format --dry-run
目标脚本 --help 或参数级检查
/tmp 脚本功能测试
/tmp 最小 Ninja depfile 测试（若涉及 depfile）
与本地最新 gitcode/master 引用比较
```

涉及 depfile 时，测试至少覆盖：

```text
第一次执行
无变化第二次 clean
已有文件内容修改后执行
新增文件后执行
删除文件后执行
工具或 node_modules 真实依赖修改后执行
再次无变化 clean
```

不得为了格式化目标文件而改写无关历史代码。测试产物只能放在 `/tmp`，不能写入源码目录或 `out/rk3568` 正式产物。

## 11. 两轮构建验收标准与指令规范

### 11.1 第一轮

真实构建只能由操作者执行：

```bash
cd /srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code

LOG_DIR=/srv/workspace/action_incremental_logs_20260828/ohos_declaration_ets2_timestamp_fix
mkdir -p "$LOG_DIR"
set -o pipefail

{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee "$LOG_DIR/first_console.log"

BUILD_STATUS=${PIPESTATUS[0]}

cp out/rk3568/build.log "$LOG_DIR/first_build.log" 2>/dev/null || true
cp out/rk3568/error.log "$LOG_DIR/first_error.log" 2>/dev/null || true
cp out/rk3568/.ninja_log "$LOG_DIR/first_ninja.log" 2>/dev/null || true

echo "BUILD_STATUS=$BUILD_STATUS"
```

第一轮结束后停止。主会话先检查构建状态、目标输出、depfile/stamp 和日志，再决定是否提供第二轮命令。

### 11.2 第二轮

两轮之间不得修改源码、构建参数、输出目录、时间戳或日志目录。只有主会话确认第一轮后，操作者才执行：

```bash
cd /srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code

LOG_DIR=/srv/workspace/action_incremental_logs_20260828/ohos_declaration_ets2_timestamp_fix
mkdir -p "$LOG_DIR"
set -o pipefail

{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee "$LOG_DIR/second_console.log"

BUILD_STATUS=${PIPESTATUS[0]}

cp out/rk3568/build.log "$LOG_DIR/second_build.log" 2>/dev/null || true
cp out/rk3568/error.log "$LOG_DIR/second_error.log" 2>/dev/null || true
cp out/rk3568/.ninja_log "$LOG_DIR/second_ninja.log" 2>/dev/null || true

echo "BUILD_STATUS=$BUILD_STATUS"
```

### 11.3 下一子根因通过标准

`ohos_declaration_ets2` 子根因通过必须同时满足：

1. 两轮均为 `rk3568 build success`；
2. 第二轮不再执行 `ohos_declaration_ets2`；
3. 对应声明的 timestamp/depfile 存在且两轮之间稳定；
4. 第二轮不再由它带动 `patch_sdk` 和 `runner_gen_code`；
5. 第二轮 SOLINK 数量显著收敛且不新增异常重链接链；
6. `ohos_base_split` 继续不执行，现有 stamp/depfile 保持稳定；
7. 不新增 GN、Ninja、Python、SDK 或 metadata 错误；
8. 已验证的 IDL、NOTICE、SA、binary info、libarkts 等修改不得回退。

### 11.4 最终 10/10 标准

只有同一代码状态下第二轮同时满足以下条件，才可更新为 10/10：

```text
原始 9 个已修 Action 均不发生无效重建
phone_install_modules 不执行
两轮构建成功
没有删除真实依赖或跳过安装逻辑
没有新增其他高扇出重复链
```

如果 `ohos_declaration_ets2` 消失后 `phone_install_modules` 仍执行，必须继续报告新的最早直接原因，不能把子问题通过表述为最终完成。

## 12. 接手者交付内容

完成下一子问题排查和补丁后，只向主会话提供：

1. 根因和完整因果链；
2. 最新上游比较结果；
3. 修改仓库、文件和精确 diff；
4. 为什么修复落在该责任层；
5. 输入、输出、depfile、stamp 的覆盖证明；
6. 静态检查和 `/tmp` 测试原始结果；
7. 对 public/static/dynamic、host/target toolchain 的影响；
8. 第一轮完整构建命令和建议日志目录；
9. 明确声明未执行真实构建、未提交、未推送。

主会话负责：

- 独立检查远程 diff 和工作树保护情况；
- 判断补丁是否遗漏真实输入；
- 在第一轮后检查产物和日志；
- 在第二轮后确认目标链是否真正消失；
- 决定继续追下一根因，或进入拆分分支、DCO 提交和 PR 阶段。

## 13. 后续但不属于当前单项的问题

当前已知但不得与 `ohos_declaration_ets2` 同时修改的问题包括：

```text
ohos_copy_internal 等其他模板声明 timestamp 但脚本可能未创建
clang_x64/gen/arkcompiler/ets_frontend/ets2panda/consistency_check.stamp 不存在
camera vdi tmp.c 不存在
system.cil.sha256 不存在
generate_pcid_build_ext_components.txt 不存在
kernel/checkpoint/compile_check 不存在
部分 HAP js_assets.zip 早于共享 releaseAssets map
systemres_hap__js_assets.d 和 telephonyres_hap__js_assets.d 缺失
```

这些问题只有在当前最早链完成单项验证后，才能重新执行只读 dry-run，按新的最早 dirty 原因排序处理。

当前接手顺序固定为：

```text
确认 ohos_declaration_ets2 直接 dirty 原因
  -> 做单一责任层最小修复
  -> 静态和 /tmp 测试
  -> 操作者第一轮构建
  -> 主会话检查
  -> 操作者第二轮构建
  -> 验证 phone_install_modules 是否消失
  -> 若仍执行，再追新的最早根因
```

## 14. OpenCode、Codex、人工验证与 PR 交付工作流

### 14.1 角色边界

当前修复流程由三个角色协作完成：

| 角色 | 主要职责 | 禁止事项 |
|---|---|---|
| OpenCode | 根据交接文档连接远程环境，定位单一根因、编写补丁、执行静态检查和 `/tmp` 功能测试 | 不执行真实 `build.sh`，不执行真实 Ninja，不 commit，不 push，不覆盖已有修改 |
| Codex | 独立检查 OpenCode 的结论和实际工作树，验证责任层、输入输出语义、上游一致性、代码规范和日志结果 | 不以 OpenCode 的文字报告代替实际 diff，不在未通过复核时给出真实编译指令，不擅自扩大修复范围 |
| 操作者 | 按 Codex 提供的指令执行第一轮和第二轮真实编译，反馈完成状态，最终确认分支、提交和 PR 操作 | 两轮之间不修改源码、参数或输出目录，不混入 grep、清理或其他构建，不自行合并多个补丁 |

总体流程：

```text
交接文档和现状确认
  -> OpenCode 单根因定位与补丁
  -> Codex 独立代码复核
  -> 不通过则退回 OpenCode 修正
  -> 静态检查通过
  -> 操作者执行第一轮真实编译
  -> Codex 检查第一轮日志和产物
  -> 操作者执行第二轮真实编译
  -> Codex 检查增量结果和回归
  -> 通过后整理 Issue 和 PR 概要
  -> 按子仓拆分分支与 DCO 提交
  -> 推送到个人 fork
  -> 操作者创建或更新 PR
  -> 跟踪门禁、评审和烟测结果
```

### 14.2 阶段一：准备交接上下文

开始修复前，Codex 负责整理并确认：

1. 当前唯一目标和不属于本轮的问题；
2. 远程地址、源码目录、产品和构建入口；
3. 相关子仓的分支、HEAD、上游引用和工作树状态；
4. 已验证修改及不得覆盖的文件；
5. 最近两轮日志、Ninja explain、目标输出和因果链；
6. 允许的只读命令和禁止执行的真实构建操作；
7. 静态检查、双轮编译和最终验收标准。

交接内容必须以事实为基础，不能把尚未通过双轮验证的推测写成已完成结论。

### 14.3 阶段二：OpenCode 联调修复

OpenCode 每次只处理一个最早直接原因。输入应包含：

```text
交接文档路径
远程连接方式
目标 GN label 或输出文件
最新日志目录
已有工作树保护清单
允许和禁止执行的命令
静态测试要求
交付格式
```

OpenCode 的标准排查顺序：

1. UTF-8 读取相关 GN、Python、JavaScript 和配置文件；
2. 检查 `git status --short --branch`，保护已有修改；
3. 使用 `ninja -t query`、`ninja -t commands` 和 `ninja -n -d explain` 建立真实依赖链；
4. 检查最新上游引用是否已有等价实现；
5. 确认问题属于缺失输出、错误输入、无条件重写、非确定顺序、mtime 传播还是错误 depfile；
6. 选择责任层准确的最小修复；
7. 执行 UTF-8、AST、GN format、`git diff --check` 和 `/tmp` 测试；
8. 停止并报告，不执行真实项目构建。

OpenCode 必须交付：

```text
根因和完整因果链
上游比较结果
修改仓库和文件
精确 diff
输入与输出覆盖证明
静态检查原始结果
跨产品和 toolchain 风险
建议的第一轮构建日志目录
未构建、未提交、未推送声明
```

### 14.4 阶段三：Codex 独立复核

Codex 收到 OpenCode 结果后，必须检查远程实际状态，不能只复述报告。

复核项目：

1. `git status` 中是否出现无关文件或覆盖已有修改；
2. 实际 diff 是否与报告一致；
3. 修复是否落在正确仓库和责任层；
4. output 是否由脚本真实生成；
5. inputs/depfile 是否覆盖内容修改、新增、删除和工具依赖；
6. depfile 左侧是否匹配第一个 GN output；
7. 是否错误删除真实依赖、只声明目录 input、无条件 touch 或伪造 clean；
8. 默认分支、public/static/dynamic、host/target toolchain 是否保持正确；
9. 上游是否已有更窄或更规范的模式；
10. UTF-8、代码风格、函数复杂度、`git diff --check`、AST 和 GN format 是否通过。

发现以下情况时必须退回 OpenCode，不得给操作者编译指令：

```text
直接删除缺失 output 但未补齐输入
只创建 stamp 但 Action 无真实依赖
用目录 mtime 代替文件内容依赖
遗漏 Node/Python 实际加载模块
路径基准与 Ninja cwd 不一致
depfile 第一个输出不匹配
修改通用模板但未证明其他调用者安全
补丁混入其他仓库或无关文件
```

复核通过后，Codex 只给第一轮真实构建指令。grep、stat、dry-run 和日志检查由 Codex单独执行，不与构建命令混在同一个代码块中。

### 14.5 阶段四：人工第一轮编译

操作者执行 Codex 提供的第一轮命令，并独立保存：

```text
first_console.log
first_build.log
first_error.log
first_ninja.log
```

第一轮用于：

- 确认 GN 和 Ninja 能接受新规则；
- 生成新增的 stamp、depfile 或中间产物；
- 确认完整 rk3568 构建通过；
- 建立第二轮比较基线。

第一轮结束后，操作者只回复完成状态。Codex连接远程检查：

```text
build success / BUILD_STATUS
FAILED、GN Failed、ninja error、Traceback
目标 Action 是否执行
新增输出是否存在
depfile 内容、目标名和路径基准
stamp/JSON/归档的 size、mtime、inode 或 hash
已有修复是否回退
```

第一轮失败时，停止第二轮，先根据日志把具体错误退回 OpenCode修正。

### 14.6 阶段五：人工第二轮编译

只有第一轮通过并经 Codex 确认后，操作者才执行第二轮。两轮之间必须满足：

```text
不修改源码
不切换分支
不执行 git 操作
不删除或触碰 out 目录
不改变构建参数
不启动其他构建
使用同一代码状态和同一产品
```

第二轮独立保存：

```text
second_console.log
second_build.log
second_error.log
second_ninja.log
```

### 14.7 阶段六：Codex 最终验证

Codex 对比两轮日志和产物，至少检查：

1. 两轮是否都为 `rk3568 build success`；
2. 目标 Action 第二轮是否消失；
3. 上游和下游高扇出 Action 是否同步收敛；
4. 新增 stamp、depfile、JSON 或归档是否稳定；
5. ACTION、CXX、SOLINK 数量是否符合预期；
6. 是否出现新的最早 dirty 原因；
7. 原始 10 个目标是否真正达到当前宣称的进度；
8. 是否新增其他部件构建错误或丢失依赖。

验证结论分为三类：

| 结论 | 含义 | 后续动作 |
|---|---|---|
| 子根因通过，最终目标未通过 | 当前修复有效，但暴露出下一层 dirty 原因 | 保留补丁，更新交接，继续处理新的最早根因 |
| 最终目标通过 | 两轮成功且原始目标第二轮不执行 | 进入 Issue、PR、分支和提交阶段 |
| 修复失败或回归 | 构建失败、目标仍由同一原因执行或其他部件受影响 | 停止提交，退回 OpenCode 修正 |

不得把“子 Action 消失”直接表述为“整个原始目标完成”。

### 14.8 阶段七：整理中文 Issue 概要

只有验证证据充分后才整理 Issue。推荐结构：

```markdown
## 问题描述
说明无源码变化的第二轮构建中，哪个 Action 仍重复执行，以及对构建时间和下游的影响。

## 复现步骤
1. 执行第一轮完整构建；
2. 不修改源码和输出目录；
3. 执行第二轮相同构建；
4. 在日志中观察目标 Action。

## 实际结果
列出第二轮重复 Action、缺失输出、mtime 变化或 Ninja explain 证据。

## 预期结果
输入未变化时目标 Action 不执行；真实输入修改、新增或删除时仍能正确触发。

## 原因分析
说明 GN outputs、脚本行为、depfile、restat 和下游传播链。

## 建议方案
说明责任层和修复原则，不删除真实依赖，不跳过尾端 Action。

## 验证结果
列出两轮构建状态、目标 Action、ACTION/SOLINK 变化和回归检查。
```

Issue 不写内部模型协作过程，只描述工程问题、原因和验证事实。远程内部路径可以作为个人留档，但提交到社区时应改成通用仓库相对路径和可复现命令。

### 14.9 阶段八：整理中文 PR 概要

PR 推荐结构：

```markdown
## 修改说明
- 修改了哪些文件；
- 补齐了哪些输入、输出、depfile 或稳定写入逻辑；
- 为什么修改位于该责任层。

## 问题原因
说明缺失输出或无效 mtime 如何触发 Ninja，并列出关键传播链。

## 方案设计
说明真实输入覆盖、路径基准、跨 toolchain 行为和避免无效重写的方法。

## 影响范围
列出涉及的产品、模板调用者、public/static/dynamic 分支和不受影响的组件。

## 验证结果
- UTF-8/AST/GN format/git diff --check；
- `/tmp` 功能或最小 Ninja 测试；
- rk3568 第一轮完整构建；
- rk3568 第二轮增量构建；
- 目标 Action 和下游链变化。

## 关联 Issue
关联对应 Issue 编号或链接。
```

PR 标题应描述具体工程修复，例如：

```text
修复 SDK 接口处理 Action 的增量依赖声明
```

不要使用“优化构建”“修复若干问题”等无法界定责任范围的宽泛标题。

### 14.10 阶段九：按子仓拆分分支和提交

OpenHarmony 多仓代码必须分别提交。当前 `ohos_base_split` 修复至少横跨：

```text
build
interface/sdk-js
```

因此不能在一个子仓提交中混入另一个子仓文件。每个子仓分别执行：

1. 确认正确 HEAD 和上游基线；
2. 创建不含 `codex` 的功能分支；
3. 只暂存该仓本问题文件；
4. 检查 staged diff；
5. 使用 DCO sign-off 提交；
6. 检查提交正文和 `Signed-off-by`；
7. 推送到操作者个人 fork。

示例流程仅供确认后使用：

```bash
git switch -c fix-sdk-interface-incremental-deps

git status --short
git diff --check

git add <本仓本问题文件>
git diff --cached --check
git diff --cached

git commit -s -m "fix sdk interface incremental dependencies"

git log -1 --format=full
git push -u <个人-fork-remote> fix-sdk-interface-incremental-deps
```

执行前必须由 Codex 根据实际仓库状态给出准确文件和 remote，不能直接复制占位符。

提交规范：

- 分支名不得包含 `codex`；
- `git commit -s` 使用与社区账号一致的姓名和邮箱；
- 提交末尾必须存在 `Signed-off-by: Name <email>`；
- 不使用 `git add .` 或 `git add -A`；
- 不提交日志、`out`、临时脚本、会话导出或其他任务文件；
- 默认不使用 force push；需要改写历史时必须先获得操作者明确许可；
- 当前工作树有多项已验证修改时，必须逐文件确认归属，禁止把所有修改一次提交。

### 14.11 阶段十：推送分支并创建 PR

推送前检查：

```text
分支基线正确
工作树无意外文件
提交只包含目标修复
DCO sign-off 正确
两轮日志对应当前提交内容
Issue 和 PR 概要已与最终 diff 对齐
```

推送目标必须是操作者的个人 fork，不直接推送官方上游。Codex 只有在操作者明确要求并确认 remote 后才能执行 `git push`。

推送成功后：

1. 向操作者提供仓库、分支名和 commit SHA；
2. 提供可直接粘贴的中文 Issue 标题与正文；
3. 提供可直接粘贴的中文 PR 标题与正文；
4. 多仓修复分别创建 PR，并在正文中注明依赖关系和合入顺序；
5. 由操作者创建 PR，或在操作者明确授权且工具可用时创建；
6. 不把内部 SSH 地址、私有日志路径、账号密钥或环境信息写入公开 Issue/PR。

跨仓 PR 推荐说明：

```text
PR A（build）：提供脚本的 depfile/stamp 写入能力
PR B（interface/sdk-js）：在 GN Action 中声明并传递 depfile/stamp

依赖顺序：先合入或同时评审 PR A，再合入 PR B。
```

实际顺序必须根据单仓兼容性判断。如果脚本参数设计为可选并保持旧调用兼容，应在 PR 中明确说明。

### 14.12 阶段十一：PR 门禁、烟测与后续修正

PR 创建后继续检查：

```text
DCO
代码格式
静态检查
GN gen
目标产品构建
其他产品或部件烟测
增量构建用例
评审意见
```

门禁失败时：

1. 先保存并读取完整日志；
2. 区分补丁回归、环境问题、基线问题和无关告警；
3. 只修复与当前 PR 有关的失败；
4. 由 OpenCode提出补丁，Codex独立检查，人工重新验证；
5. 使用新的 DCO 提交更新分支，默认不改写已推送历史；
6. 更新 PR 的验证结果和风险说明。

PR 合入前，最终状态必须能够从以下证据闭环：

```text
Issue 描述的问题
  -> PR 中的具体修改
  -> 静态和脚本测试
  -> 人工第一轮完整构建
  -> 人工第二轮增量构建
  -> 目标 Action 和下游链收敛
  -> 门禁与烟测通过
```
