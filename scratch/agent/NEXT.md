# NEXT: name the real guest writer of the {cart=0x6C637265, ram=0x801AB990} pair at RDRAM 0x179A64
HYPOTHESIS-ID: m5-audio-destub
Established (s4568): the pair is written as one coherent 8-byte group at ~141.7 s of a Start-mash run (host poller; its guest_pc is unreliable). Hypotheses: H-array-stomp (producer indexes past its list), H-bad-source (copy from an entry already holding ASCII), H-retail-same.
Discriminator: guest-store hook (in the fixup scripts, not generated files) on stores of word 0x6C637265, logging true guest pc + ra + base register, one build, one mash run, plus a control hook on a known value.
