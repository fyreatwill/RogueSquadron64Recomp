# NEXT work unit (s2163) — A1 default-on retry after S32 MEM_BU fix

HYPOTHESIS-ID: m5-a1-default-on

## Work unit

s2162 selected `H-UnsignedMemBu` and closed the s2160
`waitForAnyAudioSlot+1060` SIGSEGV. Same-build `ROGUESQ_AUDIO_UCODE=1`
now returns from wait (`c=0x11`/`0x10`) and reaches title
`1024 @ 0x00790400` plus hangar `512 @ 0x006AB400` on the qualified
recipe. Stub `=0` still matches that route.

Flip `get_rsp_microcode` so unset / empty / non-`0` selects
`factor5_ucode_b` and only `ROGUESQ_AUDIO_UCODE=0` remains the stub.
Update the s2160 hang comment. One Debug rebuild, then a same-build
unset / `=1` / `=0` triple on that binary. Do not add a wait/slot
guard, move the canary, or change `osAiGetStatus_recomp` /
`osAiSetNextBuffer_recomp`.

## Competing hypotheses and discriminator

- `H-DefaultMatchesOptIn`: unset matches `=1` (real_ucode=1, wait
  entry+return, title+hangar). Default-on is observationally the
  already-checked image arm.
- `H-StillRegress`: unset SIGSEGVs or fails title/hangar while `=1`
  still reaches them. Default-on is not the same as explicit `=1`.
- `H-StubRegress`: `=0` no longer reaches title/hangar or wait return
  on the flipped binary.
- `H-CoverageFailure`: an arm never prints `[audtask-dispatch]` or
  wait entry. Nulls are uninterpretable.

Positive controls in every arm: `[audtask-dispatch] real_ucode=` must
print; `[m5-postwait] edge=entry site=waitForAnyAudioSlot` must print
before a missing loop/return is treated as evidence.

## Exact commands

In `src/main/main.cpp:get_rsp_microcode` M_AUDTASK, invert the getenv
so unset selects the image (s2160 polarity, previously reverted). Then:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build --target RogueSquadron64Recomp -j 8

From repo root, ROM in `build/`, SIGKILL to stop:

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2163_unset 30 12

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_AUDIO_UCODE=1" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2163_on 30 12

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_AUDIO_UCODE=0" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2163_off 30 12

Run all three arms in this iteration (iron rule 13). If unset SIGSEGVs,
revert polarity before ending. Table from s2162:
`scratch/s73_post_a_scene/s2162_s32_membu_ab.txt`.
