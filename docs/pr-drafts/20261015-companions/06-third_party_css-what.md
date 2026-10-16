### 相关的Issue
https://gitcode.com/openharmony/third_party_jsframework/issues/323

### 原因（目的、解决的问题等）
CSS 使用目录复制，没有逐项声明输出，fixture 也没有完整的跨部件接口，影响 JS 构建依赖判断和清理后的恢复。

### 描述（做了什么，变更了什么）
将源码和 fixture 分别声明为具体文件复制目标，保留 runtime/src 布局，并在 bundle.json 中导出 fixture innerkit。

### 测试用例（新增、改动、可能影响的功能）
预期 JS 构建能够跟踪实际 CSS 输入，无改动时不重复复制，清理后按依赖恢复所需文件。
