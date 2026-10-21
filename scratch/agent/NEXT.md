# NEXT: fold s5761_slotwatch_god — who sets slot state bit 0x8/0x10 (kill source)?
s5760 was invalid (wrong addr 0x137F3C = craft+0x180; no death env). s5761 uses phys 0x137F24 (slot0) / 0x1381C4 (slot1), death env, lives watch as positive control.
Read scratch/agent/m6/s5761_slotwatch_god/lldb_att*.log: wp2/wp3 hits with bt, new values containing 0x8/0x10 (low half) before each lives-- (wp4) hit. Top-frame PC splits H1 collision/damage, H2 timer/objective script, H3 stale value from stubbed subsystem. If wp2/3 never fire while lives-- does, the lhu base differs (check slot index / a1 at runtime) - read a1 via a [slotst] probe.
HYPOTHESIS-ID: g1-nonhealth-fail
