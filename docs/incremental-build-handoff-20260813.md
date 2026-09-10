# OpenHarmony 增量编译项目统一交接说明（2026-08-13）

本文是新会话、新模型或另一台分析主机的当前入口。历史过程按需读取旧文档，不得用旧状态覆盖本文结论。

当前工作的核心原则：先找最早直接 dirty 节点，再决定是否修改；不能把 dry-run 的派生 `is dirty`、真实上游重建和当前 Action 自身输出不稳定混为一谈。

## 1. 当前结论摘要

### 已完成

- `ark_jsf`、`gen_snapshot`：已修复，零改动构建不再执行。
- `airscan_action`：已修复，零改动构建不再执行。
- `sa_profile_src_phone`、`sa_profile_binary_phone`、`phone_sa_profile_install_info`：已通过 PR !6965 修复输出稳定性。
- HAP signing 声明输出：已通过 `build` PR !6974 修复。
- HAP ZIP entry 动态时间：`developtools_packing_tool` 补丁已完成、验证并上传个人 fork。
- 虚拟机现已能使用独立 SSH Key 访问 GitCode 个人 fork，无需令牌。

### 尚未闭环

- `Telephony_Data_Storage_compile_app` 和 `Contacts_DataAbility_compile_app` 仍会因上游 `.so` dirty 被调度。
- `build/scripts/compile_app.py` 会无条件重写 `unsigned_hap_path_list.json`，已确认最小修复方案，但尚未实施。
- `libtel_telephony_data.z.so` 和 `libcontactsdataability.z.so` 的最早 dirty 根因尚未继续追踪。
- 原 packages 列表中的 `check_seccomp_filter_name`、`process_field_validate`、`phone_parts_list`、`phone_install_modules` 等仍有待处理项。

## 2. 操作约束

1. 所有文本按 UTF-8 读取和写入。
2. 默认只读检查代码和日志；未收到明确指令时不启动完整构建。
3. 修改前必须记录仓库、分支、HEAD 和工作树状态。
4. 不执行 `git reset --hard`、`git clean` 或递归删除，不覆盖其他会话的修改。
5. 完整编译通常由操作者手动执行，分析会话只提供命令并读取结果。
6. 一个正式 PR 只解决一个仓库内边界清晰的根因。
7. 不删除真实依赖、不跳过必要校验、不伪造空输出。
8. 成功输出必须真实存在；内容不变时应保留原文件和 mtime。
9. 不在仓库、日志或聊天中保存私钥、令牌、口令。
10. GitCode PR、门禁和最终合入由仓库所有者处理。

## 3. 身份和 DCO

账号用途：

| 用途 | 身份 |
| --- | --- |
| 所有 GitCode 正式提交的作者/DCO | `Smillick <3185479846@qq.com>` |
| GitCode 账号 | `SmillySmillick` |
| GitHub 账号 | `Smillaint` |

所有提交到 GitCode 的正式 commit 必须统一使用以下身份，禁止使用 GitCode 网页默认的
`SmillySmillick <SmillySmillick@noreply.gitcode.com>` 身份和邮箱：

```bash
git config user.name 'Smillick'
git config user.email '3185479846@qq.com'
git commit --signoff -m '<message>'
git log -1 --format=fuller
git log -1 --format=%B
```

期望签署行：

```text
Signed-off-by: Smillick <3185479846@qq.com>
```

推送前必须同时检查 Author、Committer 和 Signed-off-by：

```bash
git show -s --format=fuller HEAD
git show -s --format=%B HEAD
```

推送或更新 PR 后还必须重新 fetch 远端分支并检查远端 commit，不能只验证本地提交。
如果 PR 中仍包含错误身份的旧 commit，应使用正确身份重建或 amend commit，并通过
`git push --force-with-lease` 安全替换远端分支；不得使用无 lease 的强制推送。

packing_tool PR !1556 曾因远端旧提交 `ebbb276ed54590413001979c7a501d42a7cf1cfc`
使用 `SmillySmillick@noreply.gitcode.com` 而未通过 DCO。2026-08-13 已将 PR 分支替换为：

```text
commit：dcbbc78ada8c90cb31542ecc385bb7d5b5faddbc
Author：Smillick <3185479846@qq.com>
Committer：Smillick <3185479846@qq.com>
Signed-off-by：Smillick <3185479846@qq.com>
Change-Id：I6d4fbc122292b2cd4925e0cb718c7aafde4ce81e
```

