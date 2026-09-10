# OpenHarmony 增量编译项目交接说明（2026-08-24）

本文记录 2026-08-24 的最新修复、验证和 GitCode 状态。历史环境迁移、SSH、GitCode 身份及完整操作规范继续参考：

```text
docs/incremental-build-handoff-20260817.md
docs/incremental-build-handoff-20260819.md
```

本文件中的 packages Action 状态以 2026-08-16 整仓快照及 2026-08-20 最近两轮成功构建为准；如果与旧交接文档冲突，以本文件为准。

## 1. 当前验证环境

代码根目录：

```text
/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code
```

`build` 子仓：

```text
仓库：/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code/build
分支：incremental-build-all-validation-20260820
HEAD：f1a463340efbcaa8089df8f47e50409c14ee9322
上游跟踪：fork/incremental-build-all-validation-20260820
状态：clean，本地与 fork 远端 HEAD 一致
```

最近验证日志目录：

```text
/srv/workspace/action_incremental_logs_20260820/host_validator_upstream_v2
/srv/workspace/action_incremental_logs_20260820/host_symlink_two_stage
```

最后一组两轮完整构建结果：

```text
第一轮 BUILD_STATUS=0
第二轮 BUILD_STATUS=0
```

完整构建仍由操作者手动执行。后续不能只依据 `BUILD_STATUS=0` 判断增量问题完成，必须同时检查 Action 调度、输出 inode、mtime、SHA-256、depfile 和 `.ninja_log`。

## 2. 2026-08-20 新增修复

### 2.1 packages 聚合输出稳定化

提交：

```text
0c668bfc72507e69630a35ab8a8972fa8cc338d7  Stabilize package aggregation outputs
```

处理内容：

- parts 和平台安装元数据在内容不变时不替换原文件；
- 通过内容感知写入和 Ninja `restat` 阻断无效时间戳继续向下游传播；
- `phone_parts_list`、SA Profile 源和二进制 Action 在最近第二轮构建中均未再次执行。

### 2.2 host symlink 两阶段处理

提交：

```text
45c3af2f0c30824953bd69647d23641c14faecc5  Stabilize host symlink generation
```

处理内容：

- 原始 host 元数据先生成到 `target_gen_dir`；
- 对 host 元数据进行确定性排序，内容不变时保留 `all_parts_host.json`；
- 新增 `collect_host_symlink_info`，收集 part/module 元数据并生成真实 depfile；
- `generate_host_symlink` 只依赖稳定的 `host_symlink_info.json`；
- 符号链接创建失败保持非零退出，不使用空输出或假 stamp 跳过 Action。

最近第二轮结果：

```text
collect_host_symlink_info  执行，允许作为上游收集阶段执行
generate_host_symlink      未执行
```

以下输出的 inode、mtime、大小和 SHA-256 两轮保持一致：

```text
out/rk3568/gen/build/ohos/packages/host_symlink_info.json
out/rk3568/all_host_symlink.json
```

### 2.3 packages validator 输入与输出稳定化

提交：

```text
f1a463340efbcaa8089df8f47e50409c14ee9322  Stabilize package validation inputs
```

该提交由 `21dd2af20636c63b43f6ea5abe4587b1cd9d01d1` amend 得到，Change-Id 保持不变：

```text
Id298e0a3dd5e4870df0ef3bd86ad87cd7c7dfd7e
```

处理内容：

- install modules JSON、module list 和 arm64e metadata 使用稳定写入；
- 新增 `phone_validation_install_modules.json` 作为 validator 的稳定输入层；
- `process_field_validate` 和 `check_seccomp_filter_name` 生成稳定成功结果；
- 通过 depfile 声明实际读取的 cfg、seccomp 库和白名单文件；
- 失败时返回非零并删除旧成功结果，不能留下虚假成功标记；
- 对目录扫描排序，保证依赖收集顺序确定。

最近第二轮结果：

```text
phone_validation_install_modules  执行，允许作为稳定输入阶段执行
process_field_validate             未执行
check_seccomp_filter_name          未执行
```

稳定结果文件：

```text
out/rk3568/packages/phone/cfg_validate_result.txt
out/rk3568/packages/phone/check_seccomp_filter_name.txt
```

两个结果文件的 SHA-256 均为：

```text
114251d6c56bfdae1798438d6f5ea440b50d130d77ccda494a351c210b9f06ca
```

真实 rk3568 输入连续执行两次均返回 0，结果文件 inode、mtime 和 SHA-256 保持不变。失败夹具返回 1，并正确删除旧成功结果。

