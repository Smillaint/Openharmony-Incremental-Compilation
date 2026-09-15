# 9 月 6 日迁移复核与 SA ZIP 验证证据

- [复核交接](../../sep06-migration-review-20260915.md)
- [迁移状态与源码及日志哈希](migration-audit.json)
- [备份与修复提交信息](checkpoint.json)
- [SA 增量补丁](sa-binary-metadata-timestamp.patch)
- [七项隔离回归脚本](test_sa_binary_archive.py)
- [修复前结果 六项通过一项失败](regression-before.txt)
- [修复后结果 七项通过](regression-after.txt)

运行回归时传入完整源码根目录；脚本只在临时目录生成产物，不触发构建：

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python3 test_sa_binary_archive.py \
  --source-root /srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code
```

可加 `--baseline-file /srv/workspace/patch_backups/20260915_sa_binary_metadata_timestamp/sa_profile_binary.py.before` 重放保存的修复前源码；仍使用新仓的真实公共工具函数，不需要回退工作树。

迁移清单保存工作树状态和路径，不包含 node_modules 文件内容或凭据。完整 Git 增量 bundle 位于本地 `archives/bundles/20260915-sa-binary-review/` 和远端备份目录，不放入此证据目录。
