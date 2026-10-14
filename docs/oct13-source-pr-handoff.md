# 十项 Action 修复源码、PR 与验证交接（2026-10-13）

## 当前结论与源码版本

**修复代码有更新。** 相对本机保存的“纯迁移版 original”，本轮规范性修复与编译兼容补充共涉及 **10 个仓、23 个修复文件**；按根因准备 **12 组带 DCO 的独立补丁**。主要是 phone_install_modules 上游的 IDL、SDK、JS/CSS 生成链和 ROFS 稳定发布，以及 components.json 生命周期、安装规则输入补齐。

“源码更新”在此指修复文件发生变化。工作源码仍是 10 月 12 日拉取的目录，本次归档没有执行 repo sync、git pull 或切换上游 HEAD。17 个相关仓的 HEAD、真实索引、受控源码内容和 mtime 均保持原样；新签名快照与通过验证的完整 Git 树逐仓一致。本次只保存版本与交接，没有再次修改修复源码或启动编译。

原始十项在最终全量后的首轮、第二轮增量均为 0；后续人工增量日志也保持十项为 0。**组合构建通过与社区 PR 合入是两个独立状态。当前新增 GitCode PR 数量为 0，尚未联系评审人。** 旧 PR 地址和历史 diff 用于溯源，其当前开关、合入与门禁状态本次未联网刷新；不能将历史 open 状态当成当前状态。

源码根目录：

```text
/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code
```

## 验证结果

| 版本与阶段 | 完整耗时 | GN / Ninja | 主 Ninja 任务 | phone_install_modules | 原始十项其余九项 | 退出码 |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 最终 attempt6：空 out 全量 | 2,105.50 秒 | 25.24 / 1967.93 秒 | 125,626 | 1 | 各 1 | 0 |
| 最终 attempt6：首轮增量 | 154.81 秒 | 28.95 / 57.53 秒 | 62 | 0 | 均 0 | 0 |
| 最终 attempt6：第二轮增量 | 87.77 秒 | 22.19 / 25.92 秒 | 13 | 0 | 均 0 | 0 |
| 后续人工增量，日志 UTC 2026-10-14 03:39 | 未捕获 | 未捕获 | 13 | 0 | 均 0 | 未捕获 |

attempt6 三轮任务序列有效，95 个受控路径内容不变，轮间 mtime 不变；最后再次保存的 17 仓 Git 树与该验证版本一致。两轮增量无 CC/CXX 或共享库重链，gen_snapshot、ark_jsf、airscan_action、gen_ui_plugins、gen_sdk_ts_wrapper 均为 0。第二轮剩余 7 个 Action 和 6 个 STAMP，主要为内核检查、ko_sample 和 metadata，不属于原始十项。

全量前清空 out，并移走源码内 arkui-plugins/lib（266 文件）和 koala-wrapper/build（869 文件）；全量后两个源码生成目录没有重建。编译缓存仍然存在，所以“空 out 全量”不等于无 ccache 的冷机器性能测试。完整耗时包括前后处理，不能用 Ninja 耗时代替。

后续人工构建已无运行进程，日志进入 postbuild 统计，无 FAILED 边，连续任务序列为 1–13。终端退出码和命令完整耗时未留存，因此不将上一轮 87.77 秒归给这一轮。原日志及计数已保存：[人工增量汇总](evidence/20261013-source-handoff/manual-build-summary.json)、[压缩日志](evidence/20261013-source-handoff/manual-build.log.gz)。

更完整的验证来源、失败根因和单项回归见 [实际编译验收](oct13-phone-norm-validation.md)。其中 JS 43 项单测、IDL 141 条真实命令/1,560 个输出恢复、ROFS 6 个对象字节与 mtime 回归通过；未宣称 JS lint、设备或 XTS 通过。原始 raw 仓的 666.77 秒增量伴有 airscan 源码自修改，不能与最终稳定轮作严格等条件性能结论。

## 本轮新增修复逐仓说明

### build

**IDL 生成依赖和 clean 后恢复**：IDL 模板补齐 client、callback、common 的具体输出并转发 deps；脚本递归跟踪 import，在 out/gen 临时目录生成，完整校验输出后按内容发布。删除生成文件后可以重建，失败保留原有效产物。

文件：`config/components/idl_tool/idl.gni`、`config/components/idl_tool/idl.py`。

