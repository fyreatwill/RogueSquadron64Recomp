# NEXT (s7817)
HYPOTHESIS-ID: oracle-vi-clocked-determinism
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7816 showed every animated retail-oracle frame differs at full scale between two runs with byte-equivalent RSP plugins,
because tools/oracle/rs64_oracle.c times --press and --fb-dump by wall clock (now_s() - g_t0, poller thread). No two oracle runs
are comparable on animated scenes, so plugin effects (s7815 VU fix) and any retail A/B are unresolvable cross-run.
Unit (one oracle build, offline-ish, one emulator run at a time):
 1. Add `--clock vi` to rs64_oracle.c: press times and fb-dump delays counted in VIs (g_vis, 60/s) from dbg_vi on the emulator
    thread, not the poller; fb-dump arm on the first VI of WIDTH as now. Default stays wall clock (old scripts unchanged).
 2. Positive control: two `--clock vi` runs of tools/s7816_oracle_rsp_ab.sh (add CLOCK=vi passthrough) with the SAME plugin must give
    byte-identical dumps on animated hangar frames (s7816 floor: 4/41 exact). If not identical, find the remaining nondeterminism
    (input poll cadence, audio, angrylion threads) before step 3.
 3. Then stock vs patched under --clock vi: count differing px per frame (expect small, <=1 LSB, in the 3D hangar frames).
Hypotheses: H-det (VI clocking makes runs byte-identical) / H-thread (angrylion/plugin threading still diverges) / H-input (PIF
input timing still wall-dependent).
CPU rule: max 2 heavy jobs; one game/emulator run at a time.
