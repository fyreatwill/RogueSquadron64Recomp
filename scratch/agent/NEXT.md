# NEXT: who produced index 30 in the list entry ($s1) that musyxMixActiveVoices multiplies by 0x88 (jal 0x80090F00 -> musyxRenderVoiceSamples)
HYPOTHESIS-ID: m5-audio-destub
Established (s4570): the alloc pair never has count>=30; the bad voice is base 0x801714D0 + 30*0x88 (count there is 18). a3 chain: lhu v1,0($s1) at 0x80090ED8; a3 = table[byte]+v1*0x88.
Hypotheses: H-stale-list-entry (the $s1 list node is freed/reused memory holding text, halfword = 30), H-legit-index-wrong-array (index 30 is valid for a bigger array; the table byte selects the wrong base), H-list-walk-overrun ($s1 walks past the list end into string data).
Discriminator: new fixup script tools/apply_s4571_*.py, funcs_24.c before 0x80090F00: log s1, 0x20 bytes at s1, v1, table byte, t0 base, when v1 >= count (lhu 0x80149700) plus one in-range control; env-gated, vi_w>=512. Run with the scratch/agent/s4570_voicecount.sh pattern (3 replicates).
