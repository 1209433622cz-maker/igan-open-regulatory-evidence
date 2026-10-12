# CMM R4A12FG7：EGA受控访问可行性与数据治理

## 官方对象

- Study：`EGAS50000001654`（TenK10K Phase 1: Genotypes）
- Dataset：`EGAD50000002377`（SNP/indel multi-sample VCF）
- 样本：1,925
- assembly：GRCh38
- DAC：`EGAC50000000931`

## 官方数据使用限制

EGA页面将该数据标记为 HMB + NPUNCU：健康/医学/生物医学研究，且限非营利、非商业使用。TenK10K DAA还要求：secure institutional environment、禁止re-identification、数据仅向Authorised Personnel开放、项目结束后按协议销毁/处理、发表时正确引用/致谢。Appendix II要求项目abstract（500词以内）和注册用户信息。

## 本项目最小化原则

1. 首先请求已经派生的IL12RB2 `.ld/.bim`，若可分享则不申请individual-level WGS。
2. 只有作者/DAC明确不能直接提供派生矩阵时，才申请 `EGAD50000002377`。
3. 获批后仅在受控环境提取 chr1 IL12RB2 ±100 kb并重建matrix；不下载/分析无关染色体和表型。
4. 任何受控VCF、sample IDs、个体dosage不得进入普通YR1 release ZIP。

## 申请依赖用户/机构动作

当前不能代替用户提交：申请需要真实PI、机构、Authorised Personnel、机构签署与必要伦理/安全声明。FG7只生成可交付草稿。
