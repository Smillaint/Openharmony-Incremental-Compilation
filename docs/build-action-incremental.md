# Build Action 增量编译更新日志

## 2026-08-06：稳定 SA Profile 增量输出

状态：**已提交 PR**

- 上游仓库：[openharmony/build](https://gitcode.com/openharmony/build)
- PR：[openharmony/build !6965](https://gitcode.com/openharmony/build/merge_requests/6965)
- 分支：`codex/fix-sa-profile-incremental-build`
- 提交：`0d530d7eb691276cd27d7109b1155a21c6c0c1cc`
- DCO：`Signed-off-by: Smillick <3185479846@qq.com>`

### 涉及 Action

- `sa_profile_src_phone`
- `sa_profile_binary_phone`
- `phone_sa_profile_install_info`

### 根因

1. SA 元数据列表顺序依赖上游输入顺序，相同集合可能生成顺序不同的 JSON。
2. 多个 JSON 输出无条件写入，内容相同时仍更新时间戳。
3. SA Profile ZIP 直接重建，内容相同时仍替换原文件。
4. 公共 JSON 变化检测依赖 `str(dict)` 的结果，字典插入顺序可能影响比较结果。

### 修改

- 按 `label` 稳定排序 SA 元数据。
- JSON 写入前比较解析后的数据结构，内容相同时保留原文件。
- 使用 `build_utils.atomic_output` 生成 SA Profile ZIP，仅在内容变化时替换输出。

涉及文件：

```text
ohos/sa_profile/src_sa_profile_process.py
ohos/sa_profile/sa_profile_source.py
ohos/sa_profile/sa_profile_binary.py
ohos/sa_profile/sa_profile_merge.py
scripts/util/file_utils.py
```

### 验证

连续执行两次：

```bash
./build.sh -p rk3568 --build-target make_all 2>&1
```

结果：

- 两轮完整构建均成功。
- 第一轮正常执行三个 SA Profile Action。
- 第二轮三个 Action 均未再次执行。
- `src_sa_infos.json`、`src_sa_install_info.json`、SA ZIP 和安装信息文件保持第一轮时间戳。
- 稳定 JSON、稳定 ZIP、SA 元数据排序和 UTF-8 AST 语法检查通过。

## 2026-08-05：Packages Action 综合实验

状态：**已验证实验，不可直接作为 PR**

实验分支：`codex/packages-action-incremental-fix-20260805`

实验提交：

```text
2edc96eb Fix generated output stability for incremental builds
17a78da3 Handle invalid cached notice metadata
552dd282 Tolerate optional IDL outputs during timestamp stabilization
a335f4f4 Fix-NOTICE-incremental-outputs
9ee0ea74 Fix package action incremental outputs
26a8c7c6 Stabilize package action inputs
a5a6cdd4 Compare JSON outputs by value
dfd40cd1 Make package metadata deterministic
```

该分支同时修改 NOTICE、IDL、parts、package modules、SA Profile 和 HiSysEvent 等 13 个文件。它用于定位和验证，不应整体推送为一个 PR；已经验证且边界清晰的改动需要从最新上游主分支重新整理。

### 已确认结果

- SA Profile 子链在第二轮构建中消失，已整理为独立 PR !6965。
- HiSysEvent 自身 JSON 和 ZIP 输出可以保持稳定，但 Action 仍可能被 `phone_parts_list` 上游依赖带起。
- NOTICE 输入和 ZIP 输出能够保持稳定，但 `collect_notice_files__phone` 仍受 `phone_parts_list` 硬依赖影响。
- `generate_host_symlink` 自身输出可以稳定，第二轮仍受 `all_parts_host.json` 变化影响。
- `phone_install_modules` 的第二轮输入中确实存在重新链接的动态库和可执行文件，当前不能通过删除依赖或跳过 Action 处理。

## 剩余 Action 状态

| Action | 当前结论 | 下一步 |
| --- | --- | --- |
| `check_seccomp_filter_name` | GN 声明 `check_seccomp_filter_name.txt`，脚本成功后未生成该文件 | 增加成功结果输出，内容不变时保留时间戳 |
| `process_field_validate` | GN 声明 `cfg_validate_result.txt`，脚本未生成该文件 | 与 seccomp 校验修复分开验证或组成同类小 PR |
| `collect_notice_files__phone` | NOTICE 自身产物已稳定，仍被 `phone_parts_list` 带起 | 继续追踪 parts 聚合链 |
| `generate_host_symlink` | 自身 JSON 可稳定，上游 `all_parts_host.json` 仍变化 | 找到 host parts 元数据的最早 dirty 节点 |
| `phone_hisysevent_install_info` | 自身产物可稳定，仍受 parts 依赖影响 | 在 parts 稳定后复验 |
| `phone_parts_list` | 公共 parts 聚合链尚未收敛 | 从 `generate_src_installed_info`、`generate_host_info`、`gen_binary_installed_info` 和 `merge_all_parts` 开始追踪 |
| `phone_install_modules` | 存在真实重建输入 | 追踪最早重复链接的模块，不修改 packages 尾端依赖 |

## 排查原则

1. 先使用 `ninja -n -d explain` 找到最早 dirty 节点，再修改对应生成逻辑。
2. 区分输出缺失、内容变化、时间戳变化、depfile 变化和上游依赖 dirty。
3. 不通过删除真实输入、跳过 Action 或伪造时间戳制造“零构建”。
4. 一个 PR 只处理一个边界清晰的根因，并使用 `git commit --signoff` 满足 DCO。
5. 完整构建后连续执行第二轮，分别保存 console、`build.log` 和 `.ninja_log` 作为验证证据。
