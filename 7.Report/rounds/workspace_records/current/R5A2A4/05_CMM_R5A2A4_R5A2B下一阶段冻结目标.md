# R5A2B 下一阶段冻结目标

下一阶段：`R5A2B_CHR5_TNIP1_BOUNDED_PILOT = GO_BOUNDED`。

## 为什么转 chr5

chr18 已在充分分子 QTL 覆盖、exact donor source LD、三种 LD 定义和多信号方法下失败。按 R5A2A3/R5A2A4 的预注册停止顺序，只允许转 chr5 / rs6861227，不在 chr18 继续换基因或细胞。

chr5 具备更明确的先验候选资格：TNIP1 在 OneK1K 和 TenK10K 既有索引中均出现，且 TenK10K 的既有 SuSiE credible set 包含 exact disease lead。但这些只证明“值得测试”，没有证明 disease–eQTL 共定位。日本 MG 复制中 rs6861227 `P=0.2840654` 且方向不一致，必须作为降温证据保留。

## 本轮工作边界

1. 从已有 OneK1K 全量 archive 提取 chr5，不再下载相同大文件；
2. 固定 GRCh37 `5:149447128–151447128`，EOMG 为主、overall 为复核、LOMG 为亚型对照；
3. 主候选 TNIP1，竞争基因只限 ANXA6、ATOX1、CCDC69、GM2A、RPS14、SLC36A1、TCOF1 中真实落入 source window 者；
4. 先做官方 permutation/q-value、覆盖和 coloc.abf smoke；
5. 只有出现稳健共享信号或可分解 H3/H4 歧义，才为触发的 cell–gene 建 source LD；
6. OneK1K signal-level PASS 后才进入 TenK10K；组织分析继续 HOLD。

## 终止条件

若 chr5 在充分覆盖下没有 source-significant QTL 或共享 disease–eQTL signal：

```text
FAIL_CHR5_EXPRESSION_MEDIATION
MG_REGULATORY_MAIN = NO_GO
NEXT = IgAN_OPEN_DATA_PREFLIGHT
```

不启用 chr2、chr8 或无界全基因组扫描延长 MG 故事。
