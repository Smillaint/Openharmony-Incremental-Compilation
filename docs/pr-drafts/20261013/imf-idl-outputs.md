# 输入法 IDL shared types 输出补齐

input_client_interface 显式声明 InputMethodClientTypes.idl 的公共输出，使 clean 后生产者与消费者关系完整。

## 修改范围

仓库：`base/inputmethod/imf`。

- `interfaces/inner_api/inputmethod_controller/BUILD.gn`

## 依赖与验证

与 build 的 idl-clean-outputs 配套。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

该消费者纳入实际产品 GN 和空 out 全量验证；配套 IDL 回归覆盖141条真实命令、1,560个输出的部分/全部删除恢复。未改动 IDL 协议、生成类型或业务接口；未执行该业务模块设备测试。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/base_inputmethod_imf/imf-idl-outputs.patch)。
- 提交：`eb9b91efa291227540a3a918c0a17914f91fe4d6`。
- 迁移基线：`5f5e6178a1d5b56331dae7af12ec3fca083857f5`。
- 远程准备引用：`refs/heads/review/imf-idl-outputs-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
