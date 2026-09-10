# OpenHarmony 增量编译问题定位与修复过程（2026-08-25）

## 1. 文档目的与范围

本文记录本轮 OpenHarmony rk3568 增量编译治理从第一个问题定位开始，到当前 NOTICE 修复验证完成为止的完整过程。重点不是简单罗列提交，而是回答以下问题：

- 为什么可以判断某个 `ACTION` 属于零代码改动下的异常重跑；
- 如何从控制台、`build.log`、Ninja explain、文件属性和哈希反推到具体代码；
- 每个修复为什么选择稳定输出、补充 depfile、修正 `outputs` 或拆分两阶段等方案；
- 修复后如何证明第二轮没有误触发，并且没有掩盖真实输入变化；
- 哪些结论已经由日志和提交支撑，哪些仍属于局部验证或后续问题。

主要验证环境：

- 产品：`rk3568`
- 远程源码根目录：`/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code`
- 远程日志根目录：`/srv/workspace/action_incremental_logs_YYYYMMDD`
- 构建入口：`./build.sh --product-name rk3568 --ccache --build-target ...`
- 增量验证方式：同一源码、同一输出目录、无代码改动连续执行两轮构建

本文中的“第二轮未执行”均指对应目标没有出现在第二轮 Ninja 执行记录中；只看到 `BUILD_STATUS=0` 不足以得出该结论。

阶段状态和后续接续说明见 [incremental-build-handoff-20260825.md](./incremental-build-handoff-20260825.md)，本文侧重保留定位、实现与验证的技术过程。

## 2. 涉及的技术栈

### 2.1 OpenHarmony 构建链路

本轮问题主要位于下面这条链路：

```text
build.sh
  -> preloader / loader
  -> gn gen
  -> Ninja 依赖图与 dirty 判定
  -> GN action / generated_file / copy
  -> Python、Shell、Java 等生成脚本
  -> JSON、ZIP/HAP、stamp、depfile 和安装元数据
```

GN 负责把声明的 `inputs`、`outputs`、`deps` 转换为 Ninja 规则；Ninja 根据输入、输出、命令行和依赖关系决定目标是否 dirty。生成脚本即使产出内容相同，只要无条件重写文件，也会改变 `mtime`，继续带动下游目标。

### 2.2 本轮用到的诊断能力

- `ninja -n -d explain`：查看目标为什么被判定为 dirty；
- `ninja -t query <target>`：查看目标的直接输入、输出和依赖关系；
- `.ninja_log`：确认目标实际执行时间和输出记录；
- `gn desc`：把 GN target、脚本、输入和输出关联起来；
- `stat`、`sha256sum`：区分内容变化、时间戳变化和文件替换；
- depfile：让脚本动态读取的配置文件真正进入 Ninja 依赖图；
- `restat=1`：动作执行后若输出状态未改变，阻止无意义的 dirty 状态继续向下传播；
- Git/Repo manifest：区分当前快照可验证提交、正式上游提交和迁移提交。

### 2.3 代码层的核心修复模式

本轮修复主要落在五类模式中：

1. **内容一致时不改文件**：JSON 先解析后比较，文本和二进制使用临时文件比较，只有内容变化时才替换。
2. **输出声明与实际生成一致**：GN `outputs` 必须声明脚本真实生成的文件，不能把目录或并未生成的占位文件当作输出。
3. **动态输入写入 depfile**：脚本扫描目录、解析 JSON/YAML 后发现的文件，需要写入 depfile；否则真实输入变化不会触发重建。
4. **归档产物可复现**：ZIP/HAP 固定 entry 时间、顺序、权限与压缩参数，避免内容等价但字节不稳定。
5. **动态收集与稳定发布拆层**：允许上游 collector 扫描并执行，但先生成稳定中间产物，再由 leaf action 或 `copy` 发布最终产物，从而切断无效传播。

## 3. 判定问题和验证修复的方法

### 3.1 两轮构建的判定原则

第一轮用于让修改后的规则和输出收敛，第二轮在源码、命令和输出目录完全不变的前提下验证零改动行为。每轮至少保留：

- 控制台完整日志；
- `out/rk3568/build.log`；
- `out/rk3568/build_error.log`；
- `out/rk3568/.ninja_log`；
- 目标输出的 inode、mtime、size、SHA-256；
- 目标有动态输入时生成的 depfile；
- 对应分支、HEAD 和工作区状态。

建议统一记录格式：

```text
<output>|inode=<inode>|mtime=<epoch>|size=<bytes>
<sha256>  <output>
```

第一轮和第二轮比较时，应分别回答：

- 构建是否成功；
- 被测 `ACTION` 是否执行；
- 输出内容是否变化；
- 内容相同的输出是否被无条件重写；
- 被测动作未执行时，是否仍有其他上游或下游动作执行；
- 修改真实输入后，目标能否重新执行。

### 3.2 从日志定位到代码的固定路径

每个问题都按以下顺序收敛：

1. 从第二轮控制台日志提取重复 `ACTION` 的完整 GN label。
2. 使用 `ninja -d explain` 找到第一个 dirty 输入或缺失输出。
3. 使用 `ninja -t query`、`gn desc` 和生成的 `build.ninja` 找到脚本、`inputs`、`outputs`、depfile 和下游消费者。
4. 对相关输出记录两轮 `stat` 与 SHA-256：
   - SHA 相同、mtime 变化：通常是无条件重写；
   - 文件缺失：通常是输出声明错误或脚本未生成声明产物；
   - SHA 变化：继续检查输入是否真的变化、集合顺序是否稳定、归档元数据是否稳定；
   - 上游动作执行但输出没变、下游仍执行：检查中间层是否缺少稳定边界。
