# 音频 IDL callback 生产者依赖补齐

audio_service_idl_callback 显式依赖 audio_service_idl_interface，共享类型由明确生产者先生成，避免 clean 后抢跑或重复发布。

## 修改范围

仓库：`foundation/multimedia/audio_framework`。

- `services/audio_service/idl/BUILD.gn`

## 依赖与验证

与 build 的 idl-clean-outputs 配套。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

该消费者纳入实际产品 GN 和空 out 全量验证；配套 IDL 回归覆盖141条真实命令、1,560个输出的部分/全部删除恢复。未改动 IDL 协议、生成类型或业务接口；未执行该业务模块设备测试。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/foundation_multimedia_audio_framework/audio-idl-dependency.patch)。
- 提交：`975f1696a0696619b3b17ab726048aa46c64e6c3`。
- 迁移基线：`e811e639cbfe67ba7293d0c74d09aa8941aa4447`。
- 远程准备引用：`refs/heads/review/audio-idl-dependency-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
