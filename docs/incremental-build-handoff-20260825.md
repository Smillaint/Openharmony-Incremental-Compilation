# OpenHarmony 增量编译项目交接说明（2026-08-25）

本文在 `incremental-build-handoff-20260824.md` 基础上，记录 2026-08-24 后续完成的 HiSysEvent 与 NOTICE 增量修复、独立分支、验证证据和 GitCode 推送状态。历史环境迁移、SSH、DCO、门禁和安全操作规范继续参考：

```text
docs/incremental-build-handoff-20260817.md
docs/incremental-build-handoff-20260819.md
docs/incremental-build-handoff-20260824.md
```

如果本文件与 2026-08-24 文档中的 packages Action 进度冲突，以本文件为准。必须注意：HiSysEvent 和 NOTICE 是两个分别基于 `gitcode/master` 的独立正式分支，目前没有在同一组合分支上完成联合两轮验证。

## 1. 当前环境和仓库状态

代码根目录：

```text
/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code
```

当前 `build` 子仓：

```text
仓库路径：/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code/build
原仓远端：gitcode -> https://gitcode.com/openharmony/build
个人远端：fork -> git@gitcode.com:SmillySmillick/build.git
当前分支：fix-part-install-metadata-incremental-build
当前 HEAD：edc427a875e5c0642e31c7b3dca4f7a8b0219b71
上游跟踪：fork/fix-part-install-metadata-incremental-build
状态：clean，本地与 fork 远端 HEAD 一致
```

当前正式分支基线：

```text
c55264de  !6989 merge cherry-pick-mr-6987-1786970220491-auto into master
```

该 `gitcode/master` 引用是在 2026-08-20 获取的。后续创建或更新 PR 前必须重新 fetch 最新上游，不能把 `c55264de` 当作 2026-08-25 之后持续不变的最新 master。

当前相关本地和 fork 分支：

```text
fix-hisysevent-incremental-build
  3dc5695a126e2c9b3de9336ad8a290d2b66c8d29

fix-part-install-metadata-incremental-build
  edc427a875e5c0642e31c7b3dca4f7a8b0219b71

incremental-build-all-validation-20260820
  f1a463340efbcaa8089df8f47e50409c14ee9322
```

其中：

- `incremental-build-all-validation-20260820` 是旧组合验证分支，包含 SA、HAP signing、IDL、packages 聚合、host symlink 和 validator 等多项补丁；
- `fix-hisysevent-incremental-build` 只处理 HiSysEvent 输入和 depfile；
- `fix-part-install-metadata-incremental-build` 只处理部件安装元数据与 NOTICE 收集链；
- 两个正式分支均直接基于 `c55264de`，彼此不包含对方的提交。

## 2. HiSysEvent 独立修复

### 2.1 分支和提交

```text
分支：fix-hisysevent-incremental-build
提交：3dc5695a126e2c9b3de9336ad8a290d2b66c8d29
标题：Stabilize HiSysEvent incremental inputs
Change-Id：I2a7c11af3498a5fd01befd8ddc8365210a39996f
远端：fork/fix-hisysevent-incremental-build
```

DCO 身份：

```text
Author: Smillick <3185479846@qq.com>
Committer: Smillick <3185479846@qq.com>
Signed-off-by: Smillick <3185479846@qq.com>
```

修改文件：

```text
hb/util/loader/load_ohos_build.py
ohos/hisysevent/hisysevent_process.py
```

### 2.2 根因和修复

`phone_hisysevent_install_info` 的直接和间接输入中存在语义内容不变但每轮被重新写入的 JSON：

- loader 每轮改写 `hisysevent_configs.json`；
- `hisysevent_process.py` 每轮改写 `hisysevent_install_info.json`；
- Action 实际读取的 HiSysEvent YAML 没有全部加入 depfile。

修复内容：

- 仅对 `hisysevent_config` 的 parts 信息启用 `check_changes=True`；
- `hisysevent_install_info.json` 内容不变时保留原文件和 mtime；
- 将实际选中的 HiSysEvent YAML 文件加入 depfile；
- 不删除真实依赖，真实 YAML 内容变化仍会重新调度目标。

### 2.3 两轮验证

日志目录：

```text
/srv/workspace/action_incremental_logs_20260824/hisysevent_incremental
```

构建结果：

```text
第一轮：rk3568 build success，0:11:36
第二轮：rk3568 build success，0:08:20
```

第二轮结果：

```text
phone_hisysevent_install_info  未执行
collect_notice_files__phone    仍执行
phone_install_modules          仍执行
```

以下产物的 inode、mtime、大小和 SHA-256 两轮完全一致：

