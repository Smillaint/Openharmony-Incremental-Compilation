# IDL 输入编码兼容复核（2026-10-18）

原生成器允许注释中包含非 UTF-8 字节。新增 `collect_idl_inputs` 对整个文件做 UTF-8 解码，会使原本能生成的 IDL 在依赖扫描阶段提前失败。这是兼容性回退，已在原 [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) 修复，提交为 `4e179e356e4ef508ea0c5f302459c6e366e58baa`，DCO 检查通过。检视回复尚未发送，新提交没有触发门禁。

记录日期采用 America/Los_Angeles 的 2026-10-18，远程测试与 GitCode 回执为北京时间 2026-10-19。

## 原工具的读取方式

核对远程产品树中的 `foundation/ability/idl_tool`，现场 HEAD 为 `d45cc0a0cf24986b1c4f07a08dc7d6e3a3ee5c3b`，该仓工作区干净。

- `idl_tool_2/util/file.cpp` 的 `OpenByRead` 使用 `fopen(..., "r")`，`Read` 使用 `fread`，随后逐字节取字符，没有先将文件解码成 UTF-8。
- `idl_tool_2/lexer/lexer.cpp` 按字节识别语法并跳过注释；原工具不要求注释字节先通过 UTF-8 校验。
- 本轮直接运行现场已有的主机工具 `out/rk3568/clang_x64/ability/idl_tool/idl`，而非用模拟生成器推断。该二进制 SHA-256 为 `decd467d6cdb8874f45b65cdd323336c9763e92298717f27ac1eeea1d609c7c7`。

这里的兼容范围是原工具实际接受的字节输入，不表示它能够识别任意编码或支持任意非 ASCII 标识符。[源码快照与工具身份](evidence/20261018-idl-encoding/generator-source.json)保存了检查依据。

## 修改及重复 PR 边界

只修改 `config/components/idl_tool/idl.py` 的依赖收集：

1. 使用 `read_bytes()` 读取 IDL，注释和语法匹配均改为字节正则。
2. 仅将匹配到的 ASCII import 名转换为路径；源文件原样交给生成器，不猜测、不转换编码。
3. 保留递归依赖记录、缺失 import 报错、生成失败不替换旧输出，以及内容不变时保留时间戳的行为。

本次只更新 #6982。#6999 的历史 IDL 修改没有新增的 `collect_idl_inputs`，不存在这处严格解码回退，因此没有整段同步或扩大其范围。其他六条检视整改 PR 的版本保持原样。

## 实际对比结果

同一组样例分别运行原二进制、引入依赖扫描前的旧 wrapper、严格 UTF-8 wrapper、修复后的字节扫描 wrapper。旧 wrapper 取自 build Git 的 `de69337^2`；严格版为修复前 #6982 的 `b4ca2d41`。测试命令和全部断言保存在[复现脚本](../patches/20261018-idl-encoding/verify_remote_body.py)，[原始执行记录](evidence/20261018-idl-encoding/verification.json)保存返回码和错误输出。

| 样例 | 原二进制与旧 wrapper | 严格 UTF-8 扫描 | 修复后 |
| --- | --- | --- | --- |
| ASCII、UTF-8 无 BOM | 成功 | 成功 | 成功 |
| GBK、GB18030、Latin-1、CP1252、Shift-JIS 块注释 | 成功 | `UnicodeDecodeError` | 成功 |
| UTF-8 根文件递归 import GBK、Latin-1 文件 | 成功 | `UnicodeDecodeError` | 成功，三份输入均进入 depfile |
| 含空格及中文的目录中的 GBK 输入 | 成功 | `UnicodeDecodeError` | 成功 |
| UTF-8 BOM、UTF-16 LE/BE BOM | 失败 | 失败 | 失败 |
| 非法语法、非 ASCII import 标识符 | 失败 | 失败 | 失败 |

14 个样例中，原工具接受的 9 个均在修复后成功；生成的完整文件集合及每个文件的 SHA-256 与原二进制直接生成结果一致，旧 wrapper 的结果也一致。对这 9 个样例同时验证：

- 重复执行保持输出内容和 mtime 不变。
- 删除一份声明输出后可以恢复，恢复内容一致。
- 新增缺失 import 时构建失败，已发布输出的内容和 mtime 保持不变。
- 输入源文件字节不变；多层 import 全部收集，注释里的伪 import 不进入 depfile。

原工具拒绝的另外 5 个样例，修复后仍失败，没有通过忽略解码错误或吞掉异常来继续构建。

此前“BOM 可以读取”的记录只证明 Python 扫描成功，不能推导原生成器能够生成。本轮原二进制实际拒绝 UTF-8 BOM 样例，原有草稿中的表述已更正。

Python 字节码编译、`git diff --check`、单文件修改范围、唯一父提交和 DCO 均通过。测试产物位于独立目录 `/srv/workspace/patch_backups/20261018_idl_encoding/contract-z56l1_ls/`，没有修改产品源码或清理产品 out。本轮没有运行完整产品编译、ArkUI-X 构建或社区门禁；以上结果是原 IDL 工具的定向兼容性验证。

## 版本与恢复

- 源码修改前标签：`backup/idl-encoding-20261018` → `b4ca2d4124817b101a9335930bc758b491fc729d`，位于 `D:/workspace/repositories/pr-maintenance-20261015/build`。
- 新源码分支：`fix/idl-byte-inputs-20261018`，唯一父提交为上述旧 HEAD，提交带 `Signed-off-by: Smillick <3185479846@qq.com>`。
- 原远端分支：`fix-idl-common-outputs`，正常快进推送，没有重写历史。公开 API 回读 HEAD、分支、正文和 PR 文件范围一致，标签含 `dco检查成功`。
- 归档仓修改前标签：`backup/idl-encoding-20261018` → `0ffb33b72d3face37c828886357e544ce88ec880`。
- [源码、单次补丁、增量 bundle、复现脚本及提交清单](../patches/20261018-idl-encoding/)；bundle 需要旧 HEAD 对象，不能替代独立完整克隆。
- [发布前后 PR 快照与回读记录](evidence/20261018-idl-encoding/)。本地操作目录为 `D:/workspace/archives/20261018-idl-encoding/`。

检视回复仅更新[待确认草稿](pr-drafts/20261018-ringking0-replies.md)，没有发送或解决讨论。自动巡检保持暂停，旧提交的门禁通过记录不适用于本次新提交。
