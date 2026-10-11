# CMM R4A12FG7 执行摘要：Source-matched LD 最小访问包与主数据触发器

日期：2026-09-13

## 最终判定

- `PROJECT = CONDITIONAL_GO`
- `R4B = HOLD`
- `C1_count = null`
- IL12RB2 all-sex 分支：`ACCESS_PACKAGE_READY_SOURCE_LD_NOT_YET_RECEIVED`
- 2026 female/male SSc 主数据：`NOT_OBTAINED`
- 下一计算阶段：**仅在 source LD 到达后触发 R4A12FG8**；若 primary sex-specific bytes 先到，则立即返回 chr22/SYNGR1 主线。

## 本轮真正新增

1. FG6 release 独立复核：SHA-256 `28c7517c699065142140631c09528ab2b86490be498c019fd3111e88ef35cd54`，ZIP CRC PASS，内部 checksum 63/63 PASS。
2. 对 TenK10K v3 公共代码做代码级追踪后确认：eQTL multivariant-coloc 并不需要四套细胞特异LD；管线使用同一 TenK10K genotype bfile，对每个基因生成一个 ±100 kb signed PLINK `r` matrix。
3. 对 IL12RB2，原生派生对象可明确请求为：
   - `resources/ld/eqtl/tenk10k_phase1/chr1/ENSG00000081985.bim`
   - `resources/ld/eqtl/tenk10k_phase1/chr1/ENSG00000081985.ld`
4. 因而优先级从“申请475 GB受控WGS”纠偏为：**先请求这对原生派生文件；只有不能直接分享时才走EGA受控WGS。**
5. 冻结了 1,366 个公共 IL12RB2 eQTL variant manifest、891个R13×NK exact common set、四细胞source-CS manifest和三个必需anchor。
6. 已生成收件即运行的 source-LD validator，以及EGA获批后的安全重建脚本。

## 为什么这一变化重要

FG6 失败的是 external-reference signal coverage，而不是IL12RB2生物学。原分析代码已经生成过目标基因的source LD；如果作者可以分享该aggregate matrix，既避免reference shopping，也避免不必要获取大规模individual-level WGS，且最贴近原始SuSiE/coloc实现。
