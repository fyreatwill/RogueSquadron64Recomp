# NEXT: 21:9 + dd4 mission-load pass over the remaining levels on the s6858 spill layout
HYPOTHESIS-ID: g1d-spill-layout-level-sweep

Why: s6859 verified lvl9/lvl17 only. The s6850 lvl0-18 21:9 sweep ran on the aliased layout, and the s6858 crash was asset-load
and layout dependent (16:9 lvl1/lvl9 died at load, 21:9 lvl9/lvl17 survived while aliased). This is a new-config check after a
memory layout change, not a G4 repeat hold: short holds, load + first flight only.
Hypotheses: H-ok (every level reaches flight, spill all at 0x81) / H-load (a level dies in load_hmt_and_hob or similar on
RAMTOP 20) / H-heap (a level exhausts the 12 MB heap or the 4 MB spill arena now it no longer overlaps the heap).
Discriminator: also drop the explicit ROGUESQ_OSMEM_MB=12 from XENV_EXTRA for this sweep, so the env-free owner path is exercised
(s6859 only read it from the code); the `[ddbundle] osmem` line is the positive control and must fire in every run.
Commands: copy scratch/s6859/abd.sh to scratch/s6860/, s/s6859/s6860/, remove ROGUESQ_OSMEM_MB=12, drop RS64_RDP_BIN_PORT (not
needed: no region question here), HOLD_S=60, loop levels 0-8,10-16,18 sequentially. Per run: summary line, `[ddbundle] osmem`
count, spill prefix tally, last `[spill]` used value vs 0x400000, crash lines.
Outcomes: all clean -> close, drop the "other levels" caveat from OWNER-OPT-INS; crash -> backtrace, name the writer.
