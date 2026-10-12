# R7A2A3 QiTeng 全稿重构与证据映射

## 1. 输入与 authority

本轮按用户明确要求使用 `QiTeng_Academic_Writing_Skill_v0.3.24.2`，不使用 CC 写作 skill。QiTeng 发布包 SHA-256 为：

```text
d52d3804bf067f9ef469c9bc732ddc1acb4c123a49d086db5cec0b728e8ff17b
```

ZIP CRC、1386/1386 内部 checksum、版本一致性、inventory 和 stale-authority 检查均通过。运行 authority 固定为 `VERSION_REGISTRY.json + 01_RUNTIME/CORE/SKILL.md`。

R7A2A2 发布包通过 ZIP CRC 与 25/25 内部 checksum 验收。正文只继承冻结证据，不把报告中的行动建议当作新数据。

## 2. Argument map

```text
KNOWN
PBC 已有大量遗传位点，FCRL3/IL12RB2 不是新基因

INSUFFICIENT
传统基因提名或单信号共定位无法稳定区分细胞背景和多重局部信号

RESPONSE
疾病侧 study-derived LD + OneK 细胞/供者匹配 QTL LD + SuSiE 多信号 + TenK 独立重复

EVIDENCE
IL12RB2–NK 与 FCRL3–B 跨资源重复；CD8_ET 由 H4 转 H3；INAVA 弱 QTL；组织仅可检测

INTERPRETATION
两个既有位点获得可复算的 cell-context regulatory resolution

BOUNDARY
不证明介导、机制、PBC 特异表达或治疗有效性

NEXT TEST
细胞背景匹配的等位基因扰动 + 多祖源 source-LD 重复 + 更大 genotype-aware liver cohort
```

## 3. Section job map

| 章节 | 主要任务 | 禁止越界 |
|---|---|---|
| Title | 准确显示 source-matched、多信号、独立分子复制 | 新基因、机制、causal |
| Abstract | 报告设计、主数值、CD8_ET 反转、组织 null | 只报阳性；把 TenK 写成独立疾病复制 |
| Introduction | 先说明位点解释难题，再引出单细胞 QTL 和 LD/多信号问题 | 长篇目标基因历史；过早承诺靶点 |
| Results | 按 bounded design→IL12RB2→FCRL3→TenK→tissue→ceiling 排列 | 文献讨论、机制推断、隐藏负结果 |
| Methods | 为每个 Results 模块提供完整 owner | 未出现的分析；事后阈值 |
| Discussion | 与 Cordell/Gjoka/Han/Wang 明确区分；解释 CD8_ET 与 tissue null | 宣称首次或 validated mechanism |
| Conclusion | 收束到 repeated signal sharing 与 cell-context prioritization | 临床效用或治疗推荐 |

## 4. Claim ledger 结果

9 条核心 claim 已建立 title/abstract/results/discussion/conclusion 的允许表达和 boundary。两条主轴为 E2；组织可检测性、方向与弱 QTL 负控为 E1；新颖性定位由既有文献与本研究 E2 证据共同约束。

最重要的语言治理：

- `colocalized/shared signal/replicated/detectable` 可用；
- `causes/mediates/drives/proves/validated therapeutic target` 不可用；
- tissue 只能写 `directionally lower/higher`，不能写 `downregulated/upregulated`；
- TenK 是 independent molecular-QTL replication，不是 independent disease GWAS replication；
- robustness 和 LODO sensitivity 不得称为 independent replication。

## 5. Methods–Results mirror

11 个方法模块均有对应 Results owner：设计冻结、疾病输入、OneK 提取、harmonization、ABF smoke、source LD、多信号、TenK、肝组织处理、组织统计、可复现性。当前 mirror 为 11/11 PASS。

## 6. 稿件重构动作

| 动作 | 内容 |
|---|---|
| KEEP | 两个跨资源复制轴、所有精确统计量、5v5 donor inference |
| REORDER | 先呈现 bounded workflow，再按证据层推进 |
| REWRITE | 新颖性从 gene discovery 改为 method/replication architecture |
| BOUNDARY | tissue null、TenK source-LD 限制、European ancestry、bounded target panel |
| CLAIM DOWNGRADE | mediation/causal/therapeutic wording 全部降到 signal sharing/prioritization |
| EXPAND | CD8_ET 反转的假设变化和方法学含义 |
| KEEP NEGATIVE | INAVA 与 CD8_NC 不删除；组织非显著保留主文 |
| DEFER | 全十供者 reclustering、额外位点/细胞、湿实验 |

## 7. 当前文本状态

正文约5,900词，包含11条编号参考文献、6个主图图例、10个补充表图例和4个补充图图例。作者信息和投稿元数据使用显式占位符，没有虚构。
