# Next work unit (s4466): is the 0xF7C-over-live-blocks overlap real, or an unlogged free?

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4465): in 1 of 3 runs reaching VI 1024, rs_malloc returned 0x801931F0 size 3964 over live (never rs_free'd) blocks 0x80193E20(48), 0x80193FF0(768).
Hypotheses: (A) allocator returns overlapping block (free-list/size corruption); (B) another free path (not logged) released the nested blocks.
Discriminator: log every allocator entry (rs_malloc/rs_free/realloc/heap-init/reset) in the same run + positive control, replay with scratch/agent/s4466_an3.py. A: nested blocks still live at the 0xF7C malloc; B: an unlogged free precedes it.
