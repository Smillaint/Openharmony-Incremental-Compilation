# 安装规则文件依赖补齐

将 system_arm64e_whitelist.json 和 categorized-libraries.json 加入平台安装动作 sources。规则文件变化会正确触发安装，不再漏依赖。

## 修改范围

仓库：`build`。

- `ohos/packages/BUILD.gn`

## 依赖与验证

沿用历史 build #7046、#6999 安装修复；本补丁不替代 ROFS 和 SDK 上游修复。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

静态依赖检查和实际 GN/full/incremental 编译通过；新增输入均为安装脚本读取的具体文件。未单独执行两份规则内容变化的整仓重建实验。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/build/install-rule-inputs.patch)。
- 提交：`c672e7f7dbc80cb9c7dd55fdff887ecd09720160`。
- 迁移基线：`8c899c6d333305fcff11bd35d7ec9752cd931a50`。
- 远程准备引用：`refs/heads/review/install-rule-inputs-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
