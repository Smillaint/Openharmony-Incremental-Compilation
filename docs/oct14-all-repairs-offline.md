# 本轮全部修复的本地源码（2026-10-14）

本轮关联的 **17 个仓已恢复为独立本地 Git 仓**，累计 **68 个修复文件**，其中相对纯迁移版新增修改 **23 个文件、涉及 10 仓**；另有 **8 个锁文件及兼容差异**保留在组合验证快照中，未混入 GitCode 发布分支。

源码目录：

```text
D:\workspace\repositories\openharmony-repairs-20261014
```

17 仓的 HEAD、Git 树与归档的签名组合验证快照逐仓一致，68 个修复文件及 8 个保留差异均完成内容校验。工作树干净，对象连接检查通过，无 alternates 或远程目录依赖。保留 52,924 个受控文件的 Git 内容；音频和图形仓的 229 个 LFS 资源已下载并核对 SHA-256。

这轮只恢复源码和整理交接，没有修改修复逻辑或重新编译。远程编译机连接超时后，通过 GitCode 上游取得精确基线，再导入已有本地 bundle。

## 分支与使用范围

- 各仓默认分支 `snapshot/validated-20261013`：组合编译通过的完整签名快照，包含上述 8 个另行记录的差异。
- 已发布的 10 仓另有 `fix/incremental-build-20261013`：与 10 月 14 日 GitCode 发布记录对应，便于准备和更新 PR。
- build 另有 `review/sa-profile-pr6965-20261014`，HEAD 为 `f15f9bded74ae12a75b8a9ef729c1397a7202ec2`：本次更新后的 SA 组旧 PR #6965。
- `baseline/source-20261012` 保存各仓上游基线，可在仓内运行 `git diff baseline/source-20261012..snapshot/validated-20261013` 查看累计差异。
- 历史 `review/*` 分支按原归档保留；部分仓同时保留纯迁移快照。基线以前的历史使用浅克隆，不代表完整提交历史。

后续代码审查、修复和整理 PR 可直接使用这些本地仓。完整产品编译仍需 OpenHarmony 其余项目、Linux 环境、工具链和构建依赖；本目录没有复制全部 525 个项目、prebuilts 或 out。

## Windows 文件系统处理

`arkcompiler/ets_frontend` 两个历史测试目录的 12 个文件，及 `third_party/iptables` 中与另一文件仅大小写不同的 38 个路径，未在 Windows 工作树同时展开。它们的原始路径和内容完整保留在本地 Git 对象中，排除清单记录在各仓 `.git/windows-excluded-paths.json` 和总清单里。**本轮 68 个修复文件和 8 个保留差异均不在排除范围内，已经展开。**

这两个仓使用稀疏检出；在 Windows 上不要直接关闭稀疏检出。需要完整 Linux 文件布局时，可在相应仓运行 `git archive --format=tar -o ../source-linux.tar snapshot/validated-20261013`，将归档放到 Linux 文件系统解压。LFS 文件仅存在于音频和图形仓，已另行下载。

## 逐仓位置与版本

下表路径均相对于上述源码目录；完整提交 SHA、文件清单、上游地址、发布分支和校验结果见 `offline-sources.json`。

| 仓目录 | 累计修复文件 | 本轮新增修改文件 | 组合快照 | 主要作用 |
| --- | ---: | ---: | --- | --- |
| `arkcompiler/ets_frontend` | 3 | 0 | `68e6e8881be5` | 检查输出 stamp、依赖声明与 build_system 输出隔离 |
| `base/account/os_account` | 1 | 1 | `aa79a094d481` | 账户 IDL callback/common 输出补齐 |
| `base/inputmethod/imf` | 1 | 1 | `81ce4832726f` | 输入法 IDL 公共类型输出补齐 |
| `base/security/dlp_permission_service` | 1 | 1 | `8dae586bb6e2` | DLP IDL 公共类型输出补齐 |
| `base/security/selinux_adapter` | 0 | 0 | `40e6349f02bb` | 保留当前主干兼容版本；当前无相对上游修复差异 |
| `build` | 36 | 4 | `575035a841c7` | SA、安装与校验、NOTICE、IDL、components.json、安装规则输入及公共稳定发布 |
| `developtools/ace_ets2bundle` | 10 | 8 | `f8c82e18a71d` | libarkts 输出隔离、插件与 wrapper 具体文件生成链 |
| `developtools/packing_tool` | 1 | 0 | `2a6b3330fb42` | 固定 HAP/ZIP entry 时间戳 |
| `device/board/hihope` | 1 | 0 | `f7c4b8b0a4e5` | 相机配置在 gen 生成并明确依赖 |
| `foundation/ability/dmsfwk` | 1 | 1 | `d7c05d7ece6a` | 分布式能力 IDL 公共类型输出补齐 |
| `foundation/graphic/graphic_3d` | 1 | 1 | `b5ee76d9cb02` | ROFS 对象按内容发布，阻断无效重链 |
| `foundation/multimedia/audio_framework` | 1 | 1 | `1bca688a1452` | 音频 IDL callback 的生产者依赖补齐 |
| `interface/sdk-js` | 3 | 0 | `7b297f5537e5` | base_split stamp/depfile 和声明裁剪稳定发布 |
| `third_party/css-what` | 2 | 2 | `340729769456` | CSS/fixture 具体复制输出与 innerkit 可见性 |
| `third_party/iptables` | 1 | 0 | `96eaf4296c47` | genInit.py 内容相同时保留输出时间戳 |
| `third_party/jsframework` | 3 | 3 | `df0243e10f93` | JS 在 out 构建，补齐 CSS 依赖和测试替身 |
| `third_party/sane-airscan` | 2 | 0 | `57b06670b9f6` | 在 out/gen 应用补丁，停止反复改写源码 |

