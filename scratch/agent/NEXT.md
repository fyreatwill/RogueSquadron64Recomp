# Next work unit

HYPOTHESIS-ID: m5-synth-walk-after-free

s4698: s4672 crash = synth list walk over freed audio blocks (see PORTING-STATE s4698). PAUSE=2 (hold forever) fixes the crash but permanently skips synth.

Unit: replace "hold forever" with the right lifetime. Hypotheses:
- H-gate: retail stops the walk because the guest clears gate 0x800A0F50 right after waitForMusyXAudioTaskDone/musyxNoopStub; the port's synth thread runs in the gap (or ignores the gate). Fix: keep g_s4562_pause until the guest store to 0x800A0F50 clears it.
- H-reinit: pause must also end at audio re-init (rs_malloc 900 B at 0x80179380 / musyx init), else audio stays dead after the first shutdown.
- H-other-reader: synth is not the only reader (then PAUSE=2 would not have been 2/2 clean — currently disfavoured).
Steps: (1) grep funcs for stores to 0x800A0F50 (`-0X..($at)` with lui 0x800A) and the init that sets it; (2) add PAUSE=3 = clear pause on that gate store / on audio re-init; (3) in-run A/B arms: PAUSE=0 (control, must crash), 2, 3; positive control = PAUSE=0 crash; success = PAUSE=3 0 crashes AND [s4562] skipped count bounded AND synth entries resume after re-init (s4561-ctl rows).
Script template: scratch/agent/run_s4698_pause_ab.sh. Then proceed with M5-AUDIO-PLAN next step.
