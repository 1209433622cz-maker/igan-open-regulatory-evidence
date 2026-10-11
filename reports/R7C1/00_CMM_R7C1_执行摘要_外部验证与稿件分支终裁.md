# R7C1 执行摘要：IL12RB2 外部验证模块与稿件分支终裁

## 最终裁决

```text
PBC_PRIMARY_PROJECT = GO
R7B4B2_Q2_BASELINE = FROZEN_BYTE_IDENTICAL
R7C1 = PASS_WITH_BOUNDED_SCIENTIFIC_UPGRADE

IL12RB2_NK_EXTERNAL_DISEASE_STUDY_SUPPORT = PASS
SOURCE_CS_AUDIT = PASS_2_OF_2
CHROMATIN_TRIANGLE = PASS_WITHOUT_DIRECT_MEDIATION
OMIX001122 = DESCRIPTIVE_ONLY

NEW_GENE_LOCUS_CELL_FISHING = NO
FULL_642_RERUN = NO
NEW_BIOLOGICAL_ANALYSIS_REQUIRED = NO

NEXT = R7C2_Q1_TARGET_JOURNAL_REALITY_CHECK_AND_DUAL_TRACK_SUBMISSION_PACKAGE
```

R7C1 已把 R7C0 的预设外部证据正式整合进新的英文稿分支，同时保持作者批准的 R7B4B2 Human Genomics 稿件逐字节不变。升级成立的原因不是发现了新的候选基因，而是 IL12RB2–NK 的核心关联现在获得了三个互补层面的支持：原 OneK source-matched 多信号证据、FinnGen R13 不同疾病研究系统中的单因果验证与 source-CS 审计、以及 PBC–eQTL / PBC–caQTL / peak–gene 三角信号一致性。

升级后的证据等级仍为稳健关联，而非机制证明。FinnGen R13 与发现 GWAS 的个体级完全不重叠无法由公开元数据证实；外部验证没有重建第二套 source-LD 多信号模型；直接 eQTL–caQTL 后验和介导估计缺失；OMIX001122 只有一个 PBC 和一个对照矩阵。因此稿件没有使用“独立人群复制”“完整级联”或“介导”表述。

## 关键结果

- FinnGen R12/R13 疾病可信集：19 与 17 个成员；R13 的 17 个成员全部位于 R12 集合中，Jaccard=0.895，PIP 相关 r=0.833。
- FinnGen R13 × OneK NK/IL12RB2：1,175 个 harmonized variants；PP.H4 分别为 0.9772、0.9977、0.9998（p12=10^-6、10^-5、10^-4）。
- OneK QTL source CS 的 2/2 成员均位于 FinnGen R13 疾病 CS。
- 固定 27 基因 CASCADE 审计：22 个有相关广义细胞 eQTL 覆盖，只有 IL12RB2 返回 PBC–eQTL 共定位。
- l1.NK：PBC–IL12RB2 eQTL PP.H4=0.9703；PBC–linked-peak caQTL PP.H4=0.9695；peak–gene link beta=0.141，距 TSS 239 bp。
- OMIX001122 仅支持 IL12RB2/FCRL3 的描述性可检测性，不支持病例对照、供者复制或空间定位推断。

## 交付身份

- Manuscript MD SHA-256: `22c0039c9daab296aaf2b3b8f8d1912013d21adaeef44635a86f2a38154a9ec6`
- Manuscript DOCX SHA-256: `46ea7585be13b924746e73a7a4b87bacfbcebeec10c7d6e03ed03260d33ef67f`
- WPS PDF SHA-256: `cb9595c8db8b19166eb7df39589c4f9e941a176feb8db557df210ccb5f97c559`
- Figure 4 PNG SHA-256: `7e8b241f9963a70fd66f97e50ef6238e5d18f03acba900de1db6526ef7f9831d`
- Additional file 3 SHA-256: `186d2e914c4b3762dd489230820b3e8c3b1cbf2ce0c75412a134bfd5b6dab097`
