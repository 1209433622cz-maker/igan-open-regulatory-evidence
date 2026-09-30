# CMM R7A2A5 投稿资产与合规审计

## 输入身份

- 输入：`CMM_R7A2A4_HostileManuscriptAudit_2026-09-30.zip`
- SHA-256：`c7c50a3637068d13d593f10b182fc0f26c715d8ef53e9d6fdf228c34dd3daaf9`
- ZIP CRC：PASS
- R7A2A4 internal checksum：25/25 PASS

## 核心资产

| 资产 | 字节 | SHA-256 |
|---|---:|---|
| `R7A2A5_HumanGenomics_manuscript_v3.docx` | 55,661 | `adcd802bb744d303e8490c6cae3990ef6eb17dead1486bad0d087e8eec3b5e33` |
| `R7A2A5_HumanGenomics_manuscript_v3_WPS.pdf` | 303,033 | `052ea67842ab6ce4aa4892fe7ab8f2bb23d462dfa5bb34d1e5aa2e35a65ac6e0` |
| `R7A2A5_HumanGenomics_cover_letter_DRAFT.docx` | 38,315 | `2003acc6469855b2422fb4d556371ea36a802df0f81a97cd54fcd4fd3fd0bb91` |
| `R7A2A5_HumanGenomics_cover_letter_DRAFT_WPS.pdf` | 117,258 | `3973aa933ae462e52235b32fdc547c0031b1313dfff468432f95578ad6b02787` |
| `Additional_file_1_R7A2A5_Supplementary_Tables.xlsx` | 71,360 | `83ca2dd87f634b49cbf7ae934ee75aaebee194659cf7b46a0d7a657d439f9b16` |
| `Graphical_Abstract_R7A2A5_HumanGenomics_920x300.png` | 36,558 | `5be7ab6d0ebe0aed1b943150f45e9cfeb564f85807028b953ae3a693bea74946` |

## 主稿检查

- 标题：13 词；
- 结构化摘要：262 词；
- 标准章节和 8 个 Declarations 子标题齐全；
- 参考文献 1–19 连续，正文首次出现顺序 1–19 PASS；
- `preregistered` 未使用，保留 `prespecified, protocol-frozen`；
- TenK10K 明确为 independent molecular-QTL resource replication，并明确不是 independent disease-cohort replication；
- OneK QTL residualized LD 数学定义、PF10/PF50、跨细胞 multiplicity 边界、single-causal 与 multi-signal 区别均保留；
- 组织层结论限定为 detectability/observability，不支持经多重校正的 PBC-specific enrichment；
- 结论限定到 replicated association/signal sharing，expression mediation、mechanism 与 therapeutic relevance 均未被声明为已证实。

## 文档与渲染检查

- DOCX 双倍行距、连续行号、页码：PASS；
- WPS creator 元数据：PASS；
- 主稿 PDF：27 页，文本可抽取字符 >45,000，逐页缩略图审阅 PASS；
- 投稿信 PDF：首次渲染为 2 页，因第二页过短而调整边距/字号/段距；最终为 1 页并复核 PASS；
- 没有调用 LibreOffice。

## 图件检查

- 主图 1–6：独立 PNG，原始像素保持，约 300–320 dpi，每张 <10 MB；
- 图题均 ≤15 词；
- 图形摘要：920×300 PNG，并提供 SVG；
- Supplementary Figures S1–S4：300 dpi；
- 图件表达保留 IL12RB2-NK/FCRL3-B 正证据、FCRL3/CD8_ET 反转、INAVA uninformative control 和 tissue null boundary。

## 补充工作簿检查

工作簿含 Index 与 Supplementary Tables S1–S10，共 11 sheets。内容覆盖 source receipts、冻结比较全集、ABF screen、source-LD QC、SuSiE/signal-pair results、credible-set members、TenK replication、10 个肝组织供者、tissue sensitivity 和 claim-evidence ledger。全部 sheet 已渲染预览；公式数为 0，错误单元格为 0。

## 自动 QA

```text
R7A2A5_FINAL_QA:
  PASS = 55
  FAIL = 0
  BLOCKED_HUMAN_INPUT = 1
  MACHINE_GATE = PASS
  SUBMISSION_STATE = AWAITING_AUTHOR_METADATA
```

人类输入阻塞不是技术失败。所有未知作者信息均保留为醒目占位符，没有推测或虚构。