依赖已迁移的 IDL 命名及 common 区分修复（历史 build #6982 和缩写命名准备补丁）；与五个 IDL 消费仓协调合入。

**components.json 稳定发布**：loader 不再先删除 components.json，改用 check_changes 保留相同内容的时间戳；构建参数缓存的消费方式不变。

文件：`hb/services/loader.py`。

依赖迁移版公共 JSON 语义比较；可与安装规则输入修复分别评审。

**安装规则文件依赖补齐**：将 system_arm64e_whitelist.json 和 categorized-libraries.json 加入平台安装动作 sources。规则文件变化会正确触发安装，不再漏依赖。

文件：`ohos/packages/BUILD.gn`。

沿用历史 build #7046、#6999 安装修复；本补丁不替代 ROFS 和 SDK 上游修复。


### third_party/jsframework

**JS 构建目录与 CSS 依赖修复**：普通与独立构建均在 out 使用依赖副本；补齐具体 CSS/配置/测试输入，保留 GN 生成的 CSS 子树以避免同文件复制，分别等待构建和测试并传播失败；补齐 native 测试替身。

文件：`BUILD.gn`、`js_framework_build.sh`、`test/ut/runtime.ts`。

与 css-explicit-copy-outputs 配套；先使 CSS fixture innerkit 可见，再提交消费者。


### developtools/ace_ets2bundle

**SDK 插件和 wrapper 的具体文件生成链**：插件与 wrapper 在 out 内生成，使用受控 JSON 文件清单声明具体 inputs/outputs；按内容发布并补足 package.json 生产者依赖。通过 read_file 兼容 GN exec_script 白名单，工具文件由 depfile 跟踪。

文件：`arkui-plugins/BUILD.gn`、`arkui-plugins/build_ui_plugins.py`、`arkui-plugins/sdk_files.json`、`koala-wrapper/BUILD.gn`、`koala-wrapper/build_ts_wrapper.py`、`koala-wrapper/sdk_files.json`、`sdk_copy.gni`、`sdk_files.py`。

保留原 target、SDK 布局和独立 sysResource.js 生产者；依赖迁移版 libarkts 输出隔离。新增或删除 TS、schema、runtime 文件时刷新并提交 sdk_files.json。


### base/account/os_account

**账户 IDL callback/common 输出补齐**：frameworks_osaccount_interface 显式声明 IDomainAccountCallback.idl 与 DomainAccountIpcData.idl，避免生成文件只作为其他动作的副产物出现。

文件：`frameworks/osaccount/native/BUILD.gn`。

与 build 的 idl-clean-outputs 配套。


### base/inputmethod/imf

**输入法 IDL shared types 输出补齐**：input_client_interface 显式声明 InputMethodClientTypes.idl 的公共输出，使 clean 后生产者与消费者关系完整。

文件：`interfaces/inner_api/inputmethod_controller/BUILD.gn`。

与 build 的 idl-clean-outputs 配套。


### base/security/dlp_permission_service

**DLP IDL shared types 输出补齐**：dlp_permission_interface 显式声明 DlpPermissionTypes.idl 的公共输出，避免 clean 后缺失生成头。

文件：`interfaces/inner_api/dlp_permission/BUILD.gn`。

与 build 的 idl-clean-outputs 配套。


### foundation/ability/dmsfwk

**分布式能力 IDL shared types 输出补齐**：dmsfwk_idl 显式声明 DeviceConnectStatus.idl 的公共输出，避免依赖未声明副产物。

文件：`interfaces/innerkits/common/BUILD.gn`。

与 build 的 idl-clean-outputs 配套。


### foundation/multimedia/audio_framework

**音频 IDL callback 生产者依赖补齐**：audio_service_idl_callback 显式依赖 audio_service_idl_interface，共享类型由明确生产者先生成，避免 clean 后抢跑或重复发布。

文件：`services/audio_service/idl/BUILD.gn`。

与 build 的 idl-clean-outputs 配套。


### third_party/css-what

**CSS 源文件和 fixture 的复制边补齐**：将 CSS 目录复制拆成 9 个具体文件输出；fixture 目标采用 ohos_copy 并登记 innerkit，保留原公开 target 和 runtime/src 布局，修复跨组件生成输入可见性。

文件：`BUILD.gn`、`bundle.json`。

与 js-out-only-build 配套；生产者先于消费者合入。


