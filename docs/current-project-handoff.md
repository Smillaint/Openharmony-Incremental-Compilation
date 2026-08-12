# OpenHarmony Action 增量编译项目交接与分析指南

本文用于把当前 OpenHarmony Action 增量编译工作的完整上下文交给新的分析会话或另一台主机。内容截至 **2026-08-12**。

开始工作前先通读全文。不得只看到日志末尾的 `xx is dirty` 就直接修改对应 Action；必须找到最早的直接 dirty 原因，并区分真实重建、输出缺失、内容变化、mtime 漂移、depfile 问题和上游派生 dirty。

## 1. 项目目标

目标是在 OpenHarmony `rk3568` 无源码变化的连续构建中，消除不必要的 Action、编译和链接，同时保证：

- 不删除真实依赖；
- 不跳过必要校验；
- 不伪造时间戳；
- 不把失败结果写成成功结果；
- 输出只在内容真实变化时更新；
- 每个正式 PR 只解决边界清晰的一个根因；
- 修改具备可读性、可扩展性和失败安全性。

## 2. 操作约束

1. 所有文件按 UTF-8 读取和写入。
2. 默认先只读分析。未明确授权时，不修改代码、不执行完整编译。
3. 完整编译一般由操作者手动执行；分析会话提供准确命令并读取结果。
4. 不执行 `git reset --hard`、`git clean`、递归删除或覆盖未知改动。
5. 远程完整源码和 `out/rk3568` 可能被多个会话共享，切分支和运行 `gn gen` 前必须检查状态。
6. 不在仓库、日志或对话中输出私钥、令牌或密码。
7. GitCode 推送和 PR 创建由仓库所有者完成。分析会话不得自行输入令牌或代替创建 PR。
8. 提交必须包含 DCO：使用 `git commit --signoff`。
9. 正式 PR 基线与远程整仓 manifest 固定基线可能不同，必须分别维护“正式 PR 分支”和“整仓验证分支”。
10. 如果一次验证没有闭环，不连续叠加补丁；先汇报证据、根因和最小方案。

## 3. 远程环境

### 3.1 SSH

```bash
ssh -p 42247 \
  -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=6 \
  root@119.3.182.128
```

Windows 本机当前使用的私钥路径为：

```text
C:\Users\31854\.ssh\id_ed25519
```

只记录路径，不读取或复制私钥内容。

进入远程环境后设置 UTF-8：

```bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
```

### 3.2 完整源码

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
```

`build` 子仓库：

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/build
```

构建输出：

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/out/rk3568
```

### 3.3 远程当前状态

截至 2026-08-12：

```text
branch: sa-profile-query-validation-20260812
HEAD:   2e1aac4bedf1ac669c52098af330cd62ad76c0a2
base:   656fb7cf
status: clean
```

这是 **SA Profile 的整仓兼容验证分支**，不是正式 PR 分支。

远程 `build` 仓已知分支：

```text
sa-profile-query-validation-20260812       2e1aac4b
codex/app-sign-output-validation-20260807  0dad9413
codex/app-sign-output-fix-20260807         656140e1
codex/check-seccomp-output-fix-20260807    c46a9b82
codex/packages-action-incremental-fix-20260805 dfd40cd1
action_incremental_fix_20260804            a335f4f4
```

其中 `codex/packages-action-incremental-fix-20260805` 和 `codex/check-seccomp-output-fix-20260807` 包含多轮实验提交，不可整体当作一个正式 PR 推送。

### 3.4 远程日志目录

```text
/srv/workspace/action_incremental_logs_20260804
/srv/workspace/action_incremental_logs_20260805
/srv/workspace/action_incremental_logs_20260807
/srv/workspace/action_incremental_logs_20260812
```

2026-08-12 的关键日志：

```text
sa_pr_incompatible_error.log
sa_pr_incompatible_build.log
sa_validation_settle_console.log
sa_validation_settle_build.log
sa_validation_settle_ninja.log
sa_validation_dry_run_console.log
sa_validation_dry_run_build.log
sa_validation_second_real_console.log
sa_validation_second_real_build.log
sa_validation_second_real_ninja.log
sa_validation_direct_ninja.log
app_sign_pr_dry_run_console.log
```

## 4. 代码托管位置

### 4.1 OpenHarmony 上游

- 组织主页：<https://gitcode.com/openharmony>
- `build` 上游：<https://gitcode.com/openharmony/build>

### 4.2 GitCode 个人 fork

- 个人主页：<https://gitcode.com/SmillySmillick>
- `build`：<https://gitcode.com/SmillySmillick/build>
- `third_party_jsframework`：<https://gitcode.com/SmillySmillick/third_party_jsframework>
- `third_party_sane-airscan`：<https://gitcode.com/SmillySmillick/third_party_sane-airscan>

### 4.3 GitHub 分析日志

- 仓库：<https://github.com/Smillaint/Openharmony-Incremental-Compilation>
- 本地目录：`D:\workspace\Openharmony-Incremental-Compilation`
- 当前本地分支：`agent/document-action-incremental-fixes`
- 当前远端 `main` 仍停在初始化提交；现有文档提交位于上述功能分支，尚未合并到 `main`。

该日志仓此前缺少最近的 validator、SA query 验证、HAP signing 和 `-n/restat` 方法，本文件用于补齐统一交接信息。

### 4.4 Windows 本地代码仓

```text
D:\workspace\openharmony-build-sa
D:\workspace\gitcode_pr\third_party_jsframework
D:\workspace\gitcode_pr\third_party_sane-airscan
D:\workspace\Openharmony-Incremental-Compilation
```

当前已确认分支：

```text
build fork:
  fix-hap-sign-incremental-build
  commit 34aa8cba