```text
out/rk3568/build_configs/parts_info/hisysevent_configs.json
  SHA-256: 4ffdc4d22dd4863be7130b60cdf776f2b59d50bf72b648bf4be4aa0aea626338

out/rk3568/packages/phone/hisysevent/hisysevent_install_info.json
  SHA-256: ae681e50adae1fbcf499ab1a59e045b35408272bfcae7f01186fbeeaf4401994

out/rk3568/packages/phone/hisysevent/hisysevent.zip
  SHA-256: d5e1b7c68335a90cb59d36b1d556ba30e93054a56617688f12d2fa84a0189cf0

out/rk3568/gen/build/ohos/packages/phone_hisysevent_install_info.d
  SHA-256: 3552eb5506b4d07e3e61406b2e5d45f2741840d41ba7cb2538786fb1ba3505a5
```

## 3. NOTICE 独立修复

### 3.1 分支和提交

```text
分支：fix-part-install-metadata-incremental-build
提交：edc427a875e5c0642e31c7b3dca4f7a8b0219b71
标题：Fix incremental notice file collection
Change-Id：I385d19be88725996dac340a31f23309cadb23647
远端：fork/fix-part-install-metadata-incremental-build
```

DCO 身份：

```text
Author: Smillick <3185479846@qq.com>
Committer: Smillick <3185479846@qq.com>
Signed-off-by: Smillick <3185479846@qq.com>
```

修改文件：

```text
ohos/generate_part_info.py
ohos/packages/BUILD.gn
ohos/packages/parts_install_info.py
scripts/util/file_utils.py
```

### 3.2 根因定位

第一阶段先稳定了 part 安装元数据，但第二轮 `collect_notice_files__phone` 仍然执行。对其 depfile 中 52184 个直接输入按第一轮结束时间检查后，没有发现第一轮与第二轮之间被更新的直接输入：

```text
UPDATED_COUNT=0
```

最终根因是输出时间关系：

- part install、dep module、host module 和 system install JSON 原先会无条件重写；
- `collect_system_notice_files.py` 使用内容感知 ZIP 写入，内容相同时保留旧的 `system_notice_files.zip`；
- 最终 ZIP 的旧 mtime 可能持续早于 depfile 中已经存在的输入；
- 即使两轮之间没有输入变化，Ninja 仍会因“输入比输出新”每轮将收集 Action 判为 dirty。

### 3.3 修复设计

元数据稳定化：

- part install modules、dep modules 和 host modules JSON 启用 `check_changes=True`；
- `system_install_parts.json` 启用内容感知写入；
- `file_utils.__check_changes` 直接比较解析后的 JSON 对象，不再对 `str()` 结果重复计算 SHA-256。

NOTICE 两阶段输出：

```text
真实动态输入和 depfile
  -> stage_notice_files__<platform>
  -> target_gen_dir/system_notice_files_<platform>.zip
  -> collect_notice_files__<platform>
  -> <platform>/system_notice_files.zip
  -> merge_system_notice_file_<platform>
```

- `stage_notice_files__<platform>` 保留原有 NOTICE 动态依赖和 depfile；
- 中间 ZIP 位于 `target_gen_dir`，内容不变时保持稳定；
- 原 `collect_notice_files__<platform>` 使用仓库已有 `copy_ex` 模板，仅在中间 ZIP 内容真实变化时发布最终 ZIP；
- 最终产物路径和下游依赖不变；
- 未使用空 stamp、伪成功输出或删除真实输入的方式绕过构建。

### 3.4 两轮验证

主要日志目录：

```text
/srv/workspace/action_incremental_logs_20260824/notice_two_stage_v3
```

主要验证结果：

```text
第一轮：rk3568 build success，0:11:03
第二轮：rk3568 build success，0:08:00
```

第二轮未执行：

```text
stage_notice_files__phone
collect_notice_files__phone
merge_system_notice_file_phone
```

第二轮仍执行：

```text
phone_hisysevent_install_info
phone_install_modules
```

以下两个 ZIP 的 inode、mtime、大小和 SHA-256 两轮完全一致：

```text
out/rk3568/gen/build/ohos/packages/system_notice_files_phone.zip
out/rk3568/packages/phone/system_notice_files.zip

SHA-256:
b222f90089319d41a6df93257c1a3ef6d36ff521b13218fcbd77cdee84baddf1
```

2026-08-25 又执行了一组无源码变化的两轮构建，日志位于：

```text
/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code/first_console.log
/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code/second_console.log
```

结果：

