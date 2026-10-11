# R4A8 本地运行说明

环境已在本机检查通过：D:/bioinfor/python.exe（NumPy、SciPy、requests），C:/Program Files/R/R-4.6.0/bin/Rscript.exe（susieR 0.14.2、jsonlite）。RUN脚本仅在缺失时安装依赖；R新增包放在R4A8/R_library，不覆盖系统包。后台文档渲染遵循用户要求使用WPS；本轮只有Markdown、数据和脚本，无需渲染。

## 你现在只需下载三个文件

打开 [Zenodo 6614170 官方记录](https://zenodo.org/records/6614170)，下载 EUR 的bed、bim、fam（不要下载EAS/AFR）。保存至：

`H:\SCI2\YR1\R4A8\raw\`

|文件|页面大小|MD5|
|---|---:|---|
|[1000G_EUR.bed](https://zenodo.org/records/6614170/files/1000G_EUR.bed?download=1)|231.4 MB|a163c74ea92676c9ada76fe5eb3b2ec9|
|[1000G_EUR.bim](https://zenodo.org/records/6614170/files/1000G_EUR.bim?download=1)|51.5 MB|81b1ee40a05ef5be98ad3e496c71d708|
|[1000G_EUR.fam](https://zenodo.org/records/6614170/files/1000G_EUR.fam?download=1)|9.6 kB|669a4260fda7a9e1dd7df374aff294ea|

不要改文件名，不用解压。若浏览器也下载失败，保留失败信息；重复计算不能解决网络阻断。

## 下载后运行这一条 PowerShell 命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "H:\SCI2\YR1\R4A8\RUN_R4A8.ps1" -SkipDownload
```

`ExecutionPolicy Bypass`仅作用于这一进程，不永久修改系统策略。脚本默认使用当前机器已核验的Python/R路径；换电脑时先编辑脚本中的taskPython、taskR。

若希望脚本尝试下载，去掉 `-SkipDownload`。下载采用4MiB分段、每段最多3次尝试，并复用已有完整分片；最终MD5不通过会停止。服务器无法提供有效Range时可能失败，改用浏览器下载后再运行上面的命令。

仅检查/补齐环境：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "H:\SCI2\YR1\R4A8\RUN_R4A8.ps1" -SetupOnly
```

## 会发生什么

1. 三个参考文件MD5、503样本、BED格式和文件长度检查。
2. 与本地R4A5原始overall GWAS核对IL12RB2 1842行及signed-Z。
3. 用rsID+位置唯一匹配；只恢复可靠非回文SNP的另一等位基因，不把BIM的A1/A2冒充基因组REF/ALT。回文、方向不明、未规范indel等逐行排除。
4. 以GWAS A1剂量计算signed-r，输出矩阵和严格匹配的SNP顺序。参考MAF<1%或缺失>5%排除；其余缺失均值填补并记录。
5. z–LD工程诊断；预设estimate_s>0.1或最大标准化残差>5则HOLD，不删除异常点以强行通过。阈值是本项目保守工程规则，并非普适的生物学判据。
6. 仅诊断通过才运行L=5的SuSiE-RSS工程试验。n=26679为总样本量近似，不能代替变异级有效N；研究数N_STUDIES绝不当作n。没有证明统计可校准前，不将输出用于疾病因果主张。

503参考样本可能产生秩不足LD，PSD允许很小负浮点误差；不能以“秩不足”自动否定全部LD。脚本不启动ULK3，也不执行疾病coloc。

## 完成后告诉我

直接回复“文件已下载”或“运行完成”；我们共享此目录，我可以直接读取结果，不需要你另行上传。

关键结果：R4A8/results/ld_qc.json、IL12RB2_harmonization.tsv、kriging.tsv、rss_gate.json、R_sessionInfo.txt。若报错，复制最后20行错误文本。rss_gate.json的diagnostic_pass=false是可解释的HOLD结果，不是要求强制重跑的故障。

耗时取决于机器与网络。参考下载总约283MB；本地矩阵规模由实际交集决定，通常不需要GPU。运行时关闭PowerShell会中断任务，分段下载可重试。

本包是增量运行包，依赖H:/SCI2/YR1/R4A5/raw/GCST009131中的原始overall文件；不能孤立移走后宣称完全自包含。
