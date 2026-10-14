# phone_install_modules 历史复核与 clean 恢复修复

> 最新逐仓源码、DCO 补丁、恢复版本与 PR 更新判断见 [2026-10-13 源码交接](oct13-source-pr-handoff.md)。本文保留对应阶段记录；最终空 out 全量及连续两轮增量已经通过，不能将历史“尚未编译”状态当作当前结论。

> 该规范版本的后续人工构建在 GN 阶段失败。已完成 [SDK 文件清单的 GN 兼容修复](oct13-gn-sdk-manifest-repair.md)，当前重试使用该文档的一行指令；下列静态结果不能视为产品编译通过。

## 当前结论

远程 10 月 12 日源码中的已知历史修复未发现漏迁。复核覆盖 15 组历史准备补丁，以及与原始十项和安装上游有关的 11 个正式 PR diff。随后在远程应用规范性修改，共 **9 个仓库、18 个文件**。

**本轮没有执行 build.sh、GN gen、真实 Ninja、npm 编译或真实 IDL 生成。** Python/GN/shell 静态检查、模拟生成器回归和已有产物清单对照通过。当前工作树尚待人工编译，不能把上一阶段的编译成功或 169.92 秒增量耗时归到本轮代码。

源码位置：

```text
/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code
```

纯迁移基线的编译、首轮增量及 dry-run 证据见 [迁移验收](oct13-migration-only-validation.md)。其中 `phone_install_modules` 在首轮增量执行一次；该轮存在真实共享库重新链接，不能只凭安装动作出现在日志中认定自身修复失效。

## 历史修复核对

依据 [原始十项交接](original-ten-actions-completion-20260910.md)、[8 月最终交接](glm52-phone-install-final-handoff-20260828.md)、[iptables 交接](glm52-geninit-fix-handoff-20260901.md) 及归档 diff 核对，不以旧 PR 的开关状态推断代码是否存在。本轮没有重新查询 GitCode 在线状态。

| 链路 | 历史依据 | 新仓核对结果 |
| --- | --- | --- |
| 安装元数据、SA depfile | build #7046、#6999 | SA 过滤采用赋值而非 extend；安装 JSON、模块列表稳定写入及空 arm64e 列表输出仍在 |
| SA、parts、host、字段校验 | build #6965、#6999、#7009 | 稳定输出、排序和校验依赖仍在；SA ZIP 还保留了后补的固定 entry 时间戳 |
| hisysevent | build #7006 | JSON 比较写入及 YAML depfile 保留 |
| NOTICE | build #7009、#7048 | LICENSE 边界查找和汇总 depfile 收窄保留 |
| HAP/HSP 签名 | build #6974 | 每 target 的 sign_result.json、路径排序、SHA-256 和原子发布保留 |
| HAP ZIP | packing_tool #1556 | 统一 ZIP entry 时间设置在相关 Java 写入路径中保留 |
| IDL | build #6982、缩写命名准备补丁 | 本地/外部 common 区分、双 i 和缩写命名修复保留 |
| SDK base_split | build #7049、interface/sdk-js 准备补丁 | 脚本支持与调用方 stamp/depfile 配套均存在，保留新主干额外参数 |
| SDK 声明 | interface/sdk-js 准备补丁 | process_internal/remove_internal 的稳定输出与依赖保留 |
| ArkGuard/TypeScript/Declgen 安装 | 历史安装 depfile 补丁 | 已在新仓基线中，不需要再次迁移 |
| libarkts 与 ets2panda | 输出隔离及一致性检查准备补丁 | SDK 隔离发布路径保留；bridges 的依赖采用新主干具体文件 depfile，没有回灌旧目录 inputs |
| JS assets、static ABC、preloader | 对应三组准备补丁 | 空依赖处理、配置复制和内容感知写入存在 |
| iptables | iptables #62 | genInit 内容比较写入存在，注册顺序未改 |

