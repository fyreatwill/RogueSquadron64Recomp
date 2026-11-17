# NEXT (s7529)
HYPOTHESIS-ID: fv-host-guest-keyed-cache-lifetime

Check `wc -c < docs/CURRENT-TRUTH.md` first (59.9 KB after s7528; >60000 = MAINTENANCE iteration instead).
Fold first: scratch/agent/SOAK-RESULTS.md line for s7528_evict_levels (tools/s7528_evict_score.py score=0 -> gap FQ fix qualified 4 levels;
any FAIL: read scratch/agent/soak_results/s7528_evict_levels_*.log, the [s7528] lines name the load).

Class FV (idiom-class audit, generalises the s7528 FQ finding): every host-side container in librecomp / ultramodern / src/ keyed by a guest
address (unordered_map / map / set / vector of guest vram/rdram addresses, static caches) that is filled when guest state appears but never
invalidated when the guest reuses the address (overlay swap, rs_free/heap reuse, DMA overwrite, task end).
1. Census (offline, one pass): grep -nE 'static .*(unordered_map|std::map|unordered_set|std::set)<(u?int32_t|uint32_t|gpr)' plus
   member containers in lib/N64ModernRuntime/{librecomp,ultramodern}/src, src/main, src/rsp, src/game. Exclude pure diagnostics (rs64_s7xxx
   logging-only maps). For each: key meaning, filler, eraser (or none), reuse event that should erase.
2. Classify: H-canon (erased on the reuse event), H-dead (key space never reused: name why), H-latent-fix (needs an erase; land it with a
   same-build =0 arm and a planted-stale control like ROGUESQ_S7528_CTL), H-instrument-only.
3. Land the top H-latent-fix row with its control in the same session (L4 dd1 forced, HOLD 120, two arms one build).
Expected: a classified table (tool: tools/s7529_fv_census.py --controls with a planted missing-eraser fixture) and >=0 fixes.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
