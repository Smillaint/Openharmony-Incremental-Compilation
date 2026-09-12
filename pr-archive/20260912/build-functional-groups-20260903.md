# build 功能分组发布（2026-09-03）

本文件取代旧计划中 build 优先批次的七分支方案和整体单分支方案。其他仓库、已有历史 PR、build 的两个 P1 分支不变。

## 五个独立 PR 分支

共同基线：`42586a0f31139f5db2323ae702ed07a4674c31e1`，沿用本批已准备的官方基线，没有重新更新上游。

| 功能 | 分支 | HEAD | 提交数 |
|---|---|---|---|
| 安装依赖与元数据 | fix-install-incremental-metadata | 5be8fa471e23084eb4a884653746a55af554e7f2 | 2 |
| NOTICE 生成 | fix-notice-incremental-deps | 6840a0ba024b40ca67d0ab26aceee2a3458e7dbd | 2 |
| SDK 接口拆分 | fix-sdk-split-incremental-deps | 72115384f783e09832216c951e7743b944fd5893 | 1 |
| JS 资源构建 | fix-js-assets-incremental-deps | f03aa33b3f4d63c7fc754262a5e5de6a9adb5b66 | 1 |
| IDL 输出声明 | fix-idl-acronym-header-outputs | 97c0d5bcab3e5038ea31aac07523a8cc1bd7e23c | 1 |

五个分支各自基于共同基线，不互相堆叠。SDK、JS、IDL 三个已有分支原样保留。SDK 脚本支持需先于 interface_sdk-js 调用方合入，或协调两仓评审。

## 本地状态与远端迁移

本地已删除四个被替代的细分分支和临时整体分支：

- fix-phone-install-sa-depfile
- fix-binary-install-incremental-metadata
- fix-notice-boundary-license
- fix-notice-aggregate-depfile
- fix-phone-install-incremental-actions

旧分支全部包含在 `regroup-backup-20260903/build-before-regroup.bundle` 中，bundle 已验证为完整历史，可通过 git fetch bundle 恢复。旧发布清单及脚本另存于该目录的 Git 快照 `695a978`。

最后一次只读检查：远端已有 SDK、JS、IDL 三分支和待删除的四个细分分支，没有临时整体分支。官方 build 的 70 个开启 PR、个人 build 的 0 个开启 PR 中，没有关联上述待删除分支的 PR。远端写入尚待终端 PAT 认证。

```powershell
& 'D:\workspace\phone-install-publish-20260902\publish-build-groups.ps1'
```

脚本先验证五类分支、备份、远端 SHA 和开启 PR，再以一次原子 push 创建缺少的新分支、删除仍存在的旧分支。创建只允许远端分支不存在，删除只允许匹配已知旧 SHA；每个变动都带精确 lease，不改 master、不覆盖其他提交。认证或原子推送失败时不执行单独删除。Password 填 GitCode PAT。

只读检查：追加 `-CheckOnly`。同名远端分支已更新、旧分支有关联 PR、备份缺失、API 失败时均停止。

原 `push-action-fixes.ps1` 已通过新清单改为发布五类分支，不会重新创建已淘汰的细分分支；但它不删除旧远端分支，首次迁移应执行上述专用脚本。不要重新执行旧版 `.tmp_prepare_action_publish.py` 或 `.tmp_verify_action_publish.py` 覆盖分组清单。

## 验证范围

- 五组总计七个原修复；每组文件集合精确匹配，文件 Git blob 与原提交一致，逐提交 stable patch-id 一致，DCO 保留。
- `git diff --check` 通过；没有更改产品修复逻辑。
- 原上传脚本九项离线测试、分组迁移脚本八项离线测试，均在 Windows PowerShell 5.1 和 PowerShell 7 通过。
- 分组迁移只读预检通过。测试中的 Git、网络、上传和删除均被模拟，无真实远端写入。
- 未编译、未运行 GN gen 或真实 Ninja，未创建 PR。此前组合工作树的两轮成功不等于这五个独立分支已通过门禁。