5. 检查脚本实际读取的文件是否全部进入 GN `inputs` 或 depfile。
6. 采用最小职责修复，并执行两轮构建、输出快照对比和至少一次真实输入变化验证。

### 3.3 为什么不能只用 grep 或 `BUILD_STATUS=0`

`grep` 只适合从已经结束的日志中提取证据。如果把构建命令和 grep 粘在同一个命令块里，或者误复制包含构建入口的整段命令，就可能再次触发编译。因此验证命令应分为“执行构建”和“离线查看日志”两组。

同样，`BUILD_STATUS=0` 只能证明编译返回成功，不能证明增量行为正确。至少还要核对第二轮动作、文件状态和依赖边界。

## 4. 远程日志备份索引

下列目录已经在远程确认存在：

| 日期 | 日志目录 | 主要内容 |
| --- | --- | --- |
| 2026-08-04 | `/srv/workspace/action_incremental_logs_20260804` | jsframework、airscan 初始定位和最终零改动验证 |
| 2026-08-05 | `/srv/workspace/action_incremental_logs_20260805` | packages 聚合链路早期实验 |
| 2026-08-07 | `/srv/workspace/action_incremental_logs_20260807` | HAP 签名、seccomp、packages 输出调查 |
| 2026-08-12 | `/srv/workspace/action_incremental_logs_20260812` | SA Profile、HAP 时间戳与直接 Ninja 验证 |
| 2026-08-13 | `/srv/workspace/action_incremental_logs_20260813` | compile_app、HAP 打包探针、IDL 输出定位 |
| 2026-08-14 | `/srv/workspace/action_incremental_logs_20260814` | IDL 修复迭代日志 |
| 2026-08-17 | `/srv/workspace/action_incremental_logs_20260817` | IDL 最终验证和迁移验证 |
| 2026-08-18 | `/srv/workspace/action_incremental_logs_20260818/arkui_stamp_fix` | ArkUI stamp 输出修复验证 |
| 2026-08-19 | `/srv/workspace/action_incremental_logs_20260819` | ets2bundle、phone_parts、SA/package 组合验证 |
| 2026-08-20 | `/srv/workspace/action_incremental_logs_20260820` | host symlink、process field、seccomp validator |
| 2026-08-24 | `/srv/workspace/action_incremental_logs_20260824` | HiSysEvent、part metadata、NOTICE 两阶段修复 |
| 2026-08-25 | `/srv/workspace/action_incremental_logs_20260825/notice_repeat` | NOTICE 当前分支补充两轮复验 |

2026-08-25 的补充目录包含：

```text
first_console.log
second_console.log
second_build.log
second_ninja.log
second_outputs.txt
```

这次第一轮的 `build.log`、`.ninja_log` 和结构化 `first_outputs.txt` 没有在构建结束后单独拷贝，之后相关内部日志已经被第二轮覆盖，因此不能补造为第一轮证据。文档保留这个缺口，以两轮控制台、第二轮构建/Ninja 日志和第二轮输出快照作为补充证据。后续所有验证应在每一轮结束后立即复制内部日志与输出快照。

推荐的远程目录结构为：

```text
/srv/workspace/action_incremental_logs_YYYYMMDD/<topic>/
  branch_head.txt
  first_console.log
  first_build.log
  first_error.log
  first_ninja.log
  first_outputs.txt
  second_console.log
  second_build.log
  second_error.log
  second_ninja.log
  second_outputs.txt
  explain.log
  query.txt
```

## 5. 逐项修复过程

### 5.1 jsframework：`ark_jsf` 与 `gen_snapshot`

#### 现象和证据

仓库：`third_party/jsframework`。

`/srv/workspace/action_incremental_logs_20260804/incremental_second_console.log` 中，第二轮仍出现：

- `ACTION //third_party/jsframework:gen_snapshot`
- `ACTION //third_party/jsframework:ark_jsf`

`incremental_explain.log` 给出的关键 dirty 链路包括：

- 声明输出 `obj/third_party/jsframework/runtime` 不存在；
- css-what 源文件复制到共享 `runtime` 目录；
- `css_what_sources.stamp` 变脏；
- `strip.native.min.js` 被重新生成；
- dirty 状态继续传递到 snapshot 动作。

#### 根因

`js_framework_build.sh` 同时承担 runtime 目录清理、依赖复制和 bundle 生成。脚本删除再创建共享目录，并覆盖 `strip.native.min.js`。即使最终内容一致，目录和文件时间戳仍变化。GN 又把目录作为动作输出，Ninja 无法获得稳定的文件级输出边界。

#### 代码思路

- 不再每轮删除 `runtime` 目录；
- 对 snapshot 使用临时备份，生成后通过 `cmp -s` 比较；
- 内容一致时恢复原文件及其 mtime，内容变化时才保留新文件；
- 使用 `touch -r css_what_sources.stamp runtime` 让共享目录时间戳与真实来源稳定关联；
- 避免“为了生成一个文件而扰动整个共享目录”。

迁移验证提交：

- `869aec84388a`：Preserve jsframework incremental build outputs
- `d0752be1bbf`：Stabilize shared runtime directory timestamp

历史正式修复提交为 `a280a42`。当前 2026-08-16 快照使用迁移后的等价提交验证。

#### 验证结果

`/srv/workspace/action_incremental_logs_20260804/final_zero_change_console.log` 中，`ark_jsf`、`gen_snapshot` 和同时验证的 `airscan_action` 在零改动轮次中的匹配数量为 0；构建成功，耗时约 11 分 26 秒。

