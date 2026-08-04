# NOTICE 增量编译问题原因与修复方案

## 1. 问题表现

零代码改动再次执行：

```bash
./build.sh -p rk3568 --build-target make_all
```

Ninja 仍然执行大量名称以 `__notice` 结尾的 ACTION。`ninja -d explain` 的主要提示为：

```text
output NOTICE_FILES/.../*.a.txt doesn't exist
output obj/.../*.notice.txt doesn't exist
```

日志分析发现约 129 个缺失的 NOTICE 声明输出，并在零改动构建中触发约 130 个 NOTICE ACTION。

## 2. 涉及文件

```text
build/ohos/notice/notice.gni
build/ohos/notice/collect_module_notice_file.py
```

需要修改：

```text
build/ohos/notice/collect_module_notice_file.py
```

`notice.gni` 的输出声明和 `--output` 参数传递保持不变。

## 3. 原因

`notice.gni` 会为每个 NOTICE ACTION 声明输出。

静态库、source set 和 Rust library 使用：

```gn
outputs += [
  "${static_libraries_notice_dir}/$_notice_subdir/$module_name.a.txt",
]
```

其他模块通常使用：

```gn
outputs += [ "$target_out_dir/$module_name.notice.txt" ]
```

这些路径通过 `--output` 传给 Python 脚本：

```gn
foreach(o, outputs) {
  args += [
    "--output",
    rebase_path(o, root_build_dir),
  ]
}
```

修复前的 Python 脚本只有在找到许可证文件时才进入输出循环：

```python
if notice_file:
    if other_files:
        notice_file = f"{notice_file},{','.join(other_files)}"
    for output in options.output:
        notice_info_json = '{}.json'.format(output)
        os.makedirs(os.path.dirname(output), exist_ok=True)
        os.makedirs(os.path.dirname(notice_info_json), exist_ok=True)
        notice_files = [file for file in notice_file.split(",") if file]

        write_file_content(
            notice_files,
            options,
            output,
            notice_info_json,
            module_notice_info_list,
            depfiles,
        )
```

如果模块目录中没有 `LICENSE`、`NOTICE` 或 `README.OpenSource`：

```text
notice_file = None
```

脚本正常退出，但不会生成 GN 已声明的输出，形成以下循环：

```text
GN 声明 notice.txt 输出
  → Python 未找到许可证文件
  → Python 不创建 notice.txt
  → Ninja 下一轮发现输出不存在
  → __notice ACTION 再次执行
```

## 4. 修复代码


首先准备许可证文件列表；没有许可证时保持空列表：

```python
notice_files = []
if notice_file:
    if other_files:
        notice_file = f"{notice_file},{','.join(other_files)}"
    notice_files = [file for file in notice_file.split(",") if file]
```

随后无条件遍历所有 GN 声明输出：

```python
# GN declares every path in options.output as an action output. Create a
# stable empty notice when the module has no license file so Ninja does not
# rerun the action because a declared output is missing.
for output in options.output:
    notice_info_json = '{}.json'.format(output)
    write_file_content(
        notice_files,
        options,
        output,
        notice_info_json,
        module_notice_info_list,
        depfiles,
    )
```

同时将 `--output` 改为必需参数，避免构建定义与脚本参数不一致：

```python
parser.add_argument('--output', action='append', required=True)
```

## 5.解决问题

`write_file_content()` 可以处理空的 `notice_files`：

```python
notice_contents = []
output_content = "".join(
    "{}\n".format(content)
    for content in notice_contents
)
```

没有许可证内容时生成：

```text
module.notice.txt       0 字节空文件
module.notice.txt.json  []
```

脚本使用 `write_text_if_changed()` 写入输出：

```python
if os.path.exists(output_path):
    with open(output_path, 'r', encoding='utf-8', errors='ignore') as output_file:
        if output_file.read() == content:
            return
```

第二轮构建时空文件已经存在且内容没有变化，因此不会覆盖文件，mtime 保持不变。Ninja 同时满足：

- 声明输出真实存在；
- 输入没有变化；
- 输出内容和时间戳没有变化。

因此不会再次执行普通模块的 `__notice` ACTION。

## 6. 空 NOTICE 不影响最终结果

下游系统 NOTICE 收集脚本会跳过空文件：

```python
if os.path.exists(notice_file) is False or os.stat(
        notice_file).st_size == 0:
    continue
```

静态库 NOTICE 合并逻辑同样跳过空文件：

```python
if os.stat(file).st_size == 0:
    continue
```

所以空文件只用于满足 Ninja 的输出契约，不会向最终 NOTICE 文档加入虚假许可证内容。

## 7. 功能测试

提交前使用无许可证的临时模块目录连续执行脚本两次，验证：

- 空 NOTICE 文件存在且大小为 0；
- JSON 元数据内容为 `[]`；
- depfile 正常生成；
- 两次执行后 NOTICE 文件的纳秒级 mtime 完全一致；

## 8. 编译验证

第一轮构建：

```text
日志：验证日志/notice_fix_first_console.log
构建结果：rk3568 build success
耗时：0:06:15
__notice ACTION：7477
```

修改了所有 NOTICE ACTION 共用的 Python 脚本

源码不变、输出目录不清理，立即执行第二轮：

```text
日志：验证日志/notice_fix_second_console.log
构建结果：rk3568 build success
耗时：0:13:39
__notice ACTION：1
```

第二轮唯一剩余目标：

```text
//developtools/ace_ets2bundle/ets1.2/libarkts:panda_sdk__notice
```

该目标此前的 explain 结果为缺失：

```text
clang_x64/gen/developtools/ace_ets2bundle/ets1.2/libarkts/
panda_sdk__notice.d
```

