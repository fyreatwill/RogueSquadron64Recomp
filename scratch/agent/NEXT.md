# NEXT (s7782; s7781 closed the flag-4 loader side H-clean and found DL-chunk stores in the arena's FB slot)
HYPOTHESIS-ID: fb-shared-slot
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Datum (s7781, CURRENT-TRUTH item 32, 3 runs identical): the display-list emitter 0x8000CFD4-0x8000D6FF stores DL chunk-list
nodes (chunk+0/+4, e.g. 0x670004, 0x680004, 0x69FF9C) into the FB slot that hosts the flag-4 arena. That is 34 stores inside a live
arena, 3836 into the free slot from 0.08 ms after the drop, and 5216 while that slot is a busy FB (st 5). DL chunks come from
0x8002221C (it steals the smallest texture-pool entry from the lists at 0x80128F00 [count 0x80128EF0], 0x100 B each, free chunk
list 0x801163B0, limit 0x801163D4).

Hypotheses:
- H-design: retail deliberately hosts DL chunks in texture-pool entries whose memory is the FREE FB (same idea as the arena), and a
  chunk is never live while its slot is rendered. Then busy-slot stores are DL writes to a slot the RDP is not drawing into at that
  moment (state 5 = queued for display, not render target?).
- H-overlap: texture-pool entries were carved under an earlier FB partition (boot 640x480 at 5D4000) and now overlap the current
  FB slots (hangar 512x340 at 656000/6AB000). Then the RDP (or our rt64_writeback, 15.8k writes into this span in s7779) can
  overwrite live DL chunks. Retail-latent or port-only.
- H-arena-collide: an arena allocation and a live DL chunk occupy the same bytes in one epoch (the 34 live-arena DL stores).

Unit, ONE build, ONE run (owner route_long, `zsh tools/s7774_slot_run.zsh s7782a ROGUESQ_S7779_ARENA=1 ROGUESQ_S7781_PLANT=1 <new>`):
1. At each [s7781] open/close, walk the texture-pool lists (0x80128F00 + 4i, i < *0x80128EF0 halfword) and the DL free-chunk
   list 0x801163B0. Print each entry's address/data pointer that falls inside [slot0, bound 0x801163E4), with the FB slot table.
2. Per DL-emitter store into a slot: slot state + whether the RDP's current colour image (setColorImage, dpc_bridge) is that slot
   at that moment. That column, not st, decides whether a DL chunk was live in the render target.
3. Per live-arena DL store: was that address also handed out by the arena this epoch (log the arena's block list: walk the
   free-list descriptor at 0x8010FEFC)?
Outcomes: chunks inside the slot only while it is not the colour image = H-design (close as retail). A DL chunk inside the current
colour image = H-overlap (then repeat it in the oracle: mupen retail at boot, phys 0x62B800-0x695C00 at t~5-6 s, where ep2 already
shows busy-slot stores by 0x80014488). Arena block == DL chunk bytes = H-arena-collide.
Positive control: the s7781 plant (DEAD7781) plus a planted chunk address (fake list entry printed with the walk).
