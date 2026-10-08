# Next work unit (s4283): name the writer of the missing triangle header at the desync point

HYPOTHESIS-ID: m5-audio-destub-sequence

s4282: ODD cimg = decoded triangle data; desync precedes it (data follows a 2F/E6 with no header). Hypotheses: D) the LLE ucode never wrote the header (output pointer/advance wrong); E) a later write (other task / bump filter) overwrote the header before RT64 walked; F) the DPC bridge range starts mid-block.
Discriminator: at the first ODD event, record the offset of the last valid command, then re-run with a write-watch (or oracle) on offset+8: who wrote it and when relative to walk entry. D vs E: never written this frame vs overwritten. Positive control: watch a known-written command word.
Script template: scratch/agent/s4282_walk.sh.
