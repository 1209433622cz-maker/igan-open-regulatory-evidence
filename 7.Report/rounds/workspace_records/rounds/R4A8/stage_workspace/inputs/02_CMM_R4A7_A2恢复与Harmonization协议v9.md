# R4A7 A2恢复与harmonization试运行协议 v9

## 已经通过的逻辑正控

1. GCST009131按GRCh37处理；2026 sex-specific论文按hg38处理，两个坐标系统继续分轨。
2. IL12RB2历史SSc文献给出 rs3790566=T/C、rs3790567=A/G；当前overall中A1与其一致，可作为“source A1确实是一个真实等位基因”的正控。
3. ULK3附近独立公开summary记录可见 rs2290572=A/G（GRCh37 75,130,573），与GCST009131 A1=A兼容；仍只作为sanity control。

## production级A2恢复规则

只有实际落地的GRCh37双等位参考（首选1000G Phase3 EUR BIM/VCF）可以给区域级A2赋值。流程：

1. 以 rsID + GRCh37 position 联合匹配；不允许仅靠一个字段。
2. 对唯一biallelic SNP：若source A1属于参考两等位集合，则A2取另一等位。
3. multiallelic、position mismatch、rsID merge/retired、strand ambiguous或indel未标准化：标为REVIEW/EXCLUDE，绝不猜测。
4. A/T与C/G回文位点在没有可靠频率时不得自动翻转；有EAF/MAF后再判。
5. indel必须在同一FASTA上left-normalize后再比较。
6. 输出每条variant的 reference_build / source_A1 / recovered_A2 / ref / alt / action / exclusion_reason。

## hg19→hg38

UCSC chain文件的公开内容已核验，但坐标liftOver只用于跨build定位，不能替代等位基因标准化；GRCh37 positive-control工程应尽量留在GRCh37完成，以避免无必要转换。

## 当前状态

A2逻辑与正控：PASS；production区域级恢复：等待1000G EUR BIM/VCF真实字节。
