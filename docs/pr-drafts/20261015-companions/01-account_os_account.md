### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
账户 IDL 的 callback 和公共类型头文件没有完整声明输出，生成关系不明确，清理产物后可能缺少头文件。

### 描述（做了什么，变更了什么）
在 frameworks_osaccount_interface 中声明 IDomainAccountCallback.idl 和 DomainAccountIpcData.idl 的输出，与 build 的 IDL 模板修复配套。

### 测试用例（新增、改动、可能影响的功能）
预期生成文件由明确的目标负责，清理后能重新生成，无改动时不因缺少输出声明重复构建。
