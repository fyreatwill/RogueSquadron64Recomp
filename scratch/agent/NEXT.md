Single next work unit (s5631): fold s5630_snap3_{c,d,e,f} from scratch/agent/m6/<tag>/run.log (NOT soak_results, which has only verdict lines). For each: did it fail (grep -a 'b14=2', 'id=0x64')? Positive control: >=10 [ccosnap] lines.
Hypotheses: (D) bool[7] is set by a run-dependent event (ship/escort/enemy state) just before 0x64; (T2) a timer-gated arm sets bool 7 only when some other condition holds. S and fixed-time T are refuted (s5630).
Discriminator: in a FAILING run, the [ccosnap] where 7=1 first appears vs 0x63/0x65/0x64, with t= and neighbouring log lines (what happened in the game at that second). Then name the writer of bool[7] (grep for writes to 0x8013889F+7 = 0x801388A6, or setter callers with id 7) and make the soak survive.
If no failure in 4 runs: statically find writers of bool id 7 anyway (decompiled funcs, 0x801388A6).
HYPOTHESIS-ID: m6-mission-endurance
