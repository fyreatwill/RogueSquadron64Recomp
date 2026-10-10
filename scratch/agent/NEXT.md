# NEXT: read the s4527 holder-poll soak and decide where the stale 0x8017D910..0x188000 reference lives

HYPOTHESIS-ID: musyx-stale-stream-node-after-teardown

Context: PORTING-STATE s4527. The `ROGUESQ_LOG_S4526` poller works (control: chain len 2, voice base 0x8018D4A0 cnt 16) but the first run crashed in rs_malloc at ~20 s, so the ~122 s late window is unmeasured. `scratch/agent/soak_queue/s4527_postfix_holder_poll.sh` (s4522 recipe, 200 s) is queued; read its SOAK-RESULTS line.
Hypotheses: (A) a list link left pointing into the freed block; (B) a voice-array entry holds an old pointer; (C) neither, the stale read comes from elsewhere (cached node pointer in a global/stack).
Discriminator: grep the soak log for `s4526-P`: NODE/LINK-IN-RANGE => A (holder names the writer; store-watch it); VOICE-IN-RANGE => B; none while `alive` lines span the late window with chain len > 0 => C, widen the scan to globals 0x80149000..0x8014A000. If the run again dies before 100 s, the rs_malloc free-list crash is the blocker: audit who writes the corrupt free-list link (iron rule 11) instead.
