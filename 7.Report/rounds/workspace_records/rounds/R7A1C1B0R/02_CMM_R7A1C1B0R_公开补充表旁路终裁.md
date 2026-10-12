# 公开补充表旁路终裁

## 字节验收

| 文件 | bytes | SHA-256 |
|---|---:|---|
| Supplementary Data 1–18 | 2,585,688 | `fc42c213d4a3b6a029fbb51c7f4806a6ae9101f764510a20df3633d81140bd8d` |
| Source Data | 16,954,380 | `23ca09f165508f92fde22c52e3f0561d02852247a60a0e820c51f8ea56fb00a1` |

两者均来自 Springer 官方二进制端点，并通过 XLSX ZIP signature。

## 实际命中

Supplementary Data：

- human liver Supplementary Data 2：FCRL3 是 Naive B marker，`avg_logFC=0.60178, pct.1=0.327, pct.2=0.100`；
- human liver Supplementary Data 2：FCRL3 是 Memory B marker，`avg_logFC=0.53494, pct.1=0.384, pct.2=0.100`；
- mouse liver Supplementary Data 16：`Il12rb2` 是 GZMC− NK marker；该行不属于人 PBC donor gate；
- 五个 HRR accession 或 PBC_liver1–5：0 命中。

Source Data：target 命中 0，donor ID 命中 0。

## 判定

```text
POOLED_HUMAN_FCRL3_B_MARKER = SUPPORTIVE
HUMAN_IL12RB2_NK_MARKER = NOT_PRESENT
DONOR_TARGET_MATRIX = ABSENT
LIGHTWEIGHT_BYPASS = FAIL_NO_DONOR_TARGET_MATRIX
```

这些表支持 FCRL3 的人肝 B-cell 定位，但无法回答同一 target 是否在至少 3/5 个 PBC donors 中稳健检测。不能以 pooled marker P 值、pct.1 或小鼠 IL12rb2 替代预注册 donor gate。

来源：[PBC liver 原始论文](https://www.nature.com/articles/s41467-024-53104-9)。
