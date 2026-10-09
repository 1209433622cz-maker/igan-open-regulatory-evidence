# R7B1D FinnGen PBC–IL12RB2 与 FCRL3 终裁

## IL12RB2–NK

`CHIRBIL_PRIM` 与 IL12RB2 eQTL 共定位记录共 3 条。数值如下：

| FinnGen cell | PP.H4.abf | CS overlap | GWAS CS size | eQTL CS size |
|---|---:|---:|---:|---:|
| l1.NK | 0.9703 | 9 | 19 | 9 |
| l1.PBMC | 0.9706 | 5 | 19 | 5 |
| l2.NK | 0.9698 | 5 | 19 | 5 |

这些记录支持外部 PBC–IL12RB2 signal sharing。它们来自 FinnGen R12 disease GWAS 与同一 FinnGen multiome 资源的 eQTL，不应被称为第二套 OneK source-LD proof。

在 chromatin 层，IL12RB2 top variant `chr1_67307966_T_C` 被 CASCADE 标记为 `Positional Cascade (overlap link)`：变异落在 peak `chr1-67307618-67308670` 内，该 peak 通过 fasthurdle 与 IL12RB2 相连，且该 peak 在 NK 中具备显著 caQTL。关键限制是该变异不在 peak caQTL credible set 中；当前也没有建立 PBC–caQTL signal-level colocalization。因此允许写“linked positional chromatin layer”，禁止写“完整调控级联已证实”。

## FCRL3–B

FCRL3 gene API 显示 `l1.B`、`l2.B_intermediate` 及 CD8 细胞中的强 eQTL，但 FCRL3 marginal lead、历史 anchor 与扩展 region coloc 三类查询均未返回 `CHIRBIL_PRIM–FCRL3` pair。FCRL3 也没有 gene-level CASCADE top variant。由此形成的结论是：

> FCRL3–B 获得 OneK–TenK 跨 molecular-QTL 资源复制，但本轮没有 FinnGen PBC disease-coloc 支持。

这不否定 FCRL3，也不允许用非 PBC trait 的高 PP.H4 替代 PBC evidence。

## CD8_ET 反例

FinnGen 的 FCRL3 CD8 eQTL 不能改变 R7B1B 的信号级判断。`R7B1_000414` 在 PF10 source-matched multi-signal 模型中为 H3-supported，而 PF50 会改变模型结论；它仍然是 covariate/LD model sensitivity 和 single-causal over-assignment 的代表性反例。强 QTL 存在本身不构成 disease–QTL shared signal。
