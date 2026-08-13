# OpenHarmony 增量编译项目统一交接提示词（2026-08-12）

> 当前状态已经更新到 2026-08-13。新会话请优先阅读 [incremental-build-handoff-20260813.md](incremental-build-handoff-20260813.md)。本文保留为历史快照。

将本文完整提供给后续分析会话。本文是当前项目入口，具体历史证据再按文中的链接读取，不要凭旧结论直接改代码。

## 1. 工作目标

定位并修复 OpenHarmony `rk3568` 连续零改动构建中重复执行的 `ACTION`、重新链接和重复打包问题。

判断修复是否有效时必须同时确认：

1. 构建成功；
2. 目标输出真实存在；
3. 相同输入下输出内容稳定；
4. 内容不变时输出 mtime 不刷新；
5. Ninja `restat` 能阻断无效 dirty 传播；
6. 失败路径仍然返回非零；
7. 没有通过删除真实依赖、伪造时间戳或跳过 Action 制造“零构建”。

## 2. 身份、DCO 与代码托管账号

三个名称用途不同，不能混用：

| 用途 | 身份 |
| --- | --- |
| Git 提交作者和 DCO | `Smillick <3185479846@qq.com>` |
| GitCode 个人账号 | `SmillySmillick` |
| GitHub 个人账号 | `Smillaint` |

每个准备提交到 OpenHarmony 或项目日志仓的 commit 都必须配置并检查：

```bash
git config user.name 'Smillick'
git config user.email '3185479846@qq.com'
git config --get user.name
git config --get user.email
```

提交必须使用：

```bash
git commit --signoff -m '<commit message>'
```

提交后检查：

```bash
git log -1 --format=fuller
git log -1 --format=%B
```

提交正文必须出现完全一致的一行：

```text
Signed-off-by: Smillick <3185479846@qq.com>
```

如果已有 commit 缺少签署信息，在尚未推送或确认允许改写分支历史时使用：

```bash
git commit --amend --signoff --no-edit
```

不要把 GitCode 用户名 `SmillySmillick` 或 GitHub 用户名 `Smillaint` 写成 `Signed-off-by`。

## 3. 仓库位置

### 3.1 上游和个人 fork

```text
OpenHarmony 组织：     https://gitcode.com/openharmony
build 上游：           https://gitcode.com/openharmony/build
GitCode 个人主页：     https://gitcode.com/SmillySmillick
build fork：           https://gitcode.com/SmillySmillick/build
jsframework fork：     https://gitcode.com/SmillySmillick/third_party_jsframework
sane-airscan fork：    https://gitcode.com/SmillySmillick/third_party_sane-airscan
```

### 3.2 GitHub 项目日志和代码补丁

```text
仓库：https://github.com/Smillaint/Openharmony-Incremental-Compilation
本地：D:\workspace\Openharmony-Incremental-Compilation
```

截至本文提交前，GitHub `main` 已包含分析文档以及最近两个 `build` PR 的完整代码补丁，不再只是文字摘要：

```text
patches/build/sa-profile-incremental-0d530d7e.patch
patches/build/hap-signing-incremental-34aa8cba.patch
patches/build/README.md
```

补丁入口：

- [SA Profile 完整补丁](../patches/build/sa-profile-incremental-0d530d7e.patch)
- [HAP signing 完整补丁](../patches/build/hap-signing-incremental-34aa8cba.patch)
- [补丁说明](../patches/build/README.md)
- [最近两个 PR 的详细分析](recent-build-prs-20260812.md)

两个补丁由本地 GitCode fork 的正式 commit 直接导出，稳定 patch-id 已与原提交核对一致。

### 3.3 Windows 本地 fork

```text
build：                 D:\workspace\openharmony-build-sa
third_party_jsframework：D:\workspace\gitcode_pr\third_party_jsframework
third_party_sane-airscan：D:\workspace\gitcode_pr\third_party_sane-airscan
项目日志：              D:\workspace\Openharmony-Incremental-Compilation
```

修改正式 PR 时只进入对应的小仓，不复制整个 OpenHarmony 源码树。`build` 虽是整套构建系统仓，但 Git 只会提交明确暂存的文件。

## 4. 远程虚拟机

连接命令：

```bash
ssh -p 42247 -i ~/.ssh/id_ed25519 root@119.3.182.128
```

