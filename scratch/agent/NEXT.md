# NEXT: who writes the ASCII-valued cart address (0x17696E67 = "ing") that tid1 (pri 120) passes to do_rom_read at ~VI 5850?
HYPOTHESIS-ID: m5-audio-destub
Context (s4588): clean run dies on the odd-DMA assert in both arms; the call is tid1, guest_pc 0x80001B08, ram 0x801A9B90, 0x600 bytes. Identify what 0x80001B08 is (symbol) and what request struct the cart addr came from.
Hypotheses: H-stream-request-node-clobbered (queue node holding the cart addr overwritten by string text), H-stale-node-reused (node freed/reused by another subsystem), H-wrong-arg-in-caller (caller passes a pointer-to-text through a mis-typed field).
Discriminator: one run with ROGUESQ_LOG_S4298 (prints rdram hits for the odd value at crash, host backtrace only at crash) plus S4588, then dump the 0x80 bytes around ram 0x801A9B90 and the hits. Control: the S4298 hit scan must find the value in some node (else it was computed in registers).
Run: edit scratch/agent/s4588_run.sh arm B to add ROGUESQ_LOG_S4298=1.
