# Next work unit: what advances mission phase word 0x8010CA20 to the Mode2/Mode1 handler (success vs fail vs timer)
Hypotheses: H1 objective-complete (success path, Mode2); H2 player death/fail (Mode1 or another); H3 elapsed timer (tickMissionPhaseTransitionTimer 0x800FBBA8).
Discriminator: env TRAPSWAP=6900 zsh scratch/agent/m6_wp10ca20.sh <tag> 480 (phase was already 6 at swap 7600; at 4500+400 s still pre-phase); log every write to 0x8010CA20 with bt. Writer in timer fn => H3; objective check => H1; death handler => H2. Also label the 7 phase-table entries offline (funcs_32.c ~0x800FA854, table near 0x800AFFA0).
HYPOTHESIS-ID: m6-mission-end-trigger
