Single next work unit (s5612): find the writers of byte 0x80130B14 (observed 0 then 2, never 1) and bit 0x100 of word 0x80130B50 (observed constant 0x11). Static: grep generated C for stores at offset 0xB14/0xB50 off lui 0x8013 and off r19=0x80130B40 (+0x14/+0x10). Dynamic: lldb write-watch modeled on scratch/agent/m6_phase6.sh; positive control = a watch on gate 0x8010CA20, which must fire.
Hypotheses: H2 something writes B14=2 early and BB44's write of 1 is overwritten or not executed; H3 the poke skips BB44's real precondition; H4 B50 bit 0x100 is set by a path (pause/objective screen) never entered in the soak.
Discriminator: PC attribution of each B14 write (value 2 vs 1) across the gate 4 transition.
HYPOTHESIS-ID: m6-mission-endurance
