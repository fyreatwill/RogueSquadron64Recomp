Single next work unit (s5611): fold soaks s5610_b14_{a,b} (logs scratch/agent/m6/s5610_b14_*/run.log; grep "[mission-win] seq" for b14= and b50=).
Hypotheses: H1 b14 becomes 1 but b50 bit 0x100 never sets (loop-exit writer missing/guarded) -> find the writer of 0x80130B50 bit 0x100 (lldb write-watch, model on scratch/agent/m6_phase6.sh) and its guard. H2 b14 never reaches 1 or is cleared to 0 (writers 800C252C, 80134888) before the loop looks -> log who clears. H3 b50 bit 0x100 sets and b14=1 but the 0x820 test at 0x8003E338 (beq r3,0x820 -> 8003E230) re-enters the loop.
Discriminator: the b14/b50 columns around the gate 4 -> 0 transition. Positive control: gate/subphase columns change in the same line.
If H1: static-trace what the 0x100 setter tests (likely a done condition of an objective/pause screen).
HYPOTHESIS-ID: m6-mission-endurance