15 组准备补丁中 10 组可以直接反向匹配；5 组结合上下文复核。11 个正式 PR 中 8 个可以直接反向匹配；#6965/#6999 的差异是 SA ZIP 固定时间戳的进一步修复，#7049 的差异是主干参数扩展。原始机器检查结果见 [证据目录](evidence/20261013-phone-clean-recovery/README.md)。不能反向匹配不等于漏迁。

## 本轮修改

| 仓库与文件 | 修改和作用 |
| --- | --- |
| build：config/components/idl_tool/idl.gni、idl.py | 声明 client header，传递显式 deps；使用具体 IDL 文件和递归 import depfile；在 out/gen 临时目录生成，验证完整声明集合后只发布已声明文件；内容相同不覆盖，生成失败保留旧产物 |
| os_account、imf、dlp_permission_service、dmsfwk 的相关 BUILD.gn | 补齐实际生成的 callback/common 文件声明，避免单靠其他动作的副产物才能编译 |
| audio_framework：services/audio_service/idl/BUILD.gn | callback 显式依赖 interface 的共享类型生产者，避免 clean 后抢跑和同一输出被重复发布 |
| build：hb/services/loader.py | 删除 components.json 的先删后写行为，启用 check_changes；一次性参数缓存的消费语义保持原样 |
| jsframework：BUILD.gn、js_framework_build.sh | 补充配置/测试输入；独立构建只清理 out 内副本；npm fallback 在 out 安装；分别等待构建与测试并传播失败；移除 CSS 目录时间戳修补 |
| jsframework：test/ut/runtime.ts | 为新主干依赖的 native compileAndRunBundle 补测试替身并恢复全局状态，不删除断言或吞掉失败 |
| css-what：BUILD.gn | 将目录复制拆为 9 个具体文件的复制边，保留 runtime/src 布局、公开 innerkit 名称及部件信息 |
| ace_ets2bundle：arkui-plugins/BUILD.gn、build_ui_plugins.py | 枚举输入和输出文件，Babel 输出移到 out 临时目录，复制 components/schema/runtime 依赖后按内容发布 |
| ace_ets2bundle：koala-wrapper/BUILD.gn、build_ts_wrapper.py | Babel、声明文件和 tsbuildinfo 均写到 out；native 产物只发布到 out，并作为明确输入；取消复制回源码树 |
| ace_ets2bundle：sdk_files.py、sdk_copy.gni | 公共文件清单与复制实现；保留公开 target 和 SDK 目录布局；复制具体文件，排除 gen 目录中的 depfile；缺文件可重做，删除过期产物限定为上次记录的文件 |

插件生成的 1,071 个文件、wrapper 生成的 534 个文件，与纯迁移完整编译的现存产物清单一致；插件的 sysResource.js 继续由独立 target 生产。复制到 SDK 时显式加入该文件，不再复制整个 gen 目录。

原方案在 GN 阶段动态枚举文件，被调用白名单禁止；后续改为版本管理的具体文件清单。新增/删除 TS 或运行时包文件后，按 [清单维护步骤](oct13-gn-sdk-manifest-repair.md) 刷新并提交配置，再执行原 build.sh 指令。后续改变 Babel 忽略规则时需同步维护清单规则。

已读 build、ace_ets2bundle 及相关业务仓 AGENTS、构建 GN/脚本、依赖说明和交接。修改遵守公开 target、部件信息、工具链与 external_deps 的既有约定；不更改 IDL 协议、AST 插件顺序或业务接口，不增加 npm 依赖。

本轮范围是上述生成链，**不是整个 OpenHarmony 构建系统的规范性验收**。新主干 `ets1.2/libarkts` 的 npm/source-tree 生成方式、根 ETS loader 的 node_modules 安装与部分 SDK 目录接口仍存在，本轮保留其兼容实现；需要单独梳理完整生产者和消费者后继续迁移。Rust IDL、macOS、Windows SDK 和真实 clean 后整仓构建尚未验证。

