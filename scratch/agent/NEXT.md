# NEXT: who writes the ASCII tag 'wing' (0x77696E67) into the cart slot at RDRAM 0x179A64, and does retail have it too?
HYPOTHESIS-ID: m5-audio-destub
Hypotheses: H-key-unresolved (tag is a 4cc key never translated to a B0xxxxxx cart address by a lookup that did not run in our port), H-legit-retail (retail also holds the tag and its DMA path handles it), H-port-writer (a port stub writes the tag).
Discriminator: tools/oracle watch (physical addr of RDRAM 0x179A64, positive control: whole-RDRAM watch) on retail, or in port a write-watch on 0x179A64 logging guest_pc. Retail has no tag/unresolved => H-key-unresolved/H-port-writer; retail has it => H-legit-retail.
