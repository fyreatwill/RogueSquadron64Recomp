# NEXT (s7532)
HYPOTHESIS-ID: fy-host-shadow-copy-of-guest-bytes

Check `wc -c < docs/CURRENT-TRUTH.md` first (59.9 KB after s7531; >60000 = MAINTENANCE iteration instead).
Fold first: any new SOAK-RESULTS.md lines (none queued by s7531).

Class FY (idiom-class audit; content twin of FW/FX, which closed scalar guest-ADDRESS latches s7530-s7531):
host buffers that hold a COPY of guest RDRAM bytes (memcpy/std::copy/loop from rdram/RDRAM/state->RDRAM into a
static / member / file-scope buffer) that are read later without re-copying. If the guest rewrites the source between
copy and read, the host acts on stale bytes.
Roots: lib/N64ModernRuntime/{librecomp,ultramodern}/src, src/main, src/rsp, lib/rt64/src/{hle,gbi,render}.
1. tools/s7532_fy_census.py: grep-enumerate copy sites whose source expression mentions rdram|RDRAM|guest (memcpy, memmove,
   std::copy, std::vector assign/insert, byte loops `dst[i] = rdram[...]`), resolve the destination (local vs persistent),
   find later reads of persistent destinations; rule rows with verify/envoff like s7530 (reuse its run_checks).
   Controls: planted persistent copy read later -> UNCLASSIFIED; local-only copy -> auto; mutation of a real re-copy -> FAIL.
2. Hypotheses per site: H-canon (re-copied before every read on the same path), H-local (destination dies in scope),
   H-instrument-only, H-dead (opt-in env off / no caller), H-latent-fix (persistent copy read after a possible guest rewrite).
3. Any H-latent-fix: fix (lib/ edits -> ./submodule-patches/export.sh + commit, same session) with a =0 arm and a planted-stale
   control, L4 dd1 forced HOLD 120, two arms one build.
Discriminating outcome: 0 unclassified with controls PASS -> FY closed static; any H-latent-fix -> fix + two-arm run.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