### foundation/graphic/graphic_3d

**ROFS 对象按内容发布**：CompilerAsset.sh 在构建目录的独立临时目录生成对象，校验实际输出后比较发布。相同内容保留 mtime，缺失文件或目录能恢复，失败保留旧对象，阻断五个库的无效重链及 phone_install_modules 重跑。

文件：`lume/LumeEngine/tools/CompilerAsset.sh`。

保留编译器参数、对象格式、资源内容、插件 UID 与 API/ABI；可独立评审。


## 累计保留的历史修复

下列内容已经存在于本轮开始前的迁移基线，未因本次规范性更新重新修改；重提旧 PR 时仍需核对目标分支是否已经包含。所有具体文件均列入后面的版本清单和累计补丁。

| 仓库 | 保留的文件与作用 | 本轮新增修复 |
| --- | --- | --- |
| build | SA 排序/稳定 JSON/确定化 ZIP；parts、host、hisysevent 安装信息稳定发布；校验动作真实 result/depfile；NOTICE 分阶段发布与依赖修正；modules_install SA 过滤和输出稳定；HAP 签名、JS assets、SDK split、static ABC、preloader、ramdisk 与内核模块发布修复。累计 36 个修复文件，完整列表见 versions.json 的 repair_files。 | 其中 4 文件进一步修改，见上节；其他历史功能继续保留。 |
| developtools/packing_tool | adapter/ohos/Compressor.java：三个 ZIP entry 写入路径使用统一固定时间，避免相同内容的 HAP/ZIP 随时间改变。 | 无 |
| third_party/sane-airscan | BUILD.gn、patch_install.py：在 out/gen/patched 应用当前主干八项补丁，声明具体输入输出并编译生成副本，停止在源码树反复打补丁。 | 无 |
| base/security/selinux_adapter | 保留新主干条件；当前相对该仓上游 HEAD 无补丁。旧仓 SELinux 修复未机械回灌。 | 无，不生成重复 PR |
| device/board/hihope | rk3568/camera/vdi_impl/v4l2/BUILD.gn：相机配置在 gen 生产，去掉向源码复制和 GN 阶段 touch，消费者依赖生产者。 | 无 |
| arkcompiler/ets_frontend | ets2panda/BUILD.gn、driver/build_system/BUILD.gn、scripts/check_build_system_consistency.py：一致性检查声明输入并真正生成 stamp，build_system 输出隔离到子目录，避免复制整个公共 gen。 | 无；4 个 npm 锁文件变化另存，不计修复。 |
| interface/sdk-js | BUILD.gn、process_internal.py、remove_internal.py：base_split 配套 stamp/depfile，声明裁剪工具按内容发布并跟踪依赖，保留新主干参数。 | 无 |
| developtools/ace_ets2bundle | ets1.2/BUILD.gn、ets1.2/libarkts/BUILD.gn：保留 libarkts SDK 输出隔离和消费者复制路径。 | 两文件未再修改；新增的插件/wrapper 8 文件见上节。 |
| third_party/iptables | extensions/genInit.py：生成 initext 文本后比较发布，保留注册顺序，避免 3 个 CC、3 个 AR 和一次 LINK 因 mtime 重跑。 | 无；三个 C 文件头路径差异另存。 |

本次没有完成整个 OpenHarmony 构建系统所有 inputs/outputs 的规范化。Shader、部分 SDK/ETS loader 等历史目录接口仍存在；已修复链路的结果不能外推为所有目录依赖已消除或所有平台已通过。

## 原始十项与 PR 更新判断

