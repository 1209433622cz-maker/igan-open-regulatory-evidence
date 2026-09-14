# CMM R7A0 执行摘要：Open-data completion-first portfolio preflight

**日期：2026-09-15**

## 上游冻结确认

R6A3A1 上传包独立验收：

```text
SHA-256 = 50585deacdbb87f2f5cf3fa55fecb311e99fd57bf55e2709c57f548a90e7e906
ZIP CRC = PASS
internal checksum = 56/56 PASS
IgAN_REGULATORY_MAIN = FROZEN_ARCHIVE
```

GitHub 远端最新已验证提交为 `5be29034298192b1772dbf75696294ec8e276529`，对应 R6A3A1 终裁。

## R7A0 结论

```text
AA = FAIL_GATE0_CORE_GWAS_UNDER_FROZEN_RULES

PBC = RANK_1_ADVANCE_TO_R7A1A
CeD = RANK_2_ADVANCE_TO_R7A1A

NEW_PRIMARY_PROJECT = NOT_YET_APPROVED
NEXT_STAGE = R7A1A_PBC_CeD_TRUE_BYTE_QTL_PREFLIGHT
```

### 为什么 PBC 现在排第一

本项目目标不是“必须一区”，而是“按一区标准做、优先保证完整闭环和足够真实阳性”。在这个目标函数下，PBC 的 56 个 non-HLA GWS loci、公开研究内 LD、已发表多位点 multi-omic colocalization 阳性和公开肝组织 scRNA，显著降低项目再次被 1–2 个脆弱 locus 绑架的风险。

缺点是 2026 同型研究拥挤，因此 PBC 若最终 GO，论文定位必须收窄成：
`study-LD-aware disease fine-mapping → OneK1K single-cell source-QTL → TenK10K independent replication → liver donor-level orthogonal validation`。

### CeD 为什么仍然很强

CeD 有 39+ non-HLA loci、成熟的 published eQTL positives、且 2026 新增 active-duodenum single-cell data；目前没有发现完全同构的 single-cell QTL + lesion-tissue signal-level paper。主要短板是组织 n=4+2 和疾病侧没有像 PBC 那样已核实的 study-specific LD package。

## 本轮边界

由于当前 sandbox 无法直接取得外部二进制文件，PBC/CeD 的“来源可访问”已经通过网页/论文验证，但**真实本地字节、SHA-256 和 schema 仍未在本会话获得**。因此不把任一候选写成 Gate-0/主项目最终 PASS。

已生成 R7A1A 一键执行包，对真实本机字节完成：
1. PBC/CeD 下载与哈希；
2. GWAS schema和非MHC信号检查；
3. PBC study-input ZIP/LD inventory；
4. 预注册 3+3 control genes 的 OneK/TenK source-QTL testability；
5. 在任何 disease-QTL coloc 之前 STOP。
