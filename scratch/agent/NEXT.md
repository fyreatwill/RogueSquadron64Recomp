# NEXT: what is the text source behind cart word 0x77696E67 ("wing") in the {len=0x600, cart, ram=0x801A9B90} nodes?
HYPOTHESIS-ID: m5-audio-destub
Context (s4589): five RDRAM hits for ram 0x801A9B90; nodes at 0x1123E8 and 0x179A68 carry cart=0x77696E67 coherently; 0x17DF1C shows "wing wing" text next to 0x600/801A9B90.
Hypotheses: H-name-table-row-copied (a string table row copied into the node array), H-array-overrun (neighbouring text buffer overruns into the node array), H-stale-reuse (node memory freed and reused as a text buffer).
Discriminator: one run; at the odd DMA dump 0x80 bytes before/after 0x17DF1C, 0x1123E8, 0x179A68 as hex+ASCII (extend the s4589 block in lib/N64ModernRuntime/librecomp/src/pi.cpp). Control: ram-word hits>0 (already passes). If the text surrounds is a contiguous ASCII string covering the cart field => H-array-overrun/stale-reuse; if the cart field is an isolated 4 bytes inside non-text => H-name-table-row-copied.
Run: zsh scratch/agent/s4588_run.sh (arm B already has S4298).
