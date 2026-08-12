# OpenHarmony ACTION 增量编译修复材料

本目录用于整理 OpenHarmony `rk3568` 增量编译 ACTION 重复执行问题的修复代码、原因分析和验证日志。后续创建新 Git 仓库后，可直接以本目录作为 PR 工作区。

## 目录内容

| 路径 | 内容 |
| --- | --- |
| `action相关增量编译/airscan_action.md` | `airscan_action` 最终修复代码、注释和验证 |
| `action相关增量编译/gen_snapshot.md` | `gen_snapshot` 最终修复代码、注释和验证 |
| `action相关增量编译/ark_jsf.md` | `ark_jsf` 最终修复代码、注释和验证 |
| `action相关增量编译/远程日志/修复日志.md` | 完整修复过程、根因和验证结果 |
| `action相关增量编译/初步方案.txt` | 三个重复 ACTION 的初步问题定位 |
| `action相关增量编译/修复脚本/` | 从远端已验证工作区同步的最终修复脚本 |
| `action相关增量编译/原始脚本/` | 初始脚本备份，用于对比修改 |
| `action相关增量编译/远程日志/补丁前基线/` | 修改前的 `build.log`、`error.log` 和 `.ninja_log` |
| `action相关增量编译/远程日志/补丁后验证/` | 补丁构建、问题定位和最终零改动验证日志 |
| `docs/build-action-incremental.md` | `build` 仓 SA Profile、packages 综合实验和剩余 Action 状态 |
| `docs/parallel-analysis-prompt.md` | 供另一台主机并行分析使用的完整提示词和操作约束 |
| `docs/recent-build-prs-20260812.md` | 最近两个 `build` PR（SA Profile 与 HAP signing）的修改、验证结果和后续分析方向 |
| `docs/current-project-handoff.md` | 截至 2026-08-12 的统一交接提示词、PR 状态、待办清单和 GN/Ninja/restat 验证方法 |
| `patches/build/` | 从本地 GitCode fork 正式提交直接导出的 SA Profile 与 HAP signing 完整补丁 |
| `SSH远程.md` | SSH、文件传输、日志读取和人工编译操作说明 |

## 修复目标

```text
ACTION //third_party/jsframework:ark_jsf(//build/toolchain/ohos:ohos_clang_arm)
ACTION //third_party/jsframework:gen_snapshot(//build/toolchain/ohos:ohos_clang_arm)
ACTION //third_party/sane-airscan:airscan_action(//build/toolchain/ohos:ohos_clang_arm)
```

最终零改动验证结果：

```text
rk3568 build success
ark_jsf=0
gen_snapshot=0
airscan_action=0
all_ACTION=0
CXX=0
CC=0
SOLINK=0
```

最终代码方案分别见 `airscan_action.md`、`gen_snapshot.md` 和 `ark_jsf.md`，完整处理过程见 `action相关增量编译/远程日志/修复日志.md`。

## 后续使用

1. 新建 Git 仓库后再初始化本目录并配置远端。
2. 提交前确认 `id_ed25519` 等密钥文件没有进入暂存区。
3. 以 `action相关增量编译/原始脚本/` 和 `action相关增量编译/修复脚本/` 生成或审查最终 PR 差异。
4. 编译由操作者手动执行。未收到明确编译指令时，只进行代码修改、静态分析或指定日志读取。

当前目录中的 `.gitignore` 不忽略 `*.log`，因此远程验证日志可以随新仓库提交；私钥和常见构建产物仍会被忽略。
