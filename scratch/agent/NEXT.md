# NEXT: at the musyxSynthFrame crash site (+5688 impl), which loaded pointer is stale, and does initMusyXEngine rewrite that head before gate=1 returns?
HYPOTHESIS-ID: m5-audio-destub
Established (s4562): gate cleared AFTER frees in retail order; pause across free window does not change crash (A/B identical, +5688). H-stale-head selected.
Hypotheses: H-stale-head (head/link pointer into freed 0x80179380/0x801714D0 survives re-init); H-reinit-order (gate=1 set before list rebuilt); H-realloc-overlap (guest reallocates over freed blocks, contents reused as junk).
Discriminating step: disassemble crash site (funcs_24.c musyxSynthFrame around +5688, find the lw feeding the faulting address, x9=0x8000950e junk), log that load's source address/value and compare to freed block ranges + initMusyXEngine's stores to the head; one build, 2-arm run via scratch/agent/s4562_pause.sh (re-apply tools/apply_s4561_synth_free_order.py then apply_s4562_synth_pause.py after regen).
