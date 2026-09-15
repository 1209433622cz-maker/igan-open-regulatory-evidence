# CMM R7A1B1：R7A1C 下一阶段冻结目标

**日期：2026-09-15**

## 阶段名称

> **R7A1C — TenK10K Independent Signal Replication + PBC Liver Detectability**

## 1. 冻结基因

只允许：

```text
IL12RB2
FCRL3
```

INAVA 不进入补救；不扩展到第 4 个 PBC 基因，不启动全 56 locus 扫描。

## 2. TenK10K 复制层级

TenK10K v2 官方资源包括 28 个免疫细胞的完整 ±100 kb cis-eQTL、作者 SuSiE 95% 可信集和预计算 coloc。R7A1C 先通过远程 ZIP 成员索引提取两个基因所需的小对象，不默认下载 16.6 GB 全包。

预冻结的主兼容映射：

| OneK 通过细胞 | TenK 主兼容细胞 | 用途 |
|---|---|---|
| IL12RB2 / NK | NK | 主复制 |
| FCRL3 / B_IN | B_intermediate | 主复制 |
| FCRL3 / B_MEM | B_memory | 主复制 |
| FCRL3 / CD4_NC | CD4_Naive | 主复制 |
| FCRL3 / NK | NK | 主复制 |
| FCRL3 / NK_R | NK_Proliferating | 支持性映射，单独报告 |

`B_naive`、`NK_CD56bright` 等可用于细胞家族敏感性说明，但不能替代上述主映射形成 post-hoc 阳性。

## 3. TenK 信号门

对每个基因：

1. 提取 TenK 完整 100 kb QTL 与作者 source SuSiE credible sets；
2. 用本地 `hg19ToHg38.over.chain` 做唯一 GRCh37→GRCh38 映射，核对等位基因和 rsID；
3. 把 R7A1B 导出的 PBC/OneK 可信信号与 TenK source CS 做同信号身份检查；
4. 单信号 ABF 只作辅助，不能覆盖 source CS 冲突；
5. 至少一个主兼容细胞必须在默认先验下 H4 主导，并在 `p12=1e-6` 下不翻转为 H3；疾病共享可信集与 TenK source CS 必须有精确或高 LD 支持的成员重合。

```text
TENK_SAME_GENE_COMPATIBLE_CELL_SIGNAL_REPLICATION >= 1/2 genes
```

仅有 TenK gene-level source significance 不算复制。

## 4. PBC 肝组织门

HRA008003 当前标记为 Open Access，论文设计包括 5 例未经 UDCA 治疗的 PBC 与 5 例肝血管瘤肝组织对照，并另有 5 名健康 PBMC 对照。R7A1C 首先枚举 study/sample/experiment/file 元数据，优先寻找 processed count/annotation；若只有 BAM，生成可恢复下载和 checksum 脚本交由本机执行。

只回答以下问题：

- IL12RB2 或 FCRL3 是否在预先定义的肝内免疫谱系中可检测；
- 是否至少在 3/5 PBC donors 的同一谱系形成非零 donor-level pseudobulk；
- 病例与对照差异只作为正交支持，按 donor 而非 cell 作为统计单位；小样本不允许使用单细胞数量制造伪重复。

```text
PBC_LIVER_TARGET_DETECTABILITY = PASS
```

## 5. 出口

```text
if TENK replication >=1 gene
and PBC liver detectability PASS:
    NEW_PRIMARY_PROJECT = PBC
    NEXT = R7A2_PBC_MANUSCRIPT_SCALE_ARCHITECTURE

else:
    PBC_REGULATORY_MAIN = FROZEN_FAIL_OR_HOLD_BY_PREDEFINED_REASON
    CeD_AUTO_RESUME = NO
    NEXT = NEW_RESEARCH_ARCHITECTURE_REDESIGN
```

## 6. 公开来源

- TenK10K v2 Zenodo: https://zenodo.org/records/18221260
- GJOKA PBC summary/LD: https://www.staff.ncl.ac.uk/heather.cordell/GjokaPaper.html
- HRA008003: https://ngdc.cncb.ac.cn/gsa-human/browse/HRA008003
- PBC liver scRNA paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11458754/
