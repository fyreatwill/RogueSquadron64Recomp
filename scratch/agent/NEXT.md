# NEXT (s7528)
HYPOTHESIS-ID: closed-class-gap-ledger

Check `wc -c < docs/CURRENT-TRUTH.md` first (59.6 KB after s7527; >60000 = MAINTENANCE iteration instead).

FU CLOSED s7527 (tools/s7527_host_replace_audit.py --controls 8/8). The replaced-libultra surface (BL, BM, FG-FU) is exhausted.
The closed classes left named, unfixed gaps. One work unit: build the gap ledger, then fix or prove the top row in the same session.

1. Ledger (offline, one pass): grep CURRENT-TRUTH + PORTING-STATE s7400-s7527 for "Gap:"/"Gaps:" and "not modelled"/"never erases".
   Known rows so far:
   - FQ s7520: librecomp load_overlay never erases a replaced overlay's func_map entries (0 calls hit one in the s7520 runs).
     H-latent (a call into a stale entry would run the previous overlay's code) vs H-dead (every overlay swap reloads the same
     window and every lookup goes through the new section table). Fix candidate: erase the old section's entries on replace
     (lib/N64ModernRuntime -> ./submodule-patches/export.sh + commit SAME session); control = s7520 ROGUESQ_S7520_CTL=1 still caught,
     plus a planted lookup of a stale vram after an overlay swap that must now miss (logged) instead of returning the old func.
   - FS s7522: a later partial DMA inside a resident IMEM run is not re-split (tools/s7522_imem_residency.py assumption).
   - FP s7519: stores before a line's first marking, no eviction model.
   - EM s7486: swl/swr routed to rs64_s5660_ustore with only the aligned check.
   Classify each: H-latent-fix (real code change), H-dead (name why nothing can reach it), H-instrument-only (gap in a closed tool).
2. Take the highest H-latent-fix row (expected FQ func_map) and land it with its two-arm control in the same iteration
   (L4 dd1 forced route, HOLD 120, old vs new arm in one build via an env toggle, default stays retail-equivalent).
Expected: >=1 real code change; others proven dead or recorded as instrument-only.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
