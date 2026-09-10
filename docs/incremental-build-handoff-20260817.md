# OpenHarmony 增量编译项目交接说明（2026-08-17）

本文是 2026-08-17 起的当前交接入口。后续工作默认使用 2026-08-16 整仓快照，旧整仓只保留历史验证证据，不再作为新补丁的默认验证环境。

## 1. 当前整仓

### 新整仓（默认）

```text
/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code
```

`build` 子仓状态：

```text
仓库：/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code/build
基线：6c8feef35cad81feff41eb237cd070787997a2b7
分支：incremental-build-all-validation-20260816
HEAD：e00d6de2884c1822315f8b44ba8e5b938f0abb70
状态：clean
```

新整仓中的 IDL 补丁与旧整仓已验证提交 `4fa37075` 的稳定 patch-id 相同：

```text
1558d471fa6e6fae0ea34b3e376582057a9a570b
```

已经完成：

- `git diff --check`；
- GN `format --dry-run` 解析；
- Author、Committer、Signed-off-by 检查；
- build 个人 fork 和仓库级 SSH key 配置。

新整仓已经迁移 build、packing_tool、jsframework 和 sane-airscan 中边界清楚的增量构建修复，尚未执行完整构建。完整构建必须由操作者手动运行。

### 旧整仓（历史验证）

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
```

旧整仓保留 IDL 两轮成功构建和其他历史修复的日志、分支与产物。不要删除或用新日志覆盖：

```text
/srv/workspace/action_incremental_logs_20260817/idl_common_outputs
```

### 新整仓中需要保留的已有修改

以下子仓在迁移前已不是 clean，本次没有修改：

```text
third_party/jsframework：package-lock.json 已修改
third_party/sane-airscan：多个源码文件已修改
```

后续不得使用 `git reset --hard`、`git clean` 或 checkout 覆盖这些文件。

## 1.1 2026-08-17 迁移结果

```text
build
  分支：incremental-build-all-validation-20260816
  基线：6c8feef35cad81feff41eb237cd070787997a2b7
  c08d319f83666f1da7affee73a568a437d289cf3  SA profile
  0008197c18e088abdc43221328c55a99644af1d4  HAP signing，同时包含 compile_app 的相同修复
  e00d6de2884c1822315f8b44ba8e5b938f0abb70  IDL common outputs
  状态：clean

developtools/packing_tool
  分支：hap-reproducible-archive-validation-20260816
  基线：9cac80b676fb5fe72fdd2039e7749087caaa85a9
  4bcb6aaba5804317714c2ff1748746e53db66591  可重复 HAP ZIP 时间戳
  状态：clean

third_party/jsframework
  分支：jsframework-incremental-actions-validation-20260816
  基线：a21a6f36694c08ac0b83d077577526a7ca086d57
  869aec84388ae6bc5f8bb063ac32b9528cdb0d51  保留未变化的增量输出
  d0752be1bbf8516ee4d58b816231d1dd2007e48e  稳定共享运行时目录时间戳
  状态：迁移成功；迁移前已有 package-lock.json 修改仍保留

third_party/sane-airscan
  分支：airscan-incremental-action-validation-20260816
  基线：6bd973c4bd430e01f8e7e787cdb53d9e3fcb9014
  bb4ab646aa026a7c793d9838e2ee6d4612cfd100  在输出目录生成补丁源码
  5ed21a6722eeec9a16236446f076987b904d3db6  只编译生成后的补丁源码
  262f3134982672f2e9fd9f7b02262aacf3fd9441  排除 OHOS 不支持的后端
  状态：迁移成功；迁移前已有的 18 个源码修改仍保留
```

所有新迁移提交均使用：

```text
Smillick <3185479846@qq.com>
Signed-off-by: Smillick <3185479846@qq.com>
```

已通过 `git diff --check`、IDL GN dry-run、jsframework `bash -n` 和 airscan Python AST 解析。未执行完整构建。

没有合入组合验证分支的旧修改：

- `action_incremental_fix_20260804`、`packages-action-incremental-fix-20260805` 和 `check-seccomp-output-fix-20260807` 是相互继承的实验链，包含旧 IDL、NOTICE、packages 和 SA 多类修改，提交边界混合且未完成闭环；
- 这些提交仍完整保留在旧整仓，不能作为一个正式 PR 或直接叠加到当前组合验证分支；
- 新分支用于整仓兼容验证，不推送为正式综合 PR。正式 PR 继续按一个根因一个分支维护。

## 2. SSH 连接

Windows 主机连接虚拟机：

```powershell
ssh -p 42247 `
  -i C:\Users\31854\.ssh\id_ed25519 `
  -o IdentitiesOnly=yes `
  -o ServerAliveInterval=30 `
  -o ServerAliveCountMax=6 `
  root@119.3.182.128
```

