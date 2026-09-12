# 原始 10 个 packages Action 增量问题修复交接（2026-09-10）

## 1. 目标与阶段结论

本轮原始目标是修复 `rk3568/phone` 连续无源码变化构建中，`//build/ohos/packages` 下最初列出的 **10 个 Action 重复执行问题**。截至现有两轮验证记录，这 10 项已经初步完成修复：前 9 项逐步收敛，最后的 `phone_install_modules` 在 2026-09-01 组合工作树两轮构建中也均未执行。

**阶段状态：原始 10 项增量问题初步修复完成；正式 PR 合入及独立分支验证继续跟进。** 这两个状态分别记录：组合工作树的构建结果说明修复效果，PR 的评审、门禁和合入状态说明上游交付进度。

2026-09-01 最后两轮仍各有 9 个主 Ninja 步骤：3 个 metadata stamp、4 个 metadata Action（`generate_host_info`、`gen_binary_installed_info`、`src_sa_infos_process`、`merge_all_parts`）及 2 个 ramdisk image Action。这些不在原始 10 项列表中，归入后续扩展优化，不能据此把原始任务继续标记为未完成。剩余的 `generate_host_info` 也不是原始目标 `generate_host_symlink`。

本文的代码说明依据 2026-09-10 读取的 GitCode PR 实际 diff；构建结论依据历史验证记录，本次没有重新编译。旧交接中的“7/10”“9/10”“phone_install_modules 未完成”只描述对应日期，不再作为当前总进度。

## 2. 原始 10 项与 PR 对照

以下名称均省略共同前缀 `//build/ohos/packages:`。多个 Action 可以由同一 PR 修复；一个 Action 也可能依赖多个上游修复。PR 数量不等于目标数量。