| Action | 历史主要 PR | 相对本轮纯迁移基线的更新 | 后续提交判断 |
| --- | --- | --- | --- |
| sa_profile_src_phone | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 原 Action 直接修复未新增 | 旧 PR 未合入才按目标分支重提；不因本轮验证另建重复 PR。 |
| sa_profile_binary_phone | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 本轮未新增；累计版还包含后续补过的 ZIP entry 时间固定 | 若重提 #6965，须携带累计 ZIP 补充，不能只复制旧 PR diff。 |
| phone_sa_profile_install_info | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | 原 Action 直接修复未新增 | 核对旧 PR/主干是否已包含。 |
| check_seccomp_filter_name | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 校验逻辑未新增 | 核对旧 PR/主干是否已包含；同一 BUILD.gn 中新增安装输入不等于此 Action 被重写。 |
| process_field_validate | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 校验逻辑未新增 | 同上，保留 result、depfile 与失败清理。 |
| collect_notice_files__phone | [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009)、[#7048](https://gitcode.com/openharmony/build/merge_requests/7048) | NOTICE 直接修复未新增 | 重提时包含后续 LICENSE 边界和 depfile 修正。 |
| generate_host_symlink | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 原 Action 直接修复未新增 | 保留 collector 与发布阶段分离，不能把 generate_host_info 当成它。 |
| phone_hisysevent_install_info | [build #7006](https://gitcode.com/openharmony/build/merge_requests/7006) | 直接修复未新增 | 核对旧 PR/主干是否已包含。 |
| phone_install_modules | [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046)、[iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) 及 SDK/IDL/签名配套 | 新增两项安装规则输入；上游 IDL、SDK、JS/CSS、ROFS 链路有更新 | 需要提交本轮新增补丁；仅重提 #7046 不足以覆盖本次结果。 |
| phone_parts_list | [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999)、[#7009](https://gitcode.com/openharmony/build/merge_requests/7009) | 直接修复未新增；loader 的 components.json 稳定发布是公共上游补充 | loader 补丁单独评审，旧 parts 修复按合入状态处理。 |

十项详细历史作用与 diff 见 [原始十项交接](original-ten-actions-completion-20260910.md)。本轮新增不能全部归进单个 phone_install_modules PR，也不等于必须新建十个 Action PR。

## 新增 PR 准备清单与合入顺序

下列 12 组已经生成单提交 format-patch 和 PR 说明草稿，覆盖 10 仓、23 文件。build 仓按 IDL、loader、安装规则三个根因拆开；每组均包含真实 DCO trailer。

| 仓库 | 补丁与 PR 草稿 | 准备提交 | 文件数 |
| --- | --- | --- | ---: |
| `build` | [IDL 生成依赖和 clean 后恢复](pr-drafts/20261013/idl-clean-outputs.md) | `9cd1ddecf28a` | 2 |
| `build` | [components.json 稳定发布](pr-drafts/20261013/loader-stable-components.md) | `05906cd0b9db` | 1 |
| `build` | [安装规则文件依赖补齐](pr-drafts/20261013/install-rule-inputs.md) | `c672e7f7dbc8` | 1 |
| `third_party/jsframework` | [JS 构建目录与 CSS 依赖修复](pr-drafts/20261013/js-out-only-build.md) | `2380cf22dd9c` | 3 |
| `developtools/ace_ets2bundle` | [SDK 插件和 wrapper 的具体文件生成链](pr-drafts/20261013/sdk-explicit-file-outputs.md) | `5df2dea2c4e5` | 8 |
| `base/account/os_account` | [账户 IDL callback/common 输出补齐](pr-drafts/20261013/os-account-idl-outputs.md) | `040df4eb6e19` | 1 |
| `base/inputmethod/imf` | [输入法 IDL shared types 输出补齐](pr-drafts/20261013/imf-idl-outputs.md) | `eb9b91efa291` | 1 |
| `base/security/dlp_permission_service` | [DLP IDL shared types 输出补齐](pr-drafts/20261013/dlp-idl-outputs.md) | `6ac6b9f36f97` | 1 |
| `foundation/ability/dmsfwk` | [分布式能力 IDL shared types 输出补齐](pr-drafts/20261013/dms-idl-outputs.md) | `383286735076` | 1 |
| `foundation/multimedia/audio_framework` | [音频 IDL callback 生产者依赖补齐](pr-drafts/20261013/audio-idl-dependency.md) | `975f1696a069` | 1 |
| `third_party/css-what` | [CSS 源文件和 fixture 的复制边补齐](pr-drafts/20261013/css-explicit-copy-outputs.md) | `c8b2823a3bda` | 2 |
| `foundation/graphic/graphic_3d` | [ROFS 对象按内容发布](pr-drafts/20261013/rofs-stable-publication.md) | `faeddc68c9dc` | 1 |

1. 核对旧 PR 的当前状态与目标主干：已合入的改动不重复提交，仍开放的可在原分支更新，关闭且未合入的另开 PR 并关联旧编号。先确认迁移基线依赖是否存在。
2. build IDL 模板与五个业务消费者协调合入，避免只合一端后消费者输出不完整。历史 IDL #6982 与缩写命名修复是本轮补丁的前置上下文。
3. CSS fixture innerkit 生产者先可见，再合 JS 消费者；两个仓配套验证。SDK plugins/wrapper 作为同仓完整生成链提交，保留 sysResource 独立生产者。
4. ROFS、loader 与安装规则输入分别评审。ROFS 稳定发布是本轮去掉首轮五个共享库重链和安装重跑的关键。
5. 完成目标分支移植后执行门禁、clean 恢复及连续无改动增量验证。组合版已编译通过，12 个准备分支没有各自单独整仓编译；排除锁文件差异后的发布组合也需在目标依赖环境核验。

准备分支以本机保存的迁移快照为父提交，**不能直接将该分支整条历史推到上游发 PR**。应在对应仓的目标分支上应用单提交补丁，保留作者和 DCO；有上下文冲突时先核对前置修复，再移植，而不是把累计补丁重复叠加。

```text
Signed-off-by: Smillick <3185479846@qq.com>
```

提交使用 git commit -s；修改既有待发提交时使用 git commit --amend --signoff。DCO 必须在每个提交正文中，仅在 PR 描述里写签名不等同于提交具备 DCO。本次新建的 17 个恢复快照和 12 个准备提交均使用上述身份；旧快照保留原历史，不覆盖或强推。

## 逐仓 Git 版本与恢复文件

列中的文件数为“相对上游 HEAD 的累计修复 / 相对纯迁移版的本轮新增”，不含下节 8 个保留差异。完整 SHA、树 ID、patch 路径和签名见 [versions.json](../patches/20261013-source-handoff/versions.json)。

| 仓库 | 文件数：累计 / 新增 | 上游基线 HEAD | 本次签名快照 | 恢复文件 |
| --- | ---: | --- | --- | --- |
| `build` | 36 / 4 | `a2b72e827add` | `575035a841c7` | [累计修复](../patches/20261013-source-handoff/build/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/build/source.bundle) |
| `developtools/packing_tool` | 1 / 0 | `498ffd5552a0` | `2a6b3330fb42` | [累计修复](../patches/20261013-source-handoff/developtools_packing_tool/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/developtools_packing_tool/source.bundle) |
| `third_party/jsframework` | 3 / 3 | `a21a6f36694c` | `df0243e10f93` | [累计修复](../patches/20261013-source-handoff/third_party_jsframework/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/third_party_jsframework/source.bundle) |
| `third_party/sane-airscan` | 2 / 0 | `23f08604c5e4` | `57b06670b9f6` | [累计修复](../patches/20261013-source-handoff/third_party_sane-airscan/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/third_party_sane-airscan/source.bundle) |
| `base/security/selinux_adapter` | 0 / 0 | `f037bb425e08` | `40e6349f02bb` | 与上游基线无修复差异 · [bundle](../patches/20261013-source-handoff/base_security_selinux_adapter/source.bundle) |
| `device/board/hihope` | 1 / 0 | `5d368fb76592` | `f7c4b8b0a4e5` | [累计修复](../patches/20261013-source-handoff/device_board_hihope/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/device_board_hihope/source.bundle) |
| `arkcompiler/ets_frontend` | 3 / 0 | `c030cb21b282` | `68e6e8881be5` | [累计修复](../patches/20261013-source-handoff/arkcompiler_ets_frontend/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/arkcompiler_ets_frontend/source.bundle) |
| `interface/sdk-js` | 3 / 0 | `126ae62423b0` | `7b297f5537e5` | [累计修复](../patches/20261013-source-handoff/interface_sdk-js/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/interface_sdk-js/source.bundle) |
| `developtools/ace_ets2bundle` | 10 / 8 | `46f944c25ba8` | `f8c82e18a71d` | [累计修复](../patches/20261013-source-handoff/developtools_ace_ets2bundle/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/developtools_ace_ets2bundle/source.bundle) |
| `third_party/iptables` | 1 / 0 | `ee2df27ef936` | `96eaf4296c47` | [累计修复](../patches/20261013-source-handoff/third_party_iptables/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/third_party_iptables/source.bundle) |
| `base/account/os_account` | 1 / 1 | `36cf1be9c73f` | `aa79a094d481` | [累计修复](../patches/20261013-source-handoff/base_account_os_account/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/base_account_os_account/source.bundle) |
| `base/inputmethod/imf` | 1 / 1 | `a87ccd38dd32` | `81ce4832726f` | [累计修复](../patches/20261013-source-handoff/base_inputmethod_imf/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/base_inputmethod_imf/source.bundle) |
| `base/security/dlp_permission_service` | 1 / 1 | `f5a82a3ea9e1` | `8dae586bb6e2` | [累计修复](../patches/20261013-source-handoff/base_security_dlp_permission_service/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/base_security_dlp_permission_service/source.bundle) |
| `foundation/ability/dmsfwk` | 1 / 1 | `aa1b0347b107` | `d7c05d7ece6a` | [累计修复](../patches/20261013-source-handoff/foundation_ability_dmsfwk/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/foundation_ability_dmsfwk/source.bundle) |
| `foundation/multimedia/audio_framework` | 1 / 1 | `d128a212e695` | `1bca688a1452` | [累计修复](../patches/20261013-source-handoff/foundation_multimedia_audio_framework/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/foundation_multimedia_audio_framework/source.bundle) |
| `third_party/css-what` | 2 / 2 | `66c986b35979` | `340729769456` | [累计修复](../patches/20261013-source-handoff/third_party_css-what/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/third_party_css-what/source.bundle) |
| `foundation/graphic/graphic_3d` | 1 / 1 | `14146052f5fc` | `b5ee76d9cb02` | [累计修复](../patches/20261013-source-handoff/foundation_graphic_graphic_3d/cumulative-repairs.patch) · [bundle](../patches/20261013-source-handoff/foundation_graphic_graphic_3d/source.bundle) |

17 仓签名快照引用均为 refs/heads/backup/phone-handoff-20261013-signed；准备提交在各仓 review/*-20261013。每个 source.bundle 均已在对应仓 git bundle verify 通过，包含快照和该仓准备引用，依赖 versions.json 指定的上游基线对象，不是完整仓库镜像。

累计修复 cumulative-repairs.patch 以 base_head 为基线，适合重建整套相关修复；单项 format-patch 以 migration_base 为基线，仅表示本轮新增。两者不能重复叠加。精确恢复验证环境使用 bundle 快照，快照包含下节保留差异；正式 PR 只使用明确拆分的修复范围。

## 保留但不放入新增 PR 的差异

| 仓库 | 文件 |
| --- | --- |
| `third_party/jsframework` | `package-lock.json` |
| `arkcompiler/ets_frontend` | `ets2panda/bindings/package-lock.json`、`ets2panda/driver/interop_toolkits/gluegen/package-lock.json`、`ets2panda/linter/package-lock.json`、`legacy_bin/api8/package-lock.json` |
| `third_party/iptables` | `extensions/libipt_CLUSTERIP.c`、`extensions/libipt_realm.c`、`extensions/libxt_mac.c` |

五个 package-lock.json 包含安装过程中形成或此前保留的 registry/依赖版本差异；三个 iptables C 文件仅为 linux/if_ether.h 到 netinet/if_ether.h 的构建适配差异。它们在已验证工作树中存在，但不属于本次增量修复，未删除，也没有借归档合入修复补丁。逐仓 excluded-worktree.patch 和完整 bundle 均保存这些差异；累计修复和 12 组新补丁已排除。

## 归档与继续编译

GitHub 归档仓：Smillaint/Openharmony-Incremental-Compilation，分支 agent/document-action-incremental-fixes。仓内 patches/20261013-source-handoff 保存 17 仓 bundle、累计修复、12 组带 DCO 补丁及版本 JSON；docs/pr-drafts/20261013 保存逐项 PR 说明。

- 远程：主源码父目录下 phone_norm_validation_20261013/handoff-delivery-20261013。
- 本地完整恢复包：D:\workspace\archives\20261012-migration\handoff-delivery-20261013.tar.gz。
- 恢复包 SHA-256：8358d5252b7afd99327bbf02323257afa82a9989613e6f205fec874eab290852
- [本次源码审计](evidence/20261013-source-handoff/repository-audit.json) 保存仓库差异与来源信息。
- raw 原始对照仓没有改动；没有替换现有产物或重跑构建。

编译参数沿用原指令。当前产物可直接继续增量；需要做重新构建实验时，先保存状态、确认无构建进程，再单独清理明确的编译产物，清理完成后运行编译。

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code &&
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```
