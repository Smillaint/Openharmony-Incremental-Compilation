# 9 月 6 日源码迁移复核与 SA 归档补充修复

## 结论

2026-09-15 已连接远程构建机，确认部分修复从 8 月 16 日源码迁入 9 月 6 日源码。新仓仍缺少三个历史修复，旧仓的双轮增量结果不能直接作为新仓验收证据。

本轮在新仓补充修复了 **非空 binary SA ZIP 的元数据时间戳不稳定**。隔离回归从 6 项通过、1 项失败变为 7 项全部通过；只改 `build/ohos/sa_profile/sa_profile_binary.py`，3 行新增、1 行删除。没有执行 GN、真实 Ninja、整仓构建或性能套件，尚无新仓整仓收益数据。

## 源码与日志归属

| 用途 | 实际路径 |
| --- | --- |
| 旧源码 | `/srv/workspace/openharmony_master_default_20260816174546_huawei_9bd231a19/code` |
| 新源码 | `/srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code` |
| 既有迁移备份 | `/srv/workspace/patch_backups/20260908_aug16_to_sep06_pre_migration/` |
| 本轮备份与验证 | `/srv/workspace/patch_backups/20260915_sa_binary_metadata_timestamp/` |

新仓 build HEAD 是 `6ca3b1250746f72f097c53d319bb2c24aa97f537`，其上保留了尚未提交的迁移修改。

`action_incremental_logs_20260909/original_10_actions_recheck/second_console.log` 的实际运行时间为 9 月 10 日，日志引用的是 **8 月 16 日源码路径**。这份日志仍为 9 个主 Ninja 步骤，说明旧组合工作树的结果得到复核；它不证明 9 月 6 日仓也已收敛。

新仓 `out/rk3568/build.log` 修改时间为 9 月 9 日，包含大量编译与打包步骤，末段计数到 26272。这属于另一次大量执行的构建记录，不能与旧仓的稳态第二轮混用。当前复核材料没有提供新仓连续两轮稳态验证；不能据此断言新仓已经回归，也不能断言新仓已达到旧仓效果。

## 迁移现状

下表说明实际文件状态，不把跨版本文件不同直接认定为缺陷。完整 SHA 和状态清单见 [迁移证据](evidence/20260915/migration-audit.json)。

| 仓库 | 9 月 6 日仓现状 | 判断与后续 |
| --- | --- | --- |
| build | 31 个已跟踪修改，另有 `generate_host_info.py`、`stabilize_json_file.py` 两个已有未跟踪脚本 | 已包含 SA、packages、校验、NOTICE、HiSysEvent、SDK 等迁移代码；不能只复制已跟踪 diff 而遗漏这两个脚本 |
| interface/sdk-js | `BUILD.gn`、`process_internal.py`、`remove_internal.py` 有修改 | SDK 配套修改已存在，仍需新仓双轮验证 |
| arkcompiler/ets_frontend | consistency、build_system 修改存在；另有 package-lock 与 node_modules 变化 | 保留现状；环境及依赖文件变化不混入本轮补丁 |
| developtools/ace_ets2bundle | `ets1.2/BUILD.gn`、`ets1.2/libarkts/BUILD.gn` 有修改 | 输出隔离相关迁移已存在 |
| third_party/iptables | `genInit.py` 与旧仓修复后的 SHA 完全相同 | 内容感知生成修复已迁入；三个既有 C 文件修改保留 |
| developtools/packing_tool | 工作树干净；新仓 `Compressor.java` 缺少旧仓的固定时间常量及设置调用 | #1556 的归档时间稳定化尚未迁入，需按新基线移植并复测 HAP 哈希 |
| third_party/jsframework | 仅 package-lock 有修改；构建脚本无旧仓的 snapshot 备份、比较及恢复时间逻辑 | #853 的 runtime/snapshot 修复尚未迁入 |
| third_party/sane-airscan | 仍在源码目录运行 patch；声明的生成目录输出与实现不对应；存在 18 个修改源文件和 16 个 `.rej` | #22 的 staging 修复尚未迁入；必须先区分已打补丁内容和其他修改，再适配新上游，不能直接覆盖或反向撤销全部源文件 |

建议先处理 airscan 的迁移，再补 packing_tool 与 jsframework，取得新仓双轮日志后再定位剩余 metadata/ramdisk。原始 packages 十项与早期独立 Action 的范围仍分别记录。