### 5.2 sane-airscan：`airscan_action`

#### 现象和证据

仓库：`third_party/sane-airscan`。

`/srv/workspace/action_incremental_logs_20260804/airscan_target_build.log` 中可以看到 `airscan_action` 执行，后续重试日志出现编译错误和残留 `.rej` 文件。检查 GN 规则后发现：补丁动作直接修改源码目录，但编译目标有时仍引用原始源码；动作声明的输出也不能完整表示真正参与编译的补丁后文件。

#### 根因

- 生成阶段修改 source tree，破坏 hermetic build；
- 补丁重复执行时可能产生 `.rej`；
- patched 文件集合与编译输入集合不一致；
- 输出目录和实际编译文件之间没有一一对应关系。

#### 代码思路

- 在 `${target_gen_dir}/patched` 中构造补丁后的 staging 源码，不改原始仓库；
- 显式维护 `patched_airscan_files`，由同一集合推导 `inputs`、`outputs` 和编译源；
- 使用 `patch --fuzz=0 --no-backup-if-mismatch`；
- 先做正向 dry-run，若已应用则做反向 dry-run判断幂等状态，两者都不成立时直接失败；
- 临时 staging 完成后按内容决定是否替换正式生成目录；
- 排除 OpenHarmony 上不支持的后端，避免把非增量问题混入验证。

迁移验证提交：

- `bb4ab646`：Generate patched airscan sources outside source tree
- `5ed21a6`：Compile airscan entirely from patched generated sources
- `262f313`：Exclude unsupported airscan backends on OHOS

历史正式修复提交为 `37de4f9`。

#### 验证结果

最终零改动日志中 `airscan_action` 不再出现，并且没有新的 `.rej` 或 source tree 修改。

### 5.3 SA Profile：源配置、二进制配置和合并结果

#### 现象和证据

仓库：`build`，正式 PR 为 `build#6965`。

相关目标包括：

- `sa_profile_src_phone`
- `sa_profile_binary_phone`
- `phone_sa_profile_install_info`

早期日志显示，即使 SA 配置语义没有变化，JSON 和 ZIP 仍被重新生成。`/srv/workspace/action_incremental_logs_20260812/sa_validation_second_real_build.log` 中，第二轮仍能看到源配置和二进制配置动作，但合并后的 phone SA profile 已被 `restat` 截断，说明上游动作在执行，稳定输出已经开始发挥作用。

#### 根因

- 配置收集依赖字典或文件系统遍历顺序；
- JSON 无条件写回；
- ZIP 每次重新创建且条目元数据不稳定；
- 旧哈希使用 `str(dict)`，表达的是 Python 对象展示顺序，而不是稳定语义；
- package 聚合元数据上游变化会继续带动 SA 动作。

#### 代码思路

修改文件包括：

- `ohos/sa_profile/src_sa_profile_process.py`
- `ohos/sa_profile/sa_profile_source.py`
- `ohos/sa_profile/sa_profile_binary.py`
- `ohos/sa_profile/sa_profile_merge.py`
- `scripts/util/file_utils.py`

处理方式：

- 按 label 和路径排序后再生成；
- JSON 使用解析后的对象做语义比较；
- 统一使用 `check_changes=True`，内容相同则保留原文件；
- ZIP 先写临时文件，再通过 `atomic_output` 比较并原子替换；
- 条目名称、顺序和压缩参数保持稳定。

正式提交：`0d530d7e`；2026-08-16 快照迁移验证提交：`c08d319f`。

#### 验证结果和边界

SA 独立验证第二轮耗时约 11 分 07 秒，最终合并产物没有被下游重复消费。后续叠加 package 聚合稳定化后，源配置和二进制配置动作也可以在零改动轮次消失。

该验证主要覆盖 rk3568/phone 当前配置。其他产品中非空 binary SA、不同 `part_name_info` 组合仍需要单独覆盖，不能由本次结果直接外推。

### 5.4 HAP 签名：为签名动作增加稳定结果代理

#### 现象和证据

仓库：`build`，正式 PR 为 `build#6974`。

签名动作原先使用共享 stamp 或路径集合表示结果。路径没有变化时，HAP 内容仍可能变化；反过来，签名工具执行但产物内容相同时，共享 stamp 又会制造下游 dirty。

#### 根因

- 多个动作共享或冲突使用同一 stamp；
- 只记录文件路径，不记录输入内容；
- 结果文件不是原子写入；
- 失败场景可能留下看似成功的陈旧结果。

#### 代码思路

相关文件：`app_internal.gni`、`app_sign.py`、`compile_app.py`、`build_utils.py`。

- 每个 target 使用独立的 `${target_name}.sign_result.json`；
- 对输入路径排序，并记录 SHA-256；
- 使用原子 JSON 写入，内容一致时不替换；
- 失败时不生成虚假成功结果；
- 将“签名动作是否需要执行”和“HAP 打包是否可复现”拆成两个责任边界。

正式提交：`34aa8cba`；当前快照迁移提交：`0008197c`。

#### 验证结果

相关证据保存在 2026-08-07 和 2026-08-12 的日志目录。稳定结果代理可以阻止签名结果的无效传播，但若上游 HAP 字节真的变化，签名动作仍会正确执行。

### 5.5 packing_tool：HAP/ZIP 可复现打包

#### 现象和证据

仓库：`developtools/packing_tool`，正式 PR 为 `#1556`。

相同输入两次打包得到的 HAP SHA-256 不一致。ZIP 内容检查发现，各 entry 使用当前时间或来源文件时间，导致归档字节随构建时间变化。

