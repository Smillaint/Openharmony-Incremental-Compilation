### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
InputMethodClientTypes.idl 的公共头文件只作为生成副产物，构建图没有完整记录，清理后可能出现缺文件。

### 描述（做了什么，变更了什么）
在 input_client_interface 中通过 sources_common 声明 InputMethodClientTypes.idl 的公共输出。

### 测试用例（新增、改动、可能影响的功能）
预期公共类型文件有明确的生成目标，清理后可恢复，输入不变时不再因输出缺项触发生成。
