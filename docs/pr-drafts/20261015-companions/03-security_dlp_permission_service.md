### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
DlpPermissionTypes.idl 的公共输出没有明确声明，依赖关系不完整，清理生成文件后可能编译失败。

### 描述（做了什么，变更了什么）
在 dlp_permission_interface 中通过 sources_common 声明 DlpPermissionTypes.idl。

### 测试用例（新增、改动、可能影响的功能）
预期公共头文件按依赖生成，清理后能恢复，无改动时保留已有生成结果。
