# NEXT (s5909): identify overlay callers 0x800f141c / 0x800f14dc / 0x800ff288 of findSegmentObjectSphereHit and what consumes their hits

HYPOTHESIS-ID: g1-mission-progression

s5908: lock-on loops (funcs_13 0x8005Cxxx-D2xx) are NOT bolt damage. High-yield callers are overlay: 800f141c (7486 calls/665 hits), 800f14dc (20600/402); mass caller 800ff288 (831k/32).

Hypotheses:
- H-bolt: 0x800f141c/14dc is the bolt-vs-NPC test; hits then go to a damage routine that is gated (team/invuln/ROGUESQ_NPC_INVULN env!) -> check boring thing first: s5902_life.sh sets ROGUESQ_NPC_INVULN=1, which may itself suppress kills.
- H-terrain: those callers are terrain/ground effect collisions; bolt damage uses a different primitive (e.g. segment-vs-sphere inline).
- H-gate: hits reach damage but are dropped by life/shield check.

Discriminator: (1) static: find the overlay function containing 0x800f141c (tools/disasm_ovl2c.py or recomp'd overlay funcs) and read what follows the jal; (2) rerun s5902_life.sh WITHOUT ROGUESQ_NPC_INVULN and tally NPC kills (positive control: kill counter increments when invuln off).
