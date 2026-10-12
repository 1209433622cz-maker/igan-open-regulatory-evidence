# R5A2A3 交付包独立复核

## 完整性

接收包 `CMM_R5A2A3_chr18_colocABF_smoke_2026-09-14.zip`：

- SHA-256：`1614294be131998aed0518549b6d4a8a13986536646fbf227c18fd11b46fc804`；
- ZIP CRC：PASS；
- 内部 checksum：12/12 PASS；
- 独立 99 行动记录 SHA-256：`eebef448892b0d8221de809e3191cd692ad27c08aef2fe979975b173db623387`，与包内版本逐字节相同。

包内容已分别进入 `7.Report/current/R5A2A3`、`7.Report/rounds/R5A2A3/imported_2026-09-14`、`2_code/06_intake/mg_r5a2a3`、`3_results/04_integration/R5A2A3` 和 `0_admin/protocol/history/R5A2A3`。原始导入物保持不改写。

## 独立复算

接收脚本包含硬编码 Linux 路径 `/mnt/data/r5a2a3_work`。本地复算版只修改输入/输出路径，并将结果写入独立目录 `3_results/04_integration/R5A2A3_recomputed`。

- 3 个疾病表型 × 71 个 cell–gene = 213 项；
- 213 行汇总的最大绝对数值差为 `2.22×10^-16`；
- 非数值字段差异为 0；
- robust shared-signal 数仍为 0；
- `NK_R/ZCCHC2` 仍是唯一 targeted source-LD trigger。

另用官方 R `coloc 5.2.3` 重跑 NK_R/ZCCHC2 的 overall MG 与 LOMG，`p12=1e-6、1e-5、1e-4` 全部与接收结果一致。默认先验下 overall MG `H4=0.4273`、LOMG `H4=0.3363`，均未通过门且高度依赖 p12。

## 排序缺陷与修复

接收脚本使用输入顺序解决完全相同的 SNP posterior，导致 top-SNP 展示表在独立环境中出现 82 个同 rank variant 互换、81 个相同 variant 的 rank 互换，以及各 1 个 top-10 边界成员差异。对相同 variant 的数值最大差仍为 `2.22×10^-16`。

本地脚本已改为先按 variant ID 固定共同变异顺序，再用 variant ID 作为 posterior tie 的次级排序。这是展示层的确定性修复，不改变 PP.H0–H4、shared top、trigger 或科学判定。

机器可读审计：`3_results/00_audit/R5A2A4/R5A2A3_import_and_recalculation_audit.json`。