### 2.4 静态检查修复

`process_field_validate.py` 的 `main()` 曾被门禁报告为 57 行，超过单函数 50 行限制。已拆分为：

```text
parse_options
validate_cfg_folder
run_validation
main
```

修改后 `main()` 为 16 行；Python 语法、`git diff --check`、成功路径、失败路径和 GitCode 静态检查均通过。`opts, args` 同时改为 `opts, _`，避免保留未使用变量。

## 3. 原始十个 packages Action 最新状态

### 3.1 严格统计

以 `/srv/workspace/action_incremental_logs_20260820/host_symlink_two_stage/second_console.log` 的实际调度为准：

```text
第二轮未执行：7/10
第二轮仍执行：3/10
```

### 3.2 明细

| Action | 最近第二轮 | 当前状态 | 说明 |
| --- | --- | --- | --- |
| `sa_profile_src_phone` | 未执行 | 已收敛 | packages 聚合输出稳定后不再被无效触发 |
| `sa_profile_binary_phone` | 未执行 | 已收敛 | SA 输出稳定化与上游聚合修复共同生效 |
| `phone_sa_profile_install_info` | 未执行 | 已收敛 | Target 和产物仍存在，通过 `restat` 保持 clean |
| `check_seccomp_filter_name` | 未执行 | 已收敛 | 稳定输入、真实 depfile 和稳定成功结果已验证 |
| `process_field_validate` | 未执行 | 已收敛 | 成功和失败路径均已验证 |
| `collect_notice_files__phone` | 执行 | 未收敛 | NOTICE 自身可稳定，仍受聚合链输入影响 |
| `generate_host_symlink` | 未执行 | 已收敛 | 两阶段处理阻断动态元数据时间戳传播 |
| `phone_hisysevent_install_info` | 执行 | 未收敛 | 仍受 parts 聚合链影响 |
| `phone_install_modules` | 执行 | 未收敛 | 仍需定位最早重复链接或真实变化模块 |
| `phone_parts_list` | 未执行 | 已收敛 | packages 聚合输出稳定化已阻断无效重建 |

最近第二轮仍存在的三个原始 Action：

```text
ACTION //build/ohos/packages:phone_hisysevent_install_info
ACTION //build/ohos/packages:collect_notice_files__phone
ACTION //build/ohos/packages:phone_install_modules
```

第二轮仍执行的相关上游或隔离层 Action：

```text
ACTION //build/ohos/common:generate_host_info
ACTION //build/ohos/common:merge_all_parts
ACTION //build/ohos/packages:collect_host_symlink_info
ACTION //build/ohos/packages:phone_install_modules
ACTION //build/ohos/packages:phone_validation_install_modules
```

`collect_host_symlink_info` 和 `phone_validation_install_modules` 当前用于吸收上游时间戳变化并发布稳定输入，不能仅因它们仍执行就删除依赖或改为空 stamp。

## 4. 当前 build 组合验证分支

相对 2026-08-16 manifest 基线，当前分支包含：

```text
c08d319f83666f1da7affee73a568a437d289cf3  Stabilize SA profile incremental outputs
0008197c18e088abdc43221328c55a99644af1d4  Fix incremental HAP signing outputs
e00d6de2884c1822315f8b44ba8e5b938f0abb70  Fix common IDL output declarations
0c668bfc72507e69630a35ab8a8972fa8cc338d7  Stabilize package aggregation outputs
45c3af2f0c30824953bd69647d23641c14faecc5  Stabilize host symlink generation
f1a463340efbcaa8089df8f47e50409c14ee9322  Stabilize package validation inputs
```

2026-08-20 曾获取 `gitcode/master` 到 `c55264de`，当时相关文件中没有可直接采用的官方等价修复。该结论只代表当时上游状态；后续整理正式 PR 前必须重新 fetch 最新上游。

## 5. GitCode Issue 和 PR 状态

关联 Issue：

```text
https://gitcode.com/openharmony/build/issues/4678
无源码变化时 packages 相关 Action 仍被重复调度
```

当前组合 PR：

```text
https://gitcode.com/openharmony/build/merge_requests/6999
标题：Stabilize package validation inputs
状态：已开启
提交：6
文件改动：20
DCO：通过
静态检查：通过
编译：通过
冒烟测试：通过
代码审查：0/1
Label：waiting_for_review
```

PR #6999 当前使用组合验证分支，包含多个历史修复和多个根因。虽然门禁已经通过，但不符合旧交接文档中“一个正式 PR 只处理一个根因”的理想边界。后续必须按社区评审意见决定：