## 静态与隔离检查

- UTF-8 读取、修改 Python 的内存 compile、GN format 解析、bash -n、git diff --check 均通过。GN 解析不能替代 GN gen 的依赖图检查。
- SDK 文件清单：所有列出的输入都是存在的文件，输出与旧产物集合一致。
- 发布器：同内容保持 mtime、缺失文件恢复、缺少声明输出时不覆盖旧文件、删除过期文件及越界路径拒绝通过。
- 模拟 IDL：递归 import、只发布声明输出、部分/全部 clean 后恢复、mtime 保持和失败保留旧文件通过。
- 模拟 SDK 生成器：out 路径约束、tsbuildinfo 路径、缺失恢复及失败保留旧文件通过。
- 模拟 JS：普通/独立 × prebuilts/npm fallback 四组合均通过；构建失败与测试失败都返回非零。
- JSON：语义相同保留时间戳，删除输出后可恢复。

所有生成器回归使用临时目录或替身，没有调用真实编译器。

## Git 与补丁恢复位置

每个修改仓均先保存版本，再编辑；原 HEAD 与真实索引未切换。

- 修改前分支：`backup/before-phone-clean-recovery-20261013`。
- 修改后分支：`fix/phone-clean-recovery-20261013`。
- 远程归档：`/srv/workspace/patch_backups/20261013_phone_norm/`。
- [9 仓补丁与精确版本](../patches/20261013-phone-clean-recovery/versions.json)。repair.patch 的基线是本轮修改前快照，不能直接套到未迁移的上游 HEAD。
- 各仓 before.bundle、after.bundle 均通过 git bundle verify。
- 本地完整恢复包：`D:\workspace\archives\20261012-migration\20261013-phone-norm.tar.gz`。
- 恢复包 SHA-256：`095a8d4180c4d7d9bb8f61398dac064ebe7cc7f3d53e52ab11b9317353036e84`。

这些是本轮工作版本及归档补丁，尚未创建新的 GitCode PR。

## 人工编译与增量复测

构建行沿用原交接指令：

```bash
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```

第一次先清理当前产品产物。清理与编译分开执行，不清源码或 prebuilts；运行前确保没有其他任务正在使用该产品输出目录。日志另存到 out 外面。

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code || exit 1
log_dir="/srv/workspace/action_incremental_logs_20261013/phone_norm_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$log_dir"
printf '%s\n' "$log_dir" > /srv/workspace/patch_backups/20261013_phone_norm/manual-log-dir.txt
rm -rf -- out/rk3568
```

随后第一轮编译并保存 Ninja explain 日志：

```bash
set -o pipefail
start_time=$(date +%s)
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain 2>&1 | tee "$log_dir/first.console.log"
build_status=${PIPESTATUS[0]}
printf 'exit=%s\nwall_seconds=%s\n' "$build_status" "$(( $(date +%s) - start_time ))" | tee "$log_dir/first.status.txt"
if [ -f out/rk3568/build.log ]; then cp out/rk3568/build.log "$log_dir/first.build.log"; fi
```

仅在第一轮 exit=0 后继续。保持源码和参数不变，第二轮不清理：

```bash
start_time=$(date +%s)
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain 2>&1 | tee "$log_dir/incremental.console.log"
build_status=${PIPESTATUS[0]}
printf 'exit=%s\nwall_seconds=%s\n' "$build_status" "$(( $(date +%s) - start_time ))" | tee "$log_dir/incremental.status.txt"
if [ -f out/rk3568/build.log ]; then cp out/rk3568/build.log "$log_dir/incremental.build.log"; fi
```

检查第二轮时沿最早 dirty 原因区分真实输入变化、输出缺失和目录时间戳；关注原始十项、IDL、gen_snapshot、ark_jsf、gen_ui_plugins、gen_sdk_ts_wrapper 以及相关共享库链接。源码 clean 测试应针对明确生成文件，不运行整仓 git clean -fdx。
