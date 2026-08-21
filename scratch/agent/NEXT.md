# NEXT work unit (s2162) — S32-address the unsigned PATCH MEM_BU sites

HYPOTHESIS-ID: m5-image-wait-slot-sigsegv

## Work unit

s2161 selected `H-RetailLoadsCount`. Guest `D_80141AD0` is a legitimate
clamped config byte from `setDisplayMode` `0x8008EA44` and
`reapplyDisplayMode` `0x8008EB8C`. The port SIGSEGV at
`waitForAnyAudioSlot+1060` is the s2045 loop PATCH
`MEM_BU(0X1AD0, 0X80140000)` at `funcs_15.c:7603`: the unsigned KSEG0
constant zero-extends, so the host address is `rdram+4GB+0x141AD3`
(s2160 `x0=0x300000000`, `si_addr=0x400141ad3`). Image
`anyAudioSlotActive` is `path=gate0` and does not load the byte;
original wait MIPS does not either. Stub evaluates the same PATCH and
returns (`c=0`).

Do not add a wait/slot guard, retry default-on, move the canary, or
change `osAiGetStatus_recomp` / `osAiSetNextBuffer_recomp`.

Replace the unsigned form with the already-correct
`MEM_BU(0X1AD0, S32(0X8014 << 16))` in `fixup_game_funcs.py` and the
live generated files. This is probe addressing, not a skip/allow of a
guest defect.

## Competing hypotheses and discriminator

- `H-UnsignedMemBu`: same-build image `ROGUESQ_AUDIO_UCODE=1` reaches
  wait loop/return probes (and title) after the `S32` fix; stub still
  reaches title/hangar. The +1060 SIGSEGV was the unsigned PATCH load.
- `H-StillFaults`: image still SIGSEGVs at wait after the `S32` fix.
  The unsigned constant was not the (only) faulting load.
- `H-StubRegress`: stub wait now faults or no longer returns. The
  `S32` rewrite changed more than host addressing.
- `H-CoverageFailure`: neither arm reaches wait entry (build/recipe).
  Nulls are uninterpretable.

Positive controls in every arm: `[audtask-dispatch] real_ucode=` must
print; `[m5-postwait] edge=entry site=waitForAnyAudioSlot` must print
before a missing loop/return is treated as evidence.

## Exact commands

Live unsigned sites (5):
- `../N64Recomp/RecompiledFuncs/funcs_15.c` lines 7561, 7603, 7611, 7700
- `../N64Recomp/RecompiledFuncs/funcs_23.c` line 4590
- matching strings in `../N64Recomp/fixup_game_funcs.py`

Replace `MEM_BU(0X1AD0, 0X80140000)` with
`MEM_BU(0X1AD0, S32(0X8014 << 16))`. Do not full-regen; edit fixup plus
the two live files so the next regen keeps the fix.

Then one Debug rebuild and a same-build pair from `build/` with the ROM
present, SIGKILL to stop:

    env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 \
        ./RogueSquadron64Recomp

    env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LOG_ALL=1 \
        ./RogueSquadron64Recomp

Use the existing `scratch/s73_post_a_scene/run_mission_keys.sh` 30 12
driver. Compare wait entry/loop/return and whether image reaches title
`1024 @ 0x00790400`. ORIGIN line required if any remaining skip/allow
lands.

Table: `scratch/agent/s2161_wait_slot_oracle.txt`.
