# PR 集中归档（2026-09-12）

本目录集中保存 8 个相关源码仓的 13 个已知 GitCode PR 补丁、11 个已准备分支补丁、四仓历史验证快照、本地未提交源码差异和 9 份压缩日志。代码仓本体保留在本地 repositories 目录，完整 Git bundle 保留在本地 archives 中。

2026-09-12 两次 SSH 连接均在远程构建机握手阶段超时。因此本次没有取得新的远程源码状态或 2026-09-01 原始构建日志；远程信息来自已有交接与 2026-09-02 验证快照，不能视作 9 月 12 日远程现场。GitCode PR 补丁则在本次从公开 API 重新读取。

## 已创建 PR 的实际补丁

| 仓库 / PR | 来源分支 | HEAD | 状态 | 文件数 | 补丁 |
| --- | --- | --- | --- | --- | --- |
| [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | `codex/fix-sa-profile-incremental-build` | `0d530d7e` | open | 5 | [diff](gitcode/build/pr-6965.patch) |
| [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) | `fix-hap-sign-incremental-build` | `34aa8cba` | open | 4 | [diff](gitcode/build/pr-6974.patch) |
| [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) | `fix-idl-common-outputs` | `4fa37075` | open | 1 | [diff](gitcode/build/pr-6982.patch) |
| [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | `incremental-build-all-validation-20260820` | `f1a46334` | open | 20 | [diff](gitcode/build/pr-6999.patch) |
| [build #7006](https://gitcode.com/openharmony/build/merge_requests/7006) | `fix-hisysevent-incremental-build` | `3dc5695a` | open | 2 | [diff](gitcode/build/pr-7006.patch) |
| [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009) | `fix-part-install-metadata-incremental-build` | `edc427a8` | open | 4 | [diff](gitcode/build/pr-7009.patch) |
| [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046) | `fix-install-incremental-metadata` | `5be8fa47` | open | 2 | [diff](gitcode/build/pr-7046.patch) |
| [build #7048](https://gitcode.com/openharmony/build/merge_requests/7048) | `fix-notice-incremental-deps` | `6840a0ba` | open | 2 | [diff](gitcode/build/pr-7048.patch) |
| [build #7049](https://gitcode.com/openharmony/build/merge_requests/7049) | `fix-sdk-split-incremental-deps` | `72115384` | open | 1 | [diff](gitcode/build/pr-7049.patch) |
| [third_party_iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) | `fix-geninit-incremental-output` | `5b884558` | open | 1 | [diff](gitcode/third_party_iptables/pr-62.patch) |
| [developtools_packing_tool #1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556) | `fix/hap-reproducible-archive` | `dcbbc78a` | open | 1 | [diff](gitcode/developtools_packing_tool/pr-1556.patch) |
| [third_party_jsframework #853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853) | `fix/jsframework-incremental-actions` | `a280a42f` | open | 1 | [diff](gitcode/third_party_jsframework/pr-853.patch) |
| [third_party_sane-airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22) | `fix/airscan-incremental-action` | `37de4f97` | open | 2 | [diff](gitcode/third_party_sane-airscan/pr-22.patch) |

每个补丁按 GitCode 返回的完整文件 hunks、文件模式、新增/删除/重命名信息组装为 unified diff。相邻 JSON 保留来源、查询时间、HEAD/base 和接口返回的 patch 元数据；[清单](gitcode-manifest.json) 包含 SHA-256。已用 `git apply --numstat` 验证语法及文件数，没有在产品源码上应用补丁或重新编译。

## 已准备分支

| 仓库 | 分支 | HEAD | 补丁 |
| --- | --- | --- | --- |
| build | `fix-install-incremental-metadata` | `5be8fa47` | [format-patch](prepared/build/fix-install-incremental-metadata.patch) |
| build | `fix-sdk-split-incremental-deps` | `72115384` | [format-patch](prepared/build/fix-sdk-split-incremental-deps.patch) |
| build | `fix-notice-incremental-deps` | `6840a0ba` | [format-patch](prepared/build/fix-notice-incremental-deps.patch) |
| build | `fix-js-assets-incremental-deps` | `f03aa33b` | [format-patch](prepared/build/fix-js-assets-incremental-deps.patch) |
| build | `fix-idl-acronym-header-outputs` | `97c0d5bc` | [format-patch](prepared/build/fix-idl-acronym-header-outputs.patch) |
| build | `fix-preloader-content-aware-output` | `07a42d2c` | [format-patch](prepared/build/fix-preloader-content-aware-output.patch) |
| build | `fix-static-abc-config-copy` | `00c502f7` | [format-patch](prepared/build/fix-static-abc-config-copy.patch) |
| interface_sdk-js | `fix-interface-sdk-split-depfile` | `680b35e0` | [format-patch](prepared/interface_sdk-js/fix-interface-sdk-split-depfile.patch) |
| interface_sdk-js | `fix-sdk-declaration-incremental-deps` | `df667b6d` | [format-patch](prepared/interface_sdk-js/fix-sdk-declaration-incremental-deps.patch) |
| arkcompiler_ets_frontend | `fix-build-system-output-isolation` | `5eb9bc67` | [format-patch](prepared/arkcompiler_ets_frontend/fix-build-system-output-isolation.patch) |
| developtools_ace_ets2bundle | `fix-libarkts-sdk-incremental-deps` | `8a4c58bc` | [format-patch](prepared/developtools_ace_ets2bundle/fix-libarkts-sdk-incremental-deps.patch) |

以上从本地发布裸仓按清单的 `base..commit` 导出，逐项核对分支 HEAD。[prepared-manifest.json](prepared-manifest.json) 保存基线、完整提交和补丁哈希。部分分支对应上表已有 PR，不代表另外新增了 11 个 PR。未生成正式提交的暂缓项保留在历史验证快照中。

## 验证现场与日志

- [四仓验证现场清单](validation-snapshot-20260902/manifest.json)：历史 HEAD、status 和 full-worktree diff。整份现场差异含当时尚未纳入正式 PR 的修改及锁文件变化，不能作为正式单 PR 补丁直接套用。
- [搬迁前分支状态](local-branches-before-move.json)：本地各仓 HEAD、分支与工作树状态。
- `local-uncommitted/`：build 和 packing-tool 验证目录中原有未提交源码差异；它们与正式 PR 补丁分别保存。
- [分组发布说明](build-functional-groups-20260903.md)：原 build 七分支改为五个功能组的历史记录。
- [日志清单](logs-manifest.json)：日志原路径、原始字节 SHA-256 和压缩大小，gzip 解压字节已逐份比对。

| 原始日志 | gzip 归档 |
| --- | --- |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/final_zero_change_build.log` | [final_zero_change_build.log.gz](logs/20260804/final_zero_change_build.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/final_zero_change_console.log` | [final_zero_change_console.log.gz](logs/20260804/final_zero_change_console.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/final_zero_change_ninja.log` | [final_zero_change_ninja.log.gz](logs/20260804/final_zero_change_ninja.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/notice_fix_first_build.log` | [notice_fix_first_build.log.gz](logs/20260804/notice_fix_first_build.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/notice_fix_first_console.log` | [notice_fix_first_console.log.gz](logs/20260804/notice_fix_first_console.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/notice_fix_first_ninja.log` | [notice_fix_first_ninja.log.gz](logs/20260804/notice_fix_first_ninja.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/notice_fix_second_build.log` | [notice_fix_second_build.log.gz](logs/20260804/notice_fix_second_build.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/notice_fix_second_console.log` | [notice_fix_second_console.log.gz](logs/20260804/notice_fix_second_console.log.gz) |
| `action相关增量编译/远程日志/action_incremental_logs_20260804/notice_fix_second_ninja.log` | [notice_fix_second_ninja.log.gz](logs/20260804/notice_fix_second_ninja.log.gz) |

其他本地门禁大包、报告、临时运行环境和历史实验保留在 `D:/workspace/archives/`，没有上传源码仓的 `.git`、私钥、工具缓存或整个构建输出。已有远程验证结论仍见 [原始十项交接](../../docs/original-ten-actions-completion-20260910.md)。

## 恢复方法

在对应源码仓的干净临时分支上，先核对清单中的仓库、基线与 HEAD，再使用下面的一种方式。

GitCode 聚合 diff 用于恢复整个 PR 文件差异（不恢复逐提交历史）：

```bash
git apply --check /path/to/pr-N.patch
git apply /path/to/pr-N.patch
```

已准备分支的 format-patch 保留提交信息：

```bash
git am /path/to/prepared-branch.patch
```

本地完整分支恢复可用 `D:/workspace/archives/20260912-workspace-cleanup/git-backups/` 中的 Git bundle；已提交版本和未提交 diff 分别保存。路径搬迁表见 [工作区整理说明](../../docs/workspace-organization-20260912.md)。
