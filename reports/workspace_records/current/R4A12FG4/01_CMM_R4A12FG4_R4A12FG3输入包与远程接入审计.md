# CMM R4A12FG4：R4A12FG3 输入包与远程接入审计

## 输入包完整性

用户提供的 R4A12FG3 ZIP SHA-256 为 `5919df5762886f0e2256a2ad914e586d693ecb54e7d6de84c9f1e29d7d294175`，ZIP CRC PASS。`checksums.sha256` 的 17/17 个对象全部独立重算 PASS，9 个 standalone 附件与包内对应文件逐字节一致。

包内 `R4A12FG3_release_validation.json` 写成 `checksums_verified=16`，实际 manifest 有 17 行。这是计数错误，不改变内容完整性。原下载脚本直接写最终 `.zip` 路径，缺少 `.part`、远端长度前检、原子晋升和机器可读 receipt；原提取器按任意字段搜索基因、直接写最终输出，且未记录成员 CRC/输出哈希。两者已作为历史快照保存，当前入口已替换。

## Zenodo 独立实测

官方记录 18221260 的 API 返回 `common_all_cis_pvalues_100kb.zip` 大小 16,559,137,990 字节、MD5 `dd54714b2effb91160ac171ccb941534`。HEAD 和 Range 均实测 PASS。通过 ZIP64 尾部中央目录，仅传输少量字节即确定 28 个成员；NK 成员 local header offset=11,749,190,239，压缩大小 556,881,415，展开大小 2,272,841,254，CRC32=`25f9b199`。

1 MiB 局部成员探针直接解压出真实 header，确认 `BETA` 与 `SE` 存在。完整选择性下载随后以 67 个 8 MiB 以内的块、4 个并发连接完成，所有块写 `.part` 后原子改名，支持同命令续传。

## 完整性边界

本轮验证的是完整 NK 成员 CRC，不是整个 16.56 GB ZIP 的 provider MD5。其他 27 个成员没有下载，因此不得宣称整包 MD5 已验证。