GitCode Git Hooks 已通过，远端重新 fetch 后的提交元数据也已核验。PR 评论区仍需输入
`check dco` 触发 DCO 重新检查。

## 4. 远程虚拟机和 SSH

### 4.1 从本机连接虚拟机

Linux/macOS 风格：

```bash
ssh -p 42247 \
  -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=6 \
  root@119.3.182.128
```

Windows 私钥路径：

```text
C:\Users\31854\.ssh\id_ed25519
```

该密钥仅用于登录虚拟机，不是 GitCode 仓库密钥。

### 4.2 虚拟机访问 GitCode 的新 SSH 链路

2026-08-13 已在 GitCode 账号 `SmillySmillick` 登记虚拟机公钥：

```text
名称：openharmony-build-server
类型：ssh-ed25519
注释：openharmony-action-fixes@build-server
状态：永不过期
```

虚拟机对应私钥路径：

```text
/root/.ssh/id_ed25519_github_openharmony
```

不得复制、打印或提交该私钥。认证测试已经成功：

```text
remote: Welcome to GitCode, SmillySmillick
```

packing_tool 仓使用仓库级配置：

```bash
git config core.sshCommand \
  'ssh -i /root/.ssh/id_ed25519_github_openharmony -o IdentitiesOnly=yes'
```

这不会影响整机上的其他 Git 仓库。

### 4.3 完整源码位置

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
```

常用路径：

```text
build 仓：
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/build

packing_tool 仓：
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/developtools/packing_tool

构建输出：
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/out/rk3568

最新日志：
/srv/workspace/action_incremental_logs_20260813
```

连接后先检查：

```bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
git -C build status --short --branch
git -C developtools/packing_tool status --short --branch
ps -ef | grep -E '[b]uild\.sh|[n]inja'
```

## 5. 代码托管位置

### OpenHarmony 上游

```text
组织：https://gitcode.com/openharmony
build：https://gitcode.com/openharmony/build
packing_tool：https://gitcode.com/openharmony/developtools_packing_tool
```

### GitCode 个人 fork

```text
主页：https://gitcode.com/SmillySmillick
build：https://gitcode.com/SmillySmillick/build
packing_tool：https://gitcode.com/SmillySmillick/developtools_packing_tool
third_party_jsframework：https://gitcode.com/SmillySmillick/third_party_jsframework
third_party_sane-airscan：https://gitcode.com/SmillySmillick/third_party_sane-airscan
```

远程 packing_tool 仓当前 remote：

```text
gitcode  https://gitcode.com/openharmony/developtools_packing_tool
fork     git@gitcode.com:SmillySmillick/developtools_packing_tool.git
```

### GitHub 项目日志

```text
仓库：https://github.com/Smillaint/Openharmony-Incremental-Compilation
本地：D:\workspace\Openharmony-Incremental-Compilation
```

### Windows 本地仓库

```text
build：D:\workspace\openharmony-build-sa
packing_tool：D:\workspace\openharmony-developtools-packing-tool
项目日志：D:\workspace\Openharmony-Incremental-Compilation
```

## 6. HAP 可重复打包修复

### 6.1 对应 Action

```text
//base/telephony/telephony_data:Telephony_Data_Storage_compile_app
//applications/standard/contacts_data:Contacts_DataAbility_compile_app
```

它不是原始 `//build/ohos/packages:*` 十个 Action 中的一项，而是后续发现的两个 HAP 编译 Action。

### 6.2 根因和修改

仓库：`developtools_packing_tool`

文件：

```text
adapter/ohos/Compressor.java
```

根因：打包时 ZIP entry 使用当前时间，相同输入连续打包会得到不同 HAP 字节和 SHA-256。

修复内容：

- 引入 `FileTime`；
- 定义固定 ZIP entry 时间 `1546272000000L`，即 `2019-01-01 00:00:00`；
- 对普通文件/JSON entry 设置固定时间；
- 对并行压缩的 native library entry 设置固定时间；
- 对 STORED entry 和空目录设置固定时间；
- 统一通过 `setFixedZipEntryTime(ZipEntry)` 处理。

### 6.3 GitCode 状态

