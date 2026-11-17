# NEXT (s7530)
HYPOTHESIS-ID: fw-static-scalar-guest-pointer-latch

Check `wc -c < docs/CURRENT-TRUTH.md` first (59.9 KB after s7529; >60000 = MAINTENANCE iteration instead).
Fold first: any new SOAK-RESULTS.md lines (none queued by s7529).

Class FW (idiom-class audit, scalar twin of FV s7529): file-scope / function-static SCALAR variables holding a guest address
(names like *addr*, *ptr*, *base*, *last_*, g_cine_last_cimg_addr, cached rdram offsets) in functional (non-sNNNN-gated) code of
lib/N64ModernRuntime/{librecomp,ultramodern}/src, src/main, src/rsp. Such a latch is set when guest state appears and read later; if the
guest reuses or frees the address between set and read, the host acts on stale state.
Hypotheses per site: H-canon (re-set before every read on the same path), H-dead (no functional reader / immutable), H-latent-fix (read
can follow a guest reuse without a re-set: land a re-set with =0 arm + planted-stale control, L4 dd1 forced HOLD 120 two arms one
build), H-instrument-only.
1. Extend tools/s7529_fv_census.py (or new tools/s7530_fw_census.py) with a scalar DECL regex
   (static (u)int32_t|PTR|gpr|uintptr_t <name containing addr|ptr|base|last|cur>), same rule table + eraser/re-set regex, same
   planted fixtures (--controls).
2. Classify every site; for any H-latent-fix, land it this session with its control.
Discriminating outcome: 0 unclassified with all controls PASS -> FW closed static; any H-latent-fix -> fix + two-arm run.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