进入虚拟机后：

```bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

cd /srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code
```

主机登录私钥和 GitCode 私钥用途不同：

```text
主机登录：C:\Users\31854\.ssh\id_ed25519
虚拟机访问 GitCode：/root/.ssh/id_ed25519_github_openharmony
```

禁止读取、复制、打印或提交私钥内容。

## 3. GitCode 身份与远端

所有 GitCode 正式提交统一使用：

```text
Author：Smillick <3185479846@qq.com>
Committer：Smillick <3185479846@qq.com>
Signed-off-by：Smillick <3185479846@qq.com>
GitCode 账号：SmillySmillick
```

配置：

```bash
cd /srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code/build

git config user.name 'Smillick'
git config user.email '3185479846@qq.com'
git config core.sshCommand \
  'ssh -i /root/.ssh/id_ed25519_github_openharmony -o IdentitiesOnly=yes'
```

新整仓 `build` 当前远端：

```text
gitcode  https://gitcode.com/openharmony/build
fork     git@gitcode.com:SmillySmillick/build.git
```

只向 `fork` 推送，不得向 OpenHarmony 上游 `gitcode` 直接推送。

## 4. 当前工作

### 4.1 IDL common 输出声明

正式 PR：

```text
PR：https://gitcode.com/openharmony/build/merge_requests/6982
远端分支：fix-idl-common-outputs
正式提交：4fa37075bfa8a0f3bb36f0394adf54577b0770f2
Change-Id：Ieded5c79d24d594b9dd704b4851ea5fb9c23724d
```

修复内容：

- 修正 `sources_common` 中 `I` 开头文件的双 `i` 输出名；
- 本 target 生成的 common IDL 才进入输出和编译源计算；
- source-absolute common IDL 仅作为 action 输入，不重复声明输出；
- 保持单个 IDL action，不增加 staging、导出脚本或第二个生成 action。

旧整仓验证：

- 第一轮 `rk3568 make_all` 成功；
- 第二轮 `rk3568 make_all` 成功；
- 第二轮没有再次执行 `partner_device_agent` 和 `partner_agent_extension_interface` 的 IDL action；
- 没有 `iifusion_connectivity_types.*` 缺失输出。

新整仓迁移提交：

```text
分支：fix-idl-common-outputs-validation-20260816
提交：d88b5e7b33ab27b0e96be632d5dd35d0497a169f
基线：6c8feef35cad81feff41eb237cd070787997a2b7
```

该分支只用于新快照兼容验证，暂未推送 GitCode。正式 PR 分支仍为 `fix-idl-common-outputs`。

### 4.2 compile_app 声明输出

```text
仓库：build
分支：fix/compile-app-stable-output
提交：918e4c5bc99f0441b5b5d2fe5afc62492ecdad01
Change-Id：I447d351188a26905ca234e3c62a9b7f482960ce5
远端：SmillySmillick/build
```

修复内容：unsigned HAP/HSP 路径排序、SHA-256 声明、确定性 JSON、原子写入、内容不变时保留 mtime。该修复稳定 action 的声明输出，不负责消除上游 `.so` 的真实 dirty。

该补丁尚未迁移到新整仓。迁移时必须建立独立分支，不得与 IDL 修复合并。

### 4.3 HAP signing

```text
仓库：build
PR：!6974
分支：fix-hap-sign-incremental-build
提交：34aa8cba0c5fcb3344e2dd652c18027d69a71396
```

修复每个签名 action 的独立声明输出，使用稳定的 `sign_result.json` 记录 unsigned/signed HAP 路径与 SHA-256，并在内容不变时保留输出。

### 4.4 packing_tool 可重复 HAP

```text
仓库：developtools_packing_tool
PR：https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556
分支：fix/hap-reproducible-archive
提交：dcbbc78ada8c90cb31542ecc385bb7d5b5faddbc
```