```text
fork：https://gitcode.com/SmillySmillick/developtools_packing_tool
branch：fix/hap-reproducible-archive
commit：dcbbc78ada8c90cb31542ecc385bb7d5b5faddbc
base：9cac80b676fb5fe72fdd2039e7749087caaa85a9
Change-Id：I6d4fbc122292b2cd4925e0cb718c7aafde4ce81e
diff：1 file changed, 9 insertions(+), 1 deletion(-)
PR：!1556
PR URL：https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556
DCO：远端提交身份已修复，需在 PR 评论区输入 `check dco` 重新触发检查
```

直接查看：

```text
分支：
https://gitcode.com/SmillySmillick/developtools_packing_tool/tree/fix/hap-reproducible-archive

对比：
https://gitcode.com/SmillySmillick/developtools_packing_tool/compare/master...fix%2Fhap-reproducible-archive
```

远程整仓验证分支：

```text
branch：hap-reproducible-archive-validation-20260812
commit：9ba2cbafdd34943e14ffa7017c57015c2fa4391d
status：clean
```

该验证提交与正式补丁内容一致，包含正确 Change-Id。

### 6.4 已完成验证

新 jar：

```text
out/rk3568/obj/developtools/packing_tool/jar/app_packing_tool.jar
SHA-256：fa8ecf07401a5d8db00cc2400edcd88f2848cab0764ed810b53c2ccfcdd75103
```

使用真实 Telephony、Contacts 输入分别直接打包两次：

```text
Telephony：
round1 = 5bdc9a9cb1dc99319e2218c3d1b7c3743fcb254301e8ad25fa344f01ca93cd13
round2 = 5bdc9a9cb1dc99319e2218c3d1b7c3743fcb254301e8ad25fa344f01ca93cd13

Contacts：
round1 = 8e50c50db4671c0ad1ac20e529da59027e7cc17209d6c630290d49372450928e
round2 = 8e50c50db4671c0ad1ac20e529da59027e7cc17209d6c630290d49372450928e
```

两组 HAP 的 ZIP entry 时间均为：

```text
2019-01-01 00:00
```

验证产物：

```text
/srv/workspace/action_incremental_logs_20260813/hap_packing_probe
```

### 6.5 完整构建集成验证

Hvigor 默认使用 SDK 预置 jar：

```text
prebuilts/ohos-sdk/linux/26.0.0/toolchains/lib/app_packing_tool.jar
```

源码构建生成的新 jar 不会自动被 Hvigor 使用。因此验证时临时把新 jar 注入 SDK 路径。注入后两个 jar 的 SHA-256 一致。

实际构建日志：

```text
/srv/workspace/action_incremental_logs_20260813/hap_fixed_real_build.log
/srv/workspace/action_incremental_logs_20260813/hap_fixed_dry_run.log
```

实际构建结果：

```text
rk3568 build success
Cost Time: 0:08:24
```

Contacts Action 在该轮真实执行，正式 HAP 已使用固定时间，哈希与独立探针相同。Telephony Action 本轮没有执行，所以磁盘上的正式 Telephony HAP 仍是此前旧产物，但同一真实输入通过新 jar 的独立打包验证已经通过。

### 6.6 当前修复边界

该 PR 已解决：

```text
相同输入 -> HAP ZIP entry 时间固定 -> HAP 字节和 SHA-256 可重复
```

该 PR没有解决：

```text
上游 native library 每轮 dirty
compile_app.py 无条件重写声明 JSON 输出
两个 HAP compile_app Action 完全退出第二轮 dry-run
```

PR 描述不能声称“两个 Action 已不再 dirty”。准确表述应是：修复 HAP 打包产物因 ZIP entry 时间导致的非确定性。

## 7. HAP Action 尚未闭环的问题

### 7.1 最新 Ninja explain

直接目标 query 使用：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -n -d explain \
  obj/base/telephony/telephony_data/Telephony_Data_Storage_compile_app.stamp

prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -n -d explain \
  obj/applications/standard/contacts_data/Contacts_DataAbility_compile_app.stamp
