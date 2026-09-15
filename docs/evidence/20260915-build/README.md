# 新仓迁移修复与编译证据

完整结论见 [交接文档](../../sep06-migration-build-results-20260915.md)。

## 结果

- [逐轮构建统计](build-summary.json)：包含命令、源码路径、起止时间、退出码、实际任务数和目标 Action 计数。剔除 `[0/0]` 警告及嵌套 Hvigor 进度，避免把子进程输出混入主 Ninja 任务。
- [第七轮任务](seventh_steps.txt)、[第八轮任务](eighth_steps.txt)：均为 13 步，7 个 Action、6 个 stamp。
- `*_status.json` 为各轮原始状态；`*_console.log.gz` 为原始控制台压缩副本；`*_explain.txt` 为 Ninja 依赖解释。失败的第一、第五轮也保留。

## 补丁与 Git 版本

| 内容 | 文件 |
| --- | --- |
| 修改前快照 | [checkpoints.json](checkpoints.json) |
| 新增修复提交与分支 | [fix-commits.json](fix-commits.json) |
| 17 个 bundle 校验及哈希 | [bundle-verification.json](bundle-verification.json) |
| HAP 打包 | [packing_tool 补丁](developtools_packing_tool-fix.patch) |
| runtime/snapshot | [jsframework 补丁](third_party_jsframework-fix.patch) |
| airscan staging 与补丁方向 | [airscan 补丁](third_party_sane-airscan-fix.patch) |
| ramdisk 输出 | [ramdisk 补丁](build-ramdisk-fix.patch) |
| 摄像头生成源文件 | [camera 补丁](device_board_hihope-camera-fix.patch) |
| SELinux 默认输出与消费者 | [SELinux 补丁](base_security_selinux_adapter-fix.patch) |
| 相同内核模块发布 | [内核模块补丁](build-ko-fix.patch) |

build 修复提交的父提交包含原有迁移代码。恢复 bundle 需要对应基线提交；整理 PR 时使用单提交补丁，不把快照历史整体推送为独立修复。

## 回归

- [airscan 测试](test_airscan_incremental.py)、[七项重放日志](airscan-regression-replay.txt)、[旧源码补丁归一化记录](airscan-source-normalization.json)。
- [实际 HAP 打包命令、JAR 与产物哈希](packing-results.json)。
- [ramdisk 三项回归](ramdisk-regression.txt)。
- [摄像头四个生成文件内容对照](camera-source-equivalence.json)。
- [SELinux 十个文件哈希与 mtime 对照](selinux-output-stability.json)。
- [内核模块测试](test_ko_incremental.py)、[五项回归](ko-regression.txt)、[真实签名模块的稳定性](ko-output-stability.json)。

完整二进制恢复包及较大的 Ninja 日志保存在工作区 `archives`，路径见交接文档。此目录未包含凭据、依赖缓存或产品镜像。
