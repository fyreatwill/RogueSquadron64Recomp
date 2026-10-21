# NEXT: fold s5728_supc (SUPPRESS_BOOL=0x1A) and s5728_supd (0x5,0x3C) from SOAK-RESULTS.md.
s5728 a/b fold: bool 7 NEVER fires (only ids 0x61,0x62,0x5,0x3C,0x1A, 5 per cycle, 0x1A ~31 s after cycle start); b had no [objbool-sup] line => control failed, H-B7 untestable; a and b both mission_cycles=2 (earlier baseline 3 => run-to-run noise +-1, not an effect).
H1: 0x1A (or 0x5/0x3C) causal for mission failing to menu -> cycles drop / flight outlives ~226 s cycle. H2: not causal -> cycles ~2-3 as before; fail driver is not setObjectiveBoolean (no 0x63/0x64/0x65 ever logged) -> next probe: trace what ends the mission (mission-state writer). H3: suppression destabilises mission.
Control: m6/<tag>/run.log has [objbool-sup] lines.
HYPOTHESIS-ID: g1-bool7-suppress