```

必须加 `-w dupbuild=warn`，否则当前构建图会因已有 duplicate output 直接报错，无法进入 explain。

直接 dirty 原因：

```text
telephony/telephony_data/libtel_telephony_data.z.so is dirty
applications/contacts_data/libcontactsdataability.z.so is dirty
```

随后显示：

```text
obj/.../unsigned_hap_path_list.json is dirty
```

这是 Action 已经被安排执行后的输出解释，不是当前最早根因。

日志：

```text
/srv/workspace/action_incremental_logs_20260813/telephony_hap_target_explain.log
/srv/workspace/action_incremental_logs_20260813/contacts_hap_target_explain.log
```

### 7.2 `gn desc` 结论

两个 target 均为：

```text
type: action
script: //build/scripts/compile_app.py
```

唯一 GN 声明输出分别是：

```text
obj/base/telephony/telephony_data/Telephony_Data_Storage/unsigned_hap_path_list.json
obj/applications/standard/contacts_data/Contacts_DataAbility/unsigned_hap_path_list.json
```

HAP 文件本身不在 `outputs` 中。

日志：

```text
/srv/workspace/action_incremental_logs_20260813/telephony_hap_gn_desc.log
/srv/workspace/action_incremental_logs_20260813/contacts_hap_gn_desc.log
```

### 7.3 `compile_app.py` 的独立问题

当前代码：

```python
file_utils.write_json_file(options.output_file, unsigned_hap_path_json)
```

`build/scripts/util/file_utils.py` 已支持：

```python
write_json_file(output_file, content, check_changes=False)
```

但 `compile_app.py` 没有传 `check_changes=True`，所以 Action 一旦因上游 `.so` 被触发，即使 JSON 内容完全相同，也会刷新 JSON mtime 和 stamp。

最小方案：

```python
file_utils.write_json_file(
    options.output_file,
    unsigned_hap_path_json,
    check_changes=True,
)
```

这项应在 `build` 仓建立独立分支和独立 PR，不得混入 packing_tool PR。

注意：该改动只能稳定 Action 的声明输出和下游传播，不能阻止因真实上游 `.so` dirty 而执行 `compile_app.py`。

### 7.4 native library TODO

后续分别追踪：

```text
libtel_telephony_data.z.so
libcontactsdataability.z.so
```

步骤：

1. 用目标级 `ninja -n -d explain` 找每个 `.so` 的直接输入；
2. 用 `ninja -t query` 看输入和消费者；
3. 定位最早没有其他 dirty 解释的源文件、生成文件、depfile 或 stamp；
4. 比较两轮 `.ninja_log` 的命令哈希、输出 mtime 和 SHA-256；
5. 判断是真内容变化、mtime 漂移、命令变化还是 depfile 问题；
6. 到对应组件仓建立独立 PR，不在 `build` 或 packing_tool 尾端删除依赖。

## 8. 原 packages Action 当前状态

原始列表：

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

| Action | 当前状态 | TODO |
| --- | --- | --- |
| `sa_profile_src_phone` | PR !6965 已修复输出稳定性 | 补充其他产品场景 |
| `sa_profile_binary_phone` | PR !6965 已修复输出稳定性 | 验证非空 binary SA ZIP |
| `phone_sa_profile_install_info` | PR !6965 已修复 | 不再修改尾端 Action |
| `check_seccomp_filter_name` | 根因确认，有实验提交 | 从最新上游整理独立正式 PR |
| `process_field_validate` | 根因确认 | 实现稳定成功输出并验证失败路径 |
| `collect_notice_files__phone` | NOTICE 自身稳定，受 parts 上游影响 | 追 `phone_parts_list` |
| `generate_host_symlink` | 自身 JSON 可稳定，受 host parts 输入影响 | 追 `all_parts_host.json` |
| `phone_hisysevent_install_info` | 自身输出可稳定，受 parts 链影响 | parts 链稳定后复验 |
| `phone_parts_list` | 尚未收敛 | 追 parts 聚合链最早 dirty |
| `phone_install_modules` | 存在真实 `.so`/可执行文件重建输入 | 追最早重复链接模块 |

validator 根因：

```text
check_seccomp_filter_name：
GN 声明 check_seccomp_filter_name.txt，旧脚本成功时不生成文件。