| 序号 | 原始 Action | 直接修复 PR | 关键配套 | 代码作用与验证结论 |
| --- | --- | --- | --- | --- |
| 1 | `sa_profile_src_phone` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | [#6999](https://gitcode.com/openharmony/build/merge_requests/6999)、[#7009](https://gitcode.com/openharmony/build/merge_requests/7009) 的 parts 元数据稳定化 | SA 输入按 label 排序，源 SA 安装 JSON 内容不变不覆盖；组合验证第二轮不执行 |
| 2 | `sa_profile_binary_phone` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | #6999、#7009 的 parts 元数据稳定化 | ZIP 通过 `atomic_output` 比较后发布；已测 rk3568 配置组合验证第二轮不执行 |
| 3 | `phone_sa_profile_install_info` | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 上述源/二进制 SA 稳定输出 | 合并安装信息启用 `check_changes=True`，上游内容不变时截断传播；第二轮不执行 |
| 4 | `check_seccomp_filter_name` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 同 PR 的稳定 validation 输入层 | 真正生成成功结果，记录 cfg/seccomp 文件依赖，验证异常移除旧成功结果；第二轮不执行 |
| 5 | `process_field_validate` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 同 PR 的稳定 validation 输入层 | 补齐 cfg/白名单 depfile、成功输出和验证异常清理；第二轮不执行 |
| 6 | `collect_notice_files__phone` | [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009) | [#7048](https://gitcode.com/openharmony/build/merge_requests/7048) 的许可证边界及 depfile 修正 | NOTICE 收集和最终发布拆为两阶段，稳定部件元数据；stage/collect/merge 第二轮均不执行 |
| 7 | `generate_host_symlink` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 同 PR 的 host 元数据规范化与 collector | collector 输出稳定 `host_symlink_info.json`，原 Action 只消费该中间结果；第二轮发布阶段不执行 |
| 8 | `phone_hisysevent_install_info` | [build #7006](https://gitcode.com/openharmony/build/merge_requests/7006) | parts 元数据链 | 配置 JSON、安装 JSON 内容不变不覆盖，实际 YAML 加入 depfile；第二轮不执行 |
| 9 | `phone_install_modules` | [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046)，以及 #6999 的安装元数据稳定化 | [iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62)、build #6982/#6974/#7049、packing_tool #1556 及其他已验证上游补丁，详见第 4 节 | 修正 SA depfile 过滤，稳定安装输出，消除真实输入链的无效重编译/重链接；2026-09-01 组合工作树连续两轮均不执行 |
| 10 | `phone_parts_list` | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999)、[#7009](https://gitcode.com/openharmony/build/merge_requests/7009) | 公共 JSON 语义比较 | 聚合及 part 安装信息内容不变时不覆盖，避免带动 packages 下游；组合验证第二轮不执行 |

## 3. 各 Action 的代码修改和作用

### 3.1 sa_profile_src_phone

PR：[build #6965](https://gitcode.com/openharmony/build/merge_requests/6965)，HEAD `0d530d7e`；[diff 快照](evidence/20260910/build-6965.json)。

- `ohos/sa_profile/src_sa_profile_process.py`：`sa_info_process()` 按 `label` 排序；`main()` 写处理结果时启用 `check_changes=True`。
- `ohos/sa_profile/sa_profile_source.py`：源 SA 安装信息 JSON 启用 `check_changes=True`。
- `scripts/util/file_utils.py`：`__check_changes()` 从对 `str(dict)` 计算哈希改为直接比较解析后的 JSON 对象，避免字典键顺序影响变化判断；列表顺序仍按列表语义比较。

原先元数据顺序或无条件覆盖会更新时间戳，继续带动 SA Action。修改后相同内容保留输出时间戳；再配合 #6999/#7009 稳定 parts 输入，原始目标在组合第二轮不再执行。单独 SA 验证中允许源 Action 被上游调度但输出不变，不能把这类 `restat` 生效误写成该 Action 当轮没有执行。

### 3.2 sa_profile_binary_phone

PR：[build #6965](https://gitcode.com/openharmony/build/merge_requests/6965)；[diff 快照](evidence/20260910/build-6965.json)。

`ohos/sa_profile/sa_profile_binary.py` 将直接打开最终 ZIP 改为在 `build_utils.atomic_output()` 中生成临时 ZIP。字节相同则保留原文件，变化才发布，防止一次重复归档继续扰动安装链。原有 `add_to_zip_hermetic()` 调用得到保留。

已验证范围是当时的 rk3568/phone 配置。实际 diff 中 `part_name_info.json` 仍通过普通 `outfile.writestr()` 写入，不能据此宣称非空 binary SA 或其他产品的 ZIP 元数据均已确定化。该覆盖边界不影响已有产品的阶段结论，其他配置需要单独复验。

### 3.3 phone_sa_profile_install_info

PR：[build #6965](https://gitcode.com/openharmony/build/merge_requests/6965)；[diff 快照](evidence/20260910/build-6965.json)。

`ohos/sa_profile/sa_profile_merge.py` 的 `_generate_install_info()` 对合并后的 SA 安装列表启用 `check_changes=True`。源/二进制 SA 产物保持稳定后，不再因仅有时间戳变化重复生成最终安装信息。2026-08-12 SA 独立第二轮已有该 Action 不执行的记录，后续组合验证继续覆盖。

### 3.4 check_seccomp_filter_name

PR：[build #6999](https://gitcode.com/openharmony/build/merge_requests/6999)，HEAD `f1a46334`；[diff 快照](evidence/20260910/build-6999.json)。

- `ohos/packages/BUILD.gn`：新增 `${_platform}_validation_install_modules` 稳定输入阶段；原 validator 依赖该阶段，声明 result 和 depfile，并把路径传入脚本。
- `ohos/packages/stabilize_json_file.py`：读取安装信息 JSON，以内容感知方式写出 `phone_validation_install_modules.json`。
- `ohos/packages/check_seccomp_library_name.py`：排序遍历 cfg/seccomp 目录，将实际读取/检查的文件收集到 depfile；验证成功后用 `atomic_output` 写入固定成功文本；验证异常时移除旧 result 并继续抛出异常。

根因包含 GN 声明的 `packages/phone/check_seccomp_filter_name.txt` 原先没有真实生成，以及上游安装元数据的时间戳传播。修改同时补齐成功输出和依赖，不通过跳过校验获得 clean。2026-08-20 第二轮不执行；失败用例返回非零并清理预置旧成功结果。

### 3.5 process_field_validate

PR：[build #6999](https://gitcode.com/openharmony/build/merge_requests/6999)；[diff 快照](evidence/20260910/build-6999.json)。

复用 3.4 的稳定 validation 输入层。在 `ohos/packages/process_field_validate.py` 中：

- 使用命名参数解析，检查必需选项，拆分参数处理、目录校验和主入口；
- 排序遍历 `.cfg`，将实际 cfg 文件和存在的权限/critical 白名单加入 depfile；
- 校验成功后生成固定 `cfg_validate_result.txt`，内容相同不覆盖；
- 校验异常时删除旧成功结果并返回失败，保留原有权限和重启策略检查。

原先声明输出缺失和安装信息重复变化会使校验每轮执行。补丁使 Ninja 能够跟踪真实依赖并识别有效结果。2026-08-20 第二轮不执行；失败用例验证了非零退出和旧结果清理。

### 3.6 collect_notice_files__phone

主要 PR：[build #7009](https://gitcode.com/openharmony/build/merge_requests/7009)，HEAD `edc427a8`；补充 PR：[build #7048](https://gitcode.com/openharmony/build/merge_requests/7048)，HEAD `6840a0ba`。证据：[#7009 diff](evidence/20260910/build-7009.json)、[#7048 diff](evidence/20260910/build-7048.json)。

#7009 的实际改动：

- `ohos/generate_part_info.py`：part install、dep modules、host modules 三类 JSON 写入启用 `check_changes=True`。
- `ohos/packages/parts_install_info.py`：平台安装列表启用内容感知写入。
- `scripts/util/file_utils.py`：使用解析后的 JSON 语义比较。
- `ohos/packages/BUILD.gn`：原 collector 改名为 `stage_notice_files__<platform>`，保留真实输入和 depfile，输出至 `target_gen_dir`；原 `collect_notice_files__<platform>` 改为 `copy_ex`，发布稳定中间 ZIP 到原最终路径。

链路变为：真实许可证/模块输入 → stage → 稳定中间 ZIP → 原 collect 发布目标 → NOTICE merge。最终路径和下游接口保持一致。2026-08-24 及 08-25 的两组验证中，stage、collect、merge 第二轮均未执行，中间与最终 ZIP 的哈希和时间戳保持稳定。

#7048 补充两处正确性修复：`collect_module_notice_file.py` 先查当前目录的 LICENSE，再判断是否到达搜索边界；`collect_system_notice_files.py` 移除把生成 NOTICE 列表追加回 depfile 的语句。该独立分支拆出后未重新整仓编译，不把 #7009 的双轮结果归为 #7048 单独效果。

### 3.7 generate_host_symlink

PR：[build #6999](https://gitcode.com/openharmony/build/merge_requests/6999)；[diff 快照](evidence/20260910/build-6999.json)。

- `ohos/common/BUILD.gn`：原 host `generated_file` 改为 `generate_host_info_raw`，输出原始 JSON；新增 Action 负责稳定发布 `all_parts_host.json`。
- `ohos/common/generate_host_info.py`：检查输入类型，以规范 JSON 内容为排序键稳定 host 列表，内容相同不重写。
- `ohos/packages/BUILD.gn`：拆为 `collect_host_symlink_info` 和原 `generate_host_symlink` 两阶段。
- `ohos/packages/generate_host_symlink.py`：collector 读取 part/module 信息，将真实读取文件写入 depfile，生成稳定 `host_symlink_info.json`；发布阶段读取该映射并创建缺失链接，`subprocess.run(..., check=True)` 保留链接失败结果，最终 JSON 使用内容感知写入。

作用是将上游元数据变动与实际链接发布分开。2026-08-20 第二轮 collector 可以执行，但原始 `generate_host_symlink` 不执行；中间和最终 JSON 快照稳定。不能把 collector 或 `generate_host_info` 后续仍执行算作原始目标重新失败。

### 3.8 phone_hisysevent_install_info

PR：[build #7006](https://gitcode.com/openharmony/build/merge_requests/7006)，HEAD `3dc5695a`；[diff 快照](evidence/20260910/build-7006.json)。

- `hb/util/loader/load_ohos_build.py`：仅在处理 `hisysevent_config` 时启用 `check_changes=True`，其余 part 类型沿用原行为。
- `ohos/hisysevent/hisysevent_process.py`：将实际 `hisysevent_config_files` 加入 depfile；生成 install info JSON 时启用 `check_changes=True`。

该 PR 的直接改动是稳定写入与补齐 YAML 依赖，没有新增全量排序或 ZIP 算法。配置不变时不再传播 mtime，真实 YAML 变化仍可触发。2026-08-24 第二轮 Action 为 0，config、install info、ZIP、depfile 哈希稳定。

### 3.9 phone_install_modules

这是最后收敛的原始目标，需要同时处理自身元数据与上游真实二进制输入。主要直接改动见 [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046)，HEAD `5be8fa47`；[diff 快照](evidence/20260910/build-7046.json)。

- `ohos/packages/modules_install.py`：把 `depfiles.extend([item for item in depfiles if item not in sa_files])` 改为列表过滤赋值，真正排除原逻辑意图排除的 SA 文件，避免保留原列表后重复追加。
- `ohos/common/binary_install_info.py`：binary install JSON 启用 `check_changes=True`；可选 `dist_parts_info_file` 存在时才进入 depfile，避免不存在的可选输入持续触发 dirty。
- 前序 #6999 的 `modules_install.py` 已稳定 install/module JSON 和 module list 输出，并在 arm64e 列表为空时也生成对应声明结果。

仅改这些文件不足以解释最终收敛。此前 SDK、IDL、ArkUI 等链路确有重编译/重链接，更新后的二进制是安装 Action 的真实输入，必须逐层修上游。最后一层 iptables 由 [third_party_iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) 修复：`extensions/genInit.py` 改用 `io.StringIO` 生成完整文本，与现有 UTF-8 文件比较后决定是否写入，保留原有注册顺序和 MD5 helper 行为。

`initext.c`、`initext4.c`、`initext6.c` 不再无变化重写后，3 个 CC、3 个 AR 和 iptables LINK 均不再执行。2026-09-01 两轮 `phone_install_modules` 均为 0，主 Ninja 实际执行均为 9 步。39→9 是组合修复工作树的前后变化，不是 #62 或 #7046 单个 PR 的独立收益。

### 3.10 phone_parts_list

PR：[build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) 与 [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009)。

- #6999：`ohos/common/merge_all_subsystem.py` 对聚合信息启用内容感知写入；`ohos/packages/parts_install_info.py` 对安装列表启用内容感知写入；公共 JSON helper 采用语义比较。
- #7009：将稳定写入继续向前扩展到 `ohos/generate_part_info.py` 的 part install/dep/host 元数据；包含相同的 `parts_install_info.py` 和 helper 修正。

作用是稳定 `all_parts_info.json`、`system_install_parts.json` 及其输入，阻止上游只改 mtime 时继续调度 `phone_parts_list`、SA 和 NOTICE。2026-08-20 组合第二轮已有 `phone_parts_list` 不执行的记录。两个 PR 存在代码重叠，应在合入时核对，不重复计算收益。

## 4. 安装链上游修复与正式提交覆盖

### 4.1 已有 PR 的配套修复

| PR | 主要代码改动 | 对原始目标的作用 |
| --- | --- | --- |
| [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) | `app_internal.gni` 将共享/不足以表达结果的 stamp 改为 target 独立 `sign_result.json`；`compile_app.py` 排序 unsigned 路径并记录 SHA-256；`app_sign.py` 记录签名输出路径和哈希；`build_utils.py` 增加哈希和原子 JSON helper | 稳定 HAP/HSP 签名结果代理，内容不变时减少向 package/install 传播；真实 HAP 变化仍需签名 |
| [packing_tool #1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556) | `adapter/ohos/Compressor.java` 增加统一 ZIP entry 时间设置 helper，并在相关 entry 创建路径调用 | 降低 HAP 字节非确定性，使相同输入的 Telephony/Contacts 连续打包哈希一致，为下游签名稳定判断提供前提 |
| [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) | `config/components/idl_tool/idl.gni` 区分本地与 source-absolute common IDL；外部 IDL 保留为输入，不错误声明成当前 Action 输出；修正双 `i` 名称转换 | 消除缺失/错误输出引起的重复 IDL Action 及后续 CXX/SOLINK/install 链 |
| [build #7049](https://gitcode.com/openharmony/build/merge_requests/7049) | `ohos/sdk/parse_interface_sdk.py` 增加可选 `--stamp`/`--depfile`；记录 SDK 文件和目录、Node、权限定义、Python 依赖及 public SDK 输入；真实处理成功后写稳定 stamp | 配套调用方启用后，`ohos_base_split` 第二轮为 0，避免缺失输出持续带动声明生成和重链接；仅合入脚本支持不会自动启用调用方 |
| [iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) | `extensions/genInit.py` 改为完整文本生成后比较再写，修正未调用的 `close` | 阻断 3 个聚合 C 文件 → CC/AR/LINK → `phone_install_modules` 的最后已识别无效链 |

上述 PR 的实际文件、diff、HEAD 和查询时间保存在 [证据索引](evidence/20260910/README.md)。

### 4.2 已准备补丁但 PR 编号尚未确认的部分

组合验证还包含下列修复；现有发布清单给出了独立提交，但本次核对的 13 个已知 PR 不覆盖全部补丁。这里明确记录缺口，不为它们编造 PR 编号，也不将组合构建通过写成这些独立分支已通过门禁。

| 仓库 / 分支 | 已准备提交 | 代码与作用 | PR 记录 |
| --- | --- | --- | --- |
| `interface_sdk-js` / `fix-interface-sdk-split-depfile` | `680b35e0` | `BUILD.gn` 为 `ohos_base_split` 传入 stamp/depfile，配套 build #7049 | 9 月 9 日交接记录尚待创建；需关联同一 Issue #4706，本次未定位新的 PR 编号 |
| `interface_sdk-js` / `fix-sdk-declaration-incremental-deps` | `df667b6d` | `BUILD.gn`、`process_internal.py`、`remove_internal.py` 补充声明及内部接口生成依赖 | 尚未确认 |
| `arkcompiler_ets_frontend` / `fix-build-system-output-isolation` | `5eb9bc67` | `driver/build_system/BUILD.gn` 隔离生成物与元数据目录 | 尚未确认 |
| `developtools_ace_ets2bundle` / `fix-libarkts-sdk-incremental-deps` | `8a4c58bc` | `ets1.2/BUILD.gn`、`ets1.2/libarkts/BUILD.gn` 隔离 SDK 输出并收窄实际输入范围 | 尚未确认 |
| `build` / `fix-js-assets-incremental-deps` | `f03aa33b` | `scripts/build_js_assets.py` 处理空资源依赖并过滤临时 loader 缓存 | 尚未确认 |
| `build` / `fix-idl-acronym-header-outputs` | `97c0d5bc` | `idl.gni` 修正连续大写缩写接口的头文件输出；与 #6982 的 common IDL 问题不同 | 尚未确认 |
| `build` / `fix-preloader-content-aware-output` | `07a42d2c` | `hb/services/loader.py`、`hb/util/io_util.py` 稳定预加载 JSON/syscap 输出 | 发布清单列为后续批次，尚未确认 |
| `build` / `fix-static-abc-config-copy` | `00c502f7` | `generate_static_abc.py` 消除源配置写回副作用 | 发布清单列为后续批次，尚未确认 |

发布清单来源：`D:/workspace/repositories/pr-publishing/publish-manifest.json`，分组规则见同目录 `build-functional-groups-20260903.md`；旧七分支发布方案已被五个功能组取代。ArkGuard/TypeScript/Declgen 安装依赖的等价修复在拆分时已进入上游，不重复作为新 PR。ets2panda 一致性检查适配，以及 `lite_component.gni`、`build_image.py` 的未发布修改继续保留原交接中的待审边界。

### 4.3 早期三个独立 Action

仓库早期还记录了 `ark_jsf`、`gen_snapshot`、`airscan_action` 三项。它们不占用第 2 节原始 packages 十项的计数，但保留成果与来源：

- [third_party_jsframework #853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853)：`js_framework_build.sh` 保留共享 runtime 目录；比较 snapshot 输出内容，相同时用备份文件时间恢复输出 mtime，并与 css-what stamp 协调 runtime 目录时间。实际 diff 使用 `touch -r`，不能描述为全程仅靠原子替换。历史第二轮 `ark_jsf`、`gen_snapshot` 均为 0。
- [third_party_sane-airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22)：`BUILD.gn` 从同一源文件列表推导 inputs/outputs/编译 sources；`patch_install.py` 在生成目录 staging 中应用补丁，比较内容后逐文件发布，保留失败退出，避免构建修改源码树。历史第二轮 `airscan_action` 为 0。

## 5. 验证证据与适用范围

| 证据 | 已确认结果 | 原始日志位置 / 本地说明 |
| --- | --- | --- |
| SA 独立验证，2026-08-12 | 源/二进制 SA 输出稳定，最终 `phone_sa_profile_install_info` 不执行 | `/srv/workspace/action_incremental_logs_20260812/`；[历史方法交接](current-project-handoff.md) |
| packages/host/validator 组合，2026-08-20 | 原始 10 项中的 7 项第二轮不执行，包括 parts、三个 SA、host 发布和两个 validator | `/srv/workspace/action_incremental_logs_20260820/host_symlink_two_stage/second_console.log`；同级 `host_validator_upstream_v2/`；[交接](incremental-build-handoff-20260824.md) |
| HiSysEvent，2026-08-24 | 第 8 项能力收敛：`phone_hisysevent_install_info=0` | `/srv/workspace/action_incremental_logs_20260824/hisysevent_incremental/`；[交接](incremental-build-handoff-20260825.md) |
| NOTICE，2026-08-24/25 | 第 9 项能力收敛：NOTICE stage/collect/merge 均为 0 | `/srv/workspace/action_incremental_logs_20260824/notice_two_stage_v3/`；[交接](incremental-build-handoff-20260825.md) |
| SDK split，2026-08-28 | 配套工作树 `ohos_base_split=0`；该阶段最终 install 仍受后续上游影响 | `/srv/workspace/action_incremental_logs_20260828/ohos_base_split_depfile_fix/`；[交接](glm52-phone-install-final-handoff-20260828.md) |
| 最终组合，2026-09-01 | 两轮 `phone_install_modules=0`、iptables CC/AR/LINK=0；所记录的 9 个剩余步骤不含原始十项 | `/srv/workspace/action_incremental_logs_20260901/geninit_content_aware_fix/`；[两轮结果交接](glm52-geninit-fix-handoff-20260901.md) |

最后两轮关键数据：第一轮 GN 24.37 秒、Ninja 21.73 秒；第二轮 GN 24.72 秒、Ninja 20.84 秒；主 Ninja 实际步骤均为 9。三份 initext C 文件保持 2026-09-01 15:59:29 的原时间戳。历史残留 `error.log` 不代表这两轮出现新失败，详见原交接中的哈希核对。

验收口径：

1. “初步完成”限于既有 rk3568/phone 配置和已保存的验证记录；本次对历史记录归档整理，没有重新取得一轮构建数据。
2. Action 为 0 使用真实第二轮日志，不能只用 `ninja -n` 的 dirty 推演代替；内容和 mtime 稳定、`restat` 截断下游也是有效证据，但应与“Action 没执行”分别表述。
3. 组合工作树包含多个仓库及尚未全部发布的补丁。#7046、#7048 等从组合工作树拆出的独立分支没有单独整仓双轮证明。
4. 初步修复完成不代表所有 PR 已合入，也不代表其他产品、非空 binary SA 等未覆盖配置已验证。

## 6. 当前 PR 交付状态与后续范围

2026-09-10 对现有 13 个 PR 逐个读取公开 API 的状态与 files diff：全部 `open`，其中 12 个 `mergeable=true`，airscan #22 为 `mergeable=false`。这里是已知 PR 清单的核对结果，不是账号所有 PR 的穷举。`mergeable` 不是门禁通过或评审通过。各 PR 的完整 HEAD、实际文件数、查询时间见 [证据索引](evidence/20260910/README.md)。

后续以收尾交付为主：补齐未确认的配套 PR，协调 SDK split 两仓，跟进 #6999 与 SA/HAP/IDL 历史补丁的重叠，处理 airscan 分支不可直接合并状态，补充独立分支门禁和必要的人工双轮验证。

剩余 metadata 与 ramdisk 的 9 步作为扩展优化另行立项，不自动纳入原始十项验收。继续修改时先保存 Git 版本，再按最早直接 dirty 原因定位；完整构建沿用人工执行流程，正式提交保留 DCO。
