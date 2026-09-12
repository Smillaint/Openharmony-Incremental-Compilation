# 本地工作区整理（2026-09-12）

项目主资料仓继续使用 `D:/workspace/Openharmony-Incremental-Compilation`，其余源码仓、worktree 和发布裸仓归入 `repositories/`；历史脚本、实验、日志、补丁与报告归入 `archives/`。未删除原始资料。

本次完成 74 项路径搬迁，核验 13,460 个文件的搬迁前后 SHA-256，并核对 16 个仓库/worktree 的 HEAD 和分支引用；关联工作区已有源码修改保持一致。整理前已创建并验证 13 份本地 Git bundle，未提交差异另存恢复目录。

## 目录入口

| 路径 | 内容 |
| --- | --- |
| `Openharmony-Incremental-Compilation/` | 对外维护的文档、PR 补丁、分支清单和必要日志 |
| `repositories/` | build、IDL、packing-tool、GitCode 两个三方仓及发布仓 |
| `repositories/pr-publishing/` | 原 phone-install-publish-20260902；发布脚本基于自身目录定位仓库 |
| `archives/20260912-workspace-cleanup/` | 整理前盘点、Git bundle、未提交 diff、移动清单与校验记录 |
| `archives/legacy-materials/` | 工作区根目录原有 action/NOTICE 材料 |
| `archives/scripts/`、`archives/patches/`、`archives/bundles/` | 历史脚本、补丁和 bundle |
| `archives/logs/`、`archives/reports/`、`archives/packages/` | 日志、报告及压缩包 |
| `archives/staging/`、`archives/fixtures/`、`archives/scratch/`、`archives/tool-cache/` | 历史实验、夹具、临时文件及工具缓存 |

旧私钥副本因文件权限限制保留原位，仍在忽略规则内，不读取内容或上传。两个原先已经删除的实习总结文档保持原有状态，不在此次整理中恢复或提交删除。

## Git 和脚本路径

IDL 与 packing-tool 验证目录以及发布目录中的两个工作区属于关联 worktree。搬迁后使用 `git worktree repair` 更新管理信息，核对 HEAD、分支引用和已有源码修改；产品代码没有改变。

历史文档保留当时路径作为证据，使用旧路径前按下表转换。归档脚本可能包含当时的绝对路径，不能直接作为当前运行入口；优先使用 repositories/pr-publishing 下基于 PSScriptRoot 定位的发布脚本。

## 旧路径 → 新路径

下表路径均相对于 `D:/workspace/`。

