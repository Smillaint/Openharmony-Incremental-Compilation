# DLP IDL shared types 输出补齐

dlp_permission_interface 显式声明 DlpPermissionTypes.idl 的公共输出，避免 clean 后缺失生成头。

## 修改范围

仓库：`base/security/dlp_permission_service`。

- `interfaces/inner_api/dlp_permission/BUILD.gn`

## 依赖与验证

与 build 的 idl-clean-outputs 配套。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

该消费者纳入实际产品 GN 和空 out 全量验证；配套 IDL 回归覆盖141条真实命令、1,560个输出的部分/全部删除恢复。未改动 IDL 协议、生成类型或业务接口；未执行该业务模块设备测试。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/base_security_dlp_permission_service/dlp-idl-outputs.patch)。
- 提交：`6ac6b9f36f975b6903d67c541bd9e1be8196da5f`。
- 迁移基线：`b59001a8383d76f2708a3b0d525ae2fba538b24b`。
- 远程准备引用：`refs/heads/review/dlp-idl-outputs-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
