# JS 构建目录与 CSS 依赖修复

普通与独立构建均在 out 使用依赖副本；补齐具体 CSS/配置/测试输入，保留 GN 生成的 CSS 子树以避免同文件复制，分别等待构建和测试并传播失败；补齐 native 测试替身。

## 修改范围

仓库：`third_party/jsframework`。

- `BUILD.gn`
- `js_framework_build.sh`
- `test/ut/runtime.ts`

## 依赖与验证

与 css-explicit-copy-outputs 配套；先使 CSS fixture innerkit 可见，再提交消费者。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

隔离回归覆盖普通/独立与 prebuilts/npm fallback 四组合、同文件复制、mtime、缺失恢复及构建/测试失败传播；真实 Node/Babel 构建退出 0，43 项单元测试通过。现有 lint 日志仍有错误，未宣称 lint 通过。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/third_party_jsframework/js-out-only-build.patch)。
- 提交：`2380cf22dd9c92b3babfcfcd31cc781c83cb61d4`。
- 迁移基线：`22ddd05c7caf5fc3303a5ee207fe159ce154c238`。
- 远程准备引用：`refs/heads/review/js-out-only-build-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
