# MG 冻结与 R6A0 IgAN 下一阶段目标

## MG 项目状态

chr18 与 chr5 两条预注册机制路线均在真实字节、充分区域覆盖和 signal-level 门控下失败。因此：

```text
MG_REGULATORY_MAIN = NO_GO
MG_FORCE_SALVAGE = NO
MG_DEFAULT_RESUME = NO
FURTHER_MG_LOCUS_RESCUE = STOP
MG_DISEASE_GENETICS = RETAINED
MG_ROLE = ARCHIVED_PROJECT_AND_METHOD_ENGINEERING_ASSET
```

不再转 chr2、chr8 或更大 locus 池。MG 阶段积累的 harmonization、source donor、LD QC、coloc prior sensitivity、bounded competition、checksum 和状态机全部继续作为方法资产。

## 下一阶段

下一阶段固定为：

```text
R6A0_IGAN_OPEN_DATA_BYTE_LEVEL_PREFLIGHT = GO
IGAN_MAIN_PROJECT = NOT_YET_APPROVED
```

R6A0 只做：2023 biopsy-confirmed IgAN GWAS accession/真实字节/schema 验收；非 MHC loci 重算；OneK1K/TenK10K 可测性；GSE127136、GSE286184 等肾组织文件入口；以及 hostile novelty audit。

候选论文问题是“blood immune regulatory signal → kidney resident/disease-state convergence”，但必须由真实字节与创新性门支持。不得退化为普通的 GWAS + scRNA + MR。

只有 `GWAS bytes PASS、≥2 non-MHC testable loci、≥1 cross-QTL route、public kidney tissue PASS、permission data依赖为零、novelty gate PASS/HOLD` 同时成立，才进入 R6A1 有界 locus pilot。
