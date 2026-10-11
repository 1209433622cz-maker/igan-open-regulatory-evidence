# CMM R4A2：三位点证据重排——IRF4、chr22/SYNGR1、BCL11A

## 1. 为什么要重排

R4A1按原计划对BCL11A、IRF4、RPL3–PDGFB三个2026 sex-specific SSc locus做真实数据接入。独立复核后，三者已经不应该继续被当作等价候选：它们代表三种不同的技术/科学问题。

## 2. IRF4：最好的“跨资源不一致诊断位点”

### 当前正证据

TenK10K：

- cell: `B_naive`
- gene: `IRF4 / ENSG00000137265`
- exact lead: `6:396321:C:T`
- SuSiE PIP: **0.999309**
- credible set: **1**
- CS member count: **1**

这是一个非常干净的source-level fine-mapping结果。

### 当前反证据/不一致

FinnGen精确B-naive variant–IRF4 pair：

- p = **0.6728**
- beta = **-0.015405**
- SE = **0.036478**

FinnGen DC同一variant–IRF4 pair有nominal signal（p≈0.00638），但不能替代B-naive的同细胞复制。

### 正确解释

不能写成：

> “IRF4已在两套资源验证。”

也不能写成：

> “FinnGen否定了IRF4。”

正确状态是：

> **TenK10K提供了强B-naive fine-mapped eQTL候选，而FinnGen在同一精确B-naive pair上缺乏nominal支持；必须由SSc区域GWAS的signal-level coloc决定该疾病信号是否与任一molQTL信号共享因果变异。**

因此IRF4保留为R4A3 Track A。

## 3. chr22 rs66578187：从RPL3–PDGFB标签升级为target-competition locus

### 3.1 精确lead对SYNGR1的eQTL异常强

YR1的FinnGen exact-lead表显示：

| cell_type   | gene_symbol   |    beta |       se |           p |
|:------------|:--------------|--------:|---------:|------------:|
| l2.NK       | SYNGR1        | 0.49487 | 0.022123 | 9.9831e-110 |
| l1.PBMC     | SYNGR1        | 0.3995  | 0.01851  | 8.4633e-103 |
| l1.NK       | SYNGR1        | 0.49656 | 0.02302  | 2.8694e-102 |
| l2.CD8_TEM  | SYNGR1        | 0.47997 | 0.024773 | 4.7553e-83  |
| l1.CD8_T    | SYNGR1        | 0.46747 | 0.02656  | 5.7834e-69  |
| l1.other_T  | SYNGR1        | 0.74153 | 0.051113 | 4.0278e-46  |
| l2.MAIT     | SYNGR1        | 0.82903 | 0.057536 | 9.6118e-45  |
| l1.DC       | SYNGR1        | 0.37225 | 0.029198 | 2.4866e-36  |
| l1.B        | SYNGR1        | 0.45946 | 0.046628 | 2.3991e-22  |
| l2.cDC2     | SYNGR1        | 0.30032 | 0.030942 | 7.071e-22   |
| l2.pDC      | SYNGR1        | 0.50091 | 0.05313  | 1.6572e-20  |
| l1.CD4_T    | SYNGR1        | 0.221   | 0.037173 | 2.9004e-09  |

这不是某一个细胞的孤立结果，而是在NK、CD8 T、PBMC、B、DC等多个免疫背景中出现。

### 3.2 同一lead同时强烈影响染色质开放

最突出的peak为 `chr22-39351520-39352777`：

| cell_type         | phenotype_id            |     beta |        se |            p |
|:------------------|:------------------------|---------:|----------:|-------------:|
| l1.PBMC           | chr22-39351520-39352777 | 1.20643  | 0.02937   | 8.07902e-218 |
| l1.CD8_T          | chr22-39351520-39352777 | 1.13108  | 0.0311037 | 4.12787e-185 |
| l1.NK             | chr22-39351520-39352777 | 1.13078  | 0.0314435 | 1.42069e-183 |
| l2.CD8_TEM        | chr22-39351520-39352777 | 1.0954   | 0.0309057 | 5.32385e-179 |
| l2.NK             | chr22-39351520-39352777 | 1.12228  | 0.0318955 | 4.13044e-178 |
| l1.B              | chr22-39351520-39352777 | 1.04262  | 0.0335277 | 2.12807e-149 |
| l2.B_naive        | chr22-39351520-39352777 | 0.906197 | 0.0358637 | 4.59214e-109 |
| l1.other_T        | chr22-39351520-39352777 | 0.842735 | 0.0349503 | 2.27068e-101 |
| l1.Mono           | chr22-39351520-39352777 | 0.866413 | 0.0364848 | 2.12073e-99  |
| l2.MAIT           | chr22-39351520-39352777 | 0.821054 | 0.0351102 | 3.86802e-96  |
| l2.B_intermediate | chr22-39351520-39352777 | 0.841755 | 0.0380352 | 1.91252e-88  |
| l2.CD14_Mono      | chr22-39351520-39352777 | 0.807221 | 0.0380219 | 5.86117e-83  |
| l2.CD8_Naive      | chr22-39351520-39352777 | 0.694009 | 0.0390453 | 7.436e-61    |
| l1.DC             | chr22-39351520-39352777 | 0.685647 | 0.0409799 | 1.74665e-55  |
| l1.CD4_T          | chr22-39351520-39352777 | 0.588893 | 0.0384403 | 9.67676e-48  |

