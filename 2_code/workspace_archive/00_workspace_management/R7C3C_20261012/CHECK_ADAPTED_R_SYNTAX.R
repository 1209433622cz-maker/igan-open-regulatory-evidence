x <- read.delim('H:/SCI2/YR1/5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/organization/PATH_ONLY_ADAPTERS.tsv',check.names=FALSE,fileEncoding='UTF-8-BOM')
x <- x[grepl('[.]R$',x$path),]
x$status <- vapply(x$path,function(p){tryCatch({parse(file=file.path('H:/SCI2/YR1',p));'PASS'},error=function(e)paste('FAIL',conditionMessage(e)))},character(1))
write.table(x[,c('path','status')],'H:/SCI2/YR1/5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/paths/R_SYNTAX.tsv',sep='\t',row.names=FALSE)
print(table(x$status))