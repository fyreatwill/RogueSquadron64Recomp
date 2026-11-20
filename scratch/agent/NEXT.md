# NEXT (s7684)
HYPOTHESIS-ID: g6c-rayshield-item-key

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7683: subs 0x33/0x36/0x44/0x4B/0x4F all use handleRayShieldedNpcDestroy (0x800E4070) and reach addNpcToVisibilityBucket (H-bucket).
But the stand-in handoff detector (src/main/rs64_standins.cpp ~line 309, `it = rw(rdram, state + 0x34u)`) never matches this class
by item: 0x36 L12 9/9 and 0x4B 48/51 are match=pos (2-unit position fallback, first call only). s7681 showed the position fallback
can hand off a NEIGHBOUR early (0x14 neighbours at 37.4 vs 31.0) -> a stand-in could vanish while its own real object is still hidden.
Work unit (offline first, then ONE run on L12 scratch/s7683 recipe below):
(1) Read handleRayShieldedNpcDestroy's render case 0x800E4310: a0=*(s2+0) a1=*(s1+0) a2=s1+4 a3=*(s1+0x38). Find which register/
    field holds the DAT item for this class (s2 is the item? init case reads lhu 0x0($s2) as the subtype -> s2 IS the DAT item;
    then state passed is s1+4, and state+0x34 = s1+0x38 = the radius, not the item). Confirm in the init case where s1 is built.
(2) Hypotheses: H-key (state+0x34 is not the item for this class; key by the item the hook sees in another arg, e.g. caller's a0 if
    it is the item, or record state->item at spawn) vs H-ok (pos fallback is safe here: pillars/pads are > 2 units apart, measure
    nearest-neighbour distance per class from the DAT positions; if min > 4 units, no fix needed, document it).
(3) If H-key: fix behind ROGUESQ_S7684_RSKEY (default on inside STANDINS, =0 old), one L12 run two arms (old/fix) same binary:
    expect fix match=item for 0x36, why=real30, identical real_add frames; controls 0x12/0x13/0x35 unchanged.
Recipe: env R=<abs dir> HOLD=200 ALLOW_SLOW=1 ARMS="4:x12:ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_FORCE_SAVE_MISSION=12" zsh tools/g1e_owner_quiet_arms.zsh
If H-ok: G6c engineering done, waits on the owner's look; take the next rung (owner items 2-9, 20, 22).
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
