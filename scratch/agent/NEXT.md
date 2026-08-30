# NEXT work unit — correct swapBufferWithViMode jal delay-slot $a0

HYPOTHESIS-ID: m5-swapbuffer-delay-slot-a0

Session 3276 selected `H-PortTargetPublicationAbsent` and named a generated
delay-slot defect at `swapBufferWithViMode` jal `0x8001BB54`. Hardware would
execute `addiu $a0, $a0, -0x44` before `osViSetMode`, passing `0x80128C90`.
The recompiled order calls `osViSetMode_recomp` first with `$a0=0x80128CD4`
(width 2). ORIGIN: that jal; the observed `$a0` is not a legitimate OSViMode
pointer. This is not claimed as the title-1024 writer.

## Competing hypotheses

- `H-DelaySlotFixed`: after the fixup, the width-2 `[osViSetMode]` and
  `[phase]` rows disappear and the copied mode at `0x80128C90` is requested.
- `H-FixupMissed`: the width-2 row still appears (anchor missed or delay slot
  still after the call).
- `H-DelaySlotNotCausal`: the width-2 row disappears, but phase 4 still
  stops at `640 @ 0x0066A500` with no 1024 request (predicted).

## Discriminator

One rebuild after a regeneration-preserved fixup, one 60s `ROGUESQ_LOG_ALL=1`
run killed with SIGKILL. Compare `[osViSetMode]` requested widths and
`[phase]` transitions to s3261. A remaining width-2 row selects
`H-FixupMissed`; absence plus a 640-only stop selects `H-DelaySlotNotCausal`;
absence plus a 1024 request would be unexpected and must be reported, not
treated as the predicted success.

## Exact command

From the repository root:

```sh
# 1. Add a unique PATCH in ../N64Recomp/fixup_game_funcs.py that, in
#    funcs_5.c swapBufferWithViMode, moves
#      ctx->r4 = ADD32(ctx->r4, -0X44);
#    to immediately BEFORE osViSetMode_recomp at site 0x8001BB54, and
#    leave the post-call delay-slot copy as a no-op or comment.
#    Mirror a local tools/apply_s3277_swapbuffer_delay_slot.py so this
#    repo's commit carries the tool. Do not hand-edit funcs_5.c alone.
# 2. Apply the already-patched tree (funcs_5.c is already fixup-sentinel'd,
#    so do not re-run the full fixup on an unclean tree). Either apply the
#    local tools script to the existing generated file, or clear+regen+fixup
#    per CLAUDE.md if a full regen is required.
# 3. Build and capture:
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 \
  zsh -c 'cd build && ./RogueSquadron64Recomp' \
  > scratch/agent/s3277_swapbuffer_delay_slot.log 2>&1 &
# after 60s: kill -9 the game (SIGKILL), not SIGTERM
```

Positive control: `[osViSetMode]` still prints four-or-fewer rows and
`[m5-port-vi-control]` still fires at width >= 640. Do not change audio
behavior. Do not run M5 Step 3.
