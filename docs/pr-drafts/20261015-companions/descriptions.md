# 配套 PR 描述确认稿

共 10 条新 PR。正文只说明触发原因、修改方式和预期结果；检查记录单独保存在交接文件。所有修复提交带 `Signed-off-by: Smillick <3185479846@qq.com>`。

## Issue 分组

| 分组 | 关联 Issue | 完整 PR 组 |
| --- | --- | --- |
| IDL | build #4668 | build #6982 + 账户、输入法、DLP、分布式能力、音频五条新 PR |
| JS/CSS | jsframework #323 | jsframework #853 + css-what 新 PR |
| SDK split | build #4706 | build #7049 + interface_sdk-js 新 PR |
| 安装上游补充 | build #4704 | build #7046 + ace_ets2bundle、graphic_3d 两条新 PR；三个仓各一条 |
| loader | 新建 build Issue | 一条新的 build PR，避免与 #7046 同仓同分支共用门禁 Issue |
| HAP | build #4663 | 现有 build #6974 + packing_tool #1556；将后者正式关联到 #4663，原 #1201 保留问题记录 |

原有 SA、NOTICE、parts、HiSysEvent、airscan、iptables 等 PR 继续沿用已有 Issue。每个联合组的 PR 创建、正式关联和 DCO 均检查齐后，在组内一条 PR 发送 `start build`。

## PR 正文

### 1. account_os_account：补齐账户 IDL 的 callback 和公共类型输出

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
账户 IDL 的 callback 和公共类型头文件没有完整声明输出，生成关系不明确，清理产物后可能缺少头文件。

### 描述（做了什么，变更了什么）
在 frameworks_osaccount_interface 中声明 IDomainAccountCallback.idl 和 DomainAccountIpcData.idl 的输出，与 build 的 IDL 模板修复配套。

### 测试用例（新增、改动、可能影响的功能）
预期生成文件由明确的目标负责，清理后能重新生成，无改动时不因缺少输出声明重复构建。


### 2. inputmethod_imf：补齐输入法 IDL 公共类型输出

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
InputMethodClientTypes.idl 的公共头文件只作为生成副产物，构建图没有完整记录，清理后可能出现缺文件。

### 描述（做了什么，变更了什么）
在 input_client_interface 中通过 sources_common 声明 InputMethodClientTypes.idl 的公共输出。

### 测试用例（新增、改动、可能影响的功能）
预期公共类型文件有明确的生成目标，清理后可恢复，输入不变时不再因输出缺项触发生成。


### 3. security_dlp_permission_service：补齐 DLP 权限 IDL 公共类型输出

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
DlpPermissionTypes.idl 的公共输出没有明确声明，依赖关系不完整，清理生成文件后可能编译失败。

### 描述（做了什么，变更了什么）
在 dlp_permission_interface 中通过 sources_common 声明 DlpPermissionTypes.idl。

### 测试用例（新增、改动、可能影响的功能）
预期公共头文件按依赖生成，清理后能恢复，无改动时保留已有生成结果。


### 4. ability_dmsfwk：补齐分布式能力 IDL 公共类型输出

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
DeviceConnectStatus.idl 的公共头文件没有完整的输出声明，后续目标依赖生成副产物，清理后可能缺少文件。

### 描述（做了什么，变更了什么）
在 dmsfwk_idl 中通过 sources_common 声明 DeviceConnectStatus.idl 的公共输出。

### 测试用例（新增、改动、可能影响的功能）
预期公共类型文件由对应 IDL 目标生成，清理后可以重建，无改动时不重复发布。


### 5. multimedia_audio_framework：补齐音频 IDL callback 的生成依赖

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4668

### 原因（目的、解决的问题等）
音频 callback 使用了另一 IDL 目标生成的共享类型，但没有依赖其生产者，清理后并行构建可能先使用尚未生成的文件。

### 描述（做了什么，变更了什么）
让 audio_service_idl_callback 显式依赖 audio_service_idl_interface，先生成共享类型，再处理 callback。

### 测试用例（新增、改动、可能影响的功能）
预期 clean 后按正确顺序恢复生成文件，无改动时不因依赖断链重复构建。


