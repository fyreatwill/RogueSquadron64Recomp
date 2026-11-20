# NEXT (s7719)
HYPOTHESIS-ID: regen-replay-drift

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

gate-sweep-coverage is CLOSED (s7718: 195 gates, 190 GREEN 5 REPORT 0 RED; scratch/s7718/classification.tsv). Do not iterate it.

The two offline drift gates the sweep still cannot run are s7421_regen_drift and s7423_live_stale: both need a FRESH regen
replay tree. The last replay is s7558 (scratch/s7558/{replay,verify}); since then s7580 (lui rewrite), s7484 (load watch), s7487,
G6b/G6c and ~140 sessions of fixups landed. Question: does a pristine regen + RS64_REPLAY still reproduce the live
RecompiledFuncs (every live-only statement mirrored by a fixup/apply script)?
1. Replay per docs/REGEN-VERIFY.md (tools/regen_replay.sh -> tools/regen_verify.sh) into scratch/s7719/{replay,verify}.
   Never touch ../N64Recomp/RecompiledFuncs (live) or build/. CPU: one job (iron rule 0).
2. `python3 tools/s7421_regen_drift.py ../N64Recomp/RecompiledFuncs scratch/s7719/replay scratch/s7719/verify/compare.json
   --baseline scratch/s7558/verify/compare.json --control` and `python3 tools/s7423_live_stale.py ../N64Recomp/RecompiledFuncs
   scratch/s7719/replay --control`.
Hypotheses: H-mirrored (0 open LOST/REORDER, 0 open BEHAVIOUR: every live hand-edit dies-and-returns at regen), H-lost (>=1
live-only non-diag statement: a fix that would vanish at the next regen -> move it into a fixup script + re-replay),
H-layout (only SLOTPERM/CODEGEN rows, as s7559).
Positive controls: both tools' --control (planted LOST / planted guest store) must PASS in the same run.
Then: if the replay tree is kept (zstd tar, as s7658 did for inputs), add both to the sweep ARGS so the next drift reads RED.
Standing check: `python3 tools/s7651_gate_sweep.py --jobs 2`. Owner defaults: never flip.
