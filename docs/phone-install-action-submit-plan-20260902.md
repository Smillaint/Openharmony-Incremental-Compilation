# phone_install_modules 修复提交拆分（2026-09-02）

## 当前结果

- 除已推送的 iptables 提交外，生成 13 个独立分支和 DCO 提交：11 个优先批次、2 个后续批次。
- 每个分支只包含一个提交，直接基于对应仓库本次读取的官方 master，不包含原验证分支的其他历史提交。
- 优先批次的自动推送因缺少非交互凭据失败；本批分支尚未确认上传。手动脚本会核对目标 fork、提交 SHA、已有远端分支，并逐仓原子推送。
- 原远程编译工作树未修改；四仓 HEAD、暂存区、完整 diff 与已有修改哈希均与拆分前备份一致。未执行编译、GN gen 或真实 Ninja。

## 最直接相关的提交

`build:fix-phone-install-sa-depfile` 直接修改 phone_install_modules 所执行的 `ohos/packages/modules_install.py`：将错误的列表追加改为实际过滤，移除应排除的 SA 文件依赖，而不是再次追加未排除列表。

其余优先提交分别修复上游 Action 的输出声明、depfile、元数据输出或输出目录边界；不应把它们全部写成 phone_install_modules 自身代码修复。

## 优先上传：11 个独立提交

| 仓库 | 分支 | 提交 | 范围 |
|---|---|---|---|
| build | fix-phone-install-sa-depfile | 758a3e94 | modules_install.py：SA depfile 过滤 |
| build | fix-sdk-split-incremental-deps | 72115384 | parse_interface_sdk.py：stamp/depfile 支持 |
| build | fix-binary-install-incremental-metadata | 30db1d9a | binary_install_info.py：稳定输出和可选输入 |
| build | fix-notice-boundary-license | 40bf195f | collect_module_notice_file.py：搜索源码边界目录的 LICENSE |
| build | fix-notice-aggregate-depfile | 7bb01ddc | collect_system_notice_files.py：移除生成 NOTICE 文件的重复依赖 |
| build | fix-js-assets-incremental-deps | f03aa33b | build_js_assets.py：空资源输出依赖及 loader 临时缓存过滤 |
| build | fix-idl-acronym-header-outputs | 97c0d5bc | idl.gni：连续大写缩写接口头输出声明 |
| interface_sdk-js | fix-interface-sdk-split-depfile | 680b35e0 | BUILD.gn：ohos_base_split 调用参数和 depfile |
| interface_sdk-js | fix-sdk-declaration-incremental-deps | df667b6d | BUILD.gn、process_internal.py、remove_internal.py：声明与内部接口生成依赖 |
| arkcompiler_ets_frontend | fix-build-system-output-isolation | 5eb9bc67 | driver/build_system/BUILD.gn：隔离生成物和元数据目录 |
| developtools_ace_ets2bundle | fix-libarkts-sdk-incremental-deps | 8a4c58bc | ets1.2 的两份 BUILD.gn：SDK 输出目录隔离与输入范围 |

SDK split 两仓配套顺序：先合入 build 的脚本支持，再合入 interface_sdk-js 的调用参数，或协调同时评审。两仓分支同名，但各自是独立提交；不能只合入调用方。

## 后续批次：2 个提交，默认不上传

| 仓库 | 分支 | 提交 | 原因 |
|---|---|---|---|
| build | fix-preloader-content-aware-output | 07a42d2c | hb/services/loader.py、hb/util/io_util.py；预加载输出稳定，属于上游输入生成层 |
| build | fix-static-abc-config-copy | 00c502f7 | generate_static_abc.py；消除源配置写回副作用，改动较大，单独评审 |

## 不重复提交及暂缓项

- ArkGuard/TypeScript/Declgen 安装 depfile：官方 ace_ets2bundle master `f7a2b2b5ed478ad876f467e7d2213173339e9d4b` 已包含等价修复。安装 Action 块文本相同，安装脚本完整 Python AST 相同，不重复创建分支。
- ets2panda 一致性检查：旧补丁无法原样应用到最新脚本；暂缓 `fix-ets2panda-consistency-output`，没有生成半套 GN/脚本提交。后续需适配上游再审查。
- `lite/config/component/lite_component.gni`、`ohos/images/build_image.py`：留在原工作树和完整备份中，暂不混入本批待上传分支，需单独核对验证边界。
- package-lock.json、node_modules、其他工作树修改、日志、临时脚本和构建产物不纳入提交。
- iptables 的 `5b884558` 已推送，此处不重复上传。

## Fork 与手动上传

build 的个人 fork 已存在。以下三个同名个人 fork 在最后检查时返回项目不存在/403；若已使用不同名称创建，需要先更正发布仓库的 origin。

- https://gitcode.com/openharmony/interface_sdk-js
- https://gitcode.com/openharmony/arkcompiler_ets_frontend
- https://gitcode.com/openharmony/developtools_ace_ets2bundle

在本机 PowerShell 执行。脚本将 PAT 交给 Git 的交互提示，不把令牌写入脚本、URL、环境变量或凭据缓存。

只先上传最直接的 phone_install_modules 修复：

```powershell
& 'D:\workspace\phone-install-publish-20260902\push-action-fixes.ps1' -Repository build -Branch fix-phone-install-sa-depfile
```

上传 build 仓全部 7 个优先分支：

```powershell
& 'D:\workspace\phone-install-publish-20260902\push-action-fixes.ps1' -Repository build
```

三个 fork 建好后，上传全部优先分支；已经上传且 SHA 一致的分支自动跳过：

```powershell
& 'D:\workspace\phone-install-publish-20260902\push-action-fixes.ps1'
```

后续明确需要上传第二批时：

```powershell
& 'D:\workspace\phone-install-publish-20260902\push-action-fixes.ps1' -Repository build -Priority Later
```

Git 提示 Password 时填写 GitCode PAT，不是账号密码。每仓单独认证，最多四次。脚本不推 master、不强推、不删除远端分支、不编译、不创建 PR；远端已有不同 SHA 的同名分支时停止该操作。

## 验证口径与留档

- 提交均经 UTF-8、Python AST、git diff --check、DCO、单提交/单范围检查。
- 13 个已生成提交的 stable patch-id 与导出的原始候选补丁一致；没有在拆分过程中添加修复逻辑。
- 新分支基于最新官方 master，而两轮整仓成功来自此前组合工作树。尚未对这些独立分支重新编译，不能将旧日志表述为最新独立分支已通过门禁或整仓验证。
- 官方基线：build `42586a0f31139f5db2323ae702ed07a4674c31e1`；interface_sdk-js `b94c97d4032fba32808e194bc0723a1da409decf`；arkcompiler_ets_frontend `3d1832508bc3382bec3912178abd14530af78ab1`；developtools_ace_ets2bundle `f7a2b2b5ed478ad876f467e7d2213173339e9d4b`。
- 完整提交 SHA、文件清单及状态：`D:/workspace/phone-install-publish-20260902/publish-manifest.json`。
- 发布裸仓库：`D:/workspace/phone-install-publish-20260902/<repo>.git`。仅用于对象与分支管理，不是编译目录。
- 原始备份：`/srv/workspace/patch_backups/20260902_publish_split/snapshot-852i_798/`。