OpenHarmony 整仓路径：

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
```

常用路径：

```text
build 小仓：/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/build
构建输出： /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/out/rk3568
历史日志： /srv/workspace/action_incremental_logs_20260805
验证日志： /srv/workspace/action_incremental_logs_20260812
```

连接后先只读检查，不要直接切分支或清理输出：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
git -C build status --short --branch
git -C build log -5 --oneline --decorate
git -C build remote -v
ps -ef | grep -E '[b]uild\.sh|[n]inja'
```

私钥、令牌和密码不得写入仓库、日志或聊天输出。SSH 命令只能记录密钥文件路径，不能记录私钥内容。

## 5. 操作边界

1. 默认只读分析日志和代码。
2. 未明确授权时不要执行完整编译；给出可复制的编译命令，由仓库所有者手动运行。
3. GitCode 推送和 PR 创建由仓库所有者自行完成，因为需要其凭据。
4. 修改前记录当前分支、HEAD 和工作树；有实验改动时先保存 commit 或备份分支。
5. 正式 PR 必须从最新上游建立小分支，一个 PR 只处理一个明确根因。
6. 远程整仓可能使用和正式 PR 不同的 manifest 基线；正式分支与整仓兼容验证分支必须分离。
7. 读取和写入文本统一使用 UTF-8。
8. 不覆盖、不清理其他会话的工作树和 `out/rk3568`。

## 6. 已处理问题

### 6.1 `ark_jsf` 与 `gen_snapshot`

```text
仓库：  third_party_jsframework
分支：  fix/jsframework-incremental-actions
提交：  a280a42
结果：  最终零改动真实构建 ark_jsf=0、gen_snapshot=0
```

根因是生成目录交叉污染、runtime 和 `strip.native.min.js` 被无条件更新。修复后相同输入不再刷新输出。

### 6.2 `airscan_action`

```text
仓库：  third_party_sane-airscan
分支：  fix/airscan-incremental-action
提交：  37de4f9
结果：  最终零改动真实构建 airscan_action=0
```

根因是在源码目录重复应用补丁。修复改为复制到生成目录并只修改生成副本。

### 6.3 SA Profile 三个 Action

```text
Action： sa_profile_src_phone
        sa_profile_binary_phone
        phone_sa_profile_install_info
PR：     https://gitcode.com/openharmony/build/merge_requests/6965
分支：   codex/fix-sa-profile-incremental-build
提交：   0d530d7eb691276cd27d7109b1155a21c6c0c1cc
基线：   69f5e3070cf7dd14868ddd93f031d3a0f69178ff
DCO：    Signed-off-by: Smillick <3185479846@qq.com>
```

修改文件：

```text
ohos/sa_profile/sa_profile_binary.py
ohos/sa_profile/sa_profile_merge.py
ohos/sa_profile/sa_profile_source.py
ohos/sa_profile/src_sa_profile_process.py
scripts/util/file_utils.py
```

修复内容：

- SA 元数据按 `label` 稳定排序；
- JSON 按解析后的值比较；
- 内容相同时不重写 JSON；
- ZIP 使用原子输出，内容相同时不替换原文件。

2026-08-12 的整仓验证结论：修复有效。第二次真实构建中，`sa_profile_src_phone` 和 `sa_profile_binary_phone` 可能因上游 parts 链 dirty 被调度，但输出内容和 mtime 保持不变，Ninja `restat` 阻断后续传播；`phone_sa_profile_install_info` 未再次执行。

注意：`-n` dry-run 不会实际执行 Action，因此无法观察 `restat` 在执行后发现“输出未变化”并截断传播。dry-run 中显示派生的 `xx is dirty`，不能单独判定 SA 修复失败。

### 6.4 HAP signing 输出

```text
相关 Issue：https://gitcode.com/openharmony/build/issues/4663
分支：      fix-hap-sign-incremental-build
提交：      34aa8cba0c5fcb3344e2dd652c18027d69a71396
基线：      69f5e3070cf7dd14868ddd93f031d3a0f69178ff
DCO：       Signed-off-by: Smillick <3185479846@qq.com>
```

修改文件：

```text
ohos/app/app_internal.gni
scripts/app_sign.py
scripts/compile_app.py
scripts/util/build_utils.py
```

修改为每个签名 Action 声明独立 `sign_result.json`，记录 unsigned/signed HAP 的稳定路径和 SHA-256，并用内容感知的原子 JSON 写入避免无变化刷新。

HAP 本体仍可能因 `developtools/packing_tool/adapter/ohos/Compressor.java` 写入动态 ZIP entry 时间而变化。这属于 `developtools_packing_tool` 仓的独立根因，不能继续堆到 `build` PR。

