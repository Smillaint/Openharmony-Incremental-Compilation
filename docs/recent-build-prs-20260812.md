# 最近两个 Build PR 的修改、验证与后续方向

本文整理截至 2026-08-12 最近两个 `openharmony/build` 增量编译修复：SA Profile 稳定输出和 HAP signing 稳定输出，并记录后续分析方向。

## 1. SA Profile 增量输出

### 1.1 PR 信息

- 上游：<https://gitcode.com/openharmony/build>
- PR：<https://gitcode.com/openharmony/build/merge_requests/6965>
- fork 分支：<https://gitcode.com/SmillySmillick/build/tree/codex/fix-sa-profile-incremental-build>
- 提交：`0d530d7eb691276cd27d7109b1155a21c6c0c1cc`
- 标题：`Stabilize SA profile incremental outputs`
- DCO：已包含 `Signed-off-by`

涉及 Action：

```text
//build/ohos/packages:sa_profile_src_phone
//build/ohos/packages:sa_profile_binary_phone
//build/ohos/packages:phone_sa_profile_install_info
```

### 1.2 根因

SA Profile 链存在多种无实际语义变化的输出刷新：

1. `src_sa_infos.json` 的列表顺序依赖上游收集顺序；
2. `src_sa_install_info.json` 和 `sa_install_info.json` 无条件重写；
3. 二进制 SA ZIP 即使内容相同也会替换原文件；
4. 公共 JSON 变化检测曾使用 `str(dict)`，结果受字典插入顺序影响；
5. 上游 `phone_parts_list` 或 `src_sa_infos_process` dirty 时，三个 Action 会被连续带起。

### 1.3 修改

涉及文件：

```text
ohos/sa_profile/src_sa_profile_process.py
ohos/sa_profile/sa_profile_source.py
ohos/sa_profile/sa_profile_binary.py
ohos/sa_profile/sa_profile_merge.py
scripts/util/file_utils.py
```

主要处理：

- SA 信息按 `label` 稳定排序；
- JSON 使用解析后的数据结构判断变化；
- JSON 内容相同时不重写，保留原 mtime；
- ZIP 使用 `build_utils.atomic_output`；
- ZIP 内容相同时不替换原文件；
- 保持异常和失败返回，不通过空输出掩盖错误。

### 1.4 正式分支与验证分支

正式 PR 基于当时的官方 `build` master：

```text
base:   69f5e307
commit: 0d530d7e
```

远程完整源码由 manifest 固定在较早的 `build` 基线 `656fb7cf`。正式 PR 分支直接放入整仓会和当前 `foundation/arkui/ace_engine` 产生重复参数声明：

```text
Duplicate build argument declaration:
ace_engine_enable_reduce_eh_frame
```

该错误属于仓库版本不匹配，不属于 SA 补丁。整仓验证使用等价补丁：

```text
branch: sa-profile-query-validation-20260812
base:   656fb7cf
commit: 2e1aac4b
```

正式 PR 分支和整仓验证分支必须分离，不修改无关 `BUILDCONFIG.gn` 来强行兼容。

### 1.5 2026-08-12 验证

指导要求的快速检查：

```bash
./build.sh -p rk3568 --build-target make_all \
  --ninja-args=-dexplain \
  --ninja-args=-n \
  --ninja-args=-dstats
```

dry-run 中三个 SA Action 仍被列出，但 explain 显示直接上游是：

```text
generate_src_installed_info
  -> src_sa_infos_process
  -> sa_profile_src_phone

generate_host_info / gen_binary_installed_info
  -> merge_all_parts
  -> phone_parts_list
  -> sa_profile_binary_phone
  -> phone_sa_profile_install_info
```

`build.sh` 在 Ninja 前会运行 preloader 和 `gn gen`，刷新大量生成输入；而 `-n` 不执行 Action，无法验证 Action 执行后的 `restat`。

第二次真实构建中的关键结果：

```text
sa_profile_src_phone           执行
sa_profile_binary_phone        执行
phone_sa_profile_install_info  未执行
```

前两个 Action 执行后输出 mtime 未变化：

```text
src_sa_install_info.json       2026-08-12 11:50:10
sa_profile_binary_phone.zip    2026-08-10 09:22:00
sa_install_info.json           2026-08-10 09:22:01
merged_sa_profile.zip          2026-08-06 09:30:28
```

结论：稳定输出生效，Ninja `restat` 成功阻断 dirty 传播，`phone_sa_profile_install_info` 没有真实重跑。当前 `rk3568` 范围内修复有效。

关键日志：

```text
/srv/workspace/action_incremental_logs_20260812/sa_validation_second_real_build.log
/srv/workspace/action_incremental_logs_20260812/sa_validation_second_real_ninja.log
/srv/workspace/action_incremental_logs_20260812/sa_validation_direct_ninja.log
```

### 1.6 后续方向

1. 补充存在非空二进制 SA 的产品测试；
2. 检查 `part_name_info.json` 是否通过普通 `ZipFile.writestr()` 写入动态 entry 时间；
3. 若存在动态时间，改用 `build_utils.add_to_zip_hermetic()`；
4. 验证相同输入连续生成 ZIP 的 SHA-256、entry 顺序、时间和权限完全一致；
5. 上游 parts 链仍 dirty 时，不继续修改 SA 尾端，应单独分析 `phone_parts_list`。

