# ROFS 对象按内容发布

CompilerAsset.sh 在构建目录的独立临时目录生成对象，校验实际输出后比较发布。相同内容保留 mtime，缺失文件或目录能恢复，失败保留旧对象，阻断五个库的无效重链及 phone_install_modules 重跑。

## 修改范围

仓库：`foundation/graphic/graphic_3d`。

- `lume/LumeEngine/tools/CompilerAsset.sh`

## 依赖与验证

保留编译器参数、对象格式、资源内容、插件 UID 与 API/ABI；可独立评审。

组合源码在 rk3568/phone 使用原 make_all 命令从空 out 完成全量，随后两轮增量均退出 0；两轮原始十项 Action 均未执行，无共享库重链。完整耗时分别为 2,105.50、154.81、87.77 秒。这是组合验证，不表示本独立分支已单独整仓编译；移植到当前目标分支后仍需执行对应门禁。

6 个真实产品 ROFS 对象重复生成保持 mtime，删除对象或输出目录可恢复，冷构建结果与原产品字节一致。资产变化会更新对象；编译失败或缺少输出保留旧对象；输入输出同目录回归通过。未修改图形运行时代码，未执行设备画面、XTS 或 fuzz。

## 准备版本

- 补丁：[format-patch](../../../patches/20261013-source-handoff/foundation_graphic_graphic_3d/rofs-stable-publication.patch)。
- 提交：`faeddc68c9dc29eea314b29279348b16b12a2e27`。
- 迁移基线：`14146052f5fcc96d1619fc31cbe8663cdcdcc3de`。
- 远程准备引用：`refs/heads/review/rofs-stable-publication-20261013`。
- 提交签名：`Signed-off-by: Smillick <3185479846@qq.com>`。

该提交以保存的迁移快照为父提交。正式 PR 应从对应仓最新目标分支建立独立分支，核对先决修复后应用补丁；不能直接推送本准备分支的整条快照历史。当前尚未创建新 GitCode PR。
