# `ark_jsf` 增量编译修复方案

## 1. 原因

`ark_jsf` 的输入包含：

```text
dist/strip.native.min.js
```

该文件由 `gen_snapshot` 相关 JS 构建流程生成。旧脚本即使生成内容与上一轮完全相同，也会重新覆盖文件，导致 mtime 更新。Ninja 因输入时间变化而再次执行 `ark_jsf`：

```text
gen_snapshot
  -> dist/strip.native.min.js 的 mtime 更新
  -> ark_jsf
```

## 2. 修复文件

```text
修改后脚本/third_party/jsframework/js_framework_build.sh
```

## 3. 修复代码

脚本执行前保存旧输出及其时间戳：

```bash
# ark_jsf 依赖的最终 JS 输出。
snapshot_output="$8/dist/strip.native.min.js"
# 临时文件只用于保存构建前的内容和 mtime。
snapshot_backup=$(mktemp)
snapshot_output_exists=false
if [ -f "$snapshot_output" ]; then
  # -p 同时保存原内容和时间戳，供生成后比较与恢复。
  cp -p "$snapshot_output" "$snapshot_backup"
  snapshot_output_exists=true
fi
# 脚本正常结束或异常退出时都删除临时文件。
trap 'rm -f "$snapshot_backup"' EXIT
```

生成结束后比较新旧内容。如果内容完全一致，则恢复原文件时间戳：

```bash
# 只有新旧内容完全一致时才恢复时间戳。
if [ "$snapshot_output_exists" = true ] &&
   cmp -s "$snapshot_backup" "$snapshot_output"; then
  # 内容未变化，恢复旧 mtime，避免 ark_jsf 被时间变化误触发。
  touch -r "$snapshot_backup" "$snapshot_output"
fi
```

如果内容实际发生变化，不恢复时间戳，Ninja 仍会正常触发下游 `ark_jsf`，因此不会漏编真正的代码变化。

## 4. 解决效果与日志验证

- JS 内容不变时，`strip.native.min.js` 的 mtime 不再变化。
- JS 内容改变时仍保留新时间，正常触发下游重新生成。
- 修复后的第一轮单目标构建执行 `ark_jsf=1`，见 `jsframework_timestamp_first.log`。
- 第二轮零改动单目标构建为 `ark_jsf=0`，见 `jsframework_timestamp_second.log`。
- 最终零改动完整构建为 `ark_jsf=0`，见 `incremental_verified_console.log`。

## 5. 三阶段完整构建对比

| 阶段 | 构建结果 | 耗时 | `airscan_action` | `gen_snapshot` | `ark_jsf` | 日志 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 初步补丁后的完整构建 | 成功 | 757.09 秒 | 0 | 1 | 1 | `patch_build_final_console.log` |
| JS 时间戳最终修复前的零改动构建 | 成功 | 621.78 秒 | 0 | 1 | 1 | `incremental_second_console.log` |
| 最终修复后的零改动完整构建 | 成功 | 286.27 秒 | 0 | 0 | 0 | `incremental_verified_console.log` |

第一阶段的两个 JS ACTION 是补丁修改后的必要重建；第二阶段证明原方案尚未完全消除 JS 目录时间戳循环；第三阶段证明三个目标在零改动情况下均不再执行。
