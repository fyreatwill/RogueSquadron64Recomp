# NEXT (s7775)
HYPOTHESIS-ID: npc-slot-dangling-table
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Unit (one instrument, one build, one run): s7774 found that between the menu overlay (idx3) and initMission, *0x80130BB0 (NPC slot
table) points at memory whose entries are not RAM pointers (1578 bad entries for ~60 s during the chapter crawl / cinematic idx4).
Hypotheses: H-unused (no code reads the table in that phase), H-own-table (the cinematic re-inits a table via its own
initNpcSlotList caller 0x800A9B80/0x800C40F8 and the pointer we read is the old one: check whether *0x80130BB0 changes value),
H-latent (a dispatch/destroy does read it; retail-shaped, guarded only by luck: a garbage obj+0 jalr would abort/crash).
Instrument: extend rs64_s7774_slots ticks to print the table pointer value; add a counter on slotDispatcherIter (0x8003E8DC) and
destroyNpcSlotByIndex (0x8003ED74) entries while the scan says bad>0 (fixup/apply script hook, or a recomp_context hook if one
exists for these; check tools/apply_* for an entry-hook pattern first). Positive control: the same counters in flight must be >0.
Run: `zsh tools/s7774_slot_run.zsh dangling1` (300 s owner route).
Outcome: 0 reads while bad>0 -> H-unused, class closed; pointer changes -> H-own-table; >0 reads -> H-latent, name the caller.
Also uncovered by s7774: the mission win/outro swap (mission->cinematic) - only if a forced route reaches it cheaply.
