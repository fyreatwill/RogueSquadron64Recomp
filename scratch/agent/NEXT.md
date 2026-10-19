The s5568 schema capture is complete; do not rerun it. Both arms now pass
whole-RDRAM, VI, mapped-PC, and image controls, but exact joins still have
fewer than 20 shared rows at each mapped PC. The next work unit is one offline
ranked/lane comparison against the existing qualified retail and s5568 port
captures; do not infer a writer from the H3 schema result.

Competing hypotheses and discriminator:

1. H1: exact progress is nonportable, but within-phase rank bins and lane
   masks agree at both mapped PCs; the prior H3 is only a key-alignment issue.
2. H2: rank bins align but lane masks differ persistently by image/PC; this
   selects a real boundary/value divergence for a later writer audit.
3. H3: rank/lane alignment remains absent or controls cannot be joined, so the
   accumulator comparison is still unevaluable.

Discriminating measurement: one analyzer run must bin each arm's rows by
within-phase ordinal (not wall-clock time), compare lane masks separately for
each mapped PC/image, and report positive-control status plus a per-bin match
table. H1 requires stable lane agreement in both PCs; H2 requires stable rank
alignment with a lane mismatch; otherwise H3. First run the existing schema
self-test, then the ranked comparison on `s5354_retail_m4_pcs` and
`s5568b_m4_port_controls/run.log`.

Exact next commands after implementing the one analyzer change:

    python3 tools/analyze_m4_normalized.py --self-test
    python3 tools/analyze_m4_ranked.py --retail scratch/agent/s5354_retail_m4_pcs/mid.dump scratch/agent/s5354_retail_m4_pcs/rsp.dump scratch/agent/s5354_retail_m4_pcs/oracle.log --port scratch/agent/m6/s5568b_m4_port_controls/run.log

Resume artifacts: `src/rsp/dpc_bridge.cpp`, `tools/fixup_factor5_ucode.py`,
`tools/analyze_m4_normalized.py`, and the Session 5565 ledger entry. Do not
infer an accumulator writer or add a mitigation from the existing capture.

Ground-truth gate: the retail RSM2/RSD2 capture and the s5568 port capture both
qualify whole-RAM, VI, mapped-PC, and image controls. Do not add another live
port field until the offline rank/lane comparison shows that alignment is the
remaining discriminator.

HYPOTHESIS-ID: m4-normalized-boundary-schema
