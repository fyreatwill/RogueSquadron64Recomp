# NEXT (s7460)
HYPOTHESIS-ID: soak-stall-measure-coverage

s7459 (class DO) fixed the last blind stall measure: m6_god_common.sh counted [vi] rows (printed every 64 VIs whatever the game does),
so a held frame scored 0. It now follows the newest row's fs= and its summary carries fs_holds/max_fs_hold_vi (tools/agent/vilog_stalls.py);
the verdict counts fs_holds>0. Census of live launchers: no stall_na left (boot_freeze_hunt frozen=, g1e present ring, m6 fs).
Real-game negative control QUEUED: scratch/agent/soak_queue/s7459_m6_fs_ctl.sh.

Step 1: fold s7459_m6_fs_ctl. Expected: arms A and L both alive_at_end=1 vi_stalls30s=0 fs_holds=0, "CONTROL PASS". fs_holds>=1 on a
  healthy flight arm -> false positive: print max_fs_hold_vi and the held fs range (vilog_stalls.py prints episodes on stderr); if it is a
  load, raise nothing, check whether fs pauses in that scene (cutscene/menu) and gate --from-vi on the mission gate.
Step 2 (class DP, one build): the only REAL-game positive controls for a held frame are historical logs (s61 run4, s6993 ring). Add a
  plant ROGUESQ_PLANT_HOLD=<s>[,<dur_s>] in main.cpp beside ROGUESQ_PLANT_EXIT (s7450): at t=<s> the guest thread blocks <dur_s> (default
  40) before its next osViSwapBuffer while the VI thread keeps ticking. Then one soak, two arms (m6 L4 + g1e L4), each plant 40 s:
  expected m6 vi_stalls30s>=1 fs_holds=1, g1e vi_stalls30s=1 with max_vihold_ms>=40000 and max_gap_ms small. Hypotheses: H-ok (both see
  it), H-m6-blind (fs keeps counting while blocked -> fs is not the swap count), H-ring-blind (present re-shows a new origin).
Step 3: after DP the stall-measure class series closes; take the next ladder item (CURRENT-TRUTH Next steps; everything else waits on
  the owner, so prefer an M3 idiom-class audit per ITERATION item 3).
