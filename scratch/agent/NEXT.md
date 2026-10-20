# NEXT: log a0/a1 at the three forwarded-a0 setObjectiveBoolean sites (0x801010D4, 0x801073F4, 0x80103E70)
Hypotheses: H1 an init site passes a0=7 (explains bool7 with no voice line); H2 a0 is garbage/0 there and bool7 is set by sayWhoaHim in retail only, fail arm in port is reached by another path (bool7 read stale/aliased). Discriminator: one fixup-script log line at each site (ROGUESQ_LOG_HUDBIT) plus the existing [objbool] stream as control; run a level-0/e/5 mission start once.
HYPOTHESIS-ID: g1-bool7-voice-path
