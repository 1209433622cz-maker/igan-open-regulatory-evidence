# CMM R4A12FG7-QA 执行摘要：访问包敌意复核与 Source-LD 门控加固

日期：2026-09-13

## 最终判定

- `PROJECT = CONDITIONAL_GO`
- `R4B = HOLD`
- `C1_count = null`
- IL12RB2 all-sex 分支：`ACCESS_PACKAGE_READY_SOURCE_LD_NOT_YET_RECEIVED`
- 2026 SSc female/male 主数据：`NOT_OBTAINED`
- R4A12FG8：`NOT_TRIGGERED`

本轮属于 **R4A12FG7 的质量修订轮**，没有把尚未收到的 source-matched LD 写成分析进展，也没有启动新的生物学分析阶段。

## 本轮新增事实

1. FG7 ZIP SHA-256 为 `99f664e6df35a2fc35549771450898ca25b047f62d7d729da56d3da913a0e574`；CRC PASS，内部 manifest 23/23 PASS，15份外置文件与包内版本逐字节一致。唯一交付瑕疵是 ZIP 含有一个不必要的 `__pycache__/*.pyc`。
2. 本地扫描没有发现 `ENSG00000081985.bim/.ld`，也没有发现已获批的 TenK10K / `EGAD50000002377` VCF。因此 FG8 的数据触发条件仍未满足。
3. 原 FG7 validator 存在一个会改变判定的缺陷：它计算了 `requested_1366_fraction`，却没有把该条件纳入 PASS 核心。只保留37个 CS/anchor 变异（2.71%）的单位矩阵仍被原脚本错误判为 `PASS_SOURCE_LD_STRUCTURAL_GATE`。
4. `validate_received_tenk10k_source_ld_v2.py` 已修复该问题：必须覆盖冻结的1,366/1,366变异、全部等位基因方向、三个anchor及每个source-CS ≥95% PIP，并验证schema、重复项、finite、对称性、对角线和PSD。HOLD返回码固定为2，执行错误为3，所有结果都原子写入JSON。
5. 新版受控重建脚本只对冻结的1,366个公共eQTL变异生成矩阵，自动做预检、结构验收、checksum和工具版本记录。该产物必须标记为 `native-manifest reconstruction`，不能冒充作者原生未截断矩阵的逐字节复制。
6. TenK10K公开代码确认 eQTL LD 与疾病GWAS LD 是两个独立对象：收到TenK10K IL12RB2 LD只能解除分子QTL侧门控，FinnGen疾病侧source-matched LD仍需单独满足。

## 当前可执行动作

最小derived-LD作者请求已经修订到可发送版本，但本轮没有代表申请人对外发送，也没有提交EGA申请。对外请求仍需申请人/PI的真实姓名、机构和机构邮箱；EGA还需要正式账户、授权人员、机构签署和安全环境材料。

## 下一阶段

- 作者派生 `.bim/.ld` 到达：运行严格收件脚本，通过后才触发 **R4A12FG8 — Source-LD Reproduction + Multisignal Adjudication**。
- EGA获批且受控VCF到达：在机构安全环境运行重建脚本；通过分子QTL门后再进入FG8。
- 2026 SSc female/male summary statistics 先到：立即优先回到 chr22/SYNGR1 主线。
- 所有触发均未发生：维持 `ACCESS_PENDING`，停止增加替代LD panel、细胞类型和窗口。

