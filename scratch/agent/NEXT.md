# NEXT (s7503)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7502_ez2_levels (rows `s7502_ez2_levels ez arm=` in scratch/s7502_ez2_levels/out.txt).
EZ score 0 on L1 dd8 21:9 / L7 / L10 / L12 dd4 with ctlst=ok -> EZ CLOSED 6 levels. Note the wrapped EQ base recipe can make rc=3 on
its own (L15 os_rt64fb plant not detected in s7501 and s7502); judge EZ by the `ez score=` line. Any remaining none: read the `up cls=none`
row, check for another overlapping fb-record or a store path outside rs64_s7475_store. trunc left after pgres: ring too short, note it.

Work unit, class FA (unchanged from s7502 plan, now with the s7502 writer list): uploads whose writer is guest code reusing freed fb RAM:
allocator headers (buildHeapFreeList / rs_free / rs_malloc / coalesceFreeHeapBlocks) and packTlutEntriesRgba5551 (0x200 TLUT at the
tail of an fb idle 6-15 s). Hypotheses: H-fa-dead (image never set again, or set and filled before any draw/present/tex: harmless stale
RT64 tracking) / H-fa-live (image set this or next swap, or presented by VI, and RT64 shows/samples the uploaded bytes: visible garbage)
/ H-fa-retail (retail reuses the same RAM the same way).
Discriminator, ONE build: in rs64_s7501_up, when cls=cpu and fn is an allocator or packTlut*, register the fb with the s7500 EY tracker
(rs64_s7500_* classifies the first later event on an image: fill / draw / zread / tex / up / wb) and log whether VI origin == that fb
within the next 3 swaps. Control: the s7501 ctl word on a live fb must classify live (draw/present).
Run: `env XC=ROGUESQ_S7500_EY=1+ROGUESQ_S7500_CTL=1 zsh tools/s7501_ez_recipe.zsh` (L4 dd1, L15 dd8 21:9).
Outcome: all -> dead/fill-first => H-fa-dead, class closed; any draw/present/tex before fill => H-fa-live, then why RT64 keeps a freed fb
live, and check retail via the oracle (mupen watch on that block).