修复 ZIP entry 动态时间，使相同输入连续打包得到相同 HAP 字节和 SHA-256。它不负责消除上游 native library 的重新链接。

### 4.5 原始十个 packages action

严格按完整闭环统计：

```text
已完成：3/10
部分处理：6/10
尚未收敛：1/10
```

已完成：

- `sa_profile_src_phone`；
- `sa_profile_binary_phone`；
- `phone_sa_profile_install_info`。

部分处理：

- `check_seccomp_filter_name`：根因明确，有实验补丁，待独立正式 PR；
- `process_field_validate`：根因明确，待实现稳定成功输出；
- `collect_notice_files__phone`：自身输出稳定，仍受 parts 上游影响；
- `generate_host_symlink`：自身 JSON 稳定，仍受 host parts 输入影响；
- `phone_hisysevent_install_info`：自身输出稳定，仍受 parts 链影响；
- `phone_install_modules`：IDL 重复构建链已修，仍有其他 `.so`/可执行文件重建输入。

尚未收敛：

- `phone_parts_list`。

## 5. TODO

按优先级执行：

1. 在 2026-08-16 新整仓对组合迁移分支执行两轮真实 `make_all`。
2. 第二轮确认 IDL、SA profile、HAP signing、compile_app、packing_tool、jsframework 和 airscan 相关 action 是否仍被无效重复调度。
3. 重新触发 PR !6982 门禁，优先读取 `error.log` 第一条真实错误，不以 HB/Ninja 外层 traceback 作为根因。
4. 组合验证通过后，再分别决定各正式 PR 是否需要更新到新基线；不要把组合验证分支推送成一个正式 PR。
5. 整理 `check_seccomp_filter_name` 独立正式 PR。
6. 实现并验证 `process_field_validate` 的稳定成功输出及失败路径。
7. 追踪 `phone_parts_list` 聚合链最早 dirty 节点。
8. 继续分解 `phone_install_modules` 中除 IDL 外的重复链接模块。
9. 跟踪 SA、HAP signing、packing_tool PR 的 DCO、门禁和最终合入状态。

## 6. 规范修复流程

### 6.1 开始前只读检查

```bash
CODE_ROOT=/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code
REPO_ROOT="$CODE_ROOT/build"

git -C "$REPO_ROOT" status --short --branch
git -C "$REPO_ROOT" branch --show-current
git -C "$REPO_ROOT" rev-parse HEAD
git -C "$REPO_ROOT" log -10 --oneline --decorate
git -C "$REPO_ROOT" remote -v
ps -ef | grep -E '[b]uild\.sh|[n]inja'
```

如果工作树不干净，先确认修改归属。禁止覆盖未知修改。

### 6.2 分支和补丁边界

- 一个 PR 只处理一个根因；
- 正式 PR 分支基于合适的上游基线；
- 整仓验证分支基于 manifest 固定基线；
- 两者通过 patch-id 或完整 diff 确认补丁等价；
- 不把 compile_app、HAP signing、IDL、validator 等不同根因放进同一提交。

新整仓验证分支示例：

```bash
cd "$REPO_ROOT"
git switch -c <topic>-validation-20260816 <manifest-base>
git cherry-pick <verified-commit>
```

### 6.3 静态检查

```bash
git diff --check <base>..HEAD
git diff --stat <base>..HEAD
git diff <base>..HEAD -- <explicit-files>

cd "$CODE_ROOT"
prebuilts/build-tools/linux-x86/bin/gn format --dry-run \
  build/config/components/idl_tool/idl.gni
```

`gn format --dry-run` 只用于解析和格式检查，不能代替 `gn gen` 或真实构建。

补丁迁移后核对 patch-id：

```bash
git show --pretty=format: <old-commit> | git patch-id --stable
git show --pretty=format: <new-commit> | git patch-id --stable
```

### 6.4 Git 提交

```bash
cd "$REPO_ROOT"

git config user.name 'Smillick'
git config user.email '3185479846@qq.com'

git add -- <explicit-files>
git diff --cached --check
git diff --cached --stat
git diff --cached

git commit --signoff -m '<subject>' -m '<body>'

git show -s --format=fuller HEAD
git show -s --format=%B HEAD
```

提交必须包含：

```text
Signed-off-by: Smillick <3185479846@qq.com>
Change-Id: I...
```

