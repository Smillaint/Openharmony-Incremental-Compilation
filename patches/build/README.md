# OpenHarmony Build PR 补丁

本目录保存从本地 GitCode fork 正式提交直接导出的完整补丁，不包含远程整仓验证分支或 packages 综合实验分支中的附加修改。

两个补丁共同基于：

```text
openharmony/build
69f5e3070cf7dd14868ddd93f031d3a0f69178ff
```

## SA Profile

```text
file:   sa-profile-incremental-0d530d7e.patch
branch: codex/fix-sa-profile-incremental-build
commit: 0d530d7eb691276cd27d7109b1155a21c6c0c1cc
PR:     https://gitcode.com/openharmony/build/merge_requests/6965
```

涉及文件：

```text
ohos/sa_profile/sa_profile_binary.py
ohos/sa_profile/sa_profile_merge.py
ohos/sa_profile/sa_profile_source.py
ohos/sa_profile/src_sa_profile_process.py
scripts/util/file_utils.py
```

## HAP signing

```text
file:   hap-signing-incremental-34aa8cba.patch
branch: fix-hap-sign-incremental-build
commit: 34aa8cba0c5fcb3344e2dd652c18027d69a71396
issue:  https://gitcode.com/openharmony/build/issues/4663
```

涉及文件：

```text
ohos/app/app_internal.gni
scripts/app_sign.py
scripts/compile_app.py
scripts/util/build_utils.py
```

## 应用方式

在相同基线的 `openharmony/build` 仓中选择一个补丁执行：

```bash
git status --short
git am /path/to/sa-profile-incremental-0d530d7e.patch
```

或：

```bash
git status --short
git am /path/to/hap-signing-incremental-34aa8cba.patch
```

不要把两个补丁和 `codex/packages-action-incremental-fix-20260805` 的实验提交一起批量移植。完整根因、验证结果和剩余方向见：

```text
docs/recent-build-prs-20260812.md
docs/current-project-handoff.md
```