build SA branch:
  codex/fix-sa-profile-incremental-build
  commit 0d530d7e

third_party_jsframework:
  fix/jsframework-incremental-actions
  commit a280a42

third_party_sane-airscan:
  fix/airscan-incremental-action
  commit 37de4f9
```

## 5. 已处理问题

### 5.1 `ark_jsf` 与 `gen_snapshot`

仓库：`third_party_jsframework`

```text
branch: fix/jsframework-incremental-actions
commit: a280a42 fix: stabilize jsframework incremental actions
```

根因：

- `css-what` 和 jsframework 共用生成目录；
- `gen_snapshot` 重复改写 runtime 目录及 `strip.native.min.js`；
- 内容不变但文件或目录 mtime 被刷新，持续触发 `gen_snapshot -> ark_jsf`。

结果：最终零改动真实构建中 `ark_jsf=0`、`gen_snapshot=0`。

### 5.2 `airscan_action`

仓库：`third_party_sane-airscan`

```text
branch: fix/airscan-incremental-action
commit: 37de4f9 fix: stabilize airscan incremental build outputs
```

根因：Action 直接在源码目录应用补丁，重复执行会修改输入并产生 `.rej`。

修复：复制源码到生成目录，只在生成目录应用补丁，编译目标使用生成目录中的 patched sources。

结果：最终零改动真实构建中 `airscan_action=0`。

### 5.3 NOTICE 输出稳定化

已经完成 NOTICE 生成脚本的内容稳定化和异常缓存处理，并通过两轮构建验证。注意：

- NOTICE 产物自身可以保持稳定；
- `collect_notice_files__phone` 仍可能因为 `phone_parts_list` 上游 dirty 而被调度；
- 不要继续在 NOTICE 尾端增加跳过逻辑，应追上游 parts 聚合链。

### 5.4 SA Profile 三个 Action

正式 PR：<https://gitcode.com/openharmony/build/merge_requests/6965>

```text
branch: codex/fix-sa-profile-incremental-build
commit: 0d530d7eb691276cd27d7109b1155a21c6c0c1cc
issue/PR status: 已提交正式 PR
```

涉及：

```text
sa_profile_src_phone
sa_profile_binary_phone
phone_sa_profile_install_info
```

修改文件：

```text
ohos/sa_profile/src_sa_profile_process.py
ohos/sa_profile/sa_profile_source.py
ohos/sa_profile/sa_profile_binary.py
ohos/sa_profile/sa_profile_merge.py
scripts/util/file_utils.py
```

修复内容：

- SA 信息按 `label` 稳定排序；
- JSON 按解析后的值判断变化；
- 内容相同时不重写 JSON；
- ZIP 使用 `atomic_output`，内容相同时不替换原文件。

正式 PR 基线 `69f5e307` 与远程整仓 `656fb7cf` 不兼容，直接构建会出现：

```text
Duplicate build argument declaration:
ace_engine_enable_reduce_eh_frame
```

这不是 SA 补丁错误。验证时把同一提交 cherry-pick 到 `656fb7cf`，形成：

```text
branch: sa-profile-query-validation-20260812
commit: 2e1aac4b
```

2026-08-12 验证结论：

- 真实构建成功；
- 第二次真实构建仍因上游 parts 链执行 `sa_profile_src_phone` 和 `sa_profile_binary_phone`；
- 两个 Action 执行后输出内容及 mtime 不变；
- Ninja `restat` 阻断 dirty 传播；
- `phone_sa_profile_install_info` 在第二次真实构建中没有执行；
- 因此当前 `rk3568` 验证范围内修复有效，无需继续补丁。

尚未覆盖：非空二进制 SA、ZIP 中包含 `part_name_info.json` 的其他产品场景。审查该场景时注意普通 `ZipFile.writestr()` 可能写入动态 ZIP entry 时间；应优先使用 `build_utils.add_to_zip_hermetic()`。

### 5.5 HAP signing 输出

相关 Issue：<https://gitcode.com/openharmony/build/issues/4663>

GitCode fork 分支：

```text
branch: fix-hap-sign-incremental-build
commit: 34aa8cba Fix incremental HAP signing outputs
base:   69f5e307
```

远程正式补丁等价提交：

```text
codex/app-sign-output-fix-20260807
656140e1 Fix incremental HAP signing outputs
```

整仓兼容验证提交：

```text
codex/app-sign-output-validation-20260807
0dad9413 Fix incremental HAP signing outputs
base: 656fb7cf
```

涉及文件：

```text
ohos/app/app_internal.gni
scripts/app_sign.py
scripts/compile_app.py
scripts/util/build_utils.py
```

修复范围：

- 避免多个 app signing Action 共享或冲突的 stamp 输出；
- 为每个签名 Action声明独立 `sign_result.json`；
- 记录 unsigned/signed HAP 的稳定路径列表和 SHA-256；
- JSON 原子写入，内容相同时保留输出。

该分支已经推送到个人 fork。PR 编号和最终门禁状态没有在本地日志中确认，新会话不得猜测；需要仓库所有者补充。

### 5.6 validator 声明输出缺失

已确认两个独立根因：

```text
check_seccomp_filter_name
  GN 声明 packages/phone/check_seccomp_filter_name.txt
  旧脚本成功时未生成该文件

