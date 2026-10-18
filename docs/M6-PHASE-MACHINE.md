# M6 mission phase machine (word 0x8010CA20) — static read, s5470

Source: recompiled disassembly comments (scratch/agent/s390_verify/before_current_applied/funcs_32.c), cross-checked against s5467 lldb watch data.
Single-source (static read) until the s5470 breakpoint run confirms callers/args.

## Dispatch (runInMissionFrame 0x800FA6A4, jump table 0x800AFFA0, 7 entries)
| phase | handler | meaning |
|---|---|---|
| 0 | noopHandler_800FBBA0 | idle / in-flight, nothing ticks |
| 1 | tickMissionPhaseTransitionTimer 0x800FBBA8 | countdown of float 0x8011CA...(-0x3614) by dt; sets flag bit 0x40 in 0x8010CA1C (-0x35E4) when < 0 (fade/exit timer) |
| 2 | tickMissionObjectives 0x800FBC4C | timer sub-states via byte 0x8010C9F0: (>thresh)->1: speech cue; ->2 after wait: teardown calls then phase=0 (restart/continue) |
| 3 | requestSpeechResponseMode2 0x800FBAE8 | if one-shot byte 0x8010C9F0==0 && isSpeechBusyOrQueued()!=0: game mode byte 0x80130B14=2 (results), ++one-shot |
| 4 | requestSpeechResponseMode1 0x800FBB44 | same with mode byte = 1 |
| 5 | flashMissionAlertObjectsAndPrint 0x800FADEC | alert flashing |
| 6 | (default, no handler) | entered by clearMissionObjectiveFlagsAndEnterPhaseSix |

## Writers of the phase word
- requestMissionTransitionMode 0x800FB190(a0): ONLY when phase==0. a0==3 -> phase 3 (Mode2 results). a0==2 -> phase 4 (Mode1). Otherwise
  inspects player flags (0x80130B40+0x10 bit 0x20 -> sets mode byte 4 directly), per-player lives byte 0x80130B10+[0x8010C9E8] is DECREMENTED
  (death path); lives hit 0 -> game over (cue 0x1D, phase 3); else phase 1 (respawn timer). So 3/2 are the success/objective-complete requests,
  anything else is the player-death path.
- beginMissionEndTransition 0x800FAF0C: gated by countDisplayListChunks() (0x80007CB8) >= 0x3A98 AND phase==0 -> phase 5 (sets 0x80137CF4=1 etc).
- endMissionEndTransition 0x800FB05C: phase 5 -> 0.
- clearMissionObjectiveFlagsAndEnterPhaseSix 0x800FBD48: -> phase 6 and loads timer constant.
- initMission/choosePlayerCraftAssets: reset to 0.
- No `jal` call sites exist for requestMissionTransitionMode/beginMissionEndTransition => reached via function pointers (objective/event tables). Callers are data-driven.

## Consequence for the "success vs fail" question
Results screens are reachable by (a) a caller passing a0==3/2 (objective flow) or (b) lives reaching 0. s5464 saw FAIL results, consistent with (b),
though (a) is not excluded. s5470 breakpoint run records a0 and the caller for every request.
