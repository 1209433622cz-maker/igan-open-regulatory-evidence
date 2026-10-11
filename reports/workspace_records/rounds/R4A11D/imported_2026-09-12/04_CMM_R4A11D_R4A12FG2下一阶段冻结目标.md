# R4A11D 下一阶段冻结目标：R4A12-FG2

## 本轮完成的实质进展

1. 逐release核实R12/R13主要SSc endpoint病例数和sex counts。
2. 区分 core full-GWAS 与 non-core basic-only endpoint。
3. 核实 standard GWAS 字段足以直接提供 A1/A2语义、BETA、SE、AF。
4. 核实R12 sex-specific发布结构和heterogeneity字段。
5. 未找到R13 sex-specific官方发布证据，因此没有推定其存在。
6. 将IL12RB2主输入从“继续修2019 GCST009131”正式切换为FinnGen现代标准summary：R13 main + R12 bridge。

## R4A12-FG2：必须执行的最小任务

### Gate FG-A：真实manifest / object acquisition

- R12 public manifest
- R13 public manifest
- 精确过滤：`M13_SYSTSLCE`, `SYSTSCLE_STRICT`, `CREST`
- 下载R12/R13 `M13_SYSTSLCE` full GWAS对象
- 保存URL / bytes / SHA256 / schema / build

### Gate FG-B：R12 sex-specific endpoint availability

- 获取 `regenie_single_sex_drop_list_plus_reason_262_endpoints.txt`
- 精确检查 `M13_SYSTSLCE`
- 若未被drop：获取female、male、meta/heterogeneity文件
- 若被drop：状态写 `R12_SEX_SPECIFIC_UNAVAILABLE_BY_DESIGN`，不再猜测或反复抓取

### Gate FG-C：IL12RB2区域 smoke test

优先在R13 all-sex：

- 提取IL12RB2冻结区域
- 验证 rs6662198 / 已知lead存在性和等位基因方向
- 运行完整H6/P0
- 比较R12 vs R13 effect / P / AF / regional architecture

### Gate FG-D：method readiness

- coloc输入矩阵完整性
- SMR BESD/outcome转换表
- SuSiE-RSS LD来源与z–LD gate
- FinnGen native fine-map读取与custom RSS并行计划

## 下一阶段GO条件

满足以下条件即可进入真正疾病分析：

- 至少R13 `M13_SYSTSLCE` full GWAS字节PASS；
- IL12RB2冻结区域coverage PASS；
- effect allele / AF / beta / SE schema PASS；
- disease input与QTL build可harmonize；
- coloc可先启动；SuSiE-RSS另需LD gate。

## 不需要等待的事项

R13 all-sex一旦到位，**无需等待R12 sex-specific或2026 Lancet female/male summary**即可开始 IL12RB2 overall coloc/SMR 主分析。sex-specific数据作为独立复制层后接。
