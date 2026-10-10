# NEXT: name the writer of ASCII cart word 0x6C637265 in the odd-DMA node
HYPOTHESIS-ID: m5-audio-destub
Established (s4567): odd DMA node is {len=0x300, cart=0x6C637265, ram=0x8019C990}, 3 RDRAM copies (0x1120B0, 0x179A64, 0x17DBC8; last followed by ASCII 'late'). Single Start reaches hangar clean; mash triggers it.
Hypotheses: H-string-node (lookup returns text bytes), H-heap-clobber, H-retail-same.
Discriminator: rerun scratch/agent/s4567_guestscan.sh arm A with a write watch on 0x17DBC8/0x179A64 (pc attribution of first write of 0x6C637265), plus 'Start only inside hangar' arm to split mash count.