```text
第一轮：rk3568 build success，0:11:15
第二轮：rk3568 build success，0:08:13
第二轮未出现 stage_notice_files__phone
第二轮未出现 collect_notice_files__phone
第二轮未出现 merge_system_notice_file_phone
```

该额外验证进一步确认 NOTICE 修复在连续构建中稳定。

### 3.5 提交前检查

已完成：

```text
python3 -m py_compile
git diff --check
完整 diff 复核
Author / Committer / Signed-off-by 复核
Change-Id 复核
fork 远端 HEAD 复核
```

曾对整份 `ohos/packages/BUILD.gn` 运行 GN formatter。当前版本 formatter 会顺带改写多处与本修复无关的历史 target 标签，因此已撤销这些无关机械变化；正式提交只保留 NOTICE 修复所需的 14 行新增和 3 行删除。

## 4. 原始十个 packages Action 最新判断

### 4.1 不能直接写成单一分支 9/10

2026-08-24 上午组合分支的严格结果仍是：

```text
单一组合分支第二轮未执行：7/10
单一组合分支第二轮仍执行：3/10
```

之后分别完成：

```text
fix-hisysevent-incremental-build
  phone_hisysevent_install_info 未执行

fix-part-install-metadata-incremental-build
  collect_notice_files__phone 未执行
```

按已验证独立修复能力可以认为 9 个 Action 已有收敛方案，只剩 `phone_install_modules` 未解决；但两个新提交没有在同一个组合分支中联合执行两轮构建，因此不能把“单一代码状态严格通过 9/10”写成既成事实。

### 4.2 状态表

| Action | 修复状态 | 验证范围 | 说明 |
| --- | --- | --- | --- |
| `sa_profile_src_phone` | 已有收敛补丁 | 2026-08-20 组合分支 | packages 聚合稳定化后第二轮未执行 |
| `sa_profile_binary_phone` | 已有收敛补丁 | 2026-08-20 组合分支 | SA 输出与上游聚合修复共同生效 |
| `phone_sa_profile_install_info` | 已有收敛补丁 | 2026-08-20 组合分支 | 第二轮未执行 |
| `check_seccomp_filter_name` | 已有收敛补丁 | 2026-08-20 组合分支 | 稳定输入、真实 depfile、成功和失败路径已验证 |
| `process_field_validate` | 已有收敛补丁 | 2026-08-20 组合分支 | 第二轮未执行，静态检查已通过 |
| `collect_notice_files__phone` | 独立正式分支已收敛 | `edc427a8` 两组双轮构建 | 第二轮收集和合并均未执行 |
| `generate_host_symlink` | 已有收敛补丁 | 2026-08-20 组合分支 | 两阶段处理阻断动态元数据时间戳 |
| `phone_hisysevent_install_info` | 独立正式分支已收敛 | `3dc5695a` 一组双轮构建 | 第二轮未执行，YAML 真实依赖进入 depfile |
| `phone_install_modules` | 未收敛 | 所有最近第二轮 | 仍需定位最早真实变化或仅 mtime 变化模块 |
| `phone_parts_list` | 已有收敛补丁 | 2026-08-20 组合分支 | 聚合输出稳定化后第二轮未执行 |

## 5. GitCode 分支、Issue 和 PR 状态

### 5.1 已推送分支

```text
fork/fix-hisysevent-incremental-build
  3dc5695a126e2c9b3de9336ad8a290d2b66c8d29

fork/fix-part-install-metadata-incremental-build
  edc427a875e5c0642e31c7b3dca4f7a8b0219b71
```

NOTICE 分支的 PR 创建入口：

```text
https://gitcode.com/SmillySmillick/build/merge_requests/new?source_branch=fix-part-install-metadata-incremental-build
```

截至本文写入时，本地 Git 证据只能确认两个分支已推送，不能确认对应 OpenHarmony PR 编号、评审人或门禁状态。创建 PR 后必须把正式 URL、目标分支、DCO、静态检查、编译、冒烟测试和评审状态补充到本文。

### 5.2 既有 Issue 和组合 PR

2026-08-24 文档记录的关联 Issue：

```text
https://gitcode.com/openharmony/build/issues/4678
无源码变化时 packages 相关 Action 仍被重复调度
```

2026-08-24 文档记录的组合 PR：

```text
https://gitcode.com/openharmony/build/merge_requests/6999
标题：Stabilize package validation inputs
```

PR #6999 包含多个历史修复和多个根因。其门禁和评审状态没有在 2026-08-25 本轮通过 GitCode 页面重新核实，不能直接沿用旧文档中的 `waiting_for_review` 作为实时结论。

### 5.3 账号其他 PR

2026-08-24 文档中记录的 7 个既有 PR 状态继续作为历史参考：

