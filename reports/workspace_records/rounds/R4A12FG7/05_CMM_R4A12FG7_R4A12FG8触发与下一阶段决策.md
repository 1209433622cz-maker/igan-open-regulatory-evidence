# CMM R4A12FG7：R4A12FG8触发条件与下一阶段决策

## 当前不自动启动FG8

FG7完成的是 access package，不是source-LD结果。下一计算阶段必须由外部数据触发。

## Trigger A — PRIMARY_BYTES_READY（最高优先级）

2026 SSc female/male full summary到达并通过H6：立即中断IL12RB2支线，回到chr22/SYNGR1 primary branch。

## Trigger B — AUTHOR_DERIVED_LD_READY

收到native `ENSG00000081985.bim/.ld`：启动 **R4A12FG8 — Source-LD Reproduction + Multisignal Adjudication**。

## Trigger C — EGA_ACCESS_GRANTED

若作者派生LD不能分享但`EGAD50000002377`获批：在机构受控环境重建native-like LD；重建文件先与公开pipeline规则核对，再进入FG8。

## Trigger D — ACCESS_PENDING

材料已准备但尚未获批：不再继续换external panel，不扩细胞、不扩1 Mb、不启动caQTL。IL12RB2保持`SUMMARY_ONLY_SOURCE_MATCHED_LD_REQUIRED`。

## 当前推荐的实际下一动作

**先发送/提交最小derived-LD请求；并行准备EGA申请，但不要为了推进阶段编号继续做新的生物学分析。**
