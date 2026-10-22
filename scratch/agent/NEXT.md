# NEXT: why runModelViewerLoop (0x800C9BF0) never exits for planet asset 2/3 (levels 10/15) but does for asset 0/1 (levels 0/5)

HYPOTHESIS-ID: g1-mission-coverage-sweep

H1 exit depends on a per-asset animation/timer/model load that stalls for asset 2/3 (recomp or data bug).
H2 exit needs a button our autopilot never sends in a form the viewer reads (but level 5 exits with same keys -> weak).
H3 legit retail behaviour needing longer time than 880 s (unlikely).
Discriminator: one build logging, per frame of the viewer loop, the exit-flag slots (see subagent findings; re-derive from funcs_36.c:15160 if lost) for levels 5, 10, 15 in the same build; level 5 is the positive control.
Static references: N64Recomp/RecompiledFuncs/funcs_34.c ~6830-7250, funcs_35.c:3138, funcs_36.c:15160.
Then continue queued 17b..18b soaks.

## Subagent result (s5941, static, unrun)
Single exit: 0x800B4168 nonzero (funcs_36.c:17096), armed via G1 (A/START gated by isUnlockBitSet(asset+1), byte 0x8013A663 bit asset+1) or G2 (auto-advance 0xB8, needs state 0xBA==4 and item timer > const 0x800A79B8).
H1 (buttons locked + G2 never fires) vs H2 (armed, never completes). Discriminator: existing `[mv-ship-arm]` probe at :17136 (set ROGUESQ env that enables it; grep for it) in lvl5 (control), lvl10, lvl15 runs; plus per-60-frame print of 0xBA, MEM_BU(0x8013A663), 0xB8 at 0x800CA4AC via fixup script. Check what ROGUESQ_FORCE_UNLOCK writes to 0x8013A663.