#### 根因

ZIP entry 的时间、顺序、权限或压缩元数据不固定。即使文件内容完全一致，归档中央目录和 entry header 仍会变化。

#### 代码思路

在 `adapter/ohos/Compressor.java` 中统一设置 entry 时间：

- 固定毫秒值 `1546272000000`，即 2019-01-01；
- 普通文件、native 文件、`STORED` entry 和空目录使用同一时间；
- 保持条目顺序、压缩方法和其他归档参数稳定。

正式提交：`dcbbc78`；当前快照迁移提交：`4bcb6aa`。

#### 验证结果

`/srv/workspace/action_incremental_logs_20260813/hap_packing_probe` 中：

- Telephony 两次打包 SHA-256 均为 `5bdc9a9cb1dc99319e2218c3d1b7c3743fcb254301e8ad25fa344f01ca93cd13`；
- Contacts 两次打包 SHA-256 均为 `8e50c50db4671c0ad1ac20e529da59027e7cc17209d6c630290d49372450928e`；
- ZIP entry 时间均为 2019-01-01。

集成验证时发现 Hvigor 实际使用 SDK 内的打包 jar，而不是刚编译的源码 jar，因此曾临时注入源码构建产物验证完整链路。该修复只保证打包可复现，不会掩盖上游 `.so` 的真实变化。

### 5.6 compile_app：稳定声明 JSON

#### 现象和证据

仓库：`build`，验证分支 `fix/compile-app-stable-output`，提交 `918e4c5bc99f0441b5b5d2fe5afc62492ecdad01`。

compile_app 的声明 JSON 内容未变化，但脚本每次覆盖文件，导致下游把它当成新输出。

#### 根因

这是典型的“内容一致、mtime 改变”。动作本身可能因真实上游 `.so` 变化而执行，但不应继续重写语义相同的声明文件。

#### 代码思路

使用 `write_json_file(..., check_changes=True)` 或等价的临时文件比较与原子替换逻辑。判断依据是规范化 JSON 内容，而不是生成时间。

#### 验证结果和边界

`/srv/workspace/action_incremental_logs_20260813/compile_app_stable_output` 中：

- 第一轮成功，约 20 分 21 秒；
- 第二轮成功，约 8 分 44 秒；
- 第一轮 Telephony、Contacts 相关动作均执行；
- 第二轮 Telephony 动作消失，Contacts 仍因真实上游输入变化执行；
- 两轮 JSON 的 inode、mtime、size 和 SHA-256 保持一致。

Ninja explain 同时指出 `libtel_telephony_data.z.so`、`libcontactsdataability.z.so` 等真实上游 dirty。因此本项修复目标是阻止稳定 JSON 的无效下游传播，而不是强制动作永远不执行。

### 5.7 common IDL：修正输出命名和外部文件所有权

#### 现象和证据

仓库：`build`，正式 PR 为 `build#6982`。

IDL 规则生成的输出列表中出现双 `i` 文件名，例如接口名以 `I` 开头时被错误转换为 `iid...`。此外，source-absolute 的 common IDL 被当前 action 声明为输出，实际却由其他位置拥有。

#### 根因

- 接口名规范化规则对首字母 `I` 重复添加前缀；
- 本地生成 IDL 与外部引用 IDL 没有分组；
- action 声明了自己不生成的外部文件，造成缺失输出或持续 dirty。

#### 代码思路

在 `config/components/idl_tool/idl.gni` 中：

- 使用 `filter_exclude(..., ["//*"])` 分离本地 common IDL；
- source-absolute common IDL 仅作为输入，不声明为当前 action 输出；
- 修正接口名到文件名的转换，只生成一份合法前缀；
- `outputs` 只包含当前动作实际拥有的本地生成文件。

正式提交：`4fa37075`；当前快照迁移提交：`e00d6de2`。

#### 验证结果

`/srv/workspace/action_incremental_logs_20260813/idl_common_outputs/correct_idl_outputs.txt` 记录了三个正确输出路径。第一轮双 `i` 检查曾命中 31800 字节，修复后第二轮为 0。2026-08-17 最终验证中，两轮构建分别约 7 分 58 秒和 11 分 40 秒，目标输出的哈希和时间戳稳定。

2026-08-13、08-14 目录保留了中间失败迭代，说明修复经历了输出集合、迁移快照和完整构建的逐步收敛，而不是只保留最终成功日志。

### 5.8 ArkUI：annotate 和相关 stamp 输出

#### 现象和证据

仓库：`foundation/arkui/ace_engine`，本地验证分支 `fix-arkui-action-stamp-outputs`。

相关动作把目录或错误路径作为输出，脚本实际生成的是 `_output.stamp`。`tools/annotate.py` 中还存在 `chdir` 后相对路径写入，导致 stamp 落点依赖运行时工作目录。

#### 根因

- GN 声明输出与脚本实际输出不一致；
- 相对路径在 `os.chdir()` 后含义变化；
- 把目录当作动作输出，目录 mtime 会被其他生成物扰动。

#### 代码思路

- GN 中声明脚本真实生成的 stamp；
- 移除错误的 `ui2abc` 目录输出；
- 在切换目录前使用 `os.path.abspath()` 固定 stamp 路径；
- 每个 action 只拥有自己的文件级输出。

#### 验证结果和状态

证据位于：

- `/srv/workspace/action_incremental_logs_20260818/arkui_stamp_fix`
- `/srv/workspace/action_incremental_logs_20260819/ets2bundle_pr7061`

