Single next work unit (s5647): fold s5646_vbuf_{a,b} ([vbuf] lines in scratch/agent/m6/s5646_vbuf_*/run.log).
Premise fix: consumeVoiceSamples is a pure counter (slot+0x11D4/0x11DD); it never reads sample bytes. Slot data lives behind pointers found in the slot (scan logged by [vbuf]).
Controls first: `[vbuf] control code@0x80000400 nz800` must be >>0 in each dump, else the run is void.
Outcomes: D1 every slot-pointer target nz800=0 at later dumps => PI/ROM DMA of speech yields zeros (find DMA source via the pointer, compare with ROM bytes). D2 target nonzero => next check whether the ucode cmd list reads that address (ROGUESQ_AUDIO_UCODE; M5 de-stub target). D3 nonzero and mixed => loss is later (AI ring/gain; compare with retail oracle).
HYPOTHESIS-ID: g2-voice-never-requested
