# CMM R3 — 行动记录与下一阶段目标

**日期**：2026-09-05  
**阶段**：R3 Data & Novelty Preflight  
**上一阶段**：R2 TOP1 SSc project blueprint

---

## 1. 本轮实际完成

### A. 核查2026 sex-specific SSc GWAS
- 确认论文发表信息；
- 确认样本量；
- 确认8个sex-specific loci的总体结果；
- 确认论文已经完成大量功能注释、coloc、sex-DEG和drug repurposing；
- 确认Data Availability承诺向GWAS Catalog提供summary stats；
- 多路径搜索未能在本轮确认对应GCST accession；
- 将此问题提升为R4A硬门。

### B. 核查FinnGen next-generation multiome QTL资源
- 确认官方public release日期：2026-08-13；
- 确认1,108 donors、33 cell types；
- 确认eQTL/caQTL/SuSiE/peak-gene/CASCADE均在release范围；
- 确认访问需要online form + email instructions；
- 将其状态从R2“高潜力资源”升级为“可启动主discovery资源”。

### C. 核查replication资源
- TenK10K 1,925 donors / 28 immune cells / open Zenodo eQTL stats；
- OneK1K作为第三层/legacy replication；
- 明确TenK10K本身已有大规模MR atlas，所以不再用泛MR作为创新中心。

### D. 重构SSc disease tissue层
- 确认 GSE312129 为当前最强主疾病组织multiome；
- 确认 10 SSc + 4 HC，SSc 7F/3M；
- 确认 snRNA+snATAC + SSc Visium；
- 确认 raw ~54.3GB；
- 将 GSE249279 定为独立skin replication；
- 将 GSE236111 定为IFN/endothelial定向小样本验证；
- 将 GSE312932 定为高分辨空间后置层；
- 修正 GSE312591：不是主SSc atlas，而是RUNX1 perturbation条件性证据。

### E. 同构论文排雷
确认已有：
- 2026 sex SSc functional genetics；
- SSc skin multiome + spatial；
- SSc-ILD lung multiome；
- old SSc GWAS × cell ATAC overlap；
- population multiome CASCADE；
- TenK10K causal sc-eQTL atlas；
- context-dependent single-cell eQTL；
- tissue-resident immune eQTL。

由此重新冻结创新边界。

---

## 2. 本轮关键纠错

### 纠错1
“文章说stats会公开” ≠ “我们的workflow已有stats”。

### 纠错2
SSc skin multiome已不是创新本身。

### 纠错3
GSE312591不是case-control disease atlas。

### 纠错4
GSE312129虽然有7F/3M，但不能因为包含两性就做强sex-interaction结论。

### 纠错5
MR应从主引擎降级为支持性分析；否则容易与2025–2026大量sc-eQTL MR论文同质化。

---

## 3. 当前项目状态标签

```text
PROJECT = SSc_SexBiased_RegulatoryCascade
R3 = COMPLETE
NOVELTY = PASS_WITH_NARROWED_CLAIM
DATA_ECOSYSTEM = PASS
SEX_GWAS_ACCESS = PENDING_HARD_GATE
FINNGEN_ACCESS = PUBLIC_MANUAL_ACCESS
TISSUE_VALIDATION = PASS
FULL_ANALYSIS = NOT_YET_AUTHORIZED
NEXT = R4A
```

---

# 4. 下一阶段：R4A — Access, Harmonization & 3-Locus Smoke Test

## R4A目标
在尽可能少的数据下载和计算投入下回答：

> **这条论文最核心的遗传调控链真的跑得通吗？**

### Task 1 — Acquire
必须实际取得：

1. male SSc GWAS summary stats；
2. female SSc GWAS summary stats；
3. FinnGen multiome release manifest；
4. eQTL/caQTL/fine-map/peak-gene所需文件；
5. TenK10K最小replication文件。

### Task 2 — Freeze manifest
记录：URL/accession、文件名、size、SHA256、build、columns、allele coding、sample size、cell type定义。

### Task 3 — Harmonization test
统一：

- GRCh38；
- chr naming；
- ref/alt/effect；
- rsID ↔ chr:pos:ref:alt；
- ambiguous SNP；
- indel normalization。

### Task 4 — 3-locus smoke test
仅：

- BCL11A
- IRF4
- RPL3-PDGFB

对每个locus输出：

1. GWAS region；
2. caQTL hits by cell；
3. eQTL hits by cell；
4. fine-mapped CS；
5. shared signal/coloc；
6. peak-gene mapping；
7. candidate cascade graph。

### Task 5 — R4A GO decision

#### GO_R4B_FULL
若至少一个locus建立清晰C1 cascade，并且文件/统计流程稳定。

#### HOLD
若数据访问仍未解决。

#### PIVOT_OVERALL_SSC
若sex GWAS不可得，但GCST009131 pipeline表现很好。

#### NO_GO_SSC
若sex loci与population molQTL系统性缺乏调控连接，并且这不是技术覆盖问题。

---

## 5. R4B（只有R4A通过后）

1. 全8个sex-specific loci；
2. genome-wide/secondary SSc signals；
3. all 33 FinnGen cell types；
4. TenK10K replication；
5. GSE312129 donor-aware tissue validation；
6. GSE249279 / GSE236111 orthogonal replication；
7. 最后才做translation。

---

## 6. 当前最合理的时间/资源策略

**现在不要做**：

- 下载GSE312932 30.6GB；
- 下载全部SRA；
- 全量重跑SSc tissue atlas；
- 全局PPI/WGCNA/ML；
- docking；
- 写完整manuscript。

**现在最值钱的事情**：

> 取得两个真正决定项目成败的数据入口，然后用3个locus证明链条跑通。

这也是从54篇论文反向总结出来的研发原则：

> **先验证故事的最脆弱环节，再扩规模；不要先做大量容易做的分析。**

---

## 7. 下一阶段最终判断

> **NEXT TARGET = R4A_ACCESS_HARMONIZATION_3LOCUS_SMOKE_TEST**

项目继续推进，但不授权直接进入全量计算。
