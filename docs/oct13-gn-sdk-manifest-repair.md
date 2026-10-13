# SDK 文件清单的 GN 兼容修复

## 实际失败与修复

10 月 13 日远程构建在 GN 阶段失败，尚未进入 Ninja。保存的 error.log 指向：

```text
ERROR at //developtools/ace_ets2bundle/arkui-plugins/BUILD.gn:20:14: Disallowed exec_script call.
```

[上一阶段规范性修改](oct13-phone-audit-clean-recovery.md) 的两个 SDK BUILD.gn 使用 exec_script 枚举文件，调用方不在 OpenHarmony 白名单中。此前 Python/GN format 和模拟回归没有检查真实 GN 的调用限制，不能据此判定构建可用。

本次在 ace_ets2bundle 仓修复 8 个文件：

| 文件 | 修改 |
| --- | --- |
| arkui-plugins/BUILD.gn、koala-wrapper/BUILD.gn | 移除 exec_script，使用 read_file 读取受控 JSON 文件清单；清单、Node 和 npm 作为明确输入，工具闭包用文件 depfile 跟踪 |
| arkui-plugins/sdk_files.json、koala-wrapper/sdk_files.json | 新增版本管理的文件清单，分别列出 1,074/537 个直接输入和 1,071/534 个 payload 输出；不把整个 node_modules 目录或 gen 目录作为输入输出 |
| arkui-plugins/build_ui_plugins.py、koala-wrapper/build_ts_wrapper.py | 发布前校验实际文件集合与声明清单一致；过期清单直接报错并提示刷新；生成成功后写具体工具文件 depfile |
| sdk_copy.gni | package.json 复制目标直接依赖生成者；隔离 GN 图发现原来的私有间接依赖不足以证明生成输入的生产者关系 |
| sdk_files.py | 增加清单校验、刷新和 depfile 支持；补上 python3 shebang 与可执行文件模式，兼容本项目的 /usr/bin/env action 启动方式 |

GN 全局白名单没有修改。sysResource.js 继续由独立 target 生产；公开 target 名称、SDK 布局和产品构建参数保持既有约定。

## 验证边界

- 在临时源码树中使用空 exec_script 白名单，导入实际 SDK GN 和复制模板，成功生成 13 个 target。底层 ohos_copy 和 native 工具链使用最小替身，检查 GN 规则与生成输入的依赖关系；没有执行任何 action 或编译器。
- 输出数核对：gen_ui_plugins 为 1,072（含状态文件），gen_sdk_ts_wrapper 为 535；SDK 文件复制动作分别为 1,072 和 534，package.json 由独立 copy 目标发布。
- UTF-8、Python 语法、GN 解析、git diff --check 通过；所有清单输入均存在且清单无重复条目。
- 直接通过 /usr/bin/env 启动 sdk_files.py --help 成功，确认 action 执行权限和 shebang 可用。
- 模拟生成器回归通过：新增源码导致过期清单时，在编译/发布之前失败；工具文件 depfile、稳定 mtime、缺失恢复和失败保留旧文件通过。

**没有重跑产品 build.sh、产品 GN gen 或真实 Ninja。** 隔离图不能替代完整产品的依赖图和真实 Babel/TypeScript 编译验收。下一次人工构建应使用当前修复后的工作树。

## 版本与证据

修复前先保存 Git 版本与实际失败日志，保持工作树 HEAD 和真实索引不变。

- 修复前快照：`2a85c0803770938fbe7f77946f0d079679c47c58`，分支 `backup/before-gn-manifest-repair-20261013`。
- 修复后快照：`2a3500957d85ebdcde222066185531460a51ba17`，分支 `fix/sdk-gn-file-manifest-20261013`。
- [补丁和版本清单](../patches/20261013-gn-manifest-repair/versions.json)。补丁叠加在上一阶段规范版本上，不适用于未迁移的上游 HEAD。
- [失败日志、隔离图与回归证据](evidence/20261013-gn-manifest-repair/README.md)。
- 远程：`/srv/workspace/patch_backups/20261013_gn_manifest_repair/`。
- 本地恢复包：`D:\workspace\archives\20261012-migration\20261013-gn-manifest-repair.tar.gz`。
- 恢复包 SHA-256：`6e111e00441e11c06eaf99897859021160784692fb7955ad9a314ea3463e0f48`。

## 当前重试命令

这次失败在 GN，当前修复不需要重新删除产品产物。在已连接的远程终端复制下面的一行并回车：

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code && bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```

成功后保持源码不变，再执行同一行进行增量复测。每轮日志在 out/rk3568/build.log；第一轮结束后先保存日志，再进行增量，避免覆盖失败或完整构建证据。

此前连续粘贴的命令将 rm -rf out/rk3568 放在编译之前。检查时该目录仍有 24 GB，清理可能耗时较长；Ctrl+C 会中断清理，随后 shell 可能继续下一条编译命令。没有附加的终端会话记录，无法确认 Ctrl+C 前正在执行的具体进程。清理与编译应分别执行，等待清理正常结束后才启动编译。

## 文件清单维护

新增/删除 TS、components/schema 或运行时包文件时，刷新并提交文件清单。依赖包的来源路径改变时也应刷新。常规编译不需要执行这些命令。

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code/developtools/ace_ets2bundle
python3 sdk_files.py manifest plugins arkui-plugins ../.. --output arkui-plugins/sdk_files.json
python3 sdk_files.py manifest wrapper koala-wrapper ../.. --output koala-wrapper/sdk_files.json
```

刷新只更新受控构建配置，不生成 JS/native 中间产物。清单更新会触发 GN 重新读取，仍沿用原 build.sh 指令。
