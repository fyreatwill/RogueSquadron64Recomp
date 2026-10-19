RESUME ONLY — do not rerun s5568 or start a new live capture.

The prior work unit qualified the existing retail and s5568 port captures:
whole-RDRAM, VI, mapped-PC, and image controls all pass in the same analyzer
run, but exact phase/image/PC/progress joins remain below 20 rows at both
mapped PCs. No accumulator writer or mitigation is inferred.

Single next work unit: implement one bounded offline ranked/lane comparison,
then run it once against the existing captures. The analyzer must bin rows by
within-phase ordinal (not wall-clock time), compare lane masks separately for
each mapped PC/image, and print positive-control status plus a per-bin match
table.

Competing hypotheses and discriminator:

1. H1: rank bins and lane masks agree at both PCs; exact progress was only
   nonportable.
2. H2: rank bins align but lane masks differ persistently; this selects a
   boundary/value divergence for a later writer audit.
3. H3: rank/lane alignment remains absent or cannot be joined; comparison is
   still unevaluable.

H1 requires stable lane agreement in both PCs; H2 requires stable rank
alignment with a lane mismatch; otherwise H3. Do not add live instrumentation
until this offline result says alignment is the remaining discriminator.

Exact commands after adding the analyzer:

    python3 tools/analyze_m4_normalized.py --self-test
    python3 tools/analyze_m4_ranked.py --retail scratch/agent/s5354_retail_m4_pcs/mid.dump scratch/agent/s5354_retail_m4_pcs/rsp.dump scratch/agent/s5354_retail_m4_pcs/oracle.log --port scratch/agent/m6/s5568b_m4_port_controls/run.log

HYPOTHESIS-ID: m4-normalized-boundary-schema