### 6.5 NOTICE 和 packages 综合实验

NOTICE 输出稳定化已经过两轮验证，但 `collect_notice_files__phone` 仍可能因 `phone_parts_list` 上游 dirty 被调度。`codex/packages-action-incremental-fix-20260805` 同时混合多个实验提交，只能作为定位材料，不能整体提交正式 PR。

## 7. 原始 packages Action 当前状态

| Action | 当前状态 | 下一步 |
| --- | --- | --- |
| `sa_profile_src_phone` | PR !6965 已修复 | 补充非空 binary SA 产品场景 |
| `sa_profile_binary_phone` | PR !6965 已修复 | 检查含 `part_name_info.json` 的 ZIP 可复现性 |
| `phone_sa_profile_install_info` | PR !6965 已修复 | 不再修改尾端 Action |
| `check_seccomp_filter_name` | 根因确认，远程有实验提交 `9e2dcc48` | 从最新上游整理独立小 PR |
| `process_field_validate` | 根因确认，正式提交状态未确认 | 生成稳定成功输出并验证失败路径 |
| `collect_notice_files__phone` | NOTICE 自身稳定，受 parts 上游影响 | 追 `phone_parts_list` 的最早 dirty 节点 |
| `generate_host_symlink` | 自身 JSON 可稳定，受 host parts 输入影响 | 追 `all_parts_host.json` 上游 |
| `phone_hisysevent_install_info` | 自身输出可稳定，受 parts 链影响 | parts 稳定后复验 |
| `phone_parts_list` | 尚未收敛 | 当前 packages 列表中的优先分析项 |
| `phone_install_modules` | 存在真实 `.so` 和可执行文件重建输入 | 追最早重复链接模块，不跳过安装 Action |

validator 的直接根因：

```text
check_seccomp_filter_name
  GN 声明 check_seccomp_filter_name.txt，旧脚本成功时没有生成文件。

process_field_validate
  GN 声明 cfg_validate_result.txt，旧脚本没有生成文件。
```

合格修复必须生成固定成功标记、相同内容不刷新、验证失败仍返回非零，不能只创建空文件。

## 8. 下一阶段优先级

1. 从最新 `openharmony/build` 上游整理 `check_seccomp_filter_name` 独立正式分支；先审查实验提交，不整体 cherry-pick packages 分支。
2. 单独处理 `process_field_validate`，确认其参数、GN 输出和失败路径。
3. 使用 Ninja explain 沿 `phone_parts_list` 追到最早直接 dirty 的 parts 元数据生成节点。
4. 沿 `phone_install_modules` 找到第二轮最早重新链接的 `.so` 或可执行文件，并转到对应组件仓解决。
5. 在 `developtools_packing_tool` 仓分析 `Compressor.java` 的 ZIP entry 时间、顺序、权限和压缩参数，验证相同输入 HAP SHA-256 一致。

## 9. GN 与 Ninja 分析方法

### 9.1 先看工具帮助

```bash
prebuilts/build-tools/linux-x86/bin/gn help
prebuilts/build-tools/linux-x86/bin/gn help action
prebuilts/build-tools/linux-x86/bin/gn help copy
prebuilts/build-tools/linux-x86/bin/gn desc --help
prebuilts/build-tools/linux-x86/bin/ninja --help
prebuilts/build-tools/linux-x86/bin/ninja -t list
```

其他项目内可执行文件同样先运行 `<executable> --help`，确认真实参数后再调用。

### 9.2 使用 `gn desc` 确认 Target

```bash
prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 \
  //build/ohos/packages:sa_profile_src_phone

prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 \
  //build/ohos/packages:sa_profile_src_phone deps --tree

prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 \
  //build/ohos/packages:sa_profile_src_phone outputs
```

对其他 Action 替换 label。重点检查 target 类型、script、args、inputs、outputs、deps、depfile 和实际 Ninja 输出路径。

### 9.3 指导要求的快速 dry-run query

在已经完成至少一次真实收敛构建后运行：

```bash
./build.sh -p rk3568 --build-target make_all \
  --ninja-args=-dexplain \
  --ninja-args=-n \
  --ninja-args=-dstats 2>&1
```

它用于快速把 explain 和 stats 写入 `out/rk3568/build.log`。解释规则：