```text
third_party_jsframework#853
third_party_sane-airscan#22
build#6965
build#6974
developtools_packing_tool#1556
build#6982
build#6999
```

这些 PR 的 2026-08-25 实时状态未在本轮重新查询。接手后应从 GitCode 页面逐个确认是否仍为 `waiting_for_review`、是否有新评审意见以及是否已合入。

## 6. 下一步优先级

### 6.1 第一优先级：建立联合验证分支

在不改写两个正式分支的前提下，建立临时联合验证分支，至少组合：

```text
3dc5695a  Stabilize HiSysEvent incremental inputs
edc427a8  Fix incremental notice file collection
```

建议流程：

1. 先 fetch 最新 `gitcode/master`；
2. 确认上游是否已出现等价修复；
3. 从明确基线创建仅用于验证的临时分支；
4. cherry-pick 两个正式提交并检查冲突与 patch 边界；
5. 连续执行两轮 `./build.sh -p rk3568 --build-target make_all`；
6. 严格检查原始十个 Action；
7. 只有同一分支第二轮确实只剩 `phone_install_modules` 时，才能把严格统计更新为 9/10。

临时联合验证分支默认不推送为综合正式 PR。

### 6.2 第二优先级：完成两个独立 PR 闭环

- 为 HiSysEvent 和 NOTICE 分支记录正式 PR URL；
- PR 目标应为 OpenHarmony `build` 最新合适上游；
- 一个 PR 只处理一个根因，不把两个提交重新合并成正式综合 PR；
- 检查 Author、Committer、Signed-off-by、Change-Id；
- DCO 未刷新时在 PR 评论区执行 `check dco`；
- 门禁失败时读取最早失败任务的 `error.log`，不能只看 HB/Ninja 外层 traceback；
- 更新已存在远端分支前先读取远端 HEAD，禁止无核对强推。

### 6.3 第三优先级：排查 `phone_install_modules`

`phone_install_modules` 是当前唯一尚无收敛方案的原始目标。排查顺序：

1. 读取该 Action 在第二轮的全部直接输入；
2. 从第二轮最早重新链接的 `.so`、可执行文件或安装清单开始；
3. 比较 inode、mtime、大小和 SHA-256；
4. 对内容相同但 mtime 变化的文件继续向最早生成者反向追踪；
5. 对内容真实变化的二进制检查链接命令、嵌入时间、随机顺序和归档确定性；
6. 不删除安装依赖，不使用空安装列表或假 stamp 伪造 clean。

## 7. 验证命令和检查口径

完整构建入口：

```bash
./build.sh -p rk3568 --build-target make_all
```

必须在第一轮成功后、不修改源码和构建配置，立即执行第二轮。不要把两轮构建命令和只读 grep 放在同一代码块交给操作者复制，避免误触发额外构建。

只读检查 NOTICE Action 的安全单行命令：

```bash
grep -n -E 'ACTION //build/ohos/packages:(stage_notice_files__phone|collect_notice_files__phone|merge_system_notice_file_phone)' /path/to/second_console.log || true
```

只读检查剩余原始 Action：

```bash
grep -n -E 'ACTION //build/ohos/packages:(phone_hisysevent_install_info|phone_install_modules)' /path/to/second_console.log || true
```

完整验收不能只看 grep 或 `BUILD_STATUS=0`，还要保存并比较：

- console log；
- build.log 和 error.log；
- `.ninja_log`；
- depfile；
- 关键输出 inode、mtime、大小和 SHA-256；
- Action 的 command hash 和直接输入；
- 失败路径的非零退出及旧成功结果清理情况。

## 8. 安全和提交要求

- 所有文本按 UTF-8 读取和写入；
- 不执行 `git reset --hard`、`git clean` 或未确认目标的递归删除；
- 不覆盖其他子仓、其他分支和未知工作树修改；
- 不删除真实依赖，不使用假 stamp 或空输出绕过 Action；
- 正式 PR 原则上一个根因一个分支；
- 完整构建成功不等于增量修复完成；
- 使用 GN formatter 前先确认它是否会改写整份历史 BUILD.gn，不能把无关格式变化带入提交；
- 正式提交统一使用：

```text
Author: Smillick <3185479846@qq.com>
Committer: Smillick <3185479846@qq.com>
Signed-off-by: Smillick <3185479846@qq.com>
```

- 提交消息必须保留有效 Change-Id；
- 推送后用 `git ls-remote` 核验 fork 远端 HEAD；
- DCO、静态检查、编译和冒烟测试全部通过后，仍需代码评审和社区合入才能视为 PR 完成。