后续轮次中 `runtime_annotate`、`arkoala_annotate`、`arkoala_process` 不再出现。`components_compile_abc` 仍可能受 libarkts/SDK 链路影响，这是另一条真实依赖链。

该仓当前包含本地验证改动，不能写成已经正式提交的独立 PR。上游可参考 PR `88500` 的输出声明方向。

### 5.9 ace_ets2bundle：`install_arkguard_tsc_declgen`

#### 现象和证据

仓库：`developtools/ace_ets2bundle`，本地验证基于 PR `7061`。

安装动作使用 stamp 表示 node_modules 安装完成，但真实 TypeScript 输入和生成依赖没有进入 Ninja 图。清理 node_modules 后，陈旧 stamp 仍可能让 Ninja 误判为无需执行；反之，无关时间戳也可能触发重跑。

#### 根因

单一 stamp 只能表示上次执行成功，不能表达脚本动态读取的文件集合。

#### 代码思路

- 为动作声明 depfile；
- 脚本在处理依赖时写出实际使用的文件；
- stamp 继续表示成功结果，depfile 负责表达输入变化；
- 真实依赖删除或变化时动作可重新执行。

#### 验证结果和状态

`/srv/workspace/action_incremental_logs_20260819/ets2bundle_pr7061` 中：

- 第一轮动作出现；
- 第二轮动作不再出现；
- depfile 存在；
- 两轮构建分别约 11 分 36 秒和 9 分 13 秒。

当前仓库是本地 dirty 验证状态，不应表述为本地已经形成正式提交。

### 5.10 packages：`phone_parts_list`

#### 现象和证据

仓库：`build`，提交 `0c668bfc72507e69630a35ab8a8972fa8cc338d7`。

`merge_all_parts`、`phone_parts_list` 和 SA/package 下游存在连续触发。对输出快照比较后发现，`all_parts_info.json` 和 `system_install_parts.json` 内容相同但会被重写。

#### 根因

`merge_all_subsystem.py` 和 `parts_install_info.py` 对聚合 JSON 无条件写回。此类文件扇出很大，一个 mtime 变化会带动 SA profile、NOTICE、安装元数据等多个下游。

#### 代码思路

- 生成规范化、排序后的 JSON；
- 使用 `check_changes=True`；
- 内容一致时保留 inode 和 mtime；
- 允许 collector 自身因复杂上游执行，但利用 Ninja `restat` 阻止 dirty 继续传播。

#### 验证结果

`/srv/workspace/action_incremental_logs_20260819/phone_parts_stable_output` 中：

- 两轮 `all_parts_info.json` SHA-256 均为 `43d30...`；
- 两轮 `system_install_parts.json` SHA-256 均为 `3a879...`；
- inode、mtime、size 保持一致；
- 第二轮 `merge_all_parts` 仍执行，但 `phone_parts_list` 和 SA targets 不再执行；
- 两轮耗时约 11 分 28 秒和 8 分 33 秒。

这说明修复边界正确：上游 collector 是否还能进一步优化是后续问题，不影响本项稳定输出对下游的截断效果。

### 5.11 host symlink：动态收集与稳定发布拆层

#### 现象和证据

仓库：`build`，提交 `45c3af2f0c30824953bd69647d23641c14faecc5`。

原规则直接读取大量动态 part/module 元数据并生成最终 symlink 信息。原始 part 列表顺序、嵌套元数据时间戳或扫描顺序改变时，`generate_host_symlink`、`phone_install_modules` 等目标会被带动。

#### 根因

- `generated_file` 输出原始列表顺序不稳定；
- 动态读取的模块元数据没有完整进入 depfile；
- 扫描和最终发布耦合在一个 action 中；
- 软链接创建错误没有被严格传播。

#### 代码思路

- 把 raw list 规范化为排序后的稳定 `all_parts_host.json`；
- 新增 `collect_host_symlink_info` collector，扫描动态元数据并写 stable intermediate 与 depfile；
- leaf action 只读取 stable intermediate，生成 `all_host_symlink.json`；
- 软链接命令使用 `subprocess` 且 `check=True`；
- 最终 JSON 内容一致时不覆盖。

#### 验证结果

`/srv/workspace/action_incremental_logs_20260820/host_symlink_two_stage` 中：

- 第一轮 collector 和 leaf 均执行；
- 第二轮 collector 仍可执行，但 leaf `generate_host_symlink` 不再执行；
- intermediate SHA-256 为 `498a3a7b61f5966c11aac7d5c1936d3143179cb4686e51124d08ffecb70c8474`；
- `all_host_symlink.json` SHA-256 为 `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`；
- 稳定产物 inode、mtime、size 不变；
- 两轮耗时约 11 分 36 秒和 8 分 27 秒。

### 5.12 `process_field_validate` 与 `check_seccomp_filter_name`

#### 现象和证据

仓库：`build`，提交 `f1a463340efbcaa8089df8f47e50409c14ee9322`，Change-Id：`Id298e0a3dd5e4870df0ef3bd86ad87cd7c7dfd7e`。

GN 声明了 validator 的 `.txt` 结果，但脚本成功时没有生成这些文件；验证时一度使用了错误路径 `out/rk3568/cfg_validate_result.txt`，实际产物位于 `out/rk3568/packages/phone/`。此外，安装模块 JSON 被上游无条件重写，validator 动态扫描的 cfg、seccomp 和白名单也没有完整 depfile。

静态检查还指出 `process_field_validate.py` 的 `main()` NBNC 行数为 57，超过阈值 50。

#### 根因

