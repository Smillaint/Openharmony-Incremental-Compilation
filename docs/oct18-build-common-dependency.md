# SDK build-common 依赖排查与修复（2026-10-18）

#7006 的 SDK 失败不是 npm 安装步骤被跳过。已在失败门禁的精确 ace 源码上复现另一种情况：npm 6 沿用缺少本地依赖的旧锁文件时，安装返回 0，仍不创建 `node_modules/@koalaui/build-common`，随后 interop 编译出现与门禁相同的两条 TS6053。根目录显式声明这个已有依赖后，旧锁文件与全新安装两种场景均能编译。

一行兼容修复已追加到 [ace #7210](https://gitcode.com/openharmony/developtools_ace_ets2bundle/merge_requests/7210)，提交 `92f3fe9598c24f6118774101968176b20fc7b342`，带 `Signed-off-by: Smillick <3185479846@qq.com>`。公开 API 已回读新 HEAD 和 DCO 检查成功标签，PR 标题、正文及 Issue #4704 分组保持不变。没有修改 #7006、发送检视回复或触发新门禁。

失败节点的锁文件和 node_modules 没有取到，旧锁文件是受控复现条件，不能据此断言当次 CI 就是这个原因。华为云流水线入口无法访问，页面提示资源不存在。本记录区分可复现的代码兼容问题与尚未确认的 CI 实物状态。

## 版本与安装流程

失败 SDK 任务：[20261019-1-00249](https://dcp.openharmony.cn/workbench/cicd/detail/6ad576e764650f998bfeab08/runlist)。执行时间为北京时间 2026-10-19，记录日期采用 America/Los_Angeles 的 2026-10-18。

从任务公开发布的 [manifest](https://cidownload.openharmony.cn/tag/openharmony/master/default-xml/20261019094633/manifest.xml) 确认：

| 项目 | 失败任务使用的版本 |
| --- | --- |
| build 基线 | `6b6d6533967db07e8e7d40d140fc63d0faabacbd` |
| build #7006 补丁 | `3dc5695a126e2c9b3de9336ad8a290d2b66c8d29` |
| developtools/ace_ets2bundle | `9e0f9e58a243d7aeab672c317a2322dc37efd1a7` |
| Node / npm | 安装选择的 Node 为 14.21.1；隔离环境配套 npm 为 6.14.17 |

门禁日志明确调用了 ets1.2 的 npm 安装。精确 build 基线的 `prebuilts_download.py` 会删除该目录的 node_modules，但保留 package-lock.json，并打开 npm 的 package-lock 功能。并行子进程的 stdout/stderr 被 `communicate()` 收集；返回 0 时不输出具体安装内容，因此主日志中只有安装启动行，不能从中还原依赖树。

#7006 实物补丁只有两个 HiSysEvent Python 文件，没有更改安装配置、npm 包清单或锁文件。六种部件元数据分支的输出内容对比也一致，详见[前序排查](oct18-pr7006-sdk-gate.md)。

## 依赖关系与修改

失败 ace 版本中：

- 根目录通过本地路径安装 interop、libarkts，没有直接声明 build-common。
- interop、libarkts 的 dependencies 已包含 `@koalaui/build-common: ../build-common`。
- common、compat 的 tsconfig 都继承 `@koalaui/build-common/tsconfig.json`，其包清单只在 devDependencies 中声明该包。
- interop 的 `tsc -b .` 会构建 common、compat，因此需要这个配置文件在依赖查找路径中可见。

在没有旧锁文件的安装中，npm 6 能从本地包的依赖建立根目录链接，原代码也能编译。问题出现在保留的锁文件仍记录旧的本地包依赖、而本地包版本号没有变化时：npm 6 可以继续采用锁中的旧依赖树，安装成功却没有 build-common。

修改文件只有 `ets1.2/package.json`：

```diff
   "devDependencies": {
     "@idlizer/arktscgen": "./arktscgen",
+    "@koalaui/build-common": "./build-common",
     "@koalaui/interop": "./interop",
```

将构建入口需要的已有本地配置包列为直接开发依赖，使 npm 在本次安装时补齐依赖树和链接。没有引入第三方包、修改版本号、增加自动安装动作或跳过 TypeScript 检查；子包原有声明保留。

## 实物检查与复现

只读检查现有产品工作区，根目录链接为 `../../build-common`，目标 tsconfig 存在，common、compat、interop 等位置的 `require.resolve()` 均成功。该工作区不是失败 CI 节点，不能用它证明当次门禁的链接正常。

隔离验证使用失败 manifest 中的精确 ace 提交，源码由 `git archive` 导出到专用临时目录，工具为 Node 14.21.1 / npm 6.14.17。没有改动现有产品源码或 out。

旧锁文件通过受控夹具产生：暂时移除隔离目录中 interop、libarkts 对 build-common 的声明，生成锁文件，再恢复实际源清单。其后只删除测试目录的 node_modules，保留锁文件，模拟安装流程。该文件不是从 CI 取得的锁文件。

| 条件 | npm install | 根目录 build-common | npm run compile:interop |
| --- | --- | --- | --- |
| 原版，保留上述旧锁文件 | 0 | 不存在，require.resolve 失败 | 1，common/compat 两条 TS6053 |
| 修复版，保留同一旧锁文件 | 0 | 链接有效，require.resolve 成功 | 0 |
| 修复版，移除锁文件重新安装 | 0 | 链接有效，require.resolve 成功 | 0 |

安装命令沿用项目使用的仓库：`npm install --registry https://repo.huaweicloud.com/repository/npm/ --verbose`；编译使用包清单中已有的 `npm run compile:interop`。另一次独立的全新安装对照中，原版和修复版均通过，未将原版描述为必然失败。日志中的 fsevents 平台提示等警告没有导致安装失败。

本次验证覆盖实际安装、模块解析和 interop TypeScript 编译，没有运行完整 SDK 或产品构建，也没有验证新提交的完整门禁。

## 发布、分组与后续判断

- 修改前标签：`backup/build-common-rootcause-20261018`，ace 对应 `e76639ebbd94be09cd2038c9ae377dfca1724333`；交接仓对应 `650c643`。
- 本地源码：`D:/workspace/repositories/companion-prs-20261015/developtools_ace_ets2bundle`，分支 `fix/build-common-root-dependency-20261018`。
- 原 PR 分支：`fix/incremental-build-20261013`，正常快进到 `92f3fe9598c24f6118774101968176b20fc7b342`；没有改写历史或新建 PR。
- [源码、补丁、增量 bundle、精确版本与验证日志](evidence/20261018-build-common-rootcause/)已保存；完整临时工作记录在 `D:/workspace/archives/20261018-build-common-rootcause`。

#7210 属于安装组 Issue #4704，#7006 仍属于 HiSysEvent Issue #4682。#7006 单独重跑不会自动包含另一组尚未合入的 ace 修复；不能把 #7210 已推送等同于 #7006 门禁已修复。没有调整 Issue 分组或重新触发任务。

要确认当次故障，仍需失败节点的 package-lock.json、各级 node_modules 中 build-common 的链接和 realpath。维护者可以在原失败节点执行[只读采集脚本](evidence/20261018-build-common-rootcause/collect_failed_node.py)，参数为失败工作区的 ets1.2 路径，必要时用 `--node` 指定任务的 Node。脚本只读取相关包清单、锁文件条目、Git 版本和模块解析结果，不安装包、不清理文件，也不输出整段环境变量或认证配置。

若实物不符合旧锁文件条件，应继续排查安装后的目录替换、链接目标或工作区恢复过程，不能直接套用本次复现结论。自动巡检保持暂停，既有检视回复草稿保持原内容且未发送。