process_field_validate
  GN 声明 packages/phone/cfg_validate_result.txt
  旧脚本成功时未生成该文件
```

远程实验分支存在 `check_seccomp_filter_name` 修复提交：

```text
9e2dcc48 Fix missing seccomp validation output
```

但该提交所在分支还叠加了 packages、NOTICE、SA 等历史实验，不可整体作为正式 PR。应从最新正式上游重新建立小分支，只移植 validator 相关文件，成功标记必须：

- 文件真实存在；
- 内容固定；
- 相同内容重复执行不刷新 mtime；
- 失败路径仍返回非零；
- 不用空文件掩盖失败。

`process_field_validate` 是否已形成正式提交没有可靠证据，当前按 **待整理/待验证** 处理。

## 6. 待处理问题

原始 packages Action 列表：

```text
check_seccomp_filter_name
collect_notice_files__phone
generate_host_symlink
phone_hisysevent_install_info
phone_install_modules
phone_parts_list
phone_sa_profile_install_info
process_field_validate
sa_profile_binary_phone
sa_profile_src_phone
```

当前状态：

| Action | 状态 | 下一步 |
| --- | --- | --- |
| `sa_profile_src_phone` | 已修复，PR !6965 | 只需关注其他产品覆盖 |
| `sa_profile_binary_phone` | 已修复，PR !6965 | 补充非空 binary SA 场景测试 |
| `phone_sa_profile_install_info` | 已修复，PR !6965 | 无需继续改尾端 |
| `check_seccomp_filter_name` | 根因已确认，有实验提交 | 从最新上游整理独立小 PR |
| `process_field_validate` | 根因已确认 | 实现稳定成功输出并独立验证 |
| `collect_notice_files__phone` | NOTICE 自身稳定，仍受 parts 上游影响 | 追 `phone_parts_list`，不改 NOTICE 尾端 |
| `generate_host_symlink` | 自身 JSON 可稳定，仍受 host parts 输入影响 | 追 `all_parts_host.json` 的最早 dirty 节点 |
| `phone_hisysevent_install_info` | 自身产物可稳定，仍受 parts 依赖影响 | parts 链稳定后复验 |
| `phone_parts_list` | 未收敛 | 优先分析 parts 聚合链 |
| `phone_install_modules` | 有真实 `.so`/可执行文件重建输入 | 追最早重复链接模块，不跳过安装 Action |

其他待处理项：

### 6.1 `phone_parts_list` 上游

重点链路：

```text
各部件 build_configs
  -> generate_src_installed_info
  -> generate_host_info
  -> gen_binary_installed_info
  -> merge_all_parts
  -> phone_parts_list
  -> collect_notice_files__phone / SA / HiSysEvent / packages
