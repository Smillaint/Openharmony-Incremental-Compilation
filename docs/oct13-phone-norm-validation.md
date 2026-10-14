# 规范性修复恢复与实际编译验证

## 当前状态

2026-10-13（America/Los_Angeles）在主工作仓恢复此前保存的规范性修复，再修正实际编译暴露的 JS/CSS 依赖问题。远程日志使用 UTC，日期为 2026-10-14。raw 原始对照仓保持原样。

**attempt5 已通过真实 GN 并进入完整 Ninja 构建；全量、连续增量和 phone_install_modules 收敛结论尚待取得。** 每次 GN 失败后的主仓 out 均移动到独立归档，再从空 out 执行原产品命令。没有关闭 GN 依赖检查或修改产品参数。

## 本轮补充修改

| 仓库与文件 | 原因与修复 |
| --- | --- |
| jsframework：js_framework_build.sh | 源码 runtime/src 是 CSS 源码链接，GN 的复制结果可能是同源硬链接；原 cp -r -L 会把文件复制到自身并失败。普通构建仅复制 runtime 其余入口，保留 CSS 目标生成的 out/runtime/src；独立构建仍从 innerkit 副本复制。 |
| jsframework：BUILD.gn | 给 CSS 参数明确路径，补齐 9 个具体 CSS 输入；普通构建通过 external_deps 直接依赖两个生产者。 |
| css-what：BUILD.gn、bundle.json | 保留原 css_what_sources innerkit 及目录布局；fixture 目标使用 ohos_copy 并登记为 innerkit，声明两个具体文件输出。原主目标通过私有 deps 保证打包时包含 fixture；跨组件消费者直接引用公开目标，避免不合法 public_deps。 |
| build：ohos/packages/BUILD.gn | 将安装脚本实际读取的 arm64e 白名单与 categorized-libraries.json 补入 sources，确保规则变化会触发重新安装。 |

以上是在已恢复的 IDL 输出声明、out 内生成、JSON 稳定写入、SDK 文件清单与复制修复之上追加的 3 仓 5 文件修改，未新建 GitCode PR。前序变更见 [规范性修复](oct13-phone-audit-clean-recovery.md) 与 [GN 文件清单兼容](oct13-gn-sdk-manifest-repair.md)。

## 已完成检查

- JS 隔离回归覆盖旧同文件复制失败、普通/独立与 prebuilts/npm fallback 四组合、重复发布的 mtime、输出删除后恢复、缺失源码 CSS 链接、构建及测试失败传播；结果见 [回归记录](evidence/20261013-phone-norm-validation/js-css-regression.json)。
- 使用真实 Node/Babel/测试依赖运行 JS 构建，退出码 0，43 项单元测试通过；CSS 源码内容与 mtime 均未变化。现有 lint 日志仍有报错，不能将此次结果表述为 lint 通过。记录见 [真实 JS 构建](evidence/20261013-phone-norm-validation/js-real-build-status.json)。
- 真实 IDL 隔离 Ninja 回归：从本轮 GN 提取 141 条命令，生成 1,560 个输出；不变构建、部分输出删除后恢复、全部输出删除后恢复均通过，恢复后的不变构建均为 no work。源码未变化。使用 raw 仓已构建的同版 IDL 工具，不替代产品 GN 图和消费者编译验收；见 [逐轮记录](evidence/20261013-phone-norm-validation/idl-real-recovery-status.json) 与 [结果](evidence/20261013-phone-norm-validation/idl-real-recovery-passed.json)。
- attempt1 至 attempt4 的 GN 失败分别暴露生成文件可见性和 innerkit 声明约束；attempt5 改为直接 external_deps 后通过 GN；主 Ninja 的 gen_snapshot、ark_jsf、gen_ui_plugins 和 gen_sdk_ts_wrapper 已执行通过。
- 已保存修改前及每轮构建前的 16 仓 Git 快照，主仓 HEAD 和真实索引没有切换。恢复包内 Git bundle 校验通过。

## 安装动作验收边界

必须在全量成功后保持源码及参数不变，取得连续两轮 phone_install_modules 不执行的实际增量日志，不能沿用纯迁移版 169.92 秒或旧仓结果。

安装 depfile 仍有历史 HAP/资源目录依赖。不能仅删除目录项或改为一次性枚举后丢失新增/删除文件的触发条件。后续应从真实 Ninja explain 追踪根因，并在必要时联动生产者清单与安装消费关系。

## 构建与状态位置

```bash
cd /srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code
bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain
```

本轮运行器已启动时不要重复启动上述命令。运行目录由下列文件记录：

```text
/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/phone_norm_validation_20261013/latest-run.txt
```

对应目录的 status.json、runner.log、各阶段 console.log 和 summary.json 保存状态与计数。全量失败即停止；成功后依次执行最多三轮增量，保存原始十项及相关生成动作的次数。确认最终结论还需核对源码未变化和有效任务序列，不能仅依赖运行器结束状态。

## Git 与恢复

[本轮提交及文件清单](../patches/20261013-phone-norm-validation/versions.json) 中 before 是恢复后的规范版，after 是 attempt5 构建前快照。各仓 repair.patch 是两者之间的追加差异；cumulative.patch 是当前上游 HEAD 到该快照的完整差异，不能重复叠加使用。

- 远程归档目录：主工作目录旁 phone_norm_validation_20261013/source-delivery-attempt5。
- 本地恢复包：D:\workspace\archives\20261012-migration\source-delivery-attempt5.tar.gz。
- SHA-256：0b32e7f8ee8ef5888992ed71b2808ae0c502e814bb008fb649957a5f31501d96。
- [完整 16 仓版本](evidence/20261013-phone-norm-validation/all-repository-versions.json)。

A/B 控制器的 current 是此前缓存的规范版，不包含本轮追加差异；需要恢复本轮版本时使用上述 after 快照与补丁。切换前须停止构建并另存当前状态。
