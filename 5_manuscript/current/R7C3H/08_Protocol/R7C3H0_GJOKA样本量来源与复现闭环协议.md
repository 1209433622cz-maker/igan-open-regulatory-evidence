# R7C3H0 GJOKA 样本量来源与复现闭环协议

日期：2026-10-13

## 冻结问题

本轮只回答三个问题：

1. GJOKA 疾病侧 SuSiE-RSS 的主分析样本量 `N=24,510` 是否与原始来源一致；
2. 若改用病例对照有效样本量，关键多信号判定是否改变；
3. 公共 GitHub 快照能否在脱离 `H:\SCI2\YR1` 的干净目录中重放聚合端点。

本轮不增加疾病、位点、基因、细胞或先验配置，不重筛 6,923 比较，不重跑 486,000 次模拟。

## 主分析口径

Gjoka 与 Cordell 的 PBC fine-mapping 原文明确说明：SuSiE-RSS 使用 logistic-regression summary statistics，样本量为总样本量 24,510，即 8,021 病例和 16,489 对照。因此：

```text
PRIMARY_DISEASE_N = 24510
PRIMARY_N_STATUS = SOURCE_MATCHED
```

病例对照有效样本量仅作为二级压力测试：

```text
Neff = 4 / (1 / 8021 + 1 / 16489)
     = 21584.376825785395
```

## 预冻结压力测试集

在观察 Neff 结果前冻结 33 个比较、14 个位点，包括：

- 全部 18 个严格 A2→M H4/H3 反转；
- 4 个稿件关键轴；
- 6 个最接近 H4 判定边界的比较；
- 6 个高信息 model-sensitive 或 uninformative 比较。

类别允许重叠，因此总数为 33。每个比较运行 PF10 L=5/10/20 与 PF50 L=10，共 132 个 fit。

## 通过门

```text
FIT_QC = 132/132 PASS
FINAL_STATE_CHANGES = 0
MANUSCRIPT_KEY_AXIS_CHANGES = 0
DISEASE_CS_MEMBERSHIP = exact identity
```

若任一关键轴改变，则停止投稿包更新并进入局部复核。若全部稳定，只补充 Methods、Results、Limitations 与 Source Data 3，不重绘 Figure 1–6。

## GitHub 复现门

- 当前脚本不得硬编码本机工作区；
- 路径必须从仓库根目录解析；
- 运行输出默认写到仓库外；
- 当前 Source Data 聚合端点需 38/38 PASS；
- clean clone 运行后工作树保持 clean；
- CI 仅运行便携检查，不声称重跑原始 GWAS、LD、SuSiE 或模拟。

## 退出状态

```text
PASS_STABLE
REVIEW_REQUIRED
FAIL_QC
```

只有 `PASS_STABLE` 允许形成 R7C3H 精确版本。

