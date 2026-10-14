# SDK 插件和 wrapper 的具体文件生成链

插件与 wrapper 在 out 内生成，使用受控 JSON 文件清单声明具体 inputs/outputs；按内容发布并补足 package.json 生产者依赖。通过 read_file 兼容 GN exec_script 白名单，工具文件由 depfile 跟踪。

## 修改范围

仓库：`developtools/ace_ets2bundle`。

- `arkui-plugins/BUILD.gn`
- `arkui-plugins/build_ui_plugins.py`
- `arkui-plugins/sdk_files.json`
- `koala-wrapper/BUILD.gn`
- `koala-wrapper/build_ts_wrapper.py`
- `koala-wrapper/sdk_files.json`
- `sdk_copy.gni`
- `sdk_files.py`

## 依赖与验证

保留原 target、SDK 布局和独立 sysResource.js 生产者；依赖迁移版 libarkts 输出隔离。新增或删除 TS、schema、runtime 文件时刷新并提交 sdk_files.json。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

清单输入存在且无重复，插件/wrapper payload 输出分别为 1,071/534；模拟回归覆盖过期清单、缺失恢复、稳定发布与失败保留。在移走两个源码生成目录并清空 out 后，真实产品完整编译通过且源码生成目录未重建。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/developtools_ace_ets2bundle/sdk-explicit-file-outputs.patch)。
- 提交：`5df2dea2c4e5b96b6766e1429f94e75e5e3501d2`。
- 迁移基线：`b545845711e41987f9ca54c09b89061ce5ec6b4c`。
- 远程准备引用：`refs/heads/review/sdk-explicit-file-outputs-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
