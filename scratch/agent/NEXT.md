# NEXT (s7686)
HYPOTHESIS-ID: g6c-pos-fallback-neighbour

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7685: [s7685-pos] showed the 2-unit position fallback hands sub 0x12/0x13 (TIE) stand-ins to itemless short-lived objects spawned at
the craft (+0x30=+0x34=0.25f); ROGUESQ_S7685_POSSUB now rejects itemless callers for 0x12/0x13 and the ray-shield class (L12 fix 0 pos).
Still on the plain fallback, callers never classified: subs 0x0C/0x0D/0x14/0x1E/0x1F/0x24/0x2E/0x46/0x47 (31-log pos counts 13/61/104/22/4/1/4/8/4).
Hypotheses per sub: H-neighbour (callers itemless/other-sub like the TIEs -> add to the reject set) vs H-self (caller_sub == stand-in sub
or the real object genuinely has no table item, e.g. runtime-spawned copies -> keep the fallback).
Work unit: ONE run per level, fix binary only (no code change needed; the instrument is in), levels that carry these subs:
L1 (AT-ST 0x1F, 0x14), L4 (AT-PT 0x47), L5 (0x14/0x0D). For each: mkdir -p scratch/s7686/L<n>; then
env R=$PWD/scratch/s7686/L<n> HOLD=200 ALLOW_SLOW=1 ARMS="4:fix:ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_FORCE_SAVE_MISSION=<n>" zsh tools/g1e_owner_quiet_arms.zsh
Tally offline: grep '[s7685-pos]' -> (stand-in sub, caller_sub, c30==c34, verdict). Positive control: lines must appear for at least one sub
(L12 gave 30). Extend the reject set only for subs whose callers are itemless/other-sub AND whose real objects match by item; then a
same-binary old/fix pair on that level. If a sub's callers are same-sub, document H-self and keep the fallback. Then G6c waits on the
owner sheet. One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
