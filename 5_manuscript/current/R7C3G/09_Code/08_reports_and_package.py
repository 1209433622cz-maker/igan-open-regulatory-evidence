from pathlib import Path
from collections import Counter
import json,csv,hashlib,zipfile,shutil,html,datetime,importlib.metadata
import pymupdf
R=Path(r'H:\SCI2\YR1');A=R/'5_analysis/R7C3G_ExpertNarrative_20261012';O=R/'5_manuscript/R7C3G_ExpertNarrative_20261012';Q=O/'06_QA';C=R/'2_code/11_manuscript/R7C3G_ExpertNarrative_20261012';P=R/'7.Report/rounds/R7C3G_20261012';L=R/'6_release/R7C3G_20261012'
P.mkdir(parents=True,exist_ok=True);L.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,s):p.write_text(s,encoding='utf-8')
def tsv(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
E=json.loads((A/'EVIDENCE_AUDIT_STATE.json').read_text(encoding='utf-8'));I=json.loads((A/'LOCAL_CURRENT_IDENTITY_STATE.json').read_text(encoding='utf-8'));D=json.loads((Q/'DOCUMENT_QA_STATE.json').read_text(encoding='utf-8'));assert E['checks_fail']==0 and not D['fail']
receipt=[];B=R/'5_manuscript/R7C3F_SubmissionCandidate_20261012'
for line in (B/'checksums.sha256').read_text(encoding='utf-8-sig').splitlines():
 hh,rel=line.split('  ',1);receipt.append({'file':rel,'sha256_expected':hh,'sha256_current':sha(B/rel),'pass':sha(B/rel)==hh})
assert all(x['pass'] for x in receipt);tsv(Q/'BASELINE_23_ASSET_PRESERVATION.tsv',receipt)
docs={str(p.relative_to(O)):len(pymupdf.open(p)) for p in [*sorted((O/'01_Manuscript').glob('*.pdf')),*sorted((O/'03_Supplement').glob('*.pdf')),*sorted((O/'04_Cover').glob('*.pdf'))]}
assert sum(docs.values())==56
# Machine results and visual judgement are explicitly different forms of verification.
prior_review=json.loads((Q/'VISUAL_REVIEW_RECEIPT.json').read_text(encoding='utf-8'))
assert prior_review.get('reviewed_pdf_sha256')=={rel:sha(O/rel) for rel in docs},'Visual-review receipt is absent/stale. Actually inspect the current WPS pages before packaging; do not auto-mark review.'
assert prior_review.get('reviewed_figure_pdf_sha256')=={p.name:sha(p) for p in (O/'02_Figures').glob('*.pdf')},'Figure review receipt is stale.'
vstate={'reviewer':'Codex primary assistant; no invented external reviewer','method':'All current WPS pages inspected in contact sheets; high-risk full-size pages and all nine final figure masters reviewed; four historical SVG masters independently rendered and viewed.','pages':56,'pdf_page_counts':docs,'main_figure_pages':[{'figure':i,'candidate_page':i+17} for i in range(1,7)],'main_figures':6,'main_panels':22,'supplement_figures':3,'supplement_panels':12,'all_original_figure_objects':46,'status':'PASS_AFTER_SOURCE_AND_LAYOUT_REPAIR','resolved':['Figure5b PIP/include text collision','Supplementary FigureS3 full19/17 source-set sizes versus17-member intersection table','Figure1d three-case annotation added','Inline review lets image/legend flow together without sparse orphan pages','Obsolete intermediate page previews separated from current56 pages'],'scope_limit':'Visual approval is an editorial judgement, not validation of every raw-read or genotype-derived scientific fit.'}
vstate['reviewed_pdf_sha256']=prior_review['reviewed_pdf_sha256'];vstate['reviewed_figure_pdf_sha256']=prior_review['reviewed_figure_pdf_sha256'];vstate['S10_crosswalk_review']='37/37 historical rows routed; C17 ceiling superseded by S11; E-series IDs separate'
write(Q/'VISUAL_REVIEW_RECEIPT.json',json.dumps(vstate,ensure_ascii=False,indent=2));D['visual_review']='COMPLETED_56_OF_56_PAGES';D['baseline_assets_unchanged']=23;write(Q/'DOCUMENT_QA_STATE.json',json.dumps(D,ensure_ascii=False,indent=2))
state=json.loads((O/'08_Protocol/EDITORIAL_STATE.json').read_text(encoding='utf-8'));state.update({'status':'COMPLETE_EXPERT_AUDIT_AND_INDEPENDENT_EDITORIAL_CANDIDATE','evidence_replay':'37/37 PASS','document_machine_checks':f"{D['pass']}/{D['checks']} PASS",'baseline_preservation':'23/23 PASS','WPS_export':'4/4 PASS;56 pages inspected','github_new_editorial_assets_pushed':False,'journal_submission_completed':False});write(O/'08_Protocol/EDITORIAL_STATE.json',json.dumps(state,ensure_ascii=False,indent=2))
versions={n:importlib.metadata.version(n) for n in ['numpy','pandas','python-docx','matplotlib','PyMuPDF','pillow','openpyxl']};write(Q/'ENVIRONMENT_VERSIONS.json',json.dumps(versions,indent=2))

summary=f'''# R7C3G：导师级全量证据核查与论文叙事重构

日期：2026-10-12。依据 RP v4 和 QiTeng Academic Writing Skill v0.3.24.2。审核对象是当前 PBC 项目；SSc、MG、IgAN 保持独立归档。

## 最终判断

**PBC 继续 GO。本轮完成实质性的论文重构和图版重组，形成独立新候选稿；原 R7C3F 作者批准基线保持 23/23 文件身份不变。** 当前论文最有防守能力的贡献是：用明确协调的关联输入、来源匹配的 LD、信号对级解释和真值已知的模拟，评估 PBC 调控归因何时稳定、何时改变、以及哪些验证不能推出机制。

不应以“首次发现 IL12RB2/FCRL3”“通用更优算法”“完整因果调控级联”或“临床治疗机制”作为中心命题。新叙事保留阳性证据，也让关键反例和组织层非显著结果承担解释职责。

## 真实完成的核查

| 层级 | 本轮范围 | 实际结果与边界 |
|---|---|---|
| 全工作区文件身份 | {I['files']:,} 文件，{I['bytes']:,} bytes，{I['GiB']:.3f} GiB；14 个 reparse points 不递归 | 基于同日已完成的 fresh SHA；大小/mtime 不变才复用，新增或修改 {I['fresh_files']} 文件重新计算 SHA；0 枚举错误 |
| 可携带结果内容 | 482 个结果对象 | 480 个非空对象解析、字段与状态归档；2 个历史 IgAN 空表明确记录为未产出，不能充作 PBC 证据 |
| 投稿 Source Data | 两个 ZIP 的 56 个成员 | CRC、成员 SHA、解析均执行；新包与原两个 ZIP 逐字节相同 |
| 关键科学终点 | 642 身份/状态、分母、信号对、模拟渠道、组织 exact tests | 37/37 deterministic replay PASS；不是重跑全部 fine-mapping |
| 当前及历史图片 | 46 个 PNG/PDF/SVG 对象 | 逐对象身份、内容与取舍台账；4 个 SVG 单独渲染检查；格式副本不算独立实验 |
| 新稿与组图 | 33 项可追溯编辑；6 主图/22 panel；3 补图/12 panel | 主图重新从冻结源表绘制，保留 PDF/SVG/PNG 和 34-panel source map |
| 文档检查 | 4 个 WPS 后台导出 PDF，共 56 页 | {D['pass']}/{D['checks']} machine QA PASS；56/56 页目视复核；23/23 baseline PASS |

文件身份快照时间：{I['snapshot_at']}。这是一份分层审计：所有文件的尺寸与身份有清单，全部可携带结果有机器内容索引，核心证据有深度复算。它不意味着本轮再次从 BAM/BED 原始字节重拟合所有历史分析。

## 新的六段主线

1. **Figure 1：界定问题和分析范围。** 6,923 → 5,460 → 642；先让读者知道谁被分析、哪些未分析，以及 A0/A1/A2/M 的输入契约。
2. **Figure 2：区分输入变化与残留重分类。** 变异支持、疾病统计分别改变 15 和 19 个状态；协调输入后仍存在 8 个 H4→H3 与 10 个 H3→H4。不能把 139 次完整状态变化都写成错误纠正。
3. **Figure 3：解释信号对和细胞归因。** 32/92 的共享与独立信号共存；PF10/PF50 总体一致仍容纳 FCRL3-CD8_ET 的 .003636→.991894 反转；B-cell 跨 QTL 资源支持形成同一基因的对照。
4. **Figure 4：让真值模拟裁定收益和代价。** 假共享 12.41%→8.56%，共享恢复 32.99%→26.66%；33.08% 可评价率作为结果，不能藏到 QC。
5. **Figure 5：外部证据提高置信度但限定上限。** IL12RB2 获得不同疾病研究系统、可信集成员和 NK disease-QTL 证据；peak–gene link 的最佳标签是 PBMC；缺少直接 eQTL–caQTL posterior，不能画有方向的介导箭头。
6. **Figure 6：以真实组织边界结束生物学解释。** 全部 10 位供者显示可检测性，两基因 BH q 均 .1111；小样本、手术非病灶对照和 bounded target panel 均保留。

## 重要交付

- 期刊候选稿：`5_manuscript/R7C3G_ExpertNarrative_20261012/01_Manuscript/Manuscript_ExpertRebuilt.docx`，配套 24 页 WPS PDF。
- Results 内嵌审阅稿：`Manuscript_AuthorReview_InlineFigures.docx`，配套 25 页 WPS PDF。
- Supplementary Information：6 页 WPS PDF；Source Data 两个 ZIP 与 S1–S10 工作簿不改字节。
- 46 图片取舍表、34 panel 源表映射、15 条中心主张–证据上限图谱、33 项 before/after 编辑记录。
- 详细导师评估、图版取舍说明、完整行动记录和下一阶段协议。

## 下一阶段

**R7C3H — Final narrative sign-off and publisher proof。** 本轮不是新的生物学搜索阶段。下一步让两位作者审阅这一个明确的新版本，然后锁定唯一主稿、补充 PDF、6 张独立图及 Source Data 的上传身份，按门户生成的 proof 再核对编号、分母和声明。此前作者批准的事实与声明继续保留；新稿不能被标记为已经获新版签署或已经投稿。

npj Genomic Medicine 可继续作为当前尝试目标，但接收前景取决于编辑对实质知识增量的判断，不能从组图数量、QA PASS 或目录完整性推断。不要为提高期刊档次继续寻找替代阳性基因。本轮未提交期刊、未生成 DOI、未把新编辑稿推送 GitHub。
'''
write(P/'00_R7C3G_执行摘要_证据主线与最终裁决.md',summary)

audit='''# 医学／统计遗传学／生信导师级证据审计与叙事设计

## 1. 科学问题是否值得继续

值得继续。现有结果已经形成一个可回答的问题：**在同一疾病和固定 gene–cell 范围内，调控归因的变化来自哪些输入选择、哪些信号结构和哪些模型敏感性？** 该问题会影响后续功能实验的 gene/cell 优先级，具有具体的生物医学含义。疾病 GWAS 阳性并不保证某个细胞中的表达变化介导风险；一个优先化结果如果依赖隐藏的输入差异，可能把验证资源引向错误的细胞或机制。

这是一篇以 PBC 为实例的经验性调控归因可靠性研究，包含可复现方法审计和有限模拟。没有新算法定义或广泛性能最优性证明，因而不应包装成通用算法论文；没有新的干预实验，因而不应包装成两个治疗靶点的机制论文。将所有材料向这一中心问题组织，比继续增加组学图层更有价值。

## 2. 核查范围、文件状态与方法边界

本轮重新读取 RP v4、174 段当前英文主稿、33 段原补充说明、活动 QiTeng registry、482 个可携带结果文件以及两个 Source Data 包。原工作区的全字节审计与现阶段文件身份审计是不同职责：前者在同日 R7C3F 已执行；本轮仅在 size 和 mtime 完全一致时复用其 SHA，新增或改变字节重新 hash。原始 BAM、genotype BED、全量 eQTL 和 donor covariates 仍留在本机并保留 provenance，本轮没有重建所有 LD 或 fine-mapping。

结果索引有两份历史 IgAN 零字节表：`R6A2B0_targeted_signal_coloc.tsv` 和 `R6A2B0_targeted_susie_credible_sets.tsv`。它们属于已归档方向的未产出占位，不是当前 PBC 结论被推翻。需要保留未产出状态，而不是填假数或写为科学阴性。

`4_figures` 的 46 个对象覆盖当前 PBC 图、早期 PBC 控制图、模型审计、模拟诊断、donor 图，以及 MG/IgAN 历史图。每个对象都有路径、大小、hash、内容与采用/归档理由。PNG/PDF/SVG 是同一图的不同导出，不构成额外复制。当前新主图从冻结源表重新生成，并保留可编辑 SVG 与嵌入字体的 PDF。

## 3. 主数据：范围清楚才能讨论比例

全 registry 6,923；ABF-eligible 5,460；coverage-insufficient 1,463。后者是未满足技术门，不是 1,463 个阴性机制。多信号深度分析仅覆盖 642 个高信息比较，涉及 47 loci、200 genes、14 cell types、286 cell–locus blocks。不是全部 6,923 项都完成 SuSiE，也不是 642 个独立疾病关联。

642 保留三个冻结角色：184 primary trigger verification、455 H3 rescue/falsification、3 borderline calibration。终点分别为：

| 工作层 | H4 | H3 | Model-sensitive | Uninformative |
|---|---:|---:|---:|---:|
| Primary 184 | 83 | 19 | 52 | 30 |
| H3 layer 455 | 8 | 409 | 7 | 31 |
| Borderline 3 | 1 | 0 | 0 | 2 |
| 全部 642 | 92 | 428 | 59 | 63 |

92 个 H4 comparison 对应 27 genes/19 loci，重复 gene–cell 不能算新疾病发现。92/642 是选定高信息集的构成比例；它不是所有 PBC 风险位点的真实共享机制发生率。47 位点依赖也意味着 comparison-level 比例没有自动获得独立样本推断资格。

## 4. 同输入对照是真正的方法学支点

A0：历史 S_A support + GCST statistics + ABF；A1：S_M support + 同一 GCST statistics + ABF；A2：S_M + GJOKA disease z statistics + ABF；M：冻结 PF10 multi-signal procedure。

所有 642 项 S_M 均小于 S_A，每项减少 19–114 variants，median 65/7.67%。A0 replay 最大绝对差 3.55×10⁻¹³。A0→A1 15、A1→A2 19、A2→M 139 次 categorical changes；受影响集合可以重叠，不能相加作为独立贡献。

A2 起点 H4=113、H3=452。在完全协调支持集和疾病统计后，严格 H4→H3 为 8，H3→H4 为 10。原历史 12 个 H3→H4 中 2 个在 A2 已进入 ambiguity，因此不能继续使用 12。真实数据没有 causal truth，变化应叫 reclassification，不能叫纠错或已知假阳性下降。

A2 对 M 仍比较完整程序：credible-set discovery、先验、参数估计和判定规则都可能不同。这不是只更换 causal-variant 数量的单因素实验，也没有隔离每个程序组件的因果贡献。当前文字保留这一边界，是可发表比较的前提。

## 5. 信号对级解释与 FCRL3：全稿最值得保留的反例

92 个 H4-supported comparison 中 32 个同时有 qualifying H3 pair；92 H4 与 428 H3 均满足跨 L 的相关 pair identity stability。这直接支持“一个 locus/gene/cell 标签不足以概括该区域全部信号”，而不是支持所有分子效应都共享疾病信号。coloc 官方 SuSiE 示例本身允许共享与非共享的配对共存；本研究贡献在来源匹配、固定范围和真实再分类数据，而不是新发明这种模型结构。[coloc 官方多信号示例](https://chr1swallace.github.io/coloc/articles/a06_SuSiE.html)

520 个 PF10 definite H4/H3 comparison 中，PF50 的 491 retained、4 changed、25 uninformative，不能以全 642 为分母写 94.42%。其余 122 个 PF10 sensitive/uninformative 不在这一统计中。

FCRL3-CD8_ET 保持 A0/A1/A2 H4≈.941/.941/.949，但 M PF10 best H4=.003636，PF50 best H4=.991894。这是匹配输入后仍不能稳定获得细胞归因的具体实例。**PF50 更高不证明 PF50 正确，PF10 更低也不自动证明 PF10 生物学正确。** 因子数同时改变表达表型模型和 residualized LD，不能把反转全部归为 LD-only。

早期三正控图片仍显示 CD8_ET PF50≈.004。它属于旧阶段的模型显示，不允许覆盖当前 .991894 结果。本轮保留其历史 hash 和来源，但明确标记 superseded display，禁止混入当前主图。

相邻的 FCRL3 B_IN/B_MEM OneK H4≈.9937/.9910 和 TenK B-intermediate≈.9916 提供重要对照：同一基因的 B-cell 支持可以稳定，而 T-cell 标签仍依赖模型。TenK 使用相同 PBC GWAS，且没有重建 TenK donor LD，因此是 cross-resource molecular-QTL support，不是第二套独立疾病复制或多信号 source-LD 证明。

## 6. 模拟：收益、损失与不可评价必须一起展示

已从 iteration channels 独立重算全部 486,000 次状态；每个六场景各 81,000 个 grid-weighted iterations。没有登记的技术错误。共有 130,994 no-CS-both、16,819 no-disease-CS、177,405 no-QTL-CS、160,782 pair-evaluable，合计恰为 486,000。

假共享平均率 12.41%→8.56%，共享恢复平均率 32.99%→26.66%，同时呈现才有意义。在相关但不同信号场景 S2 中改善不彻底，在两个性状均有两信号但无共享的 S5 中改善较强；这种依赖性由补充图 S2 保留。仅 33.08% 可形成可评价 pair；conditional H4 决策率不能替代 unconditional recovery，也不能把没有可信集当成软件错误。

该模拟是两个 empirical 128-variant LD templates、固定疾病 N=24,510/QTL N=750、有限 MAF/LD/L/prior grid。它没有覆盖全部 ancestry、样本量、效应结构或 allele mismatch；它比较单 configuration，而非直接校准 cross-L + skeptical-prior + source-QC 的全套 composite gate。486,000 是大 iteration 数，不等于广泛模型外推能力。当前不得主张通用优越性或真实数据误差率已被标定。

## 7. IL12RB2 外部证据：强在哪里，断在哪里

FinnGen R13 × OneK NK/IL12RB2 使用 1,175 harmonized variants、795 cases/368,758 controls。p12=10⁻⁶/10⁻⁵/10⁻⁴ 下 H4≈.9772/.9977/.9998；OneK QTL 两个 credible-set members 均在 FinnGen R13 的 17-member disease CS。效应方向与 source membership 是增加置信度的证据，但不是唯一 causal variant 证明。

不同 disease study system 不等于已证实 participant 非重叠；公开 metadata 无法证明这一点。FinnGen R12/R13 是相关的纵向版本，CS19/17、intersection17、Jaccard17/19 用于来源稳定性，不算两次独立 disease replication。同一 multiome resource 的 NK/PBMC/子层 NK 也不算三独立 cohort。

固定 27-gene CASCADE 查询中 22 有 relevant broad-cell eQTL coverage，只有 IL12RB2 返回 PBC-eQTL coloc。未返回是 evidence availability boundary，不是另外 26 个 gene 的充分否定。保留完整覆盖台账，避免以接口缺记录制造阴性。

来源记录支持 NK disease-eQTL H4=.9703 和 NK disease-caQTL H4=.9695；peak 距 TSS239bp，fasthurdle link coefficient=.140574。关键是 peak-gene link 的 best_cell 为 PBMC，不是一个另行验证的 NK link。也没有直接 eQTL–caQTL posterior。因此主图只画无方向关联线和一个缺失的虚线边，Methods 与 Results 必须保持同一证据上限。

S8 保存旧 position-only chromatin audit；S11 保存后续冻结范围内的 regional caQTL 查证。某个 top eQTL variant 不在 peak CS 不等于整个 disease-caQTL 区域没有 sharing。当前 S11 结果取代旧 S8 的 chromatin ceiling，但不修改历史原表。补充说明正式解释该版本优先级。S10历史图号与当前图版由新增37行crosswalk逐项对应；C17的旧chromatin ceiling标记为已被S11更新。原科学数据与工作簿字节保持不变。

## 8. 肝组织结果的价值在于给机制推断划边界

两个 target–lineage pairs 在 5 PBC/5 non-lesion surgical donors 均满足 technical 和 detectability gates；FCRL3 mean log1p-CPM difference=-.7863，exact P=.1111；IL12RB2 difference=+.3300，exact P=.06349；两目标 BH q 均 .1111。本轮重算全部 252 labels，不是只抄 summary。

这支持目标在相关免疫谱系中可检测，不支持 corrected PBC-specific enrichment，更不支持 genotype-expression-tissue mediation。非显著也不能证明无疾病差异：n=5+5 有限，手术非病灶组织不是普通健康人肝脏，marker-target panel 不具备全 transcriptome cell-state 解析能力。主图保留全部 donor points/离群值，不制造阳性星号，也不追加 pooled-cell 分析挽救疾病特异性。

OMIX001122 仅提供一张 PBC 和一张 control processed matrix，缺少可用 spatial coordinates/tissue image/donor replicate design。因此只是 descriptive detectability，不能升级为独立空间验证，不值得为了多一个组学层放在主图占据中心。

## 9. 新颖性与投稿定位

IL12RB2 的遗传优先化和 FCRL3 的表达/蛋白/组织证据已有 2026 直接竞争工作；FCRL3 不是首次提出的新 gene。FinnGen population-scale immune multiome 已有公开大规模研究，资源本身也不是本项目创新。[FCRL3 原始研究](https://pmc.ncbi.nlm.nih.gov/articles/PMC12888446/)、[FinnGen multiome 原始研究](https://www.nature.com/articles/s41586-026-11078-2)

可防守的知识增量来自一组连接结果：固定 PBC-wide screen → 对称高信息集 → 输入协调归因 → 双向再分类 → pair-specific 和 covariate-specific 解释 → false-sharing/recovery/discovery 三类模拟 estimands → 外部 disease/QTL/chromatin support → donor-level non-significant tissue boundary。这个链条比“两个已知基因的多组学图谱”更有出版意义。

当前 npj Genomic Medicine 路线可以继续尝试。编辑可能仍认为单病种的经验性方法审计偏窄，这是真实的不确定性。要解决它，应把 functional prioritization 的解释后果讲清楚，而非夸大算法或临床应用。原文献、19 references、作者批准的事实和声明保留；标题12词、摘要126词、无 Intro/Discussion 子小节、Methods 仍在主文、figure legends 均低于350词。[npj 官方 Article 要求](https://www.nature.com/npjgenmed/content-types)

## 10. 论文结构与叙事的实际改动

摘要现在包含问题、固定范围、协调输入后残留双向变化、模型反例、模拟收益与损失、外部支持和组织边界。Introduction 第一段解释错选 gene/cell 对后续功能实验的代价，最后一段按新 Results 顺序提出问题。Results 每段对应数据–解释–限定–下一问题，避免在尚未解释 model-context 反例时先展开 IL12RB2 外部证据。

Discussion 首段从三个条件出发：输入协调、signal pair identity、稳定性与机制分开，不重复流水账。统计限制和生物学验证限制分两段，保留 locus dependence、selection、unknown truth、whole-procedure contrast、two-template finite simulation、shared disease GWAS、participant overlap unknown、PBMC link、direct posterior gap、small donor panel。结尾回到 functional prioritization 的可解释性，不补造 clinical benefit。

Methods 的核心规格、donor counts、harmonization、N/LD 约定、SuSiE 参数、prior 和 target-panel 细节保留。原 N=24,510 与 source 定义没有新增反证，不因常见 N_eff 公式就擅自改 N。当前 source-matched residualization 是按模型构建的工作输入，不被写成恢复了作者原始历史 PF10 矩阵。

## 11. QiTeng 执行边界

使用用户指定 ZIP 的活动 v0.3.24.2，不使用 CC skill。采用 claim/evidence ceiling、Methods–Results mirror、panel ownership、compression adequacy 与 whole-manuscript passes。本轮的文档机器检查和37科学 replay 是项目检查，不是 QiTeng 发布包 behavioural tests 的新执行；不能把实验性 skill 说成已通过外部验证。

主稿重新排序33项追踪编辑，保留完整前后差异；删去的主要是重复主图功能，必要负结果、替代解释和方法边界均未删。审阅稿允许图和图注在 Results 自然同页流动，候选稿保留文末独立图页。所有4份PDF均由后台WPS生成。

## 12. 下一阶段决策门

进入 R7C3H，目标是锁定这一版本的科学叙事和期刊 proof。现在没有必要再换疾病、增加 locus/gene/cell、重跑全部模拟或强制全10-donor reclustering。下次必须可回答：主张能逐项找到源表吗；最关键的反例和未通过项是否仍在主文；出版门户是否保留所有图、公式、补充材料和作者声明；唯一上传版本的 hash 是否已锁定。

只有当未来要升级到全流程误差控制或因果介导论文时，才另立新协议：独立 cohort 非重叠证据及 source-LD 验证、更多 ancestry/sample-size/LD templates、完整 composite-gate calibration、direct eQTL-caQTL 与 functional intervention。这些属于新增研究，不应成为当前范围内稿件无限延期的理由。
'''
write(P/'01_R7C3G_导师级全量证据审计与叙事重构.md',audit)

fig='''# R7C3G：图片、子图选择与重组设计

## 总体选择规则

一个主图回答一个问题；先定义范围与输入，再解释真实数据中的变化，随后用模拟评估代价，最后核对外部及组织边界。不是从历史图中挑最高 H4 拼成阳性故事。所有46对象的逐文件判定见 `ALL_46_IMAGE_SELECTION_LEDGER.tsv`，全部34新panel的源表见 `PANEL_EVIDENCE_MAP.tsv`。

| 新图 | 新panel | 主职责 | 原图处置 | 为什么放在这里 |
|---|---|---|---|---|
| Fig1 | a screen funnel；b input contract；c outcomes；d184/455/3 | 研究范围与比较规则 | 原Fig1身份诊断移S1；旧cohort图合并 | 不先定义 A0/A1/A2/M，后续模型差异无法解释 |
| Fig2 | a support histogram；b15/19/139；c full matrix；d113/452 denominators | 同输入仍有双向重分类 | 原Fig2e/f移新Fig3 | 六panel原图混了两个问题；拆开提升可读性 |
| Fig3 | a32/92 mixed pairs；b491/4/25；cFCRL3-CD8_ET；dB-cell cross-QTL | 信号对与细胞标签的模型边界 | 原Fig5 counterexample提前；OneK重复条图归档 | 用具体反例解释总体稳定率的局限，避免把敏感性放在后面淡化 |
| Fig4 | a6场景渠道；b条件/无条件；c false sharing/recovery；dCS discovery | 真值模拟的收益、代价和可评价率 | 原Fig3改号；LD分层放S2 | 在读者看到真实反转后，回答更复杂模型是否一定更好 |
| Fig5 | a外部prior；b2-member sourceCS；c27/22/1coverage；dassociation edges | IL12RB2 支持与证据断点 | 原Fig4 release scatter移S3 | 外部证据服务于归因可靠性，不能先把故事讲成阳性基因验证 |
| Fig6 | aFCRL3 donor；bIL12RB2 donor | 可检测性与非显著疾病差异 | 去掉旧Fig6c示意；保留全部donor | 以真实验证上限收束，而不是制造机制闭环 |

补图S1四panel给完整三相邻矩阵和单位审计；S2六panel给各场景LD依赖；S3两panel给17交集概率及19/17完整CS大小。Figure S3a 的散点只有17个共同成员，b使用identity JSON的完整集合大小，避免混淆 intersection 与 full set。

## 不进入当前主图的资产

- 原早期三正控 PF50≈.004 图：当前 source 值≈.992，属于已被当前模型审计取代的历史显示。
- 原A0 112/455/72 trigger图：保留 freeze provenance；不能替代 A2 的113/452 matched denominators。
- 模拟 truth schematic/coverage/mismatch 诊断：其必要内容已由Methods、Fig4、S2解释；不重复占主图。
- IL12RB2 R12/R13 scatter：有用，但只是同研究系统的纵向版本稳定性，放S3。
- OMIX pooled processed matrices：有检测信息，但无空间坐标、独立供者设计，保留S11和文字边界。
- MG chr18/chr5、IgAN ZMIZ1/REEP3 图：属于其他项目，留作方法复用与失败学习，不参与PBC统计验证。

## 表达与导出规范

主图PDF保留字体和向量对象，SVG保留可编辑text，PNG用于DOCX内嵌。主图宽179.07mm；Fig1–5高158.75mm，Fig6高87.63mm。使用Arial；颜色语义跨主图一致：H4/支持为teal，H3为orange，敏感为purple，无信息为grey。因果未成立的链接只用无方向线；默认H4=.80与low-p12条件优势门不混淆。

图注说明每个panel、来源、统计单位、不同分母、拟合类别和不可推出的结论。Fig6明确252枚exact标签、两目标BH、对照来源、箱线与点的定义。每张主图与完整图注在WPS稿件中同页。图色清晰不等于证据更强：来源、分母、truth以及推断范围优先于美观。

全部9张主/补图已检查；导出循环期间发现并修正Fig5b文字碰撞和S3集合大小误用，生成receipt。修复的是展示，不改原始Source Data。
'''
write(P/'02_R7C3G_图版取舍与34子图设计说明.md',fig)

nextp='''# R7C3H：最终叙事签署与出版门户 proof 门

## 本轮冻结状态

PBC_PRIMARY_PROJECT=GO；R7C3G=COMPLETE_EXPERT_EVIDENCE_NARRATIVE_REBUILD；SCIENTIFIC_ENDPOINTS_CHANGED=NO；R7C3F_BASELINE=UNCHANGED；NEW_EDITORIAL_CANDIDATE=LOCAL_REVIEW_VERSION；NEW_EXTERNAL_VALIDATION=NO；SUBMISSION_COMPLETED=NO。

## 下一步要完成的对象

1. 两位作者读Results内嵌版，重点核对新的中心贡献、FCRL3 T-cell反例、PBMC link限定、模拟恢复损失和组织非显著结论。作者资料、CRediT、无funding/利益冲突、AI disclosure等已确认事实继续保留；不推测新增确认结果。
2. 选定唯一主稿上传方案。当前期刊候选 `Manuscript_ExpertRebuilt.docx` 配6张独立PDF；Results内嵌版用于阅读。按实际门户要求选择，不能把两者同时标为Main Manuscript。
3. 补充材料主文件为一个Supplementary Information PDF；另带S1–S10 XLSX及两个Source Data ZIP。S11不伪造为第11个worksheet，外部证据放Source Data2；新增Supplementary_Editorial_Panel_Crosswalk.tsv负责历史C/MR图号与当前E-series主张的37行对应。
4. 冻结上传role、bytes、SHA和版本；若编辑了任何DOCX/图注，则重新WPS导出相关文件并核对相关页，不能继续沿用旧PDF身份。
5. 门户proof核对全部主文/六图/补充材料/声明；在收到实际期刊receipt以前，状态保持未投稿。公共GitHub和DOI记录与此次新稿的身份必须一致后才可标记新版本公开完成。

## GO/HOLD规则

- 核心结果、分母、参考文献和source匹配通过且作者签署明确版本：GO_PORTAL_PREPARATION。
- 仅排版/引用/上传role缺项：HOLD_DOCUMENT_REPAIR；修具体文件，不重开生物学筛选。
- 门户proof与冻结字节不符：HOLD_PROOF_REPAIR，不点击最终提交。
- 新证据确实损害核心推断：仅重开受影响分析，记录新协议和影响范围。

默认不增加疾病、gene/cell/locus，不重跑486k模拟，不用湿实验要求挤占当前目标。这些只在作者决定独立升级到介导机制/全流程误差控制课题时进入新设计。
'''
write(P/'03_R7C3H_下一阶段目标与门控协议.md',nextp)

action=f'''# 99_R7C3G：详细行动记录

日期：2026-10-12。任务：导师级核查本地内容、优化论文叙事、选择重组子图，使用QiTeng v0.3.24.2。执行者：当前Codex主助手；本轮没有虚构第二位外部审稿人或多个独立人工审稿结果。

## 输入与授权边界

用户明确授权科学内容核查、稿件编辑与组图优化。附件是来源材料；不因附件历史阶段要求重启SSc/MG/IgAN。原作者事实与声明保留，新稿是独立editorial candidate。当前任务没有要求再次删除/重建GitHub或向期刊最终提交。

QiTeng ZIP SHA=`d52d3804bf067f9ef469c9bc732ddc1acb4c123a49d086db5cec0b728e8ff17b`，CRC PASS，活动registry为v0.3.24.2。原主稿SHA=`d862dcc8e2e6830b28730f3c1dca5327b3dae5f4afe7a7a0e4147a5df49498aa`。RPv4SHA=`6d9de404fdcdadde28a8e4562a7f9c96ca7bfecbb75600ef79ecd887e29bcbdc`。

## 已执行步骤与真实产物

| 步骤 | 执行内容 | 证据 |
|---|---|---|
| 01 | 提取主稿/RPv4/补充说明；全4_figures身份和内容；8张原图联系表 | INPUT_RECEIPT、ALL_FIGURE_CONTENT、RESULT_SCHEMA_INDEX |
| 02 | 解析2个sourceZIP56成员；482可携带结果；独立37关键终点重算 | SCIENTIFIC_ENDPOINT_REPLAY_QA；SOURCE_ARCHIVE_FULL_INVENTORY；EVIDENCE_AUDIT_STATE |
| 03 | 从冻结源表重绘6主图和3补图，不修改拟合 | 9×PDF/SVG/PNG、34-panel source map、FIGURE_VALUES |
| 04 | 33项段落改写/重排、2种英文稿、SI、投稿信draft | before/after ledger、paragraph move map、4DOCX |
| 05 | 隐藏WPS COM只读导出，原DOCX身份不变 | 4/4 WPS receipt，4PDF |
| 06 | 页面边界、参考顺序、6主图/3补图、源文件一致性、页图注一致性 | {D['pass']}/{D['checks']} machine QA；56页PNG及当前contact sheets |
| 07 | 全工作区当前路径/bytes/mtime/SHA inheritance；所有46图片用途；15主张上限 | 当前{I['files']:,}文件索引；46-image ledger；claim-evidence map |
| 08 | 23项baseline再验收、报告与提交资产身份、打包CRC/SHA | BASELINE_23_ASSET_PRESERVATION；release receipt |

本轮安装了此前缺失的matplotlib及其依赖，使用bundled Python，不改变全局用户环境。确切版本见ENVIRONMENT_VERSIONS.json。DOCX通过python-docx创建；PDF后台使用kwps.Application ExportAsFixedFormat17，无LibreOffice。Figure vector PDF由matplotlib生成；目视页PNG由PyMuPDF生成。

## 异常、修复及保留边界

- portable结果初次遇到两历史IgAN零字节表：调整为明确未产出占位，不填充结果，不影响PBC门。
- 组织图初版按错误control字符串筛选，assert阻止绘图；改用实际CONTROL_HEMANGIOMA_NONLESION记录，确认5+5后绘图。
- 符号字体/文字碰撞在新图导出阶段修正；Fig5b分开variant/PIP/included；Fig1d显式写3例结局。
- 新S3初版错误用17行intersection表作为R12全集，目视/源表复查发现；改用frozen identity JSON19/17并加入自动assert。散点明确只显示17共同成员。
- 旧三正控PF50≈.004与当前CD8_ET PF50≈.992不一致：登记为旧展示被当前模型来源替代，不覆盖历史源字节。
- S8旧position-only ceiling与S11 regional caQTL后续结果：文字及SI明确优先级。
- peak–gene link最佳PBMC与NK disease-QTL层区别：新增Methods/Results/legend边界，不把不同cell标签拼成介导证明。
- 两类2,568计数、14comparison-model行分别说明：相同数字不等于相同统计对象。
- WPS初版稀疏跨页：字体行距与references布局微调、内嵌图块自然流动；最终候选24页、阅读版25页、SI6页、cover1页。旧多余页预览移入VISUAL_REVIEW_SUPERSEDED，不作为当前56页验收。

## 关键数据与安全继承

原baseline23/23全部重新hash匹配。两个Source DataZIP与工作簿不改字节。没有新增GWAS/SuSiE拟合，没有重跑全部模拟，没有用后验筛选新gene/cell，没有重开已归档疾病。当前全文件身份快照为{I['files']:,}文件、{I['GiB']:.3f}GiB、14reparse跳过、0枚举错误；{I['fresh_files']}新增/变更文件fresh SHA，其余复用同日hash且要求size/mtime精确相同。审计索引是时间快照，之后生成的本报告/release另由release manifest逐项验收。

- 原S10含27个历史C-series主张和10个MR镜像记录；当前重新组图后不能继续照抄旧panel地址。新增crosswalk明确逐行定位，其中C17旧position-only解释由S11更新，当前E-series主张ID与历史C-series分开。

## 成果与后续复用

最有价值的13类资产：疾病statistics/sourceLD、OneK genotype/covariate/donor inputs、variant harmonization、PF10/PF50模型身份、6923registry与对称freeze、642signalpair和fit结果、matched-input四臂、486000渠道模拟、TenK分子资源验证、FinnGen/CASCADE外部链、targeted donor与空间边界、向量图/稿件再生脚本、行动记录/版本/license/provenance。前11类是科学/工程复用，后2类是可审计交付。历史MG/IgAN/SSc失败记录供设计借鉴，不能充当前PBC重复验证。

## 最终裁决与下阶段

PBC=GO；R7C3G=COMPLETE_EXPERT_AUDIT_AND_EDITORIAL_REBUILD；NEXT=R7C3H_FINAL_NARRATIVE_AND_PUBLISHER_PROOF。新稿文件和图注均是明确独立版本，尚未标记新版作者批准、GitHub发布或期刊提交。不存在新增强制大文件下载/本地重算任务。

本轮输出完整中文专业评估、可编辑英文稿、WPS PDF、6主图/3补图、全部source及QA映射、可再生代码和ZIP。最终发布包hash/CRC/成员数见release目录外置RELEASE_RECEIPT.json；不将ZIP自身hash写入其内部以避免循环身份。
'''
write(P/'99_R7C3G_详细行动记录_20261012.md',action)

passes=[('1','Scope/current-state','RPv4 and current R7C3F read; baseline preserved'),('2','Central claim and evidence ceiling','15-claim map; no causal/newgene superiority inflation'),('3','Methods–Results mirror','Original fit specifications retained; PBMC link contextualized'),('4','Abstract/Introduction moves','126-word abstract and question-led roadmap'),('5','Results argument/evidence','Six ordered modules; boundaries and bridges preserved'),('6','Discussion interpretation','Contribution first, competing explanations, statistical/biological limits'),('7','Panel ownership and ledger','46 original image decisions;34 current panel-source rows'),('8','Compression adequacy','Remove duplicate panel functions; keep nulls, costs and model counterexample'),('9','Source/numerical/reference checks','37 replay;19-reference first occurrence;23baseline'),('10','Render/reader/submission roles','WPS56 pages;9final masters;unique main/supp/source roles')]
tsv(Q/'QITENG_TEN_PASS_RECORD.tsv',[{'pass_id':a,'governance_task':b,'execution_evidence':c,'status':'EXECUTED_PROJECT_REVIEW_NOT_SKILL_BEHAVIOURAL_TEST'} for a,b,c in passes])
for name in ['LICENSE','LICENSE_CONTENT.md','NOTICE.md']:
 shutil.copy2(R/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'/name,O/name)
for p in P.glob('*.md'):shutil.copy2(p,O/'07_Reports'/p.name)
# Narrow, correct reproduction contract for this editorial stage.
for p in C.iterdir():
 if p.suffix in ['.py','.ps1']:
  dest=O/'09_Code';dest.mkdir(exist_ok=True);shutil.copy2(p,dest/p.name)
for name in ['SCIENTIFIC_ENDPOINT_REPLAY_QA.tsv','SOURCE_ARCHIVE_FULL_INVENTORY.tsv','EVIDENCE_AUDIT_STATE.json','COHORT_OUTCOMES_RECOMPUTED.tsv','A2_TO_M_RECOMPUTED.tsv','ALL_PORTABLE_RESULT_CONTENT_INDEX.tsv','LOCAL_CURRENT_IDENTITY_STATE.json','ALL_LOCAL_TOP_LEVEL_SUMMARY.tsv','INPUT_RECEIPT.json']:
 shutil.copy2(A/name,Q/name)
readme='''# R7C3G expert evidence audit and editorial candidate — 2026-10-12

Start with `07_Reports/00_R7C3G_执行摘要_证据主线与最终裁决.md`, then read the Results-inline review manuscript. This release preserves the scientific endpoints and immutable R7C3F baseline while rebuilding argument flow and figure ownership.

## File roles

| Role | File |
|---|---|
| Journal candidate editable main, figures at end | 01_Manuscript/Manuscript_ExpertRebuilt.docx |
| WPS parity copy of candidate | 01_Manuscript/Manuscript_ExpertRebuilt.pdf |
| Reading/review main, figures with Results | 01_Manuscript/Manuscript_AuthorReview_InlineFigures.docx and .pdf |
| Six independent main figure masters | 02_Figures/Figure_1.pdf … Figure_6.pdf |
| Editable masters and reading raster copies | Corresponding SVG and 300dpi PNG |
| Three supplementary figure masters, also inside SI | Figure_S1–S3 PDF/SVG/PNG |
| One combined supplementary information | 03_Supplement/Supplementary_Information_ExpertRebuilt.pdf |
| Original workbook | 03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx |
| Full primary and bounded external aggregate evidence | 05_Source_Data/Source_Data_1*.zip and Source_Data_2*.zip |
| Editorial cover letter draft | 04_Cover/Cover_Letter_ExpertRebuilt_DRAFT.docx |
| Source/figure/claim/edit/QA audit ledgers | 06_QA/ |
| Chinese expert analysis/action record | 07_Reports/ |
| Editorial-stage regeneration scripts | 09_Code/ |

Do not upload both main versions as two Main Manuscripts. Exact-version author review and actual publisher proof remain pending; no journal submission/DOI/new GitHub editorial release is asserted here.

The original S10 ledger preserves its historical figure metadata. Use `03_Supplement/Supplementary_Editorial_Panel_Crosswalk.tsv` for all 27 C-series and 10 MR-series current destinations; C17 chromatin status is superseded by S11. Current E-series claim IDs are distinct.

## Regeneration and source contract

Run stage scripts in this dependency order: 01 inspect → 02 scientific replay → 03 figures → 04 documents → 07 current asset maps → 04a historical crosswalk → 05 WPS export → 06 machine QA → actual visual review → 08 packaging. Packaging rejects stale visual-review receipts. Scripts use the existing `H:/SCI2/YR1` frozen R7C3F source package and donor-aware prior-stage evidence. They are project-stage scripts, not a standalone reimplementation of original GWAS/fine-mapping from raw inputs. The scientific analysis repository retains those upstream tools. Run Python scripts with the bundled Python recorded in the action report; 05 exports DOCX via hidden Windows WPS COM. Source archives and workbook are byte-identical to the previous candidate. Script06 performs machine checks, while the separate visual receipt records completed review judgement.

This release contains aggregate evidence, not source genotype BED/BAMs or donor pseudobulk matrices. Third-party source terms remain in force. Existing author-owned code is under the project's MIT licence; author-owned manuscript text, newly drawn figures and shareable aggregate outputs follow the existing CC BY4.0 scope. No third-party asset is relicensed by this README. Consult the repository licence and source manifests.

The full local ~39k-file identity inventory remains in `5_analysis/R7C3G_ExpertNarrative_20261012`, outside this reader package. Counts are snapshot-specific. Machine QA pass does not establish causal mediation, universal algorithmic superiority or editorial acceptance.
'''
write(O/'00_START_HERE.md',readme)
gallery=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>R7C3G Figure Review</title><style>body{font:17px Arial;max-width:1100px;margin:30px auto;color:#26313e}img{width:100%;height:auto;border:1px solid #ddd}section{margin:32px 0}a{color:#2166ac}</style><h1>R7C3G：六主图与三补图</h1><p>用于审阅图版顺序和证据边界。对应源表、图注与统计单位见06_QA及英文稿。</p>']
for n in [1,2,3,4,5,6,'S1','S2','S3']:
 gallery.append(f'<section><h2>Figure {n}</h2><p><a href="02_Figures/Figure_{n}.pdf">Vector PDF</a> · <a href="02_Figures/Figure_{n}.svg">Editable SVG</a></p><img src="02_Figures/Figure_{n}.png" alt="Figure {n}"></section>')
write(O/'FIGURE_REVIEW_GALLERY.html','\n'.join(gallery)+'</html>')
roles=[]
for folder in ['01_Manuscript','02_Figures','03_Supplement','04_Cover','05_Source_Data']:
 for p in sorted((O/folder).iterdir()):
  if not p.is_file():continue
  role='READING_OR_EDITABLE_MASTER'
  if p.name=='Manuscript_ExpertRebuilt.docx':role='MAIN_CANDIDATE_SELECT_EXACTLY_ONE'
  elif folder=='02_Figures' and p.suffix=='.pdf' and '_S' not in p.stem:role='INDEPENDENT_MAIN_FIGURE'
  elif folder=='03_Supplement' and p.suffix in ['.pdf','.xlsx','.tsv']:role='SUPPLEMENT_UPLOAD'
  elif folder=='05_Source_Data':role='SOURCE_DATA_UPLOAD'
  elif folder=='04_Cover' and p.suffix=='.docx':role='COVER_DRAFT_EXACT_VERSION_REVIEW_REQUIRED'
  roles.append({'file':str(p.relative_to(O)).replace('\\','/'),'role':role,'bytes':p.stat().st_size,'sha256':sha(p)})
tsv(O/'UPLOAD_ROLES_AND_IDENTITIES.tsv',roles)
checks=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='checksums.sha256':checks.append(f'{sha(p)}  {p.relative_to(O).as_posix()}')
write(O/'checksums.sha256','\n'.join(checks)+'\n')
zp=L/'CMM_R7C3G_ExpertEvidenceAudit_NarrativeRebuild_20261012.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(O).as_posix())
with zipfile.ZipFile(zp) as z:
 assert z.testzip() is None
 for line in z.read('checksums.sha256').decode('utf-8').splitlines():
  hh,n=line.split('  ',1);assert hashlib.sha256(z.read(n)).hexdigest()==hh,n
 result={'zip':zp.name,'bytes':zp.stat().st_size,'sha256':sha(zp),'crc':'PASS','internal_sha256':f'{len(checks)}/{len(checks)} PASS','entries':len(z.namelist()),'machine_checks':f"{D['pass']}/{D['checks']} PASS",'science_replay':'37/37 PASS','visual_pages':'56/56 reviewed','baseline':'23/23 unchanged','new_version_submission':'NOT_EXECUTED'}
write(zp.with_suffix('.zip.sha256'),result['sha256']+'  '+zp.name+'\n');write(L/'RELEASE_RECEIPT.json',json.dumps(result,ensure_ascii=False,indent=2))
shutil.copy2(P/'99_R7C3G_详细行动记录_20261012.md',L/'99_R7C3G_详细行动记录_20261012.md')
print(json.dumps(result,ensure_ascii=False))