### 6. third_party_css-what：明确 CSS 源码和 fixture 的复制输出

### 相关的Issue
https://gitcode.com/openharmony/third_party_jsframework/issues/323

### 原因（目的、解决的问题等）
CSS 使用目录复制，没有逐项声明输出，fixture 也没有完整的跨部件接口，影响 JS 构建依赖判断和清理后的恢复。

### 描述（做了什么，变更了什么）
将源码和 fixture 分别声明为具体文件复制目标，保留 runtime/src 布局，并在 bundle.json 中导出 fixture innerkit。

### 测试用例（新增、改动、可能影响的功能）
预期 JS 构建能够跟踪实际 CSS 输入，无改动时不重复复制，清理后按依赖恢复所需文件。


### 7. interface_sdk-js：补齐 SDK 拆分和声明裁剪的增量依赖

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4706

### 原因（目的、解决的问题等）
SDK 拆分没有接入完成标记和 depfile；声明裁剪每轮复制文件并更新时间戳，导致下游反复判断输入变化。

### 描述（做了什么，变更了什么）
为拆分和声明裁剪接入 stamp、depfile，跟踪声明文件及裁剪规则。裁剪结果先生成到临时目录，内容相同时保留原输出；不带新参数的调用保留原有行为。

### 测试用例（新增、改动、可能影响的功能）
预期无改动时保留输出时间戳，声明或裁剪规则变化时正常更新，清理输出后能够恢复。


### 8. developtools_ace_ets2bundle：修复 SDK 插件和 wrapper 的重复构建

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4704

### 原因（目的、解决的问题等）
插件和 wrapper 在源码目录生成中间文件，目录形式的输入输出不能完整表达依赖；libarkts 输出也缺少隔离，容易引起重复构建，清理后可能缺少文件。

### 描述（做了什么，变更了什么）
将插件和 wrapper 放到 out 内构建，用具体文件清单声明输入输出并按内容发布，补齐 package.json 和工具依赖，隔离 libarkts 输出；清单包含主干新增的校验文件。

### 测试用例（新增、改动、可能影响的功能）
预期无改动时不重复发布 SDK 文件，清理 out 后可以恢复，源码目录不再产生这些构建中间文件。


### 9. graphic_graphic_3d：避免相同 ROFS 对象触发重复链接

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4704

### 原因（目的、解决的问题等）
资源编译每次直接替换 ROFS 对象，即使对象内容相同也会更新时间戳，继续触发共享库链接和安装。

### 描述（做了什么，变更了什么）
在构建目录的临时目录生成对象，检查输出后比较内容，仅替换有变化的文件。

### 测试用例（新增、改动、可能影响的功能）
预期相同对象保留时间戳，不再带动无效重链；对象被清理后能恢复，生成失败时保留已有有效对象。


### 10. build：保留未变化的 components.json

### 相关的Issue
https://gitcode.com/openharmony/build/issues/4761

### 原因（目的、解决的问题等）
loader 先删除 components.json 再写回，相同内容也会更新时间戳，内容变化检查无法生效；公共 JSON 比较还受字典键顺序影响。

### 描述（做了什么，变更了什么）
取消写回前的删除，使用 check_changes 比较后写入；公共 JSON 判断改为比较解析后的内容。

### 测试用例（新增、改动、可能影响的功能）
预期组件清单未变化时保留文件及时间戳，实际组件变化时正常更新，缺失的输出可由写入工具重新生成。


## loader 新 Issue 正文

### 发生了什么问题？
loader 裁剪组件清单时先删除 components.json，再写回相同内容，导致时间戳变化并继续影响下游增量判断。

### 期望行为是什么？
组件清单内容未变化时保留原文件和时间戳，实际组件变化时正常更新。

### 修改方式
取消写回前的删除，启用内容变化检查；JSON 按解析后的内容比较，避免仅字典键顺序不同触发重写。


## HAP 旧 PR 的关联调整

packing_tool #1556 的正式关联改为 https://gitcode.com/openharmony/build/issues/4663；正文的关联 Issue 字段同步为该地址，其余正文不变。packing_tool #1201 保留，不再作为该组的独立门禁入口。
