# Next work unit

HYPOTHESIS-ID: m5-retrace-pacing-vs-retail

s4899 closed the retrace/audio-done/synth join (docs/M5-S4899-CADENCE-JOIN.md):
synth entry == retrace recv1 return == audio-done msg, 1:1, chain R A W T S.
Left open: is the retrace-return rate per VI (origin change / video frame) the
same in retail as in the port?

Hypotheses:
* H1: retail also gives ~1 synth per retrace and ~1 retrace per VI; the old
  "retail 2-dominant" (s4887) was a different unit (per update_screen bucket
  aliasing) -> ratios agree once measured per VI-origin change on both sides.
* H2: retail delivers 2 retraces per video frame (e.g. 60 Hz retrace, 30 fps
  swaps) while the port delivers 1 -> port VI/retrace pacing is half rate.
* H3: port retraces are 1:1 with VI but update_screen is called in bursts
  (0/2 pattern) -> pure port frame-pacing artifact, retail ratio matches.

Discriminator: count 0x8009123C entries (oracle: tools/oracle watch-pc, s4873
twin) per VI-origin change in the hangar phase vs port S per VI-origin change
(add origin-change key to rs64_s4899_vi, or reuse s_snap rows). Controls:
whole-RDRAM watch, title/hangar phase lines. Reuse scratch/agent/run_s4899_cadence_join.sh.
