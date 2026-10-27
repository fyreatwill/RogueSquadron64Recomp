# NEXT: G3c(b) spikes - is the constant wedge vertex a stale VTX slot?
HYPOTHESIS-ID: g3c-owner-visual-b
s6366: 96.5% of flagged wedges pin yh==ym at -224.25/-170.25; border-crossing run shares a constant vertex (1113.7,-170.25).
Hypotheses: H-stale-slot (tri indexes a vertex-buffer slot not loaded this frame -> retail does it too), H-clip-const (ucode writes a fixed clip-plane vertex -> retail too), H-emu (excluded by s6300/s6301).
Work unit: one build, extend the F5 0x04 VTX probe (tools/fixup_factor5_ucode.py) to record the DMEM vertex slots loaded per task, plus on a swap that logs [spike] dump the vertex whose projected (x,y)==(1113.7,-170.25) and whether any VTX load wrote that slot. Positive control: ROGUESQ_SPIKE_CTL=40 still flags. Discriminator: slot never loaded => stale (retail identical, ask owner re CULL_SPIKE default); loaded with sane input => emulation/ucode arithmetic bug, bisect.