## 2. HAP signing 增量输出

### 2.1 分支信息

- 相关 Issue：<https://gitcode.com/openharmony/build/issues/4663>
- fork 分支：<https://gitcode.com/SmillySmillick/build/tree/fix-hap-sign-incremental-build>
- fork 提交：`34aa8cba Fix incremental HAP signing outputs`
- 正式补丁等价提交：`656140e1`
- 整仓验证提交：`0dad9413`

本地日志没有保存该 PR 的最终编号和门禁结果，后续更新时应从 GitCode 页面补齐，不能猜测。

### 2.2 根因

旧 app signing 规则存在两个问题：

1. signing Action 使用容易和 GN stamp 规则冲突的 `${target_name}.stamp` 输出；
2. unsigned/signed HAP 路径列表和签名结果缺少稳定的内容代理，无法可靠区分“路径相同但 HAP 内容变化”和“内容未变”。

这会造成 duplicate output、签名 Action 重复执行或下游无法正确利用 `restat`。

### 2.3 修改

涉及文件：

```text
ohos/app/app_internal.gni
scripts/app_sign.py
scripts/compile_app.py
scripts/util/build_utils.py
```

主要处理：

- 每个 signing Action 使用独立的 `${target_name}.sign_result.json`；
- GN 将该文件声明为 Action 的真实输出；
- unsigned HAP 列表稳定排序；
- 为每个 unsigned/signed HAP 记录 SHA-256；
- 签名结果以稳定 JSON 记录；
- JSON 通过临时文件原子生成；
- 内容相同时不替换原文件，保留 mtime；
- Action 失败时不产生伪成功结果。

### 2.4 验证结果

等价补丁在 manifest 兼容分支 `0dad9413` 上进行了整仓验证。

已确认：

- app signing Action 拥有独立真实输出；
- 输出文件真实存在；
- unsigned/signed HAP hash 被纳入稳定结果；
- duplicate signing output 的规则设计得到修正；
- 多数 signing Action 在增量构建中消失。

仍观察到 Telephony 和 Contacts 的 unsigned HAP hash 变化。该变化不是 `build/scripts/app_sign.py` 无条件改写造成的，而是上游 HAP 包本身发生变化。

### 2.5 `Compressor.java` 后续问题

上游可疑代码路径：

```text
developtools/packing_tool/adapter/ohos/Compressor.java
```

当前分析认为 HAP ZIP entry 写入了当前时间，导致相同输入重复打包时 HAP 字节和 SHA-256 变化，并进一步改变 `module.json.buildHash`。

后续应在 `developtools_packing_tool` 独立处理：

1. 使用固定 ZIP entry 时间；
2. 固定 entry 顺序；
3. 固定权限、压缩方式和压缩级别；
4. 相同输入连续打包两次，比较 HAP SHA-256；
5. 检查 Telephony 和 Contacts 的 `module.json.buildHash` 是否稳定；
6. 不把 packing tool 修改混入 `openharmony/build` PR。

### 2.6 后续验证

HAP signing PR 应再按以下顺序闭环：

1. 在 manifest 兼容分支完成一次真实构建；
2. 不切分支、不修改源码，执行第二次真实构建；
3. 保存 console、`build.log`、`.ninja_log`；
4. 执行带 `-d explain -n -d stats` 的 query；
5. 使用 `gn desc` 检查 app signing target 的 `outputs/script/deps`；
6. 比较所有 `unsigned_hap_path_list.json` 和 `sign_result.json` 的 mtime/hash；
7. 把仍变化的 Telephony/Contacts 明确归入 packing tool 后续 PR。

## 3. `-n` 与 `restat` 的验收边界

`ninja -n` 只模拟计划，不执行 Action。若上游 dirty：

```text
上游 dirty
  -> dry-run 计划执行 Action
  -> 脚本没有真实执行
  -> 无法知道输出内容是否保持不变
  -> 无法触发真实 restat
  -> 下游继续显示 xx is dirty
```

因此不能仅凭 dry-run 中出现目标 Action 判定 PR 失败。必须结合：

- 第二次真实构建是否执行；
- 输出 mtime、inode、size 和 SHA-256；
- `.ninja_log` 是否新增真实条目；
- 下游 Action 是否被 `restat` 阻断；
- explain 中第一条直接 dirty 原因。

完整方法见 [current-project-handoff.md](current-project-handoff.md)。

## 4. 下一阶段优先级

1. 补齐 HAP signing 的正式 PR 编号、门禁和最终两轮验证记录；
2. 在 `developtools_packing_tool` 修复 `Compressor.java` 的 ZIP 非确定性；
3. 把 `check_seccomp_filter_name` 从历史实验分支整理成独立小 PR；
4. 实现并验证 `process_field_validate` 的稳定成功输出；
5. 追踪 `phone_parts_list` 的最早 dirty 节点；
6. 追踪 `phone_install_modules` 中最早重复链接的具体模块；
7. 所有后续验证同时使用 `gn desc`、单目标 Ninja explain、两轮真实构建和输出 hash，不从末端 `is dirty` 直接打补丁。
