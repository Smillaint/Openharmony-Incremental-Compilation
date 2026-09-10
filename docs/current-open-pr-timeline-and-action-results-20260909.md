# OpenHarmony 增量编译 PR 时间线与 Action 收敛结果（2026-09-09）

> 本文保留 2026-09-09 时间线快照。当前目标状态、逐 Action 的精确代码说明及 2026-09-10 diff 核对结果见 [原始 10 项修复交接](original-ten-actions-completion-20260910.md)。原始十项已初步修复完成，剩余 9 个 metadata/ramdisk 步骤归入扩展优化。

## 1. 小结

截至 2026-09-09，本轮工作共有 13 个已创建的 PR，全部仍为 `open`。GitCode 当前计算结果中，12 个 PR 为 `mergeable=true`，`third_party_sane-airscan#22` 为 `mergeable=false`。`mergeable` 只表示当前分支能否直接合并，不等价于代码评审通过、门禁通过或已经合入。

本轮修复围绕三类增量构建根因展开：

1. 输出内容没有变化，但脚本无条件覆盖文件或目录，导致 mtime 更新并继续传播 dirty 状态；
2. GN/Ninja 声明的输出不存在、范围过宽或归属错误，导致 Action 每轮执行；
3. 动态扫描输入没有进入 depfile，或把缓存、生成物等不稳定文件错误纳入依赖。

现有证据表明，jsframework、airscan、IDL、HiSysEvent、NOTICE、packages validator、host symlink、SDK split 和 iptables 等子链路均取得了目标级收敛。其中 iptables 修复后的组合工作树零改动轮次从此前 39 个主 Ninja 步骤降至 9 个，iptables 的 3 个 CC、3 个 AR、1 个 LINK 以及 `phone_install_modules` 均未执行。该 39→9 是组合修复工作树的前后对比，不能全部归因于 iptables 单个 PR；iptables 可直接归因的是聚合 C 文件不再重写及其 CC/AR/LINK 链消失。

## 2. 当前 PR 总览

