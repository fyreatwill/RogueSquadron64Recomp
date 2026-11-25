# NEXT (s7922)
HYPOTHESIS-ID: preflight-transition-retail-table
s7921 closed G5c: the hangar-entry hold is retail (oracle 17 VIs on the same MusyX wait). Next, one offline unit (no game run),
capture once / analyze many, reusing s7921 captures:
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks this.
1. Build tools/s7922_transition_table.py: pair every port VI hold >= 120 ms on the owner pre-flight route (ring:
   scratch/s7921_port2/ring_q4.txt, scored by tools/s7920_hold_class.py logic, lower threshold) with the retail oracle hold at the
   same route step (scratch/s7921_oracle5/oracle.log `[vi-hold]` lines, len >= 7, matched by order of the waitForMusyX hits /
   width changes), and print port_VIs vs retail_VIs per step. Planted controls: a synthetic port hold 10 VIs longer than its
   retail twin must read PORT-LONGER; an equal pair EQUAL (exit 3 if either fails).
2. Any step where port > retail + 3 VIs is a port-only stall to root-cause (sample it like s7921 window B). If none: the whole
   pre-flight route is retail-paced; record it and take the next ladder rung (all remaining items are owner-look; check
   docs/OWNER-REVIEW-QUEUE.md is current with s7921, then M6/G4-side-effect only).
Hypotheses: H-equal (all port holds <= retail), H-port-longer (some transition has a host-only cost, e.g. overlay load s7528 evict,
RT64 framebuffer reconfiguration on the 512->796 osViSetMode reapplies, shader compile on first hangar frame).
Discriminator: per-step port_VIs - retail_VIs.
Caveat: the oracle route (Start/A every 6 s from 6 s) differs from the port autopilot (Start/Z every 4 s); match steps by
transition identity (width change / musyx wait ordinal), not by time.
