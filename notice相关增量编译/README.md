# NOTICE 相关增量编译问题

本目录记录 OpenHarmony `rk3568` 全量目标在零代码改动情况下重复执行 NOTICE ACTION 的问题、修复代码和验证结果。
```

## 修复结论

修复前，GN 为 NOTICE ACTION 声明输出文件，但模块没有许可证文件时，Python 脚本不会生成这些输出。Ninja 每轮都会因为声明输出不存在而重新执行 ACTION。

修复后，即使模块没有许可证内容，也会创建稳定的空 NOTICE 文件和空 JSON 元数据。下游 NOTICE 合并逻辑会跳过空文件，因此不会改变最终许可证内容。

验证结果：

| 构建轮次 | `__notice` ACTION | 构建结果 | 说明 |
| --- | ---: | --- | --- |
| 修复后的第一轮 | 7477 | 成功 | 公共 Python 脚本发生变化，所有相关 ACTION 必要重建 |
| 零改动第二轮 | 1 | 成功 | 普通模块 NOTICE 重复执行已消除 |

第二轮剩余目标：

```text
ACTION //developtools/ace_ets2bundle/ets1.2/libarkts:panda_sdk__notice(//build/toolchain/linux:clang_x64)
```

该目标此前由缺失的 `panda_sdk__notice.d` depfile 触发，属于独立的 SDK NOTICE 流程，不是本次普通模块空 NOTICE 输出问题。

