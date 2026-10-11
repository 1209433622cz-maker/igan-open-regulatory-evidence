# CMM R4A11：Master Protocol冻结与R4A12目标

日期：2026-09-12

## 1. 为什么本轮不直接运行coloc

2026 SSc female/male summary-statistics 真实字节仍未取得；H6 v2.1 没有输入，疾病层为 `NOT_TESTED`。此时运行 SuSiE/coloc 只能使用旧 overall GWAS、论文 top hits、图像或合成数据，都会改变 estimand 或制造不可发表的 posterior。因此本轮推进点是把真实数据到达后的所有选择提前冻结。

## 2. v11唯一母协议

`protocol/analysis_manifest_v11.json` 现在是唯一机器母版，覆盖此前冲突条款。其关键决定为：

- chr22 rs66578187 为 primary，IRF4 rs12203592 为 secondary；
- D0 固定 ±500 kb、只用 `coloc.abf` 复现原论文方向；
- D1/E1/M1 固定 ±1 Mb primary，±500 kb/±2 Mb 只做 sensitivity；
- primary caQTL 为 FinnGen `l2.NK` target peak；primary eQTL 为 TenK10K NK/SYNGR1；
- FinnGen NK eQTL 和 CD8_TEM 只作预声明 secondary；
- 20 个候选一次性冻结并使用相同规则；
- GRCh38 normalization、variant key、INFO/MAF、ambiguous SNP、duplicate/drop rules 已锁定；
- LD hierarchy、matrix QC、RSS、susieR 0.14.2 与 coloc 5.2.3 参数已锁定；
- D1/E1/M1 必须来自同一个 signal triplet，不能拼接不同 pair 的最大 H4；
- male 使用同一流程，显著/不显著之差不构成性别差异；
- All-8 对 primary 的 rescue 取消。

manifest 校验 70/70 PASS，并实测核对 10 个现有分子 evidence 文件的 SHA-256。

## 3. R4A12的触发条件

R4A12 名称冻结为：

> **R4A12 — Byte-arrival-triggered Harmonization and Coverage Gate**

只有以下任一路径成立才启动：

- female 与 male genome-wide 文件都到达；或
- provider 暂不能发布 genome-wide，但同时提供 female 与 male 的 chr22/chr6 完整预注册区域；
- 每个文件有 build、allele/effect、case/control、N 语义、ancestry、association model 和 provider checksum evidence；
- H6 v2.1 对对应 stratum 返回 exit 0 和 exact PASS。

只有 female 先到时可完成 female receipt/H6 并冻结结果，但 male gate 保持 PENDING，不能形成 sex-specific mechanism 结论。

## 4. 用户取得大文件后的运行步骤

### 4.1 归档

建议目录：

```text
H:\SCI2\YR1\incoming\2026_ssc_sex_specific\
  female.<provider-original-extension>
  male.<provider-original-extension>
  provider_checksums.sha256
  female.metadata.json
  male.metadata.json
```

不要修改原文件。复制 `h6_v2_1/metadata_female_template_v2_1.json` 和 male 模板后，只根据 provider 材料填空。下载后自己算的 SHA-256 写入 `receipt_sha256`；它不能替代下载前已有的 `expected_sha256`。

### 4.2 环境

H6 本体只用 Python 标准库。若要刷新公开入口：

```powershell
python -m pip install -r H:\SCI2\YR1\R4A11\h6_v2_1\requirements.txt
```

已验证当前环境：Python 3.13.7、requests 2.32.5、NumPy 2.3.3、SciPy 1.16.2、R 4.6.0、susieR 0.14.2、coloc 5.2.3、bcftools 1.13、PLINK2 v2.00a3。

### 4.3 先跑测试

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\R4A11\h6_v2_1\RUN_TESTS.ps1
```

应同时看到 73/73 regression PASS 和 28-case hostile suite PASS。

### 4.4 跑female和male

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\R4A11\h6_v2_1\RUN_H6_V2_1.ps1 `
  -InputFile "H:\SCI2\YR1\incoming\2026_ssc_sex_specific\female.tsv.gz" `
  -MetadataFile "H:\SCI2\YR1\incoming\2026_ssc_sex_specific\female.metadata.json" `
  -Label female `
  -OutputDir "H:\SCI2\YR1\R4A12\intake\female"

powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\R4A11\h6_v2_1\RUN_H6_V2_1.ps1 `
  -InputFile "H:\SCI2\YR1\incoming\2026_ssc_sex_specific\male.tsv.gz" `
  -MetadataFile "H:\SCI2\YR1\incoming\2026_ssc_sex_specific\male.metadata.json" `
  -Label male `
  -OutputDir "H:\SCI2\YR1\R4A12\intake\male"
```

输入格式不限于 `.tsv.gz`；plain、gzip/bgzip、bz2、xz/lzma 均可流式读取。实际路径按 provider 原文件改写，不要为了匹配示例而改后缀。

## 5. R4A12验收输出

R4A12 只在 H6 双方 PASS 后创建：

- raw receipt manifest 和 provider-evidence archive；
- GRCh38 FASTA identity/hash；
- normalized female/male 两窗口表和逐原因 drop ledger；
- disease–caQTL、disease–eQTL、caQTL–eQTL 的 pairwise coverage 表；
- allele/variant-order hashes；
- 是否允许进入 signed-LD/RSS 的单一决定。

若 coverage 失败，状态是 `UNTESTABLE`，不会立即运行 coloc。若只有某个资源缺 formal summary/LD，对应 edge 单独保持 PENDING，不用另一个资源替代。

## 6. R4A12之后

只有 coverage PASS 才进入 R4A13 LD/RSS+D0；只有 D0 和 RSS 合格才进入 R4B 的 D1/E1/M1 正式 signal-level analysis。阶段编号表达依赖关系，不表达“必须得到阳性”。

## 7. 当前不再做的循环

在公开字节无变化时，不再把同一端点零命中重新包装为 R4A12、R4A13 等新阶段。公开入口脚本可按需运行；只有 byte gate 变化、作者回复、provider 文件到达或已冻结 evidence 发生可验证更新，才触发项目状态变更。
