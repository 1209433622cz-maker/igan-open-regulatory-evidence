# R7B1D 预设对象与公开字节接入审计

## 对象冻结

R7B1D 的分析对象在当前 FinnGen 查询前由 R7B1B 代表性案例继承。三条 positive anchors 为 `R7B1_000258`、`R7B1_000410`、`R7B1_000411`；`R7B1_000414` 是 falsification anchor。对象、基因、细胞、PF10/PF50 状态和映射规则均写入 `R7B1D_external_target_registry.tsv`。本轮没有增加 OneK locus、gene 或 cell。

## API 字节

共请求 18 个当前公开对象，HTTP 200 为 18/18，有效 JSON 为 18/18。每个对象均记录 URL、UTC 时间、字节数和 SHA-256。接入包括 gene、peak、variant coloc、region coloc、region eQTL/caQTL、PBC regional GWAS、PBC Manhattan 与 phenotype autocomplete。

当前 `/api/finngen/phenos` 搜索索引返回零条 PBC 记录，但同一时点的 autocomplete、Manhattan、regional GWAS 和 disease-coloc endpoint 均正常返回 `CHIRBIL_PRIM`。因此病例数元数据沿用 R7B0 已冻结的公开返回值（760 cases、372,273 controls），而本轮 disease/eQTL 结果全部来自当前重新下载的字节。这一异常被显式记录，未用空搜索结果覆盖直接 endpoint 证据。

## 细胞映射

- OneK `NK` → FinnGen `l2.NK` primary，`l1.NK`/`l1.PBMC` compatible。
- OneK `B_IN` → FinnGen `l2.B_intermediate` primary，`l1.B` compatible。
- OneK `B_MEM` → FinnGen `l2.B_memory` primary，`l1.B` compatible；当前 FCRL3 eQTL region response 没有 `l2.B_memory`，所以只能使用 coarse B compatibility，不能写成 exact memory-B replication。
- OneK `CD8_ET` → FinnGen `l2.CD8_TEM`/`l1.CD8_T`，仅作为已冻结反例的 coverage audit，不能因外部 eQTL 强度被升级。

## 可重复性边界

CASCADE 是公开 aggregate output。个体级 FinnGen genotype/LD 没有进入本轮，故本轮不能复现 FinnGen 内部 SuSiE 或重新构建 source-matched LD。当前使用官方公开 fine-mapping/coloc 输出，并以原始 JSON、checksum 和解析代码保持可审计性。