| PR | 创建时间 | 最后更新时间 | 当前状态 | 主要修复对象 | Action 结果口径 |
|---|---|---|---|---|---|
| [third_party_jsframework#853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853) | 2026-08-05 10:15 | 2026-08-19 15:38 | open，可合并 | runtime、snapshot 稳定输出 | 第二轮 `ark_jsf`、`gen_snapshot` 均为 0 |
| [third_party_sane-airscan#22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22) | 2026-08-05 14:48 | 2026-08-05 15:54 | open，当前不可直接合并 | 补丁 staging 与精确输出 | 第二轮 `airscan_action` 为 0 |
| [build#6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 2026-08-06 11:25 | 2026-08-06 14:24 | open，可合并 | SA Profile JSON/ZIP | 稳定输出截断传播；组合验证中 SA targets 可消失 |
| [build#6974](https://gitcode.com/openharmony/build/merge_requests/6974) | 2026-08-10 10:41 | 2026-08-10 13:32 | open，可合并 | HAP/HSP 签名结果代理 | 内容不变不继续传播；真实 HAP 变化仍会签名 |
| [packing_tool#1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556) | 2026-08-13 11:52 | 2026-08-14 11:19 | open，可合并 | HAP ZIP entry 元数据 | 两组 HAP 连续打包 SHA-256 一致 |
| [build#6982](https://gitcode.com/openharmony/build/merge_requests/6982) | 2026-08-14 17:08 | 2026-08-17 16:34 | open，可合并 | common IDL 输出声明 | 错误双 `i` 输出命中从 31800 字节降为 0 |
| [build#6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 2026-08-20 18:03 | 2026-08-21 13:00 | open，可合并 | packages、host symlink、validator 组合 | 第二轮 `phone_parts_list`、host symlink leaf、两个 validator 不再执行 |
| [build#7006](https://gitcode.com/openharmony/build/merge_requests/7006) | 2026-08-24 11:19 | 2026-08-25 11:21 | open，可合并 | HiSysEvent 配置与安装信息 | 第二轮 `phone_hisysevent_install_info` 为 0 |
| [build#7009](https://gitcode.com/openharmony/build/merge_requests/7009) | 2026-08-25 10:16 | 2026-08-27 12:32 | open，可合并 | part 元数据与 NOTICE 两阶段发布 | 第二轮 NOTICE stage、collect、merge 均为 0 |
| [iptables#62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) | 2026-09-02 10:02 | 2026-09-02 11:12 | open，可合并 | `genInit.py` 聚合 C 文件 | 3 CC、3 AR、iptables LINK 和 `phone_install_modules` 均为 0 |
| [build#7046](https://gitcode.com/openharmony/build/merge_requests/7046) | 2026-09-03 15:40 | 2026-09-03 17:00 | open，可合并 | 安装 depfile、binary install 元数据 | 独立 PR 未重编；组合轮次中 `phone_install_modules` 为 0 |
| [build#7048](https://gitcode.com/openharmony/build/merge_requests/7048) | 2026-09-03 16:19 | 2026-09-03 16:20 | open，可合并 | LICENSE 边界与 NOTICE depfile | 独立 PR 未重编；避免生成 NOTICE 反向进入输入集 |
| [build#7049](https://gitcode.com/openharmony/build/merge_requests/7049) | 2026-09-03 17:21 | 2026-09-03 17:22 | open，可合并 | SDK split stamp/depfile | 与调用方配套验证时，第二轮 `ohos_base_split` 为 0 |

## 3. 分 PR 时间线、代码修改与效果

### 3.1 third_party_jsframework#853

**时间线**

- 2026-08-04：在零改动第二轮中确认 `ark_jsf` 与 `gen_snapshot` 重复执行；完成根因定位及目标级复验。
- 2026-08-05 10:15：创建 PR #853。
- 2026-08-19 15:38：PR 最后更新；截至 2026-09-09 仍为 open、可合并。

**代码修改**

- 文件：`js_framework_build.sh`，新增 18 行、删除 1 行。
- 不再为了重新生成单个文件而删除整个共享 `runtime` 目录。
- 对 `strip.native.min.js` 使用临时备份和 `cmp -s` 比较；内容相同则恢复原文件及 mtime，内容变化才保留新文件。
- 将 `runtime` 目录时间戳与 `css_what_sources.stamp` 关联，稳定共享目录状态。

**修复链路与结果**

`js_framework_build.sh` 原本会扰动 `runtime`、`css_what_sources.stamp` 和 `strip.native.min.js`，dirty 状态继续传到 snapshot。修复后的零改动轮次中：

- `ACTION //third_party/jsframework:ark_jsf`：0；
- `ACTION //third_party/jsframework:gen_snapshot`：0。

证据：`/srv/workspace/action_incremental_logs_20260804/final_zero_change_console.log`，构建成功，耗时约 11 分 26 秒。

### 3.2 third_party_sane-airscan#22

**时间线**

- 2026-08-04：确认 `airscan_action` 会修改源码树、重复应用补丁并遗留 `.rej`；完成 staging 方案及零改动复验。
- 2026-08-05 14:48：创建 PR #22；15:54 最后更新。
- 2026-09-09：仍为 open，但 GitCode 当前计算为不可直接合并，应优先检查是否落后 master 或存在冲突。

**代码修改**

- 文件：`BUILD.gn`、`patch_install.py`。
- 在 `${target_gen_dir}/patched` 中构造补丁后的源码副本，不再修改 source tree。
- 由同一份 `patched_airscan_files` 推导 Action 的 inputs、outputs 和编译 sources，避免声明与实际编译文件不一致。
- 使用严格 patch 参数并通过正向/反向 dry-run 判断未应用、已应用和非法状态；失败时不留下半成品。
- staging 完成后按内容决定是否替换正式输出，并排除 OpenHarmony 不支持的后端。

**修复链路与结果**

- `ACTION //third_party/sane-airscan:airscan_action`：零改动第二轮为 0；
- 没有新增 `.rej`，source tree 不再被构建过程修改；
- patched 源文件与实际编译输入保持一致。

证据：`/srv/workspace/action_incremental_logs_20260804/airscan_*`。

### 3.3 build#6965：SA Profile

**时间线**

- 2026-08-05 至 08-06：定位 SA JSON、ZIP 和哈希顺序不稳定问题。
- 2026-08-06 11:25：创建 PR #6965；14:24 最后更新。
- 2026-08-12：完成 SA 独立两轮验证；后续组合 package 稳定化后继续验证传播边界。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- `ohos/sa_profile/src_sa_profile_process.py`
- `ohos/sa_profile/sa_profile_source.py`
- `ohos/sa_profile/sa_profile_binary.py`
- `ohos/sa_profile/sa_profile_merge.py`
- `scripts/util/file_utils.py`

具体处理包括：按 label 和路径排序；以解析后的 JSON 对象进行语义比较；统一使用内容感知写入；ZIP 先生成临时文件，再比较并原子替换；固定条目名称、顺序和压缩参数。

**修复链路与结果**

对应 Action：

- `sa_profile_src_phone`
- `sa_profile_binary_phone`
- `phone_sa_profile_install_info`

SA 独立验证第二轮约 11 分 07 秒，最终合并产物没有被下游重复消费。叠加 package 聚合稳定化后，源配置和二进制配置 Action 可在零改动轮次消失。该结论只覆盖当时 rk3568/phone 配置，不能直接外推到非空 binary SA 或其他产品。

### 3.4 build#6974：HAP/HSP 签名

**时间线**

- 2026-08-07：开始定位共享 stamp、签名结果表达不足和失败残留问题。
- 2026-08-10 10:41：创建 PR #6974；13:32 最后更新。
- 2026-08-12：补充签名结果稳定性验证。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- `ohos/app/app_internal.gni`
- `scripts/app_sign.py`
- `scripts/compile_app.py`
- `scripts/util/build_utils.py`

每个 target 使用独立的 `${target_name}.sign_result.json`；输入路径排序并记录 SHA-256；结果 JSON 原子、内容感知写入；失败时不生成虚假成功结果。

**修复链路与结果**

影响 HAP/HSP 签名 Action 及其下游打包/安装链。修复的直接效果是：签名工具即使被真实上游触发，只要签名结果语义没有变化，就不会再通过共享 stamp 无效传播。若上游 HAP 字节确实变化，签名仍会正确执行，因此不以“所有签名 Action 永远为 0”作为验收条件。

### 3.5 developtools_packing_tool#1556：HAP 可复现打包

**时间线**

- 2026-08-13：完成相同输入连续打包探针，并于 11:52 创建 PR #1556。
- 2026-08-14 11:19：PR 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- 文件：`adapter/ohos/Compressor.java`，新增 9 行、删除 1 行。
- 将普通文件、native 文件、`STORED` entry 和空目录的 ZIP entry 时间统一为 `1546272000000`，即 2019-01-01。
- 保持原有条目顺序、权限、压缩方法和其他归档参数不变。

**修复链路与结果**

- Telephony 连续两次打包 SHA-256 均为 `5bdc9a9cb1dc99319e2218c3d1b7c3743fcb254301e8ad25fa344f01ca93cd13`；
- Contacts 连续两次打包 SHA-256 均为 `8e50c50db4671c0ad1ac20e529da59027e7cc17209d6c630290d49372450928e`；
- ZIP entry 时间均为 2019-01-01。

该 PR 直接保证 HAP 字节可复现，为下游签名 Action 的稳定判断提供前提；它本身不承诺所有签名 Action 单独消失。

### 3.6 build#6982：common IDL 输出声明

**时间线**

- 2026-08-13 至 08-14：定位双 `i` 输出名和外部 common IDL 所有权问题，经历中间失败迭代。
- 2026-08-14 17:08：创建 PR #6982。
- 2026-08-17：完成最终两轮验证；16:34 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- 文件：`config/components/idl_tool/idl.gni`，新增 8 行、删除 8 行。
- 通过 `filter_exclude(..., ["//*"])` 分离本地 common IDL 与 source-absolute 外部 IDL。
- 外部 IDL 只作为输入，不再声明成当前 Action 的输出。
- 修正接口名到文件名的转换，避免给已经以 `I` 开头的接口再次添加前缀。
- outputs 只保留当前 Action 真正生成的本地文件。

**修复链路与结果**

修复 common IDL Action 缺失/错误输出导致的每轮 dirty，并阻止其继续带动对应 CXX、SOLINK 和 `phone_install_modules` 输入链。错误双 `i` 输出检查由 31800 字节命中降为 0；2026-08-17 两轮构建约 7 分 58 秒和 11 分 40 秒，目标输出哈希与时间戳稳定。

### 3.7 build#6999：packages、host symlink 与 validator 组合 PR

**时间线**

- 2026-08-19：完成 `phone_parts_list` 聚合 JSON 稳定输出验证。
- 2026-08-20：完成 host symlink 两阶段发布、validator result/depfile/失败清理；18:03 创建 PR #6999。
- 2026-08-21 13:00：PR 最后更新；后续文档记录当时门禁已通过并进入等待评审。
- 2026-09-09：仍为 open、可合并。

**实际代码范围**

当前 PR diff 共 20 个文件，并非单一根因提交：

- packages/common：`ohos/common/BUILD.gn`、`generate_host_info.py`、`merge_all_subsystem.py`、`ohos/packages/BUILD.gn`、`generate_host_symlink.py`、`modules_install.py`、`parts_install_info.py`、`process_field_validate.py`、`check_seccomp_library_name.py`、`stabilize_json_file.py`；
- 叠加的历史内容：`config/components/idl_tool/idl.gni`、四个 SA Profile 脚本、`app_internal.gni`、`app_sign.py`、`compile_app.py`、`build_utils.py`、`file_utils.py`。

核心方案包括：

- 规范化 `all_parts_info.json`、`system_install_parts.json` 等聚合 JSON，内容一致不覆盖；
- host symlink 拆为动态 collector、稳定 intermediate 和 leaf 发布；
- validator 成功时生成真实固定 result，失败时删除旧成功文件并返回非零；
- 动态 cfg、seccomp、白名单和模块元数据写入 depfile；
- 拆分 `process_field_validate.py` 的入口职责，使 main NBNC 从 57 行降至约 16 行。

**修复链路与结果**

- `phone_parts_list`：第二轮不再执行；
- `generate_host_symlink` leaf：第二轮不再执行，collector 可按真实输入需要执行；
- `process_field_validate`、`check_seccomp_filter_name`：第二轮不再执行；
- validator 失败 fixture 返回 1，并删除预置旧成功结果；
- `all_parts_info.json`、`system_install_parts.json`、host symlink intermediate/final JSON 及 validator result 的哈希、inode、mtime、size保持稳定。

风险边界：PR #6999 含多个历史修复和多个根因，文件范围较大，并与 #6965、#6974、#6982 的部分代码重叠。社区评审可能要求拆分或同步最新 master 后消除重叠。

### 3.8 build#7006：HiSysEvent

**时间线**

- 2026-08-24：定位并修复 HiSysEvent JSON 无条件覆盖和 YAML 隐式依赖；11:19 创建 PR #7006。
- 2026-08-25 11:21：PR 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- `hb/util/loader/load_ohos_build.py`
- `ohos/hisysevent/hisysevent_process.py`

loader 和处理脚本改用 `check_changes=True`；JSON 排序、规范化；将实际读取的 YAML 配置写入 depfile，同时保留真实 YAML 变化的触发能力。

**修复链路与结果**

- `phone_hisysevent_install_info`：第二轮为 0；
- 第一轮约 11 分 36 秒，第二轮约 8 分 20 秒；
- config、install info、ZIP、depfile 的 SHA-256 均保持稳定。

当时 NOTICE 和 `phone_install_modules` 仍执行，说明本 PR 只截断 HiSysEvent 子链，没有掩盖其他上游问题。

### 3.9 build#7009：part 元数据与 NOTICE

**时间线**

- 2026-08-24：依次完成 part metadata、NOTICE v2 和两阶段 NOTICE v3 三轮迭代。
- 2026-08-25 10:16：创建 PR #7009；当天完成补充两轮复验。
- 2026-08-27 12:32：PR 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- `ohos/generate_part_info.py`
- `ohos/packages/BUILD.gn`
- `ohos/packages/parts_install_info.py`
- `scripts/util/file_utils.py`

part install、dep、host、system install JSON 改为排序和 parsed-JSON 语义比较；NOTICE collector 只生成稳定中间 ZIP；新增独立 `copy_ex` leaf 发布到最终路径；collector 保留大规模直接输入和 depfile，leaf 只依赖稳定中间 ZIP。

**修复链路与结果**

- `collect_notice_files__phone`：第二轮为 0；
- NOTICE stage 与 merge targets：第二轮为 0；
- 中间和最终 NOTICE ZIP SHA-256 均为 `b222f90089319d41a6df93257c1a3ef6d36ff521b13218fcbd77cdee84baddf1`；
- 2026-08-24 两轮约 11 分 03 秒、8 分 00 秒；2026-08-25 复验约 11 分 15 秒、8 分 13 秒。

### 3.10 third_party_iptables#62

**时间线**

- 2026-09-01：定位 `genInit.py` 无变化重写；完成隔离测试、代码审查和人工连续两轮构建。
- 2026-09-02：推送提交并于 10:02 创建 PR #62；11:12 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- 文件：`extensions/genInit.py`，新增 13 行、删除 5 行。
- 使用 `io.StringIO` 在内存中完整生成聚合 C 源码。
- 将预期文本与现有 UTF-8 文件内容比较，只有内容变化或文件缺失时才写入。
- 保留原有注册顺序、命令行参数、符号替换、排除规则和 MD5 helper 行为。

**修复链路与结果**

直接对应输出：

- `out/.../gen/initext.c`
- `out/.../gen/initext4.c`
- `out/.../gen/initext6.c`

修复前，这三个文件 mtime 每次变化，会触发 3 个 CC、3 个 AR 和 iptables LINK，iptables 又是 `phone_install_modules` 的真实输入。两轮人工验证结果：

- 第一轮：GN 24.37 秒，Ninja 21.73 秒，主 Ninja 实际 9 步；
- 第二轮：GN 24.72 秒，Ninja 20.84 秒，主 Ninja 实际 9 步；
- 两轮 iptables CC/AR/LINK 均为 0；
- 两轮 `phone_install_modules` 均为 0；
- 三个 initext 文件时间戳保持在修复前的 15:59:29；
- 对比上一阶段第二轮 39 步，组合工作树收敛为 9 步，剩余为 3 个 metadata stamp、4 个 metadata Action 和 2 个 ramdisk image Action。

日志：`/srv/workspace/action_incremental_logs_20260901/geninit_content_aware_fix`。

### 3.11 build#7046：安装依赖与 binary install 元数据

**时间线**

- 2026-08-28 至 09-02：在 `phone_install_modules` 后续排查中识别 SA depfile 过滤和 binary install 元数据问题，并从组合工作树拆出独立提交。
- 2026-09-03 15:40：创建 PR #7046；17:00 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- `ohos/packages/modules_install.py`：将错误的 `depfiles.extend(filtered)` 改为 `depfiles = filtered`，真正从 depfile 排除 SA 文件，而不是把过滤结果再次追加到原列表。
- `ohos/common/binary_install_info.py`：binary install JSON 使用内容感知写入；可选 `dist_parts_info_file` 只有实际存在时才进入 depfile。

**修复链路与结果**

对应 `phone_install_modules` 自身 depfile、`gen_binary_installed_info` 输出及其下游安装链。该独立 PR 分支拆出后没有重新执行完整编译，因此不能把组合工作树中 `phone_install_modules=0` 全部归因于 #7046。可以确认的是：代码消除了 SA 依赖过滤失效、重复追加，以及不存在的可选输入长期出现在 depfile 中的问题；binary install JSON 内容不变时不会再改写输出。

### 3.12 build#7048：NOTICE 边界与依赖

**时间线**

- 2026-08-25 至 09-02：在 NOTICE/phone install 链路中补充许可证边界检查和聚合 depfile 收敛，并拆出独立分支。
- 2026-09-03 16:19：创建 PR #7048；16:20 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- `ohos/notice/collect_module_notice_file.py`：先检查当前目录中的 LICENSE，再判断当前目录是否为递归边界，避免遗漏边界目录许可证。
- `ohos/notice/collect_system_notice_files.py`：不再把 collector 自己生成的 NOTICE 文件列表追加回 depfile。

**修复链路与结果**

修复 `collect_notice_files__phone` 一类 NOTICE collector 的许可证查找正确性和依赖闭环，避免生成物反向成为自身输入。独立 PR 未重新编译；NOTICE stage/collect/merge 为 0 的两轮证据主要来自 #7009 和组合工作树，不能单独记到 #7048 名下。

### 3.13 build#7049：SDK 接口拆分

**时间线**

- 2026-08-27：`phone_install_modules` dirty 探针证明存在大规模真实重链接输入，继续向上追到 SDK split。
- 2026-08-28：为 `ohos_base_split` 完成 stamp/depfile 修复并执行人工两轮构建。
- 2026-09-02：从组合修改中拆出 build 脚本提交。
- 2026-09-03 17:21：创建 PR #7049；17:22 最后更新。
- 2026-09-09：仍为 open、可合并。

**代码修改**

- 文件：`ohos/sdk/parse_interface_sdk.py`，新增 58 行。
- 新增可选 `--stamp`、`--depfile` 参数。
- depfile 收集 `interface/sdk-js` 文件树、权限定义、Node 可执行文件、Python 脚本依赖及 public SDK 构建输入。
- 排除 `.git`、`.gitee` 等版本管理目录，对依赖排序并转换为 Ninja 工作目录相对路径。
- 成功后通过 `atomic_output` 写入稳定空 stamp。

**修复链路与结果**

配套 Action 为 `//interface/sdk-js:ohos_base_split`。第一次验证中该 Action 执行并生成约 1.57 MB depfile；第二轮：

- `ohos_base_split`：0；
- `ohos_base_split.timestamp`：mtime/size 不变；
- `ohos_base_split.d`：mtime/size 不变。

该效果依赖 `interface_sdk-js` 调用方同时传入 stamp/depfile。#7049 只包含 build 脚本支持；调用方分支尚未创建 PR，因此当前正式提交链还没有完整闭环。验证时 `phone_install_modules` 仍受下一层 `ohos_declaration_ets2` 等 Action 带动，不能用 SDK split 子根因通过替代最终目标通过。

## 4. Action 与文件输出对应关系

| 输出文件或目录 | 触发的主要 Action/链路 | 对应 PR | 已验证结果 |
|---|---|---|---|
| jsframework `runtime`、`strip.native.min.js` | `ark_jsf` → `gen_snapshot` | #853 | 两个 Action 第二轮均为 0 |
| `${target_gen_dir}/patched` airscan 源码 | `airscan_action` → airscan 编译 | #22 | Action 第二轮为 0，无源码树污染 |
| SA Profile JSON、ZIP、install info | `sa_profile_src_phone`、`sa_profile_binary_phone`、`phone_sa_profile_install_info` | #6965 | 输出稳定，组合轮次中 SA targets 可消失 |
| `${target_name}.sign_result.json` | HAP/HSP sign → package/install | #6974 | 内容不变不继续传播 |
| HAP ZIP entry | package → sign | #1556 | 相同输入 HAP SHA-256 一致 |
| common IDL `.h` 输出 | IDL Action → CXX/SOLINK → install | #6982 | 错误输出命中为 0，mtime/hash 稳定 |
| `all_parts_info.json`、`system_install_parts.json` | `merge_all_parts` → `phone_parts_list` | #6999 | `phone_parts_list` 第二轮为 0 |
| host symlink intermediate/final JSON | collector → `generate_host_symlink` | #6999 | leaf 第二轮为 0 |
| validation install JSON、两个 result | validation stage → 两个 validator | #6999 | 两个 validator 第二轮为 0 |
| HiSysEvent config/install JSON、ZIP | `phone_hisysevent_install_info` | #7006 | 第二轮为 0 |
| intermediate/final NOTICE ZIP | stage → `collect_notice_files__phone` → merge | #7009 | 三层第二轮均为 0 |
| `initext.c`、`initext4.c`、`initext6.c` | 3 CC → 3 AR → iptables LINK → `phone_install_modules` | #62 | 直接编译/链接及 install 第二轮均为 0 |
| binary install JSON、phone install depfile | `gen_binary_installed_info` → `phone_install_modules` | #7046 | 逻辑根因已修；独立分支未重编 |
| LICENSE 结果、NOTICE depfile | NOTICE collector | #7048 | 依赖闭环已修；独立分支未重编 |
| `ohos_base_split.timestamp`、`.d` | `ohos_base_split` → declaration/ArkUI/CXX/SOLINK | #7049 | 配套工作树第二轮 Action 为 0 |

## 5. 当前结论与下一步

1. 13 个 PR 均未合入，当前仍需社区评审；#22 还需先解决不可直接合并状态。
2. #7049 必须继续提交 `interface_sdk-js:fix-interface-sdk-split-depfile` 调用方 PR，否则正式链路只有脚本能力，没有调用方启用。该调用方使用独立分支名，避免与 build #7049 的来源分支混淆；两个 PR 关联同一 Issue #4706 后联合触发门禁。
3. #6999 文件范围最大，且包含 #6965、#6974、#6982 的重叠历史内容，评审风险最高；若社区要求，应按 packages 聚合、host symlink、validator 根因拆分。
4. #7046、#7048 是从组合工作树拆出的最新基线独立分支，尚未单独重新编译；应以社区门禁和后续人工两轮复验补齐证据。
5. 当前最终零改动轮次仍有 9 个主 Ninja 步骤：3 个 metadata stamp、4 个 metadata Action（`generate_host_info`、`gen_binary_installed_info`、`src_sa_infos_process`、`merge_all_parts`）以及 2 个 ramdisk image Action。后续优化应继续从这些真实剩余节点向上定位，不能在 `phone_install_modules` 或镜像尾端直接跳过任务。

## 6. 证据来源与口径

- PR 状态、创建时间、更新时间、HEAD 和实际变更文件：2026-09-09 通过 GitCode OpenHarmony 仓库 API 只读查询。
- 全流程历史：`docs/incremental-build-repair-process-20260825.md`。
- SDK split：`docs/glm52-phone-install-final-handoff-20260828.md`。
- iptables：`docs/glm52-geninit-fix-handoff-20260901.md`、`docs/iptables-geninit-pr-20260902.md`。
- 分支重组：`D:/workspace/phone-install-publish-20260902/build-functional-groups-20260903.md`。
- 39→9 的统计使用主 Ninja 实际记录数量；Ninja 进度分母是动态估计，不能当作实际执行条数。
- “Action 为 0”只在明确保存的零改动第二轮日志中使用；没有独立构建证据的 PR 标记为“独立分支未重编”，不使用组合结果替代单 PR 结果。