- 保持当前 PR 并补充完整说明；或
- 从最新上游分别整理 packages 聚合、host symlink、validator 等独立正式分支和 PR。

不得在未读取远端 HEAD 的情况下覆盖 PR 分支。需要改写时必须使用带明确旧提交的 `--force-with-lease`。

## 6. 账号相关 PR 状态

截至 2026-08-24，与本项目相关的 7 个 PR 均已通过 DCO、静态检查、编译和冒烟测试，当前均在等待代码评审：

| PR | 内容 | 当前状态 |
| --- | --- | --- |
| `third_party_jsframework#853` | 稳定 `ark_jsf`、`gen_snapshot` 增量输出 | `waiting_for_review` |
| `third_party_sane-airscan#22` | 稳定 `airscan_action` 输入和输出 | `waiting_for_review` |
| `build#6965` | SA Profile 增量输出 | `waiting_for_review` |
| `build#6974` | HAP signing 稳定输出 | `waiting_for_review` |
| `developtools_packing_tool#1556` | 可重复 HAP ZIP entry 时间戳 | `waiting_for_review` |
| `build#6982` | common IDL 输出声明 | `waiting_for_review` |
| `build#6999` | packages、host symlink 和 validator 组合验证 | `waiting_for_review` |

所有 PR 当前都不能仅因门禁通过而视为已完成，仍需要至少一名审查人通过并由社区完成合入。

## 7. 已知环境问题

2026-08-21 在代码根目录直接运行：

```text
prebuilts/build-tools/linux-x86/bin/gn gen out/rk3568 --check
```

随后查询 Ninja 命令时出现：

```text
multiple rules generate obj/base/security/access_token/frameworks/common/permission_definition_check.stamp
```

该错误发生在本次只重构 `process_field_validate.py` 的阶段，修改没有涉及相关 BUILD.gn；此前两轮完整 `build.sh` 已成功。因此当前按生成图或基线环境问题记录，不能直接归因于 validator 修复，也不能通过删除未知 `out` 内容处理。

后续若需要复验：

1. 先由操作者正常执行项目构建入口生成构建图；
2. 读取最早的 GN/Ninja 错误和对应重复规则来源；
3. 不执行 `git clean`、`reset --hard` 或递归删除 `out`；
4. 如果错误在无本项目补丁的相同基线可复现，作为独立基线问题处理。

## 8. 下一步优先级

### 8.1 第一优先级：完成 PR 评审闭环

- 跟进 PR #6999 的审查分配和评审意见；
- 评审要求拆分时，基于最新上游建立独立正式分支；
- 每个正式提交继续检查 Author、Committer、Signed-off-by 和 Change-Id；
- 更新 PR 分支前先读取远端 HEAD，只使用精确 `--force-with-lease`。

### 8.2 第二优先级：剩余三个 packages Action

聚合链重点：

```text
各部件 build_configs
  -> generate_src_installed_info / generate_host_info
  -> gen_binary_installed_info / src_sa_infos_process
  -> merge_all_parts
  -> phone_hisysevent_install_info
  -> collect_notice_files__phone
```

应从 `merge_all_parts` 及两个叶子 Action 的 Ninja 直接输入中定位最早 dirty 文件，比较 mtime、SHA-256、command hash 和 depfile。不能在 NOTICE 或 HiSysEvent 尾端增加无条件跳过逻辑。

### 8.3 第三优先级：`phone_install_modules`

- 查询该 Action 的所有直接输入；
- 从第二轮最早重新链接的 `.so` 或可执行文件开始排查；
- 区分真实二进制变化与仅 mtime 变化；
- 不删除实际安装依赖，不通过稳定空列表跳过安装。

## 9. 后续验证和安全要求

- 所有文本按 UTF-8 读取和写入；
- 完整构建由操作者手动执行；
- 第一轮成功后，不修改源码直接执行第二轮；
- 同时保存 console、build.log、error.log、`.ninja_log`、Action 行及输出快照；
- 输出快照使用正确路径，validator 结果位于 `out/rk3568/packages/phone/`；
- 不执行 `git reset --hard`、`git clean` 或递归删除；
- 不覆盖其他子仓和未知工作树修改；
- 不删除真实依赖，不使用假 stamp 或空输出伪造 clean；
- 一个正式 PR 原则上只处理一个根因；
- 失败路径必须返回非零并移除旧成功结果；
- GitCode 正式提交统一使用：

```text
Author: Smillick <3185479846@qq.com>
Committer: Smillick <3185479846@qq.com>
Signed-off-by: Smillick <3185479846@qq.com>
```

