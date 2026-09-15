# 9 月 6 日源码迁移修复与远程构建验证

## 验证范围

**最终连续两轮完整构建成功：主 Ninja 均为 13 步，耗时分别为 87.44 秒和 88.40 秒。原始十项、早期三项以及两个 ramdisk Action 均未执行。**

本轮使用 `/srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code`，产品为 `rk3568`，目标为 `make_all`。补齐八月份修复的迁移缺口，并继续处理新仓实际构建中发现的重复任务。历史旧仓的 9 步结果不作为新仓验收证据。

实际执行命令：

```bash
bash ./build.sh -p rk3568 --build-target make_all
```

第四轮起增加 `--ninja-args=-dexplain` 记录触发原因。所有轮次在同一输出目录串行运行；每轮保留控制台、退出码、构建日志和 Ninja 日志。

## 修复、代码与 PR 对照

| 修复 | 历史 PR / 本轮提交 | 代码修改与作用 |
| --- | --- | --- |
| HAP 归档时间稳定 | [packing_tool #1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556)，`39276f0cce56` | `adapter/ohos/Compressor.java` 固定三条 ZIP 条目创建路径的修改时间，避免同输入 HAP 字节随时间变化 |
| JS runtime / snapshot 稳定 | [jsframework #853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853)，`273f047694b6` | `js_framework_build.sh` 保留共享 runtime，比较 snapshot 内容并恢复相同内容的原时间戳，避免依赖链无效重建 |
| airscan 隔离打补丁 | [sane-airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22)，`b2aa7a364840` | `BUILD.gn` 从生成目录编译 34 个文件；`patch_install.py` 在 staging 中打补丁、比较发布，显式限定正反方向，防止 GNU patch 自动反向误判 |
| 非空 SA ZIP 元数据稳定 | [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) 的补充，`a764e585eaff2` | `ohos/sa_profile/sa_profile_binary.py` 为 `part_name_info.json` 显式使用固定 ZIP 时间；详细回归见前一份复核记录 |
| ramdisk 真实输出 | 新增补丁，`bde50153f19f` | `ohos/images/BUILD.gn` 声明实际 `packages/phone/images/ramdisk.img`、`updater.img`；`build_image.py` 增加可选 depfile 目标，使依赖目标与真实输出一致，保留原打包命令参数 |
| 摄像头生成配置依赖 | 新增补丁，`1ef36b854cfc` | `device/board/hihope/rk3568/camera/vdi_impl/v4l2/BUILD.gn` 直接使用生成目录中的 C/H 文件，移除 GN 阶段 touch 和伪 `tmp.c` 输出；保留 `copy_source` 标签为依赖组 |
| 默认 SELinux 输出条件 | 新增补丁，`39e6dc71a96f` | `base/security/selinux_adapter/BUILD.gn` 仅在 split 模式声明其专用输出及预置消费者，消除默认模式中不存在的哈希、版本、兼容文件引起的重复构建 |
| 内核模块按内容发布 | 新增补丁，`6761f9a3b5ae` | `build/templates/kernel/linux-6.6/make_ko.sh` 在签名成功后逐个比较 `.ko`，仅发布变化内容，阻止相同模块带动 `mk_chip_ckm_img` |

本轮没有创建或更新 GitCode PR。表中的新增提交和适配补丁与历史 PR 分开保存，不能把历史 PR 的现有 diff 当成本轮新增修复。完整提交、基线、分支和文件清单见 [fix-commits.json](evidence/20260915-build/fix-commits.json)。

## 迁移与已有修改保护

修改前为相关仓库保存 Git 引用、工作树补丁和增量 bundle。通过临时 Git 索引制作提交，没有切换真实工作树、移动 HEAD 或暂存其他迁移修改。

airscan 原有 18 个修改源文件经逐文件比较，确认属于在源码目录应用旧补丁的结果。其中两个文件存在相同检查块重复三次的问题。恢复前保存全部差异和 16 个 `.rej`，随后改为生成目录应用补丁。其他仓库的 package-lock、node_modules、既有 C 文件修改均保留。

远程备份位于 `/srv/workspace/patch_backups/20260915_migration_build/`。build 中 ramdisk、内核模块的提交基于含迁移修改的快照，应使用单提交补丁整理上游 PR，不能整条分支直接作为独立 PR 推送。其他新增仓库提交的基线见证据索引。

## 回归与结果判定

| 轮次 | 退出码 | 主 Ninja 实际任务数 | 整体耗时 | 说明 |
| --- | --- | --- | --- | --- |
| 第二轮 | 0 | 1972 | 589.81 秒 | 迁移后三项修复及 SA 补充修复，完成大量重编译 |
| 第三轮 | 0 | 1681 | 640.60 秒 | 加入 ramdisk 修复，仍有大量链接 |
| 第四轮 | 0 | 85 | 138.34 秒 | 摄像头生成路径切换，含一次性编译 |
| 第六轮 | 0 | 20 | 84.27 秒 | SELinux 默认模式输出及消费者修复通过 |
| 第七轮 | 0 | 13 | 87.44 秒 | 内核模块内容发布修复通过 |
| 第八轮 | 0 | 13 | 88.40 秒 | 源码和产品配置不变的连续复验 |

最终每轮为 7 个 Action、6 个 stamp，没有主 Ninja C/C++ 编译、链接、COPY 或镜像生成任务。七个 Action 是 `kernel`、`ko_sample`、`rockchip_products` 和四个 metadata Action。内核与模块 Action 内部仍执行其构建检查命令，不能将主 Ninja 没有 CC/CXX 等同于完全没有内部构建活动。

内核模块发布修复使相关任务从 20 步收敛到 13 步，消除了七个下游任务；整体用时没有下降，因此仅报告任务收敛，不宣称这一项带来实测加速。完整统计和计数口径见 [build-summary.json](evidence/20260915-build/build-summary.json)，最终任务逐行记录见 [第七轮](evidence/20260915-build/seventh_steps.txt)、[第八轮](evidence/20260915-build/eighth_steps.txt)。

- SA 归档七项隔离回归通过，覆盖非空归档跨日期稳定、输入变化、输出删除和失败保留旧结果。
- airscan 七项回归通过：34 个输出与独立 `git apply` 的结果逐字节一致；源码不变；同输入哈希及 mtime 稳定；缺失输出恢复；输入变化更新；已打补丁不反向撤销；非法补丁失败且不破坏已有输出。
- 使用本轮源码生成的 Java 打包工具，对 Telephony、Contacts 两组实际 HAP 输入分别打包两次，跨越 ZIP 时间粒度，哈希均一致；归档条目固定时间且模块 JSON 内容保持。
- ramdisk 三项脚本回归通过：两个特殊镜像的 depfile 指向真实输出，普通镜像调用保持兼容。真实整仓构建成功生成两种镜像。
- 摄像头生成目录中的 `config.c`、`config.h`、`params.c`、`params.h` 与原消费文件逐字节相同，新路径已通过真实 C 编译及链接。
- SELinux 调整后，十个策略及上下文文件的哈希和 mtime 均不变。策略内容、neverallow 校验和运行时库没有修改。
- 内核模块五项脚本回归通过：首次发布、同内容不更新时间、变化发布、缺失输出恢复、签名失败保留旧输出。真实签名后的 `kosample.ko` 哈希与 mtime 也保持不变。

HAP 测试使用本轮生成的 `app_packing_tool.jar`。不能据此声称 SDK 内嵌打包工具已经被替换；ARM 目标端 C++ 打包程序没有在 x86 构建机直接运行。

## 构建过程中的修正

第一轮在 airscan 编译失败：最初的补丁检测允许 GNU patch 自动反向，误将干净输入判断为已打补丁。改为 `--force` 加显式方向，并引入独立内容对照后恢复构建。

第五轮在 GN 阶段失败：首次调整 SELinux 输出时，部分 split 专用预置目标仍无条件声明输入。同步限制消费者后，第六轮重新通过。失败轮次保留在证据中，不计入成功验收。

第二轮、第三轮分别有大量 C++ 编译和链接；第四轮包含摄像头切换生成路径的一次性重编译。因此这些轮次的任务数不能全部算作单项修复的性能收益。

## 剩余边界

内核目标仍执行其既有变更检查。`compile_check` 是未生成输出，相关脚本在运行时检查多个外部仓库；直接删除这个输出会改变触发机制，而现有 GN 依赖未完整覆盖这些源码。没有用伪造成功文件的方式跳过内核检查。

四个 metadata Action 及相应 stamp 仍会执行，但稳定发布阻止其继续传播到原始 packages 十项。最终结论应按实际执行记录判断，不能把 Ninja 开始时的计划任务数当成完成任务数，也不能声称整仓所有 Action 为零。

适用范围为本次新仓 `rk3568` 默认 SELinux 配置。没有启动设备、执行目标端 SELinux 单元测试或独立性能套件；系统/厂商 split 产品未单独整仓验证，相关声明与消费者在非默认模式保持原逻辑。日志中的既有构建警告和 Ninja trace 工具不识别新版日志格式的提示保留，成功以构建退出码和实际任务记录为准。

## 归档入口

提交、补丁、测试、压缩控制台和依赖解释见 [证据索引](evidence/20260915-build/README.md)。17 个增量 Git bundle 均通过远端 `git bundle verify`；三个下载归档的 SHA-256 与远端一致。

- 本地 Git 恢复包：`D:/workspace/archives/bundles/20260915-migration-build/`。
- 最终两轮完整 build/Ninja 日志：`D:/workspace/archives/logs/20260915-migration-build/final-full-logs.zip`。
- 远端完整逐轮日志：`/srv/workspace/action_incremental_logs_20260915/sep06_migration/`。

已阅读 build、packing_tool、SELinux 仓库规范以及镜像打包、依赖声明、构建调试和性能分析文档。修改保留既有构建风格，未修改预编译工具、策略内容或生成物来伪造验收结果。
