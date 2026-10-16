### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
DeviceConnectStatus.idl 的公共头文件没有完整的输出声明，后续目标依赖生成副产物，清理后可能缺少文件。

### 描述（做了什么，变更了什么）
在 dmsfwk_idl 中通过 sources_common 声明 DeviceConnectStatus.idl 的公共输出。

### 测试用例（新增、改动、可能影响的功能）
预期公共类型文件由对应 IDL 目标生成，清理后可以重建，无改动时不重复发布。
