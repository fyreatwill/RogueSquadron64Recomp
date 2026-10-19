# Who writes objective counters 0x80138060[n-1] (s5477, single-source static read)
Tool: tools/scan_objective_counter_writers.py over disasm_mips_elf.py dumps of 0x80000400..0x80140000.

Helpers: setObjectiveCount 800C75C0, increaseObjectiveCount 800C75EC, getObjectiveCount 800C761C (index n is 1-based; counter word = 0x80138060+4*(n-1)).

lv0 mission-end gate (lv0_checkComplexObjectives 0x8010119C): get(2)>=3 -> plays msg 553 then 800C7738; get(3)>=9 -> msg 554 + 800C7738.
(lv5 at 0x801041BC separately tests get(4)>=9 -> 800C776C; not the running level.)

Findings:
- No call site anywhere (main code: 0 jal to 75EC/75C0; overlay: 41, all constant index) increments or sets index 2, 3 or 4. Overlay constants seen: 1,2(lvg only),6,12..31,44,99,101,115,177,229,495,541,542,584.
- No lv0 function increments counters at all (lv0_objectiveProgress only does set(115,6)).
- The only other writers of the counter array are DATA-DRIVEN: applyDatObjectiveTriggerEffect (0x80065980, `counter[item.idx-1] += item.delta`, lw 0(r6)/4(r6)), datItemSetObjectiveBooleanCount (0x80065914), updateNpcEffectIntensity (0x800F3D64), executeActorType1Effect (0x800F435C).
- So for lv0, counters 2 and 3 move only when a DAT item/actor effect carries counter index 2/3 as its target. The mission ends when enough such items fire (3 or 9).

Next probe: log (idx, delta, new value) at the four store sites during a hold, and dump the lv0 DAT items whose counter target is 2/3, to see which in-game event must happen.
