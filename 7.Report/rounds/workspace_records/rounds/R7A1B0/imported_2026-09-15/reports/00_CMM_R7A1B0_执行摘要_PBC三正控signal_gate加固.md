# CMM R7A1B0 执行摘要：PBC 三正控 signal-gate 加固与真实执行包

**日期：2026-09-15**

## 当前状态

```text
R7A1A_RELEASE_INTEGRITY = PASS
PBC = GO_R7A1B_BOUNDED_SIGNAL_GATE
CeD = HOLD_NOT_SELECTED

R7A1B0_PROTOCOL_HARDENING = COMPLETE
R7A1B_TRUE_SIGNAL_INFERENCE_CURRENT_CHAT = NOT_RUN
reason = uploaded project snapshot does not include canonical 10.34 GB OneK raw cis-eQTL archive / 980-donor PLINK bytes
```

R7A1A upstream:
- SHA-256 `ce8f4658fee1557de0bc8c92fde86a3f34d3037c4a618d680f4b9132060e9116`
- ZIP CRC PASS
- internal checksums 50/50 PASS

## Important protocol amendment

The published PBC disease fine-mapping study independently reports:

- GJOKA locus 2 / 1p31.3 / IL12RB2: **two SuSiE disease credible signals**, sizes 1 and 4.
- locus 4 / 1q23.1 / FCRL3: one disease CS, size 33.
- locus 6 / 1q32.1 / INAVA: one disease CS, size 33.

Therefore IL12RB2/NK is now a **forced multi-signal target**. It cannot be terminated by a single-causal ABF result.

## Pre-signal anchor audit

The R7A1A PBC GWS rows and frozen OneK top eQTLs already show:

- **FCRL3**: B_IN and CD4_NC top eQTL are exactly at `1:157668993`, the same position as PBC GWS `rs2210913` (`P≈2.32e-8`); several other FCRL3 source-significant cell tops cluster immediately around the disease peak.
- **IL12RB2**: NK is strongly source-significant (`q≈7.5e-9`) and its top variant lies ~32 kb from the PBC regional lead; because disease locus 2 is known multi-signal, exact top-SNP mismatch is not evidence against colocalization.
- **INAVA/C1orf106**: OneK CD4_NC is weak (`q≈0.318`) and remains a preregistered falsification/uninformative control.

This makes FCRL3 the strongest expected positive and IL12RB2 a plausible multi-signal positive, but **neither is called colocalized before the true regional analysis**.

## Next

Deploy the package locally and run the frozen 9-comparison gate. Only signal-level results determine whether PBC advances.
