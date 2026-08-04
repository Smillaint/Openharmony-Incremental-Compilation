# `gen_snapshot` 增量编译修复方案

## 1. 原因

`third_party/css-what` 的 `css_what_sources` 目标先将源码复制到：

```text
out/rk3568/obj/third_party/jsframework/runtime
```

随后 `gen_snapshot` 又向同一目录复制运行时文件。旧脚本结束时还会执行：

```bash
rm -rf ./runtime
```

目录被删除、重建或写入后，`runtime` 目录时间会晚于 `css_what_sources.stamp`。下一轮 Ninja 因而得到以下变脏链路：

```text
css_what_sources.stamp
  -> obj/third_party/jsframework/runtime
  -> gen_snapshot
```

问题日志 `incremental_second_console.log` 中可以看到同一轮重新执行：

```text
COPY ../../third_party/css-what/src obj/third_party/jsframework/runtime
STAMP obj/third_party/css-what/css_what_sources.stamp
ACTION //third_party/jsframework:gen_snapshot
```

## 2. 修复文件

```text
修改后脚本/third_party/jsframework/js_framework_build.sh
```

## 3. 修复代码

脚本开始时取得 `css_what_sources.stamp`：

```bash
# $8 是 jsframework 的 target_gen_dir；相邻 css-what 目录保存其完成 stamp。
css_what_stamp="$(dirname "$8")/css-what/css_what_sources.stamp"
```

删除旧逻辑中的：

```bash
# runtime 是 css-what 与 jsframework 共用的生成目录，不能在 ACTION 结束时删除。
rm -rf ./runtime
```

上面这一行从最终脚本中删除，不再销毁共享生成目录。

构建结束后，将共享 `runtime` 目录时间稳定到 `css_what_sources.stamp`：

```bash
# 只有目录和 stamp 同时存在时才同步时间，兼容首次构建和局部目标构建。
if [ -d "$8/runtime" ] && [ -f "$css_what_stamp" ]; then
  # 让目录 mtime 与其生产者 stamp 一致，阻断“目录比 stamp 新”的循环触发。
  touch -r "$css_what_stamp" "$8/runtime"
fi
```

## 4. 解决效果与日志验证

- `runtime` 不再被脚本删除并重新创建。
- `runtime` 目录不会因为 gen_snapshot 的内部复制而持续晚于对应 stamp。
- 修复后的第一轮单目标构建执行 `gen_snapshot=1`，这是脚本发生变化后的必要重建，见 `jsframework_timestamp_first.log`。
- 第二轮零改动单目标构建为 `gen_snapshot=0`，见 `jsframework_timestamp_second.log`。
- 最终零改动完整构建为 `gen_snapshot=0`，见 `incremental_verified_console.log`。
