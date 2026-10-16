# 其他历史 PR 更新结果（2026-10-15）

**当前状态：4 条旧 PR 的源码分支均已正常推送，正文已通过浏览器替换为确认后的简短版本。GitCode API 回读的 4 个 HEAD 与发布提交一致，4 条正文与确认稿逐字一致（忽略首尾空白），PR 均保持 open。** 没有重新运行产品编译，没有新建 PR，也没有为这些 PR 触发门禁。

## 已更新的旧 PR

| PR / 原 Issue | 已发布的提交 | 文件与作用 |
| --- | --- | --- |
| [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) / [#4668](https://gitcode.com/openharmony/build/issues/4668) | `de69337b7f99f2328417e27fe591903862c9bbdc` | `config/components/idl_tool/idl.gni`、`idl.py`：补齐 client 头文件、缩写命名、生成目标依赖和递归 import；out 内临时生成、完整检查后按内容发布，支持 clean 后恢复。保留最新上游的 OHOS 工具链分支。 |
| [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046) / [#4704](https://gitcode.com/openharmony/build/issues/4704) | `04a4ff52bbc53fa8104000748c9e38a16df53ca3` | `ohos/common/binary_install_info.py`、`ohos/packages/modules_install.py`、`ohos/packages/BUILD.gn`、`scripts/util/file_utils.py`：保留 SA 过滤与可选依赖修复，补齐稳定 JSON、模块列表、空 arm64e 输出和两项安装规则输入。包含 JSON 语义比较，避免依赖另一 PR 才能稳定字典顺序。 |
| [jsframework #853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853) / [#323](https://gitcode.com/openharmony/third_party_jsframework/issues/323) | `4172098b9b45baf9b37fa3be021bf1ff6bea6359` | `BUILD.gn`、`js_framework_build.sh`、`test/ut/runtime.ts`：out 内构建、具体 CSS/配置/测试输入、保护 CSS 生成文件、并行失败传播和 native 测试替身。 |
| [airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22) / [#19](https://gitcode.com/openharmony/third_party_sane-airscan/issues/19) | `142326aff6b6bc24785d49b860c1bf006bd3aa83` | `BUILD.gn`、`patch_install.py`：保留新主干八项补丁，在 out/gen/patched 生成，按内容发布；解决旧 PR 两个文件与当前主干的文本冲突，保留原共享库有效源文件集合。 |

这些提交保留原 PR 历史，将当前上游作为另一父提交，均可从旧 PR HEAD 正常快进，不需要强推。补丁范围按功能限定，没有把累计分支的全部修复混入单条 PR。DCO 均为 `Signed-off-by: Smillick <3185479846@qq.com>`。

正文见 [四条旧 PR 描述](pr-drafts/20261015/existing-pr-descriptions.md)，只保留触发原因、修改方式和预期结果。原 PR 编号、标题、源分支及 Issue 关联继续沿用。

发布证据：[远端分支核对](../patches/20261015-pr-maintenance/published.json)、[PR HEAD 与正文回读](../patches/20261015-pr-maintenance/descriptions-updated.json)。页面截图：[IDL #6982](evidence/20261015-other-pr-refresh/build-6982.png)、[安装 #7046](evidence/20261015-other-pr-refresh/build-7046.png)、[JS #853](evidence/20261015-other-pr-refresh/jsframework-853.png)、[airscan #22](evidence/20261015-other-pr-refresh/airscan-22.png)。截图中的门禁标签属于历史运行，不代表本次提交已通过新门禁。

## 暂不追加代码的旧 PR

将旧 PR 与当前上游作三方合并，再与保存的累计修复比较，以下修复内容一致：build #6974（HAP）、#7006（HiSysEvent）、#7048（NOTICE）、#7049（SDK split）、iptables #62、packing_tool #1556。没有仅为刷新日期而制造提交。

build #7009 的 NOTICE 分阶段发布和 parts 稳定修复也没有缺失。它与累计版 `ohos/packages/BUILD.gn` 的差异来自其他功能，不能整文件覆盖，否则会带入缺少配套脚本的校验和 host 目标。

build #6999 历史分支包含 SA、HAP、旧 IDL 等前置提交。它自身的 packages 校验和 host 修复没有缺失；与累计版的差异分别属于 SA #6965、IDL #6982、安装 #7046、NOTICE #7009。保持原功能分组，不把四组后续修改重复塞回这个大 PR。

## 配套 PR 与门禁

完整 Action → PR → Issue 对应关系及实时规则见 [Action、PR 与 Issue 对照](action-pr-issue-map-20261015.md)。13 个现有 Issue 已补齐正文清单；除下列 IDL/CSS 六条配套外，SDK split 调用方、SDK 插件/wrapper、ROFS 和 loader 也仍有提交缺口。

- IDL #6982 需要账户、输入法、DLP、分布式能力、音频五仓的输出／依赖补充。这五仓的 `fix/incremental-build-20261013` 已在上轮发布，需要分别创建 PR 并关联 build Issue #4668。
- JS #853 需要 css-what 的具体复制输出及 fixture innerkit；该仓发布分支已存在，需要配套 PR，关联 jsframework Issue #323。
- 不在同仓同目标分支另建关联同 Issue 的重复 PR。跨仓配套可以沿用同一个 Issue。
- ROFS、components.json、SDK 插件/wrapper 等无对应旧 PR 的新增项仍按 [源码交接](oct13-source-pr-handoff.md) 单独处理，本次没有将它们混入四条旧 PR。
- 描述不使用旧日志替当前组合背书；完成源码和配套 PR 更新后再启动联合门禁。

## 本次检查

- 对 13 条历史 PR 实时读取状态、源分支、Issue 和 diff；查询时均为 open。
- 更新前分支另存 `before/pr-<编号>-20261015` 并导出 bundle；4 条候选提交均验证旧 HEAD 为祖先，文件范围、UTF-8、DCO、`git diff --check` 通过。
- Python 字节码编译通过；IDL 隔离检查覆盖递归 import、部分／全部 clean 恢复、稳定时间戳、失败保留和输出不完整失败。
- JSON 语义比较和删除恢复通过，JS `bash -n` 通过。
- airscan 与独立 `git apply` 的八项补丁输出逐字节一致；34 个输出的内容和时间戳稳定，缺头文件及整目录清理均能恢复，源码不变。
- Windows 对照用独立临时 Git 根目录并设置 `core.autocrlf=false`，避免父仓路径范围和自动换行转换干扰。未修改修复源码以适应测试。
- 本次未运行 GN、整仓编译、JS 运行时单测或设备冒烟；上轮组合构建记录与本次分支检查分别保留。

已读 build 仓 AGENTS、deps/external_deps、NOTICE 收集策略和 HAP 构建说明；保留公共 target、工具链选择和 NOTICE 产物边界，不更改 API/SDK 版本与既有编译指令。

## 版本与发布记录

本地独立仓：`D:/workspace/repositories/pr-maintenance-20261015/{build,third_party_jsframework,third_party_sane-airscan}`。更新分支为 `fix/pr-<编号>-refresh-20261015`，原有 17 仓源码快照不变。

归档入口：[准备清单](../patches/20261015-pr-maintenance/prepared.json)、[本次检查](../patches/20261015-pr-maintenance/verification.json)、[补丁与增量 bundle](../patches/20261015-pr-maintenance/)。bundle 以清单中的旧 PR HEAD 和 upstream SHA 为前置对象，不能作为独立完整镜像。

更新前完整 bundle 和操作脚本位于 `D:/workspace/archives/20261015-pr-maintenance/`。

最初使用当前 Windows SSH 别名连接到了另一套远程环境，因此错误判断原发布凭据不存在。随后根据历史成功脚本 `D:/workspace/archives/20261012-migration/run_remote_script.py` 找回实际发布连接；原发布目录与 SSH 凭据均仍有效，无需重新提供令牌。

发布通过原远程环境中的独立目录 `/srv/workspace/patch_backups/20261015_pr_maintenance/` 完成，没有写入远程产品源码。脚本先核对旧 HEAD、祖先关系、DCO 和补丁范围，再按仓正常推送，并用 `ls-remote` 核对四个结果。源码推送后通过浏览器保存四条正文，最后使用公开只读 API 核对 HEAD 和正文。

本地操作脚本与完整旧版本仍保存在 `D:/workspace/archives/20261015-pr-maintenance/`，发布脚本为 `remote_publish.py`，回读脚本为 `verify_publication.py`。后续发布先核对真实连接与分支状态，不以当前 SSH 别名替代历史发布连接，也不覆盖他人新增提交。