```

必须找到最早的直接 dirty 节点。不要因为日志末尾显示 `system_install_parts.json is dirty` 就直接修改 `phone_parts_list`。

### 6.2 `phone_install_modules`

已观察到 window manager、device attest 等真实 `.so` 被重新链接。需要：

1. 找到第二轮最早 dirty 的具体库；
2. 沿 Ninja explain 追输入、depfile、源文件和 stamp；
3. 区分内容真实变化与 mtime/depfile 问题；
4. 在对应模块仓库修复，不在 packages 尾端删除依赖。

### 6.3 `Compressor.java`

准确路径：

```text
developtools/packing_tool/adapter/ohos/Compressor.java
```

Telephony 和 Contacts 的 unsigned HAP 曾出现每轮 hash 变化，原因指向 ZIP entry 使用当前时间。建议方案：

- 为可复现构建使用固定 ZIP entry 时间；
- 固定 entry 顺序、权限和压缩参数；
- 保持原有异常传播；
- 单独在 `developtools_packing_tool` 仓建立 PR，不混入 `build` PR；
- 验证相同输入连续打包的 HAP SHA-256 一致。

## 7. GN、Ninja 和可执行文件帮助

先看工具自身帮助，不凭记忆猜参数。

GN 的正确帮助形式：

```bash
prebuilts/build-tools/linux-x86/bin/gn help
prebuilts/build-tools/linux-x86/bin/gn help action
prebuilts/build-tools/linux-x86/bin/gn help copy
prebuilts/build-tools/linux-x86/bin/gn help desc
prebuilts/build-tools/linux-x86/bin/gn help depfile
prebuilts/build-tools/linux-x86/bin/gn help buildargs
```

不是 `gn action --help`。GN 使用 `gn help <topic>`。

Ninja：

```bash
prebuilts/build-tools/linux-x86/bin/ninja --help
prebuilts/build-tools/linux-x86/bin/ninja -d list
prebuilts/build-tools/linux-x86/bin/ninja -t list
prebuilts/build-tools/linux-x86/bin/ninja -w list
```

其他可执行文件优先尝试：

```bash
<executable> --help
<executable> -h
```

## 8. 使用 `gn desc` 确认 Target

先看目标概要：

```bash
prebuilts/build-tools/linux-x86/bin/gn desc \
  out/rk3568 \
  //build/ohos/packages:sa_profile_src_phone
```

概要会显示 `type: action`。`gn desc` 没有单独的 `type` 查询项，不要执行：

```text
gn desc ... type
```

常用查询：

```bash
prebuilts/build-tools/linux-x86/bin/gn desc \
  out/rk3568 '<label>' outputs

prebuilts/build-tools/linux-x86/bin/gn desc \
  out/rk3568 '<label>' inputs

prebuilts/build-tools/linux-x86/bin/gn desc \
  out/rk3568 '<label>' script

prebuilts/build-tools/linux-x86/bin/gn desc \
  out/rk3568 '<label>' deps --tree
```

检查内容：

- `outputs` 是否由脚本真实生成；
- 多个 Action 是否错误共享输出；
- `inputs/sources` 是否完整；
- `depfile` 第一输出是否与 GN 规则一致；
- `deps` 是否只是调度依赖，是否存在不必要的尾端硬依赖。

## 9. 标准验证流程

### 9.1 先检查 Git 和基线

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/build

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline --decorate -10
git remote -v
```

如果工作树不干净，先判断修改归属，不覆盖未知文件。

### 9.2 正式 PR 与整仓验证分支分离

完整源码由 manifest 固定各子仓提交。正式 PR 若基于最新上游，可能不能直接放入较旧整仓。

正确做法：

1. 正式 PR 分支基于官方最新目标分支；
2. 验证分支基于整仓当前 manifest 提交；
3. 只 cherry-pick 同一个最小修复提交；
4. 两个分支补丁内容必须一致；
5. 不为消除版本冲突而修改无关仓库或无关 build argument。

### 9.3 第一次真实收敛构建

