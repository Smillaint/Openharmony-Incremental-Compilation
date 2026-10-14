### 相关的Issue
https://gitcode.com/openharmony/build/issues/4657

### 原因（目的、解决的问题等）
rk3568/phone 增量构建中的目标：
`//build/ohos/packages:sa_profile_src_phone`。

源 SA 元数据的聚合顺序可能变化，处理脚本和安装信息脚本在 JSON 内容不变时仍会覆盖输出，导致时间戳变化继续传到 SA 安装链。公共 JSON 变化检测使用字典字符串计算摘要，也会把对象键顺序差异误判为内容变化。

### 描述（做了什么，变更了什么）
1. `ohos/sa_profile/src_sa_profile_process.py`：按 label 排序元数据；生成 `src_sa_infos.json` 时启用内容变化检查。
2. `ohos/sa_profile/sa_profile_source.py`：生成源 SA 安装 JSON 时启用内容变化检查，内容不变时保留原文件和 mtime。
3. `scripts/util/file_utils.py`：比较解析后的 JSON 对象，忽略对象键顺序差异；数组顺序和真实数据变化仍参与比较。

本 PR 从旧 PR https://gitcode.com/openharmony/build/merge_requests/6965 中拆出源 SA Action 的三个文件，按 Action 单独评审；与旧 PR 的对应代码重叠，请勿重复合入。旧 PR 中 binary SA ZIP 和合并安装信息部分不在本次范围。

完整零改动增量中，该 Action 不执行还依赖上游 parts 元数据稳定化（build #6999、#7009）。上游元数据仍发生变化时，该 Action 继续执行属于正常依赖传播。

### 测试用例（新增、改动、可能影响的功能）
基于当前 master `86a670af8b35` 拆分，三个修复文件与已完成组合构建的版本一致。Python AST 和 git diff --check 通过；使用实际脚本及当前上游 helper 完成八项隔离回归：

1. 源部件筛选、平台命名、label 排序和工具链 depfile 正确。
2. 相同输入重复执行，两级 JSON 内容及纳秒级 mtime 均不变。
3. 调换 SA 元数据输入顺序，两级输出不重写。
4. JSON 对象键顺序变化不触发重写。
5. JSON 数组顺序变化仍触发更新。
6. 实际 SA 元数据变化能传到两级输出。
7. 源部件选择变化能更新安装列表。
8. 删除任一生成 JSON 后可恢复预期内容。

既有 rk3568/phone 组合修复曾从空 out 完成全量和连续两轮增量，均退出 0；两轮 `sa_profile_src_phone` 均未执行。组合构建完整耗时为 2105.50 / 154.81 / 87.77 秒，包含其他 Action 的配套修复，不能归为本 PR 单独收益。本拆分分支未重新执行独立整仓构建，社区门禁结果以本 PR 为准。

组合构建使用：
`bash ./build.sh -p rk3568 --build-target make_all --ninja-args=-dexplain`

### 是否需要同步至release分支？
- [ ] 是，需要同步的分支：
- [x] 否
理由：本次仅面向 master，其他分支需另行核对构建脚本及依赖版本。

### 是否需要刷新社区文档？
- [ ] 是，刷新社区文档pr链接：
- [x] 否
理由：仅调整构建脚本的增量输出行为，不改变对外接口或使用方式。

### 是否已执行L0用例
- [ ] 已验证
- [x] 不涉及。未修改产品运行时代码；已执行上述八项构建脚本回归，未宣称设备或 XTS 验证通过。
