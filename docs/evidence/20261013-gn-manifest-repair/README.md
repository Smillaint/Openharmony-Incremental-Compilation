# SDK GN 兼容修复证据

| 文件 | 内容 |
| --- | --- |
| failed-error.log、failed-build.log | 人工构建实际失败日志；GN 禁止新增 exec_script 调用 |
| isolated-gn.log、isolated-gn-outputs.json | 临时树中导入实际 SDK GN/复制模板，空白名单下生成图成功及输出清单 |
| repair-static-checks.json | UTF-8、语法、diff、action 执行权限、具体输入和 depfile 转义检查 |
| repair-fixture-checks.json | 使用替身生成器的 clean 恢复、过期清单拒绝、失败保留输出检查 |
| check_gn_manifest_graph.py | 隔离 GN 图检查脚本；只生成临时图，不执行 action |
| test_gn_manifest_fixtures.py | 模拟生成器回归脚本，不运行真实编译器 |

隔离图使用最小 ohos_copy/native 工具链替身，不能代表完整产品构建。源码、补丁和精确版本见 [修复交接](../../oct13-gn-sdk-manifest-repair.md)。