| 旧路径 | 新路径 |
| --- | --- |
| `.tmp-fetch-action-pr-evidence.ps1` | `archives/scripts/.tmp-fetch-action-pr-evidence.ps1` |
| `.tmp-inventory-workspace.py` | `archives/scripts/.tmp-inventory-workspace.py` |
| `.tmp-iptables-geninit-5b884558.bundle` | `archives/bundles/.tmp-iptables-geninit-5b884558.bundle` |
| `.tmp-opencode-glm52` | `archives/tool-cache/opencode-glm52` |
| `.tmp-publish-iptables-5b884558` | `repositories/iptables-publish.git` |
| `.tmp-push-iptables-auth.ps1` | `archives/scripts/.tmp-push-iptables-auth.ps1` |
| `.tmp-summary-20260902` | `archives/reports/summary-20260902` |
| `.tmp-verify-action-docs.py` | `archives/scripts/.tmp-verify-action-docs.py` |
| `.tmp-write-action-readme.py` | `archives/scripts/.tmp-write-action-readme.py` |
| `.tmp_cleanup_glm_artifacts.sh` | `archives/scripts/.tmp_cleanup_glm_artifacts.sh` |
| `.tmp_export_action_publish.py` | `archives/scripts/.tmp_export_action_publish.py` |
| `.tmp_glm52_binary_depfile_review_prompt.txt` | `archives/scripts/.tmp_glm52_binary_depfile_review_prompt.txt` |
| `.tmp_glm52_dynamic_gn_prompt.txt` | `archives/scripts/.tmp_glm52_dynamic_gn_prompt.txt` |
| `.tmp_glm52_ets2panda_build_system_prompt.txt` | `archives/scripts/.tmp_glm52_ets2panda_build_system_prompt.txt` |
| `.tmp_glm52_geninit_only_prompt.txt` | `archives/scripts/.tmp_glm52_geninit_only_prompt.txt` |
| `.tmp_glm52_js_assets_cache_depfile_prompt.txt` | `archives/scripts/.tmp_glm52_js_assets_cache_depfile_prompt.txt` |
| `.tmp_glm52_next_incremental_prompt.txt` | `archives/scripts/.tmp_glm52_next_incremental_prompt.txt` |
| `.tmp_glm52_next_incremental_root_prompt.txt` | `archives/scripts/.tmp_glm52_next_incremental_root_prompt.txt` |
| `.tmp_inspect_build_system_first.sh` | `archives/scripts/.tmp_inspect_build_system_first.sh` |
| `.tmp_inspect_build_system_second.sh` | `archives/scripts/.tmp_inspect_build_system_second.sh` |
| `.tmp_inspect_first_incremental.sh` | `archives/scripts/.tmp_inspect_first_incremental.sh` |
| `.tmp_inspect_second_incremental.sh` | `archives/scripts/.tmp_inspect_second_incremental.sh` |
| `.tmp_prepare_action_publish.py` | `archives/scripts/.tmp_prepare_action_publish.py` |
| `.tmp_remote_batch_first_build.sh` | `archives/scripts/.tmp_remote_batch_first_build.sh` |
| `.tmp_remote_batch_second_build.sh` | `archives/scripts/.tmp_remote_batch_second_build.sh` |
| `.tmp_remote_build_system_first.sh` | `archives/scripts/.tmp_remote_build_system_first.sh` |
| `.tmp_remote_build_system_second.sh` | `archives/scripts/.tmp_remote_build_system_second.sh` |
| `.tmp_remote_dryrun.sh` | `archives/scripts/.tmp_remote_dryrun.sh` |
| `.tmp_remote_preloader_first.sh` | `archives/scripts/.tmp_remote_preloader_first.sh` |
| `.tmp_remote_preloader_second.sh` | `archives/scripts/.tmp_remote_preloader_second.sh` |
| `.tmp_review_build_system_fix.sh` | `archives/scripts/.tmp_review_build_system_fix.sh` |
| `.tmp_review_geninit.py` | `archives/scripts/.tmp_review_geninit.py` |
| `.tmp_summarize_dryrun.sh` | `archives/scripts/.tmp_summarize_dryrun.sh` |
| `.tmp_verify_action_publish.py` | `archives/scripts/.tmp_verify_action_publish.py` |
| `.tmp_verify_preloader_patch.py` | `archives/scripts/.tmp_verify_preloader_patch.py` |
| `0001-Fix-common-IDL-output-declarations.patch` | `archives/patches/0001-Fix-common-IDL-output-declarations.patch` |
| `0001-Isolate-absolute-IDL-generated-outputs.patch` | `archives/patches/0001-Isolate-absolute-IDL-generated-outputs.patch` |
| `0001-Keep-common-IDL-source-names-consistent.patch` | `archives/patches/0001-Keep-common-IDL-source-names-consistent.patch` |
| `0001-Keep-IDL-template-state-private.patch` | `archives/patches/0001-Keep-IDL-template-state-private.patch` |
| `0001-Preserve-common-IDL-output-paths.patch` | `archives/patches/0001-Preserve-common-IDL-output-paths.patch` |
| `0001-Reset-IDL-path-state-between-iterations.patch` | `archives/patches/0001-Reset-IDL-path-state-between-iterations.patch` |
| `530936a76d8b548d98af94438b60d2b61b4e0917` | `archives/staging/530936a76d8b548d98af94438b60d2b61b4e0917` |
| `530936a76d8b548d98af94438b60d2b61b4e0917.tar.gz` | `archives/packages/530936a76d8b548d98af94438b60d2b61b4e0917.tar.gz` |
| `action相关增量编译` | `archives/legacy-materials/action相关增量编译` |
| `arkui_stamp_fix_stage_20260818` | `archives/staging/arkui_stamp_fix_stage_20260818` |
| `build.log` | `archives/logs/build-log` |
| `ets2bundle_pr7061_stage_20260819` | `archives/staging/ets2bundle_pr7061_stage_20260819` |
| `gate-6982-logs` | `archives/logs/gate-6982-logs` |
| `gitcode_pr` | `repositories/gitcode-pr` |
| `idl-common-output-fix.bundle` | `archives/bundles/idl-common-output-fix.bundle` |
| `idl-fix-v6.bundle` | `archives/bundles/idl-fix-v6.bundle` |
| `idl-fix-v7.bundle` | `archives/bundles/idl-fix-v7.bundle` |
| `idl-gni-double-i-bug-feedback-20260813.md` | `archives/notes/idl-gni-double-i-bug-feedback-20260813.md` |
| `idl-output-fix-v2.bundle` | `archives/bundles/idl-output-fix-v2.bundle` |
| `idl-output-fix-v3.bundle` | `archives/bundles/idl-output-fix-v3.bundle` |
| `idl-output-fix-v4.bundle` | `archives/bundles/idl-output-fix-v4.bundle` |
| `idl-output-fix-v5.bundle` | `archives/bundles/idl-output-fix-v5.bundle` |
| `notice相关增量编译` | `archives/legacy-materials/notice相关增量编译` |
| `ohos_declaration_ets2.patch` | `archives/patches/ohos_declaration_ets2.patch` |
| `ohos_declaration_gn_format.patch` | `archives/patches/ohos_declaration_gn_format.patch` |
| `ohos_declaration_test_fixture` | `archives/fixtures/ohos_declaration_test_fixture` |
| `ohos_declaration_test_fixture.tar` | `archives/packages/ohos_declaration_test_fixture.tar` |
| `openharmony-build-idl` | `repositories/openharmony-build-idl` |
| `openharmony-build-sa` | `repositories/openharmony-build-sa` |
| `openharmony-developtools-packing-tool` | `repositories/openharmony-developtools-packing-tool` |
| `openharmony-developtools-packing-tool-validation` | `repositories/openharmony-developtools-packing-tool-validation` |
| `phone-install-publish-20260902` | `repositories/pr-publishing` |
| `report` | `archives/reports/report` |
| `report.zip` | `archives/packages/report.zip` |
| `SSH远程.md` | `archives/notes/SSH远程.md` |
| `_codex_notice_v2_inputs.py` | `archives/scripts/_codex_notice_v2_inputs.py` |
| `__pycache__` | `archives/tool-cache/python-pycache` |
| `拉代码、测试、上库相关命令.txt` | `archives/notes/拉代码、测试、上库相关命令.txt` |
| `Openharmony-Incremental-Compilation/.tmp-phone-install-fix` | `archives/scratch/phone-install-fix` |

## GitHub 归档范围

详见 [PR 集中归档](../pr-archive/20260912/README.md)。GitHub 保存源码补丁和必要证据；本地完整仓库、bundle、大型历史包及工具环境继续保留本地。

远程 SSH 本次两次均在握手阶段超时，远程现场未同步。后续连通后补充最终组合构建的原始日志和各仓当前 HEAD，不将历史快照当作当前远程状态。
