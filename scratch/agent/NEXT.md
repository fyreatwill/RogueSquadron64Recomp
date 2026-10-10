# NEXT: find the writer of the garbage SETCIMG (addr=0x130393 w=1033 siz=3)

HYPOTHESIS-ID: wild-setcimg-writeback

s4548 made ROGUESQ_FL_HDR_HARD_SKIP default ON (default 3/3 survive 180 s; =0 dies at VI 640). The mitigation is in; the root cause (who emits SETCIMG 0x130393 w1033) is open (s4531 says a garbage-region SETCIMG). Next: capture the RDP/DL words preceding that SETCIMG once (dump flag, analyze offline) and compare against the F5 ucode reference's inline-data pointer advances; hypotheses: H-ucode-pointer-advance (port misparses a command length), H-DL-memory-corrupt (guest wrote garbage DL), H-retail-too (oracle rdplog shows it; unlikely). Positive control: dump must show the known good SETCIMG w512/1024 in the same run.
