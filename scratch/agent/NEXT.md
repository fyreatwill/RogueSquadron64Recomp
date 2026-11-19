# NEXT (s7626)
HYPOTHESIS-ID: g6-upstream-features

G6c step 3c (docs/G6C-STANDINS-PLAN.md "Step 3b result"): with ROGUESQ_STANDINS_FAR (default dd) the bucket accepts 24-30% of
stand-in submits, but the fb flicker test still finds nothing drawn (L1 4068 vs 4206 off, L4 1813 vs 2129, control PASS).
Hypotheses for the draw-path limit:
- H-scale: selectMeshLodAndSubmitForRender (0x80058xxx) builds the instance matrix with scale $f22 that the game shrinks toward 0
  at/past its stock far (upstream 0x80058304 re-scales to $f22+$f20 for "past stock far" objects) -> stand-ins drawn at ~0 size.
- H-flag: the per-frame flag toggle at 0x80058264 ($v1 == 0x80000) hides objects past the far (upstream sets $v1 = 0 for them).
- H-lod: the LOD slot chosen past the far is empty / a no-mesh slot, so nothing submits.
- H-traverse: traverseSceneGraphRecursive never visits our nodes (order / per-frame list reset before conversion).
1. Read selectMeshLodAndSubmitForRender in N64Recomp/RecompiledFuncs + `git show origin/main:src/game/toml_hooks.c` around
   rs64_th_selectMeshLodAndSubmitForRender_80058264/_80058304 (and where s_past_stock_far is set/reset, line ~316).
2. One instrument (new apply script, RS64_REPLAY, gated by a host flag set when the instance is a stand-in: keep a sorted host
   set of s.inst): per call log $f22, $f20, $v1 at 0x80058264, LOD index, and whether a DL submit follows. Tally per second.
   Positive control: the same counters for real spawned objects inside the stock far (must show nonzero scale and submits).
3. Arms in ONE run where possible (scratch/s7626, L1 + L4 dd4, STANDINS=1 + _LOG=1, FAR default, HOLD 130, ALLOW_SLOW=1).
Outcomes: scale ~0 -> port the upstream inflate for stand-in instances only, then re-run the s7625 pixel test (STANDINS=frame +
STANDINS_DUMP=40:46:90 + tools/s7624_flicker_score.py --control); flag hidden -> clear it for stand-ins; no submit -> LOD table.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; fb dumps ~180 MB per arm (gitignored).
