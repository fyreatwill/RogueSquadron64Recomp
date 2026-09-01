# NEXT work unit — audit the CPU MORT decode/output publication idiom

HYPOTHESIS-ID: m3-mort-publication-idiom-audit

Session 3591 closed the hangar `0x8000` Y/accumulator idiom structurally. Do
not repeat that census, re-watch `0x4B7800`, or add a guard. See
`docs/M3-S3591-HANGAR-Y-ACCUMULATOR-IDIOM-AUDIT.md`.

Next work unit: perform one complete grep-enumerate/classify audit of the
CPU-side MORT decode/output publication path at `0x8009D7D0..0x8009DD7C`.
Enumerate every entry, descriptor read, decoded-sample writer, PCM consumer,
buffer base/stride, and bound/sentinel check in the relevant generated
functions. Do not change runtime code unless the audit identifies a concrete
invalid writer/value; any mitigation would need an ORIGIN line naming that
writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-MortComplete: all decode/output writers and consumers form one bounded
  descriptor-to-PCM publication contract.
- H-MortGap: a concrete decoded-sample writer or consumer is missing, bypassed,
  or uses an invalid base/length.
- H-MortMisread: the suspected MORT address range is not the active output
  publication path.

Discriminator: the complete entry/descriptor/writer/consumer/base table.
Select H-MortGap only with a concrete missing/invalid edge; select
H-MortComplete only when all sites and bases are covered; otherwise leave it
unclassified.

Exact check:

    rg -n -i '8009D7|8009D8|8009D9|8009DA|8009DB|8009DC|8009DD|mort|pcm|sample|descriptor' ../N64Recomp/RecompiledFuncs/funcs_*.c
