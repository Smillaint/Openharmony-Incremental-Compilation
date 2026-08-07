# OpenHarmony Action 增量编译并行分析提示词

将本文完整提供给另一台主机上的终端代理。该代理负责并行分析，不得与其他会话争用远程工作树或构建输出。

## 任务目标

继续定位 OpenHarmony `rk3568` 无源码变化时仍重复执行的 Action。优先分析 `phone_parts_list` 上游 parts 元数据聚合链，并解释它如何继续带起 `collect_notice_files__phone`、`generate_host_symlink` 和 `phone_hisysevent_install_info`。

当前另一个会话正在处理 `check_seccomp_filter_name` 的声明输出缺失问题。除非用户明确移交，不要修改该 Action，避免产生冲突。

所有结论必须区分：

- Action 自身输出缺失；
- 输出内容真实变化；
- 内容相同但时间戳变化；
- depfile 内容或顺序变化；
- 上游依赖 dirty；
- 真实编译或链接输入发生变化。

## 远程连接

另一台主机需要预先安全配置对应私钥。不要在对话、日志或仓库中输出私钥内容。

```bash
ssh -p 42247 \
  -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=6 \
  root@119.3.182.128
```

非交互连接测试：

```bash
ssh -p 42247 \
  -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  -o BatchMode=yes \
  -o ConnectTimeout=15 \
  root@119.3.182.128 \
  'whoami; hostname; pwd'
```

远程源码根目录：

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
```

`build` 子仓库：

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/build
```

历史分析日志：

```text
/srv/workspace/action_incremental_logs_20260805
/srv/workspace/action_incremental_logs_20260807
```

进入远程环境后先设置 UTF-8：

```bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
```

## 并行操作边界

远程完整源码和 `out/rk3568` 由多个会话共享，必须遵守：

1. 默认只读分析，不执行 `build.sh`。
2. 不切换集成工作树中 `code/build` 的分支。
3. 不修改、移动或删除 `out/rk3568`。
4. 不运行 `git reset --hard`、`git checkout -- <file>`、`git clean` 或递归删除。
5. 不覆盖其他会话产生的日志。
6. 不在共享工作树中使用 `git stash` 保存未知改动。
7. 发现工作树非干净时，先记录文件列表并停止写操作。
8. 需要实验代码时，优先为 `build` 子仓创建独立 Git worktree；独立 worktree只用于编辑、静态检查和提交，不能直接用于完整 OpenHarmony 构建。
9. 完整编译由用户在集成工作树中手动执行。

开始分析前执行：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/build

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline --decorate -12
git remote -v
```

必须先汇报当前分支、HEAD 和工作树状态。

## Git 操作规范

### 只读分析

优先使用：

```bash
git diff
git diff --stat
git log --oneline --decorate --graph -20
git show --stat <commit>
git blame -L <start>,<end> <file>
```

### 独立实验 worktree

只有用户批准修改后才能创建。先确认目标路径不存在：

```bash
test ! -e /srv/workspace/build_parallel_phone_parts
```

再从明确基线创建：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/build

git worktree add \
  -b codex/phone-parts-analysis-20260807 \
  /srv/workspace/build_parallel_phone_parts \
  <明确的基线提交>
```

不得默认使用最新 `gitcode/master` 替换集成源码中的 manifest 固定版本。最终 PR 分支和远程构建验证分支需要分开：

- 验证分支基于完整源码的 manifest 兼容版本；
- 最终 PR 基于 OpenHarmony 官方仓最新主分支；
- 只移植经过验证且边界清晰的改动。

提交前配置正确身份：

```bash
git config user.name 'Smillick'
git config user.email '3185479846@qq.com'
```

提交必须带 DCO：

```bash
git add <明确文件列表>
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit --signoff -m '<简洁提交说明>'
```

不得向 `https://gitcode.com/openharmony/build` 直接推送。用户 fork 为：

```text
https://gitcode.com/SmillySmillick/build
```

用户负责创建 PR 和处理门禁。未经明确要求不要创建 PR。

## 已完成项目

以下 Action 已经修复并通过两轮完整构建验证，不要重复修改：

```text
sa_profile_src_phone
sa_profile_binary_phone
phone_sa_profile_install_info
```

对应信息：

```text
PR: https://gitcode.com/openharmony/build/merge_requests/6965
branch: codex/fix-sa-profile-incremental-build
commit: 0d530d7eb691276cd27d7109b1155a21c6c0c1cc
```

验证结果：第二轮三个 SA Profile Action 均未再次执行，对应 JSON 和 ZIP 保持第一轮时间戳。

## 剩余问题列表

### 1. check_seccomp_filter_name

已确认 GN 声明 `check_seccomp_filter_name.txt`，但脚本成功后不生成文件。另一个会话正在处理，当前并行会话不要修改。