## SA 补充修复

此前 #6965 已让归档通过 `atomic_output` 临时生成并比较发布，实际 SA 文件也使用固定 ZIP 时间。但 `part_name_info.json` 仍通过 `ZipFile.writestr(字符串名称, 内容)` 添加，会带入调用时的当前日期。

当 binary SA 列表为空时，该 JSON 条目不存在，历史空归档用例无法暴露问题；当列表非空时，即使 JSON 和 SA 内容完全相同，ZIP 字节仍随日期变化，随后原子发布会替换已有 ZIP，带动下游。

修复显式创建 `ZipInfo`，使用已有 `build_utils.HERMETIC_TIMESTAMP`，再写入同一 JSON 内容。没有改 JSON 结构、条目名称、顺序、文件权限、压缩方式、GN 参数或依赖声明。此前生成的非空 ZIP 首次切换到固定时间后会更新一次，之后相同输入保持稳定。

- [增量补丁](evidence/20260915/sa-binary-metadata-timestamp.patch)
- 修复前快照：`39d308ae496827dade7891eb0e0c1f062d396e3c`
- 修复提交：`a764e585eaff2ec0089c1d17129ba0ee79a65a9a`
- 备份引用：`backup/sa-binary-before-20260915`
- 修复引用：`fix/sa-binary-metadata-timestamp-20260915`

修复提交的父提交是包含既有迁移修改的快照，**不能把该分支整体当成独立上游 PR 推送**。`format-patch -1` 仅包含本轮四行差异，可用于后续整理到适当基线。没有创建或更新 GitCode PR。

## 验证与保护

使用新仓实际生成器与公共工具函数，输入输出全部放在临时目录。通过模拟相隔一天的时钟避免 ZIP 两秒时间粒度掩盖问题，没有更改服务器时钟。

| 用例 | 修复前 | 修复后 |
| --- | --- | --- |
| 非空归档跨日期重复生成，哈希与 mtime 均保持 | 失败 | 通过 |
| 空归档重复生成 | 通过 | 通过 |
| SA 内容变化正确更新 | 通过 | 通过 |
| 输出删除后重新生成 | 通过 | 通过 |
| 输入丢失报错，保留原 ZIP 且清理临时输出 | 通过 | 通过 |
| 部件映射变化正确发布 | 通过 | 通过 |
| 条目内容、顺序、权限、压缩方式及已有依赖保持 | 通过 | 通过 |

测试脚本、完整前后日志和 Git 检查点见 [证据目录](evidence/20260915/README.md)。`py_compile` 与相对快照的 `git diff --check` 通过。独立临时索引校验了其他工作文件未变；实际索引 SHA 与 HEAD 均未变化，没有暂存或切换现有工作树。

本地恢复包：`D:/workspace/archives/bundles/20260915-sa-binary-review/build-review.bundle`。远端 `git bundle verify` 通过，传输前后 SHA-256 均为 `38b109480fdd9ecf9ee081b2cfcfa80dfe0dfbabb81f0c9796397fb26227a44c`。这是以前述新仓 build HEAD 为前提的增量 bundle，恢复时须已有该基线。

## 人工补验与约束

已读新仓 `build/AGENTS.md`、`docs/编译构建调试文档.md`、`docs/FAQ.md`、`docs/编译性能分析工具使用.md` 及既有修复交接。遵守公共模板与参数不变、不手改生成物、保留既有修改等约束。

依照既有[整仓构建人工执行约定](glm52-geninit-fix-handoff-20260901.md)，本轮没有启动 `build.sh`、`hb build`、GN 或真实 Ninja，性能套件也未执行。脚本回归通过不等于 build 仓整仓验收完成。

迁移缺口处理后，在 **新源码根目录** 人工连续执行两轮：

```bash
cd /srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code
./build.sh -p rk3568 --build-target make_all
```

每轮分别保存控制台、退出码、`out/rk3568/build.log` 和 `.ninja_log`，记录 `pwd -P`、各仓 HEAD 与补丁状态。第二轮前不改源码与配置。按实际日志核对原始十个 Action、早期三个独立 Action 及剩余 metadata/ramdisk，不用 dry-run 的计划执行数代替验收结果。非空 binary SA 的脚本用例仍须保留，因为默认产品可能继续生成空归档。
