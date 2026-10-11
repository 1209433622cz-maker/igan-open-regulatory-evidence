# R7C2 npj Genomic Medicine 格式转换与 claim 重定位

## 已完成的格式门

- 标题改为无标点的 12 词标题：`Input matched multisignal colocalization clarifies regulatory assignments at primary biliary cholangitis loci`。
- 摘要改为无小标题单段格式，共 137 词，低于 150 词。
- `Background` 改为 `Introduction`。
- 取消独立 `Conclusions` 章节，将结论并入 Discussion 末段。
- 保留 Results 与 Methods 小标题；Discussion 不使用小标题。
- 将 BMC declarations 改为 Nature Portfolio 的 Ethics statement、Data availability、Code availability、Acknowledgements、Author contributions 与 Competing interests。
- 图 1-6 单独提供 PDF/PNG/SVG；图注保留在主文末尾。
- 生成 Supplementary Information 导航文件，并保留机器可读 Excel/ZIP 作为单独 source-data uploads。

## claim ceiling

允许：输入匹配后仍存在双向重分类；source-aware multi-signal 分析提高归因可解释性；IL12RB2-NK 在另一疾病研究系统获得有边界支持；疾病-eQTL 与疾病-caQTL 加 peak-gene link 构成三角信号一致性。

禁止：普遍优越的新算法；完全独立疾病复制；直接 eQTL-caQTL 共定位；染色质介导；治疗方向；功能机制已经证实。
