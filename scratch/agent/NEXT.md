# NEXT (s7367): class AQ dynamic half — get the TSan arm into missions (guest VI-handshake deadlock under slowdown)
HYPOTHESIS-ID: host-container-race
Context (s7366): the TSan arm (tools/build_tsan.sh, scratch/s7366/tsan_run.zsh) now boots (s7355 sigaltstack hook skipped under
TSan) but every run still stops in the front end: 3/3 runs (dd8 21:9 at fs=39 twice and fs=281 once; retail settings at fs=281) end in a
guest wait cycle. MAIN waits on 0x8011A818, the scheduler on 0x8011A420, and viRetraceHandlerThread is stuck in
osSendMesg(0x80128CF0, BLOCK) into a full capacity-1 queue that only MAIN drains (vflag 0x80037808 handshake, funcs_4 0x80019B3C /
funcs_5 0x8001BFDC-0x8001C0F8). TSan makes guest code ~5-20x slower, so a gfx task spans >1 VI. Static census + 2 reviews cover the
rest of class AQ (s7366 entry).
Hypotheses for the deadlock: H-slow (only a guest that misses many VIs deadlocks; retail hardware never does; a slower VI clock
lets TSan reach missions), H-sem (ultramodern's blocked-sender wake on a full queue loses a wakeup: MAIN's recv does not restart
the blocked sender), H-flag (the retrace thread reads a stale vflag across the handoff).
Discriminator (one build, the TSan arm): add ROGUESQ_VI_HZ=<n> (events.cpp vi_hz override, default 60), then run the dd8
recipe at VI_HZ=60 / 20 / 10 with ROGUESQ_G1E_TL=<file> + ROGUESQ_S4259=1. H-slow: 20 or 10 reaches initMission with no
stall-dump. H-sem: the timeline shows a CF0 recv that returns while the fullqueue sender stays blocked. H-flag: a CF0 send with no
flag-set window open (MAIN not in 0x8001BFF8 / 0x8001C048 / 0x8001C0EC).
Also check (cheap, normal build): does a heavily loaded host (tools/s7277_toggle_load_arm.zsh) ever hit the same cycle? If
so it is an owner-visible permanent freeze, not a TSan artefact.
Then: TSan run through hangar -> mission -> abort (scratch/s7326 AP route, timings scaled to the slower VI), report with
tools/s7354_tsan_report.py (exit 1 on ? / B), fix any default-path container race, 260 s dd8 smoke on build/.
Side question still carried from s7364: what did the stale tile DRAW? WLRESET=0 vs default presented frames, phase-gated.
Exit: PORTING-STATE s7367, CURRENT-TRUTH 27zf, commit; any lib/ edit -> ./submodule-patches/export.sh first.
