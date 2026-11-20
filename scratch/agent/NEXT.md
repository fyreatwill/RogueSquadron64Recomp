# NEXT (s7685)
HYPOTHESIS-ID: g6c-pos-fallback-neighbour

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7684: ray-shield class now keyed by item at state+0x30 (11/11 real30 on L12). Remaining datum: in the s7684 fix arm three sub 0x12
stand-ins (80549354/8054945C/80549564) handed off by the 2-unit POSITION fallback at frames 5713-5715 with dpos 1.97-1.99 - right at
the threshold, i.e. probably a neighbour's real object, so those stand-ins may vanish while their own object is still hidden.
Hypotheses: H-neighbour (caller is a different object/subtype: its item at state+0x34 or +0x30 is a guest pointer whose lhu +0 != 0x12)
vs H-self (caller is the 0x12 object itself whose state has no item key - same sub, dpos ~2 because it moved).
Work unit, one build: in bk_ret_impl's pos branch, read the caller's candidate item (state+0x34, else +0x30 if guest) and its lhu +0 sub;
log it on every pos match ([s7685-pos] caller_sub, stand-in sub, d). Fix behind ROGUESQ_S7685_POSSUB (default on in STANDINS, =0 old):
reject a pos match when the caller's sub is known and differs. Two arms same binary on L12 (scratch/s7684 recipe, mkdir R first!):
env R=<abs dir> HOLD=200 ALLOW_SLOW=1 ARMS="4:old:...+ROGUESQ_S7685_POSSUB=0 4:fix:..." zsh tools/g1e_owner_quiet_arms.zsh
(base env: ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_FORCE_SAVE_MISSION=12). Positive control: [s7685-pos] must log the s7684
pos matches with caller_sub. If every pos match is same-sub (H-self), no fix; document and G6c waits on the owner's look.
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