- 声明输出与成功路径实际行为不一致；
- 旧成功文件可能在失败后残留；
- 动态配置缺少 depfile，存在漏构建风险；
- 上游 JSON 不稳定造成 validator 无意义重跑；
- `main()` 同时负责参数解析、校验编排、异常处理和结果文件管理，职责过多。

#### 代码思路

相关文件：

- `ohos/packages/BUILD.gn`
- `ohos/packages/check_seccomp_library_name.py`
- `ohos/packages/modules_install.py`
- `ohos/packages/process_field_validate.py`
- `ohos/packages/stabilize_json_file.py`

处理方式：

- 新增稳定的 `<platform>_validation_install_modules.json` 中间层；
- 安装模块 JSON 采用规范化比较，内容一致不覆盖；
- validator 成功时原子写入固定文本 `validation succeeded\n`；
- 失败时删除旧 result 并返回非零，避免 stale success；
- 扫描结果排序，并把真实 cfg、seccomp、白名单写入 depfile；
- 将 `main()` 拆为 `parse_options()`、`validate_options()`、`run_validation()` 和简短入口，NBNC 从 57 行降到约 16 行。

#### 验证结果

`/srv/workspace/action_incremental_logs_20260820/host_symlink_two_stage` 及同日 validator 日志中：

- 第一轮 validation stage 执行；
- 第二轮只允许稳定输入层按需要执行，两个 validator 不再执行；
- 两个 result 文件 SHA-256 均为 `114251d6c56bfdae1798438d6f5ea440b50d130d77ccda494a351c210b9f06ca`；
- 人工失败 fixture 返回 1，并删除预置的旧成功结果；
- 上游两轮构建约 11 分 20 秒和 8 分 45 秒。

原始 `all_parts_host` 在两轮间可能变化，但规范化后结果稳定。这正是 collector 层允许吸收噪声、leaf 层保持稳定的设计目标。

### 5.13 HiSysEvent：配置与安装信息稳定化

#### 现象和证据

仓库：`build`，提交 `3dc5695a126e2c9b3de9336ad8a290d2b66c8d29`。

目标 `phone_hisysevent_install_info` 在零改动轮次仍执行。两轮比较显示 `hisysevent_configs.json` 和 install info 的语义相同，但被重新写入；脚本读取的 YAML 配置也没有完整进入依赖图。

#### 根因

- loader 和处理脚本无条件覆盖 JSON；
- 目录扫描得到的 YAML 是隐式输入；
- 上游元数据重写把 HiSysEvent 与 NOTICE、`phone_install_modules` 一起带动。

#### 代码思路

- loader 和 hisysevent process 使用 `check_changes=True`；
- JSON 输出排序、规范化；
- 将实际读取的 YAML 写入 depfile；
- 保持真实 YAML 变化能够触发重新生成。

#### 验证结果

`/srv/workspace/action_incremental_logs_20260824/hisysevent_incremental` 中：

- 第一轮约 11 分 36 秒；
- 第二轮约 8 分 20 秒；
- 第二轮 `phone_hisysevent_install_info` 不再出现；
- notice 和 `phone_install_modules` 当时仍执行，说明 HiSysEvent 修复没有掩盖其他链路；
- config、install info、ZIP 和 depfile 的哈希分别稳定为 `4ffdc4d22dd4863be7130b60cdf776f2b59d50bf72b648bf4be4aa0aea626338`、`ae681e50adae1fbcf499ab1a59e045b35408272bfcae7f01186fbeeaf4401994`、`d5e1b7c68335a90cb59d36b1d556ba30e93054a56617688f12d2fa84a0189cf0`、`3552eb5506b4d07e3e61406b2e5d45f2741840d41ba7cb2538786fb1ba3505a5`。

### 5.14 NOTICE：part 元数据稳定化与两阶段发布

#### 现象和迭代证据

仓库：`build`，当前提交 `edc427a875e5c0642e31c7b3dca4f7a8b0219b71`，分支已推送。

修复经历了三组可追溯迭代：

1. `/srv/workspace/action_incremental_logs_20260824/part_metadata_notice`：第二轮 `phone_parts_list`、`collect_notice_files__phone`、`phone_install_modules` 仍执行；
2. `/srv/workspace/action_incremental_logs_20260824/part_metadata_notice_v2`：继续补齐 part metadata 稳定化后，NOTICE 仍被最终 ZIP 的时间关系带动；
3. `/srv/workspace/action_incremental_logs_20260824/notice_two_stage_v3`：引入两阶段 NOTICE 输出后，第二轮 stage、collect 和 merge notice 均消失。

进一步检查发现 NOTICE depfile 已包含约 52184 个直接输入，并且两轮 `UPDATED_COUNT=0`。因此问题不是漏依赖，而是最终 ZIP 内容虽稳定，却保留了较旧 mtime；大量输入比它更新，Ninja 每轮都认为 action dirty。

#### 根因

- part install、dep、host、system install JSON 存在无条件重写；
- NOTICE collector 同时负责大规模扫描和最终 ZIP 发布；
- 内容比较保留了旧 ZIP，但旧 mtime 永远早于输入，形成“内容没变、规则每轮仍 dirty”的时间戳悖论；
- 单纯继续给 collector 加 `restat` 不能解决 action 自己每轮被判 dirty。

#### 代码思路

相关文件：

- `ohos/packages/generate_part_info.py`
- `ohos/packages/BUILD.gn`
- `ohos/packages/parts_install_info.py`
- `scripts/util/file_utils.py`

处理方式：

