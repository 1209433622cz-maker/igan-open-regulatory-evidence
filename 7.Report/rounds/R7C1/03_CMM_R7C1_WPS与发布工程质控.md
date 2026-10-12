# R7C1 WPS 与发布工程质控

## 文档构建

- DOCX 由冻结 R7B4B2 Markdown 分支构建，包含 6 个图对象、连续页码与连续行号。
- PDF 使用 WPS Writer COM 后台导出，未使用 LibreOffice。
- WPS PDF 共 32 页，Producer/Creator 元数据包含 WPS 标识。
- 32/32 页均以 150 dpi 渲染为 PNG，并通过 8 张四页 contact sheet 完成视觉检查。

## 视觉结果

未发现图像缺失、跨页裁切、文字重叠、超出页边距、图注错配、异常空白页或 Supplementary Table S11 遗失。新的 Figure 4 在最终版面中可读，四个 panel 与图注含义一致。

## 补充包

Additional file 3 含 25 个 ZIP entries，CRC PASS，并带内部 SHA-256 manifest。第三方 raw archive、个体基因型、BAM、pseudobulk 和权限受限资源未被重新分发。

## 文件哈希

- DOCX: `46ea7585be13b924746e73a7a4b87bacfbcebeec10c7d6e03ed03260d33ef67f`
- WPS PDF: `cb9595c8db8b19166eb7df39589c4f9e941a176feb8db557df210ccb5f97c559`
- Figure 4 PNG: `7e8b241f9963a70fd66f97e50ef6238e5d18f03acba900de1db6526ef7f9831d`
- Additional file 3: `186d2e914c4b3762dd489230820b3e8c3b1cbf2ce0c75412a134bfd5b6dab097`
