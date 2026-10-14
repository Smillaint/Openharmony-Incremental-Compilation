# CSS 源文件和 fixture 的复制边补齐

将 CSS 目录复制拆成 9 个具体文件输出；fixture 目标采用 ohos_copy 并登记 innerkit，保留原公开 target 和 runtime/src 布局，修复跨组件生成输入可见性。

## 修改范围

仓库：`third_party/css-what`。

- `BUILD.gn`
- `bundle.json`

## 依赖与验证

与 js-out-only-build 配套；生产者先于消费者合入。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

实际产品 GN 图和完整 Ninja 编译通过，验证了生成文件可见性及跨组件 innerkit 依赖；JS 真实构建与43项单元测试通过，普通/独立复制回归通过。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/third_party_css-what/css-explicit-copy-outputs.patch)。
- 提交：`c8b2823a3bdadbfdf6cc7d0bacbf8ecf10208bb9`。
- 迁移基线：`95648987c034c15781137e727eb7b1dcff051140`。
- 远程准备引用：`refs/heads/review/css-explicit-copy-outputs-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
