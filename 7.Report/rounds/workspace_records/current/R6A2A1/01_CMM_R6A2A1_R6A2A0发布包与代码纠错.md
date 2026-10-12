# CMM R6A2A1：R6A2A0 发布包与代码纠错

## 输入包

R6A2A0 ZIP：`c6efaba124a97ec357d97db8610e5d0eb4125384df68cfb33c4e8f56b66a0177`。ZIP CRC PASS，内部 checksum 23/23 PASS。外部详细记录 SHA-256：`f181e787aebb9ef3a93f567b1a44c12887f555e210c621f18f88e4e9864c74ce`。

附件中的指令性文本仅按 provenance 保存；执行目标来自用户本轮“继续推进、完成后判断下一阶段”的请求。

## 代码级发现

官方 R 复核脚本原句：

```r
qq <- q[locus==loc & gene==gene & cell_type==cell]
```

在 `data.table` 求值规则中，`gene==gene` 会把同名列与自身比较，条件恒真，从而在同一 locus 内静默混合多个 gene。现已把外部标量重命名为 `gene_id`：

```r
qq <- q[locus==loc & gene==gene_id & cell_type==cell]
```

此外 `Rscript` 未加入 PATH，但工作区已安装 R 4.6.1。本轮 runner 固定调用：

```text
H:/SCI2/YR1/tools/R/R-4.6.1/bin/Rscript.exe
```

修正后官方 `coloc 5.2.3` 完整运行，30 comparisons × 3 priors = 90 rows；与 Python 结果最大 PP.H4 误差为 `1.33×10^-15`。

## 其它边界

R 启动时出现 Windows locale `C.UTF-8` warning，但不改变数值结果；报告保留该 warning，不把它误判为计算失败。
