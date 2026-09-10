# GitCode PR diff 核对证据（2026-09-10）

通过 GitCode 公开只读 API 查询 13 个已知 PR 的详情与 files 接口。JSON 保存查询时间、来源 URL、状态、HEAD/base、文件路径、增删行统计、源码链接和接口返回的 diff；不含凭据。

代码说明以对应 HEAD 的实际 diff 为准；状态仅代表 retrieved_at 时刻。本目录不是构建日志，也不证明门禁或独立分支整仓验证通过。

每个 PR 的文件列表少于 100 项，使用 files 接口第一页（per_page=100）；逐文件检查 diff 非空且 too_large=false。以下 SHA-256 对应归档 JSON 文件，便于后续核对。

| PR | HEAD | 状态 | 可直接合并 | 文件数 | diff 快照 |
| --- | --- | --- | --- | --- | --- |
| [build #6965](https://gitcode.com/openharmony/build/merge_requests/6965) | `0d530d7e` | open | true | 5 | [build-6965.json](build-6965.json) |
| [build #6974](https://gitcode.com/openharmony/build/merge_requests/6974) | `34aa8cba` | open | true | 4 | [build-6974.json](build-6974.json) |
| [build #6982](https://gitcode.com/openharmony/build/merge_requests/6982) | `4fa37075` | open | true | 1 | [build-6982.json](build-6982.json) |
| [build #6999](https://gitcode.com/openharmony/build/merge_requests/6999) | `f1a46334` | open | true | 20 | [build-6999.json](build-6999.json) |
| [build #7006](https://gitcode.com/openharmony/build/merge_requests/7006) | `3dc5695a` | open | true | 2 | [build-7006.json](build-7006.json) |
| [build #7009](https://gitcode.com/openharmony/build/merge_requests/7009) | `edc427a8` | open | true | 4 | [build-7009.json](build-7009.json) |
| [build #7046](https://gitcode.com/openharmony/build/merge_requests/7046) | `5be8fa47` | open | true | 2 | [build-7046.json](build-7046.json) |
| [build #7048](https://gitcode.com/openharmony/build/merge_requests/7048) | `6840a0ba` | open | true | 2 | [build-7048.json](build-7048.json) |
| [build #7049](https://gitcode.com/openharmony/build/merge_requests/7049) | `72115384` | open | true | 1 | [build-7049.json](build-7049.json) |
| [developtools_packing_tool #1556](https://gitcode.com/openharmony/developtools_packing_tool/merge_requests/1556) | `dcbbc78a` | open | true | 1 | [developtools_packing_tool-1556.json](developtools_packing_tool-1556.json) |
| [third_party_iptables #62](https://gitcode.com/openharmony/third_party_iptables/merge_requests/62) | `5b884558` | open | true | 1 | [third_party_iptables-62.json](third_party_iptables-62.json) |
| [third_party_jsframework #853](https://gitcode.com/openharmony/third_party_jsframework/merge_requests/853) | `a280a42f` | open | true | 1 | [third_party_jsframework-853.json](third_party_jsframework-853.json) |
| [third_party_sane-airscan #22](https://gitcode.com/openharmony/third_party_sane-airscan/merge_requests/22) | `37de4f97` | open | false | 2 | [third_party_sane-airscan-22.json](third_party_sane-airscan-22.json) |

## openharmony/build #6965

查询时间：`2026-09-10T17:11:03.2264142+08:00`；HEAD：`0d530d7eb691276cd27d7109b1155a21c6c0c1cc`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6965)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6965/files?per_page=100&page=1)。

归档 SHA-256：`238135eea5ebc0119bc6fe5f5431780f831d336bfb5f3c1f19abb1dceffce799`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [ohos/sa_profile/sa_profile_binary.py](https://gitcode.com/openharmony/build/blob/0d530d7eb691276cd27d7109b1155a21c6c0c1cc/ohos/sa_profile/sa_profile_binary.py) | +11 / -9 |
| [ohos/sa_profile/sa_profile_merge.py](https://gitcode.com/openharmony/build/blob/0d530d7eb691276cd27d7109b1155a21c6c0c1cc/ohos/sa_profile/sa_profile_merge.py) | +2 / -1 |
| [ohos/sa_profile/sa_profile_source.py](https://gitcode.com/openharmony/build/blob/0d530d7eb691276cd27d7109b1155a21c6c0c1cc/ohos/sa_profile/sa_profile_source.py) | +2 / -1 |
| [ohos/sa_profile/src_sa_profile_process.py](https://gitcode.com/openharmony/build/blob/0d530d7eb691276cd27d7109b1155a21c6c0c1cc/ohos/sa_profile/src_sa_profile_process.py) | +4 / -2 |
| [scripts/util/file_utils.py](https://gitcode.com/openharmony/build/blob/0d530d7eb691276cd27d7109b1155a21c6c0c1cc/scripts/util/file_utils.py) | +3 / -13 |

## openharmony/build #6974

查询时间：`2026-09-10T17:11:04.7751042+08:00`；HEAD：`34aa8cba0c5fcb3344e2dd652c18027d69a71396`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6974)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6974/files?per_page=100&page=1)。

归档 SHA-256：`ca8d0c285cd0a44c526b2401a1a59373ce020a055d2219779de0625a890cdcd2`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [ohos/app/app_internal.gni](https://gitcode.com/openharmony/build/blob/34aa8cba0c5fcb3344e2dd652c18027d69a71396/ohos/app/app_internal.gni) | +4 / -1 |
| [scripts/app_sign.py](https://gitcode.com/openharmony/build/blob/34aa8cba0c5fcb3344e2dd652c18027d69a71396/scripts/app_sign.py) | +11 / -0 |
| [scripts/compile_app.py](https://gitcode.com/openharmony/build/blob/34aa8cba0c5fcb3344e2dd652c18027d69a71396/scripts/compile_app.py) | +10 / -3 |
| [scripts/util/build_utils.py](https://gitcode.com/openharmony/build/blob/34aa8cba0c5fcb3344e2dd652c18027d69a71396/scripts/util/build_utils.py) | +22 / -0 |

## openharmony/build #6982

查询时间：`2026-09-10T17:11:06.414095+08:00`；HEAD：`4fa37075bfa8a0f3bb36f0394adf54577b0770f2`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6982)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6982/files?per_page=100&page=1)。

归档 SHA-256：`e90074bfd59e280982bbd7c42ea00a489541120f8067952c8894d9448b746a37`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [config/components/idl_tool/idl.gni](https://gitcode.com/openharmony/build/blob/4fa37075bfa8a0f3bb36f0394adf54577b0770f2/config/components/idl_tool/idl.gni) | +8 / -8 |

## openharmony/build #6999

查询时间：`2026-09-10T17:11:08.1353052+08:00`；HEAD：`f1a463340efbcaa8089df8f47e50409c14ee9322`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6999)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/6999/files?per_page=100&page=1)。

归档 SHA-256：`e2084fa4ddd931d3a7fe4a04e675dda9ced9320dba4dc2e13746ce5ec5ec9a7e`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [config/components/idl_tool/idl.gni](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/config/components/idl_tool/idl.gni) | +8 / -8 |
| [ohos/app/app_internal.gni](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/app/app_internal.gni) | +4 / -1 |
| [ohos/common/BUILD.gn](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/common/BUILD.gn) | +19 / -2 |
| [ohos/common/generate_host_info.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/common/generate_host_info.py) | +54 / -0 |
| [ohos/common/merge_all_subsystem.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/common/merge_all_subsystem.py) | +2 / -1 |
| [ohos/packages/BUILD.gn](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/packages/BUILD.gn) | +67 / -6 |
| [ohos/packages/check_seccomp_library_name.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/packages/check_seccomp_library_name.py) | +52 / -14 |
| [ohos/packages/generate_host_symlink.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/packages/generate_host_symlink.py) | +53 / -22 |
| [ohos/packages/modules_install.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/packages/modules_install.py) | +9 / -6 |
| [ohos/packages/parts_install_info.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/packages/parts_install_info.py) | +2 / -1 |
| [ohos/packages/process_field_validate.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/packages/process_field_validate.py) | +92 / -25 |
| [ohos/packages/stabilize_json_file.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/packages/stabilize_json_file.py) | +41 / -0 |
| [ohos/sa_profile/sa_profile_binary.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/sa_profile/sa_profile_binary.py) | +11 / -9 |
| [ohos/sa_profile/sa_profile_merge.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/sa_profile/sa_profile_merge.py) | +2 / -1 |
| [ohos/sa_profile/sa_profile_source.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/sa_profile/sa_profile_source.py) | +2 / -1 |
| [ohos/sa_profile/src_sa_profile_process.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/ohos/sa_profile/src_sa_profile_process.py) | +4 / -2 |
| [scripts/app_sign.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/scripts/app_sign.py) | +11 / -0 |
| [scripts/compile_app.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/scripts/compile_app.py) | +10 / -3 |
| [scripts/util/build_utils.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/scripts/util/build_utils.py) | +22 / -0 |
| [scripts/util/file_utils.py](https://gitcode.com/openharmony/build/blob/f1a463340efbcaa8089df8f47e50409c14ee9322/scripts/util/file_utils.py) | +3 / -13 |

## openharmony/build #7006

查询时间：`2026-09-10T17:11:09.6858598+08:00`；HEAD：`3dc5695a126e2c9b3de9336ad8a290d2b66c8d29`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7006)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7006/files?per_page=100&page=1)。

归档 SHA-256：`6f19aceb5289189a7c3484739d303b5cee82d3047920c7ac25f8e68440e5e4cb`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [hb/util/loader/load_ohos_build.py](https://gitcode.com/openharmony/build/blob/3dc5695a126e2c9b3de9336ad8a290d2b66c8d29/hb/util/loader/load_ohos_build.py) | +5 / -1 |
| [ohos/hisysevent/hisysevent_process.py](https://gitcode.com/openharmony/build/blob/3dc5695a126e2c9b3de9336ad8a290d2b66c8d29/ohos/hisysevent/hisysevent_process.py) | +3 / -1 |

## openharmony/build #7009

查询时间：`2026-09-10T17:11:11.2359373+08:00`；HEAD：`edc427a875e5c0642e31c7b3dca4f7a8b0219b71`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7009)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7009/files?per_page=100&page=1)。

归档 SHA-256：`a1618196773a410a73917ca38b061ac6bcc7874fb5d20196bced0dff36eebfec`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [ohos/generate_part_info.py](https://gitcode.com/openharmony/build/blob/edc427a875e5c0642e31c7b3dca4f7a8b0219b71/ohos/generate_part_info.py) | +6 / -3 |
| [ohos/packages/BUILD.gn](https://gitcode.com/openharmony/build/blob/edc427a875e5c0642e31c7b3dca4f7a8b0219b71/ohos/packages/BUILD.gn) | +14 / -3 |
| [ohos/packages/parts_install_info.py](https://gitcode.com/openharmony/build/blob/edc427a875e5c0642e31c7b3dca4f7a8b0219b71/ohos/packages/parts_install_info.py) | +2 / -1 |
| [scripts/util/file_utils.py](https://gitcode.com/openharmony/build/blob/edc427a875e5c0642e31c7b3dca4f7a8b0219b71/scripts/util/file_utils.py) | +3 / -13 |

## openharmony/build #7046

查询时间：`2026-09-10T17:11:12.7294404+08:00`；HEAD：`5be8fa471e23084eb4a884653746a55af554e7f2`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7046)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7046/files?per_page=100&page=1)。

归档 SHA-256：`6ca9594187ff23f5bba309d75cb6236370598ed0b401ad9b15fec2b764d5cd62`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [ohos/common/binary_install_info.py](https://gitcode.com/openharmony/build/blob/5be8fa471e23084eb4a884653746a55af554e7f2/ohos/common/binary_install_info.py) | +3 / -2 |
| [ohos/packages/modules_install.py](https://gitcode.com/openharmony/build/blob/5be8fa471e23084eb4a884653746a55af554e7f2/ohos/packages/modules_install.py) | +1 / -1 |

## openharmony/build #7048

查询时间：`2026-09-10T17:11:14.2667934+08:00`；HEAD：`6840a0ba024b40ca67d0ab26aceee2a3458e7dbd`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7048)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7048/files?per_page=100&page=1)。

归档 SHA-256：`c3e13e1c736da2fbb3b4db88e3adda974b2571cc5b06948e5178a1e6b40cb796`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [ohos/notice/collect_module_notice_file.py](https://gitcode.com/openharmony/build/blob/6840a0ba024b40ca67d0ab26aceee2a3458e7dbd/ohos/notice/collect_module_notice_file.py) | +2 / -2 |
| [ohos/notice/collect_system_notice_files.py](https://gitcode.com/openharmony/build/blob/6840a0ba024b40ca67d0ab26aceee2a3458e7dbd/ohos/notice/collect_system_notice_files.py) | +0 / -1 |

## openharmony/build #7049

查询时间：`2026-09-10T17:11:15.745491+08:00`；HEAD：`72115384f783e09832216c951e7743b944fd5893`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7049)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/build/pulls/7049/files?per_page=100&page=1)。

归档 SHA-256：`8d656a3f6198a6142c0c1e7dd5c9a852451b79f6beb2421041bff27e77138c2f`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [ohos/sdk/parse_interface_sdk.py](https://gitcode.com/openharmony/build/blob/72115384f783e09832216c951e7743b944fd5893/ohos/sdk/parse_interface_sdk.py) | +58 / -0 |

## openharmony/developtools_packing_tool #1556

查询时间：`2026-09-10T17:11:18.996366+08:00`；HEAD：`dcbbc78ada8c90cb31542ecc385bb7d5b5faddbc`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/developtools_packing_tool/pulls/1556)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/developtools_packing_tool/pulls/1556/files?per_page=100&page=1)。

归档 SHA-256：`19bee6a5dbdd15a04f52d575e374a24d7113a2715e04523fce95032248d253db`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [adapter/ohos/Compressor.java](https://gitcode.com/openharmony/developtools_packing_tool/blob/dcbbc78ada8c90cb31542ecc385bb7d5b5faddbc/adapter/ohos/Compressor.java) | +9 / -1 |

## openharmony/third_party_iptables #62

查询时间：`2026-09-10T17:11:17.3892753+08:00`；HEAD：`5b884558dcc2c9e4b380edf8ef5aeaea8740cb0c`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/third_party_iptables/pulls/62)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/third_party_iptables/pulls/62/files?per_page=100&page=1)。

归档 SHA-256：`aaab0235cc4c19bb716e63a79f5cc43ee9a3998b4cb1c17fb2cc5026fea4af2c`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [extensions/genInit.py](https://gitcode.com/openharmony/third_party_iptables/blob/5b884558dcc2c9e4b380edf8ef5aeaea8740cb0c/extensions/genInit.py) | +13 / -5 |

## openharmony/third_party_jsframework #853

查询时间：`2026-09-10T17:11:20.5123532+08:00`；HEAD：`a280a42fe7f73d59528ecbde04f319cc61e5de0b`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/third_party_jsframework/pulls/853)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/third_party_jsframework/pulls/853/files?per_page=100&page=1)。

归档 SHA-256：`4421de3db97a66e77009d12f806a03f86b49c7807b42d2bd5f5135e41a57b25d`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [js_framework_build.sh](https://gitcode.com/openharmony/third_party_jsframework/blob/a280a42fe7f73d59528ecbde04f319cc61e5de0b/js_framework_build.sh) | +18 / -1 |

## openharmony/third_party_sane-airscan #22

查询时间：`2026-09-10T17:11:22.1119206+08:00`；HEAD：`37de4f97f4f4be0f19cda483b7202fcd34efc28a`。

来源：[PR API](https://api.gitcode.com/api/v5/repos/openharmony/third_party_sane-airscan/pulls/22)、[文件 diff API](https://api.gitcode.com/api/v5/repos/openharmony/third_party_sane-airscan/pulls/22/files?per_page=100&page=1)。

归档 SHA-256：`07e04a17f74c1aed6744db74a09f350537aeab2c08630ba2466bb052b07cbaf1`。

| 文件 | 新增 / 删除 |
| --- | --- |
| [BUILD.gn](https://gitcode.com/openharmony/third_party_sane-airscan/blob/37de4f97f4f4be0f19cda483b7202fcd34efc28a/BUILD.gn) | +63 / -50 |
| [patch_install.py](https://gitcode.com/openharmony/third_party_sane-airscan/blob/37de4f97f4f4be0f19cda483b7202fcd34efc28a/patch_install.py) | +125 / -21 |