禁止使用 GitCode 网页默认的 noreply 邮箱。

### 6.5 第一轮真实构建

构建由操作者执行：

```bash
cd /srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code

LOG_DIR=/srv/workspace/action_incremental_logs_20260817/new_snapshot
mkdir -p "$LOG_DIR"
set -o pipefail

./build.sh -p rk3568 --build-target make_all 2>&1 \
  | tee "$LOG_DIR/first_console.log"

BUILD_STATUS=${PIPESTATUS[0]}

cp out/rk3568/build.log "$LOG_DIR/first_build.log" 2>/dev/null || true
cp out/rk3568/error.log "$LOG_DIR/first_error.log" 2>/dev/null || true
cp out/rk3568/.ninja_log "$LOG_DIR/first_ninja.log" 2>/dev/null || true

echo "BUILD_STATUS=$BUILD_STATUS"
```

失败时先读取：

```bash
sed -n '1,240p' out/rk3568/error.log
grep -n -B10 -A30 -E \
  'ERROR at|FAILED:|ninja: error|Traceback|does not exist|duplicate output' \
  "$LOG_DIR/first_console.log" | head -1000
```

### 6.6 第二轮增量构建

第一轮成功后，不修改源码，执行第二轮：

```bash
cd /srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code

LOG_DIR=/srv/workspace/action_incremental_logs_20260817/new_snapshot
mkdir -p "$LOG_DIR"
set -o pipefail

./build.sh -p rk3568 --build-target make_all 2>&1 \
  | tee "$LOG_DIR/second_console.log"

BUILD_STATUS=${PIPESTATUS[0]}

cp out/rk3568/build.log "$LOG_DIR/second_build.log" 2>/dev/null || true
cp out/rk3568/error.log "$LOG_DIR/second_error.log" 2>/dev/null || true
cp out/rk3568/.ninja_log "$LOG_DIR/second_ninja.log" 2>/dev/null || true

echo "BUILD_STATUS=$BUILD_STATUS"
```

IDL 当前验证项：

```bash
grep -E \
  'ACTION .*partner_device_agent|ACTION .*partner_agent_extension_interface|iifusion_connectivity_types|ifusion_connectivity_types' \
  "$LOG_DIR/second_console.log" || true
```

验收不能只看 build success；还要确认目标 action、输出和下游是否仍被重复调度。

### 6.7 远端推送

首次推送新分支：

```bash
cd "$REPO_ROOT"

git status --short --branch
git show -s --format=fuller HEAD
git show -s --format=%B HEAD

git push -u fork HEAD:refs/heads/<branch>
```

更新已有 PR 分支前先读取远端 HEAD：

```bash
git ls-remote fork refs/heads/<branch>
```

只有在确认旧远端提交后才使用：

```bash
git push \
  --force-with-lease=refs/heads/<branch>:<expected-old-commit> \
  fork HEAD:refs/heads/<branch>
```

禁止：

```text
git push --force
向 gitcode（OpenHarmony 上游）直接 push
未核对远端 HEAD 就覆盖已有 PR 分支
```

推送后重新核验：

```bash
git ls-remote fork refs/heads/<branch>
git fetch fork <branch>
git show -s --format=fuller FETCH_HEAD
git show -s --format=%B FETCH_HEAD
```

### 6.8 DCO 和门禁

1. 确认远端 Author、Committer、Signed-off-by 均为固定身份；
2. DCO 未自动刷新时，在 PR 评论区输入 `check dco`；
3. 触发门禁后优先看最早失败任务及其 `error.log`；
4. HB、GN、Ninja 外层 traceback 只说明阶段，不是最终根因；
5. 门禁基线问题必须用日志证据区分，不能直接归因于 PR 或门禁。

## 7. 安全和工作约束

- 所有文本按 UTF-8 读写；
- 默认由操作者执行完整构建，分析会话只修改、给命令、读取日志；
- 不执行 `git reset --hard`、`git clean` 或递归删除；
- 不覆盖其他分支、子仓或未知工作树修改；
- 不删除真实依赖、不跳过校验、不伪造成功输出；
- 相同内容必须尽量保留原文件和 mtime；
- 失败路径必须保持非零退出，不得留下虚假成功标记；
- 不在仓库、日志或聊天中保存密钥、令牌和口令；
- 未完成两轮验证前不得声称增量问题已经闭环。
