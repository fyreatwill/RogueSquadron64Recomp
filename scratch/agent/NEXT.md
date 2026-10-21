# NEXT: [mtm] who sets event bits in 0x8010C9E0 (pending-event mask)
Finding s5752: requestMissionTransitionMode(a0=id) is dispatched from runInMissionFrame jalr@0x800FA820 over table 0x8010B350 ({u8 id,pad,u32 fn} x N), gated by mask word 0x8010C9E0 bit id.
Hypotheses: H1 bit1 is set every mission by a periodic/timer setter (benign, a0=1 is the normal handler); H2 bit 1 is the objective-fail/win event and the real mission end needs another bit (id 2+) whose setter is gated by a condition never met on the keyed route; H3 table entries map ids to different handlers than assumed.
Discriminating, ONE build: patch (fixup script, env ROGUESQ_LOG_MTM) in runInMissionFrame before the table loop: dump all table entries (id, fn) once, and log mask word whenever it changes (with frame#). Control: mask changes must be logged at least once per run. Outcome: which bits ever set, which fn each maps to; then grep the setter sites (funcs_11/30/32/33/35/36/37 stores to -0x3620) for the bit-2 setter and its guard.
Soak: queue 2 recipes copying scratch/agent/soak_queue/done/s5751_mtma.sh.
HYPOTHESIS-ID: g1-nonhealth-fail