- part install、dep、host、system install JSON 使用排序和 parsed-JSON 语义比较；
- collector 只生成 `${target_gen_dir}` 下的稳定中间 NOTICE ZIP；
- 增加独立 `copy_ex` leaf target，把中间 ZIP 发布到最终路径；
- collector 依赖大规模直接输入和 depfile，保证真实 NOTICE 来源变化能够触发；
- leaf 只依赖稳定中间 ZIP，中间内容不变时最终产物不被重复发布；
- 中间和最终 ZIP 使用相同内容哈希，避免多阶段引入新的非确定性。

#### 验证结果

`notice_two_stage_v3` 中：

- 第一轮成功，约 11 分 03 秒；
- 第二轮成功，约 8 分 00 秒；
- 第二轮 `collect_notice_files__phone`、NOTICE stage 和 merge 目标均未执行；
- 中间和最终 ZIP SHA-256 均为 `b222f90089319d41a6df93257c1a3ef6d36ff521b13218fcbd77cdee84baddf1`；
- 两轮 inode、mtime、size 保持稳定。

2026-08-25 又在当前提交上做了补充复验，日志已整理到 `/srv/workspace/action_incremental_logs_20260825/notice_repeat`：

- 第一轮成功，约 11 分 15 秒；
- 第二轮成功，约 8 分 13 秒；
- 被测 NOTICE targets 均未出现；
- 第二轮输出状态与 2026-08-24 已验证的稳定产物一致；由于本次未及时保留结构化 `first_outputs.txt`，不把它表述为一组独立的两轮输出属性对比。

HiSysEvent 与 NOTICE 分别在各自修复分支完成了严格两轮验证；当前证据不能替代两项提交叠加后的联合 9/10 级验证。`phone_install_modules` 仍可能由其他安装元数据上游触发，属于下一阶段问题。

## 6. 通用代码设计要点

### 6.1 JSON：比较语义，不比较格式噪声

推荐流程：

```text
读取旧文件 -> 解析 JSON
生成新对象 -> 排序并规范化
比较 Python 对象
  相同：不写文件
  不同：临时文件写入 -> fsync/close -> 原子替换
```

这样可以忽略缩进、键顺序等无意义差异，同时保留真实字段变化。不能用 `str(dict)` 作为稳定哈希来源，也不能依赖目录遍历的自然顺序。

### 6.2 文本与二进制：临时输出后按内容替换

生成脚本不应先截断正式输出。更安全的做法是：

1. 在同一文件系统创建临时文件；
2. 完整生成并关闭临时文件；
3. 比较临时文件和现有正式文件；
4. 相同则删除临时文件；
5. 不同则原子替换正式文件。

同一文件系统上的原子替换可以避免构建中断留下半文件，也能保留稳定输出的 mtime。

### 6.3 ZIP/HAP：内容稳定必须包含元数据稳定

归档可复现至少需要固定：

- entry 排序；
- entry 时间；
- 压缩算法和级别；
- Unix 权限和外部属性；
- 目录 entry 表示；
- 路径分隔符和编码。

只比较解压后的文件内容，不能证明 HAP 字节稳定；签名链路通常依赖归档原始字节，因此必须比较最终 SHA-256。

### 6.4 depfile：解决动态输入，不是稳定输出替代品

depfile 应记录脚本实际读取的配置文件，并满足：

- target 与 GN 声明的输出一致；
- 路径正确转义；
- 输入集合排序、去重；
- 被删除或新增的动态文件可以通过目录索引、manifest 或生成列表反映；
- 动作成功后再发布 depfile。

depfile 解决“真实输入变化能否触发”问题，`check_changes` 解决“等价输出是否重写”问题，两者不能互相替代。

### 6.5 两阶段 action：吸收高扇出动态噪声

适合拆层的条件：

- collector 必须扫描大量动态输入；
- collector 可能因保守依赖而执行；
- 最终语义结果通常不变；
- 最终产物有大量下游消费者。

结构如下：

```text
动态输入集合
  -> collector action + depfile
  -> 稳定中间文件
  -> leaf action/copy
  -> 最终公开产物
  -> 多个下游消费者
```

collector 可以保守，稳定中间文件必须严格；leaf 只对语义变化作出反应。这一模式已用于 host symlink、validator 输入和 NOTICE。

### 6.6 失败语义：不能留下陈旧成功产物

validator 和生成器必须满足：

- 失败返回非零；
- 删除或不发布本轮 result；
- 不覆盖最后一个完整的普通产物，除非该产物本身代表成功状态；
- success marker 内容固定；
- 外部命令使用 `check=True` 或显式检查返回码。

否则增量构建可能因为旧 result 存在而跳过真实失败。

## 7. 修复与证据汇总

