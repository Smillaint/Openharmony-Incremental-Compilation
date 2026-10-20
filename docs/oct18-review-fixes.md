# 检视整改与原 PR 更新（2026-10-18）

2026-10-20 后续：[检视回复与修订版门禁](oct20-review-replies-and-gates.md)记录八条已发布回复和八组新任务；以下内容保留各自阶段的历史状态。

七条原 PR 的修订均已正常快进推送，公开 API 回读提交、源分支和文件范围一致，DCO 检查全部通过。PR 正文和 Issue 分组保持不变，检视回复尚未发送，新提交未触发门禁。

后续[IDL 编码兼容复核](oct18-idl-encoding-compatibility.md)确认原工具支持非 UTF-8 注释，#6982 已追加字节扫描修复至 `4e179e356e4ef508ea0c5f302459c6e366e58baa`，DCO 通过。下面表格保留首轮七条修订的版本，#6982 当前版本以上述追加记录为准。

记录日期采用 America/Los_Angeles 的 2026-10-18，GitCode 检视和发布回执为北京时间 2026-10-19。

## 修改及对应版本

| PR | 修改文件及作用 | 新提交 |
| --- | --- | --- |
| [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) | `config/components/idl_tool/idl.gni`：为 ArkUI-X 补回 `idl_inner` 的未使用变量处理，保留工具选择逻辑；说明外部 common 由所属 IDL 目标生成，以及 deps 仅约束生成顺序。 | `b4ca2d4124817b101a9335930bc758b491fc729d` |
| [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) | `ohos/app/app_internal.gni`：仅内置签名脚本使用 `--output-file` 和 `.sign_result.json`；外部脚本保留原参数和 `.stamp` 输出。 | `fb6add1534863be35a9df323a8d78d5168521f6d` |
| [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | 同步外部签名兼容和 `scripts/util/file_utils.py` 的 JSON 自愈。未扩大旧 IDL 修改范围。 | `37406489bf81204ef8d1479d4f6621e1a23e7437` |
| [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | `scripts/util/file_utils.py`：损坏的旧生成 JSON 触发重写，权限和其他 I/O 错误仍向上传播。 | `270bdc5c3cd438cdc2fdd9e86a85c65dafe59559` |
| [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009) | 同步相同 JSON 自愈，保留 NOTICE 现有修复。 | `577fed97c0cf1ee5973c6d264eb32e17513059fa` |
| [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046) | 同步相同 JSON 自愈，保留安装规则输入和可选依赖修复。 | `a82a8a03bd3a43c23c186d4ed32cd2602c010c93` |
| [build #7134](https://gitcode.com/openharmony/build/merge_requests/7134) | 同步相同 JSON 自愈，保留 loader 不删除重写 `components.json` 的修复。 | `f5de052afaf6b4c7b6801f013418797ace4d2203` |

JSON 自愈只捕获 `json.decoder.JSONDecodeError`。正常文件继续作内容比较，内容不变不更新 mtime。五条 PR 的公共文件逐字节相同；两条 PR 的 `app_sign` 模板逐字节相同，其他模板与各自原代码保持一致。

IDL 的 `collect_idl_inputs` 继续对读取失败、缺失 import 报错，没有加入跳过依赖的处理。后续验证发现整份文件严格按 UTF-8 解码会收紧原工具的输入范围，已改为按字节扫描 import。早先的 UTF-8 BOM 检查只验证 Python 能读取；原生成器实际拒绝该样例，不能将两者混为生成成功。单文件 `rebase_path` 转换已核对为系统绝对路径。

## 重复修改及合入边界

#6999 历史分支仍包含多组前置修复。本次仅追加签名和公共 JSON 修订，没有整文件覆盖为累计修复分支，也没有强推或重写历史。#6999 的旧 IDL 代码原本保留 ArkUI-X 分支，因此没有再追加相同兼容修复。

`file_utils.py`、签名模板以及 IDL、NOTICE 的历史重叠仍需协调合入顺序。其中一条合入后，其余 PR 应对目标分支重新比较并保留尚未合入的增量。发布后七条 PR 的公开 `mergeable=true`、`conflict_passed=true`，说明当时没有文本冲突，不代表检视批准或门禁通过。

## 验证结果及限制

隔离验证脚本共有 11 项检查通过：

- 五条 PR 分别覆盖空文件、截断 JSON、非法 JSON 的恢复，正常内容及键序变化保持 mtime，真实变化及缺失输出重写，权限与 I/O 错误不被吞掉。
- 校验五份公共 JSON 工具的字节一致性。
- 两份实际 `app_sign` 模板分别覆盖内置签名、外部签名、外部配置缺少兼容版本时回退、显式内置路径四种配置。外部配置生成的参数由不支持新参数的严格解析器接受。
- 校验两份签名模板的一致性。
- 从实际 IDL 模板提取初始化与依赖选择逻辑，覆盖 `is_arkui_x` 两种值与 `idl_inner` 缺省/false/true 共六种组合，确认显式 deps 保留。
- 所有变更文件通过 UTF-8 读取、Python 字节码编译或 GN 语法解析；七条增量提交均通过 `git diff --check`、文件范围和 DCO 检查。

GN 隔离验证使用官方独立工具 `2598 (f90c3d9df882)`，没有替换产品 prebuilts。该验证不等于产品所固定版本的完整 GN 生成、厂商实际签名或完整 ArkUI-X 构建。独立源码仓缺少完整源码树和产品 prebuilts，本轮没有执行产品 `--build-only-gn`、构建性能套或完整产品编译；应在原产品环境按既有交接命令补验。社区门禁没有重新触发，旧提交的通过记录不适用于这七条新提交。

已读 build 仓 AGENTS、deps/external_deps 使用说明、HAP 构建指导。修订保持公共模板参数、默认签名选择、链接依赖和工具链选择的既有边界，没有更改 API/SDK 版本、合规清单或生成文件。

## Git 备份和保存位置

- 七条源码修改前标签：`backup/review-fixes-20261018/pr-<PR编号>`，位于 `D:/workspace/repositories/pr-maintenance-20261015/build`。
- 七条新源码分支：`fix/review-pr-<PR编号>-20261018`。每条新提交的唯一父提交均为更新前原 PR HEAD，均含 `Signed-off-by: Smillick <3185479846@qq.com>`。
- 归档仓修改前标签：`backup/review-fixes-20261018`。
- [修改前后版本与分支清单](../patches/20261018-review-fixes/prepared.json)、[逐 PR 补丁、增量 bundle 和源码文件](../patches/20261018-review-fixes/)。bundle 以清单中的旧 HEAD 为前置对象，不是独立完整克隆。
- [本地检查、发布回读与公开 PR 快照](evidence/20261018-review-fixes/)。
- 本地操作和完整临时验证目录：`D:/workspace/archives/20261018-review-fixes/`。
- 远程发布保存目录：`/srv/workspace/patch_backups/20261018_review_fixes/`，仅用于独立 Git 发布，没有修改远程产品源码。

检视回复见[八条草稿](pr-drafts/20261018-ringking0-replies.md)，确认前不发送、不标记讨论已解决。自动巡检保持暂停。