切分支或修改脚本后必须先真实构建。checkout 会刷新脚本 mtime，直接 dry-run 会得到一次性 dirty。

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code

mkdir -p /srv/workspace/action_incremental_logs_YYYYMMDD

{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_first_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_first_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_first_ninja.log
```

### 9.4 指导要求的快速 query

```bash
{ time ./build.sh -p rk3568 --build-target make_all \
  --ninja-args=-dexplain \
  --ninja-args=-n \
  --ninja-args=-dstats; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_dry_run_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_dry_run_build.log
```

说明：`ninja explain` 经 `build.sh` 封装后通常主要写入 `out/rk3568/build.log`，不能只看 console 日志。

### 9.5 `build.sh -n` 的边界

`build.sh` 在 Ninja 前可能执行 preloader 和 `gn gen`，刷新：

```text
out/preloader/<product>/*
out/<product>/build_configs/*
out/<product>/build.ninja
```

随后 `-n` 不执行 Action。因此它不能知道 Action 执行后输出是否保持不变，也不能触发真实的 `restat` 截断。

可能出现：

```text
上游输入被 preloader/GN 刷新
  -> Action 在 dry-run 中应执行
  -> -n 不执行脚本
  -> Ninja 无法证明输出不变
  -> 下游继续显示 xx is dirty
```

这类 `is dirty` 是派生结果，不等于修复失败。

### 9.6 第二次真实构建

```bash
{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_second_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_second_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_second_ninja.log
```

第二次真实构建才可以验证：

- Action 是否实际执行；
- 执行后输出 mtime 是否变化；
- `restat` 是否阻断下游；
- 下游 Action 是否真正消失。

### 9.7 直接 Ninja query

跳过 `build.sh` 的 preloader/GN 阶段，只检查当前 Ninja 图：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -n \
  -d explain \
  -d stats \
  obj/build/core/gn/make_all.stamp 2>&1 \
  | tee /srv/workspace/action_incremental_logs_YYYYMMDD/<task>_direct_ninja.log
```

单目标追踪：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -n -d explain \
  obj/build/ohos/packages/<target>.stamp
```

查询某个输出的直接输入和消费者：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -t query \
  '<output path relative to out/rk3568>'
```

如果构建图存在 duplicate output，普通 `-t query` 可能直接失败；可先加 `-w dupbuild=warn`，但 duplicate output 本身也应单独记录。

## 10. `restat` 的正确理解

GN 为 Action 生成 Ninja 规则时使用 `restat=1`。真实执行过程：

```text
上游 dirty
  -> Action 执行
  -> 脚本生成临时输出
  -> 内容与旧输出相同
  -> 原文件和 mtime 不变
  -> Ninja restat 发现输出未改变
  -> dirty 不再传播到下游
```

而 `ninja -n`：

```text
上游 dirty
  -> 计划执行 Action
  -> 不真正执行
  -> 无法比较执行后的输出
  -> 保守地继续把下游列为 dirty
```

所以验收不能只看 dry-run 中是否出现 Action。必须同时查看：

1. 第二次真实构建 Action 行；
2. 输出的纳秒级 mtime、inode、size；
3. SHA-256；
4. `.ninja_log` 是否新增真实条目；
5. 下游 Action 是否真实执行；
6. dry-run 中第一条直接 dirty 原因。

示例：SA 验证中前两个 Action 被上游带起，但输出 mtime 保持不变，第三个 Action没有真实执行，因此修复有效。

## 11. 日志分析命令

筛选 Action：

```bash
grep -nE \
  'ACTION //build/ohos/packages:(target_a|target_b)' \
  <build.log>
```

筛选输出 dirty：

```bash
grep -nE \
  'ninja explain:.*(output_a|output_b).*(dirty|older|does not exist)' \
  <build.log>
```

查看最早 explain，而不是只看日志末尾：

```bash
grep -n 'ninja explain:' <build.log> | head -200
```

检查输出：

```bash
stat -c '%y %i %s %n' <outputs...>
sha256sum <outputs...>
```

检查 Ninja 历史：

```bash
grep -E '<output_a>|<output_b>' out/rk3568/.ninja_log | tail -30
```

JSON 不能只比较文本顺序，必要时解析后比较数据结构。ZIP 需要检查：

- entry 名称和顺序；
- entry 时间戳；
- 权限位；
- 压缩方式和压缩级别；
- 内容 hash。

## 12. dirty 类型和处理方式

| 日志现象 | 含义 | 处理 |
| --- | --- | --- |
| `output ... doesn't exist` | 声明输出缺失 | 修脚本真实生成输出 |
| `depfile ... is missing` | depfile 未生成或路径错误 | 核对 GN `depfile` 和脚本写入 |
| `recorded mtime ... older than ...py` | 脚本刚切换或真实修改 | 先真实构建收敛 |
| `command line changed` | Ninja 命令发生变化 | 先运行一次真实构建 |
| `X is dirty` 且 X 是上游输出 | 派生 dirty | 继续向上追最早原因 |
| Action 执行、内容不变、mtime 不变 | 稳定输出生效 | 检查 restat 是否阻断下游 |
| Action 执行、内容相同、mtime 更新 | 无条件重写 | 使用 compare-before-write/atomic output |
| hash 真变化 | 真实非确定性或输入变化 | 比较结构、顺序、ZIP metadata |
| 大量 `.so` 重链 | 真实上游编译链 dirty | 追第一个库及其源输入 |

## 13. 修复实现原则

### JSON

- 使用 `sort_keys=True` 和固定缩进；
- 列表若语义无序，应按稳定唯一键排序；
- 内容相同不重写；
- 原子替换，失败时不留下半文件；
- 不用 `str(dict)` 的插入顺序作为语义比较。

### ZIP/HAP

- 固定 entry 顺序；
- 固定 entry 时间戳和权限；
- 固定压缩参数；
- 使用仓内 hermetic ZIP helper；
- 临时文件写完后比较，内容不同才替换；
- 相同输入连续运行 SHA-256 必须一致。

### validator

- 成功必须生成 GN 声明的输出；
- 成功标记内容固定；
- 内容相同不刷新；
- 失败仍返回非零；
- 不用空文件冒充验证成功。

### depfile

- 包含全部真实动态输入；
- 输入排序稳定；
- 第一输出与 Ninja/GN 规则一致；
- 不为了让 Action 消失而删除真实输入。

## 14. Git 和 PR 流程

### 14.1 更新上游

```bash
git fetch upstream
git status --short
```

新建正式分支前确认基线，分支名不强制使用 `codex/`；可使用：

```text
fix/<problem>-incremental-build
```

### 14.2 提交检查

```bash
git add <explicit files>
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit --signoff -m '<message>'
```

确认 DCO：

```bash
git log -1 --format=full
```

必须看到：

```text
Signed-off-by: Smillick <3185479846@qq.com>
```

### 14.3 推送

只给仓库所有者命令，由其自行输入 GitCode 凭据：

```bash
git push -u origin <branch>
```

不要向 `openharmony` 上游直接推送。

## 15. 新会话开始时的执行顺序

1. 阅读本文件和 `docs/build-action-incremental.md`。
2. SSH 连接远程机，设置 UTF-8。
3. 检查 `code/build` 当前分支、HEAD、工作树和远端。
4. 询问当前是否有其他会话在使用 `out/rk3568`。
5. 只读查看最新日志，不立即编译。
6. 用 `gn help`、`gn desc`、`ninja --help`、`ninja -t query` 建立目标关系。
7. 用 `ninja -n -d explain` 找最早 dirty 节点。
8. 说明当前是直接根因还是派生 dirty。
9. 只有根因和最小文件范围确认后才提出修改。
10. 完整编译命令交给操作者执行。
11. 读取两轮 console、`build.log`、`.ninja_log`、mtime 和 hash。
12. 正式 PR 使用最新上游小分支；整仓验证使用 manifest 兼容分支。
13. 不推送、不创建 PR；提供中文 Issue/PR 描述和命令即可。

## 16. 建议下一项任务

优先级建议：

1. 把 `check_seccomp_filter_name` 从实验分支整理为最新上游上的独立小 PR；
2. 用同类方式修复并验证 `process_field_validate`；
3. 只读追踪 `phone_parts_list` 的最早 dirty 节点；
4. 分离分析 `phone_install_modules` 中最早重复链接的模块；
5. 在 `developtools_packing_tool` 独立处理 `Compressor.java` 的 ZIP 时间戳；
6. 补充 HAP signing 正式 PR 编号、门禁状态和最终验证日志；
7. 将本日志分支合并或推送到 GitHub `main`，避免资料继续分散。

每次汇报应包含：当前分支/HEAD、是否只读、最早 dirty 节点、直接证据、确定事实与推断、最小修改范围、是否适合独立 PR、需要操作者执行的命令。
