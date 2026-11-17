# NEXT (s7531)
HYPOTHESIS-ID: fx-rt64-scalar-guest-latch

Check `wc -c < docs/CURRENT-TRUTH.md` first (59.9 KB after s7530; >60000 = MAINTENANCE iteration instead).
Fold first: any new SOAK-RESULTS.md lines (none queued by s7530).

Class FX (idiom-class audit, RT64 half of FW s7530): scalar latches holding a guest address / guest-derived position in
lib/rt64/src/hle + lib/rt64/src/gbi. Measured s7530 with tools/s7530_fw_census.py logic: 27 sites, 20 with functional reads and
no rule. Most interesting: rt64_interpreter.cpp s_rs64_pending_start_address (146, reads 662-674), s_rdp_advance_first_consumer_*
(144-145), rt64_state.cpp g_rs64LastSyncedViAddress (610, read 3558), g_ost_last_ctx (246), rt64_gbi_f3dfactor5.cpp
s_op01_last_ram (135, read 252-253), rt64_rdp.cpp g_rs64LastRGBA32Addr/Seq (200-201, read 2619-2621), rt64_gbi_rdp.cpp lastTask (51).
Hypotheses per site: H-canon (re-set before every read on the same path), H-dead (no functional reader / opt-in env off / no caller
in the binary), H-latent-fix (read can follow a guest reuse without re-set), H-instrument-only.
1. Add "lib/rt64/src/hle", "lib/rt64/src/gbi" to ROOTS in tools/s7530_fw_census.py (or a --roots flag) and write rule rows with
   verify/nocaller/envoff checks for the 20; keep --controls 6/6.
2. Any H-latent-fix: land the re-set in lib/rt64 (then ./submodule-patches/export.sh + commit, same session) with a =0 arm and a
   planted-stale control, L4 dd1 forced HOLD 120, two arms one build.
Discriminating outcome: 0 unclassified with controls PASS -> FX closed static; any H-latent-fix -> fix + two-arm run.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
