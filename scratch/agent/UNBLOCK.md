Route 2 — satisfy locally.

The claimed reference-RSP dependency was locally obtainable. The cxd4 source
already present at `/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4`
was compiled into `tools/agent/cxd4_vu_replay.c`. The earlier comparator's
failure was an integration defect: it assumed the large run log contained one
contiguous `[spike-vu8]` block, although other diagnostics are interleaved.

Evidence: compiling the tool and feeding lines 135071–135078 of
`scratch/agent/m6/g1_lvl2s6380long/run.log` produced
`rows=4 accCompared=24 accMismatches=0 fd57=1 malformed=0`; cxd4 independently
produced `FD57` on `VMADH` lane 1. This satisfies the positive control and
agrees with the runtime accumulator chain, refuting the RSP-emulation/clamp
disagreement form of the block. Retail visual fidelity is still unproven, so
spike culling remains opt-in and the default is unchanged.
