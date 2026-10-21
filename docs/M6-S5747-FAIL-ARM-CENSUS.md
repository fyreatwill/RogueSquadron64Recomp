# s5747 census: writers of the mission fail/win/game-over path (static, single-source)
Source: generated C in N64Recomp/RecompiledFuncs (no build/RecompiledFuncs). Bool array base 0x8013889F+id.
- Fail arm: lv2_checkComplexObjectives funcs_43.c:18807/18819 writes bool[0x64]=1,bool[0x65]=1,timer[7]=0. Guard bool[1]==1 && bool[0x63]==0 && bool[7]==1 && bool[0x64]==0 (after bool[0x65]==0). bool[7] only set by sayWhoaHim_v0x1FC (funcs_48.c:4395). bool[0x63] is never written by setObjectiveBoolean (reads only).
- Second fail arm: funcs_43.c:19107/19119 writes bool[0x6D]=1,bool[0x65]=1 when count[0x28]>0 && bool[0x6D]==0.
- Both -> setHudEnableBit4 0x800C7738 (flagword 0x8010C9E0|=4, if gate==0) -> requestMissionTransitionMode (funcs_42.c:14333/14533): gate=4 (arg 2) -> requestSpeechResponseMode2 (funcs_42.c:16211) B14=2 -> gate 6 -> mainGameLoop B14=2 case (funcs_8.c:23637) lives-- ; lives>0 same-level restart, else game over.
- Death path: requestMissionTransitionMode(1) funcs_42.c:14470-14490 lives[player]-- (0x80130B10 + byte 0x8010CA18), 0 -> B14=3.
- Not read in context: B14 writes at funcs_27.c:109161/120277, funcs_32.c:33885, funcs_33.c:20747; timer[7] incrementer; float limit at 0x800A95F0.
Tension with s5728 (bool 7 never fires yet the mission still fails): the observed fail must enter via another arg-2 caller of requestMissionTransitionMode, the 0x6D arm, or a B14 writer listed above.
