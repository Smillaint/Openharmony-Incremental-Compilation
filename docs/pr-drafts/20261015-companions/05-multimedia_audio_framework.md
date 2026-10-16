### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
音频 callback 使用了另一 IDL 目标生成的共享类型，但没有依赖其生产者，清理后并行构建可能先使用尚未生成的文件。

### 描述（做了什么，变更了什么）
让 audio_service_idl_callback 显式依赖 audio_service_idl_interface，先生成共享类型，再处理 callback。

### 测试用例（新增、改动、可能影响的功能）
预期 clean 后按正确顺序恢复生成文件，无改动时不因依赖断链重复构建。
