# CMM R7A1B1 执行摘要：PBC 三正控真实信号终裁

**日期：2026-09-15**

## 最终判定

R7A1B 已完成真实字节执行，预冻结的三基因门达到 `2/3`：

```text
FCRL3   = PASS_SIGNAL_SPECIFIC_SHARED_GENE
IL12RB2 = PASS_SIGNAL_SPECIFIC_SHARED_GENE
INAVA   = UNINFORMATIVE_WEAK_ONEK_QTL

R7A1B = COMPLETE
PBC = GO_R7A1C_TENK_REPLICATION_AND_PBC_LIVER_DETECTABILITY
NEW_PRIMARY_PROJECT = NOT_YET_APPROVED
```

PBC 仍未被宣布为新主项目。按照 R7A1A 冻结协议，只有至少一个通过基因在 TenK10K 获得同基因、兼容细胞、同信号复制，并且 PBC 肝组织能够检测到目标基因，才允许升级。

## 主要结果

9/9 个冻结 OneK1K cell–gene 输入可测试，共 24,001 行 QTL。单信号 smoke gate 中 7/9 通过，触发范围严格收缩到 7 个组合、2 个基因；INAVA 和 FCRL3/CD8_NC 没有触发 source-LD。

对 7 个触发组合构建了 donor-matched OneK1K LD，并在 PF10/PF50 协变量残差化和 `L=5/10/20` 下运行两侧 SuSiE-RSS 与 `coloc.susie`。28/28 个疾病/QTL 拟合全部收敛，全部至少形成一个经过 LD purity 筛选的 95% 可信集。

- **IL12RB2 × NK**：四个配置的最佳信号 `PP.H4=0.998027–0.998035`；最低先验 `p12=1e-6` 下最小 `H4/(H3+H4)=0.9806`。
- **FCRL3**：B_IN、B_MEM、CD4_NC、NK、NK_R 五个细胞跨四配置稳定。默认先验下各细胞最小最佳信号 `PP.H4` 分别约 0.994、0.991、0.991、0.940、0.971；低先验下最小 H4 比率仍为 0.609–0.941。
- **FCRL3 × CD8_ET**：单信号 smoke `PP.H4≈0.941`，但多信号后最佳 `PP.H4≈0.004`，明确说明强单信号结果不能绕过 source-LD 裁决。
- **INAVA/C1orf106 × CD4_NC**：OneK1K 区域最小 P≈`3.92×10^-4`，保持“信息不足”，不能写成疾病位点阴性。

## 质量结论

OneK1K 10.34 GB 原档完成全字节读取，MD5 与冻结值一致；Python ABF 与官方 R `coloc.abf` 的最大后验绝对差为 `1.44×10^-15`。GJOKA 仅下载 locus 2/4 的 4 个成员；摘要统计和 LD 均记录 SHA-256。独立 closure QA 共 21 项，全部 PASS。

R7A1B0 原脚本存在四个需要修正的实现问题：GJOKA `BETA/SE` 被误写成 `OR`、LD 变异位置列名错误、`annotate_susie` 前未设置 LD 行列名、可信集 QC 未把 LD 传回 purity 检查。修复后才运行正式终裁；核心信号后验在最后两次重跑中哈希保持一致。

## 下一阶段

R7A1C 只处理 `IL12RB2` 与 `FCRL3`：提取 TenK10K 对应完整 100 kb eQTL 与作者 source SuSiE 可信集，完成 GRCh37→GRCh38 唯一映射和信号身份复制；并对 HRA008003 的公开 PBC 肝组织单细胞资源做字节清单、最小充分下载和 donor-level target detectability。未通过的 INAVA 不进入补救分析。
