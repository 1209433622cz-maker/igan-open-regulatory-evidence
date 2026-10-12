# CMM R4A12FG6：FG5 交付包与脚本独立验收

## 1. 包完整性

输入包：`CMM_R4A12FG5_ExternalLD_ThreeCellAdjudication_2026-09-13.zip`

- ZIP SHA-256：`5e9c13d4a7ccd8df89786ab9370835719ffc0cd9eef5fa6afe42a42215da5ad8`
- ZIP CRC：PASS
- 包内文件：26
- `checksums.sha256`：25/25 PASS
- 十个独立附件与 ZIP 对应成员：10/10 字节一致

首次校验按解压根目录解释清单路径时得到 0/25；检查后确认清单路径实际相对于 ZIP 顶层目录。更正基准后 25/25 全部通过。该过程保留在 `fg5_release_integrity.json` 中，防止把校验器的路径错误误报成源包损坏。

## 2. 打包卫生

ZIP 将两个 Python `__pycache__/*.pyc` 纳入校验清单。它们没有改变科学结果，但依赖本机 Python 版本且不可审阅，不应作为研究交付物。R4A12FG6 发布包排除所有 `.pyc` 和 `__pycache__`。

## 3. 输入脚本审计与修正

FG5 附带的 LD 构建脚本假定系统可调用 `plink2`，并对 `gwas_rsids` 全列直接做 duplicate hard-fail；current 891 中含空/多 rsID 且有两个多等位位点复用 rsID，因此原实现无法稳健完成。其默认历史路径也不对应重组后的 canonical workspace。

本轮替换为直接读取 PLINK1 BED/BIM/FAM 的版本：

- 仅接受单一 `rs\d+`；
- 重复 rsID、空 rsID、多 rsID进入 mapping audit，不做猜测；
- 跨 build 以 rsID 加无序等位基因集合匹配；
- BED 原始剂量按 BIM A2 解码，并显式翻转到 current GRCh38 ALT；
- 输出 signed LD、ALT dosage、完整 mapping audit、AF 与 z–LD 诊断；
- residual 只报告，不删点。

直接解码器用历史 EUR503 503×1,555 剂量矩阵独立验证：1,555 个变异、503 人逐值相同，最大绝对差 0。

三细胞下载脚本在 Windows 上真实运行时暴露了 progress manifest 临时文件竞态。修复包括线程唯一临时名、清单锁、替换重试和已通过 extract 的 SHA/CRC 复用。随后从断点完成，三个成员最终全部 PASS；科学数据以整成员 CRC 和解压字节数为权威，不依赖中间清单是否曾写入成功。
