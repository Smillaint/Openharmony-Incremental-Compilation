# IDL 生成依赖和 clean 后恢复

IDL 模板补齐 client、callback、common 的具体输出并转发 deps；脚本递归跟踪 import，在 out/gen 临时目录生成，完整校验输出后按内容发布。删除生成文件后可以重建，失败保留原有效产物。

## 修改范围

仓库：`build`。

- `config/components/idl_tool/idl.gni`
- `config/components/idl_tool/idl.py`

## 依赖与验证

依赖已迁移的 IDL 命名及 common 区分修复（历史 build #6982 和缩写命名准备补丁）；与五个 IDL 消费仓协调合入。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

真实 IDL 隔离 Ninja 回归提取 141 条产品命令、生成 1,560 个输出；无改动为 no work，删除部分或全部输出后可恢复且再次无改动为 no work。模拟回归覆盖递归 import、声明输出不全与生成失败保留旧产物。未验证 Rust IDL、Windows/macOS SDK。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/build/idl-clean-outputs.patch)。
- 提交：`9cd1ddecf28acdd1d17ea59bdf094d5ce9458bcb`。
- 迁移基线：`8c899c6d333305fcff11bd35d7ec9752cd931a50`。
- 远程准备引用：`refs/heads/review/idl-clean-outputs-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
