# phone clean 恢复检查证据

本目录记录静态和模拟回归，未执行真实编译。

| 文件 | 内容 |
| --- | --- |
| historical-audit.json | 15 组准备补丁的反向检查与文本差异 |
| primary-pr-audit.json | 11 个正式 PR 对迁移基线的检查 |
| static-checks.json | SDK 输入数量、输出与现存产物集合对照、发布器回归 |
| fixture-checks.json | IDL、SDK、JSON 的临时目录回归结果 |
| js-path-regression.json | JS 四组合路径恢复和两个失败传播用例 |
| check_phone_norm.py | 语法、文件清单及发布器检查脚本 |
| test_phone_norm_fixtures.py | 使用模拟生成器的 IDL/SDK/JSON 检查 |
| test_js_paths_norm.py | 使用模拟 node/npm 的 JS 路径检查 |

反向检查不能直接匹配的结果，需要结合 [人工复核解释](../../oct13-phone-audit-clean-recovery.md) 阅读。模拟生成器检查不证明真实编译器输出、GN 依赖图或整仓构建成功。
