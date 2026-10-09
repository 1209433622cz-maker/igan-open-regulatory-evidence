# R7B4B 作者补全与最终投稿 QA 冻结协议

## 1. 阶段目的

R7B4B 只完成作者负责的信息、机构口径和投稿前最终一致性检查。R7B4A 已冻结研究问题、分析范围、数值结果、主图、补充材料和 Human Genomics 投稿格式；本阶段不得新增疾病、位点、基因、细胞、阈值或结果导向分析。

## 2. 必须由作者提供并确认的真实信息

1. 全部作者姓名、顺序、学位与 ORCID；
2. 编号对应的完整单位与地址；
3. 通讯作者姓名、邮寄地址、电子邮箱和电话；
4. 逐作者 CRediT 贡献；
5. Funding 机构、项目名称与 grant number，或明确的无资助声明；
6. 财务与非财务 competing interests；
7. 本机构对二次使用公开、去标识数据的 ethics、exemption 或 waiver 准确措辞；
8. Acknowledgements；
9. APC 支付、减免或协议覆盖路径，以及开放许可选择；
10. 全体作者对最终稿和投稿行为的明确批准；
11. 所在机构在投稿当日对期刊分区和认可口径的复核结果。

不得推测、补写或根据常见格式生成上述事实。

## 3. 固定输入

- R7B4A Human Genomics 主稿 Markdown 与 DOCX；
- Figure 1–6 的 PNG/PDF/SVG 冻结版本；
- 920×300 graphical abstract；
- Additional file 1 与 Additional file 2；
- cover letter 草稿、upload map 与 submission checklist；
- R7B4A 42/42 QA 记录；
- 公共仓库标签 `r7b4a-human-genomics-interface-2026-10-10`。

## 4. 执行顺序

1. 将作者提供的信息录入作者表单，并逐项保留来源或书面确认；
2. 在主稿、cover letter 和投稿系统字段中同步替换占位符；
3. 删除主稿末尾仅供内部使用的 `Author metadata completion gate` 页面；
4. 复核标题、作者顺序、单位编号、通讯信息、Funding、CRediT、利益冲突与 ethics 在所有载体中的一致性；
5. 由机构渠道重新确认 Human Genomics 的投稿当日分区、APC 和许可条件；
6. 使用 WPS Writer 后台重新导出 reviewer PDF，不使用 LibreOffice；
7. 逐页检查主稿和 cover letter，执行占位符零残留、图件身份、补充文件 CRC、引用连续性、声明完整性和上传映射 QA；
8. 生成最终提交候选包，记录精确 SHA-256；
9. 只有在通讯作者明确授权提交后，才可在外部投稿系统执行提交动作。

## 5. 硬性通过条件

```text
AUTHOR_METADATA_COMPLETE = YES
ALL_PLACEHOLDERS_REMOVED = YES
ALL_AUTHOR_APPROVAL = YES
ETHICS_WORDING_CONFIRMED = YES
FUNDING_AND_COI_CONFIRMED = YES
APC_AND_LICENCE_ROUTE_CONFIRMED = YES
INSTITUTIONAL_JOURNAL_QUALIFICATION_RECHECK = PASS
MAIN_DOCX_PDF_PARITY = PASS
COVER_LETTER_ONE_PAGE_WPS = PASS
FIGURE_AND_SUPPLEMENT_IDENTITY = PASS
FINAL_SUBMISSION_QA = PASS
SUBMISSION_AUTHORIZED_BY_CORRESPONDING_AUTHOR = YES
```

任一条件失败时，项目保持 `HOLD_HUMAN_GATE`，不得把 R7B4A 的技术完成写成已经投稿。

## 6. 合法出口

- 全部通过：进入正式投稿与提交回执归档；
- Human Genomics 资格或费用路径失败：按已冻结顺序转投 BMC Medical Genomics；
- 需要更强方法学定位且作者接受更高编辑门槛：再考虑 Genetic Epidemiology；
- 任何改投只允许改格式与期刊定位，不重开生物学候选或结果筛选。
