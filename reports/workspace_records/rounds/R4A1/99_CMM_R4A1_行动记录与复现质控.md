# CMM R4A.1：行动记录与复现质控

日期：2026-09-08。本轮未修改历史输入文件；含续推进新增报告8份，新增R4A1数据/代码目录。

## 已完成

1. 阅读并梳理用户所列22份材料及粘贴历史，形成逐文件评价。
2. 核查54篇矩阵的行数、唯一ID、年份和范式；明确本地缺少旧矩阵指向的54个独立MD。
3. 读取官方GWAS Catalog新版API文档，采用pubmed_id查询并加入GCST009131阳性控制；记录0-result与HTTP失败的区别。
4. FinnGen官方网页与浏览器前端定位公开读接口，取得gene/variant/region JSON；先检查公开认证状态，未绕过登录。
5. 复现IRF4 rsID错误空结果，按dbSNP等位信息切换canonical键成功。
6. 下载TenK10K gene-level与SuSiE包；SuSiE停滞后使用Range下载，分段长度与Content-Range检查，最后与官方MD5比对。
7. 全部56个细胞文件解析；在所有有效gene-level P上计算探索性within-cell BH；失败标签/未列出分别记录。
8. 提取IRF4、BCL11A、RPL3、PDGFB及探索候选SYNGR1、AL031590.1的gene-level和CS结果。
9. 确认IRF4–B_naive单变异CS，记录PIP=0.999308641371514，不转换为GWAS PP4。
10. 识别BCL11A远距离获取窗口风险及chr22多基因竞争；写入v3修订，不伪称为未看结果前预注册。
11. 生成数据manifest、SHA256、state JSON、可复现脚本和外部请求草稿。
12. 用户要求继续后补查旧GWAS summary服务（HTTP410）；追踪FinnGen区域接口，显式pmax=1取得11,604条IRF4 B系nominal记录。
13. 确认FinnGen B_naive同lead–IRF4 P=0.6728，与TenK10K强信号支持程度不同；修订执行摘要与下一目标，同时保留阳性/非显著证据。
14. 新增默认P过滤回归测试，最终共6项测试；完整续推进过程见06报告。

## 完整性与语义验证

| 核查 | 结果 |
|---|---|
| gene-level官方MD5 | b5cd2ee1f34f90539ebf6683dcd35a2e：PASS |
| SuSiE官方MD5 | f321c719030cc837cf27e09cd2ea6b65：PASS |
| 两ZIP内部CRC | PASS |
| gene-level细胞文件 | 28；403,011行；每cell内gene ID不重复 |
| gene-level有效值与失败标签 | 401,999有效 + 1,012非数值状态 = 403,011 |
| SuSiE细胞文件 | 28；4,193,682行；PIP范围[0,1]及finite检查通过 |
| 主/探索候选CS成员 | 1,064行 |
| 三精确lead扫描SuSiE全包 | 命中1行：IRF4 B_naive |
| 代码验证 | 6 tests PASS：BH已知答案、缺失≠零、rsID回归、原始CS独立复核、默认P过滤、state边界 |

CSV/TSV为分析中间表，不产生Excel工作簿。gene-level与SuSiE压缩包内的.tsv实际上为CSV，已按真实header读取；源文件保留原字节。

## 实际未完成

- male/female SSc summary获取；
- FinnGen完整nominal/fine-map/peak–gene release接入；
- 参考FASTA REF校验、indel左对齐、LD矩阵重建；
- 正式coloc、多信号三方共享测试、效应方向复制；
- 疾病组织、空间、药物或论文主结果分析。

本轮测试覆盖接入/描述性筛查层，未以模拟阳性冒充真实生物学结果，也没有运行SSc端到端管线。

交付前发现输入inventory的文件名过滤会误排除历史文件“05_CMM_R4A_GO_NO-GO_与下一阶段R4A1目标.md”（它包含下一阶段名称）。已将过滤改为本轮报告前缀，重新生成22份历史输入清单；最终检查8份新报告的本地链接及全部交付哈希。此修复只改变inventory覆盖，不改变分子统计结果。

## 原始来源追踪

`R4A1/source_manifest.tsv`有40条记录：原始API/网页/前端说明响应及两个原始数据包。HTTP错误响应被明确标记，不纳入有效生物学分析。

`evidence/access_log*.json`及各主题`*log.json`保存读取时间/URL/状态。部分自适应探针只保存源响应及清单URL；未伪造其原始访问时间，空时间字段表示未单独持久化。TenK10K verified_utc表示本地校验时间，不等同于传输开始时间。

公开浏览器会更新，因此复现当前数字应使用已哈希快照，而非假定将来同一URL永远返回相同内容。源build/allele文档与本地reference验证是不同状态，当前不提升为完整ANALYSIS_READY。

## 联系与用户身份

本轮未发送任何邮件、未提交FinnGen表单、未代表用户填写姓名/机构/研究承诺。04报告给出了两份可审阅请求草稿以及所需最小文件清单。

## 下一阶段决定

`R4A1B_GWAS_AND_REGIONAL_QTL_ACCESS_IRF4_B_CELL_SIGNAL_TEST`。

继续SSc项目，R4B暂缓。没有C1结果是未测试，不是三个locus生物学阴性。保持原始材料和本轮修订并存，避免后续把旧预期与新实测混为一谈。
