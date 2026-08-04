# `airscan_action` 增量编译修复方案

本方案解决零代码改动重复编译时 `airscan_action` 仍被 Ninja 执行的问题，并保留三个目标的最终联合验证结果：

```text
ACTION //third_party/sane-airscan:airscan_action(//build/toolchain/ohos:ohos_clang_arm)
ACTION //third_party/jsframework:gen_snapshot(//build/toolchain/ohos:ohos_clang_arm)
ACTION //third_party/jsframework:ark_jsf(//build/toolchain/ohos:ohos_clang_arm)
```

完整构建结果：

```text
[OHOS INFO]  rk3568 build success
=====build  successful=====
real 286.27

airscan_action=0
gen_snapshot=0
ark_jsf=0
all_ACTION=0
CXX=0
CC=0
SOLINK=0
```

验证日志：`补丁后验证/incremental_verified_console.log`。

## 1. `airscan_action` 重复执行

### 1.1 原因

原实现存在三个问题：

1. `patch_install.py` 直接在 `third_party/sane-airscan` 源码目录中执行 `patch`，构建过程会修改输入源码。
2. 补丁应用失败时只输出提示，没有让 ACTION 失败，容易留下 `.rej` 文件和部分修改的源码。
3. `BUILD.gn` 声明的输出路径与脚本实际行为不一致。ACTION 声明生成 `target_gen_dir` 下的文件，但脚本没有生成这些文件。

因此一次构建会改变下一次构建的输入，Ninja 无法得到稳定的输入、输出和时间戳关系。

### 1.2 修复文件

```text
修改后脚本/third_party/sane-airscan/BUILD.gn
修改后脚本/third_party/sane-airscan/patch_install.py
```

### 1.3 修复代码

`BUILD.gn` 统一定义参与 ACTION 的源文件，并为每个输入声明对应生成输出：

```gn
# 所有 patched sources 都写入构建输出目录，源码树保持只读。
target_dir = "${target_gen_dir}/patched"

# 脚本、补丁和参与生成的源文件全部声明为输入。
airscan_action_inputs = [
  "${source_dir}/patch_install.py",
  "${source_dir}/patches/oh-transplant.patch",
]
# 每个源文件在 patched 目录中都有明确、可被 Ninja 检查的输出。
airscan_action_outputs = []
foreach(file, airscan_library_files) {
  airscan_action_inputs += [ "${source_dir}/${file}" ]
  airscan_action_outputs += [ "${target_dir}/${file}" ]
}

action("airscan_action") {
  script = "//third_party/sane-airscan/patch_install.py"
  inputs = airscan_action_inputs
  outputs = airscan_action_outputs
  # GN 路径转换为脚本执行时使用的构建目录相对路径。
  airscan_source_dir = rebase_path("${source_dir}", root_build_dir)
  airscan_output_dir = rebase_path("${target_dir}", root_build_dir)
  args = [
    "--source-dir",
    "$airscan_source_dir",
    "--output-dir",
    "$airscan_output_dir",
  ]
}
```

共享库改为编译生成目录中的 patched sources，不再编译被 ACTION 修改过的源码目录：

```gn
# 头文件优先从 patched 目录查找，未被生成的辅助文件仍可从源码目录读取。
include_dirs = [
  target_dir,
  source_dir,
]
sources = []
foreach(file, airscan_library_files) {
  # 三个后端依赖当前 OHOS 环境未提供的外部能力，不进入共享库编译。
  if (get_path_info(file, "extension") == "c" && file != "airscan-mdns.c" &&
      file != "airscan-tiff.c" && file != "airscan-wsd.c") {
    sources += [ "${target_dir}/${file}" ]
  }
}
```

`airscan-mdns.c`、`airscan-tiff.c` 和 `airscan-wsd.c` 依赖当前 OpenHarmony 构建环境不支持的 Avahi、TIFF 或 WSD 相关能力，因此不进入 OHOS 共享库编译；它们仍作为补丁生成输入保留。

`patch_install.py` 先创建临时 staging 目录，复制源码后只在 staging 中应用补丁：

```python
# staging 与最终输出位于构建目录，避免 patch 修改源码树。
staging_dir = tempfile.mkdtemp(prefix='airscan_patch_', dir=output_parent)
try:
    # copy2 保留源文件元数据，补丁仅作用于 staging 副本。
    for file_name in AIRSCAN_LIBRARY_FILES:
        shutil.copy2(
            os.path.join(source_dir, file_name),
            os.path.join(staging_dir, file_name),
        )
    apply_patch(patch_path, staging_dir)  # 补丁失败会抛出异常并终止 ACTION。
    for file_name in AIRSCAN_LIBRARY_FILES:
        # 内容不变时不覆盖正式输出，避免无意义的 mtime 更新。
        replace_if_changed(
            os.path.join(staging_dir, file_name),
            os.path.join(output_dir, file_name),
        )
finally:
    # 无论成功或失败都清理临时副本，不污染下一轮构建。
    shutil.rmtree(staging_dir, ignore_errors=True)
```

补丁先进行严格 dry-run。如果正向补丁不能应用，再检查是否已经应用；两种检查都失败时直接终止 ACTION：

```python
# 先验证补丁能否以零 fuzz 正向应用，防止部分匹配产生错误产物。
forward_check = run_patch(patch_path, work_dir, dry_run=True)
if forward_check.returncode == 0:
    # 正向检查通过后再正式应用补丁。
    return

# 反向 dry-run 通过表示 staging 内容已经包含该补丁，可安全复用。
reverse_check = run_patch(patch_path, work_dir, reverse=True, dry_run=True)
if reverse_check.returncode == 0:
    return

raise RuntimeError('oh-transplant.patch does not apply cleanly')
```

输出文件使用 `replace_if_changed()` 比较二进制内容。内容没有变化时不覆盖文件，从而保留原时间戳：

```python
if os.path.exists(output_path):
    with open(output_path, 'rb') as output_file:
        # 字节完全一致时直接返回，保留 Ninja 已记录的输出时间戳。
        if output_file.read() == source_content:
            return
```

### 1.4 解决效果与日志验证

- ACTION 不再修改源码目录，也不会生成 `.rej` 文件。
- 输入和输出与 GN 声明一致。
- 相同内容不会被重复写入，输出时间戳保持稳定。
- 最终零改动完整构建中 `airscan_action=0`。
- `patch_build_final_console.log`、`incremental_second_console.log` 和 `incremental_verified_console.log` 中该目标均为 0 次，说明单目标生成完成后后续完整构建能够持续复用产物。