process_field_validate：
GN 声明 cfg_validate_result.txt，旧脚本不生成文件。
```

合格修复必须满足：输出真实存在、成功内容固定、相同内容不刷新、失败仍非零、原子写入。

## 9. GN/Ninja 标准分析方法

### 工具帮助

```bash
prebuilts/build-tools/linux-x86/bin/gn help
prebuilts/build-tools/linux-x86/bin/gn help action
prebuilts/build-tools/linux-x86/bin/gn help copy
prebuilts/build-tools/linux-x86/bin/gn help desc
prebuilts/build-tools/linux-x86/bin/ninja --help
prebuilts/build-tools/linux-x86/bin/ninja -d list
prebuilts/build-tools/linux-x86/bin/ninja -t list
prebuilts/build-tools/linux-x86/bin/ninja -w list
```

GN 使用 `gn help <topic>`，不要把普通可执行文件的 `--help` 形式套到 GN topic 上。

### `gn desc`

```bash
prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 '<label>'
prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 '<label>' outputs
prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 '<label>' inputs
prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 '<label>' script
prebuilts/build-tools/linux-x86/bin/gn desc out/rk3568 '<label>' deps --tree
```

### 指导要求的快速 dry-run

```bash
./build.sh -p rk3568 --build-target make_all \
  --ninja-args=-dexplain \
  --ninja-args=-n \
  --ninja-args=-dstats 2>&1
```

`build.sh` 实际传递的 Ninja 参数已经确认：

```text
ninja -w dupbuild=warn -C out/rk3568 make_all -dstats -n -dexplain
```

本次 `hap_fixed_dry_run.log` 没有保留 `ninja explain:` 行，但列出了约 8807 个计划节点。因此重要目标应使用直接 Ninja query 单独落盘。

### `-n` 和 `restat`

`ninja -n` 不执行 Action，因此不能观察 Action 运行后输出是否保持不变，也不能模拟 `restat` 在真实执行后的截断效果。

```text
上游 dirty
  -> -n 计划 Action
  -> Action 没有执行
  -> Ninja 无法证明输出不变
  -> 下游可能继续显示派生 dirty
```

所以 dry-run 适合找依赖链，不足以单独判定输出稳定化修复失败。最终验收必须结合第二次真实构建、mtime、hash 和 `.ninja_log`。

## 10. 标准构建验证命令

新日期使用新日志目录，不覆盖历史日志：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
mkdir -p /srv/workspace/action_incremental_logs_YYYYMMDD
```

第一次真实构建：

```bash
{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_first_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_first_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_first_ninja.log
```

快速 dry-run：

```bash
{ time ./build.sh -p rk3568 --build-target make_all \
  --ninja-args=-dexplain \
  --ninja-args=-n \
  --ninja-args=-dstats; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_dry_run_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_dry_run_build.log
```

第二次真实构建：

```bash
{ time ./build.sh -p rk3568 --build-target make_all; } 2>&1 \
  | tee /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_second_console.log

cp out/rk3568/build.log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_second_build.log

cp out/rk3568/.ninja_log \
  /srv/workspace/action_incremental_logs_YYYYMMDD/<topic>_second_ninja.log
```

## 11. 下一步 TODO

按优先级：

1. 在 packing_tool PR !1556 评论区输入 `check dco`，确认新提交通过 DCO 检查。
2. 完善 `developtools_packing_tool` 中文 Issue/PR 说明并推进 PR。
3. 在最新 `openharmony/build` 上维护独立分支，只修改 `compile_app.py`，启用 `check_changes=True`。
4. 由操作者进行两轮真实构建，确认 JSON 内容不变时 mtime 与 stamp 不刷新。
5. 分别追踪 `libtel_telephony_data.z.so` 和 `libcontactsdataability.z.so` 的最早 dirty 根因。
6. 从 packages 实验分支整理 `check_seccomp_filter_name` 独立 PR。
7. 单独实现并验证 `process_field_validate` 稳定输出。
8. 继续追 `phone_parts_list` 和 `phone_install_modules`，不在尾端 Action 上增加跳过逻辑。
9. 将本交接文档和 packing_tool 进展提交到 GitHub 日志仓，确保另一台主机可以直接同步。

## 12. 新会话第一轮操作

1. 阅读本文，不从旧聊天重建结论。
2. SSH 登录虚拟机，检查是否有其他构建进程。
3. 检查 `build` 和 `developtools/packing_tool` 的分支、HEAD、工作树。
4. 只读查看 `/srv/workspace/action_incremental_logs_20260813`。
5. 使用 `gn desc` 确认目标类型、输出和直接依赖。
6. 使用直接 `ninja -w dupbuild=warn -n -d explain` 找最早 dirty。
7. 汇报时区分：已验证事实、推断、直接 dirty、派生 dirty。
8. 未获得明确授权时不启动完整构建。
9. 正式修改从最新上游建立小分支；远程整仓验证分支只用于兼容验证。
10. 每次只提交一个根因，提交前检查 UTF-8、`git diff --check`、DCO 和 Change-Id。
