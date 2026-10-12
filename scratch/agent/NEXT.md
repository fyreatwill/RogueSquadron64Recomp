# Next work unit

HYPOTHESIS-ID: m5-synth-walk-after-free

s4699: PAUSE=3 (release at gate store 0x8008ED48) crashes 2/2; gate only guards update3DAudioFrame (see PORTING-STATE s4699). Retail shutdownAudioEngine (0x80091D84) calls findAndZeroTableSlotMatching(a0=0x8009123C) to deregister the synth from the 4-slot VI-retrace callback table at 0x8011A8A4.

Hypotheses:
- H-dereg: the port's retrace dispatch calls musyxSynthFrame without re-reading the table (cached/snapshotted), or the removal never matches -> synth keeps firing.
- H-stale-head: removal works, but synth list head 0x801499B0 chains into freed memory and the callback is re-registered at re-init before the head is rebuilt.
- H-removal-cond: the path that frees blocks (wait/noop stub) is not the path that deregisters.

Discriminating batch (one build, one run, template run_s4699_pause_release.sh, arms PAUSE=0 and 2): log (a) every findAndZeroTableSlotMatching call with a0 and whether a slot matched, (b) the 4 table words at every 200th musyxSynthFrame entry and at s4457-bad time, (c) writes of 0x8009123C into the table. Positive control: the registration at 0x800919D8 must show a register row.
Outcomes: removal row + table lacks 0x8009123C yet synth still enters => H-dereg; no removal row before free => H-removal-cond; removal ok and table clean until re-register => H-stale-head.
