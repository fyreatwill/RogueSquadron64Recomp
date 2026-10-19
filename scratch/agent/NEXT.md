# Next work unit: read s5479_objc_stores_early (scratch/agent/m6/s5479_objc_early, SOAK-RESULTS.md)
s5478 was invalid: watchpoints armed at swap 7600, mission onset is ~1068, counters already written, control silent. s5479 arms at swap 1100.
Hypotheses: (A) idx2/3 never written even from onset - DAT items never triggered by the autopilot; (B) written - bt names the store site, then read that DAT item's condition; (C) idx1 control silent again => instrument invalid, then arm earlier (TRAPSWAP=1000) or use a game-side store log in a fixup script.
Read: 'stop reason = watchpoint N' in lldb_att1.log (1=idx1 control must be >0), bt frames. Then dump lv0 DAT items targeting idx 2/3 offline (type u16 @0 in {0x18,0x19}).
HYPOTHESIS-ID: m6-mission-end-trigger