- `-n` 只模拟，不执行命令；
- Action 不执行就无法产生稳定输出，也无法让 Ninja 在执行后应用 `restat`；
- 所以下游 `xx is dirty` 可能只是上游 dirty 的派生结果；
- 必须继续向上追最早 dirty 节点，并结合真实第二轮构建验收。

### 9.4 直接 query 单个目标

```bash
prebuilts/build-tools/linux-x86/bin/ninja -C out/rk3568 \
  -n -d explain -d stats \
  obj/build/ohos/packages/sa_profile_src_phone.stamp

prebuilts/build-tools/linux-x86/bin/ninja -C out/rk3568 \
  -t query obj/build/ohos/packages/sa_profile_src_phone.stamp
```

目标路径必须先从 `gn desc`、`build.ninja` 或日志确认，不要猜。

## 10. 标准验证流程

### 10.1 第一次真实构建

编译由操作者执行：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
mkdir -p /srv/workspace/action_incremental_logs_20260812

{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_20260812/<topic>_first_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_20260812/<topic>_first_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_20260812/<topic>_first_ninja.log
```

### 10.2 快速 dry-run

```bash
{ time ./build.sh -p rk3568 --build-target make_all \
  --ninja-args=-dexplain \
  --ninja-args=-n \
  --ninja-args=-dstats; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_20260812/<topic>_dry_run_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_20260812/<topic>_dry_run_build.log
```

### 10.3 第二次真实构建

```bash
{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_20260812/<topic>_second_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_20260812/<topic>_second_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_20260812/<topic>_second_ninja.log
```

真实第二轮至少核对：

```bash
grep -nE 'ACTION .*<target>|is dirty|ninja explain|ninja stats' \
  /srv/workspace/action_incremental_logs_20260812/<topic>_second_build.log

stat <declared-output>
sha256sum <declared-output>
```

不要只数 Action 次数。Action 被真实上游带起但输出内容和 mtime 不变，且下游 stamp 没有重建，说明输出稳定化和 `restat` 正常；此时下一步应修上游，而不是继续给当前脚本加补丁。

## 11. dirty 根因分类

按以下顺序判断：

1. 声明输出缺失；
2. 输出内容每轮变化；
3. 内容相同但 mtime 被刷新；
4. depfile 缺失、格式错误或动态输入不完整；
5. 命令行、脚本或 GN 规则变化；
6. 上游依赖真实 dirty；
7. dry-run 无法模拟 `restat` 导致的派生 dirty。

日志末端的 `xx is dirty` 通常不是最早根因。沿 explain 链向上追，直到找到第一个不再由其他 dirty 目标解释的节点。

## 12. GitCode 正式 PR 流程

```bash
cd D:/workspace/openharmony-build-sa
git status --short --branch
git fetch upstream
git switch -c fix/<topic>-incremental-build upstream/master

git add <explicit-file-1> <explicit-file-2>
git diff --cached --check
git diff --cached --stat
git diff --cached

git config user.name 'Smillick'
git config user.email '3185479846@qq.com'
git commit --signoff -m '<message>'
git log -1 --format=%B
```

确认存在：

```text
Signed-off-by: Smillick <3185479846@qq.com>
```

之后只把推送命令交给仓库所有者：

```bash
git push -u origin fix/<topic>-incremental-build
```

不要向 `openharmony` 上游直接 push，不要代填令牌密码，不要擅自创建或合并 PR。

## 13. 新会话执行顺序

1. 阅读本文、[最近两个 PR 分析](recent-build-prs-20260812.md) 和 [补丁说明](../patches/build/README.md)。
2. 核对 DCO 配置必须是 `Smillick <3185479846@qq.com>`。
3. SSH 登录远程机，只读检查仓库、分支、HEAD、工作树和是否有编译进程。
4. 阅读最新 console、`build.log` 和 `.ninja_log`，不要先打补丁。
5. 用 `gn help`、`gn desc`、`ninja --help` 和 `ninja -t query` 确认 target 关系。
6. 用 `-n -d explain -d stats` 找最早 dirty 节点，并明确 dry-run 的 `restat` 边界。
7. 报告直接根因、派生 dirty、涉及仓库、最小修改文件和验证方案。
8. 根因明确后从最新上游创建独立小分支，避免混入 packages 综合实验。
9. 不自行完整编译；输出第一轮、dry-run、第二轮真实构建命令。
10. 用户完成构建后读取全部日志、mtime、hash 和 Ninja explain 再判断修复是否成立。
11. 提交前检查 DCO；GitCode 推送、PR 和门禁由仓库所有者完成。
