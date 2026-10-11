# CMM R4A12FG7-QA：下一阶段冻结目标与触发矩阵

日期：2026-09-13

## 当前状态

`ACCESS_PENDING_NO_FG8_TRIGGER`

本轮不增加新的pre-stage编号。下一计算阶段仍为R4A12FG8，但必须由真实外部输入触发。

## 触发矩阵

| 触发 | 进入动作 | 仍不得声称 |
|---|---|---|
| 2026 SSc female/male完整summary先到且H6 PASS | 最高优先级回到chr22/SYNGR1 sex-specific主线 | 未完成coloc前不得声称C1 |
| 作者原生IL12RB2 `.bim/.ld` 到达且v2 PASS | 启动FG8分子QTL source-LD复现；比较四细胞SuSiE/coloc | 不得称疾病侧source-matched |
| EGA获批且chr1 VCF在受控环境可用 | 运行v2重建；验收后启动FG8 | 受控字节不得进入公开release |
| 文件到达但v2 HOLD | 记录具体缺失、allele、矩阵问题；向提供方请求修复 | 不得以手工翻转或删变异绕门 |
| 无外部输入 | 保持ACCESS_PENDING | 不再换external panel、扩细胞或扩窗口 |

## FG8内部顺序

1. 入库checksum与v2结构验收；
2. 冻结1,366子集及四细胞source-CS覆盖；
3. eQTL侧SuSiE-RSS复现与source-CS一致性；
4. 与FinnGen R13 summary及疾病侧LD条件匹配；
5. coloc.susie / SMR敏感性与明确的source-matched等级标注；
6. GO/NO-GO：只有双侧LD、allele、variant coverage和收敛条件均PASS，才评估正式multisignal证据。

## 当前需要外部完成的最小动作

优先发送作者派生LD请求。若无法分享，再由申请人/PI提交EGA访问。当前draft已完成科学与数据治理内容，仍需补全真实申请人、PI、机构、机构邮箱和EGA账户信息。