## 修复文件清单


### arkcompiler/ets_frontend

- `ets2panda/BUILD.gn`
- `ets2panda/driver/build_system/BUILD.gn`
- `ets2panda/scripts/check_build_system_consistency.py`

单独保留、未纳入发布分支：

- `ets2panda/bindings/package-lock.json`
- `ets2panda/driver/interop_toolkits/gluegen/package-lock.json`
- `ets2panda/linter/package-lock.json`
- `legacy_bin/api8/package-lock.json`

### base/account/os_account

- `frameworks/osaccount/native/BUILD.gn`（本轮进一步修改）

### base/inputmethod/imf

- `interfaces/inner_api/inputmethod_controller/BUILD.gn`（本轮进一步修改）

### base/security/dlp_permission_service

- `interfaces/inner_api/dlp_permission/BUILD.gn`（本轮进一步修改）

### base/security/selinux_adapter

当前基线无修复差异，保留源码版本用于兼容核对。

### build

- `config/components/ets_frontend/generate_static_abc.py`
- `config/components/idl_tool/idl.gni`（本轮进一步修改）
- `config/components/idl_tool/idl.py`（本轮进一步修改）
- `hb/services/loader.py`（本轮进一步修改）
- `hb/util/io_util.py`
- `hb/util/loader/load_ohos_build.py`
- `lite/config/component/lite_component.gni`
- `ohos/app/app_internal.gni`
- `ohos/common/BUILD.gn`
- `ohos/common/binary_install_info.py`
- `ohos/common/generate_host_info.py`
- `ohos/common/merge_all_subsystem.py`
- `ohos/generate_part_info.py`
- `ohos/hisysevent/hisysevent_process.py`
- `ohos/images/BUILD.gn`
- `ohos/images/build_image.py`
- `ohos/notice/collect_module_notice_file.py`
- `ohos/notice/collect_system_notice_files.py`
- `ohos/packages/BUILD.gn`（本轮进一步修改）
- `ohos/packages/check_seccomp_library_name.py`
- `ohos/packages/generate_host_symlink.py`
- `ohos/packages/modules_install.py`
- `ohos/packages/parts_install_info.py`
- `ohos/packages/process_field_validate.py`
- `ohos/packages/stabilize_json_file.py`
- `ohos/sa_profile/sa_profile_binary.py`
- `ohos/sa_profile/sa_profile_merge.py`
- `ohos/sa_profile/sa_profile_source.py`
- `ohos/sa_profile/src_sa_profile_process.py`
- `ohos/sdk/parse_interface_sdk.py`
- `scripts/app_sign.py`
- `scripts/build_js_assets.py`
- `scripts/compile_app.py`
- `scripts/util/build_utils.py`
- `scripts/util/file_utils.py`
- `templates/kernel/linux-6.6/make_ko.sh`

### developtools/ace_ets2bundle

- `arkui-plugins/BUILD.gn`（本轮进一步修改）
- `arkui-plugins/build_ui_plugins.py`（本轮进一步修改）
- `arkui-plugins/sdk_files.json`（本轮进一步修改）
- `ets1.2/BUILD.gn`
- `ets1.2/libarkts/BUILD.gn`
- `koala-wrapper/BUILD.gn`（本轮进一步修改）
- `koala-wrapper/build_ts_wrapper.py`（本轮进一步修改）
- `koala-wrapper/sdk_files.json`（本轮进一步修改）
- `sdk_copy.gni`（本轮进一步修改）
- `sdk_files.py`（本轮进一步修改）

### developtools/packing_tool

- `adapter/ohos/Compressor.java`

### device/board/hihope

- `rk3568/camera/vdi_impl/v4l2/BUILD.gn`

### foundation/ability/dmsfwk

- `interfaces/innerkits/common/BUILD.gn`（本轮进一步修改）

### foundation/graphic/graphic_3d

- `lume/LumeEngine/tools/CompilerAsset.sh`（本轮进一步修改）

### foundation/multimedia/audio_framework

- `services/audio_service/idl/BUILD.gn`（本轮进一步修改）

### interface/sdk-js

- `BUILD.gn`
- `process_internal.py`
- `remove_internal.py`

### third_party/css-what

- `BUILD.gn`（本轮进一步修改）
- `bundle.json`（本轮进一步修改）

### third_party/iptables

- `extensions/genInit.py`

单独保留、未纳入发布分支：

- `extensions/libipt_CLUSTERIP.c`
- `extensions/libipt_realm.c`
- `extensions/libxt_mac.c`

### third_party/jsframework

- `BUILD.gn`（本轮进一步修改）
- `js_framework_build.sh`（本轮进一步修改）
- `test/ut/runtime.ts`（本轮进一步修改）

单独保留、未纳入发布分支：

- `package-lock.json`

### third_party/sane-airscan

- `BUILD.gn`
- `patch_install.py`

## 关联资料

- [完整版本与校验清单](evidence/20261014-offline-sources/offline-sources.json)
- [逐仓修复作用及实际编译验证](oct13-source-pr-handoff.md)
- [10 个 GitCode 仓发布记录](oct14-gitcode-publish.md)
- [SA 组旧 PR #6965 更新](oct14-sa-profile-group-update.md)

原有源码目录和未提交修改未覆盖；上述本地源码目录是单独恢复的工作副本。GitHub 保存交接、版本清单和此前的补丁/bundle，不上传这 17 个完整检出目录及 LFS 素材。
