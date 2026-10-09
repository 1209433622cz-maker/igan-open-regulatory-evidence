# R7B4B FINAL SUBMISSION QA 规范

## 1. 两种 QA 模式必须分开

### AUTHOR REVIEW 历史模式

R7B4A 的 42/42 QA 证明作者审阅版的技术接口完整。该模式允许并要求显式作者占位符、内部 `Author metadata completion gate` 页面以及待确认 cover-letter 条目。该结果永久保留，不改写为最终投稿 QA。

### FINAL SUBMISSION 模式

R7B4B 最终模式只接受作者确认后的提交候选版本。它必须：

- 删除内部作者填写页；
- 清除具体作者/声明占位标记；
- 保留正常数字引用方括号；
- 绑定最终 DOCX、WPS PDF 与逐页视觉检查回执；
- 允许页数因真实作者信息和删除内部页而变化，不固定为 31 页；
- 核对参考文献列表连续性和正文首次出现顺序；
- 核对 immutable tag 实际解析提交；
- 复核图件、graphical abstract 和两个 Additional files 的冻结身份；
- 绑定机构分区凭据、全体作者批准和通讯作者投稿授权。

## 2. 明确占位符规则

最终扫描只把以下语义标记视为占位符：

```text
TO BE COMPLETED
AUTHOR CONFIRMATION REQUIRED
LOCAL INSTITUTIONAL DETERMINATION
CRediT CONTRIBUTIONS TO BE COMPLETED
ADDITIONAL ACKNOWLEDGEMENTS TO BE COMPLETED
OPTIONAL AUTHOR BIOGRAPHICAL INFORMATION TO BE COMPLETED
FULL AUTHOR NAMES TO BE COMPLETED
NUMBERED INSTITUTIONAL ADDRESSES TO BE COMPLETED
CORRESPONDING AUTHOR NAME
SIGNATURE BLOCK
```

不得把所有 `[...]` 一律判错，因为 Vancouver 数字引用使用方括号。

## 3. WPS 版本绑定

最终 WPS 回执必须至少包含：

```json
{
  "manuscript_docx_sha256": "...",
  "manuscript_pdf_sha256": "...",
  "cover_docx_sha256": "...",
  "cover_pdf_sha256": "...",
  "wps_creator": "WPS 文字",
  "visual_inspection": "PASS_ALL_PAGES"
}
```

PDF 页数不作为固定常数。通过条件是 WPS 创建者、hash 绑定、页面完整和人工逐页检查全部通过。

## 4. 真实声明门

最终 QA 只能读取作者提供的私密记录并输出 PASS/HOLD 与 hashes，不复制签名、电话、私人邮箱或机构证明到公共资产。必须确认：

- 作者身份、顺序、单位映射和通讯作者；
- ethics/waiver/exemption/not-required 的机构正式判断；
- consent、利益冲突、研究资助、CRediT 与致谢；
- AI disclosure、原创性和未同时投稿；
- APC 路径与研究资助相互独立；
- 投稿当日机构分区凭据；
- 全体作者批准精确最终 DOCX hashes；
- 通讯作者明确授权并由作者本人操作投稿。

## 5. 状态解释

```text
PASS_FINAL_SUBMISSION
```

仅表示所有技术和作者门已绑定到同一最终版本。它不自动执行外部投稿。

```text
HOLD_HUMAN_INPUT_REQUIRED
```

表示科学稿可以继续，但真实作者/机构输入或最终文件尚未齐全。

```text
FAIL
```

表示候选文件存在占位符、版本错配、WPS/图件/补充材料身份错误或其它确定性缺陷。

## 6. 当前执行状态

本轮只运行了 pre-author gate 和空模板下的 FINAL SUBMISSION 预演。返回 `HOLD_HUMAN_INPUT_REQUIRED` 是预期结果，不是把未提供的作者信息判为科学失败。