GRCh38下SYNGR1位于chr22:39,349,991–39,385,575，所以该peak落在SYNGR1基因内部，靠近其5'端。lead rs66578187本身位于39,328,807：它比PDGFB更靠近RPL3/SYNGR1区间，但物理距离本身仍然**不能定义效应基因**。

### 3.3 为什么这是重要的新方向

2026 sex-specific GWAS将该区域命名为“RPL3–PDGFB”，并从纤维化生物学上讨论PDGFB是合理的。但是YR1真实molQTL数据提出了一个必须正面检验的竞争模型：

> Disease variant → immune chromatin peak → SYNGR1 expression

这可能成立，也可能在区域fine-mapping后消失。无论哪种结果都比直接沿用“最近/最熟悉的PDGFB”更科学。

### 3.4 当前不能越级声称的内容

当前CASCADE variant response没有正式mechanism classification；精确lead虽然进入一些低PIP credible-set记录，但尚未形成source-defined linked peak→SYNGR1 cascade。也没有SSc GWAS区域共定位。

因此当前评级：

> **C1-proximal molecular tractability / target reassignment hypothesis**

而不是C1。

## 4. BCL11A：暂时降级为“远端结构性位点”

当前GRCh38 BCL11A基因约chr2:60,450,520–60,553,924；SSc lead rs2540100为chr2:59,523,629。两者间隔约0.93 Mb。

后果是：

- ±500 kb固定region会天然漏掉BCL11A本体；
- “在当前region看不到BCL11A eQTL”不能当作生物学阴性；
- 需要更大的region、LD-based locus boundary或真实fine-mapped credible set定义窗口；
- 在IRF4/chr22技术链尚未打通前，不值得让BCL11A占用第一优先级。

## 5. 新排序

|   priority | locus                                       | TenK10K_exact_lead                                                | FinnGen_exact_lead                                                                                                                        | current_grade                                       | role_next                                                                              |
|-----------:|:--------------------------------------------|:------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------|:---------------------------------------------------------------------------------------|
|          1 | IRF4                                        | B_naive IRF4 SuSiE PIP=0.999309; CS=1; 1 member                   | B_naive IRF4 p=0.6728, beta=-0.015405, SE=0.036478; DC IRF4 nominal p=0.00638                                                             | C2/C3 only; C1 not testable                         | cross-resource discordance diagnostic; primary disease-coloc smoke locus               |
|          2 | chr22 RPL3–PDGFB region / SYNGR1 competitor | no decisive exact-lead SuSiE target in current screen             | SYNGR1 eQTL strongest l2.NK: p=9.983e-110, beta=0.49487; caQTL peak chr22-39351520-39352777 strongest l1.PBMC: p=8.079e-218, beta=1.20643 | C1-proximal molecular tractability, not C1 evidence | target-reassignment smoke locus: test SYNGR1-centered eQTL+caQTL shared disease signal |
|          3 | BCL11A                                      | no exact disease-lead BCL11A SuSiE hit in current extracted table | current exact-lead marginal screen strongest eQTL target=AC007100.1; no direct exact-lead BCL11A cascade classification                   | structural/distal unresolved                        | defer until long-range region/LD/peak-gene access is established                       |

## 6. 对论文故事的影响

原故事可能是：

> BCL11A / IRF4 / PDGFB均为sex-specific SSc候选基因。

现在更严谨的故事应该允许**locus label与effector gene解耦**：

> sex-specific SSc loci → cell-specific regulatory mechanism → evidence-based effector gene reassignment.

如果chr22最终真正支持SYNGR1而非PDGFB，这将成为论文中最有价值的机制性发现之一；如果不支持，也能通过严格negative result避免错误基因归因。
