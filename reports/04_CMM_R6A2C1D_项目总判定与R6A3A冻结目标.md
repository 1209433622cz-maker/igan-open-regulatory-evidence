# CMM R6A2C1D：项目总判定与 R6A3A 冻结目标

日期：2026-09-14

## 证据账本

| evidence unit | discovery | independent replication | status |
|---|---|---|---|
| ZMIZ1 × NK | OneK robust shared signal | TenK author-precomputed H4≈0.998 + source QTL/CS | validated anchor |
| REEP3 × CD4 | OneK Asian signal-specific PASS | TenK CD4_Naive/CD4_TCM H3-dominant；source CS overlap=0 | discovery only / replication fail |
| 8-locus bounded expansion | combined robust=0/549 tests | targeted SuSiE stable CS=0 | no added positive locus |

当前证据只支持一个跨资源遗传调控锚点。继续 full-24 会增加检验规模，却没有足够证据说明能提高真实阳性产出，因此正式冻结：

```text
IGAN_IMMUNE_CISEQTL_LANDSCAPE = NO_GO
FULL24_DEFAULT_RESUME = NO
REEP3_COUNTS_AS_REPLICATED_LOCUS = FALSE
MANUSCRIPT_SCALE_ANALYSIS = HOLD
```

## R6A3A

下一阶段是 `IgAN completion design gate`，只做两条有界路线：

1. 对 serum-IgA-concordant loci 的冻结蛋白集合执行公开 cis-pQTL 字节级预检；
2. 对已验证的 ZMIZ1 锚点执行 GSE127136 肾组织注释恢复与 donor-level 定位预检。

只接受公开、可下载、可归档的 summary bytes。UK Biobank RAP 需要 approved researcher access，因此不作为核心输入；OpenGWAS API 当前需要身份认证，因此若不能获得无需个人 token 的可归档直链，也不能作为唯一输入。优先检查 GWAS Catalog 的公开 summary-statistics 对象，其官方页面说明文件可从 FTP 获取并按夜更新。

GSE127136 已有本地 processed matrix，NCBI GEO 当前记录确认 13 名 IgAN 肾穿刺与 6 名肾癌旁组织对照，并公开约 15 MB processed counts。该数据适合 donor-level 定位，但癌旁对照限制必须保留，不能称健康肾。

恢复论文级分析的条件：新增至少一个独立 pQTL shared-signal locus，且 ZMIZ1 形成可解释的 donor-level kidney localization。任一条件失败，就冻结 IgAN regulatory main，转入新选题开放数据预检，不返回 immune cis-eQTL locus 扩张。

## 本轮查阅入口

- GWAS Catalog summary statistics：<https://www.ebi.ac.uk/gwas/downloads/summary-statistics>
- NCBI GEO GSE127136：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE127136>
- UK Biobank data access：<https://www.ukbiobank.ac.uk/about-our-data/>
- IEU OpenGWAS API：<https://api.opengwas.io/api/>

