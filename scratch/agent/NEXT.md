# NEXT (s7533)
HYPOTHESIS-ID: fz-host-thread-guest-writes

Check `wc -c < docs/CURRENT-TRUTH.md` first (59,992 B after s7532; >60000 = MAINTENANCE iteration instead — likely soon).
Fold first: SOAK-RESULTS.md line for s7532_fy_levels (score with `python3 tools/s7532_undo_score.py scratch/s7532_fy_levels l1 l7 l10 l12`).

Class FZ (idiom-class audit; reverse direction of FY): host code that WRITES guest RDRAM (memcpy/memset/std::copy into rdram,
RDRAM, g_rdram_for_submit; `rdram[...] =`; MEM_W/MEM_H/MEM_B in host .cpp) from a thread that is NOT the guest CPU thread
(gfx/Gfx-worker, audio, VI/present, RT64 workers). After an early sp_complete or any async completion the guest runs
concurrently, so such a write can (a) clobber a guest store (lost write) or (b) be observed half-done.
Roots: lib/N64ModernRuntime/{librecomp,ultramodern}/src, src/main, src/rsp, lib/rt64/src/{hle,gbi,render}.
1. tools/s7533_fz_census.py: start from s7532's in_class scanner (guest-write rows) + memset/direct-store patterns; classify each
   site's thread from its enclosing function's call root (task_thread_func / gfx_thread / audio / rt64 workers vs guest), and
   its timing (before the guest-visible completion signal = H-canon; after = candidate).
   Hypotheses per site: H-canon (guest blocked on the completion this write precedes), H-guest-thread, H-instrument-only (env off),
   H-dead, H-latent-fix (non-guest thread, guest running, range the guest also writes).
   Controls: planted write from a gfx-thread function -> UNCLASSIFIED; mutation (move a write after sp_complete) -> FAIL.
2. Known candidates already measured: s7532 wrap-restore undo (0 foreign, H-canon). RT64 framebuffer write-back to RDRAM and
   dpc_bridge patch writes (memcpy(g_rdram_for_submit + ...) in s4286/s6720/s6722 paths) are the likely remaining rows.
3. Any H-latent-fix: instrument the window like S7532_UNDO_CHK (same-run plant control), L4 dd1 + L15 dd8 21:9, HOLD 120.
Discriminating outcome: 0 unclassified + controls PASS -> FZ closed; any H-latent-fix with foreign bytes > 0 -> name the writer, fix.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
