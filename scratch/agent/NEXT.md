# Next work unit

HYPOTHESIS-ID: m5-early-musyxsynthframe-race

s4695 closed A15 (SPIN_YIELD redundant for hangar route). New observation: in
5/8 concurrent arm-runs the port dies at ~3.3 s (VI 640 phase) in
musyxSynthFrame_s4562_impl+9668, fault addr 0x400149714 (x9=0x100149714: a
guest-derived pointer > RDRAM), varying last-guest-pc. Artifacts in
scratch/agent/s4695_m5_a15_spin_yield/ (port_*.log with [CRASH] blocks).

Hypotheses:
- H-race: the audio host thread runs musyxSynthFrame while guest voice/state
  setup is mid-write (contention exposes it); survivors are just lucky.
- H-uninit: a voice-array/pointer field is legitimately uninitialised before
  title for this config (ROGUESQ_AUDIO_UCODE=1 early-start), crash rate
  independent of contention.
- H-ctrl: crash rate depends on concurrency count only.
Discriminator (ONE run): single-instance x4 sequential-start vs 4 concurrent,
same recipe (run_s4695 minus SPIN_YIELD), count early crashes per mode; plus in
the crashing frame dump the value of the faulting field and the guest address
it was loaded from (CRASH block regs x9/x0) to name the writer (ORIGIN rule 11).
Then decide guard-vs-fix. Read musyxSynthFrame_s4562_impl+9668 via the
fixup source (grep s4562 in tools/*.py).
