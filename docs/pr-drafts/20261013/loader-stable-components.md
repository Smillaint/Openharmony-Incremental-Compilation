# components.json 稳定发布

loader 不再先删除 components.json，改用 check_changes 保留相同内容的时间戳；构建参数缓存的消费方式不变。

## 修改范围

仓库：`build`。

- `hb/services/loader.py`

## 依赖与验证

依赖迁移版公共 JSON 语义比较；可与安装规则输入修复分别评审。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

JSON 回归验证语义相同保留 mtime、输出缺失后可恢复；最终产品 GN/load 和三轮 make_all 成功。参数缓存消费语义未更改。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/build/loader-stable-components.patch)。
- 提交：`05906cd0b9dbdffa00d62a7fdf8fed387427ccca`。
- 迁移基线：`8c899c6d333305fcff11bd35d7ec9752cd931a50`。
- 远程准备引用：`refs/heads/review/loader-stable-components-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