### 2. process_field_validate

已确认 GN 声明 `cfg_validate_result.txt`，但脚本不生成文件。它和 `check_seccomp_filter_name` 都依赖 `phone_install_modules`，因此补齐输出后仍可能被 dirty 的上游依赖带起。

### 3. phone_parts_list

当前并行分析的首要目标。第二轮仍观察到：

```text
all_parts_host.json
all_parts_info.json
```

发生更新时间变化。需要从下列节点寻找最早 dirty 原因：

```text
generate_src_installed_info
generate_host_info
各 part_name_info
gen_binary_installed_info
merge_all_parts
phone_parts_list
```

已发现值得检查但尚不能直接修改的脚本：

```text
build/ohos/common/binary_install_info.py
build/ohos/common/merge_all_subsystem.py
```

### 4. collect_notice_files__phone

NOTICE 自身输入和 ZIP 可以保持稳定，但它硬依赖 `phone_parts_list`。不要继续给 NOTICE 尾端增加跳过逻辑。

### 5. generate_host_symlink

自身 JSON 可以稳定，仍受 `all_parts_host.json` 变化影响。先解决 host parts 元数据来源。

### 6. phone_hisysevent_install_info

HiSysEvent JSON 和 ZIP 自身可以稳定，仍可能被 `phone_parts_list` 带起。

### 7. phone_install_modules

第二轮存在真实重新链接的动态库和可执行文件。不得删除 depfile 中的真实输入或强制跳过该 Action。需要先定位最早发生无效重建的模块。

## 优先分析任务

本会话只读分析 `phone_parts_list` 链，按以下顺序执行。

### 1. 定位目标输出和 Ninja 规则

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code

grep -R -n -A20 -B10 \
  'phone_parts_list\|merge_all_parts\|generate_host_info\|generate_src_installed_info' \
  build/ohos 2>/dev/null
```

### 2. 直接 dry-run，不执行编译

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -n -d explain \
  obj/build/ohos/packages/phone_parts_list.stamp \
  > /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_explain.log 2>&1
```

只保存本会话独有的 `parallel_` 日志，不覆盖其他日志。

### 3. 从最早 dirty 原因开始阅读

```bash
sed -n '1,240p' \
  /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_explain.log

grep -n -E \
  'dirty|missing|all_parts_host.json|all_parts_info.json|merge_all_parts|generate_host_info|generate_src_installed_info' \
  /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_explain.log \
  | head -300
```

不要从日志末尾的 `phone_parts_list` 倒推为根因，必须找到最早变脏的输入。

### 4. 查询关键目标依赖

先从 explain 日志确定准确输出路径，再执行：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -C out/rk3568 \
  -t query \
  '<准确的目标输出路径>'
```

### 5. 检查输出内容和时间戳

```bash
find out/rk3568 \
  \( -name 'all_parts_host.json' -o -name 'all_parts_info.json' \) \
  -exec stat -c '%n %s %y' {} \;
```

必要时比较日志中两轮构建对应文件的内容摘要，但不要仅凭摘要变化下结论；还需要用 JSON 解析比较结构和列表顺序。

## 编译命令

终端代理不得自行执行完整构建，只能把以下命令输出给用户手动执行。

第一轮：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code

mkdir -p /srv/workspace/action_incremental_logs_20260807

{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_first_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_first_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_first_ninja.log
```

第二轮：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code

{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_second_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_second_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_20260807/parallel_phone_parts_second_ninja.log
```

如果用户只需要原始命令，使用：

```bash
./build.sh -p rk3568 --build-target make_all 2>&1
```

## 验证标准

完整构建后需要分别确认：

1. 两轮构建是否成功。
2. 第二轮目标 Action 是否出现。
3. 相关输出内容是否变化。
4. 输出时间戳是否变化。
5. Ninja explain 给出的直接 dirty 原因。
6. depfile 是否包含全部真实输入。
7. 是否意外增加其他 Action、编译或链接步骤。

Action 第二轮仍出现不等于修复失败。如果它仅被尚未稳定的上游依赖带起，而自身输出内容和时间戳保持不变，需要明确记录这一层关系。

## 汇报格式

每轮工作完成后输出：

1. 当前分支、HEAD 和工作树状态；
2. 本轮是否只读；
3. 最早 dirty 节点；
4. 直接证据，包括日志行、文件路径和时间戳；
5. 已确认根因与尚未确认的推断；
6. 建议修改的最小文件范围；
7. 是否适合独立 PR；
8. 是否需要用户执行完整构建；
9. 如果尚未确认根因，只给方案，不连续叠加补丁。

现在先连接远程机，检查 Git 状态，然后只读生成并分析 `parallel_phone_parts_explain.log`。完成根因定位前不要修改代码，不要执行完整构建。
