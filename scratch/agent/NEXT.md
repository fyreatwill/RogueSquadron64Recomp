Single next work unit (s5615): fold s5614_real_p100/p300 from SOAK-RESULTS.md (logs in scratch/agent/soak_results/). grep '\[mission-win\] get' and 'seq gate' in each log.
Hypotheses: H1 get(2)>=3 or get(3)>=9 crosses before get(10) effect (lose arm wins); H2 gate 5 (vflags 0x101) preempts; H3 timing one-off.
Discriminator: which get() column reaches threshold before the first gate change, p100 vs p300; if get(2)/get(3) climb on their own, WIN_REAL must also hold them low (poke them to 0 each poll) - build that as the next lever. Still locate a level-id word.
HYPOTHESIS-ID: m6-mission-endurance