| 问题 | 仓库 | 核心修复 | 提交/状态 | 主要证据 |
| --- | --- | --- | --- | --- |
| jsframework action 重跑 | `third_party/jsframework` | 保留稳定输出和 runtime mtime | `869aec84388a`、`d0752be1bbf`；历史正式 `a280a42` | `20260804/final_zero_change_console.log` |
| airscan action 重跑 | `third_party/sane-airscan` | gen 目录补丁 staging、精确输出、幂等 patch | `bb4ab646`、`5ed21a6`、`262f313`；历史正式 `37de4f9` | `20260804/airscan_*` |
| SA profile 重写 | `build` | 排序、JSON 语义比较、稳定 ZIP | 正式 `0d530d7e`，迁移 `c08d319f` | `20260812/sa_validation_*` |
| HAP 签名结果不稳定 | `build` | 独立 sign result、SHA-256、原子写入 | 正式 `34aa8cba`，迁移 `0008197c` | `20260807`、`20260812` |
| HAP 打包字节变化 | `developtools/packing_tool` | 固定 ZIP entry 元数据 | 正式 `dcbbc78`，迁移 `4bcb6aa` | `20260813/hap_packing_probe` |
| compile_app JSON 重写 | `build` | JSON 内容一致不覆盖 | 验证提交 `918e4c5...` | `20260813/compile_app_stable_output` |
| IDL 输出错误 | `build` | 输出命名修正、外部 IDL 仅作输入 | 正式 `4fa37075`，迁移 `e00d6de2` | `20260813`、`20260817` |
| ArkUI stamp 错误 | `foundation/arkui/ace_engine` | 声明真实 stamp、固定绝对路径 | 本地验证状态 | `20260818/arkui_stamp_fix` |
| ets2bundle 动态输入 | `developtools/ace_ets2bundle` | depfile 表达真实依赖 | 基于 PR 7061 的本地验证 | `20260819/ets2bundle_pr7061` |
| `phone_parts_list` 传播 | `build` | 聚合 JSON 稳定写入 | `0c668bfc` | `20260819/phone_parts_stable_output` |
| host symlink 重跑 | `build` | collector + stable intermediate + leaf | `45c3af2f` | `20260820/host_symlink_two_stage` |
| validator 重跑/假成功 | `build` | 稳定输入、真实 result、depfile、失败清理 | `f1a46334` | `20260820` validator 日志 |
| HiSysEvent 重跑 | `build` | JSON 稳定写入、YAML depfile | `3dc5695a` | `20260824/hisysevent_incremental` |
| NOTICE 重跑 | `build` | part metadata 稳定化、NOTICE 两阶段发布 | `edc427a8` | `20260824/notice_two_stage_v3`、`20260825/notice_repeat` |

## 8. 当前结论与未完成项

### 8.1 已经有充分证据支持的结论

- jsframework 与 sane-airscan 的目标级零改动重跑已经消除；
- SA、HAP 签名、HAP 打包、IDL 的核心稳定性修复有独立日志与提交支撑；
- package 聚合元数据稳定后，可以利用 `restat` 阻止大量下游动作；
- host symlink、validator 和 NOTICE 的两阶段结构能有效隔离动态扫描噪声；
- NOTICE 当前提交在 2026-08-24 和 2026-08-25 均完成两轮复验。

### 8.2 仍需继续处理或补证的内容

- `phone_install_modules` 仍可能被其他安装元数据链路带动，需要从第二轮 explain 的第一个 dirty 输入继续向上追；
- HiSysEvent 与 NOTICE 需要在合并后的同一分支执行联合两轮验证；
- ArkUI 和 ace_ets2bundle 当前属于本地验证状态，需要整理干净提交并对齐上游版本；
- 非 rk3568 产品、非空 binary SA、多产品 `part_name_info` 仍需扩大覆盖；
- 2026-08-25 NOTICE 复验缺少第一轮独立 `build.log` 和 `.ninja_log`，后续验证必须逐轮即时备份；
- 全量烟测和单目标增量验证需要分别保存，不能用单目标成功替代整机产品构建成功。

## 9. 后续统一验证流程

### 9.1 构建前记录

```bash
git status --short
git branch --show-current
git rev-parse HEAD
```

对 repo 多仓工程还应记录对应子仓路径与 manifest revision，确保日志能回溯到准确代码。

### 9.2 第一轮和第二轮

构建命令单独执行并使用 `tee` 保存控制台。每一轮结束后立即复制内部日志，不要等第二轮结束再复制：

```bash
cp out/rk3568/build.log "$LOG_DIR/first_build.log"
cp out/rk3568/build_error.log "$LOG_DIR/first_error.log"
cp out/rk3568/.ninja_log "$LOG_DIR/first_ninja.log"
```

第二轮使用对应的 `second_*` 文件名。若命令通过管道连接 `tee`，必须记录构建命令自身的返回值，例如 Bash 中使用 `${PIPESTATUS[0]}`。

### 9.3 离线检查

构建完成后，再单独执行 grep：

```bash
grep -n -E 'ACTION //<target-regex>' "$LOG_DIR/second_console.log" || true
diff -u "$LOG_DIR/first_outputs.txt" "$LOG_DIR/second_outputs.txt" || true
```

该命令只读取已保存日志，不包含任何构建入口，避免误触发第三轮编译。

### 9.4 真实输入变化验证

零改动第二轮通过后，至少选择一个最小真实输入做第三组验证：

- 修改一个被 depfile 记录的 JSON/YAML/cfg；
- 确认目标重新执行；
- 确认输出语义随输入变化；
- 恢复输入后再次构建，确认输出收敛；
- validator 需额外验证失败返回码和旧 result 清理。

只有同时满足“零改动不重跑”和“真实改动能重跑”，才能证明依赖图既不过度也不缺失。

## 10. 修复原则总结

本轮问题的共同点不是 Ninja 本身错误，而是构建规则没有准确表达文件语义：脚本读取了未声明的输入、声明了并未生成的输出、或在内容不变时仍改变输出状态。有效修复必须落在正确责任层：

- 生成器负责确定性和原子输出；
- GN 负责准确声明静态输入、输出和目标关系；
- depfile 负责动态输入；
- collector 负责保守扫描；
- stable intermediate 负责吸收噪声；
- leaf publisher 负责把真正的语义变化传给下游；
- 两轮日志、输出快照和真实输入变更共同构成验证证据。

这套方法可以继续用于 `phone_install_modules` 及后续高扇出 ACTION：先找到第二轮的第一个 dirty 边，再判断属于真实输入、声明错误、无条件重写、非确定性归档还是缺少稳定边界，最后选择对应的最小修复模式。
